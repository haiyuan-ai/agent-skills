"""
Agent Search 使用示例
"""
import asyncio
import os
from scripts.agent_search import search, AgentSearch, SearchConfig


async def example_basic():
    """基础用法"""
    # 设置 API Key（实际使用时通过环境变量）
    os.environ["EXA_API_KEY"] = "your-exa-api-key"
    os.environ["BRAVE_API_KEY"] = "your-brave-api-key"  # 可选
    os.environ["TAVILY_API_KEY"] = "your-tavily-api-key"  # 可选
    os.environ["JINA_API_KEY"] = "your-jina-api-key"  # 可选

    # 简单搜索
    result = await search("Claude 3.5 Sonnet 新功能")

    print(f"查询: {result['query']}")
    print(f"找到 {result['total_found']} 条，去重后 {result['unique_count']} 条")
    print(f"\nTop 5 结果:")

    for item in result['results'][:5]:
        print(f"\n{item['rank']}. {item['title']}")
        print(f"   来源: {item['source']} | 质量分: {item['quality_score']}")
        print(f"   URL: {item['url']}")
        print(f"   预览: {item['content'][:150]}...")


async def example_advanced():
    """高级用法 - 自定义配置"""

    config = SearchConfig(
        exa_api_key=os.getenv("EXA_API_KEY"),
        brave_api_key=os.getenv("BRAVE_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        jina_api_key=os.getenv("JINA_API_KEY"),
        max_results=15,
        depth="deep"
    )

    searcher = AgentSearch(config)

    # 中文搜索（自动启用 Brave/Tavily，如已配置）
    result = await searcher.search("Python 异步编程最佳实践")

    print(f"\n搜索查询: {result['query']}")
    print(f"实际查询: {result['search_queries']}")
    print(f"使用来源: {result['sources_used']}")

    for item in result['results'][:3]:
        print(f"\n{item['rank']}. {item['title']}")
        print(f"   质量分解: {item['quality_breakdown']}")
        print(f"   内容来源: {item['content_source']}")


async def example_quick():
    """快速搜索 - 不扩展查询，不深度提取"""

    result = await search(
        query="AI 编程助手对比",
        max_results=5,
        depth="quick",  # 快速模式
        expand=False    # 不扩展查询
    )

    print(f"快速搜索结果: {len(result['results'])} 条")


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Search 示例")
    print("=" * 60)

    # 运行示例
    # asyncio.run(example_basic())
    # asyncio.run(example_advanced())
    # asyncio.run(example_quick())

    print("\n请设置 API Key 后取消注释运行相应示例")
    print("所需环境变量:")
    print("  - EXA_API_KEY (推荐)")
    print("  - BRAVE_API_KEY (可选)")
    print("  - TAVILY_API_KEY (可选)")
    print("  - JINA_API_KEY (可选)")
