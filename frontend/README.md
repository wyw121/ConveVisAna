# ConveVisAna Frontend Integration

这是 ConveVisAna 项目的前端集成目录，基于 [Convelyze](https://github.com/meetpateltech/convelyze) 前端进行扩展。

## 📁 目录结构

```
frontend/
├── utils/
│   └── apiClient.ts           # 后端 API 客户端
├── hooks/
│   ├── useDeepAnalysis.ts     # 深度分析状态管理
│   └── useBackendStatus.ts    # 后端健康检查
├── types/
│   └── deepAnalysis.ts        # TypeScript 类型定义
├── components/
│   └── deep-analysis/         # 深度分析 UI 组件
└── README.md                  # 本文件
```

## 🚀 快速开始

### 步骤 1: 引入 Convelyze 前端代码

选择以下方式之一：

#### 方式 A: 直接克隆（推荐）

```powershell
# 在 ConveVisAna 根目录执行
cd frontend
git clone https://github.com/meetpateltech/convelyze.git temp
# 将内容移到 frontend/ 根目录
Move-Item temp/* . -Force
Remove-Item temp -Recurse
# 保留原始许可证
Copy-Item LICENSE LICENSE.convelyze
```

#### 方式 B: 使用 Git Submodule

```powershell
# 在 ConveVisAna 根目录执行
git submodule add https://github.com/meetpateltech/convelyze.git frontend/convelyze
```

#### 方式 C: 手动下载

1. 访问 https://github.com/meetpateltech/convelyze
2. 下载 ZIP 并解压到 `frontend/` 目录

### 步骤 2: 安装依赖

```powershell
cd frontend

# 使用 Bun（推荐）
bun install

# 或使用 npm
npm install
```

### 步骤 3: 配置环境变量

创建 `.env.local` 文件：

```env
# 后端 API 地址
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000

# 启用深度分析功能
NEXT_PUBLIC_ENABLE_DEEP_ANALYSIS=true

# 可选：最大评估对数
NEXT_PUBLIC_MAX_EVAL_PAIRS=10
```

### 步骤 4: 启动开发服务器

```powershell
# 终端 1: 启动后端
cd ../backend
.\.venv\Scripts\Activate.ps1
python start_server.py

# 终端 2: 启动前端
cd ../frontend
bun run dev
# 或
npm run dev
```

访问 http://localhost:3000

## 🔧 已实现的集成模块

### ✅ API 客户端 (`utils/apiClient.ts`)

提供与后端通信的封装：

```typescript
import { apiClient } from '@/utils/apiClient';

// 健康检查
const health = await apiClient.checkHealth();

// 质量评估
const result = await apiClient.evaluateQuality(file, 10);

// 流程分析
const flowResult = await apiClient.analyzeFlow(file);
```

### ✅ Hooks (`hooks/`)

**useDeepAnalysis** - 深度分析状态管理：
```typescript
const {
  qualityStatus,
  qualityResult,
  runQualityEvaluation,
} = useDeepAnalysis();

await runQualityEvaluation(file);
```

**useBackendStatus** - 后端健康检查：
```typescript
const { isHealthy, checkHealth } = useBackendStatus({
  autoCheck: true,
});
```

### ✅ 类型定义 (`types/deepAnalysis.ts`)

完整的 TypeScript 类型支持。

## 📝 下一步

查看 [docs/Convelyze整合技术方案.md](../docs/Convelyze整合技术方案.md) 了解：

- [ ] 如何修改 dashboard/page.tsx 添加 Deep Analysis 模式
- [ ] 如何创建深度分析 UI 组件
- [ ] 完整的开发和部署指南

## 🎯 开发任务清单

- [x] 创建 API 客户端
- [x] 实现状态管理 Hooks
- [x] 定义 TypeScript 类型
- [ ] 引入 Convelyze 前端代码
- [ ] 创建深度分析 UI 组件
- [ ] 修改 dashboard 页面集成
- [ ] 测试前后端连通性

## 📚 相关文档

- [Convelyze 整合技术方案](../docs/Convelyze整合技术方案.md)
- [后端 API 文档](../backend/README.md)
- [项目状态](../PROJECT_STATUS.md)
