"""测试更新后的配置是否正常工作"""
from config.llm_config import get_api_key, get_model_for_task, LLMConfig
from core.custom_llm import ChatAIAPIModel

print("\n" + "="*60)
print("测试硅基流动免费模型集成")
print("="*60)

# 1. 获取配置
api_key = get_api_key()
model = get_model_for_task("evaluation")

print(f"\n✅ API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"✅ 模型: {model}")
print(f"✅ Base URL: {LLMConfig.get_base_url()}")

# 2. 创建 LLM 实例
llm = ChatAIAPIModel(api_key=api_key, model=model)
print(f"\n✅ LLM 初始化成功")

# 3. 测试简单调用
print(f"\n🔄 测试 API 调用...")
try:
    response = llm.generate("你好，请回复'测试成功'")
    print(f"✅ API 调用成功！")
    print(f"📝 模型回复: {response[:100]}")
    print("\n" + "="*60)
    print("✅ 所有测试通过！配置正确，可以正常使用")
    print("="*60 + "\n")
except Exception as e:
    print(f"❌ API 调用失败: {str(e)}")
    print("\n请检查:")
    print("1. API Key 是否正确")
    print("2. 硅基流动账户是否有可用额度")
    print("3. 是否需要完成身份验证")
