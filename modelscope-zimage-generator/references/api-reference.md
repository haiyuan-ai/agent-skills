# API Reference

ModelScope Z-Image API 完整参数参考。

## Base URL

```
https://api-inference.modelscope.cn/
```

## Endpoints

### 1. Submit Generation Task

```http
POST /v1/images/generations
Content-Type: application/json
X-ModelScope-Async-Mode: true
Authorization: Bearer {api_key}
```

**Request Body:**

```json
{
  "model": "Tongyi-MAI/Z-Image-Turbo",
  "prompt": "A golden cat in sunset",
  "loras": "liuhaotian/llava-lora",
  "n": 1,
  "size": "1024x1024"
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | 模型 ID |
| `prompt` | string | Yes | - | 文本提示词 |
| `loras` | string/object | No | - | LoRA 配置 |
| `n` | integer | No | 1 | 生成图片数量 |
| `size` | string | No | 1024x1024 | 图片尺寸 |

**Response:**

```json
{
  "task_id": "task-123456789"
}
```

### 2. Poll Task Status

```http
GET /v1/tasks/{task_id}
X-ModelScope-Task-Type: image_generation
Authorization: Bearer {api_key}
```

**Response:**

```json
{
  "task_status": "SUCCEED",
  "output_images": ["https://..."],
  "error": null
}
```

**Status Values:**

| Status | Description |
|--------|-------------|
| `PENDING` | 任务等待中 |
| `RUNNING` | 任务运行中 |
| `SUCCEED` | 任务成功 |
| `FAILED` | 任务失败 |

## Headers

| Header | Value | Description |
|--------|-------|-------------|
| `Authorization` | `Bearer {api_key}` | API 认证 |
| `Content-Type` | `application/json` | 请求格式 |
| `X-ModelScope-Async-Mode` | `true` | 启用异步模式 |
| `X-ModelScope-Task-Type` | `image_generation` | 任务类型 |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | 请求参数错误 |
| 401 | API Key 无效 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

## Rate Limits

- Turbo 模型：更高并发
- 标准模型：标准速率

## Best Practices

1. **始终使用异步模式** - 图片生成需要时间
2. **合理设置轮询间隔** - 建议 5 秒
3. **设置超时限制** - 避免无限等待
4. **保存 API Key 安全** - 使用配置文件
