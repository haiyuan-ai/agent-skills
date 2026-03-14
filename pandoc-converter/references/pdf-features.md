# PDF Features and Metadata

## PDF Metadata

```bash
pandoc input.md -o output.pdf \
  -V title="Document Title" \
  -V author="Author Name" \
  -V date="2024-03-14" \
  -V subject="Subject" \
  -V keywords="keyword1, keyword2"
```

## YAML Frontmatter

```markdown
---
title: Document Title
author: Author Name
date: 2024-03-14
subject: Subject
keywords: [kw1, kw2]

# Formatting
fontsize: 12pt
geometry: margin=2.5cm
linestretch: 1.5
papersize: a4
documentclass: article  # or ctexart, report, book

# TOC
toc: true
toc-depth: 2
numbersections: true

# Links
colorlinks: true
linkcolor: blue
---
```

## Page Layout

```bash
# Margins
-V geometry:margin=2.5cm
-V geometry:top=2cm,bottom=2cm,left=3cm,right=3cm

# Page size
-V papersize=a4        # a4, letter, a5
-V geometry:landscape  # Orientation
```

## Watermarks

```bash
pandoc input.md -o output.pdf \
  -V "header-includes=\\usepackage{draftwatermark}" \
  -V "header-includes=\\SetWatermarkText{DRAFT}" \
  -V "header-includes=\\SetWatermarkScale{0.5}"
```

## Headers/Footers

```bash
pandoc input.md -o output.pdf \
  -V "header-includes=\\usepackage{fancyhdr}" \
  -V "header-includes=\\pagestyle{fancy}" \
  -V "header-includes=\\fancyhead[L]{Left}" \
  -V "header-includes=\\fancyhead[R]{Right}" \
  -V "header-includes=\\fancyfoot[C]{\\thepage}"
```

## Multi-line YAML

```markdown
---
abstract: |
  This is a multi-line abstract.

  It can contain paragraphs.

author:
  - Alice Smith
  - Bob Jones

header-includes:
  - \\usepackage{custom-package}
  - \\setlength{\\parindent}{0pt}
---
```

## Variable Priority

Command-line `-V` overrides YAML settings.
