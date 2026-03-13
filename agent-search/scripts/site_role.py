"""
站点角色判定
"""
import re
from urllib.parse import urlparse

try:
    from .query_intent import get_status_query_subject
except ImportError:
    from query_intent import get_status_query_subject


COMMUNITY_DOMAINS = [
    "zhihu.com",
    "juejin.cn",
    "csdn.net",
    "cnblogs.com",
    "segmentfault.com",
    "stackoverflow.com",
    "medium.com",
    "dev.to",
    "weixin.qq.com",
    "sohu.com",
    "baidu.com",
    "163.com",
]

CONDITIONAL_PLATFORM_DOMAINS = [
    "cloud.tencent.com",
    "aliyun.com",
]

MEDIA_DOMAINS = [
    "36kr.com",
    "leiphone.com",
    "ifanr.com",
    "huxiu.com",
    "donews.com",
    "techcrunch.com",
    "theverge.com",
    "wired.com",
    "forbes.com",
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "cnn.com",
]

PLATFORM_OFFICIAL_BRANDS = {
    "cloud.tencent.com": ["腾讯云", "tencent cloud"],
    "aliyun.com": ["阿里云", "aliyun", "alibaba cloud"],
    "juejin.cn": ["掘金", "juejin"],
    "zhihu.com": ["知乎", "zhihu"],
    "csdn.net": ["csdn"],
    "cnblogs.com": ["博客园", "cnblogs"],
    "segmentfault.com": ["segmentfault", "思否"],
}


def normalize_domain(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    for prefix in ("www.", "m."):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    return domain


def domain_matches_subject(domain: str, subject: str) -> bool:
    if not domain or not subject:
        return False
    normalized_domain = domain.lower()
    subject_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", subject)
    domain_slug = re.sub(r"[^a-z0-9]+", "", normalized_domain.split(".")[0])
    normalized_domain_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", normalized_domain)
    if subject_slug and (
        subject_slug in normalized_domain_slug
        or (domain_slug and (subject_slug.startswith(domain_slug) or domain_slug.startswith(subject_slug)))
    ):
        return True
    for official_domain, aliases in PLATFORM_OFFICIAL_BRANDS.items():
        if normalized_domain == official_domain or normalized_domain.endswith(f".{official_domain}"):
            return any(alias in subject for alias in aliases)
    return False


def matches_query_brand(result: dict, query_or_subject: str) -> bool:
    """Check if result matches the query brand using only URL and title.

    Snippet text is untrusted third-party content and must not be used
    for brand-matching decisions to prevent injection-based manipulation.
    """
    subject = get_status_query_subject(query_or_subject).lower().strip()
    if not subject:
        return False
    title = (result.get("title", "") or "").lower()
    url = normalize_domain(result.get("url", "")).lower()
    subject_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", subject)
    haystack = " ".join([title, url])
    haystack_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", haystack)
    return subject in haystack or (subject_slug and subject_slug in haystack_slug)


def is_official_update_path(result: dict) -> bool:
    url = (result.get("url", "") or "").lower()
    return any(token in url for token in [
        "/blog", "/news", "/updates", "/update", "/release", "/releases",
        "/announcement", "/announcements", "/press", "/events", "/event",
        "/changelog",
    ])


def classify_site_role(result: dict, query: str = "", subject: str = "") -> str:
    parsed = urlparse(result.get("url", ""))
    domain = normalize_domain(result.get("url", ""))
    current_subject = (subject or get_status_query_subject(query)).strip().lower()
    domain_brand_match = bool(current_subject and domain_matches_subject(domain, current_subject))
    title = (result.get("title", "") or "").lower()
    subject_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", current_subject)
    title_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", title)
    title_brand_match = bool(current_subject and (current_subject in title or (subject_slug and subject_slug in title_slug)))
    has_official_path = is_official_update_path(result)
    path = (parsed.path or "").lower()

    if domain_brand_match:
        return "official"

    if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in CONDITIONAL_PLATFORM_DOMAINS):
        return "republisher"
    if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in MEDIA_DOMAINS):
        return "media"
    if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in COMMUNITY_DOMAINS):
        if any(token in path for token in ["/question", "/questions", "/answer", "/answers", "/post", "/posts", "/article", "/p/"]):
            return "community"
        return "republisher"

    if title_brand_match and has_official_path:
        return "official"
    if title_brand_match and path in {"", "/", "/news"}:
        return "official"
    if title_brand_match and any(token in path for token in [
        "/news", "/blog", "/about", "/product", "/products", "/solution", "/solutions",
        "/press", "/announcement", "/announcements", "/event", "/events", "/bbs",
    ]):
        return "official"
    return "neutral"
