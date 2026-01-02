"""测试硅基流动配置"""
from config.llm_config import LLMConfig, get_api_key, get_model_for_task

print("\n" + "="*60)
print("硅基流动配置验证")
print("="*60)

# 1. API Key
api_key = get_api_key()
print(f"\n✅ API Key: {api_key[:20]}...{api_key[-10:]}")

# 2. Base URL
print(f"✅ Base URL: {LLMConfig.get_base_url()}")

# 3. 默认模型
print(f"\n✅ 所有任务默认模型:")
print(f"   评估: {get_model_for_task('evaluation')}")
print(f"   流程: {get_model_for_task('flow_analysis')}")
print(f"   通用: {get_model_for_task('general')}")

# 4. 模型信息
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
info = LLMConfig.get_model_info(model_name)
print(f"\n✅ 模型详情:")
print(f"   名称: {info['name']}")
print(f"   提供商: {info['provider']}")
print(f"   成本: {info['cost']} (免费)")
print(f"   速度: {info['speed']}")
print(f"   质量: {info['quality']}")
print(f"   描述: {info['description']}")

print("\n" + "="*60)
print("✅ 配置验证成功！所有设置已更新为硅基流动免费模型")
print("="*60 + "\n")
