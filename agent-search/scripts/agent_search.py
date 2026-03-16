"""
Agent Search - 智能 Agent 搜索工具

为 AI Agent 提供深度、结构化的搜索能力。
支持 Claude Code、OpenCode、Gemini CLI、Codex CLI 等。
"""
import asyncio
import copy
import contextlib
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Dict, Optional, Literal
from dataclasses import dataclass

STRATEGY_VERSION = "v24"

try:
    from .ddgs_client import DdgsClient
    from .content_safety import apply_content_safety
    from .fresh_update_strategy import (
        build_status_summary,
        build_status_discovery_queries,
        build_status_site_queries,
        discover_official_domains,
        expand_query,
        get_max_queries_for_intent,
        get_query_source_plan,
        get_tavily_options,
        has_stale_status_results,
        is_fresh_update_intent,
        score_official_domain_candidate,
        should_early_stop,
        should_use_exa_fallback,
    )
    from .result_processor import ResultMerger, QualityScorer
    from .query_intent import (
        contains_chinese,
        detect_query_intent,
        get_status_query_subject,
        is_comparison_query,
        is_freshness_sensitive_query,
        is_news_query,
        is_release_query,
        is_troubleshooting_query,
    )
    from .site_role import (
        classify_site_role,
        domain_matches_subject as match_site_domain_subject,
        normalize_domain,
    )
    from .config import get_api_key, get_config
    from .smart_cache import get_smart_cache
except ImportError:
    from ddgs_client import DdgsClient
    from content_safety import apply_content_safety
    from fresh_update_strategy import (
        build_status_summary,
        build_status_discovery_queries,
        build_status_site_queries,
        discover_official_domains,
        expand_query,
        get_max_queries_for_intent,
        get_query_source_plan,
        get_tavily_options,
        has_stale_status_results,
        is_fresh_update_intent,
        score_official_domain_candidate,
        should_early_stop,
        should_use_exa_fallback,
    )
    from result_processor import ResultMerger, QualityScorer
    from query_intent import (
        contains_chinese,
        detect_query_intent,
        get_status_query_subject,
        is_comparison_query,
        is_freshness_sensitive_query,
        is_news_query,
        is_release_query,
        is_troubleshooting_query,
    )
    from site_role import (
        classify_site_role,
        domain_matches_subject as match_site_domain_subject,
        normalize_domain,
    )
    from config import get_api_key, get_config
    from smart_cache import get_smart_cache

if TYPE_CHECKING:
    try:
        from .exa_client import ExaClient
        from .brave_client import BraveClient
        from .tavily_client import TavilyClient
    except ImportError:
        from exa_client import ExaClient
        from brave_client import BraveClient
        from tavily_client import TavilyClient


@dataclass
class SearchConfig:
    """搜索配置"""
    exa_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    max_results: int = 10
    brave_max_results: int = 8
    tavily_max_results: int = 8
    mode: Literal["quick", "standard", "deep"] = "standard"
    enable_brave: bool = True  # 默认仅在部分意图下作为补充
    enable_tavily: bool = True  # 默认启用 Tavily 作为主搜索引擎
    source: Literal["auto", "ddgs"] = "auto"  # auto: 多源搜索 + DDGS fallback; ddgs: 仅用 DDGS

    def __post_init__(self):
        """验证配置值"""
        if self.mode not in ("quick", "standard", "deep"):
            raise ValueError(f"mode must be 'quick', 'standard' or 'deep', got {self.mode!r}")
        if self.max_results < 1 or self.max_results > 50:
            raise ValueError(f"max_results must be between 1 and 50, got {self.max_results}")
        if self.brave_max_results < 1 or self.brave_max_results > 20:
            raise ValueError(f"brave_max_results must be between 1 and 20, got {self.brave_max_results}")
        if self.tavily_max_results < 1 or self.tavily_max_results > 20:
            raise ValueError(f"tavily_max_results must be between 1 and 20, got {self.tavily_max_results}")
        if self.source not in ("auto", "ddgs"):
            raise ValueError(f"source must be 'auto' or 'ddgs', got {self.source!r}")


def domain_matches_subject(domain: str, subject: str) -> bool:
    return match_site_domain_subject(domain, (subject or "").strip().lower())


def _start_cache_warmup(cache, cache_id: Optional[int], query: str) -> None:
    """在后台预热向量缓存，不阻塞搜索返回"""
    if not cache_id or not getattr(cache, "vector_search_available", False):
        return

    task = asyncio.create_task(cache.warm_vector(cache_id, query))

    def _consume_error(done_task: asyncio.Task) -> None:
        with contextlib.suppress(asyncio.CancelledError, Exception):
            done_task.result()

    task.add_done_callback(_consume_error)


def _get_exa_client_cls():
    try:
        from .exa_client import ExaClient
    except ImportError:
        from exa_client import ExaClient
    return ExaClient


def _get_brave_client_cls():
    try:
        from .brave_client import BraveClient
    except ImportError:
        from brave_client import BraveClient
    return BraveClient


