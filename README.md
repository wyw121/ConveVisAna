# ConveVisAna – ChatGPT 对话深度分析平台 🚀

> AI 驱动的对话质量评估、流程分析与认知层级洞察（布鲁姆认知编码 + 信息增益推算）

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

![Dashboard Overview](./frontend/public/dashboard.png)

---

## 📌 项目概述与理论复现

### 核心目标
本项目基于论文 **StuGPTViz: A Visual Analytics Approach to Understand Student-ChatGPT Interactions** 的核心思想，复现并实现了以下理论框架：

### 🎯 论文理论实现

#### 1. **对话流程分析（Conversation Flow Analysis）**
- **理论来源**：StuGPTViz 论文中的对话交互模式识别
- **实现方法**：
  - 自动识别问题类型（澄清性、深入性、情感性等）
  - 统计对话轮次、消息长度、话题转移模式
  - 生成问题类型分布 (question_type_counts)
- **技术支持**：基于 Convelyze 可视化框架 + 自研分析引擎

#### 2. **布鲁姆认知层级编码（Bloom's Taxonomy Mapping）**
- **理论来源**：Bloom's Taxonomy 认知分类理论（6 层级）
- **实现方法**：
  - 启发式映射：question_type → Bloom Level
  - 认知层级：Remember（记忆）→ Understand（理解）→ Apply（应用）→ Analyze（分析）→ Evaluate（评估）→ Create（创造）
  - 可视化：雷达图展示认知层级分布 + 代表性样例
- **创新点**：前端实时计算，0 额外 API 开销

#### 3. **信息增益评估（Information Gain Estimation）**
- **理论来源**：KL Divergence (Kullback-Leibler Divergence) 信息论
- **核心公式**：IG(P, Q) = DKL(P∥Q) × R × C
  - **P**：当前对话的问题类型分布（实际分布）
  - **Q**：基线分布（预期分布，可配置）
  - **R**：相关性因子（Relevancy Score，来自质量评估）
  - **C**：内容质量因子（1 - Toxicity Score）
- **意义**：量化对话相对于基线的信息增益，评估学习效果
- **实现特点**：纯数学计算，<30ms，支持 P vs Q 对比可视化

#### 4. **对话质量评估（Quality Metrics）**
- **理论来源**：DeepEval 结构化评估框架
- **评估维度**：
  - Relevancy（相关性）：回答是否切题
  - Toxicity（毒性）：内容是否有害
  - Bias（偏见）：是否存在偏见
  - Hallucination（幻觉）：是否捏造事实
- **技术实现**：硅基流动 API + Qwen/Qwen2.5-7B-Instruct 模型

### 🔬 研究贡献
1. **完整复现论文核心思想**：从对话流分析到认知编码，再到信息增益评估
2. **算法文档化**：撰写 BLOOM_INFOGAIN_DESIGN、启发式示例文档，公式推导完整
3. **端到端验证**：提供测试指南 (DASHBOARD_BLOOM_INFOGAIN_TEST)，确保可复现性
4. **工程化实现**：基于 Convelyze + DeepEval，构建完整的分析与可视化系统

### 📖 参考基础
- **论文**：StuGPTViz: A Visual Analytics Approach to Understand Student-ChatGPT Interactions
- **前端框架**：Convelyze (https://github.com/meetpateltech/convelyze)
- **评估框架**：DeepEval (https://deepeval.com/)
- **API 服务**：硅基流动 (SiliconFlow)

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

## 📸 功能展示

### 使用步骤

<div align="center">
  <img src="./frontend/public/step-1.png" width="30%" alt="Step 1"/>
  <img src="./frontend/public/step-2.png" width="30%" alt="Step 2"/>
  <img src="./frontend/public/step-3.png" width="30%" alt="Step 3"/>
</div>

### Deep Analysis 高级模式

![Advanced Mode](./frontend/public/advanced-mode.png)

### Token 使用统计

<div align="center">
  <img src="./frontend/public/token-graph.png" width="48%" alt="Token Graph"/>
  <img src="./frontend/public/token-monthly.png" width="48%" alt="Token Monthly"/>
</div>

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

## 🔍 理论方法详解

### 布鲁姆认知层级编码
- **理论基础**：Bloom's Taxonomy（1956）认知分类体系
- **6 层级结构**：
  1. **Remember（记忆）**：回忆事实、概念
  2. **Understand（理解）**：解释、总结、推理
  3. **Apply（应用）**：在新情境中使用知识
  4. **Analyze（分析）**：区分、组织、归因
  5. **Evaluate（评估）**：批判、检验、判断
  6. **Create（创造）**：设计、构建、规划
- **映射策略**：question_type → Bloom Level 启发式规则
- **应用价值**：评估学习者的认知深度，识别学习模式

### 信息增益计算
- **理论基础**：KL Divergence（相对熵，信息论核心概念）
- **核心公式**：
  ```
  IG(P, Q) = DKL(P∥Q) × R × C
  
  其中：
  DKL(P∥Q) = Σ P(i) × log(P(i) / Q(i))
  R = Relevancy Score (0-1)
  C = 1 - Toxicity Score (0-1)
  ```
- **物理意义**：
  - **DKL**：实际分布 P 偏离基线 Q 的程度（bit）
  - **R × C**：质量修正因子，过滤低质量对话
- **应用价值**：量化对话的学习效果，识别高价值交互

### 对话流程分析
- **分析维度**：
  - 问题类型分布（澄清、深入、情感等）
  - 对话轮次与长度统计
  - 话题转移模式识别
- **输出结果**：生成 question_type_counts，作为 Bloom 编码和 InfoGain 的输入
- **技术实现**：LLM 辅助分类 + 规则引擎

---

## 📊 实现亮点

1. **论文理论完整复现**：从对话流分析到认知编码、信息增益评估的完整链路
2. **算法文档化**：详细推导过程、启发式规则、计算示例全部文档化（docs/ 目录）
3. **端到端验证**：提供测试数据和验证步骤，确保结果可复现
4. **工程化落地**：基于 Convelyze + DeepEval 构建完整系统，本地可运行

---

## 📚 参考与致谢

### 参考项目
- **Convelyze**：https://github.com/meetpateltech/convelyze  
  本项目前端基于 Convelyze 进行扩展和改造，保留了其优秀的可视化设计，并集成了 Deep Analysis 功能。

- **DeepEval**：https://deepeval.com/  
  使用 DeepEval 框架进行对话质量评估，提供结构化的评估指标（Relevancy、Toxicity、Bias 等）。

### 参考论文
- **StuGPTViz: A Visual Analytics Approach to Understand Student-ChatGPT Interactions**  
  本项目的理论基础和设计思路参考了该论文，实现了对话流程分析、认知层级编码等核心功能。

### 技术栈
- **LLM API 服务**：硅基流动 (SiliconFlow)  
  推荐使用 Qwen/Qwen2.5-7B-Instruct 模型，JSON 结构稳定，评估效果好。

- **理论基础**：Bloom's Taxonomy、KL Divergence / Information Gain

### 项目状态
- ✅ **开发环境**：本地开发测试
- ⏳ **部署状态**：暂未部署到生产服务器
- 📖 **部署指南**：参考 [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)（支持 1G 内存 / 40G 硬盘的轻量级部署）

---

## 📄 许可

MIT License

---

**一键启动 Deep Analysis，获取认知层级与信息增益洞察！** 🚀
