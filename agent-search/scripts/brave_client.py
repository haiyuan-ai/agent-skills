"""
Brave Search API 客户端 - Web 搜索结果

官方文档: https://api-dashboard.search.brave.com/documentation/web-search/get-started
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


class BraveClient:
    """Brave Search 客户端"""

    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("Brave API Key is required")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @staticmethod
    def _detect_locale(query: str) -> tuple[str, str]:
        for char in query:
            if '\u4e00' <= char <= '\u9fff':
                return "zh-hans", "CN"
        return "en", "US"

    async def search(
        self,
        query: str,
        num_results: int = 8,
        search_lang: str = None,
        country: str = None
    ) -> List[Dict]:
        """
        执行 Brave 搜索
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        if search_lang is None or country is None:
            auto_lang, auto_country = self._detect_locale(query)
            search_lang = search_lang or auto_lang
            country = country or auto_country

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": min(num_results, 20),
            "search_lang": search_lang,
            "country": country,
            "spellcheck": "0",
        }

        try:
            async with self.session.get(self.BASE_URL, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                get_smart_cache().record_provider_usage("brave", success=True)

                results = []
                web_results = data.get("web", {}).get("results", [])
                for idx, result in enumerate(web_results, 1):
                    results.append({
                        "source": "brave",
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "text": result.get("description", ""),
                        "highlights": [],
                        "score": max(0.5, 1.0 - ((idx - 1) * 0.05)),
                        "published_date": "",
                        "age": result.get("age", "") or "",
                        "author": "",
                        "position": idx,
                    })

                return results

        except Exception as e:
            get_smart_cache().record_provider_usage("brave", success=False)
            print(f"Brave search error: {e}")
            return []

    async def search_with_timeout(
        self,
        query: str,
        num_results: int = 8,
        timeout: float = 10.0
    ) -> List[Dict]:
        try:
            return await asyncio.wait_for(
                self.search(query, num_results),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Brave search timeout (> {timeout}s)")
            return []
