# mermaid-to-png

将 Markdown 文件中的 Mermaid 代码块转换为 PNG/SVG 图片，并应用内置视觉主题。

## 功能

- 自动提取 Markdown 中的 Mermaid fenced code block
- 支持 4 套内置主题：`dark-tech`、`fresh-business`、`hand-drawn`、`gradient-modern`
- 支持 PNG 和 SVG 输出
- 支持自动识别图表类型：`flowchart`、`sequence`、`gantt`、`class`、`state`
- 支持 `--replace` 输出替换了 Mermaid 图片引用的 Markdown 文件
- 支持微信公众号常用宽度 `900px`

## 前置依赖

```bash
npm install -g @mermaid-js/mermaid-cli
python3 --version
```

脚本默认要求本地已安装 `mmdc`。只有显式传入 `--allow-npx` 时，才会回退到 `npx @mermaid-js/mermaid-cli`。

## 基本用法

```bash
# 默认导出 PNG 到 ./output
python3 scripts/convert.py article.md

# 输出到指定目录
python3 scripts/convert.py article.md --output-dir ./images

# 导出 SVG
python3 scripts/convert.py article.md --format svg

# 输出 900px 宽，适合微信公众号
python3 scripts/convert.py article.md --width 900

# 替换 Mermaid 代码块，额外生成 article_converted.md
python3 scripts/convert.py article.md --replace

# 没有本地 mmdc 时，显式允许 npx fallback
python3 scripts/convert.py article.md --allow-npx
```

## 主题示例

```bash
python3 scripts/convert.py article.md --style fresh-business --width 900
python3 scripts/convert.py article.md --style dark-tech --width 900
python3 scripts/convert.py article.md --style hand-drawn --width 900
python3 scripts/convert.py article.md --style gradient-modern --width 900
```

主题建议：

- `fresh-business`：报告、流程图、业务文档
- `dark-tech`：架构图、系统图、工程博客
- `hand-drawn`：头脑风暴、教学草图、研讨会材料
- `gradient-modern`：产品介绍、营销视觉、演示稿

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入 Markdown 文件 | 必填 |
| `--output-dir` | 图片输出目录 | `./output` |
| `--style` | 内置主题 | 无 |
| `--width` | 图片宽度（像素） | `1200` |
| `--background` | 背景色 | `white` |
| `--format` | 输出格式 | `png` |
| `--replace` | 输出替换后 Markdown | `false` |
| `--chart-type` | 强制指定图表类型或使用 `auto` | `auto` |
| `--allow-npx` | 允许在未安装本地 `mmdc` 时回退到 `npx` | `false` |
| `--disable-browser-sandbox` | 禁用 Chromium sandbox，仅限受信环境 | `false` |

## 输出

示例：

```text
output/
├── diagram_1_a3f7d2e1.png
├── diagram_2_b8c9a4f3.png
└── article_converted.md
```

使用 `--replace` 时，生成的 Markdown 会引用同目录下的图片文件名。

## 常见问题

### Mermaid CLI 或浏览器启动失败

先检查 Mermaid 语法，再检查本地 `mmdc` / Puppeteer 是否能正常启动。

如果你在受限沙箱、CI、远程容器里运行，Chromium 可能无法启动；这种情况需要：

- 在可启动本地浏览器的环境中执行
- 或为 Puppeteer 提供可用的 Chrome/Chromium 环境
- 或仅在你接受风险时，显式传入 `--disable-browser-sandbox`

### 未安装 mmdc

推荐直接安装：

```bash
npm install -g @mermaid-js/mermaid-cli
```

如果只是临时运行，并且你接受动态执行 npm 包的风险，可以显式传入：

```bash
python3 scripts/convert.py article.md --allow-npx
```

### 中文显示异常

macOS:

```bash
brew install --cask font-noto-sans-cjk
```

Linux:

```bash
sudo apt-get install fonts-noto-cjk
```

## 资源

- `scripts/convert.py`：主转换脚本
- `scripts/styles.py`：主题和 Mermaid init 配置生成逻辑
