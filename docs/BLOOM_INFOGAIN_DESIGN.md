# 布鲁姆认知编码与信息增益推算 - 设计方案

## 📊 项目现状分析

### Demo 页面 vs Dashboard 页面对比

| 功能模块 | Demo 页面 | Dashboard 页面 | 差距分析 |
|---------|----------|---------------|---------|
| **质量评估** | ✅ 完整展示（模拟数据） | ✅ 实时API调用 | 无差距 |
| **流程分析** | ✅ 完整展示（模拟数据） | ✅ 实时API调用 | 无差距 |
| **布鲁姆认知编码** | ✅ 完整实现 | ❌ 缺失 | **关键差距** |
| **信息增益推算** | ✅ 完整实现 | ❌ 缺失 | **关键差距** |

### 当前实现方式

#### Demo 页面
- 使用 `BloomTaxonomyCard` 和 `InfoGainCard` 组件
- 基于**前端轻量级启发式算法**计算
- 数据来源：`flowDemoData`（模拟数据）
- **不依赖后端 API**，纯前端计算

#### Dashboard 页面
- 使用 `DeepAnalysisPanel` 组件
- 仅包含质量评估和流程分析
- **缺少**布鲁姆认知编码和信息增益推算

---

## 🎯 核心问题分析

### 问题1：数据来源与计算方式

**当前 Demo 实现**：
```typescript
// BloomTaxonomyCard.tsx - 轻量级启发式分类
function classifyTurn(question: string, type?: string): BloomLevelKey {
  const q = (question || '').toLowerCase();
  const t = (type || '').toLowerCase();
  
  // 基于关键词匹配
  if (t.includes('informational')) return 'remember';
  if (t.includes('clarification')) return 'understand';
  if (t.includes('procedural')) return 'apply';
  // ... 更多规则
}
```

**问题**：
- ✅ 优点：快速、无需API调用、实时响应
- ⚠️ 缺点：准确性有限，依赖关键词匹配

### 问题2：是否需要 LLM 辅助？

根据你的项目特点，我的分析：

#### 场景A：轻量级方案（推荐短期）⭐
**不需要 LLM**，使用增强的启发式算法

**理由**：
1. 你已经有**流程分析结果**（`question_type`）
2. 可以基于现有分类映射到布鲁姆层级
3. 信息增益只需要统计计算（KL散度）
4. 避免额外 API 成本和延迟

**适用条件**：
- ✅ 对话已经过流程分析（有 question_type）
- ✅ 需要快速展示结果
- ✅ 对精度要求适中

#### 场景B：深度方案（长期优化）
**需要 LLM**，参考 DeepEval 模式

**理由**：
1. 更精准的认知层级分类
2. 理解问题的深层语义
3. 可以生成详细的分析报告

**挑战**：
- ❌ 需要额外 API 调用（6个布鲁姆层级分类）
- ❌ 受 RPM 限制影响
- ❌ 响应时间增加

---

## 💡 推荐方案：混合策略

### 方案设计原则

**借鉴 DeepEval 的设计思路**：
1. **结构化输出**：使用 Pydantic Schema 定义返回格式
2. **批量评估**：一次API调用完成所有分类
3. **降级策略**：API失败时使用启发式算法

### 三层架构

```
┌─────────────────────────────────────────────┐
│  第1层：前端启发式算法（即时反馈）           │
│  - 无需等待，立即显示                        │
│  - 准确率 70-80%                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  第2层：LLM批量分类（可选增强）              │
│  - 后台异步调用                             │
│  - 准确率 90-95%                            │
│  - 失败时使用第1层结果                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  第3层：信息增益计算（纯数学）               │
│  - 基于分类结果计算KL散度                    │
│  - 结合质量指标                             │
└─────────────────────────────────────────────┘
```

---


## 🔧 具体实现方案

### 方案1：增强型启发式算法（短期实施）⭐

#### 优点
- ✅ 无需额外API调用
- ✅ 实时响应（<100ms）
- ✅ 0成本
- ✅ 易于实施

#### 实现步骤

**Step 1：增强前端分类算法**

基于现有 `question_type` 扩展映射规则：

