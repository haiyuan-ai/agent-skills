# Agent Search Skill

为支持 `SKILL.md` 的 Agent 提供深度、结构化的联网搜索能力。

## 特性

- 多源搜索: Tavily 主引擎 + Brave 补充 + Exa 兜底
- 查询扩展: 自动生成互补检索词
- 内容提取: 按需或全量使用 Jina Reader
- 结果融合: 去重、评分、统一排序
- 智能缓存: SQLite 持久化缓存，支持精确 / 相似 / 向量匹配
- 结构化输出: CLI 支持 `--json`，适合 Agent 消费

## 依赖

```bash
pip install -r requirements.txt
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
JINA_API_KEY="your-jina-api-key"
GEMINI_API_KEY="your-gemini-api-key"
EOF
```

搜索功能只要求三者之一存在即可，但默认推荐优先配置 `TAVILY_API_KEY`：

- `TAVILY_API_KEY`
- `BRAVE_API_KEY`
- `EXA_API_KEY`

配置方式（按优先级）：
1. 环境变量
2. `~/.agents/haiyuan-ai/.env` 配置文件（推荐，更新 skill 时不会被覆盖）

- `Tavily` 作为主引擎，普通低频用户只配它也能正常使用
- `Brave` 在已配置时作为网页 / 官方站 / 新闻类补充
- `Exa` 默认不走首轮，只在结果质量不足或 `depth=deep` 时补充

`JINA_API_KEY` 不是必需项。未配置时仍会走 `r.jina.ai` 免费端点做内容提取；如果免费端点失败或超时，搜索结果会回退到原始摘要文本，不影响主搜索流程返回。

价格与额度说明见 `references/pricing.md`。

Exa 当前公开 pricing 页显示每月最多可免费运行 `1000 requests`，且申请 API key 不需要绑定银行卡。部分新账号可能还会在控制台看到额外 promo balance（例如 `$20 balance`）；实际可用额度请以 Exa 控制台的 billing / balance 页面为准。因为 Exa 更适合作为语义补强源，所以普通低频用户不必优先配置它。

Brave 目前不是“完全免费 API key”模式，而是需要先绑定银行卡；账户每月会自动获得 `$5` credits，按当前粗略成本大约可调用 `1000` 次。Brave 还支持设置 monthly spend limit 来控制 API 成本；当达到该上限后，请求会被阻止，直到下一个 billing cycle。

Tavily 有明确的 free plan，限制为 `1000 API credits/month`。从注册门槛和默认可用性看，它更适合作为这个 skill 的默认主引擎。

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

# 深度搜索
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
    jina_api_key="...",
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
- TTL: `quick=2h`，`standard=1h`，`deep=30m`
- 缓存 scope 包含 `strategy version`、`mode`、`expand`、`max_results`，不同搜索模式和不同搜索策略不会互相污染

当前代码里的搜索策略版本是 `v8`。这个版本号用于在搜索策略发生明显变化时隔离旧缓存，例如：

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
      "content_source": "jina",
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
├── requirements.txt
├── example.py
├── references/
│   └── pricing.md
├── scripts/
│   ├── agent-search-cli
│   ├── agent_search.py
│   ├── smart_cache.py
│   ├── smart_similarity.py
│   ├── gemini_embedding.py
│   ├── exa_client.py
│   ├── brave_client.py
│   ├── tavily_client.py
│   ├── jina_client.py
│   └── result_processor.py
└── tests/
    └── test_agent_search.py
```
