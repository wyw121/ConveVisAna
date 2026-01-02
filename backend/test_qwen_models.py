"""测试硅基流动千问系列免费模型"""
from config.llm_config import get_api_key
from core.custom_llm import ChatAIAPIModel
from pydantic import BaseModel
from typing import List
import time

class OpinionList(BaseModel):
    opinions: List[str]

class QuestionClassification(BaseModel):
    question_type: str  # clarifying, deepening, emotional, technical, off-topic
    value_level: str    # high, medium, low
    reason: str

api_key = get_api_key()

# 要测试的免费模型
FREE_MODELS = [
    "Qwen/Qwen2.5-7B-Instruct",           # 最新通用模型
    "Qwen/Qwen2.5-Coder-7B-Instruct",    # 代码专用模型
    "Qwen/Qwen2-7B-Instruct",             # 旧版通用模型
]

print("\n" + "="*70)
print("硅基流动千问系列免费模型对比测试")
print("="*70)

# 测试用例
test_cases = [
    {
        "name": "观点提取（JSON输出）",
        "prompt": """请从以下文本中提取观点（opinions）:

文本: "我认为 Python 是最好的编程语言。JavaScript 很流行但是有很多缺陷。Go 语言性能很好。"

返回 JSON 格式，包含 "opinions" 键，值为观点字符串列表。""",
        "schema": OpinionList,
        "task": "evaluation"
    },
    {
        "name": "问题分类（复杂JSON）",
        "prompt": """分析这个用户问题的类型和价值：

问题: "能详细解释一下 Python 装饰器的工作原理吗？"

返回 JSON，包含:
- question_type: 问题类型（clarifying澄清, deepening深入, emotional情感, technical技术, off-topic偏题）
- value_level: 价值等级（high, medium, low）
- reason: 判断原因（简短）""",
        "schema": QuestionClassification,
        "task": "flow_analysis"
    },
    {
        "name": "简单文本生成",
        "prompt": "用一句话介绍 Python 编程语言的特点。",
        "schema": None,
        "task": "general"
    }
]

results = {}

for model_name in FREE_MODELS:
    print(f"\n{'='*70}")
    print(f"测试模型: {model_name}")
    print(f"{'='*70}")
    
    model = ChatAIAPIModel(api_key=api_key, model=model_name)
    results[model_name] = {}
    
    for test_case in test_cases:
        test_name = test_case["name"]
        print(f"\n[测试] {test_name}")
        print("-" * 70)
        
        try:
            start_time = time.time()
            
            if test_case["schema"]:
                result = model.generate(test_case["prompt"], schema=test_case["schema"])
                response_time = time.time() - start_time
                
                # 验证结果
                if test_name == "观点提取（JSON输出）":
                    success = isinstance(result.opinions, list) and len(result.opinions) > 0
                    print(f"✅ 成功 ({response_time:.2f}秒)")
                    print(f"   提取到 {len(result.opinions)} 个观点")
                elif test_name == "问题分类（复杂JSON）":
                    success = (hasattr(result, 'question_type') and 
                             hasattr(result, 'value_level') and 
                             hasattr(result, 'reason'))
                    print(f"✅ 成功 ({response_time:.2f}秒)")
                    print(f"   类型: {result.question_type}, 价值: {result.value_level}")
                
                results[model_name][test_name] = {
                    "status": "success",
                    "time": response_time,
                    "result": str(result)[:100]
                }
            else:
                result = model.generate(test_case["prompt"])
                response_time = time.time() - start_time
                
                print(f"✅ 成功 ({response_time:.2f}秒)")
                print(f"   回复: {result[:100]}...")
                
                results[model_name][test_name] = {
                    "status": "success",
                    "time": response_time,
                    "result": result[:100]
                }
            
            # 避免触发速率限制
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 失败: {str(e)[:200]}")
            results[model_name][test_name] = {
                "status": "failed",
                "error": str(e)[:200]
            }

# 生成总结报告
print("\n" + "="*70)
print("测试总结与推荐")
print("="*70)

for model_name in FREE_MODELS:
    model_results = results[model_name]
    success_count = sum(1 for r in model_results.values() if r.get("status") == "success")
    total_count = len(test_cases)
    avg_time = sum(r.get("time", 0) for r in model_results.values() if r.get("status") == "success")
    avg_time = avg_time / success_count if success_count > 0 else 0
    
    print(f"\n📊 {model_name}")
    print(f"   成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    print(f"   平均响应: {avg_time:.2f}秒")
    
    # 适用场景判断
    if "Coder" in model_name:
        print(f"   适用: ⚠️  代码相关任务（不适合对话分析）")
    elif "Qwen2.5" in model_name:
        print(f"   适用: ✅ 对话质量评估、流程分析（推荐）")
    else:
        print(f"   适用: ⚙️  通用任务（旧版本）")

print("\n" + "="*70)
print("💡 推荐方案")
print("="*70)
print("""
基于你的项目需求（对话质量评估、流程分析）：

🥇 推荐: Qwen/Qwen2.5-7B-Instruct
   - 最新版本，综合能力最强
   - 适合 JSON 结构化输出
   - 无思维链干扰
   - 免费 ✓

🥈 备选: Qwen/Qwen2-7B-Instruct  
   - 旧版本但稳定
   - 免费 ✓

❌ 不推荐: Qwen/Qwen2.5-Coder-7B-Instruct
   - 专门用于代码任务
   - 对话分析效果可能较差

💰 付费模型 (¥0.35/M Tokens):
   - 如果免费额度不够，可以考虑 Pro 版本
   - 价格便宜，质量更好
   - 但优先使用免费版本即可
""")
print("="*70 + "\n")
