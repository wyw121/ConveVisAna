"""
自定义 LLM 适配器 - 使用 chataiapi.com 的转发 API
支持 OpenAI 和 Claude 模型
"""
from typing import Optional, Dict, Any, Type
from deepeval.models.base_model import DeepEvalBaseLLM
from pydantic import BaseModel
import requests
import json


class ChatAIAPIModel(DeepEvalBaseLLM):
    """
    ChatAIAPI 的自定义 LLM 模型适配器
    支持通过 chataiapi.com 调用 OpenAI 和 Claude 模型
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://www.chataiapi.com/v1"
    ):
        """
        初始化自定义 LLM 模型
        
        Args:
            api_key: ChatAIAPI 的 API Key
            model: 模型名称，例如:
                   - deepseek-chat (你的API支持，推荐)
                   - 其他模型需要在API后台配置渠道
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self._requested_model = model  # 保存用户请求的模型名称
        self.base_url = base_url.rstrip('/')
        
        # 调用父类初始化 - 这会调用 load_model() 并设置 self.model
        super().__init__()
    
    def load_model(self):
        """加载模型 - 返回模型名称供父类使用"""
        return self._requested_model
    
    def generate(self, prompt: str, schema: Optional[BaseModel] = None):
        """
        生成响应
        
        Args:
            prompt: 输入提示
            schema: Pydantic BaseModel (deepeval 用于结构化输出)
            
        Returns:
            如果有 schema: 返回 Pydantic 模型实例
            如果无 schema: 返回字符串
        """
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # DeepSeek 需要特殊处理 JSON 输出
        # 如果有 schema,添加系统提示要求返回 JSON
        if schema:
            messages.insert(0, {
                "role": "system",
                "content": "You must respond with valid JSON only."
            })
        
        response_text = self._call_api(messages, schema)
        
        # 如果提供了 schema,将 JSON 字符串解析为 Pydantic 对象
        if schema:
            try:
                # 处理 markdown 代码块格式
                response_text = response_text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # 移除 ```json
                if response_text.startswith('```'):
                    response_text = response_text[3:]  # 移除 ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # 移除结尾 ```
                response_text = response_text.strip()
                
                response_dict = json.loads(response_text)
                return schema(**response_dict)
            except (json.JSONDecodeError, Exception) as e:
                print(f"JSON 解析失败: {e}")
                print(f"原始响应: {response_text[:500]}")
                raise
        
        return response_text
    
    async def a_generate(
        self, prompt: str, schema: Optional[BaseModel] = None
    ):
        """
        异步生成响应
        
        Args:
            prompt: 输入提示
            schema: Pydantic BaseModel
            
        Returns:
            如果有 schema: 返回 Pydantic 模型实例
            如果无 schema: 返回字符串
        """
        # 对于同步 API,直接调用同步方法
        # 如果需要真正的异步,可以使用 aiohttp
        return self.generate(prompt, schema)
    
    def _call_api(self, messages: list, schema: Optional[Dict] = None) -> str:
        """
        调用 ChatAIAPI
        
        Args:
            messages: 消息列表
            schema: JSON schema
            
        Returns:
            API 响应文本
        """
        # 根据你提供的示例，正确的 URL 格式
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,  # 使用父类设置的 self.model
            "messages": messages
        }
        
        # 如果提供了 schema,使用 JSON mode (仅支持部分模型)
        if schema:
            payload["response_format"] = {"type": "json_object"}
            print(f"\n{'='*60}")
            print(f"DEEPEVAL 请求 JSON 输出")
            print(f"{'='*60}")
            print(f"Schema 类型: {type(schema)}")
            if hasattr(schema, '__name__'):
                print(f"Schema 名称: {schema.__name__}")
            print(f"\n提示词前 800 字符:\n{messages[-1]['content'][:800]}")
            print(f"{'='*60}\n")
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        
        try:
            # 打印调试信息
            print(f"请求 URL: {url}")
            print(f"使用模型: {self.model}")
            
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            # 打印响应状态
            print(f"响应状态码: {response.status_code}")
            
            # 如果失败，打印详细错误信息
            if response.status_code != 200:
                print(f"错误响应: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            # 提取返回内容
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                
                if schema:
                    print(f"\n{'='*60}")
                    print("DEEPSEEK 响应")
                    print(f"{'='*60}")
                    print(f"响应前 800 字符:\n{content[:800]}")
                    print(f"{'='*60}\n")
                
                return content
            else:
                raise ValueError(f"API 返回格式异常: {data}")
                
        except requests.exceptions.RequestException as e:
            print(f"\n详细错误信息: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise RuntimeError(f"API 调用失败: {e}")
    
    def get_model_name(self) -> str:
        """返回模型名称"""
        return self.model


# 便捷函数：创建常用模型实例
def create_deepseek_chat(api_key: str) -> ChatAIAPIModel:
    """创建 DeepSeek Chat 模型 (你的API支持)"""
    return ChatAIAPIModel(api_key=api_key, model="deepseek-chat")


if __name__ == '__main__':
    # 测试代码
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('CHATAI_API_KEY')
    if not api_key:
        print("请在 .env 文件中设置 CHATAI_API_KEY")
        exit(1)
    
    # 创建模型
    model = create_deepseek_chat(api_key)
    
    # 测试生成
    response = model.generate("你好，请用一句话介绍你自己。")
    print(f"模型响应: {response}")
