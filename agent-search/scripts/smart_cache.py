"""
智能持久化缓存系统 - Smart Persistent Cache

支持：
1. SQLite 持久化存储
2. 多层级缓存匹配（精确 → 相似 → 向量语义）
3. Gemini Embedding 向量搜索（可选，需配置 GEMINI_API_KEY）
4. 自动 TTL 过期清理
5. 缓存统计和命中率分析
"""
import asyncio
import contextlib
import sqlite3
import json
import time
import os
import re
import struct
from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

# 导入智能相似度算法
try:
    from .smart_similarity import SmartSimilarity
except ImportError:
    from smart_similarity import SmartSimilarity

# 导入 Gemini Embedding
try:
    from .gemini_embedding import get_embedding, DEFAULT_DIMENSIONS
except ImportError:
    from gemini_embedding import get_embedding, DEFAULT_DIMENSIONS

# 导入配置
try:
    from .config import get_api_key
except ImportError:
    from config import get_api_key

try:
    from .config import get_primary_config_dir, get_legacy_config_dir
except ImportError:
    from config import get_primary_config_dir, get_legacy_config_dir


def get_default_cache_dir() -> Path:
    override = os.getenv("AGENT_SEARCH_CACHE_DIR")
    if override:
        return Path(os.path.expanduser(override))

    default_root = get_primary_config_dir()
    legacy_cache_dir = get_legacy_config_dir() / "agent_search_cache"
    default_cache_dir = default_root / "agent_search_cache"
    if default_cache_dir.exists():
        return default_cache_dir
    if legacy_cache_dir.exists():
        return legacy_cache_dir
    return default_cache_dir


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """纯 Python 余弦相似度计算（避免强制依赖 numpy）"""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def _pack_vector(vec: List[float]) -> bytes:
    """将浮点数列表打包为 bytes"""
    return struct.pack(f'{len(vec)}f', *vec)


def _unpack_vector(data: bytes) -> List[float]:
    """将 bytes 解包为浮点数列表"""
    count = len(data) // 4
    return list(struct.unpack(f'{count}f', data))


