"""
查询意图与主体提取
"""
import re


def contains_chinese(text: str) -> bool:
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            return True
    return False


def is_news_query(query: str) -> bool:
    lowered = query.lower()
    chinese_pairs = [
        "最新消息", "最新进展", "局势更新", "最新动态", "最新战况",
        "突发消息", "最新通报",
    ]
    chinese_terms = ["消息", "进展", "动态", "局势", "通报", "快讯", "新闻", "战况", "突发"]
    english_pairs = [
        "latest news", "breaking news", "latest updates",
        "recent developments", "situation update",
    ]
    english_terms = ["news", "updates", "developments", "breaking", "situation"]

    if any(term in query for term in chinese_pairs):
        return True
    if "最新" in query and any(term in query for term in chinese_terms):
        return True
    if any(term in lowered for term in english_pairs):
        return True
    if "latest" in lowered and any(term in lowered for term in english_terms):
        return True
    return False


def is_release_query(query: str) -> bool:
    lowered = query.lower()
    chinese_terms = ["版本", "文档", "发布说明", "更新日志", "变更日志", "发行说明", "最新版"]
    english_terms = ["version", "versions", "docs", "documentation", "release", "release notes", "changelog"]
    return any(term in query for term in chinese_terms) or any(term in lowered for term in english_terms)


def is_troubleshooting_query(query: str) -> bool:
    lowered = query.lower()
    chinese_terms = [
        "报错", "错误", "异常", "失败", "无法", "不能", "卡住",
        "崩溃", "闪退", "修复", "解决", "排查",
    ]
    english_terms = [
        "error", "errors", "exception", "exceptions", "failed", "failure",
        "cannot", "can't", "unable", "fix", "troubleshoot", "issue", "issues",
        "crash", "crashed", "broken", "not working", "doesn't work", "won't start",
        "permission denied", "module not found", "no module named", "traceback",
    ]
    return any(term in query for term in chinese_terms) or any(term in lowered for term in english_terms)


def is_comparison_query(query: str) -> bool:
    lowered = query.lower()
    chinese_terms = ["对比", "区别", "哪个好", "怎么选", "选哪个", "优缺点"]
    english_terms = [
        " vs ", " versus ", "comparison", "which is better", "difference between",
        "tradeoffs", "compare", "or ", "better than", "choose", "should i use",
    ]

    if any(term in query for term in chinese_terms):
        return True
    if any(term in lowered for term in english_terms):
        return True
    if "和" in query and ("区别" in query or "怎么选" in query or "哪个好" in query):
        return True
    if " or " in lowered and any(term in lowered for term in ["for ", "should i", "which", "better"]):
        return True
    return False


def is_freshness_sensitive_query(query: str) -> bool:
    lowered = query.lower()
    chinese_terms = ["怎么样", "如何", "现状", "近况", "最近", "最新", "动态", "进展"]
    english_terms = ["how is", "what's new", "whats new", "current", "recent", "latest", "updates", "status", "now"]
    return any(term in query for term in chinese_terms) or any(term in lowered for term in english_terms)


def get_status_query_subject(query: str) -> str:
    stripped = query.strip()
    if not stripped:
        return stripped

    chinese_patterns = [
        r"^(.*?)(?:最近|当前|现在)(?:怎么样|如何)\??$",
        r"^(.*?)(?:最新动态|最新消息|最新进展|最新情况)\??$",
        r"^(.*?)(?:的)?(?:产品|公司|平台|服务)?(?:怎么样|如何|现状|近况|最近发展|现在如何)\??$",
    ]
    for pattern in chinese_patterns:
        match = re.match(pattern, stripped)
        if match and match.group(1).strip():
            return match.group(1).strip()

    english_patterns = [
        r"^how is\s+(.+?)(?:\s+now|\s+currently|\s+these days)?\??$",
        r"^what(?:'s| is)\s+new with\s+(.+?)\??$",
        r"^(.+?)\s+(?:current status|status|recent updates|latest updates)\??$",
    ]
    lowered = stripped.lower()
    for pattern in english_patterns:
        match = re.match(pattern, lowered)
        if match and match.group(1).strip():
            return match.group(1).strip()

    return stripped


def detect_query_intent(query: str) -> str:
    if is_release_query(query):
        return "release"
    if is_troubleshooting_query(query):
        return "troubleshooting"
    if is_comparison_query(query):
        return "comparison"
    if is_news_query(query):
        return "news"
    if is_freshness_sensitive_query(query):
        return "status"
    return "general"
