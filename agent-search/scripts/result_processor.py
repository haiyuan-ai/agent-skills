"""
搜索结果融合、去重和质量评分
"""
import re
from typing import List, Dict
from urllib.parse import urlparse
from difflib import SequenceMatcher


class ResultMerger:
    """搜索结果融合器"""

    @staticmethod
    def normalize_url(url: str) -> str:
        """标准化 URL 用于去重"""
        parsed = urlparse(url.lower().strip())
        # 移除末尾的斜杠，忽略查询参数和锚点
        path = parsed.path.rstrip('/')
        return f"{parsed.netloc}{path}"

    @staticmethod
    def similarity(a: str, b: str) -> float:
        """计算两个字符串的相似度"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    @classmethod
    def deduplicate(cls, results: List[Dict], threshold: float = 0.85) -> List[Dict]:
        """
        对搜索结果去重

        Args:
            results: 原始结果列表
            threshold: 标题相似度阈值，超过认为重复

        Returns:
            去重后的结果列表
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "")
            title = result.get("title", "")

            # 1. URL 去重
            normalized_url = cls.normalize_url(url)
            if normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)

            # 2. 标题相似度去重
            is_duplicate = False
            for existing in unique_results:
                if cls.similarity(title, existing.get("title", "")) > threshold:
                    # 保留质量更好的结果
                    if result.get("score", 0) > existing.get("score", 0):
                        unique_results.remove(existing)
                        break
                    else:
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_results.append(result)

        return unique_results

    @classmethod
    def merge_sources(cls, exa_results: List[Dict], brave_results: List[Dict], tavily_results: List[Dict] = None) -> List[Dict]:
        """
        合并 Exa、Brave 和 Tavily 的结果

        策略:
        1. Exa 结果排在前面 (语义搜索通常更准确)
        2. Brave 和 Tavily 结果作为补充
        3. 去重处理
        """
        # 合并并去重（各客户端已自行标记 source）
        combined = exa_results + brave_results
        if tavily_results:
            combined = combined + tavily_results
        return cls.deduplicate(combined)


