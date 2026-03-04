---
name: obsidian-cli
description: |
  Operate Obsidian Vault via CLI for note management, file operations, and plugin control.
  Use when user needs to read/create/edit/delete notes, manage tasks/todos/tags/properties,
  search vault, organize files, work with daily notes/templates, view backlinks, or manage plugins/themes.
  Make sure to use this skill whenever the user mentions: vault operations, Obsidian notes, markdown files,
  "帮我改下 vault 里那篇文章", "读取 vault", "整理笔记", or any Obsidian CLI commands - even if they don't explicitly say "obsidian-cli".
---

# Obsidian CLI Skill

Automate Obsidian note-taking app using Obsidian CLI (v1.12+) for note management, file operations, plugin control, and more.

## When to Use This Skill

Trigger this skill when the user:

| 场景 | 中文表达示例 | English Examples |
|------|------------|-----------------|
| **Vault + 操作** | "vault 中的文章"、"笔记库里的内容"、"我的 md 文件" | "my vault", "notes in vault", "my md files" |
| **读取/查看** | "读取 vault"、"看看那篇 XX 笔记" | "read my note", "show me my notes", "view this file" |
| **修改/优化** | "修改 vault 内容"、"优化这篇文章"、"帮我改改" | "edit this note", "update my note", "modify the content" |
| **创建/新增** | "创建新笔记"、"新增一篇 md" | "create a new note", "add a note about XX", "new note" |
| **删除/归档** | "删除这篇笔记"、"归档旧文章" | "delete this note", "archive old files", "remove this" |
| **整理/管理** | "整理我的 vault"、"管理笔记库" | "organize my notes", "manage my vault", "cleanup files" |
| **搜索/查找** | "找找关于 AI 的笔记"、"搜索 vault" | "find notes about XX", "search my vault", "lookup" |
| **任务/属性** | "查看待办任务"、"设置标签"、"添加属性" | "my tasks", "set tags", "add property" |
| **插件/主题** | "装个插件"、"换个主题" | "install plugin", "enable theme" |

## Core Workflow

### 1. 解析用户请求

确定操作类型：
- 文件操作：read/create/edit/delete/move/rename
- 内容管理：search/tasks/tags/properties
- 链接管理：backlinks/links/orphans
- 插件主题：install/enable/disable
- 其他：daily notes/templates/workspace

### 2. 构建 CLI 命令

根据命令参考选择对应语法，注意：
- 路径使用 `path="folder/file.md"` 格式
- 带空格的值用引号包裹
- 多行内容使用 `\n` 换行

### 3. 执行命令

**必须使用 `Bash` 工具执行 Obsidian CLI 命令：**

```javascript
// ✅ 正确做法
Bash(`obsidian read path="${filePath}"`)

// ❌ 错误做法
// 直接用 Read 工具读取文件（绕过了 CLI）
```

### 4. 返回结果

将命令输出返回给用户，必要时解释结果含义。

## Prerequisites

执行命令前确认：
1. **Obsidian 应用正在运行** - CLI requires Obsidian app to be running
2. **已启用 CLI** - Settings → General → Command line interface
3. **`obsidian` 命令在 PATH 中**

```bash
# 快速检查
obsidian version
```

## Quick Command Mapping

| User Request / 用户请求 | CLI Command / CLI 命令 |
|------------------------|------------------------|
| "Read note" / "读取笔记" | `obsidian read path="..."` |
| "Create note" / "创建笔记" | `obsidian create path="..." content="..."` |
| "Append content" / "追加内容" | `obsidian append path="..." content="..."` |
| "Delete note" / "删除笔记" | `obsidian delete path="..."` |
| "Search notes" / "搜索笔记" | `obsidian search query="..."` |
| "List files" / "列出文件" | `obsidian files folder="..."` |
| "Read property" / "读取属性" | `obsidian property:read name="..." file="..."` |
| "Set property" / "设置属性" | `obsidian property:set name="..." value="..."` |
| "List tasks" / "列出任务" | `obsidian tasks todo` |
| "Toggle task" / "切换任务" | `obsidian task ref="..." toggle` |
| "Daily note tasks" / "查看日常任务" | `obsidian tasks daily` |
| "Install plugin" / "安装插件" | `obsidian plugin:install id=...` |

### Important Notes

- **Editing files**: CLI has no direct "edit" command. Use: `read` → process text → `create --overwrite`
- **Deleting content**: Read full file, delete externally, then `create path="xxx" overwrite`
- **Parameter syntax**: `parameter=value`, values with spaces need quotes: `"value with spaces"`
- **File targeting**: Use `file="filename"` for fuzzy match, `path="folder/file.md"` for full path

## Common Workflows

### Edit Note Content

```bash
# 1. Read file content
obsidian read path="Writing-MP/article.md"

# 2. Process text externally (delete/replace content)

# 3. Write modified content back
obsidian create path="Writing-MP/article.md" content="modified content" overwrite
```

### Daily Note Workflow

```bash
# Open daily note and add tasks
obsidian command id=daily-notes:daily-notes
obsidian append path="YYYY-MM-DD.md" content="\n## Today's Tasks\n- [ ] Task 1\n- [ ] Task 2"
```

### Task Management

```bash
# View all tasks from daily note
obsidian tasks daily verbose

# Toggle task status
obsidian task daily line=5 toggle

# List incomplete tasks
obsidian tasks todo
```

### Knowledge Management

```bash
# Search notes by keyword
obsidian search query="AI Agent" limit=20

# Find orphan notes
obsidian orphans

# List all tags with counts
obsidian tags counts sort=count
```

### Plugin Development

```bash
# Reload plugin under development
obsidian plugin:reload id="my-plugin"

# Screenshot for testing
obsidian dev:screenshot path="plugin-ui.png"

# Debug with JavaScript
obsidian eval code="app.plugins.getPlugin('my-plugin')"
```

## Resources

详细命令参考：
- `references/file-operations.md` - 文件操作完整命令
- `references/search-links.md` - 搜索和链接管理
- `references/tasks-properties.md` - 任务和属性管理
- `references/plugins-themes.md` - 插件和主题管理
- `references/advanced-commands.md` - 高级命令（workspace/sync/dev）

## Output Formats

Most list commands support multiple output formats:

```bash
# JSON
obsidian tags format=json
obsidian bookmarks format=json

# TSV
obsidian tags format=tsv

# YAML (properties)
obsidian properties format=yaml
```

## Troubleshooting

### Requirements
1. **Obsidian must be running**: CLI requires Obsidian app to be running
2. **Version**: Requires Obsidian 1.12+ installer
3. **CLI registration**: Enable CLI in Obsidian Settings → General → Command line interface
4. **Vault context**: Ensure you're in the correct vault directory or use `vault=` parameter
5. **File paths**: `path=` requires full path from vault root
6. **Plugin ID**: Use community plugin ID, not display name

### macOS

```bash
# Ensure PATH includes Obsidian
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

# Add to ~/.bash_profile for Bash users
echo 'export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"' >> ~/.bash_profile
```

### Windows

Run `Obsidian.com` terminal redirector (included with 1.12.4+ installer)

### Linux

```bash
# Check symlink
ls -l /usr/local/bin/obsidian

# Or create symlink
sudo ln -s /path/to/obsidian /usr/local/bin/obsidian
```
