# GPT 聊天质量评估工具

使用 [deepeval](https://deepeval.com/) 对 ChatGPT 导出的聊天记录进行质量评估分析。

## 功能特性

本工具支持以下评估维度：

1. **答案相关性 (Answer Relevancy)** - 评估回答是否与问题相关
2. **有用性 (Helpfulness)** - 评估回答是否对用户有帮助
3. **连贯性 (Coherence)** - 评估回答的逻辑性和连贯性
4. **共情能力 (Empathy)** - 评估是否展现了共情和情感支持
5. **毒性检测 (Toxicity)** - 检测是否包含有害内容
6. **偏见检测 (Bias)** - 检测是否存在性别、种族等偏见

## 安装步骤

### 1. 安装 Python 依赖

```powershell
# 创建虚拟环境(可选但推荐)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

**重要**: 本项目已配置好使用你购买的 ChatAIAPI 转发服务！

复制 `.env.example` 为 `.env`:

```powershell
Copy-Item .env.example .env
```

`.env` 文件已经预设了你的 API Key (`sk-imaEI6SqImBTTfAn8wvPiIN5oHelnY0iRbPe4CKLrDqe4pEV`)，可以直接使用。

**API 使用说明**:
- ✅ **推荐**: 使用 ChatAIAPI 转发服务 (已配置，性价比高)
  - 基础 URL: `https://www.chataiapi.com/v1`
  - 支持模型: `gpt-4o-mini`, `gpt-4o`, `claude-3-5-sonnet-20240620`, `claude-3-haiku-20240307` 等
  - 无需魔法上网，国内直接访问
  
- 可选: 使用原生 OpenAI API
  - 需要在 `.env` 中设置 `OPENAI_API_KEY`
  - 需要魔法上网

### 3. 准备数据

确保你的 ChatGPT 导出数据文件夹包含 `conversations.json` 文件。数据结构应该类似：

```
f6eaf8f0f71aa12e8832082345edd8f0ed475ded4fc40fb0ca9780a596497ada-2025-11-18-01-38-19-c9c652a5f61b4d3f862e60633a9f144a/
├── conversations.json
├── user.json
└── ...
```

## 使用方法

### 快速开始

```powershell
# 直接运行评估(使用 ChatAIAPI，已预配置)
python evaluate_chats.py
```

默认会评估前 3 个问答对，使用 `gpt-4o-mini` 模型。

### 自定义评估

编辑 `evaluate_chats.py` 中的 `main()` 函数：

```python
# 示例1: 评估所有对话
results = evaluator.evaluate_conversation()

# 示例2: 只评估前 10 个问答对
results = evaluator.evaluate_conversation(max_qa_pairs=10)

# 示例3: 只使用特定指标评估
results = evaluator.evaluate_conversation(
    max_qa_pairs=10,
    selected_metrics=['relevancy', 'helpfulness', 'empathy']
)

# 示例4: 评估特定对话
results = evaluator.evaluate_conversation(
    conversation_id='68cecae4-f7b8-8333-9279-a7d7d6989a9c'
)

# 示例5: 使用 Claude 模型评估
evaluator = ChatQualityEvaluator(
    data_folder,
    model='claude-3-haiku-20240307',  # 或 'claude-3-5-sonnet-20240620'
    use_custom_api=True
)
results = evaluator.evaluate_conversation(max_qa_pairs=5)
```

### 支持的模型

通过 ChatAIAPI 可以使用以下模型：

**OpenAI 模型** (推荐):
- `gpt-4o-mini` - 便宜快速，推荐用于大量评估
- `gpt-4o` - 更准确但更贵
- `gpt-4-turbo` - 平衡选择

**Claude 模型**:
- `claude-3-haiku-20240307` - 便宜快速
- `claude-3-5-sonnet-20240620` - 高质量评估

### 可用的评估指标

在 `selected_metrics` 参数中可以使用以下指标：

- `'relevancy'` - 答案相关性
- `'helpfulness'` - 有用性
- `'coherence'` - 连贯性
- `'empathy'` - 共情能力
- `'toxicity'` - 毒性检测
- `'bias'` - 偏见检测

## 输出结果

### 控制台输出

运行时会在控制台显示：
- 每个问答对的评估进度
- 各项指标的得分和是否通过
- 最终的评估摘要统计

示例输出：
```
评估问答对 1/5
对话: 项目合作困境分析
问题: 我和我的师傅钱一龙一起做一个项目...
  Answer Relevancy: 0.856 ✓
  Helpfulness: 0.912 ✓
  Coherence: 0.889 ✓
  Empathy: 0.734 ✓
  Toxicity: 0.021 ✓
  Bias: 0.045 ✓

============================================================
评估摘要
============================================================
总问答对数: 5

各指标得分:
------------------------------------------------------------

relevancy:
  平均分: 0.845
  最低分: 0.756
  最高分: 0.912
  通过率: 5/5 (100.0%)

helpfulness:
  平均分: 0.823
  ...
```

### JSON 结果文件

评估结果会自动保存到 `evaluation_results/chat_quality_report.json`，包含：
- 每个问答对的详细评估结果
- 各项指标的得分和原因
- 汇总统计信息

## 进阶配置

### 使用原生 OpenAI API

如果你想使用原生 OpenAI API 而非 ChatAIAPI:

1. 在 `.env` 中设置 `OPENAI_API_KEY`
2. 注释或删除 `CHATAI_API_KEY`
3. 代码会自动检测并使用 OpenAI API

```python
# 在代码中明确指定使用原生 API
evaluator = ChatQualityEvaluator(
    data_folder,
    model='gpt-4o-mini',
    use_custom_api=False  # 使用原生 OpenAI API
)
```

### 测试自定义 API 连接

```powershell
# 测试 ChatAIAPI 连接
python custom_llm.py
```

这会发送一个测试请求并显示响应。

### 调整评估阈值

在 `evaluate_chats.py` 的 `_init_metrics()` 方法中可以调整阈值：

```python
'relevancy': AnswerRelevancyMetric(
    threshold=0.8,  # 提高通过标准到 0.8
    model=self.model,
    include_reason=True
),
```

### 添加自定义评估指标

使用 `GEval` 创建自定义指标：

```python
'custom_metric': GEval(
    name="专业性",
    criteria="评估回答是否体现了专业知识和深度分析",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT
    ],
    threshold=0.7,
    model=self.model
)
```

## 与 Confident AI 集成(可选)

Confident AI 是 deepeval 的云平台，可以：
- 在线查看评估结果
- 可视化评估报告
- 团队协作和历史追踪

### 设置步骤

1. 注册 [Confident AI](https://app.confident-ai.com/)
2. 获取 API Key
3. 登录：
   ```powershell
   deepeval login
   ```
4. 运行评估后查看结果：
   ```powershell
   deepeval view
   ```

## 文件说明

- `data_loader.py` - 数据加载和预处理模块
- `custom_llm.py` - 自定义 LLM 适配器 (支持 ChatAIAPI)
- `evaluate_chats.py` - 主评估脚本
- `requirements.txt` - Python 依赖
- `.env.example` - 环境变量模板 (已预设你的 API Key)
- `README.md` - 本文档

## 故障排除

### 问题1: 评估卡住不动

如果评估过程中卡住，可能是 API 请求超时。可以：
1. 减少 `max_qa_pairs` 的数量
2. 检查网络连接
3. 检查 ChatAIAPI 服务状态

### 问题2: API Key 错误

确保 `.env` 文件中的 `CHATAI_API_KEY` 正确设置，并且：
- Key 以 `sk-` 开头
- 没有多余的空格或引号
- API 额度充足

### 问题3: 连接失败

如果提示连接失败：
1. 检查网络连接
2. 确认 ChatAIAPI 服务正常 (https://www.chataiapi.com)
3. 尝试运行 `python custom_llm.py` 测试连接

### 问题4: 模型不支持

如果提示模型不支持，请检查：
- 模型名称是否正确
- ChatAIAPI 是否支持该模型
- 建议使用 `gpt-4o-mini` 或 `claude-3-haiku-20240307`

## 成本估算

使用 ChatAIAPI 的 `gpt-4o-mini` 评估的大致成本：
- 每个问答对约 ¥0.005-0.015 (人民币)
- 评估 100 个问答对约 ¥0.5-1.5
- 实际成本取决于对话长度和使用的指标数量

**成本优化建议**:
1. 先用 `max_qa_pairs=3` 测试
2. 使用 `selected_metrics` 只评估关键指标
3. 使用 `gpt-4o-mini` 而不是 `gpt-4o`
4. 批量评估时使用 Claude Haiku 模型更便宜

## 贡献与反馈

如有问题或建议，欢迎提出 Issue 或 Pull Request。

## 参考资源

- [deepeval 官方文档](https://deepeval.com/docs/getting-started)
- [deepeval GitHub](https://github.com/confident-ai/deepeval)
- [LLM 评估指标详解](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [LLM-as-a-Judge 方法](https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method)
