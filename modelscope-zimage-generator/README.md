# English | [中文](README-zh.md)

# ModelScope Z-Image Generator Skill

A skill for coding agents such as [Claude Code](https://claude.ai/claude-code) that generates images with the ModelScope [Z-Image](https://modelscope.cn/models/Tongyi-MAI/Z-Image/summary) series.

## Features

- Supports multiple Z-Image models: Turbo and standard
- Async generation with polling
- Supports LoRA configuration, including single and multiple LoRAs
- Interactive API key setup on first run
- Secure API key storage with `0o600` permissions

## Supported Models

| Model | Description |
|------|------|
| `Tongyi-MAI/Z-Image-Turbo` | Default, optimized for speed |
| `Tongyi-MAI/Z-Image` | Better balance between quality and speed |

### Model Selection Rules

- If the user explicitly asks for "Z-Image-Turbo" -> use `Tongyi-MAI/Z-Image-Turbo`
- If the user explicitly asks for "Z-Image" -> use `Tongyi-MAI/Z-Image`
- Otherwise -> default to `Tongyi-MAI/Z-Image-Turbo`

## Installation

### Install from npm package

```bash
npx skills add haiyuan-ai/agent-skills --skill modelscope-zimage-generator
```

### Manual installation

```bash
# Clone or copy the skill directory
cp -r modelscope-zimage-generator ~/.claude/skills/
```

## Configuration

### Get an API Key

Get your API key from https://modelscope.cn/my/myaccesstoken.

### First Run

On first use, the script prompts for an API key and can save it to a config file.

### Manual Configuration

Config file:
```bash
mkdir -p ~/.config/modelscope
cat > ~/.config/modelscope/config.json << EOF
{"api_key": "ms-your-api-key"}
EOF
chmod 600 ~/.config/modelscope/config.json
```

Environment variable:
```bash
export MODELSCOPE_API_KEY="ms-your-api-key"
```

## Usage

### Use in Claude Code

Describe the request in natural language:

```
Generate an image of a golden cat
```

```
Use Z-Image to generate a cyberpunk city at night
```

```
Create a cover image for an article about AI technology
```

### Use the Python Script

```bash
# Use the default model
python scripts/generate_image.py "A golden cat" output.jpg

# Specify a model
python scripts/generate_image.py "A cat" output.jpg --model "Tongyi-MAI/Z-Image"

# Use a single LoRA
python scripts/generate_image.py "A cat" output.jpg --lora "liuhaotian/llava-lora"

# Use multiple LoRAs
python scripts/generate_image.py "A cat" output.jpg --loras '{"lora1": 0.6, "lora2": 0.4}'
```

## Command Reference

| Request | Command |
|---------|------|
| Generate an image | `python scripts/generate_image.py "prompt" output.jpg` |
| Use Z-Image | `python scripts/generate_image.py "prompt" output.jpg --model "Tongyi-MAI/Z-Image"` |
| Use LoRA | `python scripts/generate_image.py "prompt" output.jpg --lora "lora-id"` |
| Generate in parallel | Run multiple commands in the background and use `wait` |

## Documentation

- [`references/api-reference.md`](references/api-reference.md) - Full API parameter reference
- [`references/lora-config.md`](references/lora-config.md) - LoRA configuration guide
- [`references/troubleshooting.md`](references/troubleshooting.md) - Troubleshooting guide

## API Flow

```
1. POST /v1/images/generations (X-ModelScope-Async-Mode: true)
   -> returns task_id

2. GET /v1/tasks/{task_id} (X-ModelScope-Task-Type: image_generation)
   -> poll until SUCCEED or FAILED

3. Download output_images[0] and save it locally
```

## Troubleshooting

### API Key Not Found

```bash
# Set an environment variable
export MODELSCOPE_API_KEY="ms-your-key"

# Or create a config file
mkdir -p ~/.config/modelscope
echo '{"api_key": "ms-your-key"}' > ~/.config/modelscope/config.json
```

### Missing Python Modules

```bash
pip install requests pillow
```

### Other Issues

See [`references/troubleshooting.md`](references/troubleshooting.md) for more details.

## Resources

- [ModelScope](https://modelscope.cn/)
- [Z-Image model page](https://modelscope.cn/models/Tongyi-MAI/Z-Image/summary)
- [Get API key](https://modelscope.cn/my/myaccesstoken)

## License

MIT License
