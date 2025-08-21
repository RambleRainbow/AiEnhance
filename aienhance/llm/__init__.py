"""
大语言模型和嵌入模型抽象接口模块
提供统一的LLM和Embedding接口，支持OpenAI、Ollama、Anthropic等不同服务商
"""

from .adapters import (
    AnthropicLLMAdapter,
    OllamaEmbeddingAdapter,
    OllamaLLMAdapter,
    OpenAIEmbeddingAdapter,
    OpenAILLMAdapter,
)
from .interfaces import (
    ChatMessage,
    ChatResponse,
    EmbeddingProvider,
    EmbeddingProviderFactory,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMProvider,
    LLMProviderFactory,
    MessageRole,
    ModelConfig,
    ModelType,
    create_chat_message,
    create_model_config,
)

__all__ = [
    # Core Interfaces
    'LLMProvider',
    'EmbeddingProvider',
    'ChatMessage',
    'ChatResponse',
    'EmbeddingRequest',
    'EmbeddingResponse',
    'ModelConfig',
    'MessageRole',
    'ModelType',
    'LLMProviderFactory',
    'EmbeddingProviderFactory',
    'create_model_config',
    'create_chat_message',

    # Adapters
    'OllamaLLMAdapter',
    'OllamaEmbeddingAdapter',
    'OpenAILLMAdapter',
    'OpenAIEmbeddingAdapter',
    'AnthropicLLMAdapter'
]
