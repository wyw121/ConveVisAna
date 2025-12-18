"""
直接测试 ChatAIAPI 原始调用
根据你提供的代码示例进行测试
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('CHATAI_API_KEY')
base_url = "https://www.chataiapi.com/v1"

print("=" * 70)
print("直接测试 ChatAIAPI (根据你提供的代码示例)")
print("=" * 70)
print()

# 尝试不同的模型名称
test_models = [
    # 你原始代码中的示例
    "claude-3-5-sonnet-20240620",
    
    # 其他可能的名称
    "gpt-4o-mini",
    "gpt-4",
    "gpt-3.5-turbo",
    "gemini-pro",
    "deepseek-chat",
]

for model_name in test_models:
    print(f"测试模型: {model_name}")
    print("-" * 70)
    
    payload = json.dumps({
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "hello"
            }
        ]
    })
    
    url = base_url + "/chat/completions"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        # 解析响应
        data = response.json()
        
        if response.status_code == 200:
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"成功! 回复: {content}")
            print()
        else:
            error_msg = data.get('error', {}).get('message', str(data))
            print(f"失败! 错误: {error_msg}")
            print()
            
    except Exception as e:
        print(f"异常: {e}")
        print()

print()
print("=" * 70)
print("如果所有模型都失败，请:")
print("1. 检查你购买的 API 文档，查看正确的模型名称")
print("2. 联系 API 服务商客服")
print("3. 可能需要在后台配置或激活对应的模型渠道")
print("=" * 70)
