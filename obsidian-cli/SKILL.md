---
name: obsidian-cli
description: |
  Use when user needs to operate Obsidian Vault via CLI.
  Triggers: vault/笔记/笔记库/Markdown 文件操作，读取/修改/优化/更新/删除/创建/整理/搜索 笔记，
  read/edit/update/delete/create/search/organize/list notes or files,
  管理任务/todos、标签/tags、属性/properties、模板/templates、日常日记/daily notes,
  查看反向链接/backlinks、孤立笔记，管理插件/主题
  Key phrases: "vault 中的文章", "优化笔记", "读取 vault", "整理笔记", "找找那篇",
  "日常记录", "任务管理", "backlinks", "obsidian", "my notes", "md 文件",
  "my vault", "edit note", "create note", "search vault", "organize files",
  "list files", "delete file", "update content", "read from vault"
allowed-tools:
  - Bash
metadata:
  trigger: Obsidian Vault 操作，笔记管理，CLI 命令
---

# Obsidian CLI Skill

Automate Obsidian note-taking app using Obsidian CLI (v1.12+) for note management, file operations, plugin control, and more.

## ⚡ Execution Instructions / 执行指令

**当用户触发此 skill 时，必须使用 `Bash` 工具执行 Obsidian CLI 命令：**

```javascript
// ✅ 正确做法
Bash(`obsidian read path="${filePath}"`)

// ❌ 错误做法
// 直接用 Read 工具读取文件（绕过了 CLI）
// 调用 TaskOutput 获取结果（这不是异步任务）
```

### 执行流程 / Workflow

1. **解析用户请求** → 确定操作类型（read/create/search 等）
2. **构建 CLI 命令** → 根据命令参考选择对应语法
3. **执行命令** → 使用 `Bash` 工具执行
4. **返回结果** → 将命令输出返回给用户

### 前置检查 / Prerequisites

执行命令前确认：
- Obsidian 应用正在运行
- 已启用 CLI（Settings → General → Command line interface）
- `obsidian` 命令在 PATH 中

```bash
# 快速检查
obsidian version
```

---

## ⚠️ IMPORTANT: When This Skill Applies

### Core Triggers（核心触发）

**用户提到以下任一表达时，此 skill 适用：**

| 场景 | 中文表达示例 | English Examples |
|------|------------|-----------------|
| **Vault + 操作** | "vault 中的文章"、"笔记库里的内容"、"我的 md 文件" | "my vault", "notes in vault", "my md files" |
| **读取/查看** | "读取 vault"、"看看那篇 XX 笔记" | "read my note", "show me my notes", "view this file" |
| **修改/优化** | "修改 vault 内容"、"优化这篇文章"、"帮我改改" | "edit this note", "update my note", "modify the content" |
| **创建/新增** | "创建新笔记"、"新增一篇 md" | "create a new note", "add a note about XX", "new note" |
| **删除/归档** | "删除这篇笔记"、"归档旧文章" | "delete this note", "archive old files", "remove this" |
| **整理/管理** | "整理我的 vault"、"管理笔记库" | "organize my notes", "manage my vault", "cleanup files" |
| **搜索/查找** | "找找关于 AI 的笔记"、"搜索 vault" | "find notes about XX", "search my vault", "lookup" |
| **列出/统计** | "列出所有文件"、"有多少笔记" | "list all files", "count my notes", "show all notes" |
| **直接说产品名** | "obsidian create"、"用 obsidian 命令" | "obsidian cli", "run obsidian command" |

### File Operations（文件操作）

- 创建/读取/编辑/修改/删除/移动/重命名 笔记或 markdown 文件
- "帮我改下 vault 里那篇 XX 文章"、"把这篇文章移到 XX 文件夹"
- "列出 vault 里所有的 md 文件"
- "edit this file", "read my note", "delete the article", "move to folder"
- obsidian create/read/edit/delete/modify/rename/move/files

