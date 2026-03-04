# LoRA Configuration Guide

LoRA（Low-Rank Adaptation）配置指南。

## Single LoRA

使用单个 LoRA 模型：

```bash
python generate_image.py "A cat" output.jpg --lora "liuhaotian/llava-lora"
```

```json
{
  "loras": "liuhaotian/llava-lora"
}
```

## Multiple LoRAs

使用多个 LoRA 模型，权重必须总和为 1.0：

```bash
python generate_image.py "A cat" output.jpg --loras '{"lora1": 0.6, "lora2": 0.4}'
```

```json
{
  "loras": {
    "liuhaotian/llava-lora": 0.6,
    "another/lora": 0.4
  }
}
```

## Weight Rules

| 配置 | 是否有效 |
|------|---------|
| `{"lora1": 0.5, "lora2": 0.5}` | ✅ 有效 |
| `{"lora1": 0.7, "lora2": 0.3}` | ✅ 有效 |
| `{"lora1": 0.6, "lora2": 0.6}` | ❌ 无效（和 > 1.0） |
| `{"lora1": 0.4, "lora2": 0.4}` | ❌ 无效（和 < 1.0） |

## Finding LoRAs

在 ModelScope 平台查找 LoRA 模型：
- 访问 https://modelscope.cn/models
- 搜索 "lora" 关键词
- 复制模型 ID（格式：`owner/repo`）

## Examples

### Art Style LoRA

```bash
python generate_image.py "A landscape" output.jpg \
  --lora "artist/style-lora"
```

### Character LoRA

```bash
python generate_image.py "A character portrait" output.jpg \
  --lora "character/anime-lora"
```

### Combined LoRAs

```bash
python generate_image.py "A character in landscape" output.jpg \
  --loras '{"character/lora": 0.6, "background/lora": 0.4}'
```
