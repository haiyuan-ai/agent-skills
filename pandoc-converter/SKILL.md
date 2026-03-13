---
name: pandoc-converter
description: >
  Convert between Markdown, Word (.docx), and PDF via pandoc. Supports
  CJK/English, LaTeX templates, reference docx, and batch mode.
  Trigger on: "转成 PDF/Word", "导出为", "生成 PDF", "convert to",
  "export as", "markdown 转 word", "docx 转 markdown", pandoc mentions,
  or any markdown/docx/pdf format conversion request.
---

# Pandoc Document Converter

Convert between Markdown, Word (.docx), and PDF with proper CJK support out of the box.

## Supported Conversions

| From     | To           |
|----------|--------------|
| Markdown | PDF          |
| Markdown | Word (.docx) |
| Word     | Markdown     |
| Word     | PDF          |

PDF as input is not supported (pandoc limitation).

## Quick Reference

```bash
# Markdown → PDF (with Chinese support)
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"

# Markdown → Word
pandoc input.md -o output.docx

# Word → Markdown
pandoc input.docx -o output.md --extract-media=./media

# Word → PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"
```

## Step-by-step Workflow

### 1. Identify the conversion

From the user's request, determine:
- **Source file(s)**: path and format
- **Target format**: pdf, docx, or md
- **Options**: template, styling, batch mode

Verify the source file exists before proceeding.

### 2. Build the pandoc command

Start with the base: `pandoc <input> -o <output>`

Then layer on options based on the target format and user needs:

#### PDF Output

The default PDF pipeline uses xelatex for reliable CJK rendering:

```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="Source Han Sans CN" \
  -V geometry:margin=2.5cm \
  -V colorlinks=true
```

**When the user wants more control** (custom styling, academic format, specific layout), offer these LaTeX variables:

```bash
# Common useful variables
-V fontsize=12pt
-V linestretch=1.5
-V documentclass=article    # or report, book, ctexart (for Chinese-focused)
-V papersize=a4
-V toc=true                 # table of contents
-V numbersections=true
-V header-includes='\usepackage{fancyhdr}'
```

For Chinese-heavy documents, `ctexart` as documentclass gives better defaults than manually setting CJKmainfont:
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V documentclass=ctexart \
  -V geometry:margin=2.5cm
```

**Custom LaTeX template**: if the user provides a `.tex` template:
```bash
pandoc input.md -o output.pdf --template=custom.tex --pdf-engine=xelatex
```

#### Word Output

Basic conversion works well out of the box:

```bash
pandoc input.md -o output.docx
```

**With a reference template** — when the user wants specific styling (fonts, headers, spacing), they provide a `.docx` reference file:

```bash
pandoc input.md -o output.docx --reference-doc=reference.docx
```

To help the user create a reference template:
```bash
# Generate a default reference.docx the user can customize in Word
pandoc -o custom-reference.docx --print-default-data-file reference.docx
```

#### Markdown Output (from Word)

```bash
pandoc input.docx -o output.md --extract-media=./media --wrap=none
```

`--extract-media` pulls embedded images into a folder. `--wrap=none` avoids hard line breaks in the output.

If the user wants cleaner markdown, add `--markdown-headings=atx` (uses `#` style headings).

### 3. Handle images and resources

- For markdown with local images: pandoc resolves relative paths from the source file's directory. Run pandoc from that directory or use `--resource-path`.
- For Word → Markdown: always use `--extract-media` so images aren't lost.
- For PDF output with images: xelatex handles most image formats. If an image fails, check the path is correct relative to where pandoc runs.

### 4. Run and verify

Execute the command. If it succeeds, confirm the output file exists and report its size. If it fails:

- **xelatex not found**: suggest `brew install --cask mactex` or `brew install basictex`
- **Font not found**: list available CJK fonts with `fc-list :lang=zh` and pick one
- **Missing package**: for LaTeX package errors, suggest `tlmgr install <package>`

### 5. Batch conversion

When the user wants to convert multiple files, use a simple loop:

```bash
# Convert all .md files in a directory to PDF
for f in /path/to/dir/*.md; do
  pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"
done

# Convert all .docx files to markdown
for f in /path/to/dir/*.docx; do
  pandoc "$f" -o "${f%.docx}.md" --extract-media="./media/$(basename "${f%.docx}")" --wrap=none
done
```

For batch mode, report progress as each file completes.

## Common Pitfalls

- **Garbled Chinese in PDF**: always use `--pdf-engine=xelatex` with a CJK font. Never use the default pdflatex for CJK content.
- **Word styles look wrong**: the default docx output is plain. If styling matters, use `--reference-doc`.
- **Images missing in markdown output**: forgot `--extract-media`.
- **PDF margins too tight**: add `-V geometry:margin=2.5cm` or adjust as needed.

## Output Naming Convention

Unless the user specifies an output path, place the output in the same directory as the input, with the same base name and the new extension. For example, `notes.md` → `notes.pdf`.

## Safety

- Before writing output, check if the target file already exists. If it does, inform the user and ask before overwriting.
- Never use user-provided paths in shell commands without quoting. All variables in batch loops must be double-quoted.
- This skill only reads source files and writes converted output. It must not delete, move, or modify the original input files.
