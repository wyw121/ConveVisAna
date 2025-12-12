"""
严格按照商家教程测试 Gemini 模型
用代码事实证明该 API 是否支持 Gemini
"""
import requests
import json
from openai import OpenAI

# 商家提供的信息
BASEURL = "https://www.chataiapi.com/v1"
API_KEY = "sk-imaEI6SqImBTTfAn8wvPiIN5oHelnY0iRbPe4CKLrDqe4pEV"

print("=" * 80)
print("测试报告: 商家 API 对 Gemini 模型的支持情况")
print("=" * 80)
print(f"API Base URL: {BASEURL}")
print(f"测试时间: 2025-01-18")
print(f"测试依据: 商家提供的官方教程代码\n")

# ============================================================================
# 测试 1: 使用商家教程的第一种方式 (requests 库)
# ============================================================================
print("\n" + "=" * 80)
print("【测试 1】使用商家教程示例代码 - requests 方式调用 Gemini")
print("=" * 80)

gemini_models = [
    "gemini-1.5-pro",
    "gemini-1.5-flash", 
    "gemini-pro",
    "gemini-2.0-flash-exp",
    "gemini-exp-1206"
]

for model_name in gemini_models:
    print(f"\n测试模型: {model_name}")
    print("-" * 80)
    
    # 完全按照商家教程的格式
    payload = json.dumps({
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "hello"
            }
        ]
    })
    
    # 商家教程的 URL 拼接有误,这里按教程原样
    url = BASEURL + "/chat/completions"
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(f"✓ HTTP 状态码: {response.status_code}")
        
        # 解析响应
        data = response.json()
        print(f"✓ 响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 检查是否成功
        if response.status_code == 200 and 'choices' in data:
            content = data['choices'][0]['message']['content']
            print(f"✅ 模型 {model_name} 调用成功!")
            print(f"   回复内容: {content}")
        else:
            print(f"❌ 模型 {model_name} 调用失败!")
            if 'error' in data:
                print(f"   错误信息: {data['error']}")
    
    except Exception as e:
        print(f"❌ 请求异常: {e}")

# ============================================================================
# 测试 2: 使用商家教程的第二种方式 (OpenAI 客户端)
# ============================================================================
print("\n\n" + "=" * 80)
print("【测试 2】使用商家教程示例代码 - OpenAI 客户端方式调用 Gemini")
print("=" * 80)

client = OpenAI(
    api_key=API_KEY,
    base_url=BASEURL
)

for model_name in gemini_models:
    print(f"\n测试模型: {model_name}")
    print("-" * 80)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "hello"
                }
            ],
            max_tokens=100
        )
        
        print(f"✅ 模型 {model_name} 调用成功!")
        print(f"   回复内容: {response.choices[0].message.content}")
    
    except Exception as e:
        print(f"❌ 模型 {model_name} 调用失败!")
        print(f"   错误信息: {str(e)}")

# ============================================================================
# 测试 3: 测试商家声称支持的模型
# ============================================================================
print("\n\n" + "=" * 80)
print("【测试 3】测试商家声称支持的其他模型 (对比验证)")
print("=" * 80)

control_models = [
    "claude-3-5-sonnet-20240620",  # 商家教程中的示例模型
    "deepseek-chat",               # 已知可用的模型
    "gpt-3.5-turbo",              # 常见的 OpenAI 模型
]

for model_name in control_models:
    print(f"\n测试模型: {model_name}")
    print("-" * 80)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "hello"
                }
            ],
            max_tokens=100
        )
        
        print(f"✅ 模型 {model_name} 调用成功!")
        print(f"   回复内容: {response.choices[0].message.content}")
    
    except Exception as e:
        print(f"❌ 模型 {model_name} 调用失败!")
        print(f"   错误信息: {str(e)}")

# ============================================================================
# 测试 4: 尝试获取支持的模型列表
# ============================================================================
print("\n\n" + "=" * 80)
print("【测试 4】尝试获取 API 支持的模型列表")
print("=" * 80)

try:
    models_response = client.models.list()
    print("✓ 成功获取模型列表:")
    print("-" * 80)
    for model in models_response.data:
        print(f"  - {model.id}")
        if 'gemini' in model.id.lower():
            print(f"    ✅ 发现 Gemini 模型!")
except Exception as e:
    print(f"❌ 无法获取模型列表: {str(e)}")

# ============================================================================
# 总结报告
# ============================================================================
print("\n\n" + "=" * 80)
print("📊 测试总结")
print("=" * 80)
print("""
本次测试严格按照商家提供的教程代码进行:
1. ✓ 使用了商家提供的 Base URL
2. ✓ 使用了商家提供的 API Key  
3. ✓ 使用了商家教程中的两种调用方式
4. ✓ 测试了多个 Gemini 模型版本

测试结果将清楚显示:
- 哪些模型可以正常调用
- 哪些模型返回错误
- 错误的具体原因

如果 Gemini 模型全部失败,而其他模型(如 Claude/DeepSeek)成功,
则可以证明商家的 API 不支持 Gemini,与教程是否正确无关。
""")
