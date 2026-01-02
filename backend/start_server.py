"""
快速启动后端 API 服务器
"""
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 检查 API Key
api_key = (
    os.getenv("API_KEY_OVERRIDE")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("CHATAIAPI_KEY")
    or os.getenv("CHATAI_API_KEY")
)
if not api_key:
    print("⚠️  警告: 未检测到 API Key")
    print("请在 .env 文件中设置以下之一:")
    print("  - OPENAI_API_KEY")
    print("  - CHATAIAPI_KEY")
    print("  - CHATAI_API_KEY")
    print("或在终端临时设置:")
    print("  - API_KEY_OVERRIDE (优先级最高)")
    print()

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 60)
    print("🚀 ConveVisAna Backend API Server")
    print("=" * 60)
    print(f"📍 服务地址: http://localhost:{port}")
    print(f"📚 API 文档: http://localhost:{port}/docs")
    print(f"🔑 API Key: {'✅ 已配置' if api_key else '❌ 未配置'}")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
