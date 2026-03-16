"""
配置管理模块 - 支持从环境变量和 .env 文件加载配置
"""
import os
from pathlib import Path
from typing import Optional


def get_primary_config_dir() -> Path:
    return Path.home() / ".config" / "haiyuan-ai"


def get_legacy_config_dir() -> Path:
    return Path.home() / ".agents" / "haiyuan-ai"


def get_primary_env_path() -> Path:
    return get_primary_config_dir() / ".env"


def get_legacy_env_path() -> Path:
    return get_legacy_config_dir() / ".env"


def get_default_env_path() -> Path:
    primary_env_path = get_primary_env_path()
    legacy_env_path = get_legacy_env_path()
    if primary_env_path.exists():
        return primary_env_path
    if legacy_env_path.exists():
        return legacy_env_path
    return primary_env_path


def load_env_file(env_path: Optional[Path] = None) -> dict:
    """
    从 .env 文件加载环境变量

    Args:
        env_path: .env 文件路径，默认为 ~/.config/haiyuan-ai/.env，并兼容 ~/.agents/haiyuan-ai/.env

    Returns:
        加载的环境变量字典
    """
    env_vars = {}

    # 如果未指定路径，尝试查找 .env 文件
    if env_path is None:
        primary_env_path = get_primary_env_path()
        legacy_env_path = get_legacy_env_path()

        # 从当前文件位置开始向上查找
        current_dir = Path(__file__).parent.resolve()
        search_paths = [
            primary_env_path,               # ~/.config/haiyuan-ai/.env (推荐)
            legacy_env_path,                # ~/.agents/haiyuan-ai/.env (兼容旧路径)
            current_dir / ".env",           # scripts/.env
            current_dir.parent / ".env",    # agent-search/.env
            Path.cwd() / ".env",            # 当前工作目录/.env
        ]

        for path in search_paths:
            if path.exists():
                env_path = path
                break

    if env_path and env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#') or line.startswith('//'):
                    continue

                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 移除引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    env_vars[key] = value

    return env_vars


def get_api_key(key_name: str, env_file: Optional[Path] = None) -> Optional[str]:
    """
    获取 API Key，优先从环境变量读取，其次从 .env 文件读取

    Args:
        key_name: API Key 名称 (如 EXA_API_KEY)
        env_file: 可选的 .env 文件路径

    Returns:
        API Key 或 None
    """
    # 1. 首先尝试从环境变量读取
    env_value = os.getenv(key_name)
    if env_value:
        return env_value

    # 2. 从 .env 文件读取
    env_vars = load_env_file(env_file)
    return env_vars.get(key_name)


def get_config() -> dict:
    """
    获取所有搜索相关配置

    Returns:
        配置字典
    """
    return {
        'exa_api_key': get_api_key('EXA_API_KEY'),
        'brave_api_key': get_api_key('BRAVE_API_KEY'),
        'tavily_api_key': get_api_key('TAVILY_API_KEY'),
        'gemini_api_key': get_api_key('GEMINI_API_KEY'),
    }


def save_api_key(key_name: str, key_value: str, env_path: Optional[Path] = None) -> Path:
    """
    保存 API Key 到 .env 文件

    Args:
        key_name: API Key 名称
        key_value: API Key 值
        env_path: .env 文件路径，默认为 ~/.config/haiyuan-ai/.env，并兼容 ~/.agents/haiyuan-ai/.env

    Returns:
        保存的文件路径
    """
    if env_path is None:
        # 默认保存到 ~/.config/haiyuan-ai/.env；如果旧 .env 已存在且新路径不存在，则继续写旧路径
        env_path = get_default_env_path()
        env_path.parent.mkdir(parents=True, exist_ok=True)

    env_path = Path(env_path)

    # 读取现有内容
    existing_vars = {}
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    existing_vars[k.strip()] = v.strip()

    # 更新或添加新的 key
    existing_vars[key_name] = key_value

    # 写回文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("# Agent Search API Keys\n")
        f.write("# Generated automatically - DO NOT COMMIT\n\n")

        for k, v in sorted(existing_vars.items()):
            # 如果值包含特殊字符，用引号包裹
            if ' ' in v or '#' in v:
                f.write(f'{k}="{v}"\n')
            else:
                f.write(f'{k}={v}\n')

    return env_path
