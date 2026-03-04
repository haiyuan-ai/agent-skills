# mermaid-to-png

将 Markdown 文件中的 Mermaid 图表转换为 PNG/SVG 图片，支持 4 套内置专业风格主题。

## 功能特性

- 🚀 自动提取 Markdown 中的 Mermaid 代码块
- 🎨 4 套内置风格主题：深色科技、清新商务、手绘草图、渐变现代
- 🖼️ 支持自定义图片宽度、背景色、格式（PNG/SVG）
- 📝 可选替换原文中的 Mermaid 代码为图片引用
- 📦 批量处理多个图表
- 🔧 微信公众号优化（推荐宽度 900px）

## 安装

### 前置依赖

```bash
# 1. 安装 Node.js 和 npm
# 从 https://nodejs.org/ 下载安装

# 2. 安装 mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# 3. 确保 Python 3.8+ 已安装
python3 --version
```

## 使用方法

### 基本用法

```bash
# 转换 Markdown 文件
python3 scripts/convert.py article.md

# 指定输出目录
python3 scripts/convert.py article.md --output-dir ./images

# 自定义宽度（微信公众号推荐 900px）
python3 scripts/convert.py article.md --width 900

# 生成 SVG 格式
python3 scripts/convert.py article.md --format svg

# 替换 Mermaid 代码为图片引用
python3 scripts/convert.py article.md --replace
```

### 使用风格主题

```bash
# 深色科技风格（适合技术架构图）
python3 scripts/convert.py article.md --style dark-tech --width 900

# 清新商务风格（适合商务演示）
python3 scripts/convert.py article.md --style fresh-business --width 900

# 手绘草图风格（适合头脑风暴）
python3 scripts/convert.py article.md --style hand-drawn --width 900

# 渐变现代风格（适合产品展示）
python3 scripts/convert.py article.md --style gradient-modern --width 900
```

### 风格主题参考

| 风格 | 名称 | 适用场景 | 特点 |
|------|------|----------|------|
| `dark-tech` | 深色科技 | 技术架构图 | 深色背景、霓虹强调色 |
| `fresh-business` | 清新商务 | 商务演示 | 白色背景、蓝色强调 |
| `hand-drawn` | 手绘草图 | 头脑风暴 | 纸张质感、手绘字体 |
| `gradient-modern` | 渐变现代 | 产品展示 | 渐变背景、鲜艳色彩 |

### 作为 Claude Skill 使用

```bash
# 在 Claude Code 中直接使用
mermaid-to-png article.md --width 900 --replace

# 使用风格主题
mermaid-to-png article.md --style dark-tech --width 900
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入的 Markdown 文件路径 | 必填 |
| `--output-dir` | 图片输出目录 | `./output` |
| `--style` | 风格主题 | 无 |
| `--width` | 图片宽度（像素） | `1200` |
| `--background` | 背景色 | `white` |
| `--format` | 输出格式（png/svg） | `png` |
| `--replace` | 替换 Mermaid 代码为图片引用 | `false` |

## 示例

### 输入文件（article.md）

```markdown
# 系统架构

## 整体架构

```mermaid
graph TB
    A[客户端] --> B[API 网关]
    B --> C[服务 A]
    B --> D[服务 B]
```
```

### 转换命令

```bash
python3 scripts/convert.py article.md --style dark-tech --width 900 --replace
```

### 输出

```
output/
├── diagram_1_a3f7d2e1.png
└── article_converted.md
```

## 常见问题

### mermaid-cli not found

```bash
npm install -g @mermaid-js/mermaid-cli
```

### 中文显示为方框

**macOS:**
```bash
brew install --cask font-noto-sans-cjk
```

**Linux:**
```bash
sudo apt-get install fonts-noto-cjk
```

### 风格主题不生效

```bash
npm update -g @mermaid-js/mermaid-cli
```

## 资源

- [`scripts/convert.py`](scripts/convert.py) - 主转换脚本
- [`scripts/styles.py`](scripts/styles.py) - 风格主题定义

## 许可证

MIT License
