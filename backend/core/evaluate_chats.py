"""
使用 deepeval 对 GPT 聊天数据进行质量评估

支持的评估维度：
1. 答案相关性 (Answer Relevancy) - 回答是否与问题相关
2. 有用性 (Helpfulness) - 回答是否有帮助
3. 连贯性 (Coherence) - 回答是否连贯
4. 毒性检测 (Toxicity) - 是否包含有害内容
5. 偏见检测 (Bias) - 是否存在偏见
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
    BiasMetric,
    ToxicityMetric
)
from deepeval.test_case import LLMTestCaseParams

from core.data_loader import ChatDataLoader
from core.custom_llm import ChatAIAPIModel, create_deepseek_chat


# 加载环境变量
load_dotenv()


class ChatQualityEvaluator:
    """GPT 聊天质量评估器"""
    
    def __init__(
        self,
        data_folder: str,
        model: str = "gpt-4o-mini",
        use_custom_api: bool = True
    ):
        """
        初始化评估器
        
        Args:
            data_folder: 聊天数据文件夹路径
            model: 用于评估的模型，默认 gpt-4o-mini
            use_custom_api: 是否使用 ChatAIAPI (推荐)
                           True - 使用你购买的转发 API
                           False - 使用原生 OpenAI API
        """
        self.data_folder = data_folder
        self.model_name = model
        self.use_custom_api = use_custom_api
        self.loader = ChatDataLoader(data_folder)
        
        # 初始化自定义 LLM (如果使用)
        self.custom_llm = None
        if use_custom_api:
            api_key = os.getenv('CHATAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "使用自定义 API 需要设置 CHATAI_API_KEY 环境变量"
                )
            self.custom_llm = ChatAIAPIModel(api_key=api_key, model=model)
            print(f"[OK] 使用 ChatAIAPI 转发服务，模型: {model}")
        else:
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError(
                    "使用 OpenAI API 需要设置 OPENAI_API_KEY 环境变量"
                )
            print(f"[OK] 使用原生 OpenAI API，模型: {model}")
        
        # 初始化评估指标
        self.metrics = self._init_metrics()
    
    def _init_metrics(self) -> Dict:
        """初始化评估指标"""
        # 如果使用自定义 API，传递 model 参数
        model_param = self.custom_llm if self.use_custom_api else self.model_name
        
        return {
            # 1. 答案相关性 - 评估回答是否与问题相关
            'relevancy': AnswerRelevancyMetric(
                threshold=0.7,
                model=model_param,
                include_reason=True
            ),
            
            # 2. 有用性 - 评估回答是否有帮助
            'helpfulness': GEval(
                name="Helpfulness",
                criteria="评估助手的回答是否对用户有帮助，是否提供了有价值的信息或建议",
                evaluation_params=[
                    LLMTestCaseParams.INPUT,
                    LLMTestCaseParams.ACTUAL_OUTPUT
                ],
                threshold=0.7,
                model=model_param
            ),
            
            # 3. 连贯性 - 评估回答的逻辑性和连贯性
            'coherence': GEval(
                name="Coherence",
                criteria="评估回答的逻辑性、连贯性和易读性，回答是否结构清晰、表达流畅",
                evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
                threshold=0.7,
                model=model_param
            ),
            
            # 4. 共情能力 - 评估是否体现了共情和情感支持
            'empathy': GEval(
                name="Empathy",
                criteria="评估助手是否展现了共情能力，能否理解用户的情感状态并给予适当的情感支持",
                evaluation_params=[
                    LLMTestCaseParams.INPUT,
                    LLMTestCaseParams.ACTUAL_OUTPUT
                ],
                threshold=0.6,
                model=model_param
            ),
            
            # 5. 毒性检测
            'toxicity': ToxicityMetric(
                threshold=0.3,
                model=model_param
            ),
            
            # 6. 偏见检测
            'bias': BiasMetric(
                threshold=0.3,
                model=model_param
            )
        }
    
    def evaluate_conversation(
        self,
        conversation_id: str = None,
        max_qa_pairs: int = None,
        selected_metrics: List[str] = None
    ) -> Dict:
        """
        评估指定对话或所有对话
        
        Args:
            conversation_id: 要评估的对话ID，None 则评估所有对话
            max_qa_pairs: 最多评估的问答对数量，None 则评估所有
            selected_metrics: 要使用的指标列表，None 则使用所有指标
            
        Returns:
            评估结果字典
        """
        # 加载对话
        conversations = self.loader.load_conversations()
        
        if conversation_id:
            conversations = [c for c in conversations if c.conversation_id == conversation_id]
            if not conversations:
                raise ValueError(f"找不到对话ID: {conversation_id}")
        
        # 收集所有问答对
        all_qa_pairs = []
        for conv in conversations:
            qa_pairs = self.loader.get_qa_pairs(conv)
            all_qa_pairs.extend(qa_pairs)
        
        # 限制评估数量
        if max_qa_pairs:
            all_qa_pairs = all_qa_pairs[:max_qa_pairs]
        
        print(f"准备评估 {len(all_qa_pairs)} 个问答对...")
        
        # 选择要使用的指标
        if selected_metrics:
            metrics_to_use = [self.metrics[m] for m in selected_metrics if m in self.metrics]
        else:
            metrics_to_use = list(self.metrics.values())
        
        # 评估每个问答对
        results = []
        for i, qa in enumerate(all_qa_pairs, 1):
            print(f"\n评估问答对 {i}/{len(all_qa_pairs)}")
            print(f"对话: {qa['conversation_title']}")
            print(f"问题: {qa['input'][:100]}...")
            
            test_case = LLMTestCase(
                input=qa['input'],
                actual_output=qa['actual_output']
            )
            
            # 运行评估
            qa_result = {
                'conversation_id': qa['conversation_id'],
                'conversation_title': qa['conversation_title'],
                'input': qa['input'],
                'actual_output': qa['actual_output'],
                'scores': {}
            }
            
            for metric in metrics_to_use:
                try:
                    metric.measure(test_case)
                    metric_name = getattr(metric, '__name__', type(metric).__name__)
                    qa_result['scores'][metric_name] = {
                        'score': metric.score,
                        'reason': metric.reason if hasattr(metric, 'reason') else None,
                        'passed': metric.score >= metric.threshold
                    }
                    passed_str = 'PASS' if qa_result['scores'][metric_name]['passed'] else 'FAIL'
                    passed_mark = f"[{passed_str}]"
                    print(f"  {metric_name}: {metric.score:.3f} {passed_mark}")
                except Exception as e:
                    metric_name = getattr(metric, '__name__', type(metric).__name__)
                    print(f"  {metric_name}: 评估失败 - {str(e)[:100]}")
                    qa_result['scores'][metric_name] = {
                        'score': None,
                        'error': str(e)
                    }
            
            results.append(qa_result)
        
        return {
            'total_qa_pairs': len(results),
            'results': results,
            'summary': self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """生成评估摘要统计"""
        summary = {
            'total': len(results),
            'metrics': {}
        }
        
        # 统计每个指标
        for metric_name in self.metrics.keys():
            scores = [
                r['scores'][metric_name]['score'] 
                for r in results 
                if metric_name in r['scores'] and r['scores'][metric_name].get('score') is not None
            ]
            
            if scores:
                summary['metrics'][metric_name] = {
                    'average_score': sum(scores) / len(scores),
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'passed_count': sum(1 for r in results if r['scores'].get(metric_name, {}).get('passed', False)),
                    'total_evaluated': len(scores)
                }
        
        return summary
    
    def save_results(self, results: Dict, output_file: str):
        """保存评估结果到JSON文件"""
        import json
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n评估结果已保存到: {output_path}")
    
    def print_summary(self, results: Dict):
        """打印评估摘要"""
        summary = results['summary']
        
        print("\n" + "="*60)
        print("评估摘要")
        print("="*60)
        print(f"总问答对数: {summary['total']}")
        print("\n各指标得分:")
        print("-"*60)
        
        for metric_name, stats in summary['metrics'].items():
            print(f"\n{metric_name}:")
            print(f"  平均分: {stats['average_score']:.3f}")
            print(f"  最低分: {stats['min_score']:.3f}")
            print(f"  最高分: {stats['max_score']:.3f}")
            print(f"  通过率: {stats['passed_count']}/{stats['total_evaluated']} ({stats['passed_count']/stats['total_evaluated']*100:.1f}%)")


def main():
    """主函数 - 示例用法"""
    
    # 检查 API Key
    use_custom = os.getenv('CHATAI_API_KEY') is not None
    
    if use_custom:
        print("=" * 60)
        print("使用 ChatAIAPI 转发服务")
        print("=" * 60)
    else:
        if not os.getenv('OPENAI_API_KEY'):
            print("错误: 请在 .env 文件中设置以下任一 API Key:")
            print("  - CHATAI_API_KEY (推荐 - 你购买的转发 API)")
            print("  - OPENAI_API_KEY (原生 OpenAI API)")
            return
        print("=" * 60)
        print("使用原生 OpenAI API")
        print("=" * 60)
    
    # 指定数据文件夹
    data_folder = 'f6eaf8f0f71aa12e8832082345edd8f0ed475ded4fc40fb0ca9780a596497ada-2025-11-18-01-38-19-c9c652a5f61b4d3f862e60633a9f144a'
    
    # 创建评估器
    evaluator = ChatQualityEvaluator(
        data_folder,
        model='deepseek-chat',  # 你的API支持的模型
        use_custom_api=use_custom
    )
    
    # 运行评估
    # 示例1: 评估前3个问答对，使用所有指标 (快速测试)
    print("\n开始评估...")
    results = evaluator.evaluate_conversation(
        max_qa_pairs=3,
        selected_metrics=None  # None 表示使用所有指标
    )
    
    # 示例2: 只评估特定指标 (更快)
    # results = evaluator.evaluate_conversation(
    #     max_qa_pairs=5,
    #     selected_metrics=['relevancy', 'helpfulness', 'empathy']
    # )
    
    # 示例3: 使用 Claude 模型评估 (如果你想试试不同的模型)
    # evaluator_claude = ChatQualityEvaluator(
    #     data_folder,
    #     model='claude-3-haiku-20240307',
    #     use_custom_api=True
    # )
    # results = evaluator_claude.evaluate_conversation(max_qa_pairs=3)
    
    # 打印摘要
    evaluator.print_summary(results)
    
    # 保存结果
    evaluator.save_results(
        results,
        'evaluation_results/chat_quality_report.json'
    )


if __name__ == '__main__':
    main()
