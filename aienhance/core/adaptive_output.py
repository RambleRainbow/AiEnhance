"""
自适应输出模块 - 基于LLM的重构版本
使用大模型进行个性化内容生成和输出优化
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

logger = logging.getLogger(__name__)


class InformationDensity(Enum):
    """信息密度级别"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OutputStructure(Enum):
    """输出结构类型"""
    
    LINEAR = "linear"         # 线性结构
    HIERARCHICAL = "hierarchical"  # 层次结构
    NETWORK = "network"       # 网络结构


class ConceptGranularity(Enum):
    """概念粒度"""
    
    MACRO = "macro"   # 宏观层
    MESO = "meso"     # 中观层
    MICRO = "micro"   # 微观层


class PersonalizationLevel(Enum):
    """个性化程度"""
    
    MINIMAL = "minimal"     # 最小个性化
    MODERATE = "moderate"   # 中等个性化
    EXTENSIVE = "extensive" # 深度个性化


@dataclass
class OutputConfiguration:
    """输出配置"""
    
    information_density: InformationDensity
    structure_type: OutputStructure
    concept_granularity: ConceptGranularity
    cognitive_load_limit: float
    personalization_level: PersonalizationLevel


@dataclass
class AdaptiveOutputResult:
    """自适应输出结果"""
    
    adapted_content: str
    output_config: OutputConfiguration
    personalization_applied: List[str]  # 应用的个性化策略
    cognitive_load_score: float  # 认知负荷评分
    readability_score: float     # 可读性评分
    engagement_score: float      # 参与度评分
    adaptation_rationale: str    # 适配理由
    quality_metrics: Dict[str, float]  # 质量指标
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ContentOptimizationResult:
    """内容优化结果"""
    
    optimized_content: str
    optimization_type: str  # "clarity", "engagement", "comprehension"
    improvements: List[str]  # 改进点列表
    quality_score: float    # 质量评分
    readability_improvement: float  # 可读性改进度
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AdaptiveOutputConfig(LLMModuleConfig):
    """自适应输出配置"""
    
    adaptation_type: str = "adaptive_output"  # "adaptive_output" 或 "content_optimization"
    target_audience: str = "general"  # 目标受众
    optimization_focus: str = "clarity"  # 优化重点
    
    def __post_init__(self):
        if not self.prompt_template_name:
            if self.adaptation_type == "content_optimization":
                self.prompt_template_name = "content_optimization"
            else:
                self.prompt_template_name = "adaptive_output"
        if self.temperature is None:
            self.temperature = 0.6  # 中高温度，鼓励创造性适配
        if self.max_tokens is None:
            self.max_tokens = 1000


