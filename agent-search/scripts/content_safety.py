"""
第三方搜索内容安全处理。

原则：
- 只保留短摘要，不保留或回传整页正文
- 将第三方内容显式标记为 untrusted
- 清理常见 prompt injection / 指令劫持语句
"""
from __future__ import annotations

import re
from typing import Dict, Iterable


INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+(all|any|the)?\s*(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all|any|the)?\s*(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"(system|developer)\s+prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+(chatgpt|claude|an?\s+ai|a\s+helpful\s+assistant)", re.IGNORECASE),
    re.compile(r"(follow|execute|obey)\s+these\s+instructions", re.IGNORECASE),
    re.compile(r"(tool\s+call|function\s+call|browser\s+tool|web\s+search)", re.IGNORECASE),
    re.compile(r"(reveal|show|print)\s+(the\s+)?(system|hidden|developer)\s+(prompt|instructions?)", re.IGNORECASE),
    re.compile(r"(do not|don't)\s+mention", re.IGNORECASE),
)

MAX_SNIPPET_CHARS = 700


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_untrusted_text(text: str, max_chars: int = MAX_SNIPPET_CHARS) -> str:
    """清洗不可信第三方文本，只保留低风险摘要。"""
    if not text:
        return ""

    cleaned_lines = []
    for raw_line in _normalize_whitespace(text).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(pattern.search(line) for pattern in INJECTION_PATTERNS):
            continue
        cleaned_lines.append(line)

    cleaned = " ".join(cleaned_lines)
    cleaned = re.sub(r"`{3,}.*?`{3,}", " ", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if len(cleaned) > max_chars:
        return cleaned[: max_chars - 3].rstrip() + "..."
    return cleaned


def pick_search_snippet(result: Dict) -> str:
    """从搜索结果中挑选可安全展示的短摘要。"""
    highlights = result.get("highlights") or []
    candidates: Iterable[str] = list(highlights) + [result.get("text", "")]
    for candidate in candidates:
        snippet = sanitize_untrusted_text(candidate)
        if snippet:
            return snippet
    return ""


def apply_content_safety(result: Dict) -> Dict:
    """将搜索结果改写为只包含安全摘要。"""
    snippet = pick_search_snippet(result)
    result["text"] = snippet
    result["content"] = snippet
    result["content_source"] = "search_snippet"
    result["content_trust"] = "untrusted-sanitized"
    result["content_preview_only"] = True
    return result