### Content Management（内容管理）

- 搜索笔记、查找内容、"找找那篇关于 XX 的笔记"
- "search notes", "find content", "lookup in vault"
- 管理任务、todos、待办事项、"我还有什么没完成"
- "my tasks", "pending todos", "what's left"
- 管理标签 tags、属性 properties、aliases
- 日常笔记 daily notes、"今天的日记"、"写日报"
- "daily journal", "today's note"
- 模板 templates、"套用会议记录模板"
- "use template", "meeting note template"
- obsidian search/tasks/tags/properties/daily/templates

### Link & Graph（链接与图谱）

- 查看反向链接 backlinks、"谁引用了这篇"
- "backlinks", "who linked this"
- 查看出向链接 outgoing links
- 查找孤立笔记 orphans、"没有链接的笔记"
- "orphan notes", "files without links"
- 查找死胡同笔记 deadends
- obsidian backlinks/links/orphans/deadends

### Plugins & Themes（插件与主题）

- 安装/启用/禁用/卸载 插件或主题
- "给 obsidian 装个 git 插件"
- "install plugin", "enable theme", "disable addon"
- obsidian plugins/themes install/enable/disable/uninstall

---

## 🚀 Quick Command Mapping / 快速命令映射

| User Request / 用户请求 | CLI Command / CLI 命令 | Bash Example / Bash 示例 |
|------------------------|------------------------|--------------------------|
| "Read note" / "读取笔记" | `obsidian read path="..."` | `Bash('obsidian read path="file.md"')` |
| "Create note" / "创建笔记" | `obsidian create path="..." content="..."` | `Bash('obsidian create path="file.md" content="..."')` |
| "Append content" / "追加内容" | `obsidian append path="..." content="..."` | `Bash('obsidian append path="file.md" content="..."')` |
| "Delete note" / "删除笔记" | `obsidian delete path="..."` | `Bash('obsidian delete path="file.md"')` |
| "Search notes" / "搜索笔记" | `obsidian search query="..."` | `Bash('obsidian search query="keyword"')` |
| "List files" / "列出文件" | `obsidian files folder="..."` | `Bash('obsidian files folder="InBox"')` |
| "Read property" / "读取属性" | `obsidian property:read name="..." file="..."` | `Bash('obsidian property:read name="tags" file="file.md"')` |
| "Set property" / "设置属性" | `obsidian property:set name="..." value="..."` | `Bash('obsidian property:set name="tags" value="[\"a\",\"b\"]"')` |
| "List tasks" / "列出任务" | `obsidian tasks todo` | `Bash('obsidian tasks todo')` |
| "Toggle task" / "切换任务" | `obsidian task ref="..." toggle` | `Bash('obsidian task ref="file.md:5" toggle')` |
| "Daily note" / "日常笔记" | `obsidian daily` | `Bash('obsidian daily')` |
| "Read template" / "读取模板" | `obsidian template:read name="..."` | `Bash('obsidian template:read name="Meeting"')` |
| "Install plugin" / "安装插件" | `obsidian plugin:install id=...` | `Bash('obsidian plugin:install id=obsidian-git')` |
| "Enable plugin" / "启用插件" | `obsidian plugin:enable id="..."` | `Bash('obsidian plugin:enable id="obsidian-git"')` |

## Important Notes

- **Editing files**: CLI has no direct "edit" command. Use: `read` → process text → `create --overwrite`
- **Deleting content**: Read full file, delete externally, then `create path="xxx" overwrite`
- **Replacing content**: Read full file, replace externally, then `create path="xxx" overwrite`

---

## Command Reference

### File Operations

