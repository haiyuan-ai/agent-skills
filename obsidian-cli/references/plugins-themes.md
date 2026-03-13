# Plugins and Themes Reference

Obsidian CLI 插件和主题状态参考。

安全边界：
- This skill only allows inspection of already installed plugins/themes and enable or disable actions explicitly requested by the user.
- Do not install, uninstall, or download plugins, themes, or snippets through the agent.

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
```

### Theme Development

```bash
# View enabled snippets
obsidian snippets:enabled

# Enable CSS snippet
obsidian snippet:enable name="custom.css"
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

### Installing New Plugins or Themes

Installation is intentionally excluded from this skill because it downloads third-party code. Ask the user to perform installation manually inside Obsidian and then use this skill only for inspection or post-install configuration.
