"""
Agent Search - 智能 Agent 搜索工具

为 AI Agent 提供深度、结构化的搜索能力。
支持 Claude Code、OpenCode、Gemini CLI、Codex CLI 等。
"""
import asyncio
import copy
import contextlib
import re
from datetime import datetime
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass

STRATEGY_VERSION = "v22"

try:
    from .exa_client import ExaClient
    from .brave_client import BraveClient
    from .tavily_client import TavilyClient
    from .jina_client import JinaClient
    from .result_processor import ResultMerger, QualityScorer
    from .config import get_api_key, get_config
    from .smart_cache import get_smart_cache
except ImportError:
    from exa_client import ExaClient
    from brave_client import BraveClient
    from tavily_client import TavilyClient
    from jina_client import JinaClient
    from result_processor import ResultMerger, QualityScorer
    from config import get_api_key, get_config
    from smart_cache import get_smart_cache


@dataclass
class SearchConfig:
    """搜索配置"""
    exa_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    jina_api_key: Optional[str] = None
    max_results: int = 10
    brave_max_results: int = 8
    tavily_max_results: int = 8
    mode: Literal["quick", "standard", "deep"] = "standard"
    enable_brave: bool = True  # 默认仅在部分意图下作为补充
    enable_tavily: bool = True  # 默认启用 Tavily 作为主搜索引擎


