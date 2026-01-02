"""
LLM 配置管理中心
统一管理所有 LLM API 相关配置
"""
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)


class LLMConfig:
    """LLM 配置管理类 - 单一数据源 (Single Source of Truth)"""
    
    # ============ API Key 配置 ============
    
    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        获取 API Key（按优先级）
        
        优先级:
        1. API_KEY_OVERRIDE (运行时注入，最高优先级)
        2. CHATAIAPI_KEY (ChatAI 主键)
        3. CHATAI_API_KEY (ChatAI 别名)
        4. OPENAI_API_KEY (OpenAI 原生)
        
        Returns:
            API Key 字符串，如果未配置则返回 None
        """
        return (
            os.getenv("API_KEY_OVERRIDE")
            or os.getenv("CHATAIAPI_KEY")
            or os.getenv("CHATAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
    
    @staticmethod
    def get_base_url() -> str:
        """
        获取 API 基础 URL
        
        Returns:
            API 基础 URL，默认为硅基流动 API 地址
        """
        return os.getenv(
            "CHATAI_BASE_URL", 
            "https://api.siliconflow.cn/v1"
        )
    
    @staticmethod
    def is_api_available() -> bool:
        """
        检查 API Key 是否已配置
        
        Returns:
            True 如果 API Key 存在，否则 False
        """
        return bool(LLMConfig.get_api_key())
    
    # ============ 模型配置 ============
    
    # 默认模型配置 - 统一使用 Qwen2.5 获得最佳兼容性
    DEFAULT_MODELS = {
        "evaluation": "Qwen/Qwen2.5-7B-Instruct",  # 质量评估：100%测试通过，JSON完美
        "flow_analysis": "Qwen/Qwen2.5-7B-Instruct",  # 流程分析：稳定可靠，无思维链干扰
        "general": "Qwen/Qwen2.5-7B-Instruct"  # 通用：最新版本，综合能力最强
    }
    
    @classmethod
    def get_default_model(cls, task: str = "general") -> str:
        """
        获取指定任务的默认模型
        
        支持通过环境变量覆盖，例如:
        - DEFAULT_MODEL_EVALUATION
        - DEFAULT_MODEL_FLOW_ANALYSIS
        - DEFAULT_MODEL_GENERAL
        
        Args:
            task: 任务类型 (evaluation, flow_analysis, general)
        
        Returns:
            模型名称字符串
        """
        # 支持环境变量覆盖
        env_key = f"DEFAULT_MODEL_{task.upper()}"
        return os.getenv(env_key, cls.DEFAULT_MODELS.get(task, cls.DEFAULT_MODELS["general"]))
    
    # ============ 超时和重试配置 ============
    
    @staticmethod
    def get_timeout() -> tuple:
        """
        获取超时配置 (连接超时, 读取超时)
        
        支持环境变量 CHATAI_TIMEOUT，格式:
        - "连接,读取" 例如 "15,60"
        - 单值 例如 "30" (连接和读取使用同一值)
        
        Returns:
            元组 (连接超时秒数, 读取超时秒数)，默认 (15, 60)
        """
        env_timeout = os.getenv("CHATAI_TIMEOUT")
        if env_timeout:
            try:
                parts = [p.strip() for p in env_timeout.split(',')]
                if len(parts) == 2:
                    return (float(parts[0]), float(parts[1]))
                else:
                    t = float(parts[0])
                    return (t, t)
            except Exception:
                pass
        return (15, 60)  # 默认值
    
    @staticmethod
    def get_retry_config() -> Dict[str, float]:
        """
        获取重试配置
        
        支持环境变量:
        - CHATAI_RETRY_TOTAL: 重试总次数 (默认 3)
        - CHATAI_RETRY_BACKOFF: 退避因子 (默认 1.5)
        
        Returns:
            包含 'total' 和 'backoff' 的字典
        """
        return {
            "total": int(os.getenv("CHATAI_RETRY_TOTAL", "3")),
            "backoff": float(os.getenv("CHATAI_RETRY_BACKOFF", "1.5"))
        }
    
    # ============ 模型预设和元数据 ============
    
    SUPPORTED_MODELS = {
        # 推荐首选：硅基流动免费模型
        "Qwen/Qwen2.5-7B-Instruct": {
            "name": "Qwen 2.5 7B Instruct",
            "provider": "SiliconFlow (硅基流动)",
            "cost": "free",
            "speed": "fast",  # 平均 1.88秒
            "quality": "excellent",
            "recommended_for": ["evaluation", "flow_analysis", "general", "json_output", "structured_output"],
            "description": "✅ 推荐首选：最新版本，100%测试通过，JSON格式完美，无思维链干扰",
            "notes": "综合能力最强，适合所有任务场景",
            "test_results": {
                "success_rate": "100%",
                "avg_response_time": 1.88,
                "json_compatibility": "perfect"
            }
        },
        
        # 备选：硅基流动免费模型
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": {
            "name": "DeepSeek R1 Distill Qwen 7B",
            "provider": "SiliconFlow (硅基流动)",
            "cost": "free",
            "speed": "very_fast",  # 平均 2.10秒
            "quality": "good",
            "recommended_for": ["reasoning", "deep_analysis"],
            "description": "推理模型，思维能力强但输出包含思维链",
            "notes": "⚠️ 输出格式不稳定，JSON兼容性差，不推荐用于结构化输出任务",
            "test_results": {
                "success_rate": "50%",
                "avg_response_time": 2.10,
                "json_compatibility": "poor"
            }
        },
        "Qwen/Qwen2-7B-Instruct": {
            "name": "Qwen 2 7B Instruct",
            "provider": "SiliconFlow (硅基流动)",
            "cost": "free",
            "speed": "very_fast",  # 平均 1.01秒
            "quality": "good",
            "recommended_for": ["general", "json_output"],
            "description": "旧版本，速度更快但能力略弱",
            "notes": "备选方案，如需更快响应速度可考虑",
            "test_results": {
                "success_rate": "100%",
                "avg_response_time": 1.01,
                "json_compatibility": "perfect"
            }
        },
        
        # 以下模型已禁用（仅作记录）
        # "claude-3-5-sonnet-20240620": {...},
        # "deepseek-chat": {...},
        # "deepseek-ai/DeepSeek-V3.2": {...},
        # "gpt-4o-mini": {...},
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict]:
        """
        获取模型详细信息
        
        Args:
            model_name: 模型名称
        
        Returns:
            包含模型元数据的字典，如果模型不存在返回 None
        """
        return cls.SUPPORTED_MODELS.get(model_name)
    
    @classmethod
    def list_models(cls, provider: Optional[str] = None, 
                    cost: Optional[str] = None,
                    recommended_for: Optional[str] = None) -> list:
        """
        列出所有支持的模型（支持过滤）
        
        Args:
            provider: 按提供商过滤 (例如 "DeepSeek", "Anthropic")
            cost: 按成本过滤 (例如 "low", "medium", "high")
            recommended_for: 按推荐用途过滤 (例如 "evaluation", "flow_analysis")
        
        Returns:
            模型名称列表
        """
        models = []
        for model_name, info in cls.SUPPORTED_MODELS.items():
            # 应用过滤条件
            if provider and info.get("provider") != provider:
                continue
            if cost and info.get("cost") != cost:
                continue
            if recommended_for and recommended_for not in info.get("recommended_for", []):
                continue
            models.append(model_name)
        return models
    
    @classmethod
    def get_models_by_cost(cls) -> Dict[str, list]:
        """
        按成本分组返回模型
        
        Returns:
            字典，键为成本等级，值为模型名称列表
        """
        result = {
            "free": [],
            "very_low": [],
            "low": [],
            "medium": [],
            "high": []
        }
        for model_name, info in cls.SUPPORTED_MODELS.items():
            cost = info.get("cost", "medium")
            if cost in result:
                result[cost].append(model_name)
        return result
    
    @classmethod
    def recommend_model(cls, task: str, priority: str = "balanced") -> str:
        """
        智能推荐模型
        
        Args:
            task: 任务类型 (evaluation, flow_analysis, general)
            priority: 优先级 (cost - 优先成本, speed - 优先速度, quality - 优先质量, balanced - 平衡)
        
        Returns:
            推荐的模型名称
        """
        # 优先使用环境变量配置
        env_model = cls.get_default_model(task)
        if env_model != cls.DEFAULT_MODELS.get(task, cls.DEFAULT_MODELS["general"]):
            return env_model
        
        # 统一使用硅基流动免费模型
        return "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"


# ============ 便捷函数 ============

def get_api_key() -> Optional[str]:
    """
    快捷获取 API Key
    
    Returns:
        API Key 字符串，如果未配置则返回 None
    """
    return LLMConfig.get_api_key()


def get_model_for_task(task: str) -> str:
    """
    快捷获取任务默认模型
    
    Args:
        task: 任务类型 (evaluation, flow_analysis, general)
    
    Returns:
        模型名称字符串
    """
    return LLMConfig.get_default_model(task)


def get_base_url() -> str:
    """
    快捷获取 API 基础 URL
    
    Returns:
        API 基础 URL 字符串
    """
    return LLMConfig.get_base_url()


# ============ 测试代码 ============

if __name__ == '__main__':
    print("="*60)
    print("LLM 配置中心测试")
    print("="*60)
    
    # 测试 API Key
    api_key = LLMConfig.get_api_key()
    if api_key:
        print(f"\n✅ API Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("\n❌ API Key 未配置")
    
    # 测试 Base URL
    print(f"📍 Base URL: {LLMConfig.get_base_url()}")
    
    # 测试默认模型
    print("\n📋 默认模型配置:")
    print(f"  - 质量评估: {LLMConfig.get_default_model('evaluation')}")
    print(f"  - 流程分析: {LLMConfig.get_default_model('flow_analysis')}")
    print(f"  - 通用任务: {LLMConfig.get_default_model('general')}")
    
    # 测试超时配置
    timeout = LLMConfig.get_timeout()
    print(f"\n⏱️  超时配置: 连接 {timeout[0]}s, 读取 {timeout[1]}s")
    
    # 测试重试配置
    retry = LLMConfig.get_retry_config()
    print(f"🔄 重试配置: 总次数 {retry['total']}, 退避因子 {retry['backoff']}")
    
    # 测试模型列表
    print(f"\n🎯 支持的模型总数: {len(LLMConfig.list_models())}")
    
    # 按成本分组
    print("\n💰 按成本分组:")
    for cost_level, models in LLMConfig.get_models_by_cost().items():
        if models:
            print(f"  {cost_level}: {len(models)} 个模型")
    
    # 测试模型推荐
    print("\n🌟 智能推荐:")
    print(f"  成本优先 (评估): {LLMConfig.recommend_model('evaluation', 'cost')}")
    print(f"  速度优先 (流程): {LLMConfig.recommend_model('flow_analysis', 'speed')}")
    print(f"  质量优先 (通用): {LLMConfig.recommend_model('general', 'quality')}")
    
    # 测试模型信息
    test_model = "deepseek-ai/DeepSeek-V3.2"
    info = LLMConfig.get_model_info(test_model)
    if info:
        print(f"\n📖 模型信息: {test_model}")
        print(f"  名称: {info['name']}")
        print(f"  提供商: {info['provider']}")
        print(f"  成本: {info['cost']} | 速度: {info['speed']} | 质量: {info['quality']}")
        print(f"  描述: {info['description']}")
    
    print("\n" + "="*60)
