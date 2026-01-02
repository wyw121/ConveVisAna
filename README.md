# ConveVisAna - ChatGPT 对话分析工具 🚀

> AI 驱动的 ChatGPT 对话质量评估与流程分析平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📋 项目简介

**ConveVisAna** 提供专业的 ChatGPT 对话分析功能：

- 🤖 **AI 质量评估** - 6大维度评估（相关性、有用性、连贯性、同理心、毒性、偏见）
- 📊 **对话流程分析** - 识别高价值问题、话题转移、问题分类
- 🌐 **RESTful API** - 完整的后端接口，易于前端集成
- 🔧 **多模型支持** - GPT-4o-mini、Claude、DeepSeek等

---

## 🏗️ 项目结构

```
ConveVisAna/
├── backend/                 # 后端代码
│   ├── api/                # FastAPI 接口
│   │   └── main.py        # API 入口
│   ├── core/              # 核心分析模块
│   │   ├── data_loader.py
│   │   ├── custom_llm.py
│   │   ├── evaluate_chats.py
│   │   └── conversation_flow_analyzer.py
│   ├── utils/             # 工具函数
│   ├── start_server.py    # 快速启动
│   └── requirements.txt
├── docs/                  # 项目文档
│   ├── QUICKSTART.md
│   ├── FLOW_ANALYSIS_GUIDE.md
│   └── 前端迁移方案.md
├── tests/                 # 测试文件
├── scripts/               # 脚本和示例
└── README.md
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r backend/requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env` 并配置：

```env
CHATAIAPI_KEY=sk-your-api-key
CHATAIAPI_BASE_URL=https://www.chataiapi.com/v1
```

### 3. 启动服务

```bash
cd backend
python start_server.py
```

访问:
- 🌐 API: http://localhost:8000
- 📚 文档: http://localhost:8000/docs

---

## 📖 使用方式

### 方式 1: API 调用

```bash
# 质量评估
curl -X POST "http://localhost:8000/api/evaluate-quality?max_qa_pairs=3" \
  -F "file=@conversations.json"

# 流程分析
curl -X POST "http://localhost:8000/api/analyze-flow" \
  -F "file=@conversations.json"
```

### 方式 2: Python 脚本

```python
from backend.core import ChatQualityEvaluator

evaluator = ChatQualityEvaluator(
    data_folder="path/to/data",
    model="gpt-4o-mini",
    use_custom_api=True
)
results = evaluator.evaluate_conversation(max_qa_pairs=3)
```

---

## 🎯 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/evaluate-quality` | POST | 对话质量评估 |
| `/api/analyze-flow` | POST | 对话流程分析 |
| `/api/generate-report` | POST | 生成报告 |

完整文档: http://localhost:8000/docs

---

## 📊 前端集成

本项目提供完整 RESTful API，支持任何前端框架集成。

详见: [docs/前端迁移方案.md](docs/前端迁移方案.md)

```typescript
// 前端调用示例
async function evaluateQuality(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    'http://localhost:8000/api/evaluate-quality?max_qa_pairs=3',
    { method: 'POST', body: formData }
  );
  
  return response.json();
}
```

---

## 🔧 支持的模型

| 模型 | 成本 | 速度 | 推荐场景 |
|------|------|------|---------|
| gpt-4o-mini | ⭐ | ⭐⭐⭐ | 推荐，性价比高 |
| deepseek-chat | ⭐⭐ | ⭐⭐⭐ | 中文友好 |
| claude-3-haiku | ⭐⭐ | ⭐⭐ | 质量高 |
| gpt-4o | ⭐⭐⭐ | ⭐⭐ | 最准确 |

---

## 🎓 文档

