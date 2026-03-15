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
| `Sarasa Fixed SC` | CJK-aware monospace (2:1 alignment) |
| `Consolas` | Western, pre-installed |

---

## Word (.docx) Font Configuration

### Built-in Reference

The skill includes a pre-configured `reference.docx` with:

| Element | Font |
|---------|------|
| Body text (CN) | 思源黑体 CN (Source Han Sans CN) |
| Body text (EN) | Times New Roman |
| Code blocks | Sarasa Fixed SC |

### Usage

```bash
pandoc input.md -o output.docx \
  --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx
```

### ASCII Art Alignment

For ASCII diagrams and boxed text to render correctly in Word:

1. **All lines in a box must have equal width** (including trailing spaces)
2. **Use monospace font** (set in `Source Code` style)
3. **No background shading** (trailing spaces would show colored background)

Example of correct ASCII box:
```text
┌─────────────┐
│ Hello 世界  │
│ Right align │
└─────────────┘
```

Each line above is exactly 15 characters (including spaces after `│`).

### Fixing Misaligned ASCII Art

If your ASCII boxes show jagged right edges in Word, pad lines to equal width:

```python
# Quick fix script for Markdown files
import re

def fix_ascii_box(match):
    lines = match.group(1).split('\n')
    # Find box width from top border
    max_width = max(len(l) for l in lines if any(c in l for c in '┌┐└┘─│'))
    # Pad all lines
    fixed = [l.ljust(max_width) if any(c in l for c in '┌┐└┘─│') else l for l in lines]
    return '```text\n' + '\n'.join(fixed) + '```'

with open('input.md', 'r') as f:
    content = f.read()

content = re.sub(r'```text\n(.*?)```', fix_ascii_box, content, flags=re.DOTALL)

with open('input.md', 'w') as f:
    f.write(content)
```
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