```typescript
// 增强的布鲁姆分类映射
const QUESTION_TYPE_TO_BLOOM: Record<string, BloomLevelKey> = {
  // 记忆层（Remember）- 事实性、定义性问题
  'informational': 'remember',
  'definition': 'remember',
  'factual': 'remember',
  
  // 理解层（Understand）- 澄清、解释性问题
  'clarification': 'understand',
  'explanation': 'understand',
  'conceptual': 'understand',
  
  // 应用层（Apply）- 步骤、工具、实施类问题
  'procedural': 'apply',
  'tooling': 'apply',
  'implementation': 'apply',
  'how-to': 'apply',
  
  // 分析层（Analyze）- 结构、组织、对比类问题
  'architecture': 'analyze',
  'planning': 'analyze',
  'comparison': 'analyze',
  'cost': 'analyze',
  
  // 评价层（Evaluate）- 反馈、洞察、评审类问题
  'feedback': 'evaluate',
  'insight': 'evaluate',
  'report': 'evaluate',
  'review': 'evaluate',
  
  // 创造层（Create）- 设计、构建、特性开发
  'feature': 'create',
  'design': 'create',
  'build': 'create',
  'innovation': 'create',
};
```


## 🔧 具体实现方案

### 方案1：增强型启发式算法（短期实施）⭐

#### 优点
- ✅ 无需额外API调用
- ✅ 实时响应（<100ms）
- ✅ 0成本
- ✅ 易于实施

#### 实现步骤

**Step 1：增强前端分类算法**

基于现有 question_type 扩展映射规则。

**Step 2：集成到 Dashboard 页面**

修改 DeepAnalysisPanel 组件，添加布鲁姆和信息增益模块。

**Step 3：数据流设计**

`
用户上传文件 → 质量评估 + 流程分析 → 提取结果
                                        ↓
                          前端计算布鲁姆分类 + 信息增益
                                        ↓
                                   实时展示
`

#### 数据依赖

布鲁姆认知编码需要：
- flowResult.turns[] - 对话轮次
- flowResult.turns[].question_type - 问题类型
- flowResult.turns[].question - 问题文本

信息增益需要：
- flowResult.summary.question_type_counts - 类型分布
- qualityResult.metrics.relevancy.score - 相关性
- qualityResult.metrics.toxicity.score - 毒性分数


## 🔧 具体实现方案

### 方案1：增强型启发式算法（短期实施）⭐

#### 优点
- ✅ 无需额外API调用
- ✅ 实时响应（<100ms）
- ✅ 0成本
- ✅ 易于实施

#### 实现步骤

**Step 1：增强前端分类算法**

基于现有 question_type 扩展映射规则。

**Step 2：集成到 Dashboard 页面**

修改 DeepAnalysisPanel 组件，添加布鲁姆和信息增益模块。

**Step 3：数据流设计**

`
用户上传文件 → 质量评估 + 流程分析 → 提取结果
                                        ↓
                          前端计算布鲁姆分类 + 信息增益
                                        ↓
                                   实时展示
`

#### 数据依赖

布鲁姆认知编码需要：
- flowResult.turns[] - 对话轮次
- flowResult.turns[].question_type - 问题类型
- flowResult.turns[].question - 问题文本

信息增益需要：
- flowResult.summary.question_type_counts - 类型分布
- qualityResult.metrics.relevancy.score - 相关性
- qualityResult.metrics.toxicity.score - 毒性分数



### 方案2：LLM辅助分类（长期优化）

#### 设计理念：借鉴 DeepEval 模式

**DeepEval 的核心设计**：
1. 定义 Pydantic Schema
2. 要求 LLM 返回结构化 JSON
3. 自动验证和解析

#### 后端 API 设计

**新增端点**: `POST /api/analyze-bloom`

**请求参数**:
- file: 对话文件
- method: 'heuristic' | 'llm' | 'hybrid'

**响应格式**:
`json
{
  "bloom_distribution": {
    "remember": 15.5,
    "understand": 22.3,
    "apply": 35.2,
    "analyze": 12.8,
    "evaluate": 8.1,
    "create": 6.1
  },
  "examples": {
    "remember": [
      {"question": "...", "answer": "...", "confidence": 0.85}
    ]
  },
  "method_used": "hybrid",
  "processing_time": 12.5
}
`

#### Pydantic Schema 定义

```python
from pydantic import BaseModel, Field
from typing import List, Dict

class BloomClassification(BaseModel):
    level: str = Field(description="Bloom级别: remember, understand, apply, analyze, evaluate, create")
    confidence: float = Field(ge=0, le=1, description="置信度0-1")
    reason: str = Field(description="分类理由")

class TurnBloomAnalysis(BaseModel):
    turn_index: int
    question: str
    classification: BloomClassification
    
class BloomAnalysisResult(BaseModel):
    turns: List[TurnBloomAnalysis]
    distribution: Dict[str, float]
    total_turns: int
```



