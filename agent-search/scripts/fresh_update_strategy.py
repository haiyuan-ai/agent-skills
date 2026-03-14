"""
status/release 共享搜索策略
"""
from datetime import datetime
from typing import Dict, List, Literal, Optional
import re

try:
    from .query_intent import contains_chinese, detect_query_intent, get_status_query_subject
    from .result_processor import QualityScorer
    from .site_role import classify_site_role, normalize_domain
except ImportError:
    from query_intent import contains_chinese, detect_query_intent, get_status_query_subject
    from result_processor import QualityScorer
    from site_role import classify_site_role, normalize_domain


def is_fresh_update_intent(intent: str) -> bool:
    return intent in {"status", "release"}


def score_official_domain_candidate(subject: str, result: Dict) -> float:
    domain = normalize_domain(result.get("url", ""))
    site_role = classify_site_role(result, subject=subject)
    if not domain or site_role in {"republisher", "community"}:
        return 0.0
    if site_role == "media":
        return 0.2

    subject_lower = subject.lower().strip()
    title = (result.get("title", "") or "").lower()
    url = (result.get("url", "") or "").lower()
    # Only use URL and title for official domain scoring.
    # Snippet text is untrusted third-party content and must not
    # influence which domains are considered "official".
    haystack = " ".join([title, url])

    if subject_lower not in haystack:
        return 0.0
    if any(token in title for token in ["怎么样", "评价", "评测", "review", "faq", "问答"]):
        return 0.0
    if any(token in url for token in ["/question/", "/answer/", "/faq", "/blog/article"]):
        return 0.0

    score = 1.0
    brand_slug = re.sub(r"[^a-z0-9]+", "", subject_lower)
    domain_slug = re.sub(r"[^a-z0-9]+", "", domain.split(".")[0])

    if subject_lower in title:
        score += 1.0
    if subject_lower in url:
        score += 0.6
    if brand_slug and brand_slug in domain.replace(".", ""):
        score += 1.6
    if domain_slug and brand_slug and (domain_slug == brand_slug or brand_slug.startswith(domain_slug) or domain_slug.startswith(brand_slug)):
        score += 0.8
    if any(token in url for token in ["/blog", "/news", "/updates", "/update", "/release", "/announcement", "/events", "/bbs", "/about", "/product", "/products"]):
        score += 0.8
    if any(token in title for token in ["官网", "official", "发布", "更新", "动态", "launch", "update", "release"]):
        score += 0.4
    if "github.com/" in url:
        score += 0.5

    return score


def discover_official_domains(subject: str, results: List[Dict], limit: int = 1) -> List[str]:
    subject_lower = subject.lower().strip()
    if not subject_lower:
        return []

    domain_scores: Dict[str, float] = {}
    domain_hits: Dict[str, int] = {}

    for result in results:
        domain = normalize_domain(result.get("url", ""))
        score = score_official_domain_candidate(subject, result)
        if score <= 0:
            continue
        domain_scores[domain] = domain_scores.get(domain, 0.0) + score
        domain_hits[domain] = domain_hits.get(domain, 0) + 1

    ranked_domains = sorted(
        domain_scores.items(),
        key=lambda item: (item[1], domain_hits.get(item[0], 0)),
        reverse=True,
    )
    return [domain for domain, score in ranked_domains if score >= 1.5][:limit]


def build_status_site_queries(query: str, results: List[Dict], limit: int = 2) -> List[str]:
    subject = get_status_query_subject(query)
    candidate_domains = discover_official_domains(subject, results, limit=1)
    if not candidate_domains:
        return []

    domain = candidate_domains[0]
    if contains_chinese(query):
        queries = [
            f"site:{domain} {subject} 产品更新",
            f"site:{domain} {subject} 公司动态",
        ]
    else:
        queries = [
            f"site:{domain} {subject} official blog updates",
            f"site:{domain} {subject} company news",
        ]
    return list(dict.fromkeys(queries))[:limit]


def build_status_discovery_queries(query: str) -> List[str]:
    subject = get_status_query_subject(query)
    if not subject:
        return []
    if contains_chinese(query):
        return [f"{subject} 官网"]
    return [f"{subject} official website"]


def get_query_source_plan(
    intent: str,
    query_index: int,
    has_exa: bool,
    use_brave: bool,
    use_tavily: bool,
    query: str = "",
) -> Dict[str, bool]:
    if is_fresh_update_intent(intent):
        return {"exa": has_exa, "brave": use_brave, "tavily": use_tavily}

    if query_index == 0:
        return {
            "exa": has_exa and not use_tavily and not use_brave,
            "brave": use_brave and not use_tavily,
            "tavily": use_tavily,
        }

    if intent in {"news", "troubleshooting"}:
        return {"exa": False, "brave": use_brave, "tavily": use_tavily}

    return {
        "exa": has_exa and not use_tavily and not use_brave,
        "brave": use_brave and not use_tavily,
        "tavily": use_tavily,
    }


