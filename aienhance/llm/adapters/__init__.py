"""
LLM和嵌入模型适配器模块
为不同的服务商提供统一的接口适配
"""

from .ollama_adapter import OllamaLLMAdapter, OllamaEmbeddingAdapter
from .openai_adapter import OpenAILLMAdapter, OpenAIEmbeddingAdapter
from .anthropic_adapter import AnthropicLLMAdapter

__all__ = [
    'OllamaLLMAdapter',
    'OllamaEmbeddingAdapter',
    'OpenAILLMAdapter',
    'OpenAIEmbeddingAdapter',
    'AnthropicLLMAdapter'
]