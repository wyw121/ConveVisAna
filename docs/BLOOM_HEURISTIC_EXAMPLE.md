# 启发式算法详解：布鲁姆认知编码实例

## 🎯 核心问题：你已经有什么数据？

### 当你调用 `/api/analyze-flow` 时，后端返回：

```json
{
  "conversation_id": "demo-conv-001",
  "total_turns": 89,
  "turns": [
    {
      "question": "我想做一个数据看板，如何开始？",
      "answer": "先确定指标与数据来源，选择 Next.js + 图表库。",
      "question_type": "planning",  // ← 关键！已经分类了
      "turn_number": 1
    },
    {
      "question": "用哪种图表库更合适？",
      "answer": "可选 Recharts / Chart.js...",
      "question_type": "tooling",  // ← 关键！
      "turn_number": 2
    },
    {
      "question": "如何组织组件结构？",
      "answer": "将卡片拆成展示组件与容器组件...",
      "question_type": "architecture",  // ← 关键！
      "turn_number": 3
    }
  ],
  "summary": {
    "question_type_counts": {
      "planning": 12,      // ← 已经统计好了！
      "tooling": 9,
      "architecture": 14,
      "styling": 7,
      "feature": 11,
      "qa": 8,
      "insight": 10,
      "cost": 6,
      "report": 5,
      "suggestion": 7
    }
  }
}
```

## 💡 启发式算法的核心思路

**你已经有了问题类型分类（question_type），现在只需要映射到布鲁姆层级！**

### 第一步：建立映射表

```typescript
// 这是一个简单的字典映射
const QUESTION_TYPE_TO_BLOOM = {
  // 布鲁姆层级1：记忆（Remember）- 回忆事实、定义
  'informational': 'remember',
  'qa': 'remember',  // ← "质量评估包括哪些维度？"
  
  // 布鲁姆层级2：理解（Understand）- 解释概念
  'clarification': 'understand',
  'insight': 'understand',  // ← "流程分析能看到什么？"
  
  // 布鲁姆层级3：应用（Apply）- 使用方法、执行步骤
  'tooling': 'apply',      // ← "用哪种图表库更合适？"
  'styling': 'apply',      // ← "样式该如何统一？"
  'cost': 'apply',         // ← "费用如何估算？"
  
  // 布鲁姆层级4：分析（Analyze）- 分解结构、组织
  'architecture': 'analyze',  // ← "如何组织组件结构？"
  'planning': 'analyze',      // ← "我想做一个数据看板，如何开始？"
  
  // 布鲁姆层级5：评价（Evaluate）- 判断质量、反馈
  'suggestion': 'evaluate',   // ← "有没有改进建议？"
  'report': 'evaluate',       // ← "如何导出报告？"
  
  // 布鲁姆层级6：创造（Create）- 设计方案、构建
  'feature': 'create',  // ← "我需要上传 conversations.json 做分析"
};
```

### 第二步：前端计算布鲁姆分布

```typescript
function calculateBloomDistribution(flowData: FlowAnalysisResult) {
  // 1. 获取问题类型统计（已经由后端计算好）
  const typeCounts = flowData.summary.question_type_counts;
  // {
  //   planning: 12,
  //   tooling: 9,
  //   architecture: 14,
  //   ...
  // }
  
  // 2. 初始化布鲁姆层级计数器
  const bloomCounts = {
    remember: 0,
    understand: 0,
    apply: 0,
    analyze: 0,
    evaluate: 0,
    create: 0,
  };
  
  // 3. 遍历每种问题类型，累加到对应布鲁姆层级
  for (const [questionType, count] of Object.entries(typeCounts)) {
    const bloomLevel = QUESTION_TYPE_TO_BLOOM[questionType] || 'understand';
    bloomCounts[bloomLevel] += count;
  }
  
  // 结果：
  // {
  //   remember: 8 (qa),
  //   understand: 10 (insight),
  //   apply: 22 (tooling:9 + styling:7 + cost:6),
  //   analyze: 26 (architecture:14 + planning:12),
  //   evaluate: 12 (suggestion:7 + report:5),
  //   create: 11 (feature)
  // }
  
  // 4. 计算百分比
  const total = flowData.total_turns; // 89
  const distribution = {
    remember: (bloomCounts.remember / total) * 100,  // 9.0%
    understand: (bloomCounts.understand / total) * 100,  // 11.2%
    apply: (bloomCounts.apply / total) * 100,  // 24.7%
    analyze: (bloomCounts.analyze / total) * 100,  // 29.2%
    evaluate: (bloomCounts.evaluate / total) * 100,  // 13.5%
    create: (bloomCounts.create / total) * 100,  // 12.4%
  };
  
  return distribution;
}
```

