"""
Exa API 客户端 - 语义搜索
"""
import asyncio
import os
from typing import List, Dict, Optional
import aiohttp

try:
    from .config import get_api_key
    from .smart_cache import get_smart_cache
except ImportError:
    from config import get_api_key
    from smart_cache import get_smart_cache


class ExaClient:
    """Exa 语义搜索客户端"""

    BASE_URL = "https://api.exa.ai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key("EXA_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None

    def is_available(self) -> bool:
        """检查 Exa 是否可用"""
        return self.api_key is not None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search(
        self,
        query: str,
        num_results: int = 10,
        include_text: bool = False,
        highlights: bool = True
    ) -> List[Dict]:
        """
        执行 Exa 语义搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量
            include_text: 是否包含完整文本内容
            highlights: 是否包含高亮片段

        Returns:
            搜索结果列表
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.BASE_URL}/search"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate"  # 排除 brotli
        }
        payload = {
            "query": query,
            "numResults": num_results,
            "contents": {
                "text": include_text,
                "highlights": highlights
            }
        }

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                get_smart_cache().record_provider_usage("exa", success=True)

                results = []
                for result in data.get("results", []):
                    results.append({
                        "source": "exa",
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "text": " ".join(result.get("highlights", []) or []),
                        "highlights": result.get("highlights", []),
                        "score": result.get("score", 0),
                        "published_date": result.get("publishedDate", ""),
                        "author": result.get("author", ""),
                    })

                return results

        except Exception as e:
            get_smart_cache().record_provider_usage("exa", success=False)
            print(f"Exa search error: {e}")
            return []

    async def search_with_timeout(
        self,
        query: str,
        num_results: int = 10,
        timeout: float = 10.0
    ) -> List[Dict]:
        """带超时的搜索"""
        try:
            return await asyncio.wait_for(
                self.search(query, num_results),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Exa search timeout (> {timeout}s)")
            return []
