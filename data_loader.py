"""
GPT 聊天数据加载和预处理模块
用于将导出的 ChatGPT 对话数据转换为 deepeval 可评估的格式
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """单条消息"""
    role: str  # 'user' or 'assistant'
    content: str
    create_time: float
    message_id: str


@dataclass
class Conversation:
    """完整对话"""
    conversation_id: str
    title: str
    create_time: float
    messages: List[Message]


class ChatDataLoader:
    """加载和处理 ChatGPT 导出数据"""
    
    def __init__(self, data_folder: str):
        """
        初始化数据加载器
        
        Args:
            data_folder: 包含 conversations.json 的文件夹路径
        """
        self.data_folder = Path(data_folder)
        self.conversations_file = self.data_folder / "conversations.json"
        
    def load_conversations(self) -> List[Conversation]:
        """
        加载所有对话
        
        Returns:
            对话列表
        """
        if not self.conversations_file.exists():
            raise FileNotFoundError(f"找不到文件: {self.conversations_file}")
            
        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversations = []
        for conv_data in data:
            conv = self._parse_conversation(conv_data)
            if conv and len(conv.messages) > 0:
                conversations.append(conv)
                
        return conversations
    
    def _parse_conversation(self, conv_data: Dict) -> Optional[Conversation]:
        """
        解析单个对话数据
        
        Args:
            conv_data: 对话的原始数据
            
        Returns:
            解析后的对话对象
        """
        try:
            conv_id = conv_data.get('id', '')
            title = conv_data.get('title', 'Untitled')
            create_time = conv_data.get('create_time', 0)
            mapping = conv_data.get('mapping', {})
            
            # 提取消息
            messages = self._extract_messages(mapping)
            
            return Conversation(
                conversation_id=conv_id,
                title=title,
                create_time=create_time,
                messages=messages
            )
        except Exception as e:
            print(f"解析对话失败: {e}")
            return None
    
    def _extract_messages(self, mapping: Dict) -> List[Message]:
        """
        从 mapping 中提取有序的消息列表
        
        Args:
            mapping: 对话的 mapping 数据
            
        Returns:
            消息列表
        """
        messages = []
        
        # 找到根节点
        root_id = None
        for node_id, node in mapping.items():
            if node.get('parent') is None:
                root_id = node_id
                break
        
        if not root_id:
            return messages
        
        # 遍历对话树
        current_id = root_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            node = mapping.get(current_id)
            
            if not node:
                break
                
            message_data = node.get('message')
            if message_data:
                msg = self._parse_message(message_data)
                if msg:
                    messages.append(msg)
            
            # 移动到第一个子节点
            children = node.get('children', [])
            current_id = children[0] if children else None
        
        return messages
    
    def _parse_message(self, message_data: Dict) -> Optional[Message]:
        """
        解析单条消息
        
        Args:
            message_data: 消息的原始数据
            
        Returns:
            解析后的消息对象
        """
        try:
            author = message_data.get('author', {})
            role = author.get('role', '')
            
            # 只处理 user 和 assistant 的消息
            if role not in ['user', 'assistant']:
                return None
            
            content = message_data.get('content', {})
            parts = content.get('parts', [])
            
            # 提取文本内容
            text_content = self._extract_text_from_parts(parts)
            
            if not text_content:
                return None
            
            return Message(
                role=role,
                content=text_content,
                create_time=message_data.get('create_time', 0),
                message_id=message_data.get('id', '')
            )
        except Exception as e:
            print(f"解析消息失败: {e}")
            return None
    
    def _extract_text_from_parts(self, parts: List) -> str:
        """
        从 parts 中提取文本内容
        
        Args:
            parts: 消息的 parts 数组
            
        Returns:
            合并后的文本内容
        """
        texts = []
        for part in parts:
            if isinstance(part, str):
                texts.append(part)
            elif isinstance(part, dict):
                # 处理 audio_transcription 类型
                if part.get('content_type') == 'audio_transcription':
                    text = part.get('text', '')
                    if text:
                        texts.append(text)
                # 处理其他文本类型
                elif 'text' in part:
                    texts.append(part['text'])
        
        return ' '.join(texts).strip()
    
    def get_qa_pairs(self, conversation: Conversation) -> List[Dict[str, str]]:
        """
        将对话转换为问答对
        
        Args:
            conversation: 对话对象
            
        Returns:
            问答对列表，每个元素包含 'input' 和 'actual_output'
        """
        qa_pairs = []
        
        for i in range(len(conversation.messages) - 1):
            current_msg = conversation.messages[i]
            next_msg = conversation.messages[i + 1]
            
            # 用户问题 -> 助手回答
            if current_msg.role == 'user' and next_msg.role == 'assistant':
                qa_pairs.append({
                    'input': current_msg.content,
                    'actual_output': next_msg.content,
                    'conversation_id': conversation.conversation_id,
                    'conversation_title': conversation.title
                })
        
        return qa_pairs
    
    def get_conversation_turns(self, conversation: Conversation) -> List[Dict[str, str]]:
        """
        获取完整对话流的所有回合(用于流程分析)
        
        Args:
            conversation: 对话对象
            
        Returns:
            对话回合列表，每个元素包含 'question' 和 'answer'
        """
        turns = []
        
        for i in range(len(conversation.messages) - 1):
            current_msg = conversation.messages[i]
            next_msg = conversation.messages[i + 1]
            
            # 用户问题 -> 助手回答
            if current_msg.role == 'user' and next_msg.role == 'assistant':
                turns.append({
                    'question': current_msg.content,
                    'answer': next_msg.content,
                    'turn_index': len(turns) + 1,
                    'timestamp': current_msg.create_time
                })
        
        return turns


if __name__ == '__main__':
    # 示例用法
    loader = ChatDataLoader('f6eaf8f0f71aa12e8832082345edd8f0ed475ded4fc40fb0ca9780a596497ada-2025-11-18-01-38-19-c9c652a5f61b4d3f862e60633a9f144a')
    
    conversations = loader.load_conversations()
    print(f"加载了 {len(conversations)} 个对话")
    
    # 展示第一个对话的问答对
    if conversations:
        first_conv = conversations[0]
        print(f"\n对话标题: {first_conv.title}")
        print(f"消息数量: {len(first_conv.messages)}")
        
        qa_pairs = loader.get_qa_pairs(first_conv)
        print(f"问答对数量: {len(qa_pairs)}")
        
        if qa_pairs:
            print("\n第一个问答对:")
            print(f"问题: {qa_pairs[0]['input'][:100]}...")
            print(f"回答: {qa_pairs[0]['actual_output'][:100]}...")
