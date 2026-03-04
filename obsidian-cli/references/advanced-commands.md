# Advanced Commands Reference

Obsidian CLI 高级命令参考：workspace、sync、publish、dev tools 等。

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
obsidian workspace:save name="name"

# Load workspace
obsidian workspace:load name="name"

# Delete workspace
obsidian workspace:delete name="name"
```

### Tabs

```bash
# List tabs
obsidian tabs

# Get tab IDs
obsidian tabs ids

# Open tab
obsidian tab:open group="1" file="file"
obsidian tab:open view="graph"
```

### Recent Files

```bash
# List recent files
obsidian recents
```

---

## Sync

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
obsidian sync:history file="filename"

# Read specific version
obsidian sync:read file="filename" version=1

# Restore specific version
obsidian sync:restore file="filename" version=1
```

### Deleted Files

```bash
# List deleted files
obsidian sync:deleted
```

---

## Publish

```bash
# Get publish site info
obsidian publish:site

# List published files
obsidian publish:list

# Check publish status
obsidian publish:status

# Add file to publish
obsidian publish:add file="filename"

# Add changed files
obsidian publish:add changed

# Remove file from publish
obsidian publish:remove file="filename"

# Open published file
obsidian publish:open file="filename"
```

---

## File History

### Version Diff

```bash
# Compare two versions
obsidian diff file="filename" from=1 to=2

# Compare with current
obsidian diff file="filename" from=1
```

### Local History

```bash
# View history for file
obsidian history file="filename"

# List all history
obsidian history:list

# Read specific version
obsidian history:read file="filename" version=1

# Restore specific version
obsidian history:restore file="filename" version=1

# Open history view
obsidian history:open file="filename"
```

---

## Developer Tools

### DevTools

```bash
# Open DevTools
obsidian devtools

# Toggle debug mode
obsidian dev:debug on
obsidian dev:debug off
```

### CDP Commands

```bash
# Execute CDP command
obsidian dev:cdp method="CDP.method" params='{"key":"value"}'
```

### Error Capture

```bash
# View errors
obsidian dev:errors

# Clear errors
obsidian dev:errors clear
```

### Screenshot

```bash
# Take screenshot
obsidian dev:screenshot path="screenshot.png"
```

### Console

```bash
# View console
obsidian dev:console

# With filters
obsidian dev:console limit=100 level=error

# Clear console
obsidian dev:console clear
```

### CSS Inspection

```bash
# Query CSS selector
obsidian dev:css selector=".classname"

# Get specific property
obsidian dev:css selector="#id" prop="color"
```

### DOM Queries

```bash
# Query DOM
obsidian dev:dom selector="CSS selector"

# Get attribute
obsidian dev:dom selector="selector" attr="attrname"

# Get CSS property
obsidian dev:dom selector="selector" css="property"

# Get text content
obsidian dev:dom selector="selector" text

# Get all matches
obsidian dev:dom selector="selector" all
```

### Mobile Emulation

```bash
# Toggle mobile mode
obsidian dev:mobile on
obsidian dev:mobile off
```

### JavaScript Execution

```bash
# Execute JavaScript
obsidian eval code="app.vault.getFiles().length"
```

---

## Web Viewer

```bash
# Open web URL
obsidian web url="https://example.com"

# Open in new tab
obsidian web url="https://..." newtab
```

---

## Command Palette

### List Commands

```bash
# List all commands
obsidian commands

# Filter by prefix
obsidian commands filter="prefix"
```

### Execute Command

```bash
# Execute command by ID
obsidian command id="commandid"
```

### Hotkeys

```bash
# List hotkeys
obsidian hotkeys

# Get hotkey for command
obsidian hotkey id="commandid"
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

```bash
obsidian vault:open name="VaultName"
```

---

## Other Commands

### Outline

```bash
# Get outline
obsidian outline

# Format options
obsidian outline file="filename" format=tree
obsidian outline path="file.md" format=md
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
obsidian unique content="initial content"

# Open after creating
obsidian unique open
obsidian unique paneType=tab
```

### Word Count

```bash
# Get word count
obsidian wordcount

# For specific file
obsidian wordcount file="filename"

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
obsidian base:views file="filename"

# Create base view
obsidian base:create file="filename" view="view" name="name"

# Query base file
obsidian base:query file="filename" view="view" format=json
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
obsidian bookmark file="file" title="title"

# Bookmark search
obsidian bookmark search="query"

# Bookmark URL
obsidian bookmark url="https://..."

# Bookmark folder
obsidian bookmark folder="folderpath"
```

---

## System Commands

```bash
# Show help
obsidian help

# Show version
obsidian version

# Reload Obsidian
obsidian reload

# Restart Obsidian
obsidian restart
```
