[English](./README.md) | 中文

# agent-skills

一个用于本地编码与 agent 工作流的轻量级技能集合仓库。

## 已有 Skills

- `agent-search`：带意图识别、多搜索源路由和 JSON 输出的结构化联网搜索。
- `ai-vibe-detector`：分析文本中的 AI 风格信号、误判风险和自然化改写空间。
- `mermaid-to-png`：把 Markdown 里的 Mermaid 代码块转换为带样式的 PNG 或 SVG。
- `modelscope-zimage-generator`：使用 ModelScope Z-Image 系列模型生成图片，支持 LoRA 变体。
- `obsidian-cli`：通过官方 CLI 操作 Obsidian vault，处理笔记、搜索、任务和元数据。

## 目录结构

每个 skill 通常都放在独立目录里，并包含：

- `SKILL.md`：触发规则和工作流说明
- `README.md`：面向人的使用说明
- `references/`：可选的深入参考资料
- `scripts/`：可选的辅助脚本

当前 skill 目录：

- [`agent-search`](./agent-search)
- [`ai-vibe-detector`](./ai-vibe-detector)
- [`mermaid-to-png`](./mermaid-to-png)
- [`modelscope-zimage-generator`](./modelscope-zimage-generator)
- [`obsidian-cli`](./obsidian-cli)