```bash
# Create file
obsidian create name=filename content="content" template=templatename open overwrite

# Read file
obsidian read file="filename"
obsidian read path="folder/filename.md"

# Append content
obsidian append file="filename" content="content to append"
obsidian append file="filename" content="line content" inline

# Prepend content (after frontmatter)
obsidian prepend file="filename" content="content to prepend"

# Delete file
obsidian delete file="filename"
obsidian delete file="filename" permanent

# Move/Rename file
obsidian move file="filename" to="newpath"
obsidian rename file="filename" name="newname"

# List files
obsidian files
obsidian files folder="folderpath"
obsidian files ext="md"
```

### Folder Operations

```bash
# List folders
obsidian folders
obsidian folders folder="parentfolder"

# Get folder info
obsidian folder path="folderpath"
obsidian folder path="folderpath" info=files
```

### Search

```bash
# Text search
obsidian search query="keyword"
obsidian search query="keyword" path="folder" limit=10
obsidian search query="keyword" case total

# Search with context
obsidian search:context query="keyword"

# Open search view
obsidian search:open query="keyword"
```

### Link Management

```bash
# Backlinks
obsidian backlinks file="filename"
obsidian backlinks file="filename" counts

# Outgoing links
obsidian links file="filename"

# Unresolved links
obsidian unresolved
obsidian unresolved counts verbose

# Orphan files
obsidian orphans

# Dead-end files (no outgoing links)
obsidian deadends
```

### Tags

```bash
# List all tags
obsidian tags
obsidian tags counts sort=count
obsidian tags format=json

# Get tag info
obsidian tag name="#tagname"
obsidian tag name="#tagname" verbose

# Tags in current file
obsidian tags active
obsidian tags file="filename"
```

### Properties

```bash
# List properties
obsidian properties
obsidian properties counts
obsidian properties active

# Read property
obsidian property:read name="propertyname" file="filename"

# Set property
obsidian property:set name="propertyname" value="value" type=text|list|number|checkbox|date|datetime

# Remove property
obsidian property:remove name="propertyname" file="filename"

# Aliases
obsidian aliases
obsidian aliases active
obsidian aliases file="filename" verbose
```

### Tasks

```bash
# List tasks
obsidian tasks
obsidian tasks todo           # Incomplete tasks
obsidian tasks done           # Completed tasks
obsidian tasks daily          # Tasks from daily note
obsidian tasks file="filename" verbose  # With file paths and line numbers
obsidian tasks total          # Return count

# Task operations
obsidian task file="filename" line=8           # View task
obsidian task ref="filename.md:8" toggle       # Toggle status
obsidian task file="filename" line=8 done      # Mark as done
obsidian task file="filename" line=8 todo      # Mark as todo
obsidian task file="filename" line=8 status=-  # Set custom status
```

### Daily Notes

```bash
# Open daily note
obsidian daily
obsidian daily paneType=tab

# Get path
obsidian daily:path

# Read content
obsidian daily:read

# Append content
obsidian daily:append content="- [ ] new task"
obsidian daily:append content="inline content" inline open

# Prepend content
obsidian daily:prepend content="## Heading" open
```

### Templates

```bash
# List templates
obsidian templates

# Read template
obsidian template:read name="templatename"
obsidian template:read name="templatename" resolve  # Resolve variables

# Insert template
obsidian template:insert name=templatename
```

### Plugin Management

```bash
# List plugins
obsidian plugins
obsidian plugins filter=community versions
obsidian plugins:enabled

# Plugin info
obsidian plugin id="pluginid"

# Enable/Disable
obsidian plugin:enable id="pluginid"
obsidian plugin:disable id="pluginid"

# Install/Uninstall
obsidian plugin:install id=pluginid
obsidian plugin:install id=pluginid enable
obsidian plugin:uninstall id=pluginid

# Reload plugin (for dev)
obsidian plugin:reload id="pluginid"

# Toggle restricted mode
obsidian plugins:restrict on
obsidian plugins:restrict off
```

### Theme Management

