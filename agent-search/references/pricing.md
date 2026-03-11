# 搜索服务 API 定价参考

各搜索服务的免费额度和定价信息汇总。

## 免费额度对比

| 服务 | 类型 | 免费额度 | 获取地址 |
|-----|------|---------|---------|
| Tavily | AI 搜索 | 1,000 credits/month | https://tavily.com |
| Brave Search API | Web 搜索 | 需绑卡；每月赠送 $5 credits，约 1000 次调用 | https://brave.com/search/api/ |
| Exa | 语义搜索 | 每月最多 1,000 requests 免费；部分账号可能有额外 promo balance | https://dashboard.exa.ai |
| Jina | 内容提取 | 1M tokens/day | https://jina.ai/api-dashboard |
| Gemini | Embedding | 免费 | https://aistudio.google.com/apikey |

## 付费定价

### Tavily
- 有明确 free plan
- 免费额度: `1,000 API credits/month`
- 注册门槛低，适合作为默认主搜索引擎
- 本地 usage 统计当前按请求次数近似，不等于官方 credits 账单

### Exa
- 当前公开 pricing 页显示每月最多 `1,000 requests` 免费
- 申请 API key 不需要绑定银行卡
- 部分新账号可能会额外获得 promo balance
- 实际可用额度请以 Exa 控制台 billing / balance 页面为准
- 更适合作为语义补强源，而不是普通用户的默认主引擎

### Brave Search API
- 不是完全免费 API key；需要先绑定银行卡
- 每月自动赠送 `$5` credits
- 按当前粗略成本估算，约可调用 `1000` 次
- 适合原始网页搜索、新闻和官方网页命中

### Jina
- 免费: 1M tokens/day
- Pro: $9.90/month (10M tokens/day)

### Gemini (Embedding)
- 免费: 1,500 RPM, 100 RPD
- 付费: $0.0001/1K tokens
