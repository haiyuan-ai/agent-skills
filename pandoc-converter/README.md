[English](./README.md) | [中文](./README-zh.md)

# pandoc-converter

Convert between Markdown, Word (.docx), HTML, and PDF via pandoc with CJK support out of the box.

## Supported Conversions

| From     | To                       |
|----------|--------------------------|
| Markdown | PDF, Word (.docx), HTML  |
| Word     | PDF, Markdown            |
| HTML     | PDF, Word, Markdown      |

> PDF as input is not supported (pandoc limitation).

## Prerequisites

### pandoc

| OS      | Command                            |
|---------|------------------------------------|
| macOS   | `brew install pandoc`              |
| Ubuntu  | `sudo apt install pandoc`          |
| Windows | `winget install JohnMacFarlane.Pandoc` |

Verify: `pandoc --version` (requires 3.0+)

### LaTeX (required for PDF output)

| OS      | Command                                   | Notes                        |
|---------|-------------------------------------------|------------------------------|
| macOS   | `brew install --cask mactex`              | **Recommended**, full install (~4 GB) with CJK support |
| macOS   | `brew install basictex`                   | Minimal (~100 MB), requires manual CJK install: `sudo tlmgr install xeCJK ctex collection-xetex` |
| Ubuntu  | `sudo apt install texlive-xetex texlive-lang-chinese` | xelatex + CJK support |
| Windows | Install [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/) | Enable auto-install for missing packages |

Verify: `xelatex --version`

### CJK Fonts (required for Chinese PDF output)

| OS      | Recommended Font        | Install                                      |
|---------|-------------------------|----------------------------------------------|
| macOS   | PingFang SC             | Pre-installed on macOS                      |
| macOS   | Source Han Sans CN      | `brew install --cask font-source-han-sans`  |
| Ubuntu  | Noto Sans CJK SC        | `sudo apt install fonts-noto-cjk`           |
| Windows | SimSun / Microsoft YaHei | Pre-installed on Chinese Windows            |
| Windows | Source Han Sans CN      | https://github.com/adobe-fonts/source-han-sans/releases |

Verify: `fc-list :lang=zh | head -3`

## Quick Start

```bash
# Markdown to PDF (Chinese-ready)
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# Markdown to Word (with built-in reference.docx for proper fonts)
pandoc input.md -o output.docx --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx

# Markdown to HTML
pandoc input.md -o output.html --standalone

# Word to Markdown (with image extraction)
pandoc input.docx -o output.md --extract-media=./media --wrap=none

# Word to PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# HTML to Markdown
pandoc input.html -o output.md --wrap=none

# HTML to PDF
pandoc input.html -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"
```

## Usage with Claude Code

Install the skill:

```bash
claude install-skill /path/to/pandoc-converter
# or from GitHub
claude install-skill https://github.com/yourusername/pandoc-converter
```

Then just ask naturally:

- "Convert report.md to PDF"
- "把 document.docx 转成 markdown"
- "Export all .md files in ./docs to Word"
- "Generate standalone HTML from notes.md"

The skill handles CJK font selection, LaTeX engine configuration, image extraction, and batch mode automatically.

## Features

- **CJK Support**: Automatic Chinese font selection with xelatex
- **Multi-Format**: Markdown, Word, HTML, and PDF conversions
- **Font Fallback**: Multiple CJK font strategies (PingFang SC, Source Han, etc.)
- **Code Highlighting**: Syntax highlighting with customizable themes
- **Math Support**: LaTeX math rendering (MathJax, KaTeX)
- **Citations**: BibTeX and CSL style support
- **Batch Mode**: Convert multiple files at once
- **Self-Contained HTML**: Embed images and resources

## Documentation

### Core Reference
- **[SKILL.md](./SKILL.md)** - Main workflow and quick reference

### Advanced Topics
- **[references/fonts.md](./references/fonts.md)** - CJK/Western font configuration, multi-font fallback, code fonts
- **[references/syntax-highlighting.md](./references/syntax-highlighting.md)** - Code themes, language support
- **[references/math.md](./references/math.md)** - LaTeX equations, MathJax, KaTeX
- **[references/pdf-features.md](./references/pdf-features.md)** - Metadata, watermarks, headers/footers, YAML frontmatter
- **[references/advanced.md](./references/advanced.md)** - Citations, multi-file projects, GFM, Lua filters

## Recommended Fonts

### CJK Fonts
- **macOS**: `PingFang SC` (system default), `Source Han Sans CN`
- **Cross-platform**: `Source Han Sans CN`, `Noto Sans CJK SC`

### Code Fonts
- **CJK-aware monospace**: `Sarasa Fixed SC` (更纱黑体，2:1 CJK alignment)
- **Western**: `JetBrains Mono`, `Fira Code` (with ligatures)
- **CJK fallback**: `Noto Sans Mono CJK SC`

Install via Homebrew:
```bash
brew install --cask font-source-han-sans font-sarasa-gothic
```

**Windows users**: Download and install manually:
- **Source Han Sans CN**: https://github.com/adobe-fonts/source-han-sans/releases
- **Sarasa Gothic**: https://github.com/be5invis/Sarasa-Gothic/releases

---

## ASCII Art in Word

If your Markdown contains ASCII diagrams or tables, run the pre-processor before converting to Word:

```bash
# Fix ASCII art alignment (pad trailing spaces)
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md

# Then convert
pandoc input.md -o output.docx \
  --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx
```

**Why**: Word requires equal line widths in monospace blocks for proper box rendering.

See [references/fonts.md](references/fonts.md#ascii-art-alignment) for details.

## Examples

```bash
# Academic paper with citations
pandoc paper.md -o paper.pdf --pdf-engine=xelatex \
  -V CJKmainfont="Source Han Serif SC" \
  --bibliography=references.bib --citeproc

# Self-contained HTML
pandoc input.md -o output.html --standalone --embed-resources

# Batch: all .md to PDF
for f in *.md; do pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="PingFang SC"; done
```

## License

MIT
