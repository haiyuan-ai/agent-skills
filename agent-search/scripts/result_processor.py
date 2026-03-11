"""
搜索结果融合、去重和质量评分
"""
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
    def _intent_bonus(cls, result: Dict, intent: str) -> float:
        url = cls._url_lower(result)
        title = cls._title_lower(result)
        bonus = 0.0

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
        published_date = result.get("published_date", "")
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
            "original_score": round(original_score, 4)
        }

        return result

    @classmethod
    def rank(cls, results: List[Dict], intent: str = "general") -> List[Dict]:
        """对结果进行质量评分并排序"""
        scored_results = [cls.score(r) for r in results]

        filtered_results = []
        for result in scored_results:
            intent_bonus = cls._intent_bonus(result, intent)
            if intent == "release" and intent_bonus <= -1.0:
                continue
            source_bonus = cls._source_bonus(result, intent)
            result["intent_bonus"] = intent_bonus
            result["source_bonus"] = source_bonus
            result["final_score"] = round(result["quality_score"] + intent_bonus + source_bonus, 4)
            filtered_results.append(result)

        filtered_results.sort(key=lambda x: x.get("final_score", x["quality_score"]), reverse=True)

        # 添加排名
        for i, result in enumerate(filtered_results, 1):
            result["rank"] = i

        return filtered_results
