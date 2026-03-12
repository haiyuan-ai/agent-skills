[English](./README.md) | [中文](./README-zh.md)

# Agent Search Skill

Deep, structured web search for agents that support `SKILL.md`.

## Features

- Multi-source search: Tavily as the primary engine, Brave as a supplement, and Exa as a fallback
- Query expansion: Automatically generates complementary search terms
- Safe summaries: Returns only short excerpts from search engine snippets and does not fetch full third-party page content
- Result fusion: Deduplicates, scores, and ranks results consistently
- Smart cache: SQLite-backed persistent cache with exact, similarity, and vector matching
- Structured output: CLI supports `--json` for agent-friendly consumption

## Search Strategy

Agent Search detects query intent automatically and uses different strategies for different scenarios:

| Intent Type | Signals | Expansion Strategy | Search Sources | Cache TTL |
|------------|---------|--------------------|----------------|-----------|
| **News** | Latest updates, developments, ongoing situations | Expand to 3 queries with time constraints | Tavily + Brave | 1 hour |
| **Troubleshooting** | Errors, failures, not working, broken behavior | Expand to 2-3 queries with solution and GitHub terms | Tavily + Brave | 3 days |
| **Comparison** | vs, compare, differences, which is better | Expand to 3 queries with pros, cons, and reviews | Tavily + Brave | 3 days |
| **Version / Release** | Version, release notes, changelog | Expand to 2 queries with documentation terms | Mostly Tavily | 1 day |
| **General** | Everything else | Expand to 2 queries | Mostly Tavily | 1 day |

**Search source routing:**
- The first round uses Tavily by default as the primary engine
- For news, troubleshooting, and version-related queries, Brave is used as a supplemental source
- Exa semantic search is used as a fallback when result quality is insufficient or when `mode=deep`

**Returned content policy:**
- `mode=quick`: No query expansion, returns only safe excerpts from search snippets
- `mode=standard`: Expands queries, still returns only safe excerpts from search snippets
- `mode=deep`: Broader retrieval with advanced search depth, but still returns only safe excerpts from search snippets

## Dependencies

```bash
pip install -r scripts/requirements.txt
```

To run tests, also install:

```bash
pip install pytest
```

## Configuration

You can configure the tool with environment variables or a config file at `~/.agents/haiyuan-ai/.env`:

```bash
# Create the config directory
mkdir -p ~/.agents/haiyuan-ai

# Create the config file
cat > ~/.agents/haiyuan-ai/.env << 'EOF'
TAVILY_API_KEY="your-tavily-api-key"
BRAVE_API_KEY="your-brave-api-key"
EXA_API_KEY="your-exa-api-key"
GEMINI_API_KEY="your-gemini-api-key"
EOF
```

Only one of the three search APIs is required, but `TAVILY_API_KEY` is the recommended default:

| API | Free Tier | Notes |
|-----|-----------|-------|
| **Tavily** | 1,000 credits/month | No card required, recommended as the primary engine |
| **Brave** | $5 monthly credits, about 1,000 requests | Card required, useful for web and news search |
| **Exa** | 1,000 requests/month | No card required, useful for semantic coverage |

Configuration priority:
1. Environment variables
2. `~/.agents/haiyuan-ai/.env` config file, recommended because skill updates will not overwrite it

- `Tavily` is the primary engine, and it is enough for normal low-frequency usage
- `Brave` is used when configured as an additional source for web, official site, and news queries
- `Exa` is not used in the first pass by default and only supplements weak results or `mode=deep`

For safety reasons, this skill no longer fetches third-party page bodies and does not load full pages into the agent context at runtime.

Approximate cost reference for deciding whether to continue paid calls after the free tier:

| API | Cost per 1k Requests | Cost per Request |
|-----|----------------------|------------------|
| Brave | $5 | $0.005 |
| Tavily basic | $8 | $0.008 |

Use this table only as a rough estimate. Always check current official pricing from the providers.

## CLI

```bash
# Human-readable output
./scripts/agent-search-cli "Python async programming"

# Structured JSON output
./scripts/agent-search-cli "Python async programming" --json

# Deep search with broader retrieval, still snippet-only mode
./scripts/agent-search-cli "Claude 3.5 new features" --mode deep --max-results 15

# Disable query expansion
./scripts/agent-search-cli "AI coding assistant" --no-expand

# Write output to a file
./scripts/agent-search-cli "AI coding assistant" --json -o results.json
```

## Python API

```python
import asyncio
from scripts.agent_search import search, AgentSearch, SearchConfig

async def main():
    result = await search("Claude 3.5 Sonnet new features", mode="standard")
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
result = await searcher.search("Python async programming")
```

## Cache

- Storage path: `~/.agents/haiyuan-ai/agent_search_cache/`
- Match order: exact -> similarity -> vector
- Default thresholds: similarity match `0.6`, vector match `0.75`
- TTL: `quick=2h`, `standard=1h`, `deep=30m`
- Cache scope includes `strategy version`, `mode`, `expand`, and `max_results`, so different search modes and strategies do not pollute each other

The current search strategy version in the code is `v8`. This version isolates old cache entries when the search strategy changes significantly, for example:

- Query expansion rules are adjusted
- Intent detection is added or modified
- Intent-based reranking or source bonuses change
- Source routing changes by intent

If you make meaningful changes to the strategy in the future but keep the old cache scope, cached results from the previous strategy may still be served until TTL expires. The simplest ways to handle this are:

- Run `--cache-clear`
- Bump `STRATEGY_VERSION` in `scripts/agent_search.py`

Cache management:

```bash
./scripts/agent-search-cli --cache-stats
./scripts/agent-search-cli --cache-recent 5
./scripts/agent-search-cli --cache-clear
```

## Response Shape

```json
{
  "query": "original query",
  "search_queries": ["expanded query 1", "expanded query 2"],
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

## Directory Layout

```text
agent-search/
├── SKILL.md
├── README.md
├── README-zh.md
├── example.py
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
│   ├── jina_client.py
│   ├── result_processor.py
│   ├── config.py
│   └── requirements.txt
└── tests/
    └── test_agent_search.py
```
