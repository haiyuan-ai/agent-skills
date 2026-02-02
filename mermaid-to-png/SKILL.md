# mermaid-to-png

## Description

Convert Mermaid diagrams in Markdown files to PNG images for use in WeChat Official Accounts, blogs, and documents.

This skill extracts Mermaid diagrams from Markdown files, converts them to PNG (or SVG) images using mermaid-cli, and optionally replaces the code blocks with image references.

## Usage

```bash
# Convert a markdown file
claude mermaid-to-png /path/to/article.md

# Specify output directory
claude mermaid-to-png article.md --output-dir ./images

# Custom width (WeChat recommended: 900)
claude mermaid-to-png article.md --width 900

# Generate SVG instead of PNG
claude mermaid-to-png article.md --format svg

# Replace mermaid code with image references
claude mermaid-to-png article.md --replace
```

## Prerequisites

Install mermaid-cli:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input` | Input Markdown file path | Required |
| `--output-dir` | Output directory for images | `./output` |
| `--width` | Image width in pixels | `1200` |
| `--background` | Background color | `white` |
| `--format` | Output format (png/svg) | `png` |
| `--replace` | Replace code blocks with images | `false` |

## Output

The skill generates:
- PNG/SVG images for each Mermaid diagram found
- Optionally a converted Markdown file with image references

Example output structure:
```
output/
├── diagram_1_a3f7d2e1.png
├── diagram_2_b8c9a4f3.png
└── article_converted.md  (if --replace used)
```

## Triggers

- `mermaid-to-png`
- `convert mermaid`
- `mermaid to png`
- `转换 mermaid`
- `生成图表图片`