### 方案2：LLM辅助分类（长期优化）

#### 设计理念：借鉴 DeepEval 模式

**DeepEval 的核心设计**：
1. 定义 Pydantic Schema
2. 要求 LLM 返回结构化 JSON
3. 自动验证和解析

#### 后端 API 设计

**新增端点**: `POST /api/analyze-bloom`

**请求参数**:
- file: 对话文件
- method: 'heuristic' | 'llm' | 'hybrid'

**响应格式**:
`json
{
  "bloom_distribution": {
    "remember": 15.5,
    "understand": 22.3,
    "apply": 35.2,
    "analyze": 12.8,
    "evaluate": 8.1,
    "create": 6.1
  },
  "examples": {
    "remember": [
      {"question": "...", "answer": "...", "confidence": 0.85}
    ]
  },
  "method_used": "hybrid",
  "processing_time": 12.5
}
`

#### Pydantic Schema 定义

```python
from pydantic import BaseModel, Field
from typing import List, Dict

class BloomClassification(BaseModel):
    level: str = Field(description="Bloom级别: remember, understand, apply, analyze, evaluate, create")
    confidence: float = Field(ge=0, le=1, description="置信度0-1")
    reason: str = Field(description="分类理由")

class TurnBloomAnalysis(BaseModel):
    turn_index: int
    question: str
    classification: BloomClassification
    
class BloomAnalysisResult(BaseModel):
    turns: List[TurnBloomAnalysis]
    distribution: Dict[str, float]
    total_turns: int
```



#### LLM 提示词设计

```python
BLOOM_CLASSIFICATION_PROMPT = '''
你是一个教育专家，擅长基于布鲁姆认知分类法分析问题。

布鲁姆认知层级（从低到高）：
1. Remember（记忆）：回忆事实、定义
2. Understand（理解）：解释概念、总结
3. Apply（应用）：使用方法、执行步骤
4. Analyze（分析）：分解结构、对比关系
5. Evaluate（评价）：判断质量、提供反馈
6. Create（创造）：设计方案、创新思路

请分析以下问题属于哪个认知层级：

问题：{question}
上下文：{context}

返回JSON格式：
{
  "level": "apply",
  "confidence": 0.85,
  "reason": "该问题要求使用特定方法解决问题，属于应用层级"
}
'''
```

#### 批量评估策略

为了避免 RPM 限制，采用**批量评估**：

```python
def batch_classify_bloom(turns: List[Dict], batch_size: int = 10):
    \"\"\"批量分类，减少API调用次数\"\"\"
    results = []
    
    for i in range(0, len(turns), batch_size):
        batch = turns[i:i+batch_size]
        
        # 构造批量提示词
        prompt = f\"\"\"
        分析以下 {len(batch)} 个问题的布鲁姆层级：
        
        {json.dumps([{"index": j, "question": t["question"]} 
                     for j, t in enumerate(batch)], ensure_ascii=False)}
        
        返回数组，每个元素包含 level, confidence, reason
        \"\"\"
        
        # 调用LLM
        response = model.generate(prompt, schema=BatchBloomResult)
        results.extend(response.classifications)
        
        # 避免RPM限制
        time.sleep(8)  
    
    return results
```



#### LLM 提示词设计

```python
BLOOM_CLASSIFICATION_PROMPT = '''
你是一个教育专家，擅长基于布鲁姆认知分类法分析问题。

布鲁姆认知层级（从低到高）：
1. Remember（记忆）：回忆事实、定义
2. Understand（理解）：解释概念、总结
3. Apply（应用）：使用方法、执行步骤
4. Analyze（分析）：分解结构、对比关系
5. Evaluate（评价）：判断质量、提供反馈
6. Create（创造）：设计方案、创新思路

请分析以下问题属于哪个认知层级：

问题：{question}
上下文：{context}

返回JSON格式：
{
  "level": "apply",
  "confidence": 0.85,
  "reason": "该问题要求使用特定方法解决问题，属于应用层级"
}
'''
```

#### 批量评估策略

为了避免 RPM 限制，采用**批量评估**：