def get_tavily_options(intent: str, mode: Literal["quick", "standard", "deep"]) -> Dict[str, str]:
    return {
        "search_depth": "advanced" if mode == "deep" else "basic",
        "topic": "news" if intent == "news" else "general",
    }


def get_max_queries_for_intent(intent: str, query: str) -> int:
    query_length = len(query.strip())
    if intent == "general":
        return 2
    if intent in {"status", "release"}:
        return 4
    if intent == "comparison":
        return 3
    if intent == "news":
        return 3
    if intent == "troubleshooting":
        return 2 if query_length >= 24 else 3
    return 3


def should_early_stop(results: List[Dict], max_results: int, intent: str, query: str = "") -> bool:
    """
    判断是否满足质量要求，可以提前停止搜索。

    阈值设定依据（基于经验值和意图特性）：
    - general: top1≥0.82, top3_avg≥0.76 - 通用查询质量要求适中
    - release/status: top1≥0.86, top3_avg≥0.80 - 时效性敏感，要求更高质量
    - troubleshooting: top1≥0.84, top3_avg≥0.78 - 错误排查需要准确结果
    - comparison: top1≥0.83, top3_avg≥0.75 - 对比查询需要多样性
    - news: top1≥0.82, top3_avg≥0.74 - 新闻查询时效优先
    """
    if len(results) < max_results:
        return False
    if intent == "status":
        return False

    ranked = QualityScorer.rank([dict(r) for r in results], intent=intent, query=query)
    if len(ranked) < 3:
        return False

    top_three = ranked[:3]
    top_three_avg = sum(r.get("final_score", r.get("quality_score", 0.0)) for r in top_three) / 3
    top_one_score = top_three[0].get("final_score", top_three[0].get("quality_score", 0.0))

    if intent == "general":
        return top_one_score >= 0.82 and top_three_avg >= 0.76
    if is_fresh_update_intent(intent):
        return top_one_score >= 0.86 and top_three_avg >= 0.8
    if intent == "troubleshooting":
        return top_one_score >= 0.84 and top_three_avg >= 0.78
    return False


def should_use_exa_fallback(
    results: List[Dict],
    max_results: int,
    intent: str,
    depth: str,
    has_exa: bool,
) -> bool:
    """
    判断是否需要使用 Exa 作为后备搜索源。

    阈值设定依据：
    - 当现有搜索结果质量低于预期时触发 Exa 补充
    - 不同意图有不同的质量预期（参见 should_early_stop 的阈值说明）
    - deep 模式始终启用 Exa 以获得更全面结果
    """
    if not has_exa:
        return False
    if depth == "deep":
        return True
    if len(results) < max_results:
        return True

    ranked = QualityScorer.rank([dict(r) for r in results], intent=intent, query="")
    if not ranked:
        return True

    top_one_score = ranked[0].get("final_score", ranked[0].get("quality_score", 0.0))
    top_three = ranked[:3]
    if len(top_three) < 3:
        return True
    top_three_avg = sum(r.get("final_score", r.get("quality_score", 0.0)) for r in top_three) / 3

    thresholds = {
        # (top_one_threshold, top_three_threshold)
        # 阈值含义：低于该值表示结果质量不足，需要 Exa 补充
        "general": (0.66, 0.65),       # 通用查询：质量要求相对较低
        "status": (0.84, 0.76),        # 近况查询：需要高质量结果
        "release": (0.84, 0.76),       # 发布查询：需要高质量结果
        "troubleshooting": (0.84, 0.76),  # 错误排查：需要准确结果
        "comparison": (0.83, 0.75),    # 对比查询：需要多样化高质量结果
        "news": (0.82, 0.74),          # 新闻查询：时效优先，质量要求略低
    }
    top_one_threshold, top_three_threshold = thresholds.get(intent, (0.8, 0.72))
    return top_one_score < top_one_threshold or top_three_avg < top_three_threshold


