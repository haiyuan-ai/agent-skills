---
name: mermaid-to-png
description: Convert Mermaid diagrams in Markdown files to styled PNG/SVG images with built-in professional themes. Use when users need to convert Mermaid diagrams to images, apply visual styles to diagrams, or export charts for documents, blogs, and presentations. Supports 4 built-in styles (dark-tech, fresh-business, hand-drawn, gradient-modern) and custom styling.
---

# mermaid-to-png

Convert Mermaid diagrams in Markdown files to styled PNG images with professional built-in themes.

## Auto-Execution

**When this skill is triggered, automatically execute the conversion script:**

```bash
python3 ~/.claude/skills/mermaid-to-png/scripts/convert.py <input-file> --style fresh-business --width 900 --replace
```

The script will:
1. Extract all Mermaid diagrams from the Markdown file
2. Convert each diagram to PNG with the specified style
3. Replace Mermaid code blocks with image references in the output

## Features

- **4 Built-in Style Themes**: Dark Tech, Fresh Business, Hand-drawn Sketch, Gradient Modern
- **Smart Style Injection**: Automatically injects theme configuration into diagrams
- **Multi-format Output**: PNG, SVG support
- **Batch Processing**: Convert all diagrams in a Markdown file
- **WeChat Optimized**: Preset for 900px width (WeChat Official Account)

## Usage

### Basic Usage

```bash
# Convert a markdown file with default settings
claude mermaid-to-png /path/to/article.md

# Specify output directory
claude mermaid-to-png article.md --output-dir ./images
```

### Style Themes

```bash
# Use Dark Tech style (perfect for technical architecture diagrams)
claude mermaid-to-png article.md --style dark-tech

# Use Fresh Business style (clean, professional look)
claude mermaid-to-png article.md --style fresh-business

# Use Hand-drawn style (sketch look for brainstorming)
claude mermaid-to-png article.md --style hand-drawn

# Use Gradient Modern style (vibrant, eye-catching)
claude mermaid-to-png article.md --style gradient-modern
```

### Advanced Options

```bash
# Custom width (WeChat recommended: 900)
claude mermaid-to-png article.md --width 900

# Generate SVG instead of PNG
claude mermaid-to-png article.md --format svg

# Replace mermaid code with image references in markdown
claude mermaid-to-png article.md --replace

# Custom background color
claude mermaid-to-png article.md --background "#f5f5f5"
```

## Style Themes Reference

### 1. dark-tech (Dark Technology)
Best for: Technical architecture, system diagrams, API flows
- Dark background (#1a1a2e) with accent colors
- Cyan/purple highlight colors
- Tech-style monospace fonts
- High contrast for readability

### 2. fresh-business (Fresh Business)
Best for: Business presentations, reports, process flows
- Clean white/light blue background
- Professional blue (#3498db) accent
- Modern sans-serif fonts
- Subtle, corporate-friendly colors

### 3. hand-drawn (Hand-drawn Sketch)
Best for: Brainstorming, ideation, early concepts
- Warm paper-like background (#fff9e6)
- Hand-drawn style fonts (Comic Sans MS)
- Sketch-like border colors
- Casual, creative feel

### 4. gradient-modern (Gradient Modern)
Best for: Product showcases, marketing, modern apps
- Vibrant gradient backgrounds
- Bold, saturated accent colors
- Modern display fonts (SF Pro)
- Eye-catching, contemporary design

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
| `--style` | Theme style (dark-tech, fresh-business, hand-drawn, gradient-modern) | `none` |
| `--width` | Image width in pixels | `1200` |
| `--background` | Background color | `white` |
| `--format` | Output format (png/svg) | `png` |
| `--replace` | Replace code blocks with images | `false` |
| `--chart-type` | Optimize for chart type (flowchart/sequence/gantt/class/state) | `auto` |

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
