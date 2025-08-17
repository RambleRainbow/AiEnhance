"""
大语言模型和嵌入模型通用抽象接口定义
支持OpenAI、Ollama、Anthropic、Azure等多种服务商
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, AsyncIterator
from enum import Enum
import datetime


class MessageRole(Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ModelType(Enum):
    """模型类型枚举"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    MULTIMODAL = "multimodal"


@dataclass
class ChatMessage:
    """聊天消息数据结构"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """聊天响应数据结构"""
    content: str
    finish_reason: str
    usage: Dict[str, int]
    model: str
    created_at: datetime.datetime
    metadata: Optional[Dict[str, Any]] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


@dataclass
class EmbeddingRequest:
    """嵌入请求数据结构"""
    texts: List[str]
    model: str
    encoding_format: str = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingResponse:
    """嵌入响应数据结构"""
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]
    created_at: datetime.datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelConfig:
    """模型配置数据结构"""
    provider: str  # "ollama", "openai", "anthropic", etc.
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    organization: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    custom_config: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """
    大语言模型提供商抽象基类
    
    定义所有LLM提供商必须实现的核心接口
    支持同步和异步调用、流式响应、函数调用等高级功能
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """
        聊天完成接口
        
        Args:
            messages: 聊天消息列表
            **kwargs: 额外参数
            
        Returns:
            ChatResponse: 聊天响应
        """
        pass
    
    @abstractmethod
    async def chat_stream(self, messages: List[ChatMessage], **kwargs) -> AsyncIterator[str]:
        """
        流式聊天完成接口
        
        Args:
            messages: 聊天消息列表
            **kwargs: 额外参数
            
        Yields:
            str: 流式响应片段
        """
        pass
    
    async def completion(self, prompt: str, **kwargs) -> str:
        """
        文本完成接口 (可选实现)
        
        Args:
            prompt: 输入提示
            **kwargs: 额外参数
            
        Returns:
            str: 完成的文本
        """
        # 默认实现：转换为chat格式
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.chat(messages, **kwargs)
        return response.content
    
    async def function_call(self, messages: List[ChatMessage], 
                          functions: List[Dict[str, Any]], **kwargs) -> ChatResponse:
        """
        函数调用接口 (可选实现)
        
        Args:
            messages: 聊天消息列表
            functions: 可用函数列表
            **kwargs: 额外参数
            
        Returns:
            ChatResponse: 包含函数调用的响应
        """
        # 默认实现：添加函数到kwargs中
        kwargs['functions'] = functions
        return await self.chat(messages, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.config.provider,
            "model": self.config.model_name,
            "initialized": self.is_initialized,
            "config": self.config.custom_config or {}
        }
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.config.model_name:
            return False
        return True


class EmbeddingProvider(ABC):
    """
    嵌入模型提供商抽象基类
    
    定义所有嵌入模型提供商必须实现的核心接口
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化嵌入提供商"""
        pass
    
    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        生成嵌入向量
        
        Args:
            request: 嵌入请求
            
        Returns:
            EmbeddingResponse: 嵌入响应
        """
        pass
    
    async def embed_single(self, text: str, **kwargs) -> List[float]:
        """
        单文本嵌入便捷接口
        
        Args:
            text: 输入文本
            **kwargs: 额外参数
            
        Returns:
            List[float]: 嵌入向量
        """
        request = EmbeddingRequest(
            texts=[text],
            model=self.config.model_name,
            **kwargs
        )
        response = await self.embed(request)
        return response.embeddings[0] if response.embeddings else []
    
    async def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        批量文本嵌入便捷接口
        
        Args:
            texts: 输入文本列表
            **kwargs: 额外参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        request = EmbeddingRequest(
            texts=texts,
            model=self.config.model_name,
            **kwargs
        )
        response = await self.embed(request)
        return response.embeddings
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.config.provider,
            "model": self.config.model_name,
            "initialized": self.is_initialized,
            "config": self.config.custom_config or {}
        }
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.config.model_name:
            return False
        return True


class LLMProviderFactory:
    """LLM提供商工厂类"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class):
        """注册LLM提供商"""
        cls._providers[provider_name] = provider_class
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> LLMProvider:
        """
        创建LLM提供商实例
        
        Args:
            config: 模型配置
            
        Returns:
            LLMProvider: LLM提供商实例
        """
        provider_name = config.provider.lower()
        
        if provider_name not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的LLM提供商列表"""
        return list(cls._providers.keys())


class EmbeddingProviderFactory:
    """嵌入提供商工厂类"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class):
        """注册嵌入提供商"""
        cls._providers[provider_name] = provider_class
    
    @classmethod
    def create_provider(cls, config: ModelConfig) -> EmbeddingProvider:
        """
        创建嵌入提供商实例
        
        Args:
            config: 模型配置
            
        Returns:
            EmbeddingProvider: 嵌入提供商实例
        """
        provider_name = config.provider.lower()
        
        if provider_name not in cls._providers:
            raise ValueError(f"不支持的嵌入提供商: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的嵌入提供商列表"""
        return list(cls._providers.keys())


# 便捷函数
def create_chat_message(role: str, content: str, **kwargs) -> ChatMessage:
    """创建聊天消息的便捷函数"""
    return ChatMessage(
        role=MessageRole(role),
        content=content,
        **kwargs
    )


def create_model_config(provider: str, model_name: str, **kwargs) -> ModelConfig:
    """创建模型配置的便捷函数"""
    return ModelConfig(
        provider=provider,
        model_name=model_name,
        **kwargs
    )


def create_embedding_request(texts: Union[str, List[str]], model: str, **kwargs) -> EmbeddingRequest:
    """创建嵌入请求的便捷函数"""
    if isinstance(texts, str):
        texts = [texts]
    
    return EmbeddingRequest(
        texts=texts,
        model=model,
        **kwargs
    )