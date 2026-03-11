"""
Agent Search - 智能 Agent 搜索工具

为 Claude Code Agent 提供深度、结构化的搜索能力。
"""

from .agent_search import search, AgentSearch, SearchConfig

__version__ = "0.1.0"
__all__ = ["search", "AgentSearch", "SearchConfig"]
