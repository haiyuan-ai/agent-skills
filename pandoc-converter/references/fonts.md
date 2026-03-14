# Font Configuration

CJK and code font setup for pandoc.

## Quick Start

```bash
# macOS
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="PingFang SC" \
  -V monofont="JetBrains Mono"

# Cross-platform
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="Source Han Sans CN" \
  -V monofont="Sarasa Mono SC"
```

## Font Variables

| Variable | Purpose |
|----------|---------|
| `CJKmainfont` | CJK body text |
| `CJKsansfont` | CJK sans-serif (via header-includes) |
| `CJKmonofont` | CJK monospace (via header-includes) |
| `mainfont` | Western body text |
| `sansfont` | Western sans-serif |
| `monofont` | Western monospace |

## CJK Fonts

### macOS
- `PingFang SC` (system default)
- `Songti SC` (serif)
- `Heiti SC` (legacy)

### Cross-platform
- `Source Han Sans CN` / `Noto Sans CJK SC`
- `Sarasa Gothic SC`

Install: `brew install --cask font-source-han-sans`

## Code Fonts

| Font | Type |
|------|------|
| `JetBrains Mono` | Western, ligatures |
| `Fira Code` | Western, ligatures |
| `Sarasa Mono SC` | CJK, 2:1 alignment |
| `Noto Sans Mono CJK SC` | CJK |

## Multi-Font Fallback

```bash
# Using ctex (auto-detects available fonts)
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V documentclass=ctexart

# Manual fallback
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V "header-includes=\\setCJKmainfont{PingFang SC}" \
  -V "header-includes=\\setCJKmonofont{Sarasa Mono SC}"
```

## Font Scaling

```bash
-V "header-includes=\\setmonofont{JetBrains Mono}[Scale=0.85]"
```

## System Detection

```bash
fc-list :lang=zh | grep -i "pingfang\|source.*han"
```

## Complete Example

```bash
pandoc paper.md -o paper.pdf \
  --pdf-engine=xelatex \
  -V "header-includes=\\setCJKmainfont{Source Han Serif SC}" \
  -V "header-includes=\\setCJKmonofont{Sarasa Mono SC}" \
  -V "header-includes=\\setmonofont{JetBrains Mono}[Scale=0.85]" \
  -V linestretch=1.5
```