class QualityScorer:
    """结果质量评分器"""

    # 来源权威性权重
    SOURCE_AUTHORITY = {
        "github.com": 0.95,
        "stackoverflow.com": 0.95,
        "medium.com": 0.80,
        "dev.to": 0.80,
        "wikipedia.org": 0.90,
        "arxiv.org": 0.95,
        "zhihu.com": 0.85,
        "juejin.cn": 0.80,
        "csdn.net": 0.70,
        "blog": 0.75,  # 域名包含 blog
        "default": 0.60
    }

    @staticmethod
    def _url_lower(result: Dict) -> str:
        return result.get("url", "").lower()

    @staticmethod
    def _title_lower(result: Dict) -> str:
        return result.get("title", "").lower()

    @staticmethod
    def _text_lower(result: Dict) -> str:
        return result.get("text", "").lower()

    @staticmethod
    def is_freshness_sensitive_query(query: str) -> bool:
        if not query:
            return False
        lowered = query.lower()
        chinese_terms = ["怎么样", "如何", "现状", "近况", "最近", "最新", "动态", "进展"]
        english_terms = ["how is", "what's new", "whats new", "current", "recent", "latest", "updates", "status", "now"]
        return any(term in query for term in chinese_terms) or any(term in lowered for term in english_terms)

    @classmethod
    def extract_embedded_date(cls, result: Dict) -> str:
        """从标题和正文中提取显式日期，作为 published_date 的兜底"""
        haystack = "\n".join([
            result.get("published_date", "") or "",
            result.get("title", "") or "",
            result.get("text", "") or "",
        ])

        patterns = [
            r"(20\d{2}-\d{2}-\d{2})",
            r"(20\d{2}/\d{2}/\d{2})",
            r"(20\d{2}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)",
            r"(20\d{2}年\d{1,2}月\d{1,2}日)",
            r"posted\s*@\s*(20\d{2}-\d{2}-\d{2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, haystack, re.IGNORECASE)
            if match:
                return (
                    match.group(1)
                    .replace("/", "-")
                    .replace(" ", "")
                    .replace("年", "-")
                    .replace("月", "-")
                    .replace("日", "")
                )

        title = result.get("title", "") or ""
        year_match = re.search(r"(20\d{2})", title)
        if year_match:
            return f"{year_match.group(1)}-01-01"
        return ""

    @classmethod
    def _effective_published_date(cls, result: Dict) -> str:
        return result.get("published_date", "") or cls.extract_embedded_date(result)

    @classmethod
    def _is_update_like_result(cls, result: Dict) -> bool:
        title = cls._title_lower(result)
        url = cls._url_lower(result)
        tokens = [
            "update", "updates", "release", "launch", "announcement",
            "更新", "更新报告", "功能更新", "发布", "发布会", "升级", "动态"
        ]
        return any(token in title for token in tokens) or any(token in url for token in ["/release", "/updates", "/news", "/announcement"])

    @classmethod
    def _is_discussion_like_result(cls, result: Dict) -> bool:
        title = cls._title_lower(result)
        url = cls._url_lower(result)
        title_tokens = ["怎么样", "评价", "评测", "faq", "问答", "review", "how is", "worth it"]
        url_tokens = ["/question/", "/questions/", "/answer/", "/answers/", "/faq"]
        return any(token in title for token in title_tokens) or any(token in url for token in url_tokens)

    @classmethod
    def _is_official_update_path(cls, result: Dict) -> bool:
        url = cls._url_lower(result)
        return any(token in url for token in [
            "/blog", "/news", "/updates", "/update", "/release", "/releases",
            "/announcement", "/announcements", "/press", "/events", "/event",
            "/changelog"
        ])

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

    @staticmethod
    def _query_subject(query: str) -> str:
        stripped = (query or "").strip()
        if not stripped:
            return ""
        chinese_patterns = [
            r"^(.*?)(?:最近|当前|现在)(?:怎么样|如何)\??$",
            r"^(.*?)(?:最新动态|最新消息|最新进展|最新情况)\??$",
            r"^(.*?)(?:的)?(?:产品|公司|平台|服务)?(?:怎么样|如何|现状|近况|最近发展|现在如何)\??$",
        ]
        for pattern in chinese_patterns:
            match = re.match(pattern, stripped)
            if match and match.group(1).strip():
                return match.group(1).strip().lower()
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
        return lowered

    @classmethod
    def _matches_query_brand(cls, result: Dict, query: str) -> bool:
        subject = cls._query_subject(query)
        if not subject:
            return False
        url = cls._url_lower(result)
        title = cls._title_lower(result)
        text = cls._text_lower(result)
        subject_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", subject)
        haystack = " ".join([url, title, text])
        haystack_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", haystack)
        return subject in haystack or (subject_slug and subject_slug in haystack_slug)

    @classmethod
    def _domain_matches_query_brand(cls, domain: str, query: str) -> bool:
        subject = cls._query_subject(query)
        return cls._domain_matches_subject(domain, subject)

    @classmethod
    def _domain_matches_subject(cls, domain: str, subject: str) -> bool:
        if not domain or not subject:
            return False
        normalized_domain = domain.lower()
        subject_slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", subject)
        domain_slug = re.sub(r"[^a-z0-9]+", "", normalized_domain.split(".")[0])
        if subject_slug and (subject_slug in re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", normalized_domain) or (domain_slug and (subject_slug.startswith(domain_slug) or domain_slug.startswith(subject_slug)))):
            return True
        for official_domain, aliases in cls.PLATFORM_OFFICIAL_BRANDS.items():
            if normalized_domain == official_domain or normalized_domain.endswith(f".{official_domain}"):
                return any(alias in subject for alias in aliases)
        return False

    @classmethod
    def _normalize_domain(cls, url: str) -> str:
        domain = urlparse(url).netloc.lower()
        for prefix in ("www.", "m."):
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        return domain

    @classmethod
    def classify_site_role(cls, result: Dict, query: str = "", subject: str = "") -> str:
        parsed = urlparse(result.get("url", ""))
        domain = cls._normalize_domain(result.get("url", ""))
        current_subject = (subject or cls._query_subject(query)).strip().lower()
        domain_brand_match = bool(current_subject and cls._domain_matches_subject(domain, current_subject))
        content_brand_match = bool(current_subject and cls._matches_query_brand(result, current_subject))

        if domain_brand_match:
            return "official"

        path = (parsed.path or "").lower()
        if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in cls.CONDITIONAL_PLATFORM_DOMAINS):
            return "republisher"
        if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in cls.MEDIA_DOMAINS):
            return "media"
        if any(domain == suffix or domain.endswith(f".{suffix}") for suffix in cls.COMMUNITY_DOMAINS):
            if any(token in path for token in ["/question", "/questions", "/answer", "/answers", "/post", "/posts", "/article", "/p/"]):
                return "community"
            return "republisher"

        if content_brand_match and cls._is_official_update_path(result):
            return "official"
        if cls._is_official_update_path(result):
            return "official"

        path = (parsed.path or "").lower()
        if path in {"", "/", "/news"}:
            return "official"
        if any(token in path for token in [
            "/news", "/blog", "/about", "/product", "/products", "/solution", "/solutions",
            "/press", "/announcement", "/announcements", "/event", "/events", "/bbs"
        ]):
            return "official"
        return "neutral"

    @classmethod
    def _is_company_site_like(cls, result: Dict, query: str) -> bool:
        return cls.classify_site_role(result, query=query) == "official"

    @classmethod
    def _is_republisher_like(cls, result: Dict, query: str = "") -> bool:
        return cls.classify_site_role(result, query=query) in {"republisher", "community", "media"}

    @staticmethod
    def _is_fresh_update_intent(intent: str) -> bool:
        return intent in {"status", "release"}

    @classmethod
    def _source_bonus(cls, result: Dict, intent: str) -> float:
        source = result.get("source", "")
        bonus_map = {
            "release": {"brave": 0.05, "tavily": 0.04, "exa": 0.0},
            "troubleshooting": {"brave": 0.06, "exa": 0.02, "tavily": 0.0},
            "news": {"brave": 0.05, "tavily": 0.05, "exa": 0.0},
            "comparison": {"exa": 0.05, "brave": 0.03, "tavily": 0.0},
        }
        return bonus_map.get(intent, {}).get(source, 0.0)

    @classmethod
    def _fresh_update_bonus(cls, result: Dict, intent: str, query: str = "") -> float:
        url = cls._url_lower(result)
        title = cls._title_lower(result)
        effective_date = cls._effective_published_date(result)
        freshness = cls.calculate_freshness_score(effective_date)
        bonus = 0.0

        if cls._is_update_like_result(result):
            bonus += 0.08
            if freshness >= 0.8:
                bonus += 0.12
            elif freshness >= 0.6:
                bonus += 0.06
        elif freshness >= 0.8:
            bonus += 0.08
        elif freshness >= 0.6:
            bonus += 0.04
        elif effective_date:
            bonus -= 0.04
        else:
            bonus -= 0.02

        if cls._is_official_update_path(result):
            bonus += 0.04

        if query and cls._is_company_site_like(result, query):
            bonus += 0.20
            if cls._is_official_update_path(result):
                bonus += 0.10

        if intent == "release":
            if "csdn.net" in url:
                return -1.0
            if "nodejs.org" in url:
                bonus += 0.12
            if any(token in url for token in ["nodejs.org", "/docs/", "/download", "changelog"]):
                bonus += 0.22
            if "/release" in url or "releases/tag" in url:
                bonus += 0.10
            if "github.com" in url and "/releases" in url:
                bonus += 0.06
            if any(token in title for token in ["release", "release notes", "changelog", "download", "文档", "发布说明", "更新日志"]):
                bonus += 0.06
        else:
            if cls._is_discussion_like_result(result) or cls._is_republisher_like(result, query=query):
                bonus -= 0.08

        return round(bonus, 4)

    @classmethod
    def _intent_bonus(cls, result: Dict, intent: str, query: str = "") -> float:
        url = cls._url_lower(result)
        title = cls._title_lower(result)
        text = cls._text_lower(result)
        bonus = 0.0

        if cls._is_fresh_update_intent(intent):
            return cls._fresh_update_bonus(result, intent, query=query)

        elif intent == "troubleshooting":
            if "stackoverflow.com" in url:
                bonus += 0.24
            if "github.com" in url and "/issues" in url:
                bonus += 0.12
            if any(token in url for token in ["/troubleshoot", "/troubleshooting", "/faq", "/known-issues"]):
                bonus += 0.12
            if any(token in title for token in ["error", "fix", "issue", "troubleshooting", "faq", "解决方案", "报错", "错误"]):
                bonus += 0.06

        elif intent == "news":
            if "wikipedia.org" in url:
                bonus -= 0.18
            if any(token in url for token in ["/docs/", "/download", "/release", "/changelog"]):
                bonus -= 0.40
            if any(token in title for token in [
                "最新", "消息", "进展", "更新", "局势", "通报",
                "latest", "update", "updates", "breaking", "developments"
            ]):
                bonus += 0.08
            if result.get("published_date"):
                bonus += 0.10
            if any(token in url for token in ["/news", "/world", "/international", "/article", "/live", "/politics"]):
                bonus += 0.06
            if any(token in url for token in [
                "reuters.com", "apnews.com", "bbc.com", "cnn.com",
                "news.cn", "xinhuanet.com", "rthk.hk"
            ]):
                bonus += 0.08

        elif intent == "comparison":
            if any(token in url for token in ["wikipedia.org", "/release", "/download", "/docs/"]):
                bonus -= 0.14
            if any(token in title for token in [
                " vs ", "comparison", "compare", "pros and cons", "tradeoffs",
                "benchmark", "区别", "优缺点", "怎么选", "哪个好"
            ]):
                bonus += 0.10
            if any(token in url for token in ["/compare", "/comparison", "/benchmark", "/vs"]):
                bonus += 0.10
            if any(token in url for token in ["github.com", "medium.com", "dev.to"]):
                bonus += 0.05

        return round(bonus, 4)

    @classmethod
    def get_source_authority(cls, url: str) -> float:
        """获取来源权威性分数"""
        url_lower = url.lower()

        for domain, score in cls.SOURCE_AUTHORITY.items():
            if domain in url_lower:
                return score

        return cls.SOURCE_AUTHORITY["default"]

    @classmethod
    def calculate_freshness_score(cls, published_date: str) -> float:
        """
        计算时效性分数

        越新的内容分数越高
        """
        if not published_date:
            return 0.5  # 未知日期给中等分数

        try:
            from datetime import datetime, timezone

            # 尝试解析日期
            date_formats = [
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"
            ]

            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(published_date, fmt)
                    break
                except:
                    continue

            if not parsed_date:
                return 0.5

            # 计算年龄
            now = datetime.now(timezone.utc)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

            age_days = (now - parsed_date).days

            # 分数随时间衰减
            if age_days <= 7:
                return 1.0  # 一周内
            elif age_days <= 30:
                return 0.9  # 一月内
            elif age_days <= 90:
                return 0.8  # 三月内
            elif age_days <= 365:
                return 0.6  # 一年内
            else:
                return 0.4  # 一年以上

        except:
            return 0.5

    @classmethod
    def calculate_content_completeness(cls, text: str) -> float:
        """计算内容完整度"""
        length = len(text)

        if length < 500:
            return 0.3
        elif length < 1000:
            return 0.5
        elif length < 2000:
            return 0.7
        elif length < 5000:
            return 0.85
        else:
            return 1.0

    @classmethod
    def score(cls, result: Dict) -> Dict:
        """
        计算综合质量分数

        权重:
        - 来源权威性: 30%
        - 时效性: 30%
        - 内容完整度: 20%
        - 原始相关性分数: 20%
        """
        url = result.get("url", "")
        text = result.get("text", "")
        published_date = cls._effective_published_date(result)
        original_score = result.get("score", 0.5)

        # 各维度分数
        authority = cls.get_source_authority(url)
        freshness = cls.calculate_freshness_score(published_date)
        completeness = cls.calculate_content_completeness(text)

        # 加权计算
        final_score = (
            authority * 0.30 +
            freshness * 0.30 +
            completeness * 0.20 +
            original_score * 0.20
        )

        # 添加到结果中
        result["quality_score"] = round(final_score, 4)
        result["quality_breakdown"] = {
            "authority": round(authority, 4),
            "freshness": round(freshness, 4),
            "completeness": round(completeness, 4),
            "original_score": round(original_score, 4),
            "effective_published_date": published_date,
        }

        return result

    @classmethod
    def rank(cls, results: List[Dict], intent: str = "general", query: str = "") -> List[Dict]:
        """对结果进行质量评分并排序"""
        scored_results = [cls.score(r) for r in results]

        filtered_results = []
        for result in scored_results:
            intent_bonus = cls._intent_bonus(result, intent, query=query)
            if intent == "release" and intent_bonus <= -1.0:
                continue
            source_bonus = cls._source_bonus(result, intent)
            result["intent_bonus"] = intent_bonus
            result["source_bonus"] = source_bonus
            result["final_score"] = round(result["quality_score"] + intent_bonus + source_bonus, 4)
            filtered_results.append(result)

        filtered_results.sort(key=lambda x: x.get("final_score", x["quality_score"]), reverse=True)
        if intent == "status":
            filtered_results = cls._rerank_status_results(filtered_results, query=query)

        # 添加排名
        for i, result in enumerate(filtered_results, 1):
            result["rank"] = i

        return filtered_results

    @classmethod
    def _rerank_status_results(cls, results: List[Dict], query: str = "") -> List[Dict]:
        """为 status 查询提供新近内容保底，避免旧问答页长期压在前面"""
        if len(results) < 2:
            return results

        def freshness(result: Dict) -> float:
            return result.get("quality_breakdown", {}).get("freshness", 0.5)

        def status_priority(result: Dict) -> float:
            bonus = result.get("final_score", result.get("quality_score", 0.0))
            if cls._is_update_like_result(result):
                bonus += 0.08
            if cls._is_official_update_path(result):
                bonus += 0.06
            if query and cls._is_company_site_like(result, query):
                bonus += 0.22
            if freshness(result) >= 0.8:
                bonus += 0.10
            elif freshness(result) >= 0.6:
                bonus += 0.06
            if cls._is_discussion_like_result(result):
                bonus -= 0.08
            return bonus

        candidate_index = None
        candidate_score = None
        for index, result in enumerate(results[:8]):
            result_freshness = freshness(result)
            company_site_like = bool(query and cls._is_company_site_like(result, query))
            if result_freshness < 0.6 and not company_site_like:
                continue
            if not (cls._is_update_like_result(result) or cls._is_official_update_path(result) or company_site_like):
                continue
            score = status_priority(result)
            if candidate_score is None or score > candidate_score:
                candidate_index = index
                candidate_score = score

        if candidate_index is None:
            return results

        top_result = results[0]
        top_is_stale = (
            freshness(top_result) < 0.6
            or cls._is_discussion_like_result(top_result)
            or (query and not cls._is_company_site_like(top_result, query))
        )
        if candidate_index > 0 and top_is_stale:
            promoted = results.pop(candidate_index)
            results.insert(0, promoted)
        elif candidate_index > 2:
            promoted = results.pop(candidate_index)
            results.insert(2, promoted)

        official_indices = [
            idx for idx, item in enumerate(results[:6])
            if query and cls._is_company_site_like(item, query)
        ]
        if official_indices:
            best_official_index = official_indices[0]
            best_official = results[best_official_index]
            leading_republisher = [
                idx for idx, item in enumerate(results[:best_official_index])
                if cls._is_republisher_like(item, query=query) and not cls._is_company_site_like(item, query)
            ]
            if leading_republisher:
                insert_at = leading_republisher[0]
                promoted = results.pop(best_official_index)
                results.insert(insert_at, promoted)

        return results
    PLATFORM_OFFICIAL_BRANDS = {
        "cloud.tencent.com": ["腾讯云", "tencent cloud"],
        "aliyun.com": ["阿里云", "aliyun", "alibaba cloud"],
        "juejin.cn": ["掘金", "juejin"],
        "zhihu.com": ["知乎", "zhihu"],
        "csdn.net": ["csdn"],
        "cnblogs.com": ["博客园", "cnblogs"],
        "segmentfault.com": ["segmentfault", "思否"],
    }
