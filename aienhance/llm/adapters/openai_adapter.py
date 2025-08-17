"""
OpenAI LLM和嵌入模型适配器
支持OpenAI GPT系列模型和嵌入模型
"""

import asyncio
import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
import logging

from ..interfaces import (
    LLMProvider, EmbeddingProvider, ChatMessage, ChatResponse, 
    EmbeddingRequest, EmbeddingResponse, ModelConfig, MessageRole
)

logger = logging.getLogger(__name__)


class OpenAILLMAdapter(LLMProvider):
    """
    OpenAI LLM适配器
    
    支持GPT-3.5、GPT-4等OpenAI模型
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = None
    
    async def initialize(self) -> bool:
        """初始化OpenAI客户端"""
        try:
            # 导入OpenAI库
            try:
                from openai import AsyncOpenAI
            except ImportError as e:
                logger.error("OpenAI库未安装，请运行: pip install openai")
                return False
            
            # 初始化客户端
            client_kwargs = {}
            
            if self.config.api_key:
                client_kwargs['api_key'] = self.config.api_key
            
            if self.config.api_base:
                client_kwargs['base_url'] = self.config.api_base
            
            if self.config.organization:
                client_kwargs['organization'] = self.config.organization
            
            if self.config.timeout:
                client_kwargs['timeout'] = self.config.timeout
            
            if self.config.max_retries:
                client_kwargs['max_retries'] = self.config.max_retries
            
            self.client = AsyncOpenAI(**client_kwargs)
            
            # 测试连接
            await self._test_connection()
            
            self.is_initialized = True
            logger.info(f"OpenAI LLM初始化成功: {self.config.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI LLM初始化失败: {e}")
            return False
    
    async def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """OpenAI聊天完成接口"""
        if not self.is_initialized:
            raise RuntimeError("OpenAI LLM未初始化")
        
        try:
            # 转换消息格式
            openai_messages = self._convert_messages_to_openai(messages)
            
            # 构建请求参数
            request_params = {
                "model": self.config.model_name,
                "messages": openai_messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty)
            }
            
            # 添加函数调用支持
            if "functions" in kwargs:
                request_params["functions"] = kwargs["functions"]
            if "function_call" in kwargs:
                request_params["function_call"] = kwargs["function_call"]
            
            # 添加工具调用支持
            if "tools" in kwargs:
                request_params["tools"] = kwargs["tools"]
            if "tool_choice" in kwargs:
                request_params["tool_choice"] = kwargs["tool_choice"]
            
            # 过滤None值
            request_params = {k: v for k, v in request_params.items() if v is not None}
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(**request_params)
            
            return self._convert_openai_response_to_chat(response)
            
        except Exception as e:
            logger.error(f"OpenAI聊天请求失败: {e}")
            raise
    
    async def chat_stream(self, messages: List[ChatMessage], **kwargs) -> AsyncIterator[str]:
        """OpenAI流式聊天接口"""
        if not self.is_initialized:
            raise RuntimeError("OpenAI LLM未初始化")
        
        try:
            # 转换消息格式
            openai_messages = self._convert_messages_to_openai(messages)
            
            # 构建请求参数
            request_params = {
                "model": self.config.model_name,
                "messages": openai_messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "stream": True
            }
            
            # 过滤None值
            request_params = {k: v for k, v in request_params.items() if v is not None}
            
            # 流式调用
            async for chunk in await self.client.chat.completions.create(**request_params):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI流式聊天失败: {e}")
            raise
    
    async def _test_connection(self):
        """测试OpenAI连接"""
        try:
            # 发送一个简单的请求测试连接
            await self.client.models.list()
            logger.info("OpenAI连接测试成功")
        except Exception as e:
            raise RuntimeError(f"OpenAI连接测试失败: {e}")
    
    def _convert_messages_to_openai(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """将ChatMessage转换为OpenAI格式"""
        openai_messages = []
        
        for message in messages:
            openai_message = {
                "role": message.role.value,
                "content": message.content
            }
            
            if message.name:
                openai_message["name"] = message.name
            
            if message.function_call:
                openai_message["function_call"] = message.function_call
            
            if message.tool_calls:
                openai_message["tool_calls"] = message.tool_calls
            
            openai_messages.append(openai_message)
        
        return openai_messages
    
    def _convert_openai_response_to_chat(self, openai_response) -> ChatResponse:
        """将OpenAI响应转换为ChatResponse"""
        choice = openai_response.choices[0]
        message = choice.message
        
        return ChatResponse(
            content=message.content or "",
            finish_reason=choice.finish_reason,
            usage=openai_response.usage.model_dump() if openai_response.usage else {},
            model=openai_response.model,
            created_at=datetime.datetime.fromtimestamp(openai_response.created),
            function_call=getattr(message, 'function_call', None),
            tool_calls=getattr(message, 'tool_calls', None),
            metadata={"provider": "openai"}
        )


class OpenAIEmbeddingAdapter(EmbeddingProvider):
    """
    OpenAI嵌入模型适配器
    
    支持text-embedding-ada-002等OpenAI嵌入模型
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = None
    
    async def initialize(self) -> bool:
        """初始化OpenAI嵌入客户端"""
        try:
            # 导入OpenAI库
            try:
                from openai import AsyncOpenAI
            except ImportError as e:
                logger.error("OpenAI库未安装，请运行: pip install openai")
                return False
            
            # 初始化客户端
            client_kwargs = {}
            
            if self.config.api_key:
                client_kwargs['api_key'] = self.config.api_key
            
            if self.config.api_base:
                client_kwargs['base_url'] = self.config.api_base
            
            if self.config.organization:
                client_kwargs['organization'] = self.config.organization
            
            self.client = AsyncOpenAI(**client_kwargs)
            
            # 测试连接
            await self._test_connection()
            
            self.is_initialized = True
            logger.info(f"OpenAI嵌入模型初始化成功: {self.config.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI嵌入模型初始化失败: {e}")
            return False
    
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """OpenAI嵌入生成接口"""
        if not self.is_initialized:
            raise RuntimeError("OpenAI嵌入模型未初始化")
        
        try:
            # 构建请求参数
            embed_params = {
                "model": self.config.model_name,
                "input": request.texts,
                "encoding_format": request.encoding_format
            }
            
            if request.dimensions:
                embed_params["dimensions"] = request.dimensions
            
            if request.user:
                embed_params["user"] = request.user
            
            # 调用OpenAI嵌入API
            response = await self.client.embeddings.create(**embed_params)
            
            # 提取嵌入向量
            embeddings = [embedding.embedding for embedding in response.data]
            
            return EmbeddingResponse(
                embeddings=embeddings,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else {},
                created_at=datetime.datetime.now(),
                metadata={"provider": "openai"}
            )
            
        except Exception as e:
            logger.error(f"OpenAI嵌入生成失败: {e}")
            raise
    
    async def _test_connection(self):
        """测试OpenAI连接"""
        try:
            # 发送一个简单的请求测试连接
            await self.client.models.list()
            logger.info("OpenAI嵌入服务连接测试成功")
        except Exception as e:
            raise RuntimeError(f"OpenAI嵌入服务连接测试失败: {e}")


# 注册OpenAI适配器
from ..interfaces import LLMProviderFactory, EmbeddingProviderFactory

LLMProviderFactory.register_provider("openai", OpenAILLMAdapter)
EmbeddingProviderFactory.register_provider("openai", OpenAIEmbeddingAdapter)