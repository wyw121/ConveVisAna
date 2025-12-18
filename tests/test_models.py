"""
测试你的 ChatAIAPI 支持哪些模型
"""
import os
from dotenv import load_dotenv
from custom_llm import ChatAIAPIModel

load_dotenv()

# 根据错误信息，你的 API 支持这些模型分组
# Gemini, DeepSeek-Huoshan, Doubao-Huoshan, Chatgpt, Claude-官, 
# default, DeepSeek-Baidu, Qwen-Aliyun, DeepSeek, Chatgpt-官

# 让我们尝试一些可能的模型名称
test_models = [
    # Gemini 系列
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    
    # DeepSeek 系列
    "deepseek-chat",
    "deepseek-coder",
    
    # Claude 系列 (可能的名称)
    "claude-3-sonnet",
    "claude-3-haiku",
    "claude-3-opus",
    
    # Qwen 系列
    "qwen-turbo",
    "qwen-plus",
    "qwen-max",
    
    # 其他可能的模型
    "gpt-3.5-turbo",
    "gpt-4",
    "doubao",
]

api_key = os.getenv('CHATAI_API_KEY')
if not api_key:
    print("错误: 未找到 CHATAI_API_KEY")
    exit(1)

print("=" * 60)
print("测试你的 ChatAIAPI 支持的模型")
print("=" * 60)
print()

working_models = []

for model_name in test_models:
    print(f"测试模型: {model_name}")
    try:
        model = ChatAIAPIModel(api_key=api_key, model=model_name)
        response = model.generate("你好")
        print(f"  ✅ 成功! 响应: {response[:50]}...")
        working_models.append(model_name)
    except Exception as e:
        error_msg = str(e)
        if "均无可用渠道" in error_msg or "503" in error_msg:
            print(f"  ❌ 不支持")
        elif "400" in error_msg:
            print(f"  ❌ 请求格式错误")
        else:
            print(f"  ❌ 失败: {error_msg[:100]}")
    print()

print("=" * 60)
print("总结")
print("=" * 60)
if working_models:
    print(f"✅ 发现 {len(working_models)} 个可用模型:")
    for m in working_models:
        print(f"  - {m}")
else:
    print("❌ 没有找到可用的模型")
    print()
    print("建议:")
    print("1. 检查你的 API 服务商文档，查看支持的模型列表")
    print("2. 联系 API 服务商获取正确的模型名称")
    print("3. 错误信息显示支持: Gemini, DeepSeek, Doubao, Claude, Qwen")
