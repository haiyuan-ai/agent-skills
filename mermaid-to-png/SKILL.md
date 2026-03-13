---
name: mermaid-to-png
description: Convert Mermaid code blocks in Markdown into polished PNG or SVG images. Use when users ask to export Mermaid diagrams, replace Mermaid blocks with images, restyle diagrams for articles/slides/WeChat, or make Mermaid charts more presentation-ready. Supports built-in themes `dark-tech`, `fresh-business`, `hand-drawn`, and `gradient-modern`.
---

# mermaid-to-png

Convert Mermaid code blocks in Markdown files to styled PNG/SVG images with built-in themes.

## Use This Skill When

- The input is a Markdown file containing ```mermaid``` code blocks
- The user wants PNG/SVG exports, visual polish, or image replacement in the Markdown
- The target is an article, slide deck, blog post, or WeChat Official Account post
- The user says "make this Mermaid diagram look better" without naming a file format

## Workflow

1. Inspect the Markdown file and confirm it contains Mermaid code blocks.
2. Run the bundled converter:

```bash
python3 mermaid-to-png/scripts/convert.py <input-file> --style fresh-business --width 900 --replace
```

3. Pick a style based on context:
- `fresh-business`: reports, docs, business/process diagrams
- `dark-tech`: architecture, engineering, API/system diagrams
- `hand-drawn`: ideation, teaching, workshop notes
- `gradient-modern`: product, marketing, keynote-style visuals
4. Use `--width 900` for WeChat unless the user requests something else.
5. Add `--replace` when the user wants a Markdown file with image references.

## Key Options

- `--style <name>`: apply one built-in theme
- `--format png|svg`: choose raster or vector output
- `--width <px>`: image width, default `1200`
- `--replace`: emit `<input>_converted.md` with Mermaid blocks replaced by image links
- `--output-dir <dir>`: store generated assets in a specific directory
- `--chart-type auto|flowchart|sequence|gantt|class|state`: override type detection only if auto-detection is wrong

## Notes

- The converter auto-detects common Mermaid chart types.
- When `--replace` is used, the converted Markdown references image filenames in the same output directory.
- Prefer a locally installed `mmdc`; the script falls back to `npx @mermaid-js/mermaid-cli`.

## Prerequisites

```bash
npm install -g @mermaid-js/mermaid-cli
```

If rendering fails, check Mermaid syntax first, then verify `mmdc`/Puppeteer can run in the local environment.
