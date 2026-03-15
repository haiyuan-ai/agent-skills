---
name: pandoc-converter
description: >
  Convert between Markdown, Word (.docx), HTML, and PDF via pandoc with CJK support.
  Trigger on: "转成/生成 PDF/Word/HTML", "导出为", "convert to", "export as",
  pandoc mentions, or any format conversion involving md/docx/html/pdf.
---

# Pandoc Document Converter

Convert between Markdown, Word (.docx), HTML, and PDF with proper CJK support out of the box.

## Supported Conversions

| From     | To           |
|----------|--------------|
| Markdown | PDF          |
| Markdown | Word (.docx) |
| Markdown | HTML         |
| Word     | Markdown     |
| Word     | PDF          |
| HTML     | Markdown     |
| HTML     | Word (.docx) |
| HTML     | PDF          |

PDF as input is not supported (pandoc limitation).

---

## Quick Reference

```bash
# Markdown to PDF (recommended: use script)
bash ~/.agents/skills/pandoc-converter/scripts/convert-to-pdf.sh input.md

# Markdown to PDF (manual)
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# Markdown to Word
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md  # optional
pandoc input.md -o output.docx --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx

# Markdown to HTML
pandoc input.md -o output.html --standalone

# Word to Markdown
pandoc input.docx -o output.md --extract-media=./media

# Word to PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# HTML to Markdown
pandoc input.html -o output.md --wrap=none

# HTML to Word
pandoc input.html -o output.docx --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx

# HTML to PDF
pandoc input.html -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"
```

---

## Scripts

| Script | Purpose | When to use |
|--------|---------|-------------|
| `convert-to-pdf.sh` | Optimized PDF with CJK monospace font, 11pt, 1.5cm margins | All PDF conversions (recommended) |
| `fix-ascii-art.py` | Pad ASCII box lines to equal width | Before Word conversion if ASCII diagrams exist |

---

## Step-by-step Workflow

### 1. Identify the conversion

From the user's request, determine:
- **Source file(s)**: path and format
- **Target format**: pdf, docx, md, or html
- **Options**: template, styling, batch mode

Verify the source file exists before proceeding.

### 2. Build the pandoc command

Start with the base: `pandoc <input> -o <output>`

Then layer on options based on the target format.

#### PDF Output

**Recommended: use the conversion script** (includes CJK monospace font, 11pt, optimized margins):
```bash
bash ~/.agents/skills/pandoc-converter/scripts/convert-to-pdf.sh input.md
```

**Manual setup**:
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="PingFang SC" \
  -V monofont="Sarasa Fixed SC" \
  -V geometry:margin=2cm
```

**Common variables**:
```bash
-V fontsize=11pt             # 11pt recommended for technical docs
-V linestretch=1.5
-V papersize=a4
-V toc=true
```

**Font recommendations**:
- macOS: `PingFang SC` (system font)
- Cross-platform: `Source Han Sans CN` / `Noto Sans CJK SC`
- Code: `Sarasa Fixed SC` (CJK-aware monospace)

📚 **Font details**: [references/fonts.md](references/fonts.md)

#### Word Output

**Recommended workflow**:
```bash
# 1. Fix ASCII art alignment (if needed)
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md --check

# 2. Fix if issues found
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md

# 3. Convert with reference.docx
pandoc input.md -o output.docx \
  --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx
```

Built-in `reference.docx` includes:
- **CJK font**: 思源黑体 CN (Source Han Sans CN)
- **English font**: Times New Roman
- **Code font**: Sarasa Fixed SC (CJK-aware monospace)
- **Table styles**: Header shading, vertical center alignment

**Table tips**:
- Keep tables under 6 columns for readability
- Use short cell content; break long text into multiple rows
- Avoid nested lists inside table cells

#### Markdown Output

```bash
pandoc input.docx -o output.md --extract-media=./media --wrap=none
```

#### HTML Output

```bash
# Standalone HTML
pandoc input.md -o output.html --standalone

# With CSS
pandoc input.md -o output.html --standalone --css=style.css

# Self-contained (embed images)
pandoc input.md -o output.html --standalone --embed-resources
```

#### HTML Input

```bash
# HTML to Markdown
pandoc input.html -o output.md --wrap=none

# HTML to PDF
pandoc input.html -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"
```

### 3. Handle images and resources

- For markdown with local images: use `--resource-path` if needed
- For Word to Markdown: always use `--extract-media`
- For PDF with images: xelatex handles most formats

### 4. Run and verify

Execute the command. Common issues:

| Issue | Solution |
|-------|----------|
| xelatex not found | `brew install --cask mactex` |
| Font not found | `fc-list :lang=zh` to list available fonts |
| Missing LaTeX package | `tlmgr install <package>` |

### 5. Batch conversion

```bash
# All .md to PDF
for f in *.md; do pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="PingFang SC"; done

# All .docx to Markdown
for f in *.docx; do pandoc "$f" -o "${f%.docx}.md" --extract-media=./media --wrap=none; done

# All .md to HTML
for f in *.md; do pandoc "$f" -o "${f%.md}.html" --standalone; done
```

---

## Advanced Features

The following features are documented in separate reference files:

| Feature | Description | Reference |
|---------|-------------|-----------|
| **Font Configuration** | CJK fonts, fallback, code fonts | [references/fonts.md](references/fonts.md) |
| **Syntax Highlighting** | Code themes, language support | [references/syntax-highlighting.md](references/syntax-highlighting.md) |
| **Math** | LaTeX equations, MathJax, KaTeX | [references/math.md](references/math.md) |
| **PDF Features** | Metadata, frontmatter, watermarks | [references/pdf-features.md](references/pdf-features.md) |
| **Advanced** | Citations, multi-file, GFM, Lua filters | [references/advanced.md](references/advanced.md) |

---

## Common Pitfalls

- **Garbled Chinese text in PDF**: Always use `--pdf-engine=xelatex` with a CJK font
- **Word styles look wrong**: Use `--reference-doc` for custom styling
- **Images missing in Markdown output**: Add `--extract-media`
- **PDF margins too tight**: Add `-V geometry:margin=2cm`
- **HTML lacks styles**: Use `--standalone`
- **HTML images not showing**: Use `--embed-resources` to inline images
- **Citations not rendering**: Ensure `--citeproc` is included
- **Math not rendering in HTML**: Add `--mathjax` or `--katex`
- **ASCII art misaligned in Word/PDF**: 
  - Run `python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md`
  - Use `convert-to-pdf.sh` which enforces monospace font
- **Code block background shows trailing spaces**: reference.docx has no shading on Source Code style

---

## Tips & Tricks

**Dry run**: Add `--verbose` to see what pandoc is doing.

**List supported formats**:
```bash
pandoc --list-input-formats
pandoc --list-output-formats
```

**Check template**:
```bash
pandoc --print-default-template=latex
```

**Self-contained HTML**: Use `--embed-resources --standalone` for single-file distribution.

---

## Output Naming

Unless the user specifies an output path, place the output in the same directory as the input, with the same base name and the new extension.

---

## Safety

- Check if target file exists before overwriting
- Always quote paths in shell commands
- Only read source files and write output; never modify originals