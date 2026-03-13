# Security Model

## Architecture

agent-search is a CLI tool that queries third-party search APIs (Brave, Tavily, Exa) and returns structured, sanitized snippets. It is designed to be invoked by AI agents (Claude Code, etc.) as a skill.

## Content trust boundary

### What it does

- Sends user queries to search providers
- Receives search-provider snippets (titles, URLs, short text excerpts)
- Sanitizes, scores, deduplicates, and returns results as JSON

### What it does NOT do

- **No full-page extraction**: The Jina Reader integration was removed. `jina_client.py` is a compatibility stub that performs no remote requests.
- **No snippet-driven routing**: Domain discovery, brand matching, and follow-up query generation use only URL/domain/title fields — never snippet text content. This prevents attackers from influencing search routing by embedding keywords in page body.
- **No code execution from results**: Search results are data only; no field is evaluated or executed.

## Injection defense (content_safety.py)

| Layer | Protection |
|-------|-----------|
| Line-level filtering | Known prompt injection patterns (EN + ZH) are detected and stripped |
| Cross-line check | Joined text is re-checked to catch split-line bypass attempts |
| Truncation | Snippets capped at 700 chars |
| HTML/code stripping | HTML tags and fenced code blocks removed |
| Title check | Titles containing injection patterns are cleared |
| URL allowlist | Only `http(s)://` URLs are allowed; all other schemes are rejected |
| Trust labeling | Every result carries `content_trust: untrusted-third-party` and `safety_notice` |

## Supply chain

- `agent-search-cli` is a plaintext Python script in this repository, not a compiled binary or system-installed package.
- All search client modules (`brave_client.py`, `tavily_client.py`, `exa_client.py`) are local source files, not external packages.
- Runtime dependency: `aiohttp` pinned to exact version in `requirements.txt` for reproducibility.
- API keys are read from environment variables or `.env` files; they are never logged, cached, or transmitted beyond their respective search provider.

## Residual risks

- **Indirect prompt injection via snippets**: Search snippets pass through injection filtering but the filter is pattern-based and not exhaustive. Consuming agents should treat all `content` and `text` fields as untrusted user input.
- **Third-party API trust**: Results depend on Brave/Tavily/Exa APIs. If a provider is compromised, crafted results could reach the agent. The sanitization layer mitigates but does not eliminate this risk.

## Reporting

If you find a security issue, please open a GitHub issue or contact the maintainer directly.