## 🔍 具体例子演示

### 输入数据（来自流程分析API）

```json
{
  "summary": {
    "question_type_counts": {
      "planning": 12,      
      "tooling": 9,
      "architecture": 14,
      "styling": 7,
      "feature": 11,
      "qa": 8,
      "insight": 10,
      "cost": 6,
      "report": 5,
      "suggestion": 7
    }
  },
  "total_turns": 89
}
```

### 处理过程

```
步骤1：映射问题类型 → 布鲁姆层级

planning (12次)     → analyze      ✓
tooling (9次)       → apply        ✓
architecture (14次) → analyze      ✓
styling (7次)       → apply        ✓
feature (11次)      → create       ✓
qa (8次)            → remember     ✓
insight (10次)      → understand   ✓
cost (6次)          → apply        ✓
report (5次)        → evaluate     ✓
suggestion (7次)    → evaluate     ✓

步骤2：累加到布鲁姆层级

remember:   qa (8)                              = 8
understand: insight (10)                        = 10
apply:      tooling (9) + styling (7) + cost (6) = 22
analyze:    planning (12) + architecture (14)   = 26
evaluate:   report (5) + suggestion (7)         = 12
create:     feature (11)                        = 11

步骤3：计算百分比（总数89）

remember:   8/89  = 9.0%
understand: 10/89 = 11.2%
apply:      22/89 = 24.7%
analyze:    26/89 = 29.2%
evaluate:   12/89 = 13.5%
create:     11/89 = 12.4%
```

### 输出结果

```json
{
  "bloom_distribution": {
    "remember": 9.0,
    "understand": 11.2,
    "apply": 24.7,
    "analyze": 29.2,
    "evaluate": 13.5,
    "create": 12.4
  }
}
```

## 📊 前端展示

现在你的 `BloomTaxonomyCard` 组件会显示：

```
布鲁姆认知编码
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

记忆 (Remember)    ████░░░░░░  9.0%
理解 (Understand)  █████░░░░░ 11.2%
应用 (Apply)       ████████░░ 24.7%
分析 (Analyze)     █████████░ 29.2%
评价 (Evaluate)    █████░░░░░ 13.5%
创造 (Create)      ████░░░░░░ 12.4%
```

## ✅ 为什么说"0成本、无API调用"？

因为：
1. ✅ 后端已经返回了 `question_type`（流程分析的一部分）
2. ✅ 映射逻辑在前端完成（纯JavaScript计算）
3. ✅ 不需要再次调用 LLM API
4. ✅ 计算时间 < 100ms

## 🆚 对比：如果用LLM方案

如果用LLM重新分类，你需要：

```python
# 后端需要额外调用
for turn in turns:  # 89个问题
    prompt = f"分析这个问题的布鲁姆层级：{turn.question}"
    result = llm.generate(prompt)  # ← 每次都要API调用！
    
# 总计：89次API调用（或者批量9次）
# 时间：30-60秒
# 成本：¥0.1-0.5
# 风险：RPM限制
```

## 🎯 总结

**启发式算法 = 利用现有数据 + 简单映射**

- 输入：`question_type`（已有）
- 处理：字典映射（前端）
- 输出：布鲁姆分布（即时）

**不需要重新调用API，只是换了一种角度看现有数据！**

---

## 💡 代码示例

完整的前端实现：

```typescript
// utils/bloomClassifier.ts

export type BloomLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

const MAPPING: Record<string, BloomLevel> = {
  'qa': 'remember',
  'informational': 'remember',
  'insight': 'understand',
  'clarification': 'understand',
  'tooling': 'apply',
  'styling': 'apply',
  'cost': 'apply',
  'architecture': 'analyze',
  'planning': 'analyze',
  'report': 'evaluate',
  'suggestion': 'evaluate',
  'feature': 'create',
};

export function classifyBloom(flowResult: FlowAnalysisResult) {
  const counts = { remember: 0, understand: 0, apply: 0, analyze: 0, evaluate: 0, create: 0 };
  
  for (const [type, count] of Object.entries(flowResult.summary.question_type_counts)) {
    const level = MAPPING[type] || 'understand';
    counts[level] += count;
  }
  
  const total = flowResult.total_turns;
  return Object.fromEntries(
    Object.entries(counts).map(([k, v]) => [k, (v / total) * 100])
  );
}
```

使用：

```typescript
// 在组件中
const bloomDistribution = classifyBloom(flowResult);
// 立即得到结果，无需等待！
```

---

**这就是"启发式算法"的全部秘密！你明白了吗？** 😊
