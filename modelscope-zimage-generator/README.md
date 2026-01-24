# ModelScope Z-Image Generator Skill

一个用于 [Claude Code](https://claude.ai/claude-code) 等Coding Agent的Skill，使用 ModelScope 免费的 [造相-Z-Image-Turbo](https://modelscope.cn/models/Tongyi-MAI/Z-Image-Turbo/summary?version=master) 系列模型生成图片。

## 功能特性

- 支持多个 Z-Image 模型（Turbo、Base、Edit）,目前默认Turbo，未来有可能扩展到Base和Edit，取决于Z-Image模型的发布时间
- 异步生成 + 轮询机制
- 支持多个 LoRA 配置
- 首次使用自动引导配置 API Key
- 安全的 API Key 输入（隐藏显示）
- 自动保存 API Key 到配置文件（权限 0o600）

## 支持的模型

| 模型 | 说明 |
|--------|------|
| `Tongyi-MAI/Z-Image-Turbo` | 默认，快速生成 |
| `Tongyi-MAI/Z-Image-Base` | 更高质量 |
| `Tongyi-MAI/Z-Image-Edit` | 图片编辑 |

## 安装

### 方法一：从 npm 包安装（推荐）

```bash
npx skills add haiyuan-ai/agent-skills --skill modelscope-zimage-generator
```

### 方法二：手动安装

1. 下载 `modelscope-zimage-generator` 文件
2. 复制到 Claude Code skills 目录：

```bash
# macOS/Linux
cp modelscope-zimage-generator ~/.claude/skills/

# Windows
copy modelscope-zimage-generator %USERPROFILE%\.claude\skills\
```

## 配置

### 获取 API Key

访问 https://modelscope.cn/my/myaccesstoken 获取你的 API Key。

### 首次使用

首次使用技能时，会自动提示你输入 API Key：

```
ModelScope API key not found.
Get your API key from: https://modelscope.cn/my/myaccesstoken

Enter your ModelScope API key (input will be hidden):
```

输入后可以选择是否保存到配置文件，下次使用无需再次输入。

### 手动配置（可选）

**配置文件方式：**
```bash
mkdir -p ~/.config/modelscope
cat > ~/.config/modelscope/config.json << EOF
{
  "api_key": "ms-your-api-key-here"
}
EOF
```

**环境变量方式：**
```bash
export MODELSCOPE_API_KEY="ms-your-api-key-here"
```

## 使用方法

### 在 Claude Code/OpenCode等Coding Agnet 中使用

直接用自然语言描述你想要生成的图片：

```
用魔搭生成图片：一只在雪地里玩耍的金色小猫
```

```
生成一张赛博朋克风格的未来城市夜景图
```

### 使用 Python 脚本

```bash
# 使用默认模型 Z-Image-Turbo
python generate_image.py "A golden cat" output.jpg

# 指定使用 Z-Image-Base 模型
python generate_image.py "A golden cat" output.jpg "Tongyi-MAI/Z-Image-Base"
```

### LoRA 支持

单个 LoRA：

```python
"loras": "<lora-repo-id>"
```

多个 LoRA（权重总和需为 1.0）：

```python
"loras": {"<lora-id1>": 0.6, "<lora-id2>": 0.4}
```

## API 工作流程

1. 提交生成请求（设置 `X-ModelScope-Async-Mode: true`）
2. 接收 `task_id`
3. 轮询 `/v1/tasks/{task_id}`（设置 `X-ModelScope-Task-Type: image_generation`）
4. 等待状态为 `SUCCEED` 或 `FAILED`
5. 从 `output_images[0]` 下载图片

## 许可证

MIT License
