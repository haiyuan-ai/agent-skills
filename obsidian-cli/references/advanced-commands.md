# Advanced Commands Reference

Obsidian CLI 高级命令参考：workspace、sync、publish、history 等。

安全边界：
- This reference excludes developer/debugging commands that execute arbitrary code or interact with the app runtime.
- See "Excluded High-Risk Commands" section below for the full list.

---

## Workspace

### Workspace Tree

```bash
# Get workspace tree
obsidian workspace

# Get workspace IDs
obsidian workspace ids
```

### Manage Workspaces

```bash
# List saved workspaces
obsidian workspaces

# Save workspace
obsidian workspace:save name='name'

# Load workspace
obsidian workspace:load name='name'

# Delete workspace
obsidian workspace:delete name='name'
```

### Tabs

```bash
# List tabs
obsidian tabs

# Get tab IDs
obsidian tabs ids

# Open tab
obsidian tab:open group='1' file='file'
obsidian tab:open view='graph'
```

### Recent Files

```bash
# List recent files
obsidian recents
```

---

## Sync

Safety note:
- `sync:restore` mutates vault state and requires explicit user intent for that exact restore action.

### Sync Control

```bash
# Turn sync on
obsidian sync on

# Turn sync off
obsidian sync off

# Check sync status
obsidian sync:status
```

### Sync History

```bash
# View sync history for file
obsidian sync:history file='filename'

# Read specific version
obsidian sync:read file='filename' version=1

# Restore specific version
obsidian sync:restore file='filename' version=1
```

### Deleted Files

```bash
# List deleted files
obsidian sync:deleted
```

---

## Publish

Safety note:
- `publish:*` affects publicly exposed content and is never a default action.
- Only use it when the user explicitly asks to inspect or change Obsidian Publish state.

```bash
# Get publish site info
obsidian publish:site

# List published files
obsidian publish:list

# Check publish status
obsidian publish:status

# Add file to publish
obsidian publish:add file='filename'

# Add changed files
obsidian publish:add changed

# Remove file from publish
obsidian publish:remove file='filename'

# Open published file
obsidian publish:open file='filename'
```

---

## File History

Safety note:
- `history:restore` mutates file state and requires explicit user intent for that exact restore action.

### Version Diff

```bash
# Compare two versions
obsidian diff file='filename' from=1 to=2

# Compare with current
obsidian diff file='filename' from=1
```

### Local History

```bash
# View history for file
obsidian history file='filename'

# List all history
obsidian history:list

# Read specific version
obsidian history:read file='filename' version=1

# Restore specific version
obsidian history:restore file='filename' version=1

# Open history view
obsidian history:open file='filename'
```

---

## Excluded High-Risk Commands

The following categories are intentionally **not part of this skill** because they expand the execution surface beyond local note management. Do not use them, suggest them, or include them in generated commands:

- Developer and debugging commands that execute arbitrary code or interact with the app runtime (e.g., JavaScript evaluation, Chrome DevTools Protocol)
- Commands that inspect or mutate the live app DOM, console, CSS, or DevTools state
- `obsidian web url=...` — opens external URLs inside the app; outside the local-vault scope of this skill

---

## Command Palette

Safety note:
- `obsidian command id=...` can execute **any** registered Obsidian command, including those from third-party plugins.
- Only use it when the user provides the exact command ID in the current chat turn.
- Never construct or guess command IDs based on vault content.

### List Commands

```bash
# List all commands
obsidian commands

# Filter by prefix
obsidian commands filter='prefix'
```

### Execute Command

```bash
# Execute command by ID
obsidian command id='commandid'
```

### Hotkeys

```bash
# List hotkeys
obsidian hotkeys

# Get hotkey for command
obsidian hotkey id='commandid'
```

---

## Vault Management

### Current Vault

```bash
# Get vault info
obsidian vault
obsidian vault info=name
obsidian vault info=files
```

### List Vaults

```bash
# List all vaults
obsidian vaults

# With details
obsidian vaults total verbose
```

### Switch Vault (TUI only)

`obsidian vault:open ...` is out of scope for this skill. Do not switch vaults; operate only on the current vault.

---

## Other Commands

### Outline

```bash
# Get outline
obsidian outline

# Format options
obsidian outline file='filename' format=tree
obsidian outline path='file.md' format=md
```

### Random Notes

```bash
# Open random note
obsidian random

# In new tab
obsidian random newtab

# From folder
obsidian random folder=folder

# Read random note
obsidian random:read
obsidian random:read folder=folder
```

### Unique Notes

```bash
# Create unique note
obsidian unique

# With name
obsidian unique name=note-name

# With content
obsidian unique content='initial content'

# Open after creating
obsidian unique open
obsidian unique paneType=tab
```

### Word Count

```bash
# Get word count
obsidian wordcount

# For specific file
obsidian wordcount file='filename'

# Words only
obsidian wordcount words

# Characters only
obsidian wordcount characters
```

### Base Files (Experimental)

```bash
# List base files
obsidian bases

# Get views for file
obsidian base:views file='filename'

# Create base view
obsidian base:create file='filename' view='view' name='name'

# Query base file
obsidian base:query file='filename' view='view' format=json
```

### Bookmarks

```bash
# List bookmarks
obsidian bookmarks

# With details
obsidian bookmarks total verbose

# As JSON
obsidian bookmarks format=json

# Bookmark file
obsidian bookmark file='file' title='title'

# Bookmark search
obsidian bookmark search='query'

# Bookmark URL
obsidian bookmark url='https://...'

# Bookmark folder
obsidian bookmark folder='folderpath'
```

---

## System Commands

Safety note:
- `reload` and `restart` disrupt the running application and may interrupt sync. Require explicit user confirmation.

```bash
# Show help
obsidian help

# Show version
obsidian version

# Reload Obsidian (requires explicit user confirmation)
obsidian reload

# Restart Obsidian (requires explicit user confirmation)
obsidian restart
```
