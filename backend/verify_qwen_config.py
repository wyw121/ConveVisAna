"""验证 Qwen2.5 配置更新"""
from config.llm_config import LLMConfig

print("="*70)
print("Qwen2.5 配置验证")
print("="*70)

# 检查默认模型
print("\n📋 默认模型配置：")
print(f"   评估任务:    {LLMConfig.get_default_model('evaluation')}")
print(f"   流程分析:    {LLMConfig.get_default_model('flow_analysis')}")
print(f"   通用任务:    {LLMConfig.get_default_model('general')}")

# 检查模型信息
print("\n📊 Qwen2.5 模型详情：")
model_info = LLMConfig.get_model_info("Qwen/Qwen2.5-7B-Instruct")
if model_info:
    print(f"   名称:        {model_info['name']}")
    print(f"   提供商:      {model_info['provider']}")
    print(f"   费用:        {model_info['cost']}")
    print(f"   速度:        {model_info['speed']}")
    print(f"   质量:        {model_info['quality']}")
    print(f"   描述:        {model_info['description']}")
    if 'test_results' in model_info:
        print(f"\n   测试结果:")
        print(f"     成功率:       {model_info['test_results']['success_rate']}")
        print(f"     平均响应:     {model_info['test_results']['avg_response_time']}秒")
        print(f"     JSON兼容性:   {model_info['test_results']['json_compatibility']}")

# 验证所有任务都使用 Qwen2.5
print("\n✅ 配置状态检查：")
all_qwen = True
for task in ["evaluation", "flow_analysis", "general"]:
    model = LLMConfig.get_default_model(task)
    is_qwen = model == "Qwen/Qwen2.5-7B-Instruct"
    status = "✅" if is_qwen else "❌"
    print(f"   {status} {task}: {model}")
    if not is_qwen:
        all_qwen = False

if all_qwen:
    print("\n🎉 配置完成！所有任务已统一使用 Qwen/Qwen2.5-7B-Instruct")
    print("\n💡 下一步：")
    print("   1. 重启后端服务：python backend/start_server.py")
    print("   2. 测试评估接口，验证 JSON 输出正常")
else:
    print("\n⚠️  警告：部分任务未使用 Qwen2.5，请检查配置")

print("="*70)
