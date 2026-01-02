"""
测试 SiliconFlow API 密钥和 DeepSeek 模型
"""
import requests
import time
from typing import Dict, Any

# SiliconFlow API 配置
API_KEY = "sk-pgorpekchnscrzsupkywglclsxxouuhzjtiierkcxaoxxxqu"
BASE_URL = "https://api.siliconflow.cn/v1"

# 要测试的模型
MODELS_TO_TEST = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "deepseek-ai/DeepSeek-V3.2"
]

def test_model(model_name: str) -> Dict[str, Any]:
    """
    测试指定的模型
    
    Args:
        model_name: 模型名称
        
    Returns:
        测试结果字典
    """
    print(f"\n{'='*60}")
    print(f"测试模型: {model_name}")
    print(f"{'='*60}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user", 
                "content": "你好！请简单介绍一下你自己，包括你的名字和主要功能。"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    result = {
        "model": model_name,
        "status": "unknown",
        "response_time": 0,
        "error": None,
        "response_content": None
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        result["response_time"] = time.time() - start_time
        
        print(f"HTTP 状态码: {response.status_code}")
        print(f"响应时间: {result['response_time']:.2f} 秒")
        
        if response.status_code == 200:
            data = response.json()
            result["status"] = "success"
            result["response_content"] = data['choices'][0]['message']['content']
            
            print(f"\n✅ [成功] 模型可用！")
            print(f"\n模型回复:")
            print(f"{'─'*60}")
            print(result["response_content"])
            print(f"{'─'*60}")
            
            # 显示使用的 token 数量
            if 'usage' in data:
                usage = data['usage']
                print(f"\nToken 使用情况:")
                print(f"  - 提示词: {usage.get('prompt_tokens', 'N/A')}")
                print(f"  - 完成: {usage.get('completion_tokens', 'N/A')}")
                print(f"  - 总计: {usage.get('total_tokens', 'N/A')}")
        else:
            result["status"] = "failed"
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            
            print(f"\n❌ [失败] 请求失败")
            print(f"错误信息:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "请求超时 (>60秒)"
        print(f"\n⏱️ [超时] 请求超时")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"\n❌ [错误] 发生异常: {str(e)}")
    
    return result

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("SiliconFlow API 密钥测试")
    print("="*60)
    print(f"API 密钥: {API_KEY[:20]}...{API_KEY[-10:]}")
    print(f"API 地址: {BASE_URL}")
    print(f"待测试模型数: {len(MODELS_TO_TEST)}")
    
    results = []
    
    # 测试每个模型
    for model in MODELS_TO_TEST:
        result = test_model(model)
        results.append(result)
        time.sleep(2)  # 避免请求过快
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    success_count = 0
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"\n{status_icon} {result['model']}")
        print(f"   状态: {result['status']}")
        print(f"   响应时间: {result['response_time']:.2f} 秒")
        
        if result["error"]:
            print(f"   错误: {result['error']}")
        
        if result["status"] == "success":
            success_count += 1
    
    print("\n" + "="*60)
    print(f"测试完成: {success_count}/{len(results)} 个模型可用")
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()
