# File Operations Reference

Obsidian CLI 文件操作完整命令参考。

---

## Create File

```bash
# 创建文件
obsidian create name=filename content="content" template=templatename open overwrite

# 使用完整路径
obsidian create path="folder/filename.md" content="content" overwrite
```

### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Filename only | `name=Meeting-Notes` |
| `path` | Full path from vault root | `path="Work/Meeting-Notes.md"` |
| `content` | File content (use \n for newlines) | `content="Line 1\n\nLine 2"` |
| `template` | Template name to apply | `template=Meeting` |
| `open` | Open note after creating | `open` |
| `overwrite` | Overwrite if exists | `overwrite` |

---

## Read File

```bash
# Read by filename (fuzzy match)
obsidian read file="filename"

# Read by full path
obsidian read path="folder/filename.md"

# Copy output to clipboard
obsidian read path="file.md" --copy
```

---

## Append Content

```bash
# Append to end of file
obsidian append file="filename" content="content to append"

# Append without newline
obsidian append file="filename" content="inline content" inline

# Append and open
obsidian append file="filename" content="new line" inline open
```

---

## Prepend Content (after frontmatter)

```bash
# Prepend to beginning of file
obsidian prepend file="filename" content="content to prepend"

# Prepend and open
obsidian prepend file="filename" content="## Heading" open
```

---

## Delete File

```bash
# Delete file (moves to system trash)
obsidian delete file="filename"

# Permanent delete (bypass trash)
obsidian delete file="filename" permanent
```

---

## Move/Rename File

```bash
# Move file to new location
obsidian move file="filename" to="newpath"

# Rename file
obsidian rename file="filename" name="newname"
```

---

## List Files

```bash
# List all files
obsidian files

# List files in folder
obsidian files folder="folderpath"

# List files by extension
obsidian files ext="md"
obsidian files ext="pdf"
```

---

## Folder Operations

```bash
# List all folders
obsidian folders

# List subfolders
obsidian folders folder="parentfolder"

# Get folder info
obsidian folder path="folderpath"
obsidian folder path="folderpath" info=files
```

---

## Editing Workflow

CLI has no direct "edit" command. Use this workflow:

```bash
# 1. Read file content
obsidian read path="Writing-MP/article.md"

# 2. Process text externally (delete/replace content)

# 3. Write modified content back
obsidian create path="Writing-MP/article.md" content="modified content" overwrite
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
