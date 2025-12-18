# ConveVisAna Frontend 集成指南

## 🎯 当前状态

✅ **已完成**：
- 创建了前端目录结构
- 实现了 API 客户端 (`utils/apiClient.ts`)
- 实现了状态管理 Hooks (`hooks/`)
- 定义了 TypeScript 类型 (`types/deepAnalysis.ts`)
- 准备了环境变量配置模板

⏳ **待完成**：
- 引入 Convelyze 前端代码
- 创建深度分析 UI 组件
- 修改 dashboard 页面集成

## 🚀 下一步操作

### 1. 引入 Convelyze 前端

在 PowerShell 中执行：

\`\`\`powershell
# 进入前端目录
cd d:\repositories\ConveVisAna\frontend

# 克隆 Convelyze
git clone https://github.com/meetpateltech/convelyze.git temp

# 移动文件到当前目录（保留已有的 utils/hooks/types）
Get-ChildItem temp -Exclude '.git' | Move-Item -Destination . -Force

# 清理临时目录
Remove-Item temp -Recurse -Force

# 保留原始许可证
if (Test-Path LICENSE) {
    Copy-Item LICENSE LICENSE.convelyze
}
\`\`\`

### 2. 安装依赖

\`\`\`powershell
# 使用 Bun（推荐）
bun install

# 或使用 npm
npm install
\`\`\`

### 3. 配置环境变量

\`\`\`powershell
# 复制环境变量模板
Copy-Item .env.example .env.local

# 编辑 .env.local，设置后端地址
# NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
\`\`\`

### 4. 验证基础功能

启动开发服务器：

\`\`\`powershell
bun run dev
# 或
npm run dev
\`\`\`

访问 http://localhost:3000，确认 Convelyze 原有功能正常运行。

### 5. 测试后端连通性

在浏览器控制台执行：

\`\`\`javascript
// 测试 API 客户端
const { apiClient } = await import('/utils/apiClient.ts');
const health = await apiClient.checkHealth();
console.log(health);
\`\`\`

预期输出：
\`\`\`json
{
  "status": "healthy",
  "has_api_key": true
}
\`\`\`

## 📋 待开发的 UI 组件

根据方案书第 5.3 节，需要创建以下组件：

### components/deep-analysis/
- [ ] `DeepAnalysisPanel.tsx` - 主面板（分析选项、隐私提示）
- [ ] `QualityMetricsCard.tsx` - 质量评估结果展示
- [ ] `FlowAnalysisSection.tsx` - 流程分析结果展示
- [ ] `LoadingOverlay.tsx` - 加载状态组件

## 🔄 集成到 Dashboard

需要修改 `app/dashboard/page.tsx`：

1. 导入深度分析组件
2. 添加 `mode` 状态的 `'deep'` 选项
3. 在按钮组添加 "Deep Analysis" 按钮
4. 添加渲染分支

详见 [docs/Convelyze整合技术方案.md](../docs/Convelyze整合技术方案.md) 第 5.2 节。

## 🐛 故障排查

### 问题：无法连接后端

**检查清单**：
1. 后端是否已启动？(`python backend/start_server.py`)
2. 环境变量是否正确？(`.env.local` 中的 `NEXT_PUBLIC_BACKEND_BASE_URL`)
3. CORS 是否配置？(后端 `.env` 中的 `ALLOWED_ORIGINS`)
4. 防火墙是否阻止？

### 问题：TypeScript 类型错误

如果导入路径报错，检查 `tsconfig.json` 中的 `paths` 配置：

\`\`\`json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
\`\`\`

### 问题：模块找不到

确保已安装所有依赖：
\`\`\`powershell
bun install
# 或
npm install
\`\`\`

## 📚 相关资源

- [完整技术方案](../docs/Convelyze整合技术方案.md)
- [Convelyze 原仓库](https://github.com/meetpateltech/convelyze)
- [后端 API 文档](../backend/README.md)
- [Next.js 文档](https://nextjs.org/docs)

## ✅ 验收标准

完成集成后，应能实现：

1. ✅ Convelyze 原有功能完全保留
2. ✅ 上传 conversations.json 后立即显示基础统计
3. ✅ 出现 "Deep Analysis" 按钮（如果后端已配置）
4. ✅ 点击按钮后能调用后端 API
5. ✅ 显示质量评估或流程分析结果
6. ✅ 错误处理友好（网络错误、后端错误等）

---

**准备好了吗？** 按照上述步骤开始集成！如有问题，查看技术方案文档或提交 Issue。
