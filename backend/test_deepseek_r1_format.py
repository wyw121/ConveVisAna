"""测试 DeepSeek-R1 模型的响应格式处理"""
from config.llm_config import get_api_key, LLMConfig
from core.custom_llm import ChatAIAPIModel
from pydantic import BaseModel
from typing import List

# 定义测试用的 Schema
class OpinionList(BaseModel):
    opinions: List[str]

print("\n" + "="*60)
print("测试 DeepSeek-R1 JSON 输出格式")
print("="*60)

api_key = get_api_key()
model = ChatAIAPIModel(api_key=api_key, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")

# 测试 1: 无 schema 的普通文本响应
print("\n[测试 1] 普通文本响应")
try:
    response = model.generate("请用一句话介绍 Python")
    print(f"✅ 响应成功")
    print(f"内容: {response[:200]}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试 2: 带 schema 的 JSON 响应
print("\n[测试 2] JSON 格式响应 (带 schema)")
prompt = """请从以下文本中提取观点（opinions）:

文本: "我认为 Python 是最好的编程语言。JavaScript 很流行但是有很多缺陷。"

返回 JSON 格式，包含 "opinions" 键，值为观点列表。"""

try:
    result = model.generate(prompt, schema=OpinionList)
    print(f"✅ JSON 解析成功")
    print(f"类型: {type(result)}")
    print(f"观点列表: {result.opinions}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60 + "\n")
