"""
Deprecated compatibility shim.

This skill no longer performs runtime full-page extraction from third-party URLs.
The previous Jina Reader integration was removed to reduce prompt injection risk
and to avoid loading arbitrary external page content into agent context.
"""
from __future__ import annotations

from typing import Dict, Optional


class JinaClient:
    """Compatibility stub that performs no remote extraction."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

    def should_extract(self, exa_result: Dict) -> tuple[bool, str]:
        return False, "Remote page extraction has been disabled for security reasons"

    async def extract(self, url: str) -> Optional[Dict]:
        return None

    async def extract_with_timeout(
        self,
        url: str,
        timeout: float = 3.0
    ) -> Optional[Dict]:
        return None

    async def extract_multiple(
        self,
        urls: list[str],
        max_concurrent: int = 3,
        cache_ttl: int = 21600
    ) -> Dict[str, Optional[Dict]]:
        return {url: None for url in urls}
