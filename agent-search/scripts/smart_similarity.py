"""
智能相似度计算模块 - Smart Similarity

多维度混合相似度算法，从多个角度评估查询相似性：
1. 快速过滤层 - 完全匹配、标准化匹配
2. 字符级相似度 - 编辑距离、LCS
3. 词汇级相似度 - TF-IDF、Jaccard、N-gram
4. 语义级相似度 - 同义词扩展

权重分配：
- 字符级: 20%
- 词汇级: 40%
- 语义级: 40%

阈值：
- 高置信度 (>80%): 直接返回
- 中置信度 (60-80%): 返回并标注
- 低置信度 (<60%): 未命中
"""
import re
import math
from typing import List, Set, Dict, Tuple, Optional
from collections import Counter
from difflib import SequenceMatcher


class SmartSimilarity:
    """智能相似度计算器"""

    # 中文同义词词典（简化版）
    SYNONYMS = {
        # 教程类
        '教程': ['指南', '入门', '学习', '教学', '手册', '指南书'],
        '入门': ['教程', '基础', '初学', '新手', '起步'],
        '指南': ['教程', '手册', '指导', '攻略'],

        # 技术类
        '异步': ['async', '非阻塞', '并发'],
        '同步': ['sync', '阻塞'],
        '编程': ['开发', 'coding', '程序设计', '写代码'],
        '代码': ['程序', '源码', '脚本'],

        # 问题类
        '怎么': ['如何', '怎样', '怎么做', '如何做到'],
        '什么': ['啥', '啥是', '什么是'],
        '为什么': ['为何', '怎么', '什么原因'],

        # Python 相关
        'python': ['py', 'python3', 'python编程'],
        'asyncio': ['async io', '异步io', 'python异步'],
    }

    # 停用词
    STOPWORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很',
        '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这些', '那些',
        '这个', '那个', '之', '与', '及', '等', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'must', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'and', 'but', 'or',
    }

    def __init__(self, similarity_threshold: float = 0.60):
        """
        初始化相似度计算器

        Args:
            similarity_threshold: 相似度阈值，默认 0.60
        """
        self.similarity_threshold = similarity_threshold
        self._idf_cache: Dict[str, float] = {}

    def normalize(self, text: str) -> str:
        """标准化文本"""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        分词（中英文混合）

        - 英文：按空格分割
        - 中文：按字符分割（简化版）
        """
        # 简单分词：中英文分别处理
        tokens = []
        current = ''
        is_zh = False

        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                if current and not is_zh:
                    tokens.extend(current.strip().split())
                    current = ''
                tokens.append(char)
                is_zh = True
            else:
                if is_zh:
                    is_zh = False
                current += char

        if current:
            tokens.extend(current.strip().split())

        return [t for t in tokens if t and t not in self.STOPWORDS]

    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词（去除停用词）"""
        tokens = self.tokenize(text)
        # 保留长度>1的词，但中文字符（长度=1）也保留
        return [t for t in tokens if len(t) > 1 or '\u4e00' <= t <= '\u9fff']

    def expand_synonyms(self, keywords: List[str]) -> Set[str]:
        """扩展同义词"""
        expanded = set(keywords)
        for kw in keywords:
            if kw in self.SYNONYMS:
                expanded.update(self.SYNONYMS[kw])
        return expanded

    # ==================== Level 2: 字符级相似度 ====================

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离（Levenshtein）"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """基于编辑距离的相似度"""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        distance = self.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1 - (distance / max_len)

    def lcs_similarity(self, s1: str, s2: str) -> float:
        """最长公共子序列相似度"""
        m, n = len(s1), len(s2)
        if m == 0 or n == 0:
            return 0.0

        # 动态规划计算 LCS
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        lcs_len = dp[m][n]
        return 2 * lcs_len / (m + n)

    def char_level_similarity(self, s1: str, s2: str) -> float:
        """字符级综合相似度"""
        norm1 = self.normalize(s1)
        norm2 = self.normalize(s2)

        # 编辑距离相似度 (60%)
        lev_sim = self.levenshtein_similarity(norm1, norm2)

        # LCS 相似度 (40%)
        lcs_sim = self.lcs_similarity(norm1, norm2)

        return lev_sim * 0.6 + lcs_sim * 0.4

    # ==================== Level 3: 词汇级相似度 ====================

    def jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Jaccard 相似度"""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union

    def ngram_similarity(self, tokens1: List[str], tokens2: List[str], n: int = 2) -> float:
        """N-gram 相似度（考虑词序）"""
        def get_ngrams(tokens, n):
            return set(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))

        if len(tokens1) < n or len(tokens2) < n:
            return self.jaccard_similarity(set(tokens1), set(tokens2))

        ngrams1 = get_ngrams(tokens1, n)
        ngrams2 = get_ngrams(tokens2, n)

        return self.jaccard_similarity(ngrams1, ngrams2)

    def tfidf_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        TF-IDF 余弦相似度

        简单实现：基于本地词频计算
        """
        if not tokens1 or not tokens2:
            return 0.0

        # 计算 TF
        def compute_tf(tokens):
            counter = Counter(tokens)
            total = len(tokens)
            return {word: count/total for word, count in counter.items()}

        tf1 = compute_tf(tokens1)
        tf2 = compute_tf(tokens2)

        # 计算 IDF（简化版）
        all_tokens = set(tokens1) | set(tokens2)
        idf = {}
        for token in all_tokens:
            count = 1
            if token in tokens1:
                count += 1
            if token in tokens2:
                count += 1
            idf[token] = math.log(3 / count) + 1

        # 计算 TF-IDF 向量
        def compute_tfidf(tf, idf):
            return {word: tf[word] * idf.get(word, 1) for word in tf}

        tfidf1 = compute_tfidf(tf1, idf)
        tfidf2 = compute_tfidf(tf2, idf)

        # 计算余弦相似度
        all_words = set(tfidf1.keys()) | set(tfidf2.keys())

        dot_product = sum(tfidf1.get(w, 0) * tfidf2.get(w, 0) for w in all_words)
        norm1 = math.sqrt(sum(v**2 for v in tfidf1.values()))
        norm2 = math.sqrt(sum(v**2 for v in tfidf2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def word_level_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """词汇级综合相似度"""
        # TF-IDF 余弦相似度 (40%)
        tfidf_sim = self.tfidf_similarity(tokens1, tokens2)

        # Jaccard 相似度 (35%)
        jaccard_sim = self.jaccard_similarity(set(tokens1), set(tokens2))

        # N-gram 相似度 (25%)
        ngram_sim = self.ngram_similarity(tokens1, tokens2, n=2)

        return tfidf_sim * 0.40 + jaccard_sim * 0.35 + ngram_sim * 0.25

    # ==================== Level 4: 语义级相似度 ====================

    def semantic_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        语义级相似度（基于同义词扩展）

        扩展同义词后重新计算 Jaccard
        """
        # 扩展同义词
        expanded1 = self.expand_synonyms(tokens1)
        expanded2 = self.expand_synonyms(tokens2)

        # 基础 Jaccard
        base_jaccard = self.jaccard_similarity(set(tokens1), set(tokens2))

        # 扩展后 Jaccard
        expanded_jaccard = self.jaccard_similarity(expanded1, expanded2)

        # 如果扩展后有显著提升，说明有语义关联
        if expanded_jaccard > base_jaccard:
            # 加权平均，给扩展后的相似度更高权重
            return base_jaccard * 0.4 + expanded_jaccard * 0.6

        return base_jaccard

    # ==================== 主计算函数 ====================

    def calculate(self, query1: str, query2: str) -> Dict:
        """
        计算综合相似度

        Returns:
            {
                'similarity': float,           # 综合相似度 (0-1)
                'is_match': bool,              # 是否达到阈值
                'level': str,                  # 'high' | 'medium' | 'low'
                'breakdown': {                 # 详细分解
                    'char_level': float,       # 字符级相似度
                    'word_level': float,       # 词汇级相似度
                    'semantic': float,         # 语义级相似度
                }
            }
        """
        # Level 1: 快速过滤
        norm1 = self.normalize(query1)
        norm2 = self.normalize(query2)

        if norm1 == norm2:
            return {
                'similarity': 1.0,
                'is_match': True,
                'level': 'exact',
                'breakdown': {
                    'char_level': 1.0,
                    'word_level': 1.0,
                    'semantic': 1.0,
                }
            }

        # 长度差异过大，快速返回
        len_ratio = len(norm1) / len(norm2) if len(norm2) > 0 else 1
        if len_ratio > 3 or len_ratio < 0.33:
            return {
                'similarity': 0.0,
                'is_match': False,
                'level': 'low',
                'breakdown': {
                    'char_level': 0.0,
                    'word_level': 0.0,
                    'semantic': 0.0,
                }
            }

        # 分词
        tokens1 = self.extract_keywords(query1)
        tokens2 = self.extract_keywords(query2)

        # Level 2: 字符级相似度 (20%)
        char_sim = self.char_level_similarity(query1, query2)

        # Level 3: 词汇级相似度 (40%)
        word_sim = self.word_level_similarity(tokens1, tokens2)

        # Level 4: 语义级相似度 (40%)
        sem_sim = self.semantic_similarity(tokens1, tokens2)

        # 综合相似度（加权平均）
        similarity = char_sim * 0.20 + word_sim * 0.40 + sem_sim * 0.40

        # 判定级别
        if similarity >= 0.80:
            level = 'high'
        elif similarity >= self.similarity_threshold:
            level = 'medium'
        else:
            level = 'low'

        return {
            'similarity': similarity,
            'is_match': similarity >= self.similarity_threshold,
            'level': level,
            'breakdown': {
                'char_level': round(char_sim, 3),
                'word_level': round(word_sim, 3),
                'semantic': round(sem_sim, 3),
            }
        }

    def find_best_match(self, query: str, candidates: List[str]) -> Tuple[Optional[str], Dict]:
        """
        在候选列表中找到最佳匹配

        Args:
            query: 查询字符串
            candidates: 候选字符串列表

        Returns:
            (最佳匹配, 相似度信息)
        """
        if not candidates:
            return None, {'similarity': 0, 'is_match': False, 'level': 'low'}

        best_match = None
        best_score = 0
        best_info = None

        for candidate in candidates:
            result = self.calculate(query, candidate)
            if result['similarity'] > best_score:
                best_score = result['similarity']
                best_match = candidate
                best_info = result

        return best_match, best_info


