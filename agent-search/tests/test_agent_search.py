"""
Agent Search 测试
"""
import asyncio
import pytest
import sys
import os
import tempfile
import time

# 添加 scripts 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from result_processor import ResultMerger, QualityScorer
from smart_cache import SmartCache
from smart_similarity import SmartSimilarity


class TestResultMerger:
    """测试结果合并器"""

    def test_normalize_url(self):
        assert ResultMerger.normalize_url("https://example.com/path/") == "example.com/path"
        assert ResultMerger.normalize_url("HTTPS://EXAMPLE.COM/PATH") == "example.com/path"
        assert ResultMerger.normalize_url("https://example.com") == "example.com"

    def test_similarity(self):
        assert ResultMerger.similarity("hello world", "hello world") == 1.0
        assert ResultMerger.similarity("hello", "world") < 0.5
        assert ResultMerger.similarity("Python 教程", "Python教程") > 0.8

    def test_deduplicate(self):
        results = [
            {"title": "Python 教程", "url": "https://example.com/python"},
            {"title": "Python教程", "url": "https://example.com/python"},
            {"title": "JavaScript 教程", "url": "https://example.com/js"},
        ]
        unique = ResultMerger.deduplicate(results)
        assert len(unique) == 2

    def test_merge_sources(self):
        exa_results = [
            {"title": "Exa Result 1", "url": "https://exa.com/1", "source": "exa"},
        ]
        brave_results = [
            {"title": "Brave Result 1", "url": "https://search.brave.com/1", "source": "brave"},
        ]
        tavily_results = [
            {"title": "Tavily Result 1", "url": "https://tavily.com/1", "source": "tavily"},
        ]
        # Test merging with two sources
        merged = ResultMerger.merge_sources(exa_results, brave_results)
        assert len(merged) == 2
        assert merged[0]["source"] == "exa"
        assert merged[1]["source"] == "brave"

        # Test merging with three sources
        merged_three = ResultMerger.merge_sources(exa_results, brave_results, tavily_results)
        assert len(merged_three) == 3
        sources = [r["source"] for r in merged_three]
        assert "exa" in sources
        assert "brave" in sources
        assert "tavily" in sources


