# Convelyze 前端引入脚本
# 自动化引入 Convelyze 前端代码到 ConveVisAna

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ConveVisAna - Convelyze 前端引入脚本" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$frontendPath = $PSScriptRoot
$tempPath = Join-Path $frontendPath "temp-convelyze"

# 检查是否已存在 Convelyze 代码
if (Test-Path (Join-Path $frontendPath "app")) {
    Write-Host "⚠️  检测到已存在 app 目录，可能已引入 Convelyze" -ForegroundColor Yellow
    $continue = Read-Host "是否继续？这将覆盖现有文件 (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "操作已取消" -ForegroundColor Red
        exit 0
    }
}

# 步骤 1: 克隆 Convelyze
Write-Host "[1/5] 克隆 Convelyze 仓库..." -ForegroundColor Green
try {
    git clone https://github.com/meetpateltech/convelyze.git $tempPath
    if ($LASTEXITCODE -ne 0) {
        throw "Git clone 失败"
    }
} catch {
    Write-Host "❌ 克隆失败: $_" -ForegroundColor Red
    Write-Host "请确保已安装 Git 并可访问 GitHub" -ForegroundColor Yellow
    exit 1
}

# 步骤 2: 移动文件
Write-Host "[2/5] 移动文件到前端目录..." -ForegroundColor Green

# 保护已创建的集成文件
$protectedPaths = @(
    "utils/apiClient.ts",
    "hooks/useDeepAnalysis.ts",
    "hooks/useBackendStatus.ts",
    "types/deepAnalysis.ts",
    "README.md",
    ".env.example",
    "INTEGRATION_GUIDE.md"
)

# 移动所有文件，排除 .git
Get-ChildItem $tempPath -Exclude ".git" | ForEach-Object {
    $relativePath = $_.FullName.Substring($tempPath.Length + 1)
    
    # 检查是否是受保护的文件
    $isProtected = $false
    foreach ($protected in $protectedPaths) {
        if ($relativePath -eq $protected) {
            $isProtected = $true
            Write-Host "  ⏭️  跳过受保护文件: $relativePath" -ForegroundColor Yellow
            break
        }
    }
    
    if (-not $isProtected) {
        $destination = Join-Path $frontendPath $relativePath
        $destDir = Split-Path $destination -Parent
        
        # 确保目标目录存在
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        Copy-Item $_.FullName $destination -Recurse -Force
        Write-Host "  ✅ 复制: $relativePath" -ForegroundColor Gray
    }
}

# 步骤 3: 保留原始 LICENSE
Write-Host "[3/5] 保留 Convelyze 原始许可证..." -ForegroundColor Green
$licensePath = Join-Path $frontendPath "LICENSE"
if (Test-Path $licensePath) {
    Copy-Item $licensePath (Join-Path $frontendPath "LICENSE.convelyze") -Force
    Write-Host "  ✅ 已保存为 LICENSE.convelyze" -ForegroundColor Gray
}

# 步骤 4: 清理临时目录
Write-Host "[4/5] 清理临时文件..." -ForegroundColor Green
Remove-Item $tempPath -Recurse -Force

# 步骤 5: 创建环境变量文件
Write-Host "[5/5] 配置环境变量..." -ForegroundColor Green
$envExamplePath = Join-Path $frontendPath ".env.example"
$envLocalPath = Join-Path $frontendPath ".env.local"

if (-not (Test-Path $envLocalPath)) {
    Copy-Item $envExamplePath $envLocalPath -Force
    Write-Host "  ✅ 已创建 .env.local" -ForegroundColor Gray
} else {
    Write-Host "  ⏭️  .env.local 已存在，跳过" -ForegroundColor Yellow
}

# 完成
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  ✅ Convelyze 前端引入完成！" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 下一步操作：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 安装依赖：" -ForegroundColor White
Write-Host "   bun install" -ForegroundColor Gray
Write-Host "   # 或" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 配置环境变量（.env.local）：" -ForegroundColor White
Write-Host "   NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 启动开发服务器：" -ForegroundColor White
Write-Host "   bun run dev" -ForegroundColor Gray
Write-Host "   # 或" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 访问：" -ForegroundColor White
Write-Host "   http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 详细指南：" -ForegroundColor Cyan
Write-Host "   查看 INTEGRATION_GUIDE.md" -ForegroundColor Gray
Write-Host ""
