"""
Agent Search - 智能 Agent 搜索工具

为 AI Agent 提供深度、结构化的搜索能力。
支持 Claude Code、OpenCode、Gemini CLI、Codex CLI 等。
"""
import asyncio
import copy
import contextlib
from datetime import datetime
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass

STRATEGY_VERSION = "v24"

try:
    from .exa_client import ExaClient
    from .brave_client import BraveClient
    from .tavily_client import TavilyClient
    from .jina_client import JinaClient
    from .fresh_update_strategy import (
        build_status_summary,
        build_status_discovery_queries,
        build_status_site_queries,
        discover_official_domains,
        expand_query,
        get_jina_cache_ttl,
        get_jina_extraction_limit,
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
    from exa_client import ExaClient
    from brave_client import BraveClient
    from tavily_client import TavilyClient
    from jina_client import JinaClient
    from fresh_update_strategy import (
        build_status_summary,
        build_status_discovery_queries,
        build_status_site_queries,
        discover_official_domains,
        expand_query,
        get_jina_cache_ttl,
        get_jina_extraction_limit,
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
        response = {
            "query": query,
            "search_queries": executed_queries,
            "sources_used": (["exa"] if has_exa else []) + (["brave"] if use_brave else []) + (["tavily"] if use_tavily else []),
            "total_found": len(all_results),
            "unique_count": len(unique_results),
            "results_returned": len(final_results),
            "results": final_results
        }
        if intent == "status":
            response["status_summary"] = build_status_summary(final_results, query=query)
        return response

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