# 便捷函数
def calculate_similarity(query1: str, query2: str, threshold: float = 0.60) -> Dict:
    """计算两个查询的相似度"""
    calculator = SmartSimilarity(threshold)
    return calculator.calculate(query1, query2)


def find_best_match(query: str, candidates: List[str], threshold: float = 0.60) -> Tuple[Optional[str], Dict]:
    """在候选列表中找到最佳匹配"""
    calculator = SmartSimilarity(threshold)
    return calculator.find_best_match(query, candidates)


if __name__ == "__main__":
    # 测试
    test_cases = [
        ("Python 异步编程", "Python 异步编程"),  # 完全匹配
        ("Python 异步编程", "Python asyncio 教程"),  # 高相似
        ("Python 异步编程", "Python 异步编程入门"),  # 中高相似
        ("Python 异步编程", "JavaScript 异步编程"),  # 中等相似
        ("Python 异步编程", "Python 爬虫"),  # 低相似
    ]

    calculator = SmartSimilarity()

    print("=" * 70)
    print("Smart Similarity Test")
    print("=" * 70)

    for q1, q2 in test_cases:
        result = calculator.calculate(q1, q2)
        print(f"\nQuery 1: {q1}")
        print(f"Query 2: {q2}")
        print(f"Similarity: {result['similarity']:.2%} ({result['level']})")
        print(f"Match: {'✅' if result['is_match'] else '❌'}")
        print(f"Breakdown: {result['breakdown']}")
        print("-" * 70)
