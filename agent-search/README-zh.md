[English](./README.md) | 中文

# Agent Search Skill

为支持 `SKILL.md` 的 Agent 提供深度、结构化的联网搜索能力。

## 特性

- 多源搜索: Tavily 主引擎 + Brave 补充 + Exa 兜底
- 查询扩展: 自动生成互补检索词
- 安全摘要: 仅返回搜索引擎摘要的短摘录，不抓取第三方页面全文
- 结果融合: 去重、评分、统一排序
- 智能缓存: SQLite 持久化缓存，支持精确 / 相似 / 向量匹配
- 结构化输出: CLI 支持 `--json`，适合 Agent 消费

## 搜索策略

Agent Search 自动识别查询意图，针对不同场景采用不同策略：

| 意图类型 | 识别特征 | 扩展策略 | 搜索源 | 缓存 TTL |
|---------|---------|---------|--------|---------|
| **新闻** | 最新消息、动态、局势 | 扩展 3 个查询，加时间限定 | Tavily + Brave | 1 小时 |
| **故障排查** | 报错、错误、无法、失败 | 扩展 2-3 个查询，加解决方案/GitHub | Tavily + Brave | 3 天 |
| **对比** | vs、对比、区别、哪个好 | 扩展 3 个查询，加优缺点/评测 | Tavily + Brave | 3 天 |
| **版本/发布** | 版本、发布说明、changelog | 扩展 2 个查询，加文档关键词 | Tavily 为主 | 1 天 |
| **通用** | 其他查询 | 扩展 2 个查询 | Tavily 为主 | 1 天 |

**搜索源路由逻辑：**
- 首轮查询默认使用 Tavily 主引擎
- 新闻/故障排查/版本类查询，Brave 作为补充源
- Exa 语义搜索作为兜底，在结果质量不足或 `mode=deep` 时启用

**返回内容策略：**
- `mode=quick`: 不扩展查询，只返回搜索摘要安全摘录
- `mode=standard`: 扩展查询，只返回搜索摘要安全摘录
- `mode=deep`: 更广泛检索与 advanced 搜索深度，但仍只返回搜索摘要安全摘录

## 依赖

```bash
pip install -r scripts/requirements.txt
```

运行测试还需要：

```bash
pip install pytest
```

## 配置

支持环境变量或配置文件 `~/.agents/haiyuan-ai/.env`：

```bash
# 创建配置目录
mkdir -p ~/.agents/haiyuan-ai

# 编辑配置文件
cat > ~/.agents/haiyuan-ai/.env << 'EOF'
TAVILY_API_KEY="your-tavily-api-key"
BRAVE_API_KEY="your-brave-api-key"
EXA_API_KEY="your-exa-api-key"
GEMINI_API_KEY="your-gemini-api-key"
EOF
```

搜索功能只要求三者之一存在即可，但默认推荐优先配置 `TAVILY_API_KEY`：

| API | 免费额度 | 特点 |
|-----|---------|------|
| **Tavily** | 1,000 credits/month | 无需绑卡，推荐作为主引擎 |
| **Brave** | 每月 $5 credits（约 1000 次）| 需绑卡，适合网页/新闻搜索 |
| **Exa** | 1,000 requests/month | 无需绑卡，适合语义补强 |

配置方式（按优先级）：
1. 环境变量
2. `~/.agents/haiyuan-ai/.env` 配置文件（推荐，更新 skill 时不会被覆盖）

- `Tavily` 作为主引擎，普通低频用户只配它也能正常使用
- `Brave` 在已配置时作为网页 / 官方站 / 新闻类补充
- `Exa` 默认不走首轮，只在结果质量不足或 `mode=deep` 时补充

出于安全原因，skill 不再抓取第三方网页正文，也不会在运行时加载整页内容到 agent 上下文中。

用于评估“超过免费额度后是否继续付费调用”的粗略成本参考：

| API | 每 1k 请求成本 | 单次请求成本 |
|-----|---------------|-------------|
| Brave | $5 | $0.005 |
| Tavily basic | $8 | $0.008 |

这张表适合作为继续调用的成本估算依据；实际计费请以各服务商当期官方价格为准。

## CLI

```bash
# 人类可读输出
./scripts/agent-search-cli "Python 异步编程"

# 结构化 JSON 输出
./scripts/agent-search-cli "Python 异步编程" --json

# 深度搜索（更广泛检索，但仍为摘要模式）
./scripts/agent-search-cli "Claude 3.5 新功能" --mode deep --max-results 15

# 不扩展查询
./scripts/agent-search-cli "AI 编程助手" --no-expand

# 输出到文件
./scripts/agent-search-cli "AI 编程助手" --json -o results.json
```

## Python API

```python
import asyncio
from scripts.agent_search import search, AgentSearch, SearchConfig

async def main():
    result = await search("Claude 3.5 Sonnet 新功能", mode="standard")
    print(result["results"][0]["title"])

asyncio.run(main())
```

```python
config = SearchConfig(
    exa_api_key="...",
    brave_api_key="...",
    tavily_api_key="...",
    max_results=10,
    mode="standard",
)

searcher = AgentSearch(config)
result = await searcher.search("Python 异步编程")
```

## 缓存

- 存储位置: `~/.agents/haiyuan-ai/agent_search_cache/`
- 匹配层级: 精确 -> 相似 -> 向量
- 默认阈值: 相似匹配 `0.6`，向量匹配 `0.75`
- TTL 按意图决定: `news=1h`、`general=1d`、`troubleshooting=3d`、`comparison=3d`、`release=6h`、`status=6h`
- `quick` 模式会关闭查询扩展，并把缓存 TTL 封顶到 12 小时；`deep` 模式没有单独更短的 TTL
- 缓存 scope 包含 `strategy version`、`mode`、`expand`、`max_results`，不同搜索模式和不同搜索策略不会互相污染

当前代码里的搜索策略版本是 `v24`。这个版本号用于在搜索策略发生明显变化时隔离旧缓存，例如：

- 调整 query expansion 规则
- 新增或修改意图识别
- 修改按意图的 rerank / source bonus
- 改变按意图的搜索源路由

如果你未来明显修改了上述策略，但仍沿用旧缓存 scope，TTL 有效期内可能继续命中旧策略结果。最简单的处理方式有两种：

- 直接执行 `--cache-clear`
- bump `scripts/agent_search.py` 里的 `STRATEGY_VERSION`

缓存管理：

```bash
./scripts/agent-search-cli --cache-stats
./scripts/agent-search-cli --cache-recent 5
./scripts/agent-search-cli --cache-clear
```

## 返回结构

```json
{
  "query": "原始查询",
  "search_queries": ["扩展查询1", "扩展查询2"],
  "sources_used": ["exa", "brave", "tavily"],
  "total_found": 25,
  "unique_count": 18,
  "results_returned": 10,
  "results": [
    {
      "rank": 1,
      "source": "exa",
      "title": "...",
      "url": "...",
      "content": "...",
      "content_source": "search_snippet",
      "content_trust": "untrusted-sanitized",
      "quality_score": 0.92
    }
  ]
}
```

## 目录

```text
agent-search/
├── SKILL.md
├── README.md
├── README-zh.md
├── scripts/
│   ├── agent-search-cli
│   ├── agent_search.py
│   ├── smart_cache.py
│   ├── smart_similarity.py
│   ├── gemini_embedding.py
│   ├── exa_client.py
│   ├── brave_client.py
│   ├── tavily_client.py
│   ├── content_safety.py
│   ├── result_processor.py
│   ├── config.py
│   └── requirements.txt
└── tests/
    └── test_agent_search.py
```
