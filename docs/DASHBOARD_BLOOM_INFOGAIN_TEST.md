# Dashboard 布鲁姆认知编码与信息增益推算测试指南

## 🎯 测试目标

验证 Dashboard 页面已成功集成布鲁姆认知编码和信息增益推算功能。

## ✅ 实施完成清单

- ✅ **BloomTaxonomyCard 组件**：已存在于 `frontend/components/deep-analysis/`
- ✅ **InfoGainCard 组件**：已存在于 `frontend/components/deep-analysis/`
- ✅ **DeepAnalysisPanel 集成**：已添加两个新组件的导入和渲染
- ✅ **数据流连接**：组件接收 `flowResult` 和 `qualityResult` 数据
- ✅ **TypeScript 类型**：所有类型定义完整
- ✅ **组件导出**：已在 `index.ts` 中统一导出

## 🚀 测试步骤

### 前置条件

1. **启动后端服务**
   ```bash
   cd backend
   python start_server.py
   ```
   确保后端运行在 `http://localhost:8000`

2. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```
   前端将运行在 `http://localhost:3001` (因端口3000被占用)

### 测试流程

#### 步骤1：访问 Dashboard 页面

打开浏览器访问：
```
http://localhost:3001/dashboard
```

#### 步骤2：切换到 Deep Analysis 模式

在 Dashboard 页面顶部切换到 "Deep Analysis" 模式。

#### 步骤3：上传对话文件

上传 `conversations.json` 测试文件（或任何符合格式的对话文件）。

#### 步骤4：运行质量评估

点击 "开始质量评估" 按钮，等待评估完成。

预期结果：
- ✅ 显示质量评估卡片（Relevancy, Helpfulness, Coherence, Toxicity, Bias）
- ✅ 各指标显示分数和通过状态

#### 步骤5：运行流程分析

点击 "开始流程分析" 按钮，等待分析完成。

预期结果：
- ✅ 显示流程分析卡片（问题类型统计、平均长度等）
- ✅ 显示对话轮次详情

#### 步骤6：验证布鲁姆认知编码

**自动触发条件**：当质量评估和流程分析都完成后，自动显示。

预期结果：
- ✅ 显示布鲁姆认知编码卡片
- ✅ 6个层级的分布条形图：
  - 记忆 (Remember)
  - 理解 (Understand)
  - 应用 (Apply)
  - 分析 (Analyze)
  - 评价 (Evaluate)
  - 创造 (Create)
- ✅ 每个层级显示百分比
- ✅ 显示代表性样例（Q&A对）
- ✅ 底部显示认知层级洞察

#### 步骤7：验证信息增益推算

预期结果：
- ✅ 显示信息增益推算卡片
- ✅ 顶部显示 DKL(P∥Q) 值
- ✅ 三个参数区域：
  - 公式说明
  - 参数值（R、C、IG）
  - 解读说明
- ✅ P vs Q 分布对比柱状图
- ✅ 底部显示信息增益洞察

## 🔍 数据流验证

### 布鲁姆认知编码数据来源

```typescript
// 输入数据
flowResult: {
  turns: [
    {
      question: "...",
      answer: "...",
      question_type: "planning" // ← 关键字段
    }
  ]
}

// 映射逻辑（启发式算法）
question_type → bloom_level
- planning → analyze
- tooling → apply
- architecture → analyze
- feature → create
- insight → understand
- qa → remember
// ... 等等
```

### 信息增益推算数据来源

```typescript
// 输入数据1：流程分析
flowResult: {
  summary: {
    question_type_counts: {
      planning: 12,
      tooling: 9,
      architecture: 14,
      // ... 其他类型
    }
  }
}

// 输入数据2：质量评估
qualityResult: {
  metrics: {
    relevancy: { score: 0.91 },  // R 因子
    toxicity: { score: 0.028 }   // C = 1 - toxicity
  }
}

// 计算公式（纯前端）
P = normalize(question_type_counts)  // 当前分布
Q = baseline_distribution            // 基线分布（预定义）
DKL = ∑ P(i) × log(P(i) / Q(i))    // KL散度
R = relevancy.score
C = 1 - toxicity.score
IG = DKL × R × C
```

## 📊 预期输出示例

### 布鲁姆认知编码

```
布鲁姆认知编码
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

记忆 (Remember)    ████░░░░░░  9.0%
理解 (Understand)  █████░░░░░ 11.2%
应用 (Apply)       ████████░░ 24.7%
分析 (Analyze)     █████████░ 29.2%
评价 (Evaluate)    █████░░░░░ 13.5%
创造 (Create)      ████░░░░░░ 12.4%

🧭 认知层级洞察
当前对话以分析(Analyze)为主；建议引导用户提升到更高层级...
```

