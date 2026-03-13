---
name: modelscope-zimage-generator
description: |
  Generate images with ModelScope Z-Image models.
  Use for image generation, artwork, cover images, and LoRA-based variants.
  Supports async polling.
---

# ModelScope Z-Image Generator Skill

Generate images using ModelScope's Z-Image series models with async polling flow.

## When to Use This Skill

Use this skill when the user asks to:

- generate an image or illustration
- create artwork or a cover image
- use ModelScope Z-Image or Z-Image-Turbo explicitly
- generate multiple image variants
- apply a LoRA during generation

Common trigger phrases:
- English: `generate an image`, `create artwork`, `make a cover`, `use Z-Image`
- Chinese: `生成图片`, `画一张图`, `创建封面图`, `用 Z-Image`

## Core Workflow

### 1. Parse the Request

Identify the generation mode:
- text-to-image
- LoRA-assisted generation
- multi-image or batch generation

### 2. Choose the Model

Select the model based on the user's request:
- explicit `Z-Image-Turbo` -> `Tongyi-MAI/Z-Image-Turbo`
- explicit `Z-Image` -> `Tongyi-MAI/Z-Image`
- default -> `Tongyi-MAI/Z-Image-Turbo`

### 3. Run the Generator Script

```bash
cd /path/to/modelscope-zimage-generator
python scripts/generate_image.py "prompt" output.jpg
```

### 4. Return the Result

Tell the user what happened:
- success: return the output path
- failure: explain the error clearly

## Prerequisites

Before running:
1. **ModelScope API key**: obtain it from `https://modelscope.cn/my/myaccesstoken`
2. **Python environment**: requires `requests` and `PIL`
3. **Valid script path**: make sure `generate_image.py` exists

## Quick Command Mapping

| User Request | Command |
|-------------|---------|
| "Generate image" | `python scripts/generate_image.py "prompt" output.jpg` |
| "Use Z-Image" | `python scripts/generate_image.py "prompt" output.jpg --model "Tongyi-MAI/Z-Image"` |
| "With LoRA" | `python scripts/generate_image.py "prompt" output.jpg --lora "lora-id"` |

## Common Workflows

### Text-to-Image

```bash
python scripts/generate_image.py "A golden cat in sunset" golden_cat.jpg
```

### Specify Model

```bash
python scripts/generate_image.py "A cat" output.jpg --model "Tongyi-MAI/Z-Image"
```

### With LoRA

```bash
# Single LoRA
python scripts/generate_image.py "A cat" output.jpg --lora "liuhaotian/llava-lora"

# Multiple LoRAs (weights sum to 1.0)
python scripts/generate_image.py "A cat" output.jpg --loras '{"lora1": 0.6, "lora2": 0.4}'
```

### Batch Generation

```bash
# Generate multiple images in parallel
python scripts/generate_image.py "A cat" cat1.jpg &
python scripts/generate_image.py "A dog" dog1.jpg &
wait
```

## Resources

Read references only when needed:
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

- Default timeout is 5 minutes (60 polling attempts)
- Increase polling attempts or inspect the task status

### LoRA Not Working

- Check whether the LoRA ID is valid
- Make sure multiple LoRA weights sum to `1.0`
- Do not use `--lora` and `--loras` together