```bash
# List themes
obsidian themes
obsidian themes versions

# Current theme
obsidian theme

# Set theme
obsidian theme:set name="themename"

# Install/Uninstall
obsidian theme:install name=themename
obsidian theme:install name=themename enable
obsidian theme:uninstall name=themename

# CSS snippets
obsidian snippets
obsidian snippets:enabled
obsidian snippet:enable name="snippetname"
obsidian snippet:disable name="snippetname"
```

### Workspace

```bash
# Workspace tree
obsidian workspace
obsidian workspace ids

# Manage workspaces
obsidian workspaces
obsidian workspace:save name="name"
obsidian workspace:load name="name"
obsidian workspace:delete name="name"

# Tabs
obsidian tabs
obsidian tabs ids
obsidian tab:open group="1" file="file"
obsidian tab:open view="graph"

# Recent files
obsidian recents
```

### Outline

```bash
obsidian outline
obsidian outline file="filename" format=tree
obsidian outline path="file.md" format=md
```

### Sync

```bash
# Sync control
obsidian sync on
obsidian sync off
obsidian sync:status

# Sync history
obsidian sync:history file="filename"
obsidian sync:read file="filename" version=1
obsidian sync:restore file="filename" version=1

# Deleted files
obsidian sync:deleted
```

### Publish

```bash
obsidian publish:site
obsidian publish:list
obsidian publish:status
obsidian publish:add file="filename"
obsidian publish:add changed
obsidian publish:remove file="filename"
obsidian publish:open file="filename"
```

### File History

```bash
# Version diff
obsidian diff file="filename" from=1 to=2
obsidian diff file="filename" from=1

# Local history
obsidian history file="filename"
obsidian history:list
obsidian history:read file="filename" version=1
obsidian history:restore file="filename" version=1
obsidian history:open file="filename"
```

### Random Notes

```bash
obsidian random
obsidian random newtab
obsidian random folder=folder
obsidian random:read
obsidian random:read folder=folder
```

### Unique Notes

```bash
obsidian unique
obsidian unique name=note-name
obsidian unique content="initial content"
obsidian unique open
obsidian unique paneType=tab
```

### Word Count

```bash
obsidian wordcount
obsidian wordcount file="filename"
obsidian wordcount words
obsidian wordcount characters
```

### Base Files (Experimental)

```bash
obsidian bases
obsidian base:views file="filename"
obsidian base:create file="filename" view="view" name="name"
obsidian base:query file="filename" view="view" format=json
```

### Bookmarks

```bash
obsidian bookmarks
obsidian bookmarks total verbose
obsidian bookmarks format=json

obsidian bookmark file="file" title="title"
obsidian bookmark search="query"
obsidian bookmark url="https://..."
obsidian bookmark folder="folderpath"
```

### Command Palette

```bash
# List commands
obsidian commands
obsidian commands filter="prefix"

# Execute command
obsidian command id="commandid"

# Hotkeys
obsidian hotkeys
obsidian hotkey id="commandid"
```

### Vault Management

```bash
obsidian vault
obsidian vault info=name
obsidian vault info=files

obsidian vaults
obsidian vaults total verbose

# Switch vault (TUI only)
obsidian vault:open name="VaultName"
```

### Developer Tools

```bash
# DevTools
obsidian devtools
obsidian dev:debug on
obsidian dev:debug off

# CDP commands
obsidian dev:cdp method="CDP.method" params='{"key":"value"}'

# Error capture
obsidian dev:errors
obsidian dev:errors clear

# Screenshot
obsidian dev:screenshot path="screenshot.png"

# Console
obsidian dev:console
obsidian dev:console limit=100 level=error
obsidian dev:console clear

# CSS inspection
obsidian dev:css selector=".classname"
obsidian dev:css selector="#id" prop="color"

# DOM queries
obsidian dev:dom selector="CSS selector"
obsidian dev:dom selector="selector" attr="attrname"
obsidian dev:dom selector="selector" css="property"
obsidian dev:dom selector="selector" text
obsidian dev:dom selector="selector" all

# Mobile emulation
obsidian dev:mobile on
obsidian dev:mobile off

# JavaScript execution
obsidian eval code="app.vault.getFiles().length"
```

