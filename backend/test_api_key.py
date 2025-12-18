"""
测试 API Key 是否可用
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("CHATAIAPI_KEY")

if not api_key:
    print("❌ 未找到 API Key")
    exit(1)

print(f"✅ API Key: {api_key[:20]}...{api_key[-10:]}")
print("\n正在测试 API Key...")

# 测试 ChatAIAPI 端点
try:
    # 根据你提供的API,这应该是一个兼容 OpenAI 的接口
    # 常见的转发服务通常使用这个端点
    response = requests.post(
        "https://api.chataiapi.com/v1/chat/completions",  # 根据实际服务调整
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "测试连接，请回复'OK'"}
            ],
            "max_tokens": 10
        },
        timeout=10
    )
    
    print(f"\n状态码: {response.status_code}")
    print(f"响应: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✅ API Key 有效！")
    else:
        print(f"\n⚠️ API 返回错误: {response.status_code}")
        print(f"详情: {response.text}")
        
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
