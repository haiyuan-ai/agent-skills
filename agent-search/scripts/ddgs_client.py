"""
DDGS (DuckDuckGo Search) 客户端 - 零配置搜索兜底

无需 API Key，基于 ddgs 库。
用作无 API Key 时的 fallback 或用户显式指定 --source ddgs 时的搜索源。
"""
import asyncio
from typing import List, Dict, Optional

try:
    from .smart_cache import get_smart_cache
except ImportError:
    from smart_cache import get_smart_cache


class DdgsClient:
    """DDGS 搜索客户端"""

    def __init__(self):
        self._ddgs = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    def _do_search(self, query: str, num_results: int) -> List[Dict]:
        """同步搜索（在线程中调用）"""
        from ddgs import DDGS

        raw = DDGS().text(query, max_results=num_results)
        results = []
        for idx, item in enumerate(raw, 1):
            results.append({
                "source": "ddgs",
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "text": item.get("body", ""),
                "highlights": [],
                "score": max(0.5, 1.0 - ((idx - 1) * 0.05)),
                "published_date": "",
                "author": "",
                "position": idx,
            })
        return results

    async def search(self, query: str, num_results: int = 8) -> List[Dict]:
        """异步搜索（通过 asyncio.to_thread 包装同步调用）"""
        try:
            results = await asyncio.to_thread(self._do_search, query, num_results)
            get_smart_cache().record_provider_usage("ddgs", success=True)
            return results
        except Exception as e:
            get_smart_cache().record_provider_usage("ddgs", success=False)
            print(f"DDGS search error: {e}")
            return []

    async def search_with_timeout(
        self,
        query: str,
        num_results: int = 8,
        timeout: float = 10.0,
    ) -> List[Dict]:
        """带超时的搜索"""
        try:
            return await asyncio.wait_for(
                self.search(query, num_results),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            print(f"DDGS search timeout (> {timeout}s)")
            return []
