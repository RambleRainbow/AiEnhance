"""
领域推断模块
使用大模型进行查询领域推断的抽象接口和实现
支持多模型协同调度的可配置架构
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .prompts import get_prompt_manager

logger = logging.getLogger(__name__)


@dataclass
class DomainInferenceResult:
    """领域推断结果"""

    primary_domains: List[str]  # 主要领域
    secondary_domains: List[str]  # 次要领域
    confidence_scores: Dict[str, float]  # 每个领域的置信度
    interdisciplinary: bool  # 是否跨学科
    reasoning: Optional[str] = None  # 推理过程（可选）
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据


@dataclass
class DomainInferenceConfig:
    """领域推断配置"""

    llm_provider: Any  # LLM提供商实例
    model_name: Optional[str] = None  # 特定模型名称
    temperature: float = 0.1  # 低温度确保一致性
    max_tokens: int = 300  # 限制输出长度
    timeout: int = 10  # 超时设置
    custom_domains: Optional[List[str]] = None  # 自定义领域列表


class DomainInferenceProvider(ABC):
    """领域推断提供商抽象接口"""

    def __init__(self, config: DomainInferenceConfig):
        self.config = config
        self.is_initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化提供商"""
        pass

    @abstractmethod
    async def infer_domains(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> DomainInferenceResult:
        """推断查询涉及的领域"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


class LLMDomainInferenceProvider(DomainInferenceProvider):
    """基于大模型的领域推断提供商"""

    def __init__(self, config: DomainInferenceConfig):
        super().__init__(config)
        self.llm_provider = config.llm_provider
        self.prompt_manager = get_prompt_manager()

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured")
                return False

            # 这里可以添加LLM连接测试
            self.is_initialized = True
            logger.info("LLM domain inference provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LLM domain inference provider: {e}")
            return False

    async def infer_domains(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> DomainInferenceResult:
        """使用大模型推断领域"""
        if not self.is_initialized:
            raise RuntimeError("Domain inference provider not initialized")

        try:
            # 准备领域列表
            base_domains = [
                "technology",
                "science",
                "education",
                "business",
                "art",
                "health",
                "finance",
                "legal",
                "engineering",
                "mathematics",
                "language",
                "history",
                "philosophy",
                "psychology",
                "social_science",
            ]
            domains_list = self.config.custom_domains or base_domains
            domains_str = ", ".join(domains_list)

            # 使用集中式提示词管理器渲染提示
            prompt = self.prompt_manager.render_prompt(
                name="domain_inference_basic",
                variables={"domains": domains_str, "query": query, "context": context},
            )

            # 调用LLM
            response = await asyncio.wait_for(
                self._call_llm(prompt), timeout=self.config.timeout
            )

            # 解析响应
            return self._parse_llm_response(response, query)

        except asyncio.TimeoutError:
            logger.error(f"LLM domain inference timeout for query: {query[:50]}...")
            raise TimeoutError(
                f"Domain inference timeout after {self.config.timeout} seconds"
            )

        except Exception as e:
            logger.error(f"LLM domain inference failed: {e}")
            raise

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM生成响应"""
        try:
            # 构建消息格式
            messages = [{"role": "user", "content": prompt}]

            # 调用LLM (需要适配不同的LLM接口)
            if hasattr(self.llm_provider, "generate_async"):
                # 异步接口
                response = await self.llm_provider.generate_async(
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name,
                )
            elif hasattr(self.llm_provider, "chat"):
                # 同步聊天接口
                response = await asyncio.to_thread(
                    self.llm_provider.chat,
                    messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name or "default",
                )
            else:
                raise ValueError("Unsupported LLM provider interface")

            # 提取文本内容
            if isinstance(response, dict):
                return response.get("content", response.get("message", str(response)))
            elif hasattr(response, "content"):
                return response.content
            else:
                return str(response)

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _parse_llm_response(
        self, response: str, original_query: str
    ) -> DomainInferenceResult:
        """解析LLM响应"""
        try:
            # 尝试提取JSON部分
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # 解析JSON
            parsed = json.loads(response)

            # 验证必需字段
            primary_domains = parsed.get("primary_domains", [])
            secondary_domains = parsed.get("secondary_domains", [])
            confidence_scores = parsed.get("confidence_scores", {})
            interdisciplinary = parsed.get("interdisciplinary", False)
            reasoning = parsed.get("reasoning", "")

            return DomainInferenceResult(
                primary_domains=primary_domains,
                secondary_domains=secondary_domains,
                confidence_scores=confidence_scores,
                interdisciplinary=interdisciplinary,
                reasoning=reasoning,
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_query,
                },
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            # 这里可以添加特定的清理逻辑
            self.is_initialized = False
            logger.info("LLM domain inference provider cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class DomainInferenceManager:
    """领域推断管理器

    支持多提供商配置和切换，为多模型协同调度做准备
    """

    def __init__(self):
        self.providers: Dict[str, DomainInferenceProvider] = {}
        self.default_provider_name: Optional[str] = None

    async def register_provider(
        self, name: str, provider: DomainInferenceProvider
    ) -> bool:
        """注册领域推断提供商"""
        try:
            success = await provider.initialize()
            if success:
                self.providers[name] = provider
                if self.default_provider_name is None:
                    self.default_provider_name = name
                logger.info(f"Registered domain inference provider: {name}")
                return True
            else:
                logger.error(f"Failed to initialize provider: {name}")
                return False
        except Exception as e:
            logger.error(f"Error registering provider {name}: {e}")
            return False

    async def infer_domains(
        self,
        query: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DomainInferenceResult:
        """推断领域"""
        provider_name = provider_name or self.default_provider_name

        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not found: {provider_name}")

        provider = self.providers[provider_name]
        return await provider.infer_domains(query, context)

    async def cleanup(self) -> None:
        """清理所有提供商"""
        for name, provider in self.providers.items():
            try:
                await provider.cleanup()
                logger.info(f"Cleaned up provider: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up provider {name}: {e}")

        self.providers.clear()
        self.default_provider_name = None

    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.providers.keys())

    def set_default_provider(self, name: str) -> bool:
        """设置默认提供商"""
        if name in self.providers:
            self.default_provider_name = name
            return True
        return False
