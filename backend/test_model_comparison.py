"""测试 Qwen 模型的 JSON 输出"""
from config.llm_config import get_api_key, get_model_for_task, LLMConfig
from core.custom_llm import ChatAIAPIModel
from pydantic import BaseModel
from typing import List

class OpinionList(BaseModel):
    opinions: List[str]

print("\n" + "="*60)
print("测试硅基流动免费模型对比")
print("="*60)

api_key = get_api_key()

# 测试 1: Qwen 模型（推荐用于 JSON）
print("\n[模型 1] Qwen/Qwen2.5-7B-Instruct")
print("特点: 适合 JSON 输出，无思维链")
print("-" * 60)

qwen_model = ChatAIAPIModel(api_key=api_key, model="Qwen/Qwen2.5-7B-Instruct")

prompt = """请从以下文本中提取观点（opinions）:

文本: "我认为 Python 是最好的编程语言。JavaScript 很流行但是有很多缺陷。"

返回 JSON 格式，包含 "opinions" 键，值为观点列表。"""

try:
    result = qwen_model.generate(prompt, schema=OpinionList)
    print(f"✅ JSON 解析成功")
    print(f"观点列表: {result.opinions}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试 2: DeepSeek-R1 模型
print("\n[模型 2] deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
print("特点: 推理能力强，但会输出思维链")
print("-" * 60)

r1_model = ChatAIAPIModel(api_key=api_key, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")

try:
    result = r1_model.generate(prompt, schema=OpinionList)
    print(f"✅ JSON 解析成功")
    print(f"观点列表: {result.opinions}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 显示当前配置
print("\n" + "="*60)
print("当前默认模型配置:")
print("="*60)
print(f"评估任务: {get_model_for_task('evaluation')}")
print(f"流程分析: {get_model_for_task('flow_analysis')}")
print(f"通用任务: {get_model_for_task('general')}")
print("\n✅ 推荐: 评估任务使用 Qwen 模型，可避免思维链导致的 JSON 解析问题")
print("="*60 + "\n")