### Web Viewer

```bash
obsidian web url="https://example.com"
obsidian web url="https://..." newtab
```

### System Commands

```bash
obsidian help
obsidian version
obsidian reload
obsidian restart
```

---

## Parameter Syntax

### Basic Format

```bash
# Parameters
parameter=value

# Values with spaces
parameter="value with spaces"

# Multiline content
content="line1\n\nparagraph2"

# Newline and tab
# \n = newline
# \t = tab
```

### Flags (Boolean Switches)

```bash
obsidian create name="file" open overwrite
```

Common flags:
- `open` - Open after creating
- `overwrite` - Overwrite if exists
- `newtab` - Open in new tab
- `inline` - Without newline
- `total` - Return count
- `counts` - Include counts
- `verbose` - Detailed output
- `resolve` - Resolve template variables
- `enable` - Enable after install
- `done` - Done status
- `todo` - Todo status
- `case` - Case sensitive

### File Targeting

```bash
# By filename (fuzzy match)
file="filename"

# By full path
path="folder/filename.md"

# By reference (file:line)
ref="filename.md:8"
```

### Vault Targeting

```bash
# Current vault (default)
# Or specify:
vault="VaultName"
vault="VaultID"
```

---

## Usage Examples

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
# Create and open daily note, add tasks
obsidian daily
obsidian daily:append content="## Today's Tasks\n- [ ] Task 1\n- [ ] Task 2"

# Create meeting note
obsidian create name=Meeting-2025-01-15 template=Meeting open

# Quick note
obsidian create name="QuickNote-$(date +%s)" content="idea content"
```

### Task Management

```bash
# View all tasks from daily note
obsidian tasks daily verbose

# Toggle task status
obsidian task daily line=5 toggle

# List incomplete tasks
obsidian tasks todo

# Count tasks
obsidian tasks daily total
```

### Knowledge Management

```bash
# Search notes by keyword
obsidian search query="AI Agent" limit=20

# Find orphan notes
obsidian orphans

# Find unresolved links
obsidian unresolved verbose

# List all tags with counts
obsidian tags counts sort=count
```

### Plugin Development

```bash
# Reload plugin under development
obsidian plugin:reload id="my-plugin"

# View plugin info
obsidian plugin id="my-plugin"

# Screenshot for testing
obsidian dev:screenshot path="plugin-ui.png"

# View console errors
obsidian dev:errors

# Debug with JavaScript
obsidian eval code="app.plugins.getPlugin('my-plugin')"
```

### Theme Development

```bash
# Install and enable theme
obsidian theme:install name="Minimal" enable

# View enabled snippets
obsidian snippets:enabled

# Enable CSS snippet
obsidian snippet:enable name="custom.css"

# Inspect CSS
obsidian dev:css selector=".markdown-preview-view"
```

### Batch Operations

```bash
# List all Markdown files
obsidian files ext="md"

# Get all properties
obsidian properties counts

# Export all tags as JSON
obsidian tags format=json

# Get workspace tree
obsidian workspace ids
```

### Vault Management

```bash
# List all vaults
obsidian vaults verbose

# Get current vault info
obsidian vault info=files

# Switch vault (TUI)
obsidian vault:open name="My Vault"
```

---

## Output Formats

Most list commands support multiple output formats:

```bash
# JSON
obsidian tags format=json
obsidian bookmarks format=json

# TSV
obsidian tags format=tsv

# CSV
obsidian tags format=csv

# YAML (properties)
obsidian properties format=yaml

# Markdown
obsidian outline format=md

# Paths (base query)
obsidian base:query format=paths
```

---

## Clipboard Operations

```bash
# Copy output to clipboard
obsidian read --copy
obsidian search query="TODO" --copy
```

---

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