```python
def batch_classify_bloom(turns: List[Dict], batch_size: int = 10):
    \"\"\"批量分类，减少API调用次数\"\"\"
    results = []
    
    for i in range(0, len(turns), batch_size):
        batch = turns[i:i+batch_size]
        
        # 构造批量提示词
        prompt = f\"\"\"
        分析以下 {len(batch)} 个问题的布鲁姆层级：
        
        {json.dumps([{"index": j, "question": t["question"]} 
                     for j, t in enumerate(batch)], ensure_ascii=False)}
        
        返回数组，每个元素包含 level, confidence, reason
        \"\"\"
        
        # 调用LLM
        response = model.generate(prompt, schema=BatchBloomResult)
        results.extend(response.classifications)
        
        # 避免RPM限制
        time.sleep(8)  
    
    return results
```



### 方案3：混合策略（推荐）⭐⭐⭐

#### 设计思路

结合两种方案的优点：
1. **默认使用启发式算法**（快速、免费）
2. **可选 LLM 增强**（精准、深入）
3. **智能降级**（API失败时自动降级）

#### 用户交互流程

`
用户完成质量评估+流程分析
         ↓
立即显示启发式结果（0延迟）
         ↓
[可选] 点击"使用AI增强分析"按钮
         ↓
后台调用LLM重新分类
         ↓
更新结果显示（标注"AI增强"）
`

#### 前端实现

```typescript
// useBloomAnalysis.ts
export function useBloomAnalysis() {
  const [heuristicResult, setHeuristicResult] = useState(null);
  const [llmResult, setLlmResult] = useState(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  
  const runHeuristic = useCallback((flowData) => {
    // 即时计算
    const result = classifyWithHeuristics(flowData);
    setHeuristicResult(result);
  }, []);
  
  const runLLMEnhancement = useCallback(async (file) => {
    setIsEnhancing(true);
    try {
      const result = await apiClient.analyzeBloom(file, 'llm');
      setLlmResult(result);
    } catch (err) {
      // 失败时保留启发式结果
      console.error('LLM增强失败，使用启发式结果');
    } finally {
      setIsEnhancing(false);
    }
  }, []);
  
  return {
    result: llmResult || heuristicResult,
    isEnhanced: !!llmResult,
    isEnhancing,
    runHeuristic,
    runLLMEnhancement
  };
}
```



### 方案3：混合策略（推荐）⭐⭐⭐

#### 设计思路

结合两种方案的优点：
1. **默认使用启发式算法**（快速、免费）
2. **可选 LLM 增强**（精准、深入）
3. **智能降级**（API失败时自动降级）

#### 用户交互流程

`
用户完成质量评估+流程分析
         ↓
立即显示启发式结果（0延迟）
         ↓
[可选] 点击"使用AI增强分析"按钮
         ↓
后台调用LLM重新分类
         ↓
更新结果显示（标注"AI增强"）
`

#### 前端实现

```typescript
// useBloomAnalysis.ts
export function useBloomAnalysis() {
  const [heuristicResult, setHeuristicResult] = useState(null);
  const [llmResult, setLlmResult] = useState(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  
  const runHeuristic = useCallback((flowData) => {
    // 即时计算
    const result = classifyWithHeuristics(flowData);
    setHeuristicResult(result);
  }, []);
  
  const runLLMEnhancement = useCallback(async (file) => {
    setIsEnhancing(true);
    try {
      const result = await apiClient.analyzeBloom(file, 'llm');
      setLlmResult(result);
    } catch (err) {
      // 失败时保留启发式结果
      console.error('LLM增强失败，使用启发式结果');
    } finally {
      setIsEnhancing(false);
    }
  }, []);
  
  return {
    result: llmResult || heuristicResult,
    isEnhanced: !!llmResult,
    isEnhancing,
    runHeuristic,
    runLLMEnhancement
  };
}
```



---

## 📝 实施计划

### 阶段1：Dashboard集成（立即实施）

**目标**：让 Dashboard 页面达到 Demo 页面的展示效果

**任务清单**：
- [ ] 修改 DeepAnalysisPanel.tsx，添加布鲁姆和信息增益卡片
- [ ] 确保 qualityResult 和 lowResult 数据传递正确
- [ ] 测试前端计算逻辑
- [ ] 验证样式一致性

**预计时间**：2小时

**风险**：无，纯前端修改

---

### 阶段2：增强启发式算法（短期优化）

**目标**：提升分类准确率到 80%+

