# ConveVisAna – ChatGPT 对话深度分析平台 🚀

> AI 驱动的对话质量评估、流程分析与认知层级洞察（布鲁姆认知编码 + 信息增益推算）

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

---

## 📌 项目亮点与个人贡献

- **重新实现 Deep Analysis（核心创新）**
  - 布鲁姆认知编码：基于对话问题类型的启发式映射，6 个认知层级可视化（Remember→Understand→Apply→Analyze→Evaluate→Create）。
  - 信息增益推算：IG = DKL(P∥Q) × R × C，前端纯数学计算（0 额外 API 调用，<30ms）。
  - 对话流分析：基于 question_type_counts 生成 P 分布，结合基线 Q 分布与质量因子（relevancy/toxicity）。
- **前端改造**
  - Dashboard 集成 BloomTaxonomyCard 与 InfoGainCard，数据来自已有质量评估与流程分析 API。
  - 主页与 Demo 同步视觉，轮播组件固定 16:9 防比例跳动，资源改为本地加载。
  - Deep Analysis 流程卡片：质量评估 → 流程分析 → 布鲁姆认知编码 → 信息增益推算。
- **文档与可复现性**
  - 完整撰写 BLOOM_INFOGAIN_DESIGN / BLOOM_HEURISTIC_EXAMPLE / INFOGAIN_HEURISTIC_EXAMPLE，说明算法、公式、示例与代码。
  - 新增 DASHBOARD_BLOOM_INFOGAIN_TEST，给出端到端验证步骤。

**参考与来源**
- 原项目参考：https://github.com/meetpateltech/convelyze
- 论文思路参考：Bloom's Taxonomy；KL Divergence / Information Gain；DeepEval 结构化评估。

---

## 🏗️ 项目结构（精简版）

```
ConveVisAna/
├── backend/
│   ├── api/main.py                  # FastAPI 入口与路由
│   ├── core/
│   │   ├── evaluate_chats.py        # 质量评估管线（DeepEval 风格）
│   │   ├── conversation_flow_analyzer.py  # 对话流程/问题类型分析
│   │   ├── custom_llm.py            # 模型/供应商封装
│   │   └── data_loader.py
│   ├── start_server.py              # 后端启动脚本
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # 主页（突出 Deep Analysis）
│   │   ├── dashboard/page.tsx       # Dashboard 主页面
│   │   └── demo/page.tsx            # Demo 页面（全量组件示例）
│   ├── components/deep-analysis/
│   │   ├── DeepAnalysisPanel.tsx    # 深度分析主面板
│   │   ├── BloomTaxonomyCard.tsx    # 布鲁姆认知编码可视化
│   │   ├── InfoGainCard.tsx         # 信息增益推算可视化
│   │   ├── QualityMetricsCard.tsx   # 质量评估结果
│   │   └── FlowAnalysisSection.tsx  # 流程分析结果
│   └── public/                      # 本地图片资源（轮播/步骤）
│
├── docs/
│   ├── BLOOM_INFOGAIN_DESIGN.md     # 方案设计（三种策略）
│   ├── BLOOM_HEURISTIC_EXAMPLE.md   # 布鲁姆启发式实例
│   ├── INFOGAIN_HEURISTIC_EXAMPLE.md# 信息增益推算实例
│   └── DASHBOARD_BLOOM_INFOGAIN_TEST.md # Dashboard 测试指南
└── README.md
```

---

## 🚀 快速使用指南

### 后端（FastAPI）
```bash
# 1) 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows
# source .venv/bin/activate      # macOS/Linux

# 2) 安装依赖
pip install -r backend/requirements.txt

# 3) 复制配置
cp backend/.env.example backend/.env
# 填写 API Key / Base URL（如硅基流动或自有 OpenAI 兼容端）

# 4) 启动服务
cd backend
python start_server.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 前端（Next.js 14）
```bash
cd frontend
npm install
npm run dev
# 默认 3000 端口，如被占用会自动切到 3001
```

### 深度分析（Dashboard）
1. 打开浏览器访问 `http://localhost:3000/dashboard`（或 3001）。
2. 上传 conversations.json。
3. 依次点击「开始质量评估」和「开始流程分析」。
4. 自动出现：
   - 布鲁姆认知编码卡片（6 层级分布 + 代表性样例）。
   - 信息增益推算卡片（DKL、R、C、IG 及 P vs Q 对比图）。

### API 直调（示例）
```bash
# 质量评估
curl -X POST "http://localhost:8000/api/evaluate-quality?max_qa_pairs=3" \
  -F "file=@conversations.json"

# 流程分析
curl -X POST "http://localhost:8000/api/analyze-flow" \
  -F "file=@conversations.json"
```

---

## 🔍 Deep Analysis 设计要点

- **布鲁姆认知编码（启发式）**
  - 输入：flowResult.turns[].question_type / question
  - 逻辑：question_type → Bloom Level 映射（6 层级），前端累加并可视化。
  - 特性：纯前端计算，0 额外 API，<10ms。

- **信息增益推算**
  - 公式：IG(P,Q) = DKL(P∥Q) × R × C
  - 输入：
    - P：流程分析的 question_type_counts 归一化
    - Q：预设基线分布（可调）
    - R：quality.metrics.relevancy.score
    - C：1 - quality.metrics.toxicity.score
  - 特性：纯数学计算，0 额外 API，<30ms，提供 P vs Q 可视化。

- **流程分析呈现**
  - 问题类型统计、轮次/长度、模式与情感等指标。
  - 与布鲁姆/信息增益联动：同一份 flowResult 直接驱动两张卡片。

- **模型与评估**
  - 推荐：Qwen/Qwen2.5-7B-Instruct（硅基流动），JSON 结构稳定。
  - 可替换其他 OpenAI 兼容模型，通过 custom_llm.py 配置。

---

## 🧭 我的主要贡献

1) **Deep Analysis 全量打通**：Dashboard 集成布鲁姆认知编码与信息增益推算，前端纯计算，0 额外 API。 
2) **算法落地与文档**：撰写 BLOOM_INFOGAIN_DESIGN / BLOOM_HEURISTIC_EXAMPLE / INFOGAIN_HEURISTIC_EXAMPLE，给出公式、示例与代码。 
3) **体验与性能**：
   - 轮播 16:9 固定，资源本地化，加载更快。
   - Hero/Features/Steps 区域重写，突出 Deep Analysis 与使用步骤。
4) **可复现性**：提供 DASHBOARD_BLOOM_INFOGAIN_TEST 测试指南，一键验证端到端流程。

---

## 📚 参考与致谢

- 原项目参考：https://github.com/meetpateltech/convelyze
- 理论基础：Bloom's Taxonomy；KL Divergence / Information Gain；DeepEval 结构化评估思路。

---

## 📄 许可

MIT License

---

**一键启动 Deep Analysis，获取认知层级与信息增益洞察！** 🚀
