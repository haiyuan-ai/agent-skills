# Table Optimization for Pandoc

Best practices for rendering Markdown tables in Word (.docx) and PDF.

---

## Quick Start

```bash
# Word with table styles
pandoc input.md -o output.docx \
  --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx

# PDF with optimized table width
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="PingFang SC" \
  -V monofont="Sarasa Fixed SC" \
  -V geometry:margin=2cm
```

---

## Known Limitations

### PDF Table Width

By default, pandoc creates narrow centered tables in PDF. To improve:

**Option 1: Reduce margins**
```bash
-V geometry:margin=1.5cm  # Default is 2.5cm
```

**Option 2: Use full-width table LaTeX (advanced)**
Create a header file `header.tex`:
```latex
\usepackage{tabularx}
\makeatletter
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\makeatother
```
Then: `pandoc input.md -o output.pdf -H header.tex`

### PDF Horizontal Rules (---)

Pandoc renders `---` as short centered lines. This is by design in the LaTeX template.

**Workaround**: Use section headers (`## Section`) instead of horizontal rules for visual separation in PDF.

### Word Table Styles

Pandoc uses the "Normal Table" style by default for Markdown tables. The built-in `reference.docx` includes:

- **Normal Table**: Default style for all tables (clean, borderless)
- **Table Grid**: Reference style (can be applied manually in Word)

**Workaround**: After conversion, select tables in Word and apply "Table Grid" style from the Styles gallery.

---

## Common Issues & Solutions

### Issue 1: Tables span multiple pages

**Problem**: Long tables break awkwardly across pages.

**Solution**: Add `--variable=table-use-row-headings=true` for Word, or split into multiple tables.

### Issue 2: Column widths are inconsistent

**Problem**: Pandoc auto-distributes column widths equally, causing text wrapping issues.

**Solution**: Use simpler table structures or pre-format with HTML colgroups:

```markdown
<table>
<col width="30%">
<col width="70%">
<tbody>
<tr><td>Short</td><td>Long content...</td></tr>
</tbody>
</table>
```

### Issue 3: Table borders missing in Word

**Problem**: Converted tables have no visible borders.

**Solution**: Use `reference.docx` with pre-defined "Table Grid" style (included in this skill).

### Issue 4: CJK text overflowing in PDF

**Problem**: Chinese characters overflow cell boundaries.

**Solution**: 
- Increase cell padding with `geometry:margin`
- Use `--variable=CJKoptions{AutoFakeBold}` in header
- Reduce font size: `-V fontsize=10pt`

### Issue 5: Complex tables render poorly

**Problem**: Nested lists, code blocks, or images inside tables break layout.

**Solution**: 
- Flatten nested content into simple text
- Move code examples outside tables
- Use separate figures for complex data

---

## Best Practices

### ✅ Do:
- Keep tables under 6 columns
- Use short, descriptive headers
- Limit cell content to 1-2 lines
- Use bullet lists outside tables for complex items
- Test with representative data

### ❌ Don't:
- Nest tables inside tables
- Put code blocks inside cells
- Use tables for layout (use sections instead)
- Create tables wider than page width

---

## Example: Well-Formatted Table

```markdown
| Module      | Duration | Format          | Audience              |
|-------------|----------|-----------------|-----------------------|
| AI Evolution| 30 min   | Theory + Demo   | All roles             |
| Tool Demo   | 45 min   | Hands-on Lab    | Technical staff       |
| Best Practices | 30 min | Case Studies   | Project leads         |
```

Renders cleanly in Word and PDF with:
- Consistent column widths
- Centered vertical alignment
- Header row shading
- Proper CJK font support

---

## Advanced: Custom Table Styles

To customize table appearance in Word:

1. Open `reference.docx`
2. Home → Styles → Manage Styles
3. Find "Table Grid" style
4. Modify:
   - Borders: All borders, 0.5pt
   - Shading: Header row = light gray (F0F0F0)
   - Font: Same as body text
5. Save and use with `--reference-doc`

---

## Related

- [fonts.md](fonts.md) - Font configuration for CJK support
- [pdf-features.md](pdf-features.md) - PDF-specific formatting options
