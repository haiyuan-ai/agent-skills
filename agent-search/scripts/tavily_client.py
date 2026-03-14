"""
Tavily Search API 客户端 - AI 搜索引擎

专为 AI Agent 设计的搜索 API，返回经过 AI 处理的搜索结果
免费额度: 1000 credits/月
文档: https://tavily.com
"""
import asyncio
from typing import List, Dict, Optional
import aiohttp

try:
    from .config import get_api_key
    from .smart_cache import get_smart_cache
except ImportError:
    from config import get_api_key
    from smart_cache import get_smart_cache


class TavilyClient:
    """Tavily AI 搜索客户端"""

    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Tavily API Key is required")
        self.session: Optional[aiohttp.ClientSession] = None

    def is_available(self) -> bool:
        """检查 Tavily 是否可用"""
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
        num_results: int = 8,
        search_depth: str = "basic",
        topic: str = "general"
    ) -> List[Dict]:
        """
        执行 Tavily 搜索

        Args:
            query: 搜索查询
            num_results: 返回结果数量 (最大 20)
            search_depth: 搜索深度 ("basic" 或 "advanced")
            topic: 搜索主题 ("general" 或 "news")

        Returns:
            搜索结果列表
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": min(num_results, 20),  # Tavily 最大 20
            "search_depth": search_depth,
            "topic": topic,
            "include_answer": False,  # 不需要 LLM 生成的答案
            "include_raw_content": False,  # 只获取处理后的内容
            "include_images": False
        }

        try:
            async with self.session.post(self.BASE_URL, headers=headers, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                get_smart_cache().record_provider_usage("tavily", success=True)

                results = []

                # 处理搜索结果
                search_results = data.get("results", [])
                for idx, result in enumerate(search_results, 1):
                    results.append({
                        "source": "tavily",
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "text": result.get("content", ""),  # Tavily 返回 AI 处理后的内容
                        "highlights": [],
                        "score": result.get("score", 0),  # Tavily 的相关性分数
                        "published_date": result.get("published_date", ""),
                        "author": result.get("author", ""),
                        "position": idx,
                    })

                return results

        except Exception as e:
            get_smart_cache().record_provider_usage("tavily", success=False)
            print(f"Tavily search error: {e}")
            return []

    async def search_with_timeout(
        self,
        query: str,
        num_results: int = 8,
        search_depth: str = "basic",
        topic: str = "general",
        timeout: float = 10.0
    ) -> List[Dict]:
        """带超时的搜索"""
        try:
            return await asyncio.wait_for(
                self.search(query, num_results, search_depth=search_depth, topic=topic),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Tavily search timeout (> {timeout}s)")
            return []
