# Tasks and Properties Reference

Obsidian CLI 任务、标签和属性管理命令参考。

---

## Tasks

### List Tasks

```bash
# List all tasks
obsidian tasks

# Incomplete tasks only
obsidian tasks todo

# Completed tasks
obsidian tasks done

# Tasks from daily note
obsidian tasks daily

# Tasks with file paths and line numbers
obsidian tasks file="filename" verbose

# Return count only
obsidian tasks total
```

### Task Operations

```bash
# View task at specific line
obsidian task file="filename" line=8

# Toggle task status
obsidian task ref="filename.md:8" toggle

# Mark as done
obsidian task file="filename" line=8 done

# Mark as todo
obsidian task file="filename" line=8 todo

# Set custom status
obsidian task file="filename" line=8 status=-
```

---

## Tags

### List Tags

```bash
# List all tags
obsidian tags

# With counts, sorted by count
obsidian tags counts sort=count

# Export as JSON
obsidian tags format=json

# Export as TSV
obsidian tags format=tsv

# Export as CSV
obsidian tags format=csv
```

### Tag Info

```bash
# Get info about specific tag
obsidian tag name="#tagname"

# Verbose output
obsidian tag name="#tagname" verbose
```

### Tags in File

```bash
# Tags in current file
obsidian tags active

# Tags in specific file
obsidian tags file="filename"
```

---

## Properties

### List Properties

```bash
# List all properties
obsidian properties

# With counts
obsidian properties counts

# Properties in current file
obsidian properties active

# Export as YAML
obsidian properties format=yaml
```

### Read Property

```bash
obsidian property:read name="propertyname" file="filename"
```

### Set Property

```bash
obsidian property:set name="propertyname" value="value" type=text|list|number|checkbox|date|datetime
```

### Remove Property

```bash
obsidian property:remove name="propertyname" file="filename"
```

---

## Aliases

### List Aliases

```bash
# List all aliases
obsidian aliases

# Aliases in current file
obsidian aliases active

# Aliases in specific file
obsidian aliases file="filename" verbose
```

---

## Daily Notes

Daily notes 需要通过 Daily Notes 核心插件启用。命令使用 `command` 执行插件命令：

```bash
# Open daily note (requires Daily Notes core plugin)
obsidian command id=daily-notes:daily-notes

# Open daily note in new tab
obsidian command id=daily-notes:daily-notes paneType=tab

# Get daily note path (returns file path)
obsidian eval code="app.vault.getConfig('dailyNotesSettings').folder"
```

**Note**: Daily notes 相关文件操作使用标准文件命令：

```bash
# Read daily note content (replace YYYY-MM-DD.md with actual file)
obsidian read path="2026-03-04.md"

# Append to daily note
obsidian append path="2026-03-04.md" content="- [ ] new task"
```

---

## Templates

```bash
# List templates
obsidian templates

# Read template
obsidian template:read name="templatename"

# Read template with resolved variables
obsidian template:read name="templatename" resolve

# Insert template
obsidian template:insert name=templatename
```

---

## Usage Examples

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

### Tag Management

```bash
# List all tags with counts
obsidian tags counts sort=count

# Export tags as JSON
obsidian tags format=json
```

### Property Management

```bash
# Set a text property
obsidian property:set name="status" value="in-progress" type=text

# Set a list property (tags)
obsidian property:set name="tags" value="[\"work\",\"urgent\"]" type=list

# Set a checkbox property
obsidian property:set name="completed" value="false" type=checkbox

# Set a date property
obsidian property:set name="due" value="2024-02-01" type=date
```

---

## Property Types

| Type | Example |
|------|---------|
| `text` | `value="My Title"` |
| `number` | `value="4.5"` |
| `checkbox` | `value="true"` or `value="false"` |
| `date` | `value="2024-01-15"` |
| `datetime` | `value="2024-01-15T14:30:00"` |
| `list` | `value="[\"a\",\"b\"]"` |
