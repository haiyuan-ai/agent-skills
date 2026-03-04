---
name: modelscope-zimage-generator
description: |
  Generate images using ModelScope Z-Image series models (Z-Image-Turbo, Z-Image, Z-Image-Edit).
  Use when user asks to generate images, create artwork, make cover images, or requests image generation.
  Supports async generation with polling, optional LoRA configurations, and reference images for editing.
---

# ModelScope Z-Image Generator Skill

Generate images using ModelScope's Z-Image series models with async polling flow.

## When to Use This Skill

| 场景 | 中文表达示例 | English Examples |
|------|------------|-----------------|
| **生成图片** | "生成一张图片"、"画一只猫"、"创建封面图" | "generate an image", "create a picture", "make a cover" |
| **艺术创作** | "画一幅画"、"创作艺术品" | "create artwork", "paint a picture" |
| **图片编辑** | "修改这张图"、"添加一个元素" | "edit this image", "add something to the picture" |
| **批量生成** | "多生成几张"、"并行生成" | "generate multiple", "parallel generation" |

## Core Workflow

### 1. 解析用户请求

确定生成需求：
- 文本生成图片：文生图
- 图片编辑：图生图（需要参考图）
- LoRA 定制：指定风格模型
- 批量生成：多张图片

### 2. 选择模型

根据用户指定选择模型：
- 用户明确说 "Z-Image-Turbo" → `Tongyi-MAI/Z-Image-Turbo`
- 用户明确说 "Z-Image" → `Tongyi-MAI/Z-Image`
- 默认 → `Tongyi-MAI/Z-Image-Turbo`

### 3. 构建并执行生成脚本

```bash
cd /Users/ningoo/.claude/skills/modelscope-zimage-generator/scripts
python generate_image.py "prompt" output.jpg
```

### 4. 返回结果

告知用户生成结果：
- 成功：返回文件路径 "Image saved to: /path/to/output.jpg"
- 失败：解释错误原因

## Prerequisites

执行前确认：
1. **ModelScope API Key** - 从 https://modelscope.cn/my/myaccesstoken 获取
2. **Python 环境** - 需要 `requests` 和 `PIL` 库
3. **脚本路径正确** - 确保 `generate_image.py` 存在

## Quick Command Mapping

| User Request | Command |
|-------------|---------|
| "Generate image" | `python generate_image.py "prompt" output.jpg` |
| "Use Z-Image" | `python generate_image.py "prompt" --model "Tongyi-MAI/Z-Image"` |
| "With LoRA" | `python generate_image.py "prompt" --lora "lora-id"` |
| "Edit image" | `python generate_image.py "prompt" --ref "input.jpg" output.jpg` |

## Common Workflows

### Text-to-Image

```bash
python generate_image.py "A golden cat in sunset" golden_cat.jpg
```

### Specify Model

```bash
python generate_image.py "A cat" output.jpg --model "Tongyi-MAI/Z-Image"
```

### With LoRA

```bash
# Single LoRA
python generate_image.py "A cat" output.jpg --lora "liuhaotian/llava-lora"

# Multiple LoRAs (weights sum to 1.0)
python generate_image.py "A cat" output.jpg --loras '{"lora1": 0.6, "lora2": 0.4}'
```

### Batch Generation

```bash
# Generate multiple images in parallel
python generate_image.py "A cat" cat1.jpg &
python generate_image.py "A dog" dog1.jpg &
wait
```

## Resources

详细参考：
- `references/api-reference.md` - API 完整参数
- `references/lora-config.md` - LoRA 配置指南
- `references/troubleshooting.md` - 故障排查

## Troubleshooting

### API Key Not Found

```bash
# Option 1: Environment variable
export MODELSCOPE_API_KEY="ms-your-key"

# Option 2: Config file
mkdir -p ~/.config/modelscope
cat > ~/.config/modelscope/config.json << EOF
{"api_key": "ms-your-key"}
EOF
```

### Task Timeout

- 默认超时 5 分钟（60 次轮询）
- 增加轮询次数或检查任务状态

### LoRA Not Working

- 检查 LoRA ID 是否正确
- 确认 LoRA 权重和为 1.0
