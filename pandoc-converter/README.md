# pandoc-converter

Convert between Markdown, Word (.docx), and PDF via pandoc with CJK support out of the box.

## Supported Conversions

| From     | To              |
|----------|-----------------|
| Markdown | PDF, Word       |
| Word     | PDF, Markdown   |

> PDF as input is not supported (pandoc limitation).

## Prerequisites

### pandoc

| OS      | Command                            |
|---------|------------------------------------|
| macOS   | `brew install pandoc`              |
| Ubuntu  | `sudo apt install pandoc`          |
| Windows | `winget install JohnMacFarlane.Pandoc` |

Verify: `pandoc --version` (requires 3.0+).

### LaTeX (required for PDF output)

| OS      | Command                                   | Notes                        |
|---------|-------------------------------------------|------------------------------|
| macOS   | `brew install --cask mactex`              | Full install (~4 GB)         |
| macOS   | `brew install basictex`                   | Minimal (~100 MB), may need `tlmgr install` for extra packages |
| Ubuntu  | `sudo apt install texlive-xetex texlive-lang-chinese` | xelatex + CJK support |
| Windows | Install [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/) | Enable auto-install for missing packages |

Verify: `xelatex --version`

### CJK Fonts (required for Chinese PDF output)

| OS      | Recommended Font        | Install                                      |
|---------|-------------------------|----------------------------------------------|
| macOS   | Source Han Sans CN      | `brew install --cask font-source-han-sans-cn` (or already bundled on many macOS setups) |
| Ubuntu  | Noto Sans CJK SC       | `sudo apt install fonts-noto-cjk`           |
| Windows | SimSun / Microsoft YaHei | Pre-installed on Chinese Windows             |

Verify: `fc-list :lang=zh | head -3`

## Quick Start

```bash
# Markdown -> PDF (Chinese-ready)
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"

# Markdown -> Word
pandoc input.md -o output.docx

# Word -> Markdown (with image extraction)
pandoc input.docx -o output.md --extract-media=./media --wrap=none

# Word -> PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"
```

## Usage with Claude Code

Install the skill:

```bash
claude install-skill /path/to/pandoc-converter
# or from GitHub
claude install-skill https://github.com/anthropics/agent-skills/tree/main/pandoc-converter
```

Then just ask naturally:

- "把 report.md 转成 PDF"
- "Convert notes.docx to markdown"
- "Export all .md files in ./docs to Word"

The skill handles CJK font selection, LaTeX engine configuration, image extraction, and batch mode automatically.

## Advanced Options

- **Custom LaTeX template**: `--template=custom.tex`
- **Reference Word style**: `--reference-doc=reference.docx`
- **Chinese-optimized PDF**: uses `ctexart` document class
- **Batch conversion**: converts all matching files in a directory

See [SKILL.md](./SKILL.md) for the full workflow reference.

## License

MIT
