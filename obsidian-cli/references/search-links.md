# Search and Links Reference

Obsidian CLI 搜索和链接管理命令参考。

---

## Text Search

```bash
# Basic search
obsidian search query="keyword"

# Search with path limit
obsidian search query="keyword" path="folder" limit=10

# Case sensitive search
obsidian search query="keyword" case

# Return count only
obsidian search query="keyword" total
```

### Search with Context

```bash
# Search with surrounding context
obsidian search:context query="keyword"
```

### Open Search View

```bash
# Open search view in Obsidian
obsidian search:open query="keyword"
```

---

## Backlinks (反向链接)

```bash
# Get backlinks for a file
obsidian backlinks file="filename"

# Get backlink counts
obsidian backlinks file="filename" counts
```

---

## Outgoing Links (出向链接)

```bash
# Get outgoing links from a file
obsidian links file="filename"
```

---

## Unresolved Links (未解析链接)

```bash
# List unresolved links
obsidian unresolved

# With counts
obsidian unresolved counts

# Verbose output
obsidian unresolved counts verbose
```

---

## Orphan Files (孤立笔记)

```bash
# Find files with no links
obsidian orphans
```

---

## Dead-end Files (死胡同笔记)

```bash
# Find files with no outgoing links
obsidian deadends
```

---

## Usage Examples

### Search notes by keyword

```bash
obsidian search query="AI Agent" limit=20
```

### Find orphan notes

```bash
obsidian orphans
```

### Find unresolved links

```bash
obsidian unresolved verbose
```

### Check backlinks

```bash
obsidian backlinks file="My Note" counts
```