### 信息增益推算

```
信息增益推算
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DKL(P∥Q): 0.0259

参数：
- R（相关性）≈ 0.91
- C（置信度）≈ 0.97
- IG（信息增益）≈ 0.0229

[P vs Q 分布对比柱状图]

📈 信息增益洞察
当前 IG ≈ 0.0229。若希望进一步提升，可引导产生与基线分布差异更大的问题类型...
```

## 🐛 常见问题排查

### 问题1：组件不显示

**症状**：只显示质量评估和流程分析，不显示布鲁姆和信息增益

**原因**：需要**同时完成**质量评估和流程分析

**解决**：
1. 先点击 "开始质量评估"，等待完成
2. 再点击 "开始流程分析"，等待完成
3. 两个都完成后，布鲁姆和信息增益会自动显示

### 问题2：后端连接失败

**症状**：显示 "后端连接失败" 红色提示

**解决**：
```bash
cd backend
python start_server.py
```

确保后端服务运行正常。

### 问题3：数据为空

**症状**：组件显示但没有数据

**检查**：
1. 浏览器开发者工具 Console 是否有错误
2. Network 标签检查 API 调用是否成功
3. 确认上传的文件格式正确

### 问题4：类型错误

**症状**：TypeScript 编译错误

**解决**：
```bash
cd frontend
npm run build
```

检查类型定义是否完整。

## ✨ 性能指标

根据设计文档，启发式算法应达到：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API 调用 | 0 | 无需额外 API 调用 |
| 计算时间 | <30ms | 纯前端数学计算 |
| 准确率 | 75-85% | 启发式映射准确率 |
| 用户体验 | 即时 | 无等待时间 |

## 📝 测试检查清单

测试完成后，请确认：

- [ ] ✅ Dashboard 页面可以正常访问
- [ ] ✅ 可以上传 conversations.json 文件
- [ ] ✅ 质量评估功能正常工作
- [ ] ✅ 流程分析功能正常工作
- [ ] ✅ 布鲁姆认知编码卡片正常显示
  - [ ] 6个层级的分布条
  - [ ] 每个层级的百分比
  - [ ] 代表性样例
  - [ ] 认知层级洞察
- [ ] ✅ 信息增益推算卡片正常显示
  - [ ] DKL 值计算正确
  - [ ] R、C、IG 参数显示
  - [ ] P vs Q 分布对比图
  - [ ] 信息增益洞察
- [ ] ✅ 所有组件响应式布局正常
- [ ] ✅ 深色模式/浅色模式切换正常
- [ ] ✅ 无 Console 错误
- [ ] ✅ 无 TypeScript 编译错误

## 🎉 测试成功标志

如果看到以下内容，说明集成成功：

1. **完整的 4 个卡片区域**：
   - 质量评估卡片（5个指标）
   - 流程分析卡片（问题类型统计）
   - 布鲁姆认知编码卡片（6层级分布）
   - 信息增益推算卡片（IG公式和对比图）

2. **数据真实性**：
   - 布鲁姆分布百分比总和接近 100%
   - IG 值为正数（通常 0.01-0.1 范围）
   - P vs Q 对比图显示实际差异

3. **用户体验**：
   - 两个分析完成后，立即显示布鲁姆和信息增益（无延迟）
   - 所有图表渲染流畅
   - 提示信息清晰易懂

## 📚 参考文档

- [BLOOM_INFOGAIN_DESIGN.md](./BLOOM_INFOGAIN_DESIGN.md) - 完整设计方案
- [BLOOM_HEURISTIC_EXAMPLE.md](./BLOOM_HEURISTIC_EXAMPLE.md) - 布鲁姆认知编码实例
- [INFOGAIN_HEURISTIC_EXAMPLE.md](./INFOGAIN_HEURISTIC_EXAMPLE.md) - 信息增益推算实例

## 🚀 下一步

测试完成后，可以考虑：

1. **优化映射规则**：根据实际数据调整 `question_type → bloom_level` 映射
2. **调整基线分布**：优化 Q 分布定义，使 KL 散度更有意义
3. **添加导出功能**：支持导出布鲁姆和信息增益报告
4. **可视化增强**：添加更多图表类型（雷达图、热力图等）
5. **LLM 增强**：实施方案2或方案3，提供可选的 LLM 精确分析

---

**测试日期**: 2026-01-02  
**实施方案**: 方案1 - 增强型启发式算法  
**技术栈**: Next.js 14 + TypeScript + React + Recharts  
**状态**: ✅ 实施完成，等待测试验证
