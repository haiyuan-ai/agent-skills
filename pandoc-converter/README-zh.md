[English](./README.md) | [中文](./README-zh.md)

# pandoc-converter

基于 pandoc 的文档格式转换技能，开箱即用支持 Markdown、Word、HTML、PDF 互转。

## 支持的转换

| 输入     | 输出                      |
|----------|---------------------------|
| Markdown | PDF、Word (.docx)、HTML   |
| Word     | PDF、Markdown             |
| HTML     | PDF、Word、Markdown       |

> PDF 作为输入暂不支持（pandoc 本身限制）。

## 前置依赖

### pandoc

| 系统    | 安装命令                              |
|---------|---------------------------------------|
| macOS   | `brew install pandoc`                 |
| Ubuntu  | `sudo apt install pandoc`             |
| Windows | `winget install JohnMacFarlane.Pandoc` |

验证：`pandoc --version`（需要 3.0+）

### LaTeX（生成 PDF 时必需）

| 系统    | 安装命令                                     | 说明                          |
|---------|----------------------------------------------|-------------------------------|
| macOS   | `brew install --cask mactex`                 | 完整安装（约 4 GB）          |
| macOS   | `brew install basictex`                      | 精简版（约 100 MB），可能需要 `tlmgr install` 补装包 |
| Ubuntu  | `sudo apt install texlive-xetex texlive-lang-chinese` | xelatex + 中文支持    |
| Windows | 安装 [MiKTeX](https://miktex.org/) 或 [TeX Live](https://tug.org/texlive/) | 建议开启自动安装缺失包 |

验证：`xelatex --version`

### 中文字体（生成中文 PDF 时必需）

| 系统    | 推荐字体              | 安装方式                                    |
|---------|-----------------------|---------------------------------------------|
| macOS   | 苹方 (PingFang SC)    | macOS 系统自带                              |
| macOS   | 思源黑体 CN           | `brew install --cask font-source-han-sans`  |
| Ubuntu  | Noto Sans CJK SC      | `sudo apt install fonts-noto-cjk`          |
| Windows | 宋体 / 微软雅黑       | 中文 Windows 系统自带                       |

验证：`fc-list :lang=zh | head -3`

## 快速开始

```bash
# Markdown → PDF（中文就绪）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# Markdown → Word
pandoc input.md -o output.docx

# Markdown → HTML
pandoc input.md -o output.html --standalone

# Word → Markdown（自动提取图片）
pandoc input.docx -o output.md --extract-media=./media --wrap=none

# Word → PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# HTML → Markdown
pandoc input.html -o output.md --wrap=none

# HTML → PDF
pandoc input.html -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"
```

## 在 Claude Code 中使用

安装技能：

```bash
claude install-skill /path/to/pandoc-converter
# 或从 GitHub 安装
claude install-skill https://github.com/yourusername/pandoc-converter
```

然后用自然语言即可：

- "把 report.md 转成 PDF"
- "把 notes.docx 转成 markdown"
- "把 docs 目录下所有 md 文件导出为 Word"
- "从 notes.md 生成独立 HTML"

技能会自动处理中文字体选择、LaTeX 引擎配置、图片提取和批量模式。

## 功能特性

- **CJK 支持**：xelatex 自动处理中文字体
- **多格式**：Markdown、Word、HTML、PDF 互转
- **字体回退**：支持多字体策略（苹方、思源黑体等）
- **代码高亮**：可自定义语法高亮主题
- **数学公式**：支持 LaTeX 公式渲染（MathJax、KaTeX）
- **参考文献**：支持 BibTeX 和 CSL 样式
- **批量处理**：一次性转换多个文件
- **独立 HTML**：内嵌图片和资源

## 文档

### 核心参考
- **[SKILL.md](./SKILL.md)** - 主要工作流和快速参考

### 进阶主题
- **[references/fonts.md](./references/fonts.md)** - 中英文字体配置、多字体回退、代码字体
- **[references/syntax-highlighting.md](./references/syntax-highlighting.md)** - 代码高亮主题、语言支持
- **[references/math.md](./references/math.md)** - LaTeX 公式、MathJax、KaTeX
- **[references/pdf-features.md](./references/pdf-features.md)** - 元数据、水印、页眉页脚、前置元数据
- **[references/advanced.md](./references/advanced.md)** - 参考文献、多文件合并、GFM、Lua 过滤器

## 推荐字体

### 中文字体
- **macOS**：苹方 `PingFang SC`（系统默认）、思源黑体 `Source Han Sans CN`
- **跨平台**：思源黑体 `Source Han Sans CN`、Noto Sans CJK SC

### 代码字体
- **西文**：JetBrains Mono、Fira Code（连字支持）
- **中文**：更纱黑体 `Sarasa Mono SC`（2:1 对齐）、Noto Sans Mono CJK SC

通过 Homebrew 安装：
```bash
brew install --cask font-jetbrains-mono font-sarasa-gothic font-source-han-sans
```

## 示例

### 学术论文
```bash
pandoc paper.md -o paper.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="Source Han Serif SC" \
  -V monofont="JetBrains Mono" \
  --bibliography=references.bib \
  --citeproc \
  --highlight-style=tango \
  -V toc=true
```

### 独立 HTML
```bash
pandoc input.md -o output.html \
  --standalone \
  --embed-resources \
  --mathjax \
  --highlight-style=monochrome
```

### 批量转换
```bash
# 转换所有 markdown 文件为 PDF
for f in *.md; do
  pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="PingFang SC"
done
```

## 许可证

MIT
