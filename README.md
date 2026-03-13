[English](./README.md) | [中文](./README-zh.md)

# agent-skills

A small collection of reusable skills for local coding and agent workflows.

## Included Skills

- `agent-search`: Structured web search with intent detection, multi-source routing, and JSON-friendly output.
- `ai-vibe-detector`: Reviews text for AI-style signals, false-positive risk, and naturalization opportunities.
- `mermaid-to-png`: Converts Mermaid blocks in Markdown into styled PNG or SVG assets.
- `modelscope-zimage-generator`: Generates images with ModelScope Z-Image models, including LoRA-based variants.
- `obsidian-cli`: Operates an Obsidian vault through the official CLI for notes, search, tasks, and metadata.

## Layout

Each skill lives in its own folder and usually includes:

- `SKILL.md`: trigger rules and workflow guidance
- `README.md`: human-readable usage notes
- `references/`: optional deeper references
- `scripts/`: optional helper scripts

Current skill directories:

- [`agent-search`](./agent-search)
- [`ai-vibe-detector`](./ai-vibe-detector)
- [`mermaid-to-png`](./mermaid-to-png)
- [`modelscope-zimage-generator`](./modelscope-zimage-generator)
- [`obsidian-cli`](./obsidian-cli)
