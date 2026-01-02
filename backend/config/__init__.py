"""
配置管理模块
"""
from .llm_config import LLMConfig, get_api_key, get_model_for_task

__all__ = ['LLMConfig', 'get_api_key', 'get_model_for_task']
