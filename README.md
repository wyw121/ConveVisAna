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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可

MIT License

---

**开始你的对话分析之旅！** 🚀
