"""
对话流程分析器 - 分析整个对话的发展过程
针对完整对话链条,识别关键问题、无效问题、话题转折等
"""
from typing import List, Dict, Any
from deepeval.test_case import LLMTestCase
from deepeval.metrics import BaseMetric
from pydantic import BaseModel
import json


class QuestionClassification(BaseModel):
    """问题分类结果"""
    question_type: str  # clarifying, deepening, emotional, technical, off-topic
    value_level: str  # high, medium, low
    reason: str


class TurnAnalysis(BaseModel):
    """单轮对话分析"""
    turn_index: int
    question_classification: QuestionClassification
    builds_on_previous: bool
    topic_shift: bool


class ConversationFlowAnalyzer:
    """对话流程分析器"""
    
    def __init__(self, model):
        """
        Args:
            model: LLM 模型实例(用于分析)
        """
        self.model = model
    
    def analyze_conversation_flow(
        self, 
        conversation_turns: List[Dict[str, str]],
        conversation_title: str = ""
    ) -> Dict[str, Any]:
        """
        分析完整对话流程
        
        Args:
            conversation_turns: 对话回合列表 [{"question": "...", "answer": "..."}, ...]
            conversation_title: 对话标题
            
        Returns:
            分析结果字典
        """
        print(f"\n分析对话流程: {conversation_title}")
        print(f"总回合数: {len(conversation_turns)}")
        
        results = {
            'conversation_title': conversation_title,
            'total_turns': len(conversation_turns),
            'turn_analysis': [],
            'high_value_turns': [],
            'low_value_turns': [],
            'topic_shifts': [],
            'flow_summary': {}
        }
        
        # 逐轮分析
        for idx, turn in enumerate(conversation_turns):
            print(f"\n分析第 {idx+1}/{len(conversation_turns)} 轮...")
            
            turn_result = self._analyze_single_turn(
                turn,
                idx,
                conversation_turns[:idx] if idx > 0 else []
            )
            
            results['turn_analysis'].append(turn_result)
            
            # 分类存储
            if turn_result['value_level'] == 'high':
                results['high_value_turns'].append({
                    'turn_index': idx + 1,
                    'question': turn['question'],
                    'type': turn_result['question_type'],
                    'reason': turn_result['reason']
                })
            elif turn_result['value_level'] == 'low':
                results['low_value_turns'].append({
                    'turn_index': idx + 1,
                    'question': turn['question'],
                    'type': turn_result['question_type'],
                    'reason': turn_result['reason']
                })
            
            if turn_result.get('topic_shift'):
                results['topic_shifts'].append({
                    'turn_index': idx + 1,
                    'question': turn['question']
                })
        
        # 生成流程摘要
        results['flow_summary'] = self._generate_flow_summary(results)
        
        return results
    
    def _analyze_single_turn(
        self,
        turn: Dict[str, str],
        turn_index: int,
        previous_turns: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """分析单个对话回合"""
        
        # 构建分析提示词
        context = "\n\n".join([
            f"问题 {i+1}: {t['question']}\n回答 {i+1}: {t['answer']}"
            for i, t in enumerate(previous_turns[-2:])  # 只看最近2轮
        ])
        
        prompt = f"""你是一个对话质量分析专家。分析以下用户问题的价值和类型。

{'前两轮对话:\n' + context if context else '这是对话的第一轮'}

当前问题: {turn['question']}

请分析:
1. 问题类型(question_type):
   - clarifying: 澄清性问题(要求解释、举例)
   - deepening: 深入性问题(深挖细节、探讨方案)
   - emotional: 情感性问题(求助、倾诉)
   - technical: 技术性问题(how-to、troubleshooting)
   - off-topic: 偏题/闲聊

2. 价值等级(value_level):
   - high: 高价值(能引发有用回答)
   - medium: 中等价值
   - low: 低价值(无意义/重复)

3. 是否基于前文(builds_on_previous): true/false
4. 是否话题转移(topic_shift): true/false
5. 原因(reason): 简短说明判断依据

以 JSON 格式返回。
"""

        try:
            # 调用 LLM 分析
            response_text = self.model.generate(prompt, schema=None)
            
            # 解析 JSON
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            
            return {
                'turn_index': turn_index + 1,
                'question': turn['question'][:100] + '...' if len(turn['question']) > 100 else turn['question'],
                'question_type': analysis.get('question_type', 'unknown'),
                'value_level': analysis.get('value_level', 'medium'),
                'builds_on_previous': analysis.get('builds_on_previous', False),
                'topic_shift': analysis.get('topic_shift', False),
                'reason': analysis.get('reason', '')
            }
        except Exception as e:
            print(f"  分析失败: {e}")
            return {
                'turn_index': turn_index + 1,
                'question': turn['question'][:100],
                'question_type': 'unknown',
                'value_level': 'medium',
                'builds_on_previous': False,
                'topic_shift': False,
                'reason': f'分析出错: {str(e)}'
            }
    
    def _generate_flow_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成对话流程摘要"""
        
        total = results['total_turns']
        high_count = len(results['high_value_turns'])
        low_count = len(results['low_value_turns'])
        shift_count = len(results['topic_shifts'])
        
        # 统计问题类型
        type_counts = {}
        for turn in results['turn_analysis']:
            qtype = turn['question_type']
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        return {
            'total_turns': total,
            'high_value_ratio': high_count / total if total > 0 else 0,
            'low_value_ratio': low_count / total if total > 0 else 0,
            'topic_shifts_count': shift_count,
            'question_type_distribution': type_counts,
            'efficiency_score': (high_count - low_count) / total if total > 0 else 0
        }
    
    def save_analysis(self, results: Dict[str, Any], output_path: str):
        """保存分析结果"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n对话流程分析已保存: {output_path}")


