# ModelScope Z-Image Generator Skill

一个用于 [Claude Code](https://claude.ai/claude-code) 等 Coding Agent 的 Skill，使用 ModelScope [Z-Image](https://modelscope.cn/models/Tongyi-MAI/Z-Image/summary) 系列模型生成图片。

## 功能特性

- 支持多个 Z-Image 模型（Turbo、标准版、Edit）
- 异步生成 + 轮询机制
- 支持 LoRA 配置（单个/多个）
- 自动引导配置 API Key
- 安全的 API Key 存储（权限 0o600）

## 支持的模型

| 模型 | 说明 |
|------|------|
| `Tongyi-MAI/Z-Image-Turbo` | 默认，快速生成 |
| `Tongyi-MAI/Z-Image` | 平衡质量和速度 |
| `Tongyi-MAI/Z-Image-Edit` | 图片编辑 |

### 模型选择规则

- 用户明确说 "Z-Image-Turbo" → `Tongyi-MAI/Z-Image-Turbo`
- 用户明确说 "Z-Image" → `Tongyi-MAI/Z-Image`
- 默认 → `Tongyi-MAI/Z-Image-Turbo`

## 安装

### 从 npm 包安装（推荐）

```bash
npx skills add haiyuan-ai/agent-skills --skill modelscope-zimage-generator
```

### 手动安装

```bash
# 克隆或下载仓库
cp -r modelscope-zimage-generator ~/.claude/skills/
```

## 配置

### 获取 API Key

访问 https://modelscope.cn/my/myaccesstoken 获取你的 API Key。

### 首次使用

首次使用时会自动提示输入 API Key，并可选择保存到配置文件。

### 手动配置

**配置文件方式：**
```bash
mkdir -p ~/.config/modelscope
cat > ~/.config/modelscope/config.json << EOF
{"api_key": "ms-your-api-key"}
EOF
chmod 600 ~/.config/modelscope/config.json
```

**环境变量方式：**
```bash
export MODELSCOPE_API_KEY="ms-your-api-key"
```

## 使用方法

### 在 Claude Code 中使用

直接用自然语言描述：

```
生成一张金色的猫的图片
```

```
用 Z-Image 模型生成一张赛博朋克风格的城市夜景
```

```
创建一个文章封面图，主题是 AI 科技
```

### 使用 Python 脚本

```bash
# 使用默认模型
python generate_image.py "A golden cat" output.jpg

# 指定模型
python generate_image.py "A cat" output.jpg --model "Tongyi-MAI/Z-Image"

# 使用 LoRA
python generate_image.py "A cat" output.jpg --lora "liuhaotian/llava-lora"

# 使用多个 LoRA
python generate_image.py "A cat" output.jpg --loras '{"lora1": 0.6, "lora2": 0.4}'
```

## 命令参考

| 用户请求 | 命令 |
|---------|------|
| 生成图片 | `python generate_image.py "prompt" output.jpg` |
| 指定模型 | `python generate_image.py "prompt" --model "Tongyi-MAI/Z-Image"` |
| 使用 LoRA | `python generate_image.py "prompt" --lora "lora-id"` |
| 批量生成 | 并行执行多个命令 + `wait` |

## 详细文档

- [`references/api-reference.md`](references/api-reference.md) - API 完整参数
- [`references/lora-config.md`](references/lora-config.md) - LoRA 配置指南
- [`references/troubleshooting.md`](references/troubleshooting.md) - 故障排查

## API 工作流程

```
1. POST /v1/images/generations (X-ModelScope-Async-Mode: true)
   → 返回 task_id

2. GET /v1/tasks/{task_id} (X-ModelScope-Task-Type: image_generation)
   → 轮询直到 SUCCEED 或 FAILED

3. 下载 output_images[0] 保存为本地文件
```

## 故障排查

### API Key 未找到

```bash
# 设置环境变量
export MODELSCOPE_API_KEY="ms-your-key"

# 或创建配置文件
mkdir -p ~/.config/modelscope
echo '{"api_key": "ms-your-key"}' > ~/.config/modelscope/config.json
```

### 模块缺失

```bash
pip install requests pillow
```

### 其他问题

详见 [`references/troubleshooting.md`](references/troubleshooting.md)

## 资源链接

- [ModelScope 官网](https://modelscope.cn/)
- [Z-Image 模型页面](https://modelscope.cn/models/Tongyi-MAI/Z-Image/summary)
- [获取 API Key](https://modelscope.cn/my/myaccesstoken)

## 许可证

MIT License
