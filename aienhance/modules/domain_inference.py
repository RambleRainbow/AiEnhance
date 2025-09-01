"""
领域推断模块
使用大模型进行查询领域推断的抽象接口和实现
支持多模型协同调度的可配置架构
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

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
class DomainInferenceConfig(LLMModuleConfig):
    """领域推断配置"""
    
    custom_domains: Optional[List[str]] = None  # 自定义领域列表
    
    def __post_init__(self):
        if not self.prompt_template_name:
            self.prompt_template_name = "domain_inference_basic"
        if self.temperature is None:
            self.temperature = 0.1  # 低温度确保一致性
        if self.max_tokens is None:
            self.max_tokens = 300  # 限制输出长度


class LLMDomainInferenceProvider(
    LLMModuleProvider[DomainInferenceResult, DomainInferenceConfig]
):
    """基于大模型的领域推断提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured")
                return False

            self.is_initialized = True
            logger.info("LLM domain inference provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LLM domain inference provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> DomainInferenceResult:
        """处理领域推断业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Domain inference provider not initialized")

        try:
            # 准备提示词变量
            variables = self._prepare_prompt_variables(input_data, context)

            # 调用LLM
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )

            # 解析响应
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"LLM domain inference failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备领域推断提示词变量"""
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

        return {
            "domains": domains_str,
            "query": input_data,
            "context": context,
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> DomainInferenceResult:
        """解析LLM响应"""
        try:
            # 使用基类的JSON提取方法
            parsed = self._extract_json_from_response(response)

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
                    "original_query": original_input,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse domain inference response: {e}")
            raise


class DomainInferenceManager(LLMModuleManager[DomainInferenceResult, DomainInferenceConfig]):
    """领域推断管理器"""

    def __init__(self):
        super().__init__("domain_inference")

    async def infer_domains_async(
        self,
        query: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DomainInferenceResult:
        """推断领域 - 提供向后兼容的方法名"""
        return await self.process(query, provider_name, context)

    async def infer_domains(
        self,
        query: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> DomainInferenceResult:
        """推断领域 - 向后兼容方法"""
        return await self.process(query, provider_name, context)
