"""
Jina Reader API 客户端 - 内容深度提取
"""
import asyncio
from typing import Optional, Dict
import aiohttp

try:
    from .config import get_api_key
    from .smart_cache import get_smart_cache
except ImportError:
    from config import get_api_key
    from smart_cache import get_smart_cache


class JinaClient:
    """Jina Reader 客户端 - 提取干净的网页内容"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_api_key("JINA_API_KEY")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def should_extract(self, exa_result: Dict) -> tuple[bool, str]:
        """
        判断是否需要使用 Jina Reader 提取内容

        Returns:
            (是否需要提取, 原因)
        """
        text = exa_result.get("text", "")
        score = exa_result.get("score", 0)

        # 条件 1: 内容太短
        if len(text) < 1000:
            return True, f"内容过短 ({len(text)} 字符)，需要提取完整内容"

        # 条件 2: Exa 评分较低
        if score < 0.7:
            return True, f"Exa 评分较低 ({score:.2f})，需要验证内容质量"

        # 条件 3: 噪音检测
        noise_indicators = [
            "Home >", "Navigation", "Menu", "©", "All rights reserved",
            "Privacy Policy", "Terms of Service", "Cookie Policy"
        ]
        noise_count = sum(1 for indicator in noise_indicators if indicator in text)
        if noise_count >= 2:
            return True, "检测到导航/噪音内容，需要净化提取"

        # 条件 4: 内容被截断
        if text.endswith("...") or "Read more" in text[-100:]:
            return True, "内容被截断，需要获取完整版本"

        return False, "Exa 内容质量良好"

    async def extract(self, url: str) -> Optional[Dict]:
        """
        使用 Jina Reader 提取网页内容

        Args:
            url: 网页 URL

        Returns:
            提取的内容字典，失败返回 None
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Jina Reader 免费端点
        reader_url = f"https://r.jina.ai/{url}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with self.session.get(reader_url, headers=headers) as response:
                response.raise_for_status()
                content = await response.text()

                # 解析内容
                lines = content.split('\n')
                title = lines[0].strip() if lines else ""
                markdown = '\n'.join(lines[1:]).strip() if len(lines) > 1 else content

                return {
                    "title": title,
                    "markdown": markdown,
                    "url": url,
                    "length": len(markdown)
                }

        except Exception as e:
            print(f"Jina Reader 提取失败 {url[:50]}...: {e}")
            return None

    async def extract_with_timeout(
        self,
        url: str,
        timeout: float = 5.0
    ) -> Optional[Dict]:
        """带超时的提取"""
        try:
            return await asyncio.wait_for(
                self.extract(url),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Jina Reader 超时 (> {timeout}s): {url[:50]}...")
            return None

    async def extract_multiple(
        self,
        urls: list[str],
        max_concurrent: int = 3,
        cache_ttl: int = 21600
    ) -> Dict[str, Optional[Dict]]:
        """
        批量提取多个 URL 的内容

        Args:
            urls: URL 列表
            max_concurrent: 最大并发数

        Returns:
            URL -> 内容的映射字典
        """
        cache = get_smart_cache()
        cached_results: Dict[str, Optional[Dict]] = {}
        uncached_urls = []

        for url in urls:
            cached = cache.get_cached_content(url)
            if cached is not None:
                cached_results[url] = cached
            else:
                uncached_urls.append(url)

        if not uncached_urls:
            return cached_results

        semaphore = asyncio.Semaphore(max_concurrent)

        async def extract_with_limit(url):
            async with semaphore:
                return url, await self.extract_with_timeout(url)

        tasks = [extract_with_limit(url) for url in uncached_urls]
        results = await asyncio.gather(*tasks)

        fetched_results = {}
        for url, content in results:
            fetched_results[url] = content
            if content is not None:
                cache.set_cached_content(url, content, ttl=cache_ttl)

        return {**cached_results, **fetched_results}