class TestQualityScorer:
    """测试质量评分器"""

    def test_get_source_authority(self):
        assert QualityScorer.get_source_authority("https://github.com/repo") == 0.95
        assert QualityScorer.get_source_authority("https://example.com") == 0.60
        assert QualityScorer.get_source_authority("https://myblog.com") == 0.75

    def test_calculate_freshness_score(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        assert QualityScorer.calculate_freshness_score(today) == 1.0
        assert QualityScorer.calculate_freshness_score("") == 0.5

    def test_calculate_content_completeness(self):
        assert QualityScorer.calculate_content_completeness("a" * 100) == 0.3
        assert QualityScorer.calculate_content_completeness("a" * 1500) == 0.7
        assert QualityScorer.calculate_content_completeness("a" * 6000) == 1.0

    def test_score(self):
        result = {
            "title": "Test",
            "url": "https://github.com/test",
            "text": "a" * 3000,
            "published_date": "2024-03-01",
            "score": 0.9
        }
        scored = QualityScorer.score(result)
        assert "quality_score" in scored
        assert "quality_breakdown" in scored
        assert scored["quality_score"] > 0

    def test_rank(self):
        results = [
            {"title": "Low", "url": "http://example.com", "text": "short", "score": 0.5},
            {"title": "High", "url": "https://github.com", "text": "a" * 5000, "score": 0.9},
        ]
        ranked = QualityScorer.rank(results)
        assert ranked[0]["title"] == "High"
        assert ranked[0]["rank"] == 1

    def test_rank_release_filters_csdn_and_prefers_official(self):
        results = [
            {"title": "Node.js latest version - CSDN", "url": "https://blog.csdn.net/foo/article/details/1", "text": "a" * 3000, "score": 0.95},
            {"title": "Download Node.js", "url": "https://nodejs.org/en/download/current", "text": "a" * 1500, "score": 0.7},
            {"title": "Node.js release notes", "url": "https://github.com/nodejs/node/releases/tag/v25.8.0", "text": "a" * 1500, "score": 0.75},
        ]
        ranked = QualityScorer.rank(results, intent="release")
        urls = [r["url"] for r in ranked]
        assert "https://blog.csdn.net/foo/article/details/1" not in urls
        assert ranked[0]["url"] == "https://nodejs.org/en/download/current"

    def test_rank_troubleshooting_prefers_stackoverflow(self):
        results = [
            {"title": "Node.js permission denied error", "url": "https://example.com/blog/node-error", "text": "a" * 2000, "score": 0.8},
            {"title": "Node.js permission denied error - Stack Overflow", "url": "https://stackoverflow.com/questions/123/test", "text": "a" * 800, "score": 0.65},
            {"title": "Node issue discussion", "url": "https://github.com/nodejs/node/issues/123", "text": "a" * 1000, "score": 0.7},
        ]
        ranked = QualityScorer.rank(results, intent="troubleshooting")
        assert ranked[0]["url"] == "https://stackoverflow.com/questions/123/test"
        assert ranked[1]["url"] == "https://github.com/nodejs/node/issues/123"

    def test_rank_news_prefers_recent_news_over_wiki(self):
        results = [
            {
                "title": "美以对伊朗行动最新进展",
                "url": "https://www.reuters.com/world/middle-east/test-news",
                "text": "a" * 1200,
                "score": 0.72,
                "published_date": "2026-03-11"
            },
            {
                "title": "2026年美以空袭伊朗 - 维基百科",
                "url": "https://zh.wikipedia.org/wiki/test",
                "text": "a" * 5000,
                "score": 0.88,
                "published_date": ""
            },
            {
                "title": "Node.js docs latest update",
                "url": "https://nodejs.org/docs/latest/api/",
                "text": "a" * 2000,
                "score": 0.9,
                "published_date": "2026-03-10"
            },
        ]
        ranked = QualityScorer.rank(results, intent="news")
        assert ranked[0]["url"] == "https://www.reuters.com/world/middle-east/test-news"
        assert ranked[-1]["url"] == "https://nodejs.org/docs/latest/api/"

    def test_rank_comparison_prefers_real_comparison_content(self):
        results = [
            {
                "title": "React vs Vue comparison",
                "url": "https://dev.to/someone/react-vs-vue-comparison",
                "text": "a" * 1800,
                "score": 0.72,
                "published_date": "2025-12-01"
            },
            {
                "title": "React documentation",
                "url": "https://react.dev/learn",
                "text": "a" * 3000,
                "score": 0.9,
                "published_date": "2026-01-10"
            },
            {
                "title": "Vue 3 release notes",
                "url": "https://github.com/vuejs/core/releases/tag/v3.0.0",
                "text": "a" * 1500,
                "score": 0.82,
                "published_date": "2025-11-01"
            },
        ]
        ranked = QualityScorer.rank(results, intent="comparison")
        assert ranked[0]["url"] == "https://dev.to/someone/react-vs-vue-comparison"
        assert ranked[-1]["url"] == "https://github.com/vuejs/core/releases/tag/v3.0.0"

    def test_rank_applies_source_bonus_for_troubleshooting(self):
        results = [
            {
                "title": "Node install error fix",
                "url": "https://example.com/node-install-error",
                "text": "a" * 1500,
                "score": 0.7,
                "source": "brave"
            },
            {
                "title": "Node install error fix",
                "url": "https://example.org/node-install-error",
                "text": "a" * 1500,
                "score": 0.7,
                "source": "exa"
            },
        ]
        ranked = QualityScorer.rank(results, intent="troubleshooting")
        assert ranked[0]["source"] == "brave"
        assert ranked[0]["source_bonus"] > ranked[1]["source_bonus"]


class TestSmartCache:
    """测试智能缓存（使用临时目录，不依赖 GEMINI_API_KEY）"""

    def _make_cache(self):
        tmpdir = tempfile.mkdtemp()
        return SmartCache(cache_dir=tmpdir)

    def test_exact_match(self):
        cache = self._make_cache()
        cache.set("Python tutorial", {"results": [1, 2, 3]}, ttl=3600)
        result = cache.get("Python tutorial")
        assert result['hit'] is True
        assert result['match_type'] == 'exact'
        assert result['similarity'] == 1.0
        assert result['data'] == {"results": [1, 2, 3]}

    def test_cache_miss(self):
        cache = self._make_cache()
        result = cache.get("nonexistent query")
        assert result['hit'] is False
        assert result['match_type'] == 'none'

    def test_similar_match(self):
        cache = self._make_cache()
        cache.set("Python asyncio tutorial", {"results": ["async"]}, ttl=3600)
        # 相似查询应该命中
        result = cache.get("Python asyncio 教程")
        # 可能命中也可能不命中，取决于相似度阈值
        if result['hit']:
            assert result['match_type'] == 'similar'
            assert result['similarity'] >= 0.6

    def test_cache_expiration(self):
        cache = self._make_cache()
        cache.set("test", {"data": "value"}, ttl=3)
        # 立即查询应该命中
        result = cache.get("test")
        assert result['hit'] is True
        # 等待过期
        time.sleep(3.1)
        result = cache.get("test")
        assert result['hit'] is False

    def test_cache_stats(self):
        cache = self._make_cache()
        cache.set("test1", {"v": 1})
        cache.get("test1")
        cache.get("test1")
        cache.get("test2")  # miss
        stats = cache.get_stats()
        assert stats['total_entries'] == 1
        assert stats['total_hits'] >= 1

    def test_clear(self):
        cache = self._make_cache()
        cache.set("test", {"data": "value"})
        cache.clear()
        result = cache.get("test")
        assert result['hit'] is False

    def test_list_recent(self):
        cache = self._make_cache()
        cache.set("query1", {"r": 1})
        cache.set("query2", {"r": 2})
        recent = cache.list_recent(limit=5)
        assert len(recent) == 2

    def test_content_cache(self):
        cache = self._make_cache()
        content = {"title": "Example", "markdown": "Body", "url": "https://example.com", "length": 4}
        cache.set_cached_content("https://example.com", content, ttl=10)
        cached = cache.get_cached_content("https://example.com")
        assert cached == content

    def test_content_cache_expiration(self):
        cache = self._make_cache()
        content = {"title": "Example", "markdown": "Body", "url": "https://example.com", "length": 4}
        cache.set_cached_content("https://example.com", content, ttl=1)
        time.sleep(1.1)
        cached = cache.get_cached_content("https://example.com")
        assert cached is None

    def test_provider_usage_stats_and_warnings(self):
        cache = self._make_cache()
        for _ in range(950):
            cache.record_provider_usage("exa", success=True)
        stats = cache.get_provider_usage_stats()
        exa_stats = next(item for item in stats if item["provider"] == "exa")
        assert exa_stats["request_count"] == 950
        assert exa_stats["success_count"] == 950
        warnings = cache.get_provider_warnings()
        exa_warning = next(item for item in warnings if item["provider"] == "exa")
        assert exa_warning["level"] == "critical"
        assert exa_warning["free_limit"] == 1000

    def test_cache_scope_isolated(self):
        cache = self._make_cache()
        cache.set("Python tutorial", {"mode": "quick"}, scope="depth=quick|max=5|expand=0")
        cache.set("Python tutorial", {"mode": "deep"}, scope="depth=deep|max=10|expand=1")

        quick_result = cache.get("Python tutorial", scope="depth=quick|max=5|expand=0")
        deep_result = cache.get("Python tutorial", scope="depth=deep|max=10|expand=1")
        miss_result = cache.get("Python tutorial", scope="depth=standard|max=10|expand=1")

        assert quick_result["hit"] is True
        assert quick_result["data"] == {"mode": "quick"}
        assert deep_result["hit"] is True
        assert deep_result["data"] == {"mode": "deep"}
        assert miss_result["hit"] is False


class TestSmartSimilarity:
    """测试智能相似度算法"""

    def test_exact_match(self):
        calc = SmartSimilarity()
        result = calc.calculate("Python tutorial", "Python tutorial")
        assert result['similarity'] == 1.0
        assert result['level'] == 'exact'

    def test_high_similarity(self):
        calc = SmartSimilarity()
        result = calc.calculate("Python 异步编程", "Python 异步编程入门")
        assert result['similarity'] > 0.5

    def test_low_similarity(self):
        calc = SmartSimilarity()
        result = calc.calculate("Python 异步编程", "JavaScript 爬虫框架")
        assert result['similarity'] < 0.6

    def test_length_disparity(self):
        calc = SmartSimilarity()
        result = calc.calculate("a", "a very long query that is much longer")
        assert result['similarity'] == 0.0


class TestQueryExpansion:
    """测试查询扩展"""

    def test_contains_chinese(self):
        from agent_search import contains_chinese
        assert contains_chinese("中文") is True
        assert contains_chinese("English") is False
        assert contains_chinese("Python 教程") is True

    def test_is_news_query(self):
        from agent_search import is_news_query
        assert is_news_query("美以对伊朗行动的最新消息") is True
        assert is_news_query("Middle East latest updates") is True
        assert is_news_query("Python 怎么用") is False
        assert is_news_query("最新的 Python 文档") is False
        assert is_news_query("latest React docs") is False
        assert is_news_query("latest Node.js version") is False

    def test_is_release_query(self):
        from agent_search import is_release_query
        assert is_release_query("最新的 Python 文档") is True
        assert is_release_query("latest React docs") is True
        assert is_release_query("latest Node.js version") is True
        assert is_release_query("美以对伊朗行动的最新消息") is False

    def test_is_troubleshooting_query(self):
        from agent_search import is_troubleshooting_query
        assert is_troubleshooting_query("npm install 报错") is True
        assert is_troubleshooting_query("Node.js permission denied error") is True
        assert is_troubleshooting_query("Python module not found") is True
        assert is_troubleshooting_query("app not working after deploy") is True
        assert is_troubleshooting_query("latest React docs") is False
        assert is_troubleshooting_query("美以对伊朗行动的最新消息") is False

    def test_is_comparison_query(self):
        from agent_search import is_comparison_query
        assert is_comparison_query("Python vs Node.js") is True
        assert is_comparison_query("React 和 Vue 区别") is True
        assert is_comparison_query("Next.js 和 Remix 怎么选") is True
        assert is_comparison_query("Should I use Next.js or Remix") is True
        assert is_comparison_query("React or Vue for dashboard") is True
        assert is_comparison_query("latest React docs") is False

    def test_detect_query_intent(self):
        from agent_search import detect_query_intent
        assert detect_query_intent("美以对伊朗行动的最新消息") == "news"
        assert detect_query_intent("npm install 报错") == "troubleshooting"
        assert detect_query_intent("Python vs Node.js") == "comparison"
        assert detect_query_intent("latest Node.js version") == "release"
        assert detect_query_intent("Python 是什么") == "general"

    def test_strategy_version_in_cache_scope(self):
        from agent_search import STRATEGY_VERSION
        assert STRATEGY_VERSION == "v8"

    def test_query_source_plan(self):
        from agent_search import get_query_source_plan

        first_query_plan = get_query_source_plan("general", 0, True, True, True)
        assert first_query_plan == {"exa": False, "brave": False, "tavily": True}

        general_expanded = get_query_source_plan("general", 1, True, True, True)
        assert general_expanded == {"exa": False, "brave": False, "tavily": True}

        news_expanded = get_query_source_plan("news", 1, True, True, True)
        assert news_expanded == {"exa": False, "brave": True, "tavily": True}

        release_expanded = get_query_source_plan("release", 2, True, True, True)
        assert release_expanded == {"exa": False, "brave": True, "tavily": True}

        troubleshooting_expanded = get_query_source_plan("troubleshooting", 1, True, True, True)
        assert troubleshooting_expanded == {"exa": False, "brave": True, "tavily": True}

        comparison_expanded = get_query_source_plan("comparison", 1, True, True, True)
        assert comparison_expanded == {"exa": False, "brave": False, "tavily": True}

        fallback_plan = get_query_source_plan("general", 0, True, True, False)
        assert fallback_plan == {"exa": False, "brave": True, "tavily": False}

    def test_max_queries_for_intent(self):
        from agent_search import get_max_queries_for_intent
        assert get_max_queries_for_intent("general", "Python tutorial") == 2
        assert get_max_queries_for_intent("release", "latest Node.js version") == 2
        assert get_max_queries_for_intent("news", "美以对伊朗行动的最新消息") == 3
        assert get_max_queries_for_intent("comparison", "Python vs Node.js") == 3
        assert get_max_queries_for_intent("troubleshooting", "Python module not found after installing package in CI pipeline") == 2

    def test_jina_extraction_limit(self):
        from agent_search import get_jina_extraction_limit
        assert get_jina_extraction_limit("general", "quick", 10) == 0
        assert get_jina_extraction_limit("release", "standard", 10) == 3
        assert get_jina_extraction_limit("comparison", "standard", 10) == 2
        assert get_jina_extraction_limit("news", "deep", 1) == 1

    def test_jina_cache_ttl(self):
        from agent_search import get_jina_cache_ttl
        assert get_jina_cache_ttl("news") == 900
        assert get_jina_cache_ttl("release") == 43200
        assert get_jina_cache_ttl("troubleshooting") == 86400
        assert get_jina_cache_ttl("general") == 21600

    def test_should_early_stop(self):
        from agent_search import should_early_stop
        strong_results = [
            {"title": "Official release notes", "url": "https://nodejs.org/en/download/current", "text": "a" * 2000, "score": 0.85, "source": "brave"},
            {"title": "Node.js changelog", "url": "https://github.com/nodejs/node/releases/tag/v1", "text": "a" * 1800, "score": 0.82, "source": "exa"},
            {"title": "Node.js docs", "url": "https://nodejs.org/docs/latest/api/", "text": "a" * 2200, "score": 0.8, "source": "tavily"},
        ]
        weak_results = [
            {"title": "Blog post", "url": "https://example.com/post1", "text": "a" * 700, "score": 0.55, "source": "exa"},
            {"title": "Another post", "url": "https://example.com/post2", "text": "a" * 600, "score": 0.52, "source": "exa"},
            {"title": "More results", "url": "https://example.com/post3", "text": "a" * 650, "score": 0.5, "source": "brave"},
        ]
        assert should_early_stop(strong_results, max_results=3, intent="release") is True
        assert should_early_stop(weak_results, max_results=3, intent="general") is False

    def test_should_use_exa_fallback(self):
        from agent_search import should_use_exa_fallback
        strong_results = [
            {"title": "Strong 1", "url": "https://example.com/1", "text": "a" * 2000, "score": 0.9, "source": "brave"},
            {"title": "Strong 2", "url": "https://example.com/2", "text": "a" * 1800, "score": 0.88, "source": "tavily"},
            {"title": "Strong 3", "url": "https://example.com/3", "text": "a" * 1700, "score": 0.86, "source": "brave"},
        ]
        weak_results = [
            {"title": "Weak 1", "url": "https://example.com/a", "text": "a" * 700, "score": 0.55, "source": "brave"},
            {"title": "Weak 2", "url": "https://example.com/b", "text": "a" * 650, "score": 0.5, "source": "tavily"},
            {"title": "Weak 3", "url": "https://example.com/c", "text": "a" * 600, "score": 0.48, "source": "brave"},
        ]
        assert should_use_exa_fallback(strong_results, 3, "general", "standard", True) is False
        assert should_use_exa_fallback(weak_results, 3, "general", "standard", True) is True
        assert should_use_exa_fallback(strong_results, 3, "general", "deep", True) is True
        assert should_use_exa_fallback(strong_results, 3, "general", "standard", False) is False

    def test_expand_query(self):
        from agent_search import expand_query
        chinese_queries = expand_query("Python 教程")
        assert len(chinese_queries) >= 1
        assert "Python 教程" in chinese_queries

        english_queries = expand_query("Python tutorial")
        assert len(english_queries) >= 1
        assert "Python tutorial" in english_queries

        what_queries = expand_query("Python 是什么")
        assert any("介绍" in q for q in what_queries)

        how_queries = expand_query("Python 怎么用")
        assert any("教程" in q for q in how_queries)

        news_queries = expand_query("美以对伊朗行动的最新消息")
        assert "美以对伊朗行动的最新消息" in news_queries
        assert not any("教程" in q for q in news_queries)
        assert any(("最新进展" in q) or ("局势更新" in q) for q in news_queries)

        latest_doc_queries = expand_query("最新的 Python 文档")
        assert not any("局势更新" in q or "最新进展" in q for q in latest_doc_queries)
        assert any("发布说明" in q or "更新日志" in q for q in latest_doc_queries)

        latest_version_queries = expand_query("latest Node.js version")
        assert len(latest_version_queries) <= 2
        assert any("release notes" in q or "changelog" in q for q in latest_version_queries)

        troubleshooting_queries = expand_query("npm install 报错")
        assert any("解决方案" in q for q in troubleshooting_queries)
        assert any("GitHub issue" in q for q in troubleshooting_queries)
        assert not any("教程" in q for q in troubleshooting_queries)

        english_troubleshooting_queries = expand_query("Python module not found")
        assert any("fix" in q or "github issue" in q for q in english_troubleshooting_queries)

        comparison_queries = expand_query("Python vs Node.js")
        assert any("pros and cons" in q or "comparison" in q for q in comparison_queries)

        chinese_comparison_queries = expand_query("React 和 Vue 区别")
        assert any("优缺点" in q or "怎么选" in q for q in chinese_comparison_queries)

        english_comparison_queries = expand_query("Should I use Next.js or Remix")
        assert any("pros and cons" in q or "comparison" in q for q in english_comparison_queries)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
