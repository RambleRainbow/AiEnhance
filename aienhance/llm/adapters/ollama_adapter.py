"""
Ollama LLM和嵌入模型适配器
支持本地部署的Ollama服务
"""

import datetime
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import aiohttp

from ..interfaces import (
    ChatMessage,
    ChatResponse,
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMProvider,
    MessageRole,
    ModelConfig,
)

logger = logging.getLogger(__name__)


class OllamaLLMAdapter(LLMProvider):
    """
    Ollama LLM适配器
    
    支持本地部署的Ollama服务，提供高度自定义的开源模型访问
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        self.session = None

    async def initialize(self) -> bool:
        """初始化Ollama连接"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )

            # 检查Ollama服务是否运行
            await self._check_ollama_health()

            # 检查模型是否可用
            await self._ensure_model_available()

            self.is_initialized = True
            logger.info(f"Ollama LLM初始化成功: {self.config.model_name}")
            return True

        except Exception as e:
            logger.error(f"Ollama LLM初始化失败: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False

    async def chat(self, messages: list[ChatMessage], **kwargs) -> ChatResponse:
        """Ollama聊天完成接口"""
        if not self.is_initialized:
            raise RuntimeError("Ollama LLM未初始化")

        try:
            # 使用局部session避免事件循环冲突
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # 构建Ollama格式的请求
                ollama_messages = self._convert_messages_to_ollama(messages)

                request_data = {
                    "model": self.config.model_name,
                    "messages": ollama_messages,
                    "stream": False,
                    "options": self._build_generation_options(**kwargs)
                }

                # 添加系统提示（如果有）
                system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
                if system_messages:
                    request_data["system"] = system_messages[-1].content

                # 发送请求
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    return self._convert_ollama_response_to_chat(result)

        except Exception as e:
            logger.error(f"Ollama聊天请求失败: {e}")
            raise

    async def chat_stream(self, messages: list[ChatMessage], **kwargs) -> AsyncIterator[str]:
        """Ollama流式聊天接口"""
        if not self.is_initialized:
            raise RuntimeError("Ollama LLM未初始化")

        # 为每次流式调用创建新的session，避免事件循环冲突
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                # 构建流式请求
                ollama_messages = self._convert_messages_to_ollama(messages)

                request_data = {
                    "model": self.config.model_name,
                    "messages": ollama_messages,
                    "stream": True,
                    "options": self._build_generation_options(**kwargs)
                }

                # 添加系统提示（如果有）
                system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
                if system_messages:
                    request_data["system"] = system_messages[-1].content

                # 发送流式请求
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=request_data
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if 'message' in chunk and 'content' in chunk['message']:
                                    content = chunk['message']['content']
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

                            # 检查是否完成
                            if chunk.get('done', False):
                                break

            except Exception as e:
                logger.error(f"Ollama流式聊天失败: {e}")
                raise

    async def completion(self, prompt: str, **kwargs) -> str:
        """Ollama文本完成接口"""
        if not self.is_initialized:
            raise RuntimeError("Ollama LLM未初始化")

        try:
            # 使用局部session避免事件循环冲突
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                request_data = {
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": self._build_generation_options(**kwargs)
                }

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    return result.get('response', '')

        except Exception as e:
            logger.error(f"Ollama文本完成失败: {e}")
            raise

    async def _check_ollama_health(self):
        """检查Ollama服务健康状态"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                response.raise_for_status()
                logger.info("Ollama服务运行正常")
        except Exception as e:
            raise RuntimeError(f"Ollama服务不可用: {e}")

    async def _ensure_model_available(self):
        """确保模型可用，如果不存在则尝试拉取"""
        try:
            # 检查模型是否已存在
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                response.raise_for_status()
                result = await response.json()

                available_models = [model['name'] for model in result.get('models', [])]

                if self.config.model_name not in available_models:
                    logger.warning(f"模型 {self.config.model_name} 不存在，尝试拉取...")
                    await self._pull_model()
                else:
                    logger.info(f"模型 {self.config.model_name} 已可用")

        except Exception as e:
            logger.error(f"检查模型可用性失败: {e}")
            raise

    async def _pull_model(self):
        """拉取模型"""
        try:
            request_data = {"name": self.config.model_name}

            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=request_data
            ) as response:
                response.raise_for_status()

                # 等待拉取完成
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            status = chunk.get('status', '')
                            if 'pulling' in status.lower():
                                logger.info(f"正在拉取模型: {status}")
                            elif chunk.get('error'):
                                raise RuntimeError(f"拉取模型失败: {chunk['error']}")
                            elif status == 'success':
                                logger.info(f"模型 {self.config.model_name} 拉取成功")
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            raise RuntimeError(f"拉取模型失败: {e}")

    def _convert_messages_to_ollama(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
        """将ChatMessage转换为Ollama格式"""
        ollama_messages = []

        for message in messages:
            if message.role == MessageRole.SYSTEM:
                continue  # 系统消息单独处理

            ollama_message = {
                "role": message.role.value,
                "content": message.content
            }

            ollama_messages.append(ollama_message)

        return ollama_messages

    def _convert_ollama_response_to_chat(self, ollama_response: dict[str, Any]) -> ChatResponse:
        """将Ollama响应转换为ChatResponse"""
        message = ollama_response.get('message', {})
        content = message.get('content', '')

        # 计算token使用量（Ollama可能不提供，使用估算）
        prompt_tokens = ollama_response.get('prompt_eval_count', 0)
        completion_tokens = ollama_response.get('eval_count', 0)

        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

        return ChatResponse(
            content=content,
            finish_reason=ollama_response.get('done_reason', 'stop'),
            usage=usage,
            model=self.config.model_name,
            created_at=datetime.datetime.now(),
            metadata={
                "total_duration": ollama_response.get('total_duration'),
                "load_duration": ollama_response.get('load_duration'),
                "prompt_eval_duration": ollama_response.get('prompt_eval_duration'),
                "eval_duration": ollama_response.get('eval_duration')
            }
        )

    def _build_generation_options(self, **kwargs) -> dict[str, Any]:
        """构建Ollama生成选项"""
        options = {}

        # 从配置和kwargs中设置参数
        if self.config.temperature is not None:
            options["temperature"] = kwargs.get("temperature", self.config.temperature)

        if self.config.max_tokens is not None:
            options["num_predict"] = kwargs.get("max_tokens", self.config.max_tokens)

        if self.config.top_p is not None:
            options["top_p"] = kwargs.get("top_p", self.config.top_p)

        # Ollama特有参数
        options.update({
            "num_ctx": kwargs.get("num_ctx", 2048),  # 上下文长度
            "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
            "seed": kwargs.get("seed", -1),
            "stop": kwargs.get("stop", [])
        })

        # 添加自定义配置
        if self.config.custom_config:
            options.update(self.config.custom_config)

        return options

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()


class OllamaEmbeddingAdapter(EmbeddingProvider):
    """
    Ollama嵌入模型适配器
    
    支持Ollama的嵌入模型服务
    """

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        self.session = None

    async def initialize(self) -> bool:
        """初始化Ollama嵌入服务"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )

            # 检查Ollama服务
            await self._check_ollama_health()

            # 确保嵌入模型可用
            await self._ensure_embedding_model_available()

            self.is_initialized = True
            logger.info(f"Ollama嵌入模型初始化成功: {self.config.model_name}")
            return True

        except Exception as e:
            logger.error(f"Ollama嵌入模型初始化失败: {e}")
            if self.session:
                await self.session.close()
                self.session = None
            return False

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Ollama嵌入生成接口"""
        if not self.is_initialized:
            raise RuntimeError("Ollama嵌入模型未初始化")

        try:
            embeddings = []
            total_tokens = 0

            # 批量处理文本
            for text in request.texts:
                request_data = {
                    "model": self.config.model_name,
                    "prompt": text
                }

                async with self.session.post(
                    f"{self.base_url}/api/embeddings",
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    embedding = result.get('embedding', [])
                    embeddings.append(embedding)

                    # 估算token使用量
                    total_tokens += len(text.split())

            usage = {
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }

            return EmbeddingResponse(
                embeddings=embeddings,
                model=self.config.model_name,
                usage=usage,
                created_at=datetime.datetime.now(),
                metadata={"provider": "ollama"}
            )

        except Exception as e:
            logger.error(f"Ollama嵌入生成失败: {e}")
            raise

    async def _check_ollama_health(self):
        """检查Ollama服务健康状态"""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                response.raise_for_status()
                logger.info("Ollama嵌入服务运行正常")
        except Exception as e:
            raise RuntimeError(f"Ollama服务不可用: {e}")

    async def _ensure_embedding_model_available(self):
        """确保嵌入模型可用"""
        try:
            # 检查模型是否已存在
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                response.raise_for_status()
                result = await response.json()

                available_models = [model['name'] for model in result.get('models', [])]

                if self.config.model_name not in available_models:
                    logger.warning(f"嵌入模型 {self.config.model_name} 不存在")
                    # 可以选择自动拉取或抛出错误
                    raise RuntimeError(f"嵌入模型 {self.config.model_name} 不可用")
                else:
                    logger.info(f"嵌入模型 {self.config.model_name} 已可用")

        except Exception as e:
            logger.error(f"检查嵌入模型可用性失败: {e}")
            raise

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()


# 注册Ollama适配器
from ..interfaces import EmbeddingProviderFactory, LLMProviderFactory

LLMProviderFactory.register_provider("ollama", OllamaLLMAdapter)
EmbeddingProviderFactory.register_provider("ollama", OllamaEmbeddingAdapter)
