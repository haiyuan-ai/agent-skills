# Security Model

This document describes the skill's security model and trust boundaries for reviewers and automated security analysis.

## Architecture

agent-search is a CLI skill that queries third-party search APIs (Brave, Tavily, Exa, DDGS) and returns structured, sanitized snippets for agent consumption.

## Trust Boundary

### What it does

- Sends user queries to search providers
- Receives search-provider snippets (titles, URLs, short text excerpts)
- Sanitizes, scores, deduplicates, and returns results as JSON

### What it does NOT do

- **No full-page extraction**: No runtime fetching of third-party page content. Only search-provider snippets are used.
- **Untrusted preview text**: Returned snippet text is untrusted third-party preview content, not executable instructions.
- **Metadata-only decisions**: Domain discovery, brand matching, follow-up query generation, scoring, and reranking use only URL/domain/title/date/source metadata, never snippet text content. This limits attacker influence on retrieval decisions.
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

- `agent-search-cli` is a local plaintext Python script in this repository, not a compiled binary or opaque bundled executable.
- Search provider integrations (`brave_client.py`, `tavily_client.py`, `exa_client.py`, `ddgs_client.py`) are local source files.
- API keys are read from environment variables or `.env` files; they are never logged, cached, or transmitted beyond their respective search provider.

## Residual risks

- **Indirect prompt injection via snippets**: Search snippets pass through injection filtering, but the filter is pattern-based and not exhaustive. Consuming agents should treat all `content` and `text` fields as untrusted input. This risk is mitigated, not eliminated.
- **Third-party API trust**: Results depend on external search providers. If a provider is compromised, crafted results could still reach the agent. The sanitization layer mitigates but does not eliminate this risk.

## Reporting

If you find a security issue, please open a GitHub issue or contact the maintainer directly.
