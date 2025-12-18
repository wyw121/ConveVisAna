"""
快速诊断脚本 - 不会中断后端服务
"""
import json
import sys

print("=" * 60)
print("🔍 ConveVisAna 前后端连接诊断")
print("=" * 60)

# 1. 检查后端环境变量
print("\n[1] 检查后端环境变量...")
try:
    from dotenv import load_dotenv
    import os
    
    # 加载 .env 文件
    env_path = r"d:\repositories\ConveVisAna\backend\.env"
    load_dotenv(env_path)
    
    api_key = os.getenv("CHATAIAPI_KEY")
    if api_key:
        print(f"✅ CHATAIAPI_KEY: {api_key[:15]}...{api_key[-10:]}")
    else:
        print("❌ CHATAIAPI_KEY 未找到")
        
except Exception as e:
    print(f"❌ 环境变量检查失败: {e}")

# 2. 检查前端环境变量
print("\n[2] 检查前端环境变量...")
try:
    with open(r"d:\repositories\ConveVisAna\frontend\.env.local", 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('NEXT_PUBLIC_BACKEND_BASE_URL'):
                print(f"✅ {line.strip()}")
                break
except Exception as e:
    print(f"❌ 前端环境变量检查失败: {e}")

# 3. 测试后端 API (使用 urllib，不会中断服务)
print("\n[3] 测试后端 API 连接...")
try:
    import urllib.request
    import urllib.error
    
    # 测试根路径
    try:
        with urllib.request.urlopen('http://localhost:8000/', timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ 后端根路径: {data}")
    except urllib.error.URLError as e:
        print(f"❌ 无法连接到 http://localhost:8000/: {e}")
    
    # 测试健康检查
    try:
        with urllib.request.urlopen('http://localhost:8000/api/health', timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ 健康检查响应:")
            print(f"   - status: {data.get('status')}")
            print(f"   - version: {data.get('version')}")
            print(f"   - api_available: {data.get('api_available')}")
            print(f"   - has_api_key: {data.get('has_api_key')}")
            
            if data.get('has_api_key'):
                print("✅ 后端报告: API Key 已配置")
            else:
                print("❌ 后端报告: API Key 未配置")
                
    except urllib.error.URLError as e:
        print(f"❌ 无法连接到 http://localhost:8000/api/health: {e}")
        
except Exception as e:
    print(f"❌ API 测试失败: {e}")

# 4. 检查端口占用
print("\n[4] 检查端口占用...")
import socket

def check_port(port, name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    if result == 0:
        print(f"✅ 端口 {port} ({name}) 正在监听")
        return True
    else:
        print(f"❌ 端口 {port} ({name}) 未监听")
        return False

backend_ok = check_port(8000, "后端")
frontend_ok = check_port(3000, "前端")

# 5. 总结
print("\n" + "=" * 60)
print("📊 诊断总结")
print("=" * 60)

if backend_ok and frontend_ok:
    print("✅ 前后端服务都在运行")
    print("\n建议操作:")
    print("1. 在浏览器中打开: http://localhost:3000/dashboard")
    print("2. 检查浏览器控制台的错误信息")
    print("3. 刷新页面 (Ctrl+F5 强制刷新)")
    print("\n如果前端仍显示'后端未配置',可能是:")
    print("- 前端需要重启以加载环境变量")
    print("- 浏览器缓存了旧的代码")
else:
    if not backend_ok:
        print("❌ 后端服务未运行")
        print("   运行: cd d:\\repositories\\ConveVisAna\\backend && python start_server.py")
    if not frontend_ok:
        print("❌ 前端服务未运行")
        print("   运行: cd d:\\repositories\\ConveVisAna\\frontend && npm run dev")

print("=" * 60)
