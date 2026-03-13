# pandoc-converter

基于 pandoc 的文档格式转换技能，开箱即用支持中英文。

## 支持的转换

| 输入     | 输出            |
|----------|-----------------|
| Markdown | PDF、Word       |
| Word     | PDF、Markdown   |

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
| macOS   | 思源黑体 CN           | `brew install --cask font-source-han-sans-cn`（macOS 通常已自带） |
| Ubuntu  | Noto Sans CJK SC     | `sudo apt install fonts-noto-cjk`          |
| Windows | 宋体 / 微软雅黑       | 中文 Windows 系统自带                       |

验证：`fc-list :lang=zh | head -3`

## 快速开始

```bash
# Markdown → PDF（中文就绪）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"

# Markdown → Word
pandoc input.md -o output.docx

# Word → Markdown（自动提取图片）
pandoc input.docx -o output.md --extract-media=./media --wrap=none

# Word → PDF
pandoc input.docx -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Source Han Sans CN"
```

## 在 Claude Code 中使用

安装技能：

```bash
claude install-skill /path/to/pandoc-converter
# 或从 GitHub 安装
claude install-skill https://github.com/anthropics/agent-skills/tree/main/pandoc-converter
```

然后用自然语言即可：

- "把 report.md 转成 PDF"
- "把 notes.docx 转成 markdown"
- "把 docs 目录下所有 md 文件导出为 Word"

技能会自动处理中文字体选择、LaTeX 引擎配置、图片提取和批量模式。

## 进阶选项

- **自定义 LaTeX 模板**：`--template=custom.tex`
- **Word 参考样式**：`--reference-doc=reference.docx`
- **中文优化 PDF**：使用 `ctexart` 文档类
- **批量转换**：转换目录下所有匹配文件

完整工作流参考 [SKILL.md](./SKILL.md)。

## 许可证

MIT