def main():
    """演示用法"""
    from custom_llm import create_deepseek_chat
    import os
    from dotenv import load_dotenv
    from core.data_loader import ChatDataLoader
    
    load_dotenv()
    
    # 创建模型
    api_key = os.getenv('CHATAI_API_KEY')
    model = create_deepseek_chat(api_key)
    
    # 加载对话数据
    data_path = "f6eaf8f0f71aa12e8832082345edd8f0ed475ded4fc40fb0ca9780a596497ada-2025-11-18-01-38-19-c9c652a5f61b4d3f862e60633a9f144a"
    loader = ChatDataLoader(data_path)
    conversations = loader.load_conversations()
    
    print(f"加载了 {len(conversations)} 个对话\n")
    
    # 查找回合数最多的对话
    longest_conv = None
    max_turns = 0
    
    for i, conv in enumerate(conversations):
        turns = loader.get_conversation_turns(conv)
        print(f"{i+1}. {conv.title}: {len(turns)} 回合")
        if len(turns) > max_turns:
            max_turns = len(turns)
            longest_conv = conv
    
    # 分析回合数最多的对话
    if longest_conv:
        print(f"\n选择分析: {longest_conv.title} ({max_turns} 回合)\n")
        
        turns = loader.get_conversation_turns(longest_conv)
        
        if turns:
            # 创建分析器
            analyzer = ConversationFlowAnalyzer(model)
            
            # 分析对话流程
            results = analyzer.analyze_conversation_flow(
                turns,
                longest_conv.title
            )
            
            # 保存结果
            output_path = 'evaluation_results/conversation_flow_analysis.json'
            analyzer.save_analysis(results, output_path)
            
            # 打印摘要
            print("\n" + "="*60)
            print("对话流程分析摘要")
            print("="*60)
            summary = results['flow_summary']
            print(f"总回合数: {summary['total_turns']}")
            print(f"高价值问题比例: {summary['high_value_ratio']:.1%}")
            print(f"低价值问题比例: {summary['low_value_ratio']:.1%}")
            print(f"话题转移次数: {summary['topic_shifts_count']}")
            print(f"对话效率分数: {summary['efficiency_score']:.2f}")
            
            print("\n问题类型分布:")
            for qtype, count in summary['question_type_distribution'].items():
                print(f"  {qtype}: {count} 次")
            
            print("\n高价值问题:")
            for item in results['high_value_turns'][:5]:
                q = item['question'][:60] + '...' if len(item['question']) > 60 else item['question']
                print(f"  第{item['turn_index']}轮 [{item['type']}]: {q}")
                print(f"    → {item['reason']}")
            
            print("\n低价值问题:")
            for item in results['low_value_turns'][:5]:
                q = item['question'][:60] + '...' if len(item['question']) > 60 else item['question']
                print(f"  第{item['turn_index']}轮 [{item['type']}]: {q}")
                print(f"    → {item['reason']}")


if __name__ == '__main__':
    main()
