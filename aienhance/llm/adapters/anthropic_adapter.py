"""
Anthropic Claude LLM适配器
支持Claude-3等Anthropic模型
"""

import datetime
import logging
from collections.abc import AsyncIterator

from ..interfaces import (
    ChatMessage,
    ChatResponse,
    LLMProvider,
    MessageRole,
    ModelConfig,
)

logger = logging.getLogger(__name__)


class AnthropicLLMAdapter(LLMProvider):
    """
    Anthropic Claude LLM适配器

    支持Claude-3 Haiku、Sonnet、Opus等模型
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = None

    async def initialize(self) -> bool:
        """初始化Anthropic客户端"""
        try:
            # 导入Anthropic库
            try:
                from anthropic import AsyncAnthropic
            except ImportError:
                logger.error("Anthropic库未安装，请运行: pip install anthropic")
                return False

            # 初始化客户端
            client_kwargs = {}

            if self.config.api_key:
                client_kwargs["api_key"] = self.config.api_key

            if self.config.api_base:
                client_kwargs["base_url"] = self.config.api_base

            if self.config.timeout:
                client_kwargs["timeout"] = self.config.timeout

            if self.config.max_retries:
                client_kwargs["max_retries"] = self.config.max_retries

            self.client = AsyncAnthropic(**client_kwargs)

            self.is_initialized = True
            logger.info(f"Anthropic LLM初始化成功: {self.config.model_name}")
            return True

        except Exception as e:
            logger.error(f"Anthropic LLM初始化失败: {e}")
            return False

    async def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        """Anthropic聊天完成接口"""
        if not self.is_initialized:
            raise RuntimeError("Anthropic LLM未初始化")

        try:
            # 转换消息格式
            anthropic_messages, system_prompt = self._convert_messages_to_anthropic(
                messages
            )

            # 构建请求参数
            request_params = {
                "model": self.config.model_name,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 1000),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }

            # 添加系统提示
            if system_prompt:
                request_params["system"] = system_prompt

            # 过滤None值
            request_params = {k: v for k, v in request_params.items() if v is not None}

            # 调用Anthropic API
            response = await self.client.messages.create(**request_params)

            return self._convert_anthropic_response_to_chat(response)

        except Exception as e:
            logger.error(f"Anthropic聊天请求失败: {e}")
            raise

    async def chat_stream(
        self, messages: list[ChatMessage], **kwargs
    ) -> AsyncIterator[str]:
        """Anthropic流式聊天接口"""
        if not self.is_initialized:
            raise RuntimeError("Anthropic LLM未初始化")

        try:
            # 转换消息格式
            anthropic_messages, system_prompt = self._convert_messages_to_anthropic(
                messages
            )

            # 构建请求参数
            request_params = {
                "model": self.config.model_name,
                "messages": anthropic_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 1000),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": True,
            }

            # 添加系统提示
            if system_prompt:
                request_params["system"] = system_prompt

            # 过滤None值
            request_params = {k: v for k, v in request_params.items() if v is not None}

            # 流式调用
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic流式聊天失败: {e}")
            raise

    def _convert_messages_to_anthropic(
        self, messages: list[ChatMessage]
    ) -> tuple[list[dict[str, str]], str | None]:
        """将ChatMessage转换为Anthropic格式"""
        anthropic_messages = []
        system_prompt = None

        for message in messages:
            if message.role == MessageRole.SYSTEM:
                # Anthropic将系统消息作为单独的参数
                system_prompt = message.content
                continue

            anthropic_message = {"role": message.role.value, "content": message.content}

            anthropic_messages.append(anthropic_message)

        return anthropic_messages, system_prompt

    def _convert_anthropic_response_to_chat(self, anthropic_response) -> ChatResponse:
        """将Anthropic响应转换为ChatResponse"""
        # 提取文本内容
        content = ""
        if anthropic_response.content:
            for block in anthropic_response.content:
                if hasattr(block, "text"):
                    content += block.text

        # 计算token使用量
        usage = {
            "prompt_tokens": anthropic_response.usage.input_tokens
            if anthropic_response.usage
            else 0,
            "completion_tokens": anthropic_response.usage.output_tokens
            if anthropic_response.usage
            else 0,
            "total_tokens": (
                anthropic_response.usage.input_tokens
                + anthropic_response.usage.output_tokens
            )
            if anthropic_response.usage
            else 0,
        }

        return ChatResponse(
            content=content,
            finish_reason=anthropic_response.stop_reason or "stop",
            usage=usage,
            model=anthropic_response.model,
            created_at=datetime.datetime.now(),
            metadata={
                "provider": "anthropic",
                "stop_sequence": anthropic_response.stop_sequence,
            },
        )


# 注册Anthropic适配器
from ..interfaces import LLMProviderFactory

LLMProviderFactory.register_provider("anthropic", AnthropicLLMAdapter)