- 📖 [快速开始](docs/QUICKSTART.md)
- 📊 [流程分析指南](docs/FLOW_ANALYSIS_GUIDE.md)
- 🔗 [前端集成方案](docs/前端迁移方案.md)
- 📚 [DeepEval 文档](https://docs.deepeval.com/)

---

## 💡 核心优势

| 功能 | ConveVisAna | 其他工具 |
|------|-------------|---------|
| AI 质量评估 | ✅ 6大维度 | ❌ 基础统计 |
| 流程分析 | ✅ LLM驱动 | ⚠️ 规则匹配 |
| API 支持 | ✅ 完整 | ⚠️ 有限 |
| 模型选择 | ✅ 多模型 | ⚠️ 固定 |

---

## 🚧 未来计划

### 短期改进（优先级 P0）

#### 1. 后端请求间隔优化
**问题**: 硅基流动免费 API 存在 RPM 限制（~10请求/分钟），未实名认证时易触发 `403 RPM limit exceeded`

**改进方案**:
- 在评估指标之间添加智能请求间隔（6-10秒）
- 实现自适应速率控制（检测到 429/403 自动降速）
- 添加配置项 `EVALUATION_REQUEST_DELAY` 允许用户自定义间隔

**预期效果**: 避免 RPM 限制，确保 6 个评估指标全部完成

#### 2. 前端实时进度显示
**问题**: 评估过程中前端只显示"分析中..."，用户无法了解具体进度

**改进方案**:
- 实时显示当前评估的指标名称（如"正在评估：Relevancy..."）
- 显示已完成/总指标数进度条（如"进度: 4/6"）
- 展示每个指标的实时状态（✓完成 / ⏳进行中 / ❌失败）
- 显示每个指标的响应时间和得分

**预期效果**:
```
质量评估进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Relevancy     [完成] 100% (1.66秒)
✓ Helpfulness   [完成]  10% (2.91秒)  
✓ Coherence     [完成]  20% (1.08秒)
⏳ Empathy       [评估中...]
⚠ Toxicity      [待评估]
⚠ Bias          [待评估]

总进度: 3/6 (50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 3. 详细错误提示优化
**问题**: 错误提示不够清晰，用户不知道如何解决问题

**改进方案**:
- 识别 RPM 限制错误，显示友好提示："检测到 API 速率限制，请完成实名认证或等待后重试"
- 提供解决方案链接（如硅基流动认证页面）
- 区分不同错误类型（网络错误、认证错误、速率限制等）
- 添加"重试"按钮，自动重新评估失败的指标

**预期效果**:
```
⚠️ 评估部分失败 (4/6 成功)

失败原因:
• Toxicity: RPM 速率限制
  → 解决方案: 完成实名认证 [立即认证]
  → 或者: 等待 1 分钟后重试 [重试]
  
• Bias: RPM 速率限制  
  → 解决方案: 同上
```

### 中期改进（优先级 P1）

- **流式响应**: 使用 WebSocket 或 SSE 实时推送评估日志
- **指标选择器**: 允许用户选择评估哪些维度（减少 API 调用）
- **评估队列**: 支持批量评估多个对话文件
- **结果缓存**: 避免重复评估相同内容

### 长期改进（优先级 P2）

- **本地模型支持**: 集成 Ollama 等本地 LLM，完全免费无限制
- **自定义评估维度**: 用户自定义评估标准和提示词
- **评估报告导出**: PDF/Excel 格式导出详细报告
- **数据可视化增强**: 更丰富的图表和趋势分析

---

## 💡 已知限制

### 硅基流动 API 限制
- **免费账户**: 约 10 RPM（每分钟10个请求）
- **已实名认证**: 约 60 RPM
- **建议**: 完成实名认证以获得更好体验
- **认证链接**: https://cloud.siliconflow.cn/account

### 模型选择建议
- **推荐**: `Qwen/Qwen2.5-7B-Instruct` - 100%测试通过，JSON格式完美
- **备选**: `Qwen/Qwen2-7B-Instruct` - 速度更快（1.01秒）
- **不推荐**: `DeepSeek-R1` - 输出包含思维链，JSON兼容性差

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可

MIT License

---

**开始你的对话分析之旅！** 🚀