**任务清单**：
- [ ] 扩展 QUESTION_TYPE_TO_BLOOM 映射表
- [ ] 添加关键词权重系统
- [ ] 引入多语言支持（中英文关键词）
- [ ] 单元测试覆盖

**预计时间**：1天

**风险**：低，不依赖外部服务

---

### 阶段3：LLM API 开发（中期规划）

**目标**：提供可选的 LLM 增强分析

**任务清单**：
- [ ] 后端：创建 /api/analyze-bloom 端点
- [ ] 后端：实现 Pydantic Schema 定义
- [ ] 后端：批量评估逻辑（避免RPM限制）
- [ ] 前端：添加"AI增强"按钮和状态
- [ ] 前端：结果对比显示

**预计时间**：3天

**风险**：
- ⚠️ RPM 限制（需实名认证或添加延迟）
- ⚠️ API 成本（免费额度有限）

---

### 阶段4：混合策略实施（长期优化）

**目标**：智能选择最佳分类方法

**任务清单**：
- [ ] 实现降级策略
- [ ] 添加缓存机制（避免重复调用）
- [ ] 性能监控和日志
- [ ] A/B测试对比准确率

**预计时间**：5天

**风险**：复杂度高，需要完善的错误处理

---



---

## 📝 实施计划

### 阶段1：Dashboard集成（立即实施）

**目标**：让 Dashboard 页面达到 Demo 页面的展示效果

**任务清单**：
- [ ] 修改 DeepAnalysisPanel.tsx，添加布鲁姆和信息增益卡片
- [ ] 确保 qualityResult 和 lowResult 数据传递正确
- [ ] 测试前端计算逻辑
- [ ] 验证样式一致性

**预计时间**：2小时

**风险**：无，纯前端修改

---

### 阶段2：增强启发式算法（短期优化）

**目标**：提升分类准确率到 80%+

**任务清单**：
- [ ] 扩展 QUESTION_TYPE_TO_BLOOM 映射表
- [ ] 添加关键词权重系统
- [ ] 引入多语言支持（中英文关键词）
- [ ] 单元测试覆盖

**预计时间**：1天

**风险**：低，不依赖外部服务

---

### 阶段3：LLM API 开发（中期规划）

**目标**：提供可选的 LLM 增强分析

**任务清单**：
- [ ] 后端：创建 /api/analyze-bloom 端点
- [ ] 后端：实现 Pydantic Schema 定义
- [ ] 后端：批量评估逻辑（避免RPM限制）
- [ ] 前端：添加"AI增强"按钮和状态
- [ ] 前端：结果对比显示

**预计时间**：3天

**风险**：
- ⚠️ RPM 限制（需实名认证或添加延迟）
- ⚠️ API 成本（免费额度有限）

---

### 阶段4：混合策略实施（长期优化）

**目标**：智能选择最佳分类方法

**任务清单**：
- [ ] 实现降级策略
- [ ] 添加缓存机制（避免重复调用）
- [ ] 性能监控和日志
- [ ] A/B测试对比准确率

**预计时间**：5天

**风险**：复杂度高，需要完善的错误处理

---


## 📊 方案对比总结

| 维度 | 启发式算法 | LLM分类 | 混合策略 |
|------|-----------|---------|---------|
| **准确率** | 70-80% | 90-95% | 85-95% |
| **响应时间** | <100ms | 30-60s | 立即/可选 |
| **API成本** | ¥0 | ¥0.1-0.5/次 | ¥0/可选 |
| **RPM限制** | 无 | 严格 | 部分受限 |
| **实施难度** | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| **用户体验** | 优秀 | 一般 | 极佳 |
| **推荐指数** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 推荐实施路线图

### 第1周：快速上线
1. ✅ 集成现有组件到 Dashboard
2. ✅ 使用启发式算法
3. ✅ 验证功能完整性

### 第2周：优化准确率
1. 📈 扩展映射规则
2. 📈 添加关键词权重
3. 📈 多语言支持

### 第3-4周：可选增强
1. 🚀 开发 LLM API
2. 🚀 实现混合策略
3. 🚀 用户可选择方法

### 第5周+：持续优化
1. 🔧 缓存机制
2. 🔧 性能监控
3. 🔧 A/B测试

---

## 💡 关键决策建议

### 对于你的项目，我建议：

1. **立即实施**：集成现有组件（阶段1）
   - ✅ 2小时即可完成
   - ✅ 0风险
   - ✅ 功能完整