def has_stale_status_results(results: List[Dict], current_year: Optional[int] = None) -> bool:
    if not results:
        return True
    if current_year is None:
        current_year = datetime.now().year

    ranked = QualityScorer.rank([dict(r) for r in results], intent="status", query="")
    top_results = ranked[:5]
    if not top_results:
        return True

    dated_count = 0
    recent_count = 0
    for result in top_results:
        effective_date = result.get("quality_breakdown", {}).get("effective_published_date", "")
        if not effective_date:
            continue
        dated_count += 1
        if effective_date.startswith(str(current_year)) or effective_date.startswith(str(current_year - 1)):
            recent_count += 1

    if dated_count == 0:
        return True
    return recent_count == 0 or dated_count < max(2, len(top_results) // 2)


def expand_query(query: str) -> List[str]:
    queries = [query]
    intent = detect_query_intent(query)

    if intent == "news":
        if contains_chinese(query):
            for term in ["最新消息", "最新进展", "局势更新"]:
                if term not in query:
                    queries.append(f"{query} {term}")
        else:
            queries.extend([f"{query} latest updates {datetime.now().year}", f"{query} breaking news"])
    elif intent == "release":
        if contains_chinese(query):
            queries.extend([f"{query} 发布说明", f"{query} 更新日志", f"{query} 官方文档"])
        else:
            queries.extend([f"{query} release notes", f"{query} changelog", f"{query} official docs"])
    elif intent == "troubleshooting":
        if contains_chinese(query):
            queries.extend([f"{query} 解决方案", f"{query} GitHub issue"])
        else:
            queries.extend([f"{query} fix", f"{query} github issue"])
    elif intent == "comparison":
        if contains_chinese(query):
            queries.extend([f"{query} 优缺点", f"{query} 怎么选"])
        else:
            queries.extend([f"{query} pros and cons", f"{query} comparison"])
    elif "是什么" in query or "what is" in query.lower():
        queries.extend([
            query.replace("是什么", "介绍").replace("what is", "introduction to"),
            query + " 教程" if contains_chinese(query) else query + " tutorial",
        ])
    elif "怎么用" in query or "how to" in query.lower():
        queries.extend([
            query.replace("怎么用", "使用教程"),
            query + " 示例" if contains_chinese(query) else query + " examples",
        ])
    elif intent == "status":
        subject = get_status_query_subject(query)
        if contains_chinese(query):
            queries.extend([f"{subject} 官网 产品更新", f"{subject} 发布会", f"{subject} 公司动态"])
        else:
            queries.extend([f"{subject} official blog updates", f"{subject} changelog", f"{subject} current status"])
    else:
        if contains_chinese(query):
            queries.extend([query + " 教程", query + " 示例", query + " 评测"])
        else:
            queries.extend([query + " tutorial", query + " examples", query + " review"])

    return list(dict.fromkeys(queries))


def _effective_date(result: Dict) -> str:
    return result.get("quality_breakdown", {}).get("effective_published_date", "") or result.get("published_date", "")


def _status_result_type(result: Dict, query: str) -> str:
    role = classify_site_role(result, query=query)
    title = (result.get("title", "") or "").lower()
    url = (result.get("url", "") or "").lower()
    haystack = " ".join([title, url])

    event_tokens = ["发布会", "大会", "峰会", "conference", "summit", "event", "webinar", "launch event"]
    review_tokens = ["评测", "评价", "怎么样", "review", "faq", "问答"]
    product_tokens = ["产品更新", "功能更新", "更新报告", "发布说明", "更新日志", "release", "changelog", "update report"]

    if role in {"community", "republisher", "media"} and any(token in haystack for token in review_tokens):
        return "third_party_review"
    if role in {"community", "republisher", "media"}:
        return "third_party_coverage"
    if any(token in haystack for token in event_tokens):
        return "event"
    if any(token in haystack for token in product_tokens):
        return "product_update"
    if role == "official":
        return "company_update"
    return "other"


def _serialize_status_result(result: Dict, query: str) -> Dict:
    return {
        "title": result.get("title", ""),
        "url": result.get("url", ""),
        "effective_published_date": _effective_date(result),
        "site_role": classify_site_role(result, query=query),
        "status_result_type": _status_result_type(result, query),
        "source": result.get("source", ""),
        "final_score": result.get("final_score", result.get("quality_score", result.get("score", 0.0))),
    }


def _build_status_highlights(summary: Dict) -> List[str]:
    highlights = []
    label_map = [
        ("latest_official_update", "最近官方动态"),
        ("latest_product_update", "最近产品更新"),
        ("latest_event", "最近活动动态"),
        ("latest_company_update", "最近公司动态"),
        ("latest_third_party_review", "最近第三方评价"),
    ]
    seen_urls = set()
    for field, label in label_map:
        item = summary.get(field)
        if not item or item.get("url") in seen_urls:
            continue
        seen_urls.add(item.get("url"))
        date_text = item.get("effective_published_date") or "日期未知"
        highlights.append(f"{label}: {date_text} | {item.get('title', '')}")
    return highlights


def build_status_summary(results: List[Dict], query: str, as_of_date: Optional[str] = None) -> Dict:
    if as_of_date is None:
        as_of_date = datetime.now().strftime("%Y-%m-%d")

    def rank_key(result: Dict):
        return (
            _effective_date(result) or "",
            result.get("final_score", result.get("quality_score", result.get("score", 0.0))),
        )

    official_results = [r for r in results if classify_site_role(r, query=query) == "official"]
    official_with_dates = sorted([r for r in official_results if _effective_date(r)], key=rank_key, reverse=True)
    latest_official = official_with_dates[0] if official_with_dates else (official_results[0] if official_results else None)

    summary = {
        "as_of_date": as_of_date,
        "latest_official_update": _serialize_status_result(latest_official, query) if latest_official else None,
    }

    for field, result_type in [
        ("latest_product_update", "product_update"),
        ("latest_event", "event"),
        ("latest_company_update", "company_update"),
        ("latest_third_party_review", "third_party_review"),
    ]:
        typed_results = [r for r in results if _status_result_type(r, query) == result_type]
        typed_results = sorted(typed_results, key=rank_key, reverse=True)
        summary[field] = _serialize_status_result(typed_results[0], query) if typed_results else None

    summary["highlights"] = _build_status_highlights(summary)
    return summary
