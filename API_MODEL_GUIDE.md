# API 模型配置指南

## 🚨 当前问题

ChatAIAPI 返回 503 错误：
```
所有令牌分组下对于模型 gpt-4o-mini 均无可用渠道，请更换分组尝试
```

这说明：
1. **API 密钥额度可能用完**
2. **模型 `gpt-4o-mini` 在 ChatAIAPI 不可用**

---

## 💡 解决方案

### 方案 1: 更换支持的模型（推荐）

ChatAIAPI 通常支持以下模型：

#### DeepSeek 系列（成本低，性能好）
- `deepseek-chat` - 推荐！性价比高
- `deepseek-reasoner` - 推理能力强

#### 其他常见模型
- `gpt-3.5-turbo` - OpenAI 模型
- `gpt-4` - 高级模型（成本高）
- `claude-3-haiku` - Anthropic 模型（快速）
- `gemini-pro` - Google 模型

#### 修改方法：

编辑 `backend/core/evaluate_chats.py` 第 40 行：
```python
def __init__(
    self,
    data_folder: str,
    model: str = "deepseek-chat",  # 改这里！
    use_custom_api: bool = True
):
```

或者在前端调用时指定模型（如果前端有模型选择器）。

---

### 方案 2: 检查 API 额度

1. 登录你的 ChatAIAPI 账户
2. 查看余额和可用模型
3. 如果额度用完，需要充值

---

### 方案 3: 使用原生 OpenAI API

如果有 OpenAI API Key：

1. 编辑 `backend/.env`：
   ```env
   OPENAI_API_KEY=sk-your-real-openai-key
   ```

2. 在 API 调用时设置 `use_custom_api=False`

---

## 🔧 快速修复步骤

### 立即尝试 DeepSeek 模型：

1. **编辑文件** `backend/core/evaluate_chats.py`:
   ```python
   # 第 40 行附近
   model: str = "deepseek-chat",  # 改成这个
   ```

2. **重启后端**:
   ```bash
   # 在后端终端按 Ctrl+C
   cd d:\repositories\ConveVisAna\backend
   python start_server.py
   ```

3. **刷新前端页面**，重新上传文件并点击 "Run Quality Evaluation"

---

## 📊 模型对比

| 模型 | 成本 | 速度 | 质量 | 推荐度 |
|------|------|------|------|--------|
| `deepseek-chat` | ⭐ 低 | ⭐⭐⭐ 快 | ⭐⭐⭐⭐ 优秀 | ⭐⭐⭐⭐⭐ |
| `gpt-3.5-turbo` | ⭐⭐ 中 | ⭐⭐⭐ 快 | ⭐⭐⭐ 良好 | ⭐⭐⭐⭐ |
| `gpt-4o-mini` | ⭐⭐ 中 | ⭐⭐ 中 | ⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ |
| `gpt-4` | ⭐⭐⭐⭐⭐ 高 | ⭐ 慢 | ⭐⭐⭐⭐⭐ 最佳 | ⭐⭐ |
| `claude-3-haiku` | ⭐⭐ 中 | ⭐⭐⭐⭐ 很快 | ⭐⭐⭐ 良好 | ⭐⭐⭐⭐ |

---

## 🛠️ 技术细节

### 模型在代码中的使用位置：

1. **评估器初始化**: `backend/core/evaluate_chats.py:40`
2. **流程分析**: `backend/core/conversation_flow_analyzer.py:221`
3. **自定义 LLM**: `backend/core/custom_llm.py:214`

### API 端点配置：

`backend/api/main.py` 的评估端点默认使用 `gpt-4o-mini`：
```python
async def evaluate_quality(
    file: UploadFile = File(...),
    max_qa_pairs: int = 3,
    model: str = "gpt-4o-mini"  # 这里也可以改
):
```

---

## ❓ 常见问题

**Q: 为什么我的 API Key 不能用了？**
- A: 可能是额度用完，或者 ChatAIAPI 的 gpt-4o-mini 渠道临时不可用

**Q: 换成 deepseek-chat 会影响评估质量吗？**
- A: DeepSeek 性能很好，适合对话质量评估，性价比更高

**Q: 如何查看我的 API 剩余额度？**
- A: 登录 https://www.chataiapi.com/ 查看账户余额

**Q: 前端已经显示部分结果，为什么崩溃了？**
- A: 已修复！现在前端会安全处理失败的指标，显示"评估失败或数据缺失"

---

## ✅ 修复确认

修复前端后，即使部分指标评估失败，也会显示：
- ✅ 成功的指标正常显示分数
- ⚠️ 失败的指标显示"评估失败或数据缺失"
- 📊 雷达图仍然可以渲染（失败的指标分数为 0）

不会再出现 "Cannot read properties of undefined" 错误！
