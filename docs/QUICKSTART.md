# ChatAIAPI 快速开始指南

## 📝 你的 API 已配置好！

API Key: `sk-imaEI6SqImBTTfAn8wvPiIN5oHelnY0iRbPe4CKLrDqe4pEV`  
基础 URL: `https://www.chataiapi.com/v1`

## 🚀 三步开始使用

### 1️⃣ 安装依赖
```powershell
pip install -r requirements.txt
```

### 2️⃣ 配置环境
```powershell
# 复制配置文件(API Key 已预设)
Copy-Item .env.example .env
```

### 3️⃣ 运行评估
```powershell
# 测试 API 连接
python custom_llm.py

# 运行评估(评估前3个对话)
python evaluate_chats.py
```

## ✨ 支持的模型

### OpenAI 模型 (推荐)
- `gpt-4o-mini` ⭐ - 便宜快速，适合大量评估
- `gpt-4o` - 更准确，成本稍高
- `gpt-4-turbo` - 平衡选择

### Claude 模型
- `claude-3-haiku-20240307` - 性价比高
- `claude-3-5-sonnet-20240620` - 高质量评估

## 💡 使用示例

```python
# 使用 GPT-4o-mini (推荐)
evaluator = ChatQualityEvaluator(
    data_folder,
    model='gpt-4o-mini',
    use_custom_api=True
)

# 使用 Claude Haiku (便宜)
evaluator = ChatQualityEvaluator(
    data_folder,
    model='claude-3-haiku-20240307',
    use_custom_api=True
)

# 评估前 5 个对话
results = evaluator.evaluate_conversation(max_qa_pairs=5)
```

## 💰 成本参考

| 模型 | 每个问答对 | 100个问答对 |
|------|-----------|------------|
| gpt-4o-mini | ¥0.005-0.015 | ¥0.5-1.5 |
| claude-3-haiku | ¥0.003-0.010 | ¥0.3-1.0 |
| gpt-4o | ¥0.05-0.15 | ¥5-15 |

## 🔧 常见调整

### 评估更多对话
```python
results = evaluator.evaluate_conversation(max_qa_pairs=20)
```

### 只评估特定指标(更快更便宜)
```python
results = evaluator.evaluate_conversation(
    max_qa_pairs=10,
    selected_metrics=['relevancy', 'helpfulness']
)
```

### 切换模型
```python
# 在 evaluate_chats.py 中修改
evaluator = ChatQualityEvaluator(
    data_folder,
    model='claude-3-haiku-20240307',  # 改成你想用的模型
    use_custom_api=True
)
```

## ❓ 遇到问题?

1. **API 连接失败**: 运行 `python custom_llm.py` 测试连接
2. **评估太慢**: 减少 `max_qa_pairs` 或使用更少的指标
3. **成本太高**: 使用 `gpt-4o-mini` 或 `claude-3-haiku`

详细文档请查看 `README.md`