@dataclass
class CacheEntry:
    """缓存条目"""
    query: str                    # 原始查询
    normalized_query: str         # 标准化查询
    result_data: Dict             # 搜索结果
    keywords: List[str]           # 提取的关键词
    timestamp: float              # 创建时间
    access_count: int             # 访问次数
    last_access: float            # 最后访问时间
    ttl: int                      # 过期时间（秒）
    hit_count: int = 0            # 命中次数

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> Dict:
        return {
            'query': self.query,
            'normalized_query': self.normalized_query,
            'result_data': json.dumps(self.result_data),
            'keywords': json.dumps(self.keywords),
            'timestamp': self.timestamp,
            'access_count': self.access_count,
            'last_access': self.last_access,
            'ttl': self.ttl,
            'hit_count': self.hit_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        return cls(
            query=data['query'],
            normalized_query=data['normalized_query'],
            result_data=json.loads(data['result_data']),
            keywords=json.loads(data['keywords']),
            timestamp=data['timestamp'],
            access_count=data['access_count'],
            last_access=data['last_access'],
            ttl=data['ttl'],
            hit_count=data.get('hit_count', 0)
        )


class SmartCache:
    """
    智能持久化缓存

    三级匹配策略：
    1. 精确匹配：查询完全一致
    2. 相似匹配：关键词重合度 > 阈值（SmartSimilarity）
    3. 向量匹配：Gemini Embedding 语义相似度（可选）
    """

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = str(get_default_cache_dir())

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.cache_dir / "search_cache.db"
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

        # 配置参数
        self.similarity_threshold = 0.6
        self.vector_similarity_threshold = 0.75
        self.max_cache_entries = 1000
        self.cleanup_interval = 100
        self.write_count = 0

        # 初始化智能相似度计算器
        self.similarity_calc = SmartSimilarity(self.similarity_threshold)

        # 检查 Gemini API Key
        self.gemini_api_key = get_api_key('GEMINI_API_KEY')
        self.vector_search_available = self.gemini_api_key is not None
    def _get_conn(self) -> sqlite3.Connection:
        """获取复用的数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                normalized_query TEXT NOT NULL,
                result_data TEXT NOT NULL,
                keywords TEXT NOT NULL,
                timestamp REAL NOT NULL,
                access_count INTEGER DEFAULT 1,
                last_access REAL NOT NULL,
                ttl INTEGER DEFAULT 3600,
                hit_count INTEGER DEFAULT 0,
                UNIQUE(normalized_query)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_vectors (
                cache_id INTEGER PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY (cache_id) REFERENCES search_cache(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS content_cache (
                url TEXT PRIMARY KEY,
                content_data TEXT NOT NULL,
                timestamp REAL NOT NULL,
                ttl INTEGER DEFAULT 21600,
                access_count INTEGER DEFAULT 1,
                last_access REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS provider_usage_monthly (
                provider TEXT NOT NULL,
                year_month TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                last_called REAL NOT NULL,
                PRIMARY KEY (provider, year_month)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON search_cache(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_last_access ON search_cache(last_access)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_timestamp ON content_cache(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_content_last_access ON content_cache(last_access)")
        conn.commit()

    def _normalize_query(self, query: str) -> str:
        query = query.lower().strip()
        query = re.sub(r'\s+', ' ', query)
        query = re.sub(r'[^\w\s]', '', query)
        return query

    def _scope_prefix(self, scope: Optional[str] = None) -> str:
        if not scope:
            return ""
        return f"scope={self._normalize_query(scope)}::"

    def _scoped_normalized_query(self, query: str, scope: Optional[str] = None) -> str:
        return f"{self._scope_prefix(scope)}{self._normalize_query(query)}"

    def _extract_keywords(self, query: str) -> List[str]:
        return self.similarity_calc.extract_keywords(query)

    def _extract_identity_tokens(self, query: str) -> Dict[str, set]:
        text = query.lower()
        vendors = set(re.findall(r"\b(openai|anthropic|google|meta|mistral|xai|grok|deepseek|qwen|alibaba|aliyun|claude|gpt|gemini)\b", text))
        versions = set(re.findall(r"\b[a-z]+(?:-[a-z]+)?[- ]\d+(?:\.\d+)*\b|\b[a-z]+-\d+(?:\.\d+)*\b|\b\d+(?:\.\d+)+\b", text))
        versions = {
            token for token in versions
            if not re.fullmatch(r"(?:openai|anthropic|google|meta|mistral|xai|grok|deepseek|qwen|alibaba|aliyun)\s+20\d{2}", token)
        }
        years = set(re.findall(r"\b20\d{2}\b", text))
        quoted_terms = set(re.findall(r"\b[a-z][a-z0-9.+-]{2,}\b", text))
        key_terms = {
            token for token in quoted_terms
            if any(ch.isdigit() for ch in token) or token in vendors
        }
        return {
            "vendors": vendors,
            "versions": versions,
            "years": years,
            "key_terms": key_terms,
        }

    def _is_identity_sensitive_query(self, query: str) -> bool:
        identity = self._extract_identity_tokens(query)
        return bool(identity["vendors"] or identity["versions"] or identity["years"])

    def _passes_identity_guard(self, query: str, cached_query: str) -> bool:
        current = self._extract_identity_tokens(query)
        cached = self._extract_identity_tokens(cached_query)

        for field in ("vendors", "versions", "years"):
            current_values = current[field]
            cached_values = cached[field]
            if current_values and cached_values and current_values != cached_values:
                return False

        current_terms = current["key_terms"]
        cached_terms = cached["key_terms"]
        if current_terms and cached_terms:
            overlap = len(current_terms & cached_terms)
            required = min(len(current_terms), len(cached_terms))
            if overlap < required:
                return False

        return True

    def _get_exact_match(self, query: str, scope: Optional[str] = None) -> Optional[CacheEntry]:
        normalized = self._scoped_normalized_query(query, scope)
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM search_cache WHERE normalized_query = ?",
            (normalized,)
        )
        row = cursor.fetchone()
        if row:
            return CacheEntry.from_dict(dict(row))
        return None

    def _get_similar_match(self, query: str, scope: Optional[str] = None) -> Optional[Tuple[CacheEntry, Dict]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        scope_prefix = self._scope_prefix(scope)
        cursor = conn.execute(
            """
            SELECT * FROM search_cache
            WHERE normalized_query LIKE ?
            ORDER BY last_access DESC
            LIMIT 100
            """,
            (f"{scope_prefix}%",)
        )
        rows = cursor.fetchall()

        best_match = None
        best_result = None

        for row in rows:
            entry = CacheEntry.from_dict(dict(row))
            if entry.is_expired():
                continue
            result = self.similarity_calc.calculate(query, entry.query)
            if result['is_match'] and self._is_identity_sensitive_query(query):
                if not self._passes_identity_guard(query, entry.query):
                    continue
            if result['is_match'] and (best_result is None or result['similarity'] > best_result['similarity']):
                best_result = result
                best_match = entry

        if best_match and best_result:
            return best_match, best_result
        return None

    def _get_vector_match(self, query: str, scope: Optional[str] = None) -> Optional[Tuple[CacheEntry, Dict]]:
        """
        向量语义匹配：调用 Gemini Embedding 生成查询向量，
        与缓存中的向量逐条计算余弦相似度。
        """
        if not self.vector_search_available:
            return None

        query_vec = get_embedding(query, self.gemini_api_key)
        if query_vec is None:
            return None

        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        scope_prefix = self._scope_prefix(scope)
        # 加载所有向量（最多 1000 条，内存安全）
        cursor = conn.execute("""
            SELECT qv.cache_id, qv.embedding, sc.*
            FROM query_vectors qv
            JOIN search_cache sc ON qv.cache_id = sc.id
            WHERE sc.normalized_query LIKE ?
        """, (f"{scope_prefix}%",))
        rows = cursor.fetchall()

        best_entry = None
        best_sim = 0.0

        for row in rows:
            row_dict = dict(row)
            entry = CacheEntry.from_dict(row_dict)
            if entry.is_expired():
                continue
            if self._is_identity_sensitive_query(query) and not self._passes_identity_guard(query, entry.query):
                continue

            cached_vec = _unpack_vector(row_dict['embedding'])
            sim = _cosine_similarity(query_vec, cached_vec)

            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_entry and best_sim >= self.vector_similarity_threshold:
            return best_entry, {
                'similarity': best_sim,
                'is_match': True,
                'level': 'high' if best_sim >= 0.85 else 'medium',
                'breakdown': {
                    'vector_similarity': round(best_sim, 3),
                    'method': 'gemini_embedding'
                }
            }

        return None

    def get(self, query: str, scope: Optional[str] = None) -> Dict:
        """
        获取缓存（三级匹配）

        Returns:
            {
                'hit': True/False,
                'match_type': 'exact'/'similar'/'vector'/'none',
                'similarity': float,
                'data': Dict,
                'original_query': str
            }
        """
        # 1. 精确匹配
        exact = self._get_exact_match(query, scope)
        if exact and not exact.is_expired():
            self._update_access(exact.normalized_query)
            return {
                'hit': True,
                'match_type': 'exact',
                'similarity': 1.0,
                'data': deepcopy(exact.result_data),
                'original_query': exact.query
            }

        # 2. 相似匹配
        similar = self._get_similar_match(query, scope)
        if similar:
            entry, sim_result = similar
            self._update_access(entry.normalized_query)
            return {
                'hit': True,
                'match_type': 'similar',
                'similarity': sim_result['similarity'],
                'similarity_level': sim_result['level'],
                'similarity_breakdown': sim_result['breakdown'],
                'data': deepcopy(entry.result_data),
                'original_query': entry.query
            }

        # 3. 向量匹配
        if self.vector_search_available:
            vector_match = self._get_vector_match(query, scope)
            if vector_match:
                entry, sim_result = vector_match
                self._update_access(entry.normalized_query)
                return {
                    'hit': True,
                    'match_type': 'vector',
                    'similarity': sim_result['similarity'],
                    'similarity_level': sim_result['level'],
                    'similarity_breakdown': sim_result['breakdown'],
                    'data': deepcopy(entry.result_data),
                    'original_query': entry.query
                }

        return {
            'hit': False,
            'match_type': 'none',
            'similarity': 0.0,
            'data': None,
            'original_query': None
        }

    def set(self, query: str, result_data: Dict, ttl: Optional[int] = None, scope: Optional[str] = None):
        if ttl is None:
            ttl = 3600

        normalized = self._scoped_normalized_query(query, scope)
        keywords = self._extract_keywords(query)
        timestamp = time.time()

        entry = CacheEntry(
            query=query,
            normalized_query=normalized,
            result_data=result_data,
            keywords=keywords,
            timestamp=timestamp,
            access_count=1,
            last_access=timestamp,
            ttl=ttl
        )

        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO search_cache
            (query, normalized_query, result_data, keywords, timestamp, access_count, last_access, ttl, hit_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.query,
            entry.normalized_query,
            json.dumps(entry.result_data),
            json.dumps(entry.keywords),
            entry.timestamp,
            entry.access_count,
            entry.last_access,
            entry.ttl,
            entry.hit_count
        ))

        cursor = conn.execute("SELECT id FROM search_cache WHERE normalized_query = ?", (normalized,))
        row = cursor.fetchone()
        cache_id = row[0] if row else None
        conn.commit()

        self.write_count += 1
        if self.write_count >= self.cleanup_interval:
            self.cleanup()
            self.write_count = 0

        return cache_id

    def _store_vector(self, cache_id: int, query: str):
        """调用 Gemini Embedding API 生成向量并存储"""
        vec = get_embedding(query, self.gemini_api_key)
        if vec is None:
            return

        vec_bytes = _pack_vector(vec)
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO query_vectors (cache_id, embedding) VALUES (?, ?)",
            (cache_id, vec_bytes)
        )
        conn.commit()

    async def warm_vector(self, cache_id: Optional[int], query: str):
        """后台生成并存储查询向量，避免阻塞主搜索流程"""
        if not (self.vector_search_available and cache_id):
            return

        vec = await asyncio.to_thread(get_embedding, query, self.gemini_api_key)
        if vec is None:
            return

        vec_bytes = _pack_vector(vec)
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO query_vectors (cache_id, embedding) VALUES (?, ?)",
            (cache_id, vec_bytes)
        )
        conn.commit()

    def _update_access(self, normalized_query: str):
        conn = self._get_conn()
        conn.execute("""
            UPDATE search_cache
            SET access_count = access_count + 1,
                last_access = ?,
                hit_count = hit_count + 1
            WHERE normalized_query = ?
        """, (time.time(), normalized_query))
        conn.commit()

    def cleanup(self):
        current_time = time.time()
        conn = self._get_conn()
        # 删除过期条目（CASCADE 会自动删除对应向量）
        conn.execute("""
            DELETE FROM search_cache WHERE (? - timestamp) > ttl
        """, (current_time,))

        # 容量溢出清理
        conn.execute("""
            DELETE FROM search_cache
            WHERE id NOT IN (
                SELECT id FROM search_cache
                ORDER BY last_access DESC
                LIMIT ?
            )
        """, (self.max_cache_entries,))
        conn.execute("""
            DELETE FROM content_cache WHERE (? - timestamp) > ttl
        """, (current_time,))

        conn.commit()

    def get_stats(self) -> Dict:
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) FROM search_cache")
        total = cursor.fetchone()[0]

        cursor = conn.execute("""
            SELECT COUNT(*) FROM search_cache WHERE (? - timestamp) > ttl
        """, (time.time(),))
        expired = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COALESCE(SUM(hit_count), 0) FROM search_cache")
        total_hits = cursor.fetchone()[0]

        db_size = os.path.getsize(self.db_path) if self.db_path.exists() else 0

        vector_count = 0
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM query_vectors")
            vector_count = cursor.fetchone()[0]
        except Exception:
            pass

        return {
            'total_entries': total,
            'expired_entries': expired,
            'active_entries': total - expired,
            'total_hits': total_hits,
            'db_size_mb': round(db_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir),
            'vector_search_enabled': self.vector_search_available,
            'vector_entries': vector_count
        }

    def clear(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM query_vectors")
        conn.execute("DELETE FROM search_cache")
        conn.execute("DELETE FROM content_cache")
        conn.commit()

    def list_recent(self, limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT query, timestamp, last_access, access_count, hit_count
            FROM search_cache
            ORDER BY last_access DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_cached_content(self, url: str) -> Optional[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM content_cache WHERE url = ?",
            (url,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        row_dict = dict(row)
        if time.time() - row_dict["timestamp"] > row_dict["ttl"]:
            conn.execute("DELETE FROM content_cache WHERE url = ?", (url,))
            conn.commit()
            return None

        conn.execute("""
            UPDATE content_cache
            SET access_count = access_count + 1,
                last_access = ?
            WHERE url = ?
        """, (time.time(), url))
        conn.commit()

        return json.loads(row_dict["content_data"])

    def set_cached_content(self, url: str, content_data: Dict, ttl: int = 21600):
        timestamp = time.time()
        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO content_cache
            (url, content_data, timestamp, ttl, access_count, last_access)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            url,
            json.dumps(content_data),
            timestamp,
            ttl,
            1,
            timestamp
        ))
        conn.commit()

    @staticmethod
    def _current_year_month() -> str:
        return datetime.now().strftime("%Y-%m")

    def record_provider_usage(self, provider: str, success: bool):
        year_month = self._current_year_month()
        now = time.time()
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO provider_usage_monthly
            (provider, year_month, request_count, success_count, error_count, last_called)
            VALUES (?, ?, 1, ?, ?, ?)
            ON CONFLICT(provider, year_month) DO UPDATE SET
                request_count = request_count + 1,
                success_count = success_count + excluded.success_count,
                error_count = error_count + excluded.error_count,
                last_called = excluded.last_called
        """, (
            provider,
            year_month,
            1 if success else 0,
            0 if success else 1,
            now,
        ))
        conn.commit()

    def get_provider_usage_stats(self, year_month: Optional[str] = None) -> List[Dict]:
        if year_month is None:
            year_month = self._current_year_month()
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT provider, year_month, request_count, success_count, error_count, last_called
            FROM provider_usage_monthly
            WHERE year_month = ?
            ORDER BY provider ASC
        """, (year_month,))
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_provider_free_limits() -> Dict[str, int]:
        return {
            "exa": 1000,
            "brave": 1000,
            "tavily": 1000,
        }

    def get_provider_warnings(self, year_month: Optional[str] = None) -> List[Dict]:
        limits = self.get_provider_free_limits()
        warnings = []
        for item in self.get_provider_usage_stats(year_month):
            provider = item["provider"]
            limit = limits.get(provider)
            if not limit:
                continue
            usage = item["request_count"]
            ratio = usage / limit
            if ratio >= 0.95:
                warnings.append({
                    "provider": provider,
                    "request_count": usage,
                    "free_limit": limit,
                    "usage_ratio": round(ratio, 4),
                    "level": "critical",
                })
            elif ratio >= 0.8:
                warnings.append({
                    "provider": provider,
                    "request_count": usage,
                    "free_limit": limit,
                    "usage_ratio": round(ratio, 4),
                    "level": "warning",
                })
        return warnings


class NullSmartCache:
    """No-op cache used when persistent cache initialization fails."""

    vector_search_available = False
    cache_dir = Path("<disabled>")

    def get(self, query: str, scope: Optional[str] = None) -> Dict:
        return {
            "hit": False,
            "match_type": "none",
            "similarity": 0.0,
            "data": None,
        }

    def set(self, query: str, result_data: Dict, ttl: int = 3600, scope: Optional[str] = None):
        return None

    def clear(self):
        return None

    def get_stats(self) -> Dict:
        return {
            "total_entries": 0,
            "active_entries": 0,
            "expired_entries": 0,
            "total_hits": 0,
            "db_size_mb": 0,
            "cache_dir": str(self.cache_dir),
            "vector_search_enabled": False,
            "vector_entries": 0,
        }

    def list_recent(self, limit: int = 10) -> List[Dict]:
        return []

    def get_provider_usage_stats(self, year_month: Optional[str] = None) -> List[Dict]:
        return []

    def get_provider_free_limits(self) -> Dict[str, int]:
        return {
            "exa": 1000,
            "brave": 1000,
            "tavily": 1000,
        }

    def get_provider_warnings(self, year_month: Optional[str] = None) -> List[Dict]:
        return []

    def record_provider_usage(self, provider: str, success: bool = True) -> None:
        return None

    def set_cached_content(self, url: str, content: Dict, ttl: int = 21600) -> None:
        return None

    def get_cached_content(self, url: str):
        return None

    async def warm_vector(self, cache_id: Optional[int], query: str) -> None:
        return None


# 全局缓存实例
_global_smart_cache: Optional[object] = None


def get_smart_cache():
    global _global_smart_cache
    if _global_smart_cache is None:
        try:
            _global_smart_cache = SmartCache()
        except Exception as exc:
            suggested_dir = get_default_cache_dir()
            print(
                "⚠️ Cache unavailable, continuing without persistent cache: "
                f"{exc}. Ensure the cache path is writable or set "
                f"AGENT_SEARCH_CACHE_DIR (for example: {suggested_dir})."
            )
            _global_smart_cache = NullSmartCache()
    return _global_smart_cache


def clear_smart_cache():
    global _global_smart_cache
    if _global_smart_cache:
        with contextlib.suppress(Exception):
            _global_smart_cache.clear()
    _global_smart_cache = None
