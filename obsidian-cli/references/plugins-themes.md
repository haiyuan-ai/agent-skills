# Plugins and Themes Reference

Obsidian CLI 插件和主题管理命令参考。

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

### Enable/Disable Plugins

```bash
# Enable plugin
obsidian plugin:enable id="pluginid"

# Disable plugin
obsidian plugin:disable id="pluginid"
```

### Install/Uninstall Plugins

```bash
# Install plugin
obsidian plugin:install id=pluginid

# Install and enable
obsidian plugin:install id=pluginid enable

# Uninstall plugin
obsidian plugin:uninstall id=pluginid
```

### Reload Plugin (Development)

```bash
# Reload plugin under development
obsidian plugin:reload id="pluginid"
```

### Toggle Restricted Mode

```bash
# Enable restricted mode
obsidian plugins:restrict on

# Disable restricted mode
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

### Set Theme

```bash
# Set active theme
obsidian theme:set name="themename"
```

### Install/Uninstall Themes

```bash
# Install theme
obsidian theme:install name=themename

# Install and enable
obsidian theme:install name=themename enable

# Uninstall theme
obsidian theme:uninstall name=themename
```

### CSS Snippets

```bash
# List CSS snippets
obsidian snippets

# List enabled snippets
obsidian snippets:enabled

# Enable snippet
obsidian snippet:enable name="snippetname"

# Disable snippet
obsidian snippet:disable name="snippetname"
```

---

## Usage Examples

### Plugin Development Workflow

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
2. Enable the theme: `obsidian theme:set name="ThemeName"`
3. Reload Obsidian if needed: `obsidian reload`