def _get_tavily_client_cls():
    try:
        from .tavily_client import TavilyClient
    except ImportError:
        from tavily_client import TavilyClient
    return TavilyClient


class AgentSearch:
    """Agent Search 主类"""

    def __init__(self, config: SearchConfig):
        self.config = config

    async def search_single(
        self,
        query: str,
        exa: Optional[Any] = None,
        brave: Optional[Any] = None,
        tavily: Optional[Any] = None,
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
            print(f"   ⚠️ No available search sources")
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

    async def _search_ddgs_only(self, query: str, expand: bool = True) -> Dict:
        """仅使用 DDGS 搜索（用户显式指定或无 API Key fallback）"""
        print(f"🔍 Searching: {query}")
        print("   🦆 Using DDGS (DuckDuckGo)")

        queries = expand_query(query) if expand else [query]
        intent = detect_query_intent(query)
        print(f"   Expanded to {len(queries)} queries")
        print(f"   Intent: {intent}")

        ddgs = DdgsClient()
        async with ddgs:
            all_results = []
            for q in queries:
                results = await ddgs.search_with_timeout(q, self.config.max_results)
                print(f"   ✓ '{q}' returned {len(results)} results")
                all_results.extend(results)

        unique_results = ResultMerger.deduplicate(all_results)
        print(f"   Deduplicated: {len(unique_results)} results")

        unique_results = [apply_content_safety(dict(r)) for r in unique_results]
        ranked_results = QualityScorer.rank(unique_results, intent=intent, query=query)
        final_results = ranked_results[:self.config.max_results]
        final_results = self._attach_safe_content(final_results)

        response = {
            "query": query,
            "search_queries": list(queries),
            "sources_used": ["ddgs"],
            "total_found": len(all_results),
            "unique_count": len(unique_results),
            "results_returned": len(final_results),
            "results": final_results,
        }
        if intent == "status":
            response["status_summary"] = build_status_summary(final_results, query=query)
        return response

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
        # 用户显式指定 DDGS
        if self.config.source == "ddgs":
            return await self._search_ddgs_only(query, expand)

        print(f"🔍 Searching: {query}")

        # 1. 确定是否使用 Tavily 和 Brave
        use_brave = self.config.enable_brave and self.config.brave_api_key is not None
        use_tavily = self.config.enable_tavily and self.config.tavily_api_key is not None
        if use_tavily:
            print("   Tavily (AI search) enabled")
        if use_brave:
            print("   Brave Search enabled")

        # 2. 扩展查询
        queries = expand_query(query) if expand else [query]
        executed_queries = list(queries)
        intent = detect_query_intent(query)
        print(f"   Expanded to {len(queries)} queries")
        print(f"   Intent: {intent}")

        # 3. 创建复用的客户端实例
        has_exa = self.config.exa_api_key is not None
        exa = _get_exa_client_cls()(self.config.exa_api_key) if has_exa else None
        brave = _get_brave_client_cls()(self.config.brave_api_key) if use_brave else None
        tavily = _get_tavily_client_cls()(self.config.tavily_api_key) if use_tavily else None

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
            print(f"   ✓ '{queries[0]}' returned {len(first_results)} results")
            all_results.extend(first_results)

            extra_status_queries: List[str] = []
            if intent == "status" and has_stale_status_results(ResultMerger.deduplicate(all_results)):
                print("   🕒 First-round results are stale, fetching fresher updates")
                extra_status_queries = build_status_discovery_queries(query)
                extra_status_queries.extend(build_status_site_queries(query, ResultMerger.deduplicate(all_results)))
                extra_status_queries = list(dict.fromkeys(extra_status_queries))
                if extra_status_queries:
                    print(f"   🎯 Adding {len(extra_status_queries)} site-targeted queries")
                    executed_queries.extend([q for q in extra_status_queries if q not in executed_queries])

            exa_fallback_used = should_use_exa_fallback(
                ResultMerger.deduplicate(all_results),
                self.config.max_results,
                intent,
                self.config.mode,
                has_exa
            )
            if exa_fallback_used:
                print("   ➕ First-round results insufficient, adding Exa semantic search")
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
                        print(f"   ✓ Exa supplement '{q}' returned {len(results)} results")
                        all_results.extend(results)
            if intent != "status" and len(queries) > 1 and should_early_stop(
                ResultMerger.deduplicate(all_results),
                self.config.max_results,
                intent,
                query=query,
            ):
                print("   ⏹️ First-round quality sufficient, skipping expansion")
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
                        print(f"   ✓ '{q}' returned {len(results)} results")
                        all_results.extend(results)

                if intent == "status" and has_stale_status_results(ResultMerger.deduplicate(all_results)):
                    late_status_queries = [
                        q for q in build_status_site_queries(query, ResultMerger.deduplicate(all_results))
                        if q not in executed_queries
                    ]
                    if late_status_queries:
                        print(f"   🎯 Adding {len(late_status_queries)} site-targeted queries based on discovered domains")
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
                            print(f"   ✓ '{q}' returned {len(results)} results")
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
        print(f"   Deduplicated: {len(unique_results)} results")

        # 5.1 DDGS fallback: 所有 API 引擎均无结果时兜底
        ddgs_used = False
        if len(unique_results) == 0:
            print("   🦆 All sources returned no results, falling back to DDGS")
            ddgs = DdgsClient()
            async with ddgs:
                ddgs_results = await ddgs.search_with_timeout(query, self.config.max_results)
            unique_results = ddgs_results
            ddgs_used = True

        unique_results = [apply_content_safety(dict(result)) for result in unique_results]

        # 6. 质量评分和排序
        ranked_results = QualityScorer.rank(unique_results, intent=intent, query=query)

        # 7. 限制返回数量
        final_results = ranked_results[:self.config.max_results]

        # 8. 所有模式都只返回搜索摘要的安全摘录，不加载整页正文
        final_results = self._attach_safe_content(final_results)

        # 9. 构建返回结构
        sources = (["exa"] if has_exa else []) + (["brave"] if use_brave else []) + (["tavily"] if use_tavily else [])
        if ddgs_used:
            sources.append("ddgs")
        response = {
            "query": query,
            "search_queries": executed_queries,
            "sources_used": sources,
            "total_found": len(all_results),
            "unique_count": len(unique_results),
            "results_returned": len(final_results),
            "results": final_results
        }
        if intent == "status":
            response["status_summary"] = build_status_summary(final_results, query=query)
        return response

    async def _refresh_fresh_update_candidates(self, results: List[Dict], intent: str) -> List[Dict]:
        """兼容旧调用；不再抓取第三方正文。"""
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

    def _attach_safe_content(self, results: List[Dict]) -> List[Dict]:
        for result in results:
            apply_content_safety(result)
        return results

    async def _conditional_enrich(self, results: List[Dict], intent: str = "general") -> List[Dict]:
        """兼容旧调用；统一返回安全摘录。"""
        return self._attach_safe_content(results)


async def search(
    query: str,
    max_results: int = 10,
    mode: Literal["quick", "standard", "deep"] = "standard",
    expand: bool = True,
    use_cache: bool = True,
    source: Literal["auto", "ddgs"] = "auto",
) -> Dict:
    """
    便捷的搜索函数（支持智能缓存）

    从环境变量读取 API Keys:
    - EXA_API_KEY (可选)
    - BRAVE_API_KEY (可选)
    - TAVILY_API_KEY (可选)
    Args:
        query: 搜索查询
        max_results: 最大返回结果数
        mode: 搜索模式 (quick/standard/deep)
        expand: 是否扩展查询
        use_cache: 是否使用缓存
        source: 搜索源 (auto: 多源搜索 + DDGS fallback; ddgs: 仅用 DDGS)

    Returns:
        结构化搜索结果
    """
    # quick 模式强制不扩展查询，保证单次请求速度
    if mode == "quick":
        expand = False

    cache_scope = f"strategy={STRATEGY_VERSION}|mode={mode}|expand={int(expand)}|max_results={max_results}|source={source}"

    # 读取配置
    config = get_config()
    exa_key = config.get('exa_api_key')
    brave_key = config.get('brave_api_key')
    tavily_key = config.get('tavily_api_key')
    if source == "auto" and not exa_key and not brave_key and not tavily_key:
        print("ℹ️  No API keys configured, using DDGS (DuckDuckGo)")
        print("   Set TAVILY_API_KEY etc. for better multi-source results")

    # 初始化智能缓存
    cache = get_smart_cache()

    # 检查缓存
    if use_cache:
        cache_result = cache.get(query, scope=cache_scope)
        if cache_result['hit']:
            match_type = cache_result['match_type']

            if match_type == 'exact':
                print(f"  💾 Exact cache hit")
            elif match_type == 'similar':
                original = cache_result.get('original_query', 'N/A')
                similarity = cache_result.get('similarity', 0)
                level = cache_result.get('similarity_level', 'unknown')
                breakdown = cache_result.get('similarity_breakdown', {})
                print(f"  💡 Similar cache hit")
                print(f"     Similarity: {similarity:.1%} ({level})")
                print(f"     Original: {original}")
                if breakdown:
                    print(f"     Char: {breakdown.get('char_level', 0):.1%} | Word: {breakdown.get('word_level', 0):.1%} | Semantic: {breakdown.get('semantic', 0):.1%}")
            elif match_type == 'vector':
                original = cache_result.get('original_query', 'N/A')
                similarity = cache_result.get('similarity', 0)
                level = cache_result.get('similarity_level', 'unknown')
                breakdown = cache_result.get('similarity_breakdown', {})
                print(f"  🧠 Vector cache hit")
                print(f"     Vector similarity: {similarity:.1%} ({level})")
                print(f"     Original: {original}")
                if breakdown:
                    print(f"     Method: {breakdown.get('method', 'vector_search')} | Vector similarity: {breakdown.get('vector_similarity', 0):.1%}")

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
        max_results=max_results,
        mode=mode,
        source=source,
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
