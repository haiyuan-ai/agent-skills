"""
Gemini Embedding API 封装

使用 Google Gemini gemini-embedding-001 模型生成文本向量。
同步调用（urllib），适合缓存场景的低频使用。
"""
import json
import urllib.request
import urllib.error
from typing import Optional, List


# 默认模型和维度
DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 3072
API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def get_embedding(
    text: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> Optional[List[float]]:
    """
    获取文本的 embedding 向量

    Args:
        text: 输入文本
        api_key: Gemini API Key
        model: 模型名称

    Returns:
        浮点数列表（3072维），失败返回 None
    """
    url = f"{API_BASE}/models/{model}:embedContent?key={api_key}"
    payload = {
        "content": {
            "parts": [{"text": text}]
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["embedding"]["values"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        return None


def get_embeddings_batch(
    texts: List[str],
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> List[Optional[List[float]]]:
    """
    批量获取 embedding（逐条调用，简单可靠）

    Args:
        texts: 文本列表
        api_key: Gemini API Key
        model: 模型名称

    Returns:
        向量列表，失败项为 None
    """
    return [get_embedding(t, api_key, model) for t in texts]