def contains_chinese(text: str) -> bool:
    """检测文本是否包含中文字符"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def is_news_query(query: str) -> bool:
    """检测查询是否偏向新闻/动态检索"""
    lowered = query.lower()
    chinese_pairs = [
        "最新消息", "最新进展", "局势更新", "最新动态", "最新战况",
        "突发消息", "最新通报"
    ]
    chinese_terms = ["消息", "进展", "动态", "局势", "通报", "快讯", "新闻", "战况", "突发"]
    english_pairs = [
        "latest news", "breaking news", "latest updates",
        "recent developments", "situation update"
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
    """检测查询是否偏向版本/发布说明/文档检索"""
    lowered = query.lower()
    chinese_terms = ["版本", "文档", "发布说明", "更新日志", "变更日志", "发行说明", "最新版"]
    english_terms = ["version", "versions", "docs", "documentation", "release", "release notes", "changelog"]

    if any(term in query for term in chinese_terms):
        return True
    if any(term in lowered for term in english_terms):
        return True
    return False


def is_troubleshooting_query(query: str) -> bool:
    """检测查询是否偏向报错排查/修复"""
    lowered = query.lower()
    chinese_terms = [
        "报错", "错误", "异常", "失败", "无法", "不能", "卡住",
        "崩溃", "闪退", "修复", "解决", "排查"
    ]
    english_terms = [
        "error", "errors", "exception", "exceptions", "failed", "failure",
        "cannot", "can't", "unable", "fix", "troubleshoot", "issue", "issues",
        "crash", "crashed", "broken", "not working", "doesn't work", "won't start",
        "permission denied", "module not found", "no module named", "traceback"
    ]

    if any(term in query for term in chinese_terms):
        return True
    if any(term in lowered for term in english_terms):
        return True
    return False


def is_comparison_query(query: str) -> bool:
    """检测查询是否偏向方案对比/决策"""
    lowered = query.lower()
    chinese_terms = ["对比", "区别", "哪个好", "怎么选", "选哪个", "优缺点"]
    english_terms = [
        " vs ", " versus ", "comparison", "which is better", "difference between",
        "tradeoffs", "compare", "or ", "better than", "choose", "should i use"
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


def detect_query_intent(query: str) -> Literal["news", "status", "troubleshooting", "comparison", "release", "general"]:
    """识别查询主意图，用于扩展和排序"""
    if is_release_query(query):
        return "release"
    if is_troubleshooting_query(query):
        return "troubleshooting"
    if is_news_query(query):
        return "news"
    if is_freshness_sensitive_query(query):
        return "status"
    if is_comparison_query(query):
        return "comparison"
    return "general"


def is_fresh_update_intent(intent: str) -> bool:
    """status/release 共享“新近官方更新”检索策略"""
    return intent in {"status", "release"}


def is_freshness_sensitive_query(query: str) -> bool:
    """检测查询是否虽非新闻意图，但明显依赖较新的信息"""
    lowered = query.lower()
    chinese_terms = ["怎么样", "如何", "现状", "近况", "最近", "最新", "动态", "进展"]
    english_terms = ["how is", "what's new", "whats new", "current", "recent", "latest", "updates", "status", "now"]

    if any(term in query for term in chinese_terms):
        return True
    if any(term in lowered for term in english_terms):
        return True
    return False


def get_status_query_subject(query: str) -> str:
    """提取 status 查询里的主体，避免扩展词继续带着“怎么样/如何”"""
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


def normalize_candidate_domain(url: str) -> str:
    return QualityScorer._normalize_domain(url)


def domain_matches_subject(domain: str, subject: str) -> bool:
    return QualityScorer._domain_matches_subject(domain, (subject or "").strip().lower())


def is_generic_content_domain(domain: str, subject: str = "") -> bool:
    site_role = QualityScorer.classify_site_role({"url": f"https://{domain}"}, subject=subject)
    return site_role in {"republisher", "community"}


def is_media_domain(domain: str) -> bool:
    site_role = QualityScorer.classify_site_role({"url": f"https://{domain}"})
    return site_role == "media"


def score_official_domain_candidate(subject: str, result: Dict) -> float:
    domain = normalize_candidate_domain(result.get("url", ""))
    site_role = QualityScorer.classify_site_role(result, subject=subject)
    if not domain or site_role in {"republisher", "community"}:
        return 0.0
    if site_role == "media" or is_media_domain(domain):
        return 0.2

    subject_lower = subject.lower().strip()
    title = (result.get("title", "") or "").lower()
    text = (result.get("text", "") or "").lower()
    url = (result.get("url", "") or "").lower()
    haystack = " ".join([title, text, url])

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
    if any(token in text for token in ["copyright", "版权所有", "联系我们", "about us", "company", "产品", "解决方案"]):
        score += 0.3

    return score


def discover_official_domains(subject: str, results: List[Dict], limit: int = 1) -> List[str]:
    """从已召回结果中估计更像官方站点的候选域名，用于 status 二次定向查询"""
    subject_lower = subject.lower().strip()
    if not subject_lower:
        return []

    domain_scores: Dict[str, float] = {}
    domain_hits: Dict[str, int] = {}

    for result in results:
        domain = normalize_candidate_domain(result.get("url", ""))
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
    """基于候选官方域名生成 status 的 site 定向查询"""
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
    """为 status 查询补一个通用的官网发现查询，不依赖任何品牌白名单"""
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
    """
    根据查询意图和扩展查询序号，决定本轮使用哪些搜索源

    query_index=0 表示原始查询，后续为扩展查询。
    """
    if is_fresh_update_intent(intent):
        return {
            "exa": has_exa,
            "brave": use_brave,
            "tavily": use_tavily,
        }

    # Tavily 作为默认主引擎；没有 Tavily 时再退回 Brave。
    if query_index == 0:
        return {
            "exa": has_exa and not use_tavily and not use_brave,
            "brave": use_brave and not use_tavily,
            "tavily": use_tavily,
        }

    # 更偏网页命中的查询，在 Tavily 基础上允许 Brave 补充。
    if intent in {"news", "troubleshooting"}:
        return {
            "exa": False,
            "brave": use_brave,
            "tavily": use_tavily,
        }

    # general / comparison 默认仍以 Tavily 为主；无 Tavily 时退回 Brave。
    return {
        "exa": has_exa and not use_tavily and not use_brave,
        "brave": use_brave and not use_tavily,
        "tavily": use_tavily,
    }


def get_tavily_options(
    intent: str,
    mode: Literal["quick", "standard", "deep"]
) -> Dict[str, str]:
    """根据搜索意图和模式生成 Tavily 参数"""
    return {
        "search_depth": "advanced" if mode == "deep" else "basic",
        "topic": "news" if intent == "news" else "general",
    }


def _start_cache_warmup(cache, cache_id: Optional[int], query: str) -> None:
    """在后台预热向量缓存，不阻塞搜索返回"""
    if not cache_id or not getattr(cache, "vector_search_available", False):
        return

    task = asyncio.create_task(cache.warm_vector(cache_id, query))

    def _consume_error(done_task: asyncio.Task) -> None:
        with contextlib.suppress(asyncio.CancelledError, Exception):
            done_task.result()

    task.add_done_callback(_consume_error)


def get_max_queries_for_intent(intent: str, query: str) -> int:
    """
    根据查询意图和查询长度，限制扩展查询数量
    """
    query_length = len(query.strip())

    if intent == "general":
        return 2
    if intent == "status":
        return 4
    if intent == "release":
        return 4
    if intent == "comparison":
        return 3
    if intent == "news":
        return 3
    if intent == "troubleshooting":
        if query_length >= 24:
            return 2
        return 3
    return 3


def get_jina_extraction_limit(intent: str, depth: str, result_count: int) -> int:
    """
    根据查询意图和深度，限制 Jina 正文提取数量
    """
    if depth == "quick" or result_count <= 0:
        return 0

    intent_limits = {
        "release": 3,
        "status": 3,
        "troubleshooting": 3,
        "news": 3,
        "comparison": 2,
        "general": 2,
    }

    if depth == "deep":
        return result_count

    return min(result_count, intent_limits.get(intent, 2))


def get_jina_cache_ttl(intent: str) -> int:
    """按意图设置 Jina 正文缓存 TTL"""
    ttl_map = {
        "news": 900,
        "status": 21600,
        "release": 21600,
        "troubleshooting": 86400,
        "comparison": 86400,
        "general": 21600,
    }
    return ttl_map.get(intent, 21600)


def should_early_stop(
    results: List[Dict],
    max_results: int,
    intent: str,
    query: str = "",
) -> bool:
    """
    判断首轮查询结果是否足够好，从而跳过后续扩展查询
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

    # 版本/文档与通用查询更适合早停；新闻和对比更依赖补充结果
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
    has_exa: bool
) -> bool:
    """
    判断是否需要在 Tavily/Brave 之后补充 Exa 语义搜索
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
        # general 默认先走 Tavily，必要时再加 Brave。普通网页在当前评分模型下
        # 很难达到官方文档/高权威域名的分数，因此需要更宽松的补 Exa 阈值。
        "general": (0.66, 0.65),
        "status": (0.84, 0.76),
        "release": (0.84, 0.76),
        "troubleshooting": (0.84, 0.76),
        "comparison": (0.83, 0.75),
        "news": (0.82, 0.74),
    }
    top_one_threshold, top_three_threshold = thresholds.get(intent, (0.8, 0.72))
    return top_one_score < top_one_threshold or top_three_avg < top_three_threshold


def has_stale_status_results(results: List[Dict], current_year: Optional[int] = None) -> bool:
    """判断 status 查询首轮结果是否明显偏旧或缺少时间信息"""
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
    """
    将查询扩展为多个互补查询

    使用模板策略快速扩展查询
    """
    queries = [query]  # 原始查询

    # 检测查询类型并扩展
    intent = detect_query_intent(query)

    if intent == "news":
        if contains_chinese(query):
            base_query = query
            for term in ["最新消息", "最新进展", "局势更新"]:
                if term not in query:
                    queries.append(f"{base_query} {term}")
        else:
            queries.extend([
                f"{query} latest updates {datetime.now().year}",
                f"{query} breaking news"
            ])
    elif intent == "release":
        if contains_chinese(query):
            queries.extend([
                f"{query} 发布说明",
                f"{query} 更新日志",
                f"{query} 官方文档",
            ])
        else:
            queries.extend([
                f"{query} release notes",
                f"{query} changelog",
                f"{query} official docs",
            ])
    elif intent == "troubleshooting":
        if contains_chinese(query):
            queries.extend([
                f"{query} 解决方案",
                f"{query} GitHub issue"
            ])
        else:
            queries.extend([
                f"{query} fix",
                f"{query} github issue"
            ])
    elif intent == "comparison":
        if contains_chinese(query):
            queries.extend([
                f"{query} 优缺点",
                f"{query} 怎么选"
            ])
        else:
            queries.extend([
                f"{query} pros and cons",
                f"{query} comparison"
            ])
    elif "是什么" in query or "what is" in query.lower():
        # 定义型查询
        queries.extend([
            query.replace("是什么", "介绍").replace("what is", "introduction to"),
            query + " 教程" if contains_chinese(query) else query + " tutorial"
        ])
    elif "怎么用" in query or "how to" in query.lower():
        # 教程型查询
        queries.extend([
            query.replace("怎么用", "使用教程"),
            query + " 示例" if contains_chinese(query) else query + " examples"
        ])
    elif "vs" in query.lower() or "对比" in query or "比较" in query:
        # 对比型查询
        queries.extend([
            query + " 优缺点",
            query + " review" if not contains_chinese(query) else query + " 评测"
        ])
    elif intent == "status":
        subject = get_status_query_subject(query)
        if contains_chinese(query):
            queries.extend([
                f"{subject} 官网 产品更新",
                f"{subject} 发布会",
                f"{subject} 公司动态",
            ])
        else:
            queries.extend([
                f"{subject} official blog updates",
                f"{subject} changelog",
                f"{subject} current status",
            ])
    else:
        # 通用扩展
        if contains_chinese(query):
            queries.extend([
                f"{query} 最新",
                f"{query} 教程"
            ])
        else:
            queries.extend([
                f"{query} latest {datetime.now().year}",
                f"{query} tutorial guide"
            ])

    # 去重并按意图限制扩展数量
    max_queries = get_max_queries_for_intent(intent, query)
    return list(dict.fromkeys(queries))[:max_queries]


class AgentSearch:
    """Agent Search 主类"""

    def __init__(self, config: SearchConfig):
        self.config = config

    async def search_single(
        self,
        query: str,
        exa: Optional['ExaClient'] = None,
        brave: Optional['BraveClient'] = None,
        tavily: Optional['TavilyClient'] = None,
        intent: str = "general",
    ) -> List[Dict]:
        """
        执行单次搜索（Exa、Brave、Tavily 并行）

        Args:
            query: 搜索查询
            exa: 复用的 ExaClient 实例
            brave: 复用的 BraveClient 实例
            tavily: 复用的 TavilyClient 实例

        Returns:
            搜索结果列表
        """
        tasks = []
        task_sources = []

        if exa:
            tasks.append(exa.search_with_timeout(query, self.config.max_results))
            task_sources.append('exa')
        if brave:
            tasks.append(brave.search_with_timeout(query, self.config.brave_max_results))
            task_sources.append('brave')
        if tavily:
            tavily_options = get_tavily_options(intent, self.config.mode)
            tasks.append(
                tavily.search_with_timeout(
                    query,
                    self.config.tavily_max_results,
                    search_depth=tavily_options["search_depth"],
                    topic=tavily_options["topic"],
                )
            )
            task_sources.append('tavily')

        if not tasks:
            print(f"   ⚠️ 无可用搜索源")
            return []

        results_list = await asyncio.gather(*tasks)

        # 根据任务来源分配结果
        exa_results = []
        brave_results = []
        tavily_results = []

        for i, results in enumerate(results_list):
            source = task_sources[i]
            if source == 'exa':
                exa_results = results
            elif source == 'brave':
                brave_results = results
            elif source == 'tavily':
                tavily_results = results

        # 合并所有结果
        return ResultMerger.merge_sources(exa_results, brave_results, tavily_results)

    async def search(
        self,
        query: str,
        expand: bool = True
    ) -> Dict:
        """
        执行完整搜索流程

        Args:
            query: 搜索查询
            expand: 是否扩展查询

        Returns:
            结构化搜索结果
        """
        print(f"🔍 开始搜索: {query}")

        # 1. 确定是否使用 Tavily 和 Brave
        use_brave = self.config.enable_brave and self.config.brave_api_key is not None
        use_tavily = self.config.enable_tavily and self.config.tavily_api_key is not None
        if use_tavily:
            print("   启用 Tavily (AI 搜索) 主引擎")
        if use_brave:
            print("   启用 Brave Search 搜索补充")

        # 2. 扩展查询
        queries = expand_query(query) if expand else [query]
        executed_queries = list(queries)
        intent = detect_query_intent(query)
        print(f"   扩展为 {len(queries)} 个查询")
        print(f"   查询意图: {intent}")

        # 3. 创建复用的客户端实例
        has_exa = self.config.exa_api_key is not None
        exa = ExaClient(self.config.exa_api_key) if has_exa else None
        brave = BraveClient(self.config.brave_api_key) if use_brave else None
        tavily = TavilyClient(self.config.tavily_api_key) if use_tavily else None

        try:
            if exa:
                await exa.__aenter__()
            if brave:
                await brave.__aenter__()
            if tavily:
                await tavily.__aenter__()

            # 4. 执行原始查询（默认优先 Tavily，Brave 仅在缺少 Tavily 或特定意图下补充）
            all_results = []
            first_plan = get_query_source_plan(intent, 0, has_exa, use_brave, use_tavily, query=query)
            first_results = await self.search_single(
                queries[0],
                exa=exa if first_plan["exa"] else None,
                brave=brave if first_plan["brave"] else None,
                tavily=tavily if first_plan["tavily"] else None,
                intent=intent,
            )
            print(f"   ✓ '{queries[0]}' 返回 {len(first_results)} 条结果")
            all_results.extend(first_results)

            extra_status_queries: List[str] = []
            if intent == "status" and has_stale_status_results(ResultMerger.deduplicate(all_results)):
                print("   🕒 首轮结果偏旧，继续补充更偏最新动态的结果")
                extra_status_queries = build_status_discovery_queries(query)
                extra_status_queries.extend(build_status_site_queries(query, ResultMerger.deduplicate(all_results)))
                extra_status_queries = list(dict.fromkeys(extra_status_queries))
                if extra_status_queries:
                    print(f"   🎯 补充 {len(extra_status_queries)} 条官方站点定向查询")
                    executed_queries.extend([q for q in extra_status_queries if q not in executed_queries])

            exa_fallback_used = should_use_exa_fallback(
                ResultMerger.deduplicate(all_results),
                self.config.max_results,
                intent,
                self.config.mode,
                has_exa
            )
            if exa_fallback_used:
                print("   ➕ 首轮结果不足，补充 Exa 语义搜索")
                exa_tasks = []
                if exa and not first_plan["exa"]:
                    exa_tasks.append(self.search_single(queries[0], exa=exa, intent=intent))
                exa_followups = queries[1:] + [q for q in extra_status_queries if q not in queries]
                if exa and exa_followups:
                    exa_tasks.extend([self.search_single(q, exa=exa, intent=intent) for q in exa_followups])
                if exa_tasks:
                    exa_results_list = await asyncio.gather(*exa_tasks)
                    exa_queries = ([queries[0]] if exa and not first_plan["exa"] else []) + exa_followups
                    for q, results in zip(exa_queries, exa_results_list):
                        print(f"   ✓ Exa 补充 '{q}' 返回 {len(results)} 条结果")
                        all_results.extend(results)
            if intent != "status" and len(queries) > 1 and should_early_stop(
                ResultMerger.deduplicate(all_results),
                self.config.max_results,
                intent,
                query=query,
            ):
                print("   ⏹️ 首轮结果质量足够，跳过扩展查询")
            else:
                search_tasks = []
                remaining_queries = queries[1:] + [q for q in extra_status_queries if q not in queries]
                for idx, q in enumerate(remaining_queries, start=1):
                    plan = get_query_source_plan(intent, idx, has_exa, use_brave, use_tavily, query=query)
                    search_tasks.append(
                        self.search_single(
                            q,
                            exa=exa if plan["exa"] else None,
                            brave=brave if plan["brave"] else None,
                            tavily=tavily if plan["tavily"] else None,
                            intent=intent,
                        )
                    )

                if search_tasks:
                    results_list = await asyncio.gather(*search_tasks)
                    for q, results in zip(remaining_queries, results_list):
                        print(f"   ✓ '{q}' 返回 {len(results)} 条结果")
                        all_results.extend(results)

                if intent == "status" and has_stale_status_results(ResultMerger.deduplicate(all_results)):
                    late_status_queries = [
                        q for q in build_status_site_queries(query, ResultMerger.deduplicate(all_results))
                        if q not in executed_queries
                    ]
                    if late_status_queries:
                        print(f"   🎯 基于已发现域名，继续补充 {len(late_status_queries)} 条 site 定向查询")
                        executed_queries.extend(late_status_queries)
                        late_tasks = []
                        for idx, q in enumerate(late_status_queries, start=len(queries) + len(extra_status_queries)):
                            plan = get_query_source_plan(intent, idx, has_exa, use_brave, use_tavily, query=query)
                            late_tasks.append(
                                self.search_single(
                                    q,
                                    exa=exa if plan["exa"] else None,
                                    brave=brave if plan["brave"] else None,
                                    tavily=tavily if plan["tavily"] else None,
                                    intent=intent,
                                )
                            )
                        late_results_list = await asyncio.gather(*late_tasks)
                        for q, results in zip(late_status_queries, late_results_list):
                            print(f"   ✓ '{q}' 返回 {len(results)} 条结果")
                            all_results.extend(results)
        finally:
            if exa:
                await exa.__aexit__(None, None, None)
            if brave:
                await brave.__aexit__(None, None, None)
            if tavily:
                await tavily.__aexit__(None, None, None)

        # 5. 去重
        unique_results = ResultMerger.deduplicate(all_results)
        print(f"   去重后: {len(unique_results)} 条")

        if is_fresh_update_intent(intent) and self.config.mode != "quick":
            unique_results = await self._refresh_fresh_update_candidates(unique_results, intent=intent)

        # 6. 质量评分和排序
        ranked_results = QualityScorer.rank(unique_results, intent=intent, query=query)

        # 7. 限制返回数量
        final_results = ranked_results[:self.config.max_results]

        # 8. 仅 deep 模式使用 Jina Reader 深度提取
        if self.config.mode == "deep":
            final_results = await self._enrich_with_jina(final_results, intent=intent)
        else:
            for result in final_results:
                result["content"] = result.get("text", "")
                result["content_source"] = "original"

        # 9. 构建返回结构
        return {
            "query": query,
            "search_queries": executed_queries,
            "sources_used": (["exa"] if has_exa else []) + (["brave"] if use_brave else []) + (["tavily"] if use_tavily else []),
            "total_found": len(all_results),
            "unique_count": len(unique_results),
            "results_returned": len(final_results),
            "results": final_results
        }

    async def _refresh_fresh_update_candidates(self, results: List[Dict], intent: str) -> List[Dict]:
        """为新近官方更新类查询补抓少量候选页正文，用于提取更可靠的日期信号"""
        urls = self._get_fresh_update_refresh_urls(results, intent=intent)
        if not urls:
            return results

        print(f"   📖 补抓 {len(urls)} 条候选页，提取日期信号")
        async with JinaClient(self.config.jina_api_key) as jina:
            contents = await jina.extract_multiple(
                urls,
                max_concurrent=2,
                cache_ttl=get_jina_cache_ttl("status"),
            )

        for result in results:
            content = contents.get(result.get("url", ""))
            if content and content.get("markdown"):
                result["text"] = content["markdown"]
                result["rerank_source"] = "jina"
        return results

    def _get_fresh_update_refresh_urls(self, results: List[Dict], intent: str) -> List[str]:
        ranked = QualityScorer.rank([dict(r) for r in results], intent=intent)
        urls = []
        for result in ranked[:6]:
            if result.get("published_date"):
                continue
            if result.get("quality_breakdown", {}).get("effective_published_date"):
                continue
            if not (
                QualityScorer._is_update_like_result(result)
                or QualityScorer._is_official_update_path(result)
            ):
                continue
            urls.append(result["url"])
            if len(urls) >= 3:
                break
        return urls

    async def _enrich_with_jina(self, results: List[Dict], intent: str = "general") -> List[Dict]:
        """
        使用 Jina Reader 深度提取所有结果
        """
        print("   📖 使用 Jina Reader 深度提取内容...")

        extraction_limit = get_jina_extraction_limit(intent, self.config.mode, len(results))
        urls = [r["url"] for r in results[:extraction_limit]]

        if not urls:
            for result in results:
                result["content"] = result.get("text", "")
                result["content_source"] = "original"
            return results

        async with JinaClient(self.config.jina_api_key) as jina:
            contents = await jina.extract_multiple(
                urls,
                max_concurrent=3,
                cache_ttl=get_jina_cache_ttl(intent)
            )

        for result in results:
            url = result["url"]
            if url in contents and contents[url]:
                result["content"] = contents[url]["markdown"]
                result["content_source"] = "jina"
            else:
                result["content"] = result.get("text", "")
                result["content_source"] = "original"

        return results

    async def _conditional_enrich(self, results: List[Dict], intent: str = "general") -> List[Dict]:
        """
        根据质量条件决定是否使用 Jina Reader
        """
        async with JinaClient(self.config.jina_api_key) as jina:
            urls_to_extract = []
            extraction_limit = get_jina_extraction_limit(intent, self.config.mode, len(results))

            for result in results:
                should_extract, reason = jina.should_extract(result)
                if should_extract:
                    urls_to_extract.append((result["url"], reason))

            if urls_to_extract:
                urls_to_extract = urls_to_extract[:extraction_limit]
                print(f"   📖 {len(urls_to_extract)} 条结果需要深度提取...")

                urls = [u for u, _ in urls_to_extract]
                contents = await jina.extract_multiple(
                    urls,
                    max_concurrent=3,
                    cache_ttl=get_jina_cache_ttl(intent)
                )

                for result in results:
                    url = result["url"]
                    if url in contents and contents[url]:
                        result["content"] = contents[url]["markdown"]
                        result["content_source"] = "jina"
                    else:
                        result["content"] = result.get("text", "")
                        result["content_source"] = "original"
            else:
                for result in results:
                    result["content"] = result.get("text", "")
                    result["content_source"] = "original"

        return results


async def search(
    query: str,
    max_results: int = 10,
    mode: Literal["quick", "standard", "deep"] = "standard",
    expand: bool = True,
    use_cache: bool = True
) -> Dict:
    """
    便捷的搜索函数（支持智能缓存）

    从环境变量读取 API Keys:
    - EXA_API_KEY (可选)
    - BRAVE_API_KEY (可选)
    - TAVILY_API_KEY (可选)
    - JINA_API_KEY (可选)

    Args:
        query: 搜索查询
        max_results: 最大返回结果数
        mode: 搜索模式 (quick/standard/deep)
        expand: 是否扩展查询
        use_cache: 是否使用缓存

    Returns:
        结构化搜索结果
    """
    # quick 模式强制不扩展查询，保证单次请求速度
    if mode == "quick":
        expand = False

    cache_scope = f"strategy={STRATEGY_VERSION}|mode={mode}|expand={int(expand)}|max_results={max_results}"

    # 读取配置
    config = get_config()
    exa_key = config.get('exa_api_key')
    brave_key = config.get('brave_api_key')
    tavily_key = config.get('tavily_api_key')
    jina_key = config.get('jina_api_key')

    if not exa_key and not brave_key and not tavily_key:
        print("⚠️  警告: 未设置任何搜索 API Key")
        print("   推荐至少设置 TAVILY_API_KEY；也支持 BRAVE_API_KEY 或 EXA_API_KEY")
        print("   - 环境变量: TAVILY_API_KEY、BRAVE_API_KEY 或 EXA_API_KEY")
        print("   - 或在 .env 文件中配置")
        print()

    # 初始化智能缓存
    cache = get_smart_cache()

    # 检查缓存
    if use_cache:
        cache_result = cache.get(query, scope=cache_scope)
        if cache_result['hit']:
            match_type = cache_result['match_type']

            if match_type == 'exact':
                print(f"  💾 精确缓存命中")
            elif match_type == 'similar':
                original = cache_result.get('original_query', 'N/A')
                similarity = cache_result.get('similarity', 0)
                level = cache_result.get('similarity_level', 'unknown')
                breakdown = cache_result.get('similarity_breakdown', {})
                print(f"  💡 相似缓存命中")
                print(f"     相似度: {similarity:.1%} ({level})")
                print(f"     原查询: {original}")
                if breakdown:
                    print(f"     字符级: {breakdown.get('char_level', 0):.1%} | "
                          f"词汇级: {breakdown.get('word_level', 0):.1%} | "
                          f"语义级: {breakdown.get('semantic', 0):.1%}")
            elif match_type == 'vector':
                original = cache_result.get('original_query', 'N/A')
                similarity = cache_result.get('similarity', 0)
                level = cache_result.get('similarity_level', 'unknown')
                breakdown = cache_result.get('similarity_breakdown', {})
                print(f"  🧠 向量语义缓存命中")
                print(f"     向量相似度: {similarity:.1%} ({level})")
                print(f"     原查询: {original}")
                if breakdown:
                    print(f"     方法: {breakdown.get('method', 'vector_search')} | "
                          f"向量相似度: {breakdown.get('vector_similarity', 0):.1%}")

            cached_data = copy.deepcopy(cache_result['data'])
            if isinstance(cached_data, dict):
                cached_data['query'] = query
                if match_type != 'exact':
                    cached_data['cache_origin_query'] = cache_result.get('original_query')
            return cached_data

    # 执行搜索
    search_config = SearchConfig(
        exa_api_key=exa_key,
        brave_api_key=brave_key,
        tavily_api_key=tavily_key,
        jina_api_key=jina_key,
        max_results=max_results,
        mode=mode
    )

    searcher = AgentSearch(search_config)
    result = await searcher.search(query, expand=expand)

    # 获取查询意图用于缓存 TTL 计算
    intent = detect_query_intent(query)

    # 保存到缓存（按意图决定基础 TTL，news 例外保持短周期）
    if use_cache and result:
        intent_ttl_map = {
            "news":            3600,    # 1 小时（时效性强）
            "general":         86400,   # 1 天
            "troubleshooting": 259200,  # 3 天（解决方案稳定）
            "comparison":      259200,  # 3 天（框架对比稳定）
            "release":         21600,   # 6 小时（官方更新类）
            "status":          21600,   # 6 小时（近况类）
        }
        ttl = intent_ttl_map.get(intent, 86400)
        # deep 模式内容最全，不缩短；quick 模式适当缩短（快速确认事实，不需要长期缓存）
        if mode == "quick":
            ttl = min(ttl, 43200)  # quick 最多缓存 12 小时
        cache_id = cache.set(query, result, ttl=ttl, scope=cache_scope)
        _start_cache_warmup(cache, cache_id, query)

    return result


# 兼容旧版调用
__all__ = ["search", "AgentSearch", "SearchConfig"]
