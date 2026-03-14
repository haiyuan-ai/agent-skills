# Advanced Features

## Citations

```bash
# Basic BibTeX
pandoc input.md -o output.pdf \
  --bibliography=references.bib \
  --citeproc

# With CSL style
pandoc input.md -o output.pdf \
  --bibliography=references.bib \
  --citeproc \
  --csl=apa.csl
```

**Markdown**: `[@smith2020]` or `[@smith2020, pp. 23-25]`

**CSL Styles**: `apa.csl`, `mla.csl`, `ieee.csl`, `gb-t-7714-2015-numeric.csl`

Download: https://github.com/citation-style-language/styles

---

## Multi-File Projects

```bash
# Combine files
pandoc ch1.md ch2.md ch3.md -o book.pdf

# Wildcards (alphabetical)
pandoc chapters/*.md -o book.pdf

# With metadata
pandoc metadata.yaml 00-title.md chapters/*.md -o book.pdf
```

**Naming**: Use `01-`, `02-` prefixes to control order.

**File inclusion**:
```markdown
```{include chapter1.md}
```

```bash
pandoc main.md -o output.pdf --file-scope
```

---

## Markdown Variants

```bash
# GitHub Flavored Markdown (GFM)
pandoc input.md -o output.pdf --from=gfm

# CommonMark (strict)
pandoc input.md -o output.docx --from=commonmark

# Extensions
--from=markdown+task_lists+emoji    # Enable
--from=markdown-smart               # Disable smart quotes
```

**GFM Features**:
```markdown
- [ ] Task list
~~strikethrough~~
https://auto.link
```

---

## Lua Filters

```bash
# Apply filter
pandoc input.md -o output.pdf --lua-filter=filter.lua

# Global directory: ~/.pandoc/filters/
```

**Examples**:

```lua
-- Figure numbering
local n = 0
function Figure(el)
  n = n + 1
  el.caption = pandoc.Strong("Figure " .. n .. ": ") .. el.caption
  return el
end

-- Task list styling
function BulletList(el)
  for _, item in ipairs(el.content) do
    local first = item[1] and item[1][1]
    if first then
      if first.text == "[ ]" then first.text = "☐ "
      elseif first.text == "[x]" then first.text = "☑ " end
    end
  end
  return el
end

-- Word count
local words = 0
function Str(el)
  words = words + select(2, el.text:gsub("%S+", ""))
end
function Pandoc(el)
  print("Words: " .. words); return el
end
```

Resources: https://pandoc.org/lua-filters.html
