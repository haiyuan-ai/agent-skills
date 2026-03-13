# Plugins and Themes Reference

Obsidian CLI 插件和主题状态参考。

安全边界：
- This skill is read-only for plugins, themes, and snippets.
- Do not install, uninstall, enable, disable, reload, download, or switch plugins, themes, or snippets through the agent.
- If the user wants plugin or theme changes, ask them to perform the change manually in Obsidian.

---

## Plugin Management

### List Plugins

```bash
# List all plugins
obsidian plugins

# Filter by community plugins
obsidian plugins filter=community

# Show versions
obsidian plugins versions

# List enabled plugins
obsidian plugins:enabled
```

### Plugin Info

```bash
# Get plugin info by ID
obsidian plugin id="pluginid"
```

### Mutating Commands Are Out of Scope

Do not use:

```bash
obsidian plugin:enable id="pluginid"
obsidian plugin:disable id="pluginid"
obsidian plugin:reload id="pluginid"
obsidian plugins:restrict on
obsidian plugins:restrict off
```

---

## Theme Management

### List Themes

```bash
# List all themes
obsidian themes

# Show versions
obsidian themes versions
```

### Current Theme

```bash
# Get current theme
obsidian theme
```

### CSS Snippets

```bash
# List CSS snippets
obsidian snippets

# List enabled snippets
obsidian snippets:enabled

# Do not mutate snippet state with this skill
```

---

## Usage Examples

### Inspect Plugin State

```bash
obsidian plugins:enabled
obsidian plugin id="my-plugin"
```

### Inspect Theme State

```bash
obsidian theme
obsidian snippets:enabled
```

---

## Common Plugin IDs

| Plugin Name | Plugin ID |
|-------------|-----------|
| Obsidian Git | `obsidian-git` |
| Dataview | `obsidian-dataview` |
| Templater | `templater-obsidian` |
| Calendar | `calendar` |
| Tasks | `obsidian-tasks-plugin` |
| QuickAdd | `quickadd` |
| Various Highlights | `obsidian-various-highlights` |
| Style Settings | `obsidian-style-settings` |
| Commander | `obsidian-commander` |
| Projects | `obsidian-projects` |

---

## Common Theme Names

| Theme Name |
|------------|
| Default |
| Minimal |
| Things |
| ITS Theme |
| Blue Topaz |
| Atomus |
| LYT Mode |
| Ebullientworks |

---

## Troubleshooting

### Plugin Not Found

Ensure you're using the correct plugin ID (not display name). Plugin IDs are usually in kebab-case:
- `obsidian-git` (not "Obsidian Git")
- `templater-obsidian` (not "Templater")

### Theme Not Applying

1. Check if theme is installed: `obsidian themes`
2. Check current theme: `obsidian theme`
3. Ask the user to change it manually in Obsidian

### Installing New Plugins or Themes

Installation is intentionally excluded from this skill because it downloads third-party code. Ask the user to perform installation manually inside Obsidian and then use this skill only for inspection or post-install configuration.
