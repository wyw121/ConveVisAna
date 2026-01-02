"""
自定义 LLM 适配器 - 使用硅基流动免费 API
支持 DeepSeek 等模型
"""
from typing import Optional, Dict, Any, Type
from deepeval.models.base_model import DeepEvalBaseLLM
from pydantic import BaseModel
import requests
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 导入配置中心
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.llm_config import LLMConfig


class ChatAIAPIModel(DeepEvalBaseLLM):
    """
    LLM 模型适配器 - 使用硅基流动免费 API
    支持 DeepSeek-R1-Distill-Qwen-7B 等模型
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None
    ):
        """
        初始化自定义 LLM 模型
        
        Args:
            api_key: API Key（默认从配置中心获取）
            model: 模型名称（默认使用配置中心的通用模型）
            base_url: API 基础 URL（默认从配置中心获取）
        """
        # 使用配置中心的默认值
        self.api_key = api_key or LLMConfig.get_api_key()
        self._requested_model = model or LLMConfig.get_default_model("general")
        self.base_url = (base_url or LLMConfig.get_base_url()).rstrip('/')
        
        # 使用配置中心的超时配置
        self._timeout = LLMConfig.get_timeout()
        
        # 使用配置中心的重试配置
        retry_config = LLMConfig.get_retry_config()
        retry_total = int(retry_config["total"])
        retry_backoff = float(retry_config["backoff"])
        status_forcelist = [429, 500, 502, 503, 504]
        retry = Retry(
            total=retry_total,
            connect=retry_total,
            read=retry_total,
            status=retry_total,
            backoff_factor=retry_backoff,
            status_forcelist=status_forcelist,
            allowed_methods=["POST", "GET"],
            raise_on_status=False,
        )
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
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
        # OpenAI 兼容路径
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
            print(f"超时设置: connect={self._timeout[0]}s, read={self._timeout[1]}s")
            print(f"重试: total={int(os.getenv('CHATAI_RETRY_TOTAL', '3'))}, backoff={float(os.getenv('CHATAI_RETRY_BACKOFF', '1.5'))}")
            
            response = self.session.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=self._timeout
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
                original_content = content  # 保存原始内容用于调试
                
                # 处理 DeepSeek-R1 模型的特殊输出格式
                # R1 模型会输出 <think>推理过程</think> + 最终答案
                # 或者在没有标签时，推理过程直接混在回答中
                if '<think>' in content and '</think>' in content:
                    # 情况1: 有明确的 think 标签
                    import re
                    # 找到最后一个 </think> 标签后的内容
                    match = re.search(r'</think>\s*(.+)$', content, re.DOTALL)
                    if match:
                        content = match.group(1).strip()
                        if schema:
                            print(f"\n[INFO] 检测到 DeepSeek-R1 <think> 标签，已提取最终答案")
                elif not schema:
                    # 情况2: 普通文本响应，可能包含隐式推理过程
                    # 对于 R1 模型，通常推理过程很长，最终答案在后面
                    # 可以尝试提取最后的简洁答案
                    lines = content.split('\n')
                    # 如果响应很长且包含多个段落，尝试提取最后的简洁部分
                    if len(content) > 500:
                        # 寻找最后一个完整的答案段落
                        import re
                        # 通常最终答案会比较简短和直接
                        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                        if len(paragraphs) > 1:
                            # 使用最后一段作为答案
                            content = paragraphs[-1]
                            print(f"\n[INFO] DeepSeek-R1 长响应，提取最后段落作为答案")
                
                if schema:
                    print(f"\n{'='*60}")
                    print("模型响应（处理后）")
                    print(f"{'='*60}")
                    print(f"响应内容:\n{content[:800]}")
                    print(f"{'='*60}\n")
                
                return content
            else:
                raise ValueError(f"API 返回格式异常: {data}")
                
        except requests.exceptions.ReadTimeout as e:
            print(f"\n读取超时: {e}")
            print("建议: \n- 检查网络/代理设置\n- 尝试减少提示词长度或响应长度\n- 通过 CHATAI_TIMEOUT 调整超时，例如 \"20,60\"\n- 尝试将 CHATAI_BASE_URL 设置为 https://api.chataiapi.com/v1")
            raise RuntimeError(f"API 调用失败: {e}")
        except requests.exceptions.ConnectTimeout as e:
            print(f"\n连接超时: {e}")
            print("建议: \n- 检查域名可达性和 DNS\n- 如在公司/校园网，确认防火墙策略\n- 通过 CHATAI_BASE_URL 切换备用域名")
            raise RuntimeError(f"API 调用失败: {e}")
        except requests.exceptions.RequestException as e:
            print(f"\n详细错误信息: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise RuntimeError(f"API 调用失败: {e}")
    
    def get_model_name(self) -> str:
        """返回模型名称"""
        return self.model


# 便捷函数：创建常用模型实例
def create_default_model(api_key: str = None) -> ChatAIAPIModel:
    """创建默认模型实例（使用配置中心的默认模型）"""
    return ChatAIAPIModel(api_key=api_key)


def create_deepseek_r1(api_key: str = None) -> ChatAIAPIModel:
    """创建 DeepSeek R1 Distill 模型实例（硅基流动免费模型）"""
    return ChatAIAPIModel(api_key=api_key, model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")


# 保持向后兼容的别名
def create_claude_sonnet(api_key: str = None) -> ChatAIAPIModel:
    """[已废弃] 使用默认模型代替"""
    return create_default_model(api_key)


def create_deepseek_chat(api_key: str = None) -> ChatAIAPIModel:
    """[已废弃] 使用默认模型代替"""
    return create_default_model(api_key)


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
    model = create_claude_sonnet(api_key)
    
    # 测试生成
    response = model.generate("你好，请用一句话介绍你自己。")
    print(f"模型响应: {response}")