class LLMAdaptiveOutputProvider(
    LLMModuleProvider[AdaptiveOutputResult, AdaptiveOutputConfig]
):
    """基于大模型的自适应输出提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for adaptive output")
                return False

            self.is_initialized = True
            logger.info("LLM adaptive output provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize adaptive output provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> AdaptiveOutputResult:
        """处理自适应输出业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Adaptive output provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Adaptive output generation failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备自适应输出提示词变量"""
        original_content = input_data
        user_profile = ""
        cognitive_preferences = ""
        context_info = ""
        
        if context:
            user_profile = context.get("user_profile", "")
            cognitive_preferences = context.get("cognitive_preferences", "")
            context_info = context.get("context_info", "")
            
            # 处理用户画像数据
            if isinstance(user_profile, dict):
                profile_items = []
                for key, value in user_profile.items():
                    profile_items.append(f"{key}: {value}")
                user_profile = "; ".join(profile_items)
            
        return {
            "original_content": original_content,
            "user_profile": user_profile or "通用用户画像",
            "cognitive_preferences": cognitive_preferences or "标准认知偏好",
            "context_info": context_info or "标准输出情境",
            "target_audience": self.config.target_audience,
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> AdaptiveOutputResult:
        """解析自适应输出LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析输出配置
            config_data = parsed.get("output_configuration", {})
            
            # 解析信息密度
            density_str = config_data.get("information_density", "medium").lower()
            information_density = InformationDensity.MEDIUM
            for density_enum in InformationDensity:
                if density_enum.value in density_str:
                    information_density = density_enum
                    break

            # 解析结构类型
            structure_str = config_data.get("structure_type", "linear").lower()
            structure_type = OutputStructure.LINEAR
            for structure_enum in OutputStructure:
                if structure_enum.value in structure_str:
                    structure_type = structure_enum
                    break

            # 解析概念粒度
            granularity_str = config_data.get("concept_granularity", "meso").lower()
            concept_granularity = ConceptGranularity.MESO
            for granularity_enum in ConceptGranularity:
                if granularity_enum.value in granularity_str:
                    concept_granularity = granularity_enum
                    break

            # 解析个性化程度
            personalization_str = config_data.get("personalization_level", "moderate").lower()
            personalization_level = PersonalizationLevel.MODERATE
            for personalization_enum in PersonalizationLevel:
                if personalization_enum.value in personalization_str:
                    personalization_level = personalization_enum
                    break

            # 构建输出配置
            output_config = OutputConfiguration(
                information_density=information_density,
                structure_type=structure_type,
                concept_granularity=concept_granularity,
                cognitive_load_limit=min(1.0, max(0.0, config_data.get("cognitive_load_limit", 0.7))),
                personalization_level=personalization_level
            )

            # 解析个性化策略
            personalization_applied = parsed.get("personalization_applied", [])
            if not isinstance(personalization_applied, list):
                personalization_applied = []

            # 解析质量指标
            quality_metrics = parsed.get("quality_metrics", {})
            if not isinstance(quality_metrics, dict):
                quality_metrics = {}

            return AdaptiveOutputResult(
                adapted_content=parsed.get("adapted_content", original_input),
                output_config=output_config,
                personalization_applied=personalization_applied,
                cognitive_load_score=min(1.0, max(0.0, parsed.get("cognitive_load_score", 0.5))),
                readability_score=min(1.0, max(0.0, parsed.get("readability_score", 0.7))),
                engagement_score=min(1.0, max(0.0, parsed.get("engagement_score", 0.6))),
                adaptation_rationale=parsed.get("adaptation_rationale", "基于用户画像的标准适配"),
                quality_metrics=quality_metrics,
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "adaptation_strategies": len(personalization_applied),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse adaptive output response: {e}")
            # 返回最小适配的安全输出
            return AdaptiveOutputResult(
                adapted_content=original_input,
                output_config=OutputConfiguration(
                    information_density=InformationDensity.MEDIUM,
                    structure_type=OutputStructure.LINEAR,
                    concept_granularity=ConceptGranularity.MESO,
                    cognitive_load_limit=0.7,
                    personalization_level=PersonalizationLevel.MINIMAL
                ),
                personalization_applied=[],
                cognitive_load_score=0.5,
                readability_score=0.5,
                engagement_score=0.5,
                adaptation_rationale="解析错误，使用最小适配策略",
                quality_metrics={},
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "error": str(e),
                },
            )


class LLMContentOptimizationProvider(
    LLMModuleProvider[ContentOptimizationResult, AdaptiveOutputConfig]
):
    """基于大模型的内容优化提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for content optimization")
                return False

            self.is_initialized = True
            logger.info("LLM content optimization provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize content optimization provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> ContentOptimizationResult:
        """处理内容优化业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Content optimization provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备内容优化提示词变量"""
        original_content = input_data
        optimization_goals = ""
        quality_requirements = ""
        
        if context:
            optimization_goals = context.get("optimization_goals", "")
            quality_requirements = context.get("quality_requirements", "")
            
        return {
            "original_content": original_content,
            "optimization_focus": self.config.optimization_focus,
            "optimization_goals": optimization_goals or "提升内容质量和可读性",
            "quality_requirements": quality_requirements or "标准质量要求",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> ContentOptimizationResult:
        """解析内容优化LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析改进点
            improvements = parsed.get("improvements", [])
            if not isinstance(improvements, list):
                improvements = []

            return ContentOptimizationResult(
                optimized_content=parsed.get("optimized_content", original_input),
                optimization_type=parsed.get("optimization_type", "clarity"),
                improvements=improvements,
                quality_score=min(1.0, max(0.0, parsed.get("quality_score", 0.7))),
                readability_improvement=min(1.0, max(-1.0, parsed.get("readability_improvement", 0.1))),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "improvements_count": len(improvements),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse content optimization response: {e}")
            return ContentOptimizationResult(
                optimized_content=original_input,
                optimization_type="fallback",
                improvements=[],
                quality_score=0.5,
                readability_improvement=0.0,
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "error": str(e),
                },
            )


class AdaptiveOutputManager(LLMModuleManager[AdaptiveOutputResult, AdaptiveOutputConfig]):
    """自适应输出管理器"""

    def __init__(self):
        super().__init__("adaptive_output")

    async def adapt_output_async(
        self,
        content: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdaptiveOutputResult:
        """自适应输出 - 提供向后兼容的方法名"""
        return await self.process(content, provider_name, context)


class ContentOptimizationManager(LLMModuleManager[ContentOptimizationResult, AdaptiveOutputConfig]):
    """内容优化管理器"""

    def __init__(self):
        super().__init__("content_optimization")

    async def optimize_content_async(
        self,
        content: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ContentOptimizationResult:
        """内容优化 - 提供向后兼容的方法名"""
        return await self.process(content, provider_name, context)