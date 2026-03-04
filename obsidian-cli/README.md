# Obsidian CLI Skill

通过 Obsidian 官方 CLI (v1.12+) 自动化操作 Obsidian 笔记应用。此 Skill 使 AI Agent 能够通过命令行控制 Obsidian，实现脚本化、自动化和与外部工具的集成。

## 前置条件

- **Obsidian 1.12+** 安装版（必需）
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

1. 确保已安装 Obsidian 1.12+
2. 在 Obsidian 中启用 CLI：设置 → 通用 → 命令行界面
3. 克隆或下载此仓库的 `obsidian-cli` 文件夹到本地
4. 将 `SKILL.md` 和 `references/` 目录复制到你的 Agent skills 目录（如 `~/.claude/skills/obsidian-cli/`）

## Skill 核心功能

### 执行流程

1. **解析用户请求** → 确定操作类型（read/create/search 等）
2. **构建 CLI 命令** → 根据命令参考选择对应语法
3. **执行命令** → 使用 `Bash` 工具执行
4. **返回结果** → 将命令输出返回给用户

### 快速命令映射

| 用户请求 | 命令示例 |
|---------|---------|
| 读取笔记 | `obsidian read path="file.md"` |
| 创建笔记 | `obsidian create path="..." content="..."` |
| 追加内容 | `obsidian append path="..." content="..."` |
| 删除笔记 | `obsidian delete path="..."` |
| 搜索笔记 | `obsidian search query="keyword"` |
| 列出文件 | `obsidian files folder="..."` |
| 读取属性 | `obsidian property:read name="..." file="..."` |
| 设置属性 | `obsidian property:set name="..." value="..."` |
| 列出任务 | `obsidian tasks todo` |
| 切换任务 | `obsidian task ref="..." toggle` |
| 日常任务 | `obsidian tasks daily` |
| 安装插件 | `obsidian plugin:install id=...` |

### 重要说明

- **编辑文件**: CLI 没有直接的 "edit" 命令。使用：`read` → 处理文本 → `create --overwrite`
- **参数语法**: `parameter=value`，带空格的值需要引号：`"value with spaces"`
- **文件定位**: `file="filename"` 模糊匹配，`path="folder/file.md"` 完整路径

### 触发条件

当用户使用中英文表达以下意图时，Skill 会自动触发：

| 场景 | 中文表达示例 | English Examples |
|------|------------|-----------------|
| **Vault + 操作** | "vault 中的文章"、"笔记库里的内容" | "my vault", "notes in vault" |
| **读取/查看** | "读取 vault"、"看看那篇笔记" | "read my note", "show me my notes" |
| **修改/优化** | "修改 vault 内容"、"帮我改改" | "edit this note", "update my note" |
| **创建/新增** | "创建新笔记"、"新增一篇 md" | "create a new note", "new note" |
| **删除/归档** | "删除这篇笔记"、"归档旧文章" | "delete this note", "archive old files" |
| **整理/管理** | "整理我的 vault"、"管理笔记库" | "organize my notes", "manage my vault" |
| **搜索/查找** | "找找关于 AI 的笔记"、"搜索 vault" | "find notes about XX", "search my vault" |
| **任务/属性** | "查看待办任务"、"设置标签" | "my tasks", "set tags" |
| **插件/主题** | "装个插件"、"换个主题" | "install plugin", "enable theme" |

## 使用示例

### 基本操作

```bash
# 读取笔记
obsidian read path="Notes/MyNote.md"

# 创建新笔记
obsidian create path="Notes/NewNote.md" content="# 标题\n\n内容在这里"

# 追加内容
obsidian append path="Notes/MyNote.md" content="\n## 新增段落"

# 搜索笔记
obsidian search query="AI Agent" limit=20

# 列出未完成任务
obsidian tasks todo

# 设置属性
obsidian property:set name="status" value="draft" file="Note.md"
```

### 编辑笔记内容

```bash
# 1. 读取文件内容
obsidian read path="Writing-MP/article.md"

# 2. 外部处理文本（删除/替换内容）

# 3. 写回修改后的内容
obsidian create path="Writing-MP/article.md" content="modified content" overwrite
```

### 任务管理

```bash
# 列出所有未完成任务
obsidian tasks todo

# 查看日常笔记中的任务
obsidian tasks daily verbose

# 切换任务状态
obsidian task daily line=5 toggle

# 标记任务为完成
obsidian task file="Note.md" line=10 done
```

### 知识图谱维护

```bash
# 查找孤立笔记（无入向链接）
obsidian orphans

# 查找死胡同笔记（无出向链接）
obsidian deadends

# 列出所有标签，按频率排序
obsidian tags counts sort=count

# 列出生成的反向链接
obsidian backlinks path="Notes/MyNote.md"
```

### Daily Note 工作流

```bash
# 打开日常笔记（需要 Daily Notes 核心插件）
obsidian command id=daily-notes:daily-notes

# 追加任务到日常笔记
obsidian append path="2026-03-05.md" content="\n## Today's Tasks\n- [ ] Task 1\n- [ ] Task 2"
```

### 插件开发

```bash
# 重新加载开发中的插件
obsidian plugin:reload id="my-plugin"

# 截图用于测试
obsidian dev:screenshot path="plugin-ui.png"

# 执行 JavaScript 调试
obsidian eval code="app.plugins.getPlugin('my-plugin')"
```

## 命令参考

完整命令参考请参阅 [references/](references/) 目录：

- [`references/file-operations.md`](references/file-operations.md) - 文件操作命令
- [`references/search-links.md`](references/search-links.md) - 搜索和链接管理
- [`references/tasks-properties.md`](references/tasks-properties.md) - 任务和属性管理
- [`references/plugins-themes.md`](references/plugins-properties.md) - 插件和主题管理
- [`references/advanced-commands.md`](references/advanced-commands.md) - 高级命令

## 输出格式

大多数列表命令支持多种输出格式：

```bash
# JSON
obsidian tags format=json
obsidian bookmarks format=json

# TSV
obsidian tags format=tsv

# YAML (属性)
obsidian properties format=yaml
```

## 故障排查

### "command not found: obsidian"

**macOS:** 将 Obsidian 添加到 PATH：
```bash
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
```

添加到 `~/.zprofile` 或 `~/.bash_profile` 永久生效：
```bash
echo 'export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"' >> ~/.zprofile
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
4. 验证 Obsidian 版本是 1.12+

### macOS 特别说明

确保使用的是 Obsidian 1.12+ 内置的 CLI 功能，需要在 **设置 → 通用 → 命令行界面** 中启用。

## 资源链接

- [Obsidian CLI 官方文档](https://help.obsidian.md/cli)
- [Obsidian 下载](https://obsidian.md/download)
- [Obsidian 论坛](https://forum.obsidian.md/)
