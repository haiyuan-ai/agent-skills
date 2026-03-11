---
name: agent-search
description: |
  **Intelligent search tool - USE IMMEDIATELY when user needs external info!**

  **Trigger:** search verbs ("search"/"look up"/"查"/"搜"/"google"), real-time queries ("latest"/"news"/"更新"/"进展"), research/comparison ("调研"/"对比"/"vs"), proper nouns (names/companies/products)

  **Skip:** local operations (git/refactoring); specific tool already mentioned; general knowledge

  **Features:** Multi-source search (Tavily+Brave+Exa), JSON output via `--json`

version: 0.6.0
author: Haiyuan AI
---

# Agent Search

## Execution

Execute via CLI with JSON output:

```bash
~/.agents/skills/agent-search/scripts/agent-search-cli "query" --json
```

If installed at a different path (e.g., `~/.claude/skills/`), use the actual path.

## Search Modes

- `quick`: No query expansion, no deep extraction. Fastest. Cache up to 12h.
- `standard`: Query expansion, no Jina Reader. Cache 1h-3d by intent.
- `deep`: Query expansion, Jina Reader for full text. Cache 1h-3d by intent.

Default: `standard`.

Use `deep` when:
- User asks for "deep research", "comprehensive", "as much as possible"
- Comparing multiple options needing more context
- Recent events where result quality depends on full text

Use `quick` when:
- User just wants links or quick fact check
- User already gave specific query, no expansion needed

## Query Intent Detection

Auto-detects query intent, affects expansion strategy and cache TTL:

| Intent | Keywords | Strategy |
|--------|----------|----------|
| **News** | latest news, updates, "最新消息", "动态" | Less expansion, short cache (1h) |
| **Troubleshooting** | error, crash, "报错", "错误" | Add solution keywords, long cache (3d) |
| **Comparison** | vs, compare, "对比", "区别" | Add pros/cons keywords |
| **Release/Docs** | version, changelog, "版本", "发布说明" | Add docs keywords |
| **General** | default | Standard expansion |

Intent priority: release → troubleshooting → news → comparison → general

## Agent Usage Guidelines

- Read `--json` output by default; don't parse human-readable text
- Use `quick` or `standard` for simple facts
- Don't trigger if user explicitly disables web search
- Use native tool if user explicitly specifies a search source

## Output Constraints (Anti-Hallucination)

**Strict rules - never fabricate information:**

1. **Answer based on search results only**
   - Never add info not in search results
   - Never fabricate names, products, versions, people, data
   - If uncertain, clearly state "no relevant info found in search results"

2. **Facts must have sources**
   - Every key fact must cite source (e.g., from [source website])
   - If results contradict, list different claims with sources

3. **Distinguish certainty levels**
   - Certain: state directly with source
   - Uncertain: use "according to X...", "search results mention..."
   - Not found: clearly state "no relevant info found"

4. **No over-inference**
   - State facts from results only, don't infer beyond
   - Example: if result says "V6.0 released April 2023", don't infer "current latest is V6.0"

5. **Dates and versions**
   - If result shows old version/date, state the info timestamp
   - Example: "According to April 2023 official announcement, latest version is V6.0"
