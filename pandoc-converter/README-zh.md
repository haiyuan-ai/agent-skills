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
| macOS   | `brew install --cask mactex`                 | **推荐**，完整安装（约 4 GB），含 CJK 支持 |
| macOS   | `brew install basictex`                      | 精简版（约 100 MB），需额外安装 CJK 包：`sudo tlmgr install xeCJK ctex collection-xetex` |
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
| Windows | 思源黑体 CN           | https://github.com/adobe-fonts/source-han-sans/releases |

验证：`fc-list :lang=zh | head -3`

## 快速开始

```bash
# Markdown → PDF（中文就绪）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="PingFang SC"

# Markdown → PDF（推荐：优化字体和布局）
pandoc input.md -o output.pdf --pdf-engine=xelatex \
  -H <(cat << 'EOF'
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}
\setCJKmonofont{Sarasa Fixed SC}
\setmonofont{Sarasa Fixed SC}
\usepackage{geometry}
\geometry{margin=1.5cm,a4paper}
EOF
)

# Markdown → Word（使用预设字体配置）
pandoc input.md -o output.docx --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx

# 使用优化脚本（推荐）
bash ~/.agents/skills/pandoc-converter/scripts/convert-to-pdf.sh input.md
```

### 字体说明

Skill 内置 `reference.docx` 模板，默认字体配置：
- **中文**：思源黑体 CN
- **英文**：Times New Roman
- **代码**：Sarasa Fixed SC（更纱黑体）

安装推荐字体：
```bash
# macOS
brew install --cask font-source-han-sans font-sarasa-gothic

# Ubuntu/Debian
sudo apt install fonts-noto-cjk fonts-sarasa-gothic

# Windows
# 思源黑体：https://github.com/adobe-fonts/source-han-sans/releases
# 更纱黑体：https://github.com/be5invis/Sarasa-Gothic/releases
```

### ASCII 图形对齐

如果 Markdown 中包含 ASCII 表格/图形，转换前建议运行预处理：

```bash
# 自动补齐尾随空格，确保右边框对齐
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md

# 然后转换
pandoc input.md -o output.docx \
  --reference-doc=~/.agents/skills/pandoc-converter/references/reference.docx
```

**原理**：Word 中等宽字体渲染要求 ASCII 框的每行字符数一致（包括尾随空格）。

### PDF 优化建议

**字体大小**：
- 默认 LaTeX 使用 10pt，偏小
- **推荐 11pt**：适合技术文档，阅读舒适
- 12pt：适合打印或视力不佳的读者

```bash
-V fontsize=11pt  # 在转换脚本中已默认使用
```

**代码块等宽字体**：必须显式设置 `\setCJKmonofont`，否则中文代码块可能不使用等宽字体：

```latex
\usepackage{xeCJK}
\setCJKmainfont{PingFang SC}      # 中文正文
\setCJKmonofont{Sarasa Fixed SC}  # 中文等宽（代码块）
\setmonofont{Sarasa Fixed SC}     # 英文等宽
```

**表格宽度**：默认 LaTeX 表格居中且较窄，可通过以下方式改善：
- 减小页边距：`\geometry{margin=1.5cm}`（默认约 2.5cm）
- 表格会自动适应可用宽度

**ASCII 图形对齐排查**：

如果在 Obsidian 中对齐但 PDF/Word 中不对齐：

```bash
# 1. 检查源文件
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md --check

# 2. 如有问题，自动修复
python3 ~/.agents/skills/pandoc-converter/scripts/fix-ascii-art.py input.md

# 3. 重新转换 PDF
bash ~/.agents/skills/pandoc-converter/scripts/convert-to-pdf.sh input.md
```

**推荐工作流**：
```bash
# 一键转换（推荐）
bash ~/.agents/skills/pandoc-converter/scripts/convert-to-pdf.sh input.md
```

📚 **详细文档**：[references/tables.md](references/tables.md) | [references/fonts.md](references/fonts.md)

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
- **[references/fonts.md](./references/fonts.md)** - 中英文字体配置、多字体回退、代码字体
- **[references/tables.md](./references/tables.md)** - 表格优化最佳实践
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

```bash
# 学术论文（带参考文献）
pandoc paper.md -o paper.pdf --pdf-engine=xelatex \
  -V CJKmainfont="Source Han Serif SC" \
  --bibliography=references.bib --citeproc

# 独立 HTML（内嵌图片）
pandoc input.md -o output.html --standalone --embed-resources

# 批量转换
for f in *.md; do pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="PingFang SC"; done
```

## 许可证

MIT
