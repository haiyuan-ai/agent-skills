# Troubleshooting

故障排查指南。

## API Key 问题

### "API key not found"

**症状：** 脚本提示找不到 API Key

**解决方案：**

```bash
# 方案 1：环境变量
export MODELSCOPE_API_KEY="ms-your-api-key"

# 方案 2：配置文件
mkdir -p ~/.config/modelscope
cat > ~/.config/modelscope/config.json << EOF
{"api_key": "ms-your-api-key"}
EOF
chmod 600 ~/.config/modelscope/config.json
```

### "Invalid API key"

**症状：** API Key 格式错误或无效

**解决方案：**
1. 确认 API Key 以 `ms-` 开头
2. 访问 https://modelscope.cn/my/myaccesstoken 重新生成
3. 检查配置文件 JSON 格式是否正确

## 任务超时

### "Timeout: Image generation took too long"

**症状：** 任务执行超时

**可能原因：**
- 服务器负载高
- 提示词过于复杂
- 模型正在维护

**解决方案：**
1. 稍后重试
2. 简化提示词
3. 尝试使用 Turbo 模型

## 生成失败

### "Error submitting task"

**症状：** 提交任务失败

**可能原因：**
- API Key 无效
- 网络问题
- 模型 ID 错误

**解决方案：**
```bash
# 测试连接
curl -H "Authorization: Bearer ms-your-key" \
  https://api-inference.modelscope.cn/v1/models

# 检查模型 ID
python generate_image.py "test" test.jpg --model "Tongyi-MAI/Z-Image-Turbo"
```

### "Task failed"

**症状：** 任务状态变为 FAILED

**可能原因：**
- 提示词包含敏感内容
- 模型无法解析提示词
- 服务器错误

**解决方案：**
1. 修改提示词，移除敏感内容
2. 使用更清晰的描述
3. 联系 ModelScope 支持

## LoRA 问题

### LoRA 不生效

**症状：** 使用 LoRA 但生成结果无变化

**可能原因：**
- LoRA ID 错误
- LoRA 与模型不兼容
- 权重设置不当

**解决方案：**
1. 确认 LoRA ID 正确（`owner/repo` 格式）
2. 检查 LoRA 是否兼容 Z-Image 模型
3. 调整权重值

## 图片质量问题

### 图片模糊

**解决方案：**
1. 使用更高的分辨率设置
2. 优化提示词描述
3. 尝试不同模型版本

### 内容不符合预期

**解决方案：**
1. 添加更多细节描述
2. 使用负面提示词（如支持）
3. 多次生成选择最佳结果

## Python 环境问题

### ModuleNotFoundError: No module named 'requests'

**解决方案：**
```bash
pip install requests pillow
```

### Python 版本不兼容

**要求：** Python 3.7+

**检查版本：**
```bash
python --version
```