2. **短期优化**：增强启发式算法（阶段2）
   - ✅ 准确率提升到 80%+
   - ✅ 无需外部依赖
   - ✅ 成本为0

3. **长期规划**：LLM增强作为可选功能（阶段3-4）
   - ⚠️ 等用户完成实名认证后再开发
   - ⚠️ 作为"专业版"功能
   - ⚠️ 不影响基础体验

---

## 📚 参考资料

### 布鲁姆认知分类法
- [Bloom's Taxonomy - Wikipedia](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)
- [A Model of Learning Objectives - Iowa State University](https://www.celt.iastate.edu/teaching/effective-teaching-practices/revised-blooms-taxonomy/)

### DeepEval 相关
- [DeepEval Documentation](https://docs.deepeval.com/)
- [Pydantic JSON Mode](https://docs.pydantic.dev/latest/)
- [Structured Output with LLMs](https://python.langchain.com/docs/how_to/structured_output/)

### 信息增益与KL散度
- [Kullback–Leibler Divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)
- [Information Gain in Machine Learning](https://en.wikipedia.org/wiki/Information_gain_in_decision_trees)

---

## 🎬 下一步行动

建议你：

1. **阅读本文档**，理解三种方案
2. **选择实施路线**（推荐：启发式算法 → 混合策略）
3. **开始阶段1**：修改 DeepAnalysisPanel.tsx
4. **测试验证**：确保功能正常
5. **持续迭代**：根据用户反馈优化

**我可以立即帮你实施阶段1，需要吗？**


## 📊 方案对比总结

| 维度 | 启发式算法 | LLM分类 | 混合策略 |
|------|-----------|---------|---------|
| **准确率** | 70-80% | 90-95% | 85-95% |
| **响应时间** | <100ms | 30-60s | 立即/可选 |
| **API成本** | ¥0 | ¥0.1-0.5/次 | ¥0/可选 |
| **RPM限制** | 无 | 严格 | 部分受限 |
| **实施难度** | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| **用户体验** | 优秀 | 一般 | 极佳 |
| **推荐指数** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 推荐实施路线图

### 第1周：快速上线
1. ✅ 集成现有组件到 Dashboard
2. ✅ 使用启发式算法
3. ✅ 验证功能完整性

### 第2周：优化准确率
1. 📈 扩展映射规则
2. 📈 添加关键词权重
3. 📈 多语言支持

### 第3-4周：可选增强
1. 🚀 开发 LLM API
2. 🚀 实现混合策略
3. 🚀 用户可选择方法

### 第5周+：持续优化
1. 🔧 缓存机制
2. 🔧 性能监控
3. 🔧 A/B测试

---

## 💡 关键决策建议

### 对于你的项目，我建议：

1. **立即实施**：集成现有组件（阶段1）
   - ✅ 2小时即可完成
   - ✅ 0风险
   - ✅ 功能完整

2. **短期优化**：增强启发式算法（阶段2）
   - ✅ 准确率提升到 80%+
   - ✅ 无需外部依赖
   - ✅ 成本为0

3. **长期规划**：LLM增强作为可选功能（阶段3-4）
   - ⚠️ 等用户完成实名认证后再开发
   - ⚠️ 作为"专业版"功能
   - ⚠️ 不影响基础体验

---

## 📚 参考资料

### 布鲁姆认知分类法
- [Bloom's Taxonomy - Wikipedia](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)
- [A Model of Learning Objectives - Iowa State University](https://www.celt.iastate.edu/teaching/effective-teaching-practices/revised-blooms-taxonomy/)

### DeepEval 相关
- [DeepEval Documentation](https://docs.deepeval.com/)
- [Pydantic JSON Mode](https://docs.pydantic.dev/latest/)
- [Structured Output with LLMs](https://python.langchain.com/docs/how_to/structured_output/)

### 信息增益与KL散度
- [Kullback–Leibler Divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)
- [Information Gain in Machine Learning](https://en.wikipedia.org/wiki/Information_gain_in_decision_trees)

---

## 🎬 下一步行动

建议你：

1. **阅读本文档**，理解三种方案
2. **选择实施路线**（推荐：启发式算法 → 混合策略）
3. **开始阶段1**：修改 DeepAnalysisPanel.tsx
4. **测试验证**：确保功能正常
5. **持续迭代**：根据用户反馈优化

**我可以立即帮你实施阶段1，需要吗？**

