# Obsidian CLI Skill

通过 Obsidian 官方 CLI (v1.12+) 自动化操作 Obsidian 笔记应用。此 Skill 使 AI Agent 能够通过命令行控制 Obsidian，实现脚本化、自动化和与外部工具的集成。

## 前置条件

- **Obsidian 1.12.4+** 安装版（必需）
- **CLI 已启用**：在 Obsidian 设置 → 通用 → 命令行界面 中启用
- **Obsidian 应用必须运行中**：执行 CLI 命令时 Obsidian 需要处于运行状态

## 安装

### 一键安装（推荐）

```bash
# 方式一：安装单个 Skill
npx skills add haiyuan-ai/agent-skills/obsidian-cli

# 方式二：从仓库安装指定 Skill
npx skills add haiyuan-ai/agent-skills --skill obsidian-cli
```

安装完成后，Skill 会被复制到 `~/.claude/skills/obsidian-cli/` 或相应 Agent 的 skills 目录，Claude Code、OpenCode、Gemini CLI 等支持 Skill 协议的 Coding Agent 即可自动加载使用。

### 手动安装

1. 确保已安装 Obsidian 1.12.4+
2. 在 Obsidian 中启用 CLI：设置 → 通用 → 命令行界面
3. 克隆或下载此仓库的 `obsidian-cli` 文件夹到本地
4. 将 `SKILL.md` 复制到你的 Agent skills 目录（如 `~/.claude/skills/obsidian-cli/`）

## Skill 核心功能

### 执行指令（Execution Instructions）

Skill 内置执行指引，告诉 AI 如何正确调用 CLI 命令：

- **正确做法**：使用 `Bash` 工具执行 `obsidian read path="..."`
- **错误做法**：直接用 `Read` 工具读取文件（绕过了 CLI）

### 执行流程

1. **解析用户请求** → 确定操作类型（read/create/search 等）
2. **构建 CLI 命令** → 根据命令参考选择对应语法
3. **执行命令** → 使用 `Bash` 工具执行
4. **返回结果** → 将命令输出返回给用户

### 快速命令映射（Quick Command Mapping）

Skill 提供 14 个常用命令的快速参考表，AI 可以直接找到正确的命令语法：

| 用户请求 | 命令示例 |
|---------|---------|
| 读取笔记 | `obsidian read path="file.md"` |
| 创建笔记 | `obsidian create path="..." content="..."` |
| 搜索笔记 | `obsidian search query="keyword"` |
| 列出任务 | `obsidian tasks todo` |
| 切换任务 | `obsidian task ref="file.md:5" toggle` |

### 触发条件

当用户使用中英文表达以下意图时，Skill 会自动触发：

- **中文**："读取 vault 中的文章"、"修改笔记内容"、"搜索关键词"、"创建新笔记"
- **English**: "read my note", "edit this file", "search notes", "create a new note"

## 使用示例

### 基本操作

```bash
# 读取笔记
obsidian read path="Notes/MyNote.md"

# 创建新笔记
obsidian create name="新笔记" content="# 标题\n\n内容在这里"

# 追加到每日笔记
obsidian daily:append content="- [ ] 新任务"

# 搜索笔记
obsidian search query="AI Agent" limit=20

# 列出任务
obsidian tasks todo

# 管理属性
obsidian property:set name="status" value="draft" file="Note.md"
```

### 自动化场景

#### AI 辅助写作流程
```bash
# 读取 Inbox 素材
obsidian read path="InBox/material.md"

# 创建草稿
obsidian create path="Drafts/article.md" content="..."

# 设置发布状态
obsidian property:set name="status" value="draft"
```

#### 任务管理
```bash
# 列出所有未完成任务
obsidian tasks todo verbose

# 切换任务状态
obsidian task ref="Daily/2026-02-28:5" toggle

# 标记任务为完成
obsidian task file="Note.md" line=10 done
```

#### 知识图谱维护
```bash
# 查找孤立笔记
obsidian orphans total

# 查找死胡同笔记
obsidian deadends total

# 生成链接报告
obsidian links format=json > links-report.json
```

## 命令参考

### 文件操作
- `obsidian read` - 读取文件内容
- `obsidian create` - 创建新文件
- `obsidian append` - 追加内容到文件
- `obsidian prepend` - 在文件开头前置内容
- `obsidian delete` - 删除文件
- `obsidian move` - 移动或重命名文件
- `obsidian files` - 列出仓库中的文件

### 内容管理
- `obsidian search` - 按文本搜索笔记
- `obsidian tasks` - 列出和管理任务
- `obsidian tags` - 列出和管理标签
- `obsidian properties` - 管理笔记属性
- `obsidian daily` - 每日笔记操作

### 链接管理
- `obsidian backlinks` - 列出反向链接
- `obsidian links` - 列出出向链接
- `obsidian orphans` - 列出无入向链接的文件
- `obsidian deadends` - 列出无出向链接的文件

### 插件与主题
- `obsidian plugins` - 列出已安装插件
- `obsidian plugin:install` - 安装社区插件
- `obsidian plugin:enable/disable` - 启用/禁用插件
- `obsidian theme:set` - 设置当前主题
- `obsidian snippets` - 管理 CSS 片段

### 开发者工具
- `obsidian devtools` - 切换开发者工具
- `obsidian dev:screenshot` - 截图
- `obsidian dev:css` - 检查 CSS
- `obsidian dev:dom` - 查询 DOM 元素
- `obsidian eval` - 执行 JavaScript

## 参数语法

```bash
# 基本格式
obsidian [命令] [参数=值] [标志]

# 参数
parameter=value          # 简单值（不需要引号）
parameter="带空格的值"    # 含空格的值需要引号

# 标志（布尔开关，不带 --）
obsidian create name=Note open overwrite

# 全局标志（例外，需要 --）
obsidian read --copy     # 复制输出到剪贴板
```

## 文件定位

```bash
# 通过文件名（模糊匹配，类似 wikilinks）
file=Recipe

# 通过完整路径（从仓库根目录）
path=Templates/Recipe.md

# 通过引用（文件：行号）
ref="Daily/2026-02-28.md:5"
```

## 输出格式

大多数列表命令支持多种输出格式：

```bash
obsidian tags format=json
obsidian tags format=tsv
obsidian tags format=csv
obsidian properties format=yaml
obsidian outline format=md
```

## 故障排查

### "command not found: obsidian"

**macOS:** 将 Obsidian 添加到 PATH：
```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

**Linux:** 创建符号链接：
```bash
sudo ln -s /path/to/obsidian /usr/local/bin/obsidian
```

**Windows:** 运行 `Obsidian.com` 终端重定向器（随 1.12.4+ 安装器提供）

### CLI 不工作

1. 确保 Obsidian 应用正在运行
2. 检查 CLI 是否在 设置 → 通用 中启用
3. CLI 注册后重启终端
4. 验证 Obsidian 版本是 1.12.4+

### macOS 特别说明

确保使用的是 Obsidian 1.12.4+ 内置的 CLI 功能，需要在 **设置 → 通用 → 命令行界面** 中启用。

如果 PATH 配置后仍不工作，添加到 `~/.zprofile`：
```bash
echo 'export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"' >> ~/.zprofile
```

## 资源链接

- [Obsidian CLI 官方文档](https://help.obsidian.md/cli)
- [Obsidian 下载](https://obsidian.md/download)
- [Obsidian 论坛](https://forum.obsidian.md/)
