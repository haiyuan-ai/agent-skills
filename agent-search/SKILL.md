---
name: agent-search
description: |
  智能 Agent 搜索工具，为支持 SKILL.md 的 Agent 提供深度、结构化的联网搜索能力。

  **自动触发条件:**
  - 用户明确要求搜索互联网信息: "搜索", "查一下", "帮我搜", "网上查查", "search for", "look up"
  - 用户需要获取实时/最新外部信息: "最新的XX是什么", "XX有什么新进展", "今年XX趋势"
  - 用户需要对某个话题做深度调研: "帮我调研一下", "研究一下XX的现状", "对比一下XX和YY"
  - 用户用 /agent-search 明确调用

  **不要触发的情况:**
  - 用户在讨论本地代码、报错、重构、git 或其他开发任务
  - 用户明确指定了其他搜索工具: "use exa", "exa search", "用 exa 搜"
  - 用户在问 Agent 自身稳定知识范围内即可回答的问题

  **核心功能:**
  - 多源搜索: Tavily 主引擎 + Brave 补充 + Exa 兜底
  - 结构化输出: CLI 支持 `--json`，便于 Agent 消费

version: 0.6.0
author: Haiyuan AI
---

# Agent Search

## 执行方式

优先执行 CLI，并要求输出 JSON：

```bash
~/.agents/skills/agent-search/scripts/agent-search-cli "用户查询内容" --json
```

如果当前运行环境把 skill 安装在其他路径（如 `~/.claude/skills/`），请改为当前 skill 实际路径后再执行。

## 搜索模式

- `quick`: 不扩展查询，不深度提取，最快，缓存最多 12 小时
- `standard`: 扩展查询，不使用 Jina Reader，按意图缓存 1 小时～3 天
- `deep`: 扩展查询，所有结果都用 Jina Reader 提取全文，按意图缓存 1 小时～3 天

默认用 `standard`。

这些情况建议用 `deep`：
- 用户明确要求“深度调研”“全面梳理”“尽量全”
- 用户在比较多个方案，且需要更多上下文
- 用户问的是近期动态，且结果质量明显依赖正文提取

这些情况建议用 `quick`：
- 用户只是要几个链接或快速确认事实
- 用户已经给了很具体的 query，不需要扩展

## 面向 Agent 的使用约定

- 默认读取 `--json` 输出，不要解析人类可读模式的格式化文本
- 如果用户只要简单事实，优先 `quick` 或 `standard`
- 如果用户指定不要联网，不要触发本 skill
- 如果用户明确要求某个搜索源，优先走对应原生工具，不强制走本 skill
- 更完整的配置、缓存、价格和实现说明见 `README.md`
