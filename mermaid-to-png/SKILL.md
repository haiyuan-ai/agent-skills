---
name: mermaid-to-png
description: Convert Mermaid diagrams in Markdown files to styled PNG/SVG images with built-in professional themes. Use when users need to convert Mermaid diagrams to images, apply visual styles to diagrams, or export charts for documents, blogs, and presentations. Make sure to use this skill whenever the user mentions: mermaid diagrams, converting charts to images, diagram visualization, creating presentation-ready graphics, Markdown files with mermaid code blocks, or WeChat Official Account images - even if they don't explicitly say "convert to PNG". Supports 4 built-in styles (dark-tech, fresh-business, hand-drawn, gradient-modern) and custom styling.
---

# mermaid-to-png

Convert Mermaid diagrams in Markdown files to styled PNG images with professional built-in themes.

## When to Use This Skill

Trigger this skill when the user:
- Mentions converting mermaid diagrams to images
- Asks to export charts from Markdown files
- Needs presentation-ready diagram images
- References WeChat Official Account image requirements (900px width)
- Says things like "make this diagram look better" or "add styles to this chart"
- Has Markdown files with ```mermaid``` code blocks that need visual polish

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

## Resources

This skill includes:
- `scripts/convert.py` - Main conversion script with batch processing
- `scripts/styles.py` - Style theme definitions and injection logic

## Prerequisites

Install mermaid-cli:

```bash
npm install -g @mermaid-js/mermaid-cli
```

## Troubleshooting

### mermaid-cli not found
```
Error: mermaid-cli not found
Install with: npm install -g @mermaid-js/mermaid-cli
```

### Conversion timed out
- The diagram may be too complex - try reducing diagram size
- Check if Puppeteer (used by mermaid-cli) is properly installed
- Try increasing the timeout or simplifying the diagram syntax

### Style not applied correctly
- Ensure the diagram type matches the style configuration
- Some diagram types (gantt, sequence) have specific style requirements
- Check that the mermaid syntax is valid

## Arguments Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `input` | Input markdown file path | Required |
| `--output-dir` | Output directory for images | `./output` |
| `--style` | Theme style | `none` |
| `--width` | Image width in pixels | `1200` |
| `--background` | Background color | `white` |
| `--format` | Output format (png/svg) | `png` |
| `--replace` | Replace code blocks with images | `false` |
| `--chart-type` | Optimize for chart type | `auto` |

Available styles: `dark-tech`, `fresh-business`, `hand-drawn`, `gradient-modern`

## Output

The skill generates:
- PNG/SVG images for each Mermaid diagram found (saved to `output/` or specified directory)
- Optionally a converted Markdown file with image references (if `--replace` used)

Example output structure:
```
output/
├── diagram_1_a3f7d2e1.png
├── diagram_2_b8c9a4f3.png
└── article_converted.md
```
