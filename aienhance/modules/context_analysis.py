"""
情境分析模块 - 基于LLM的重构版本
使用大模型分析用户当前的任务场景和问题意图
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from ..core.llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    
    EXPLORATORY = "exploratory"  # 探索型任务
    ANALYTICAL = "analytical"    # 分析型任务
    CREATIVE = "creative"        # 创新型任务
    RETRIEVAL = "retrieval"      # 检索型任务


class UrgencyLevel(Enum):
    """紧急程度"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ComplexityLevel(Enum):
    """复杂度等级"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ContextAnalysisResult:
    """情境分析结果"""
    
    task_type: TaskType
    urgency_level: UrgencyLevel
    complexity_level: ComplexityLevel
    resource_constraints: Dict[str, float]  # 资源约束 (time_pressure, knowledge_gap, tool_availability)
    social_context: Dict[str, Any]  # 社交情境 (collaboration_needed, audience_type, etc.)
    environmental_factors: list[str]  # 环境影响因素
    recommended_approach: str  # 建议的处理方式
    context_summary: str  # 情境总结
    confidence: float  # 分析置信度
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ContextAnalysisConfig(LLMModuleConfig):
    """情境分析配置"""
    
    def __post_init__(self):
        if not self.prompt_template_name:
            self.prompt_template_name = "context_analysis"
        if self.temperature is None:
            self.temperature = 0.3  # 中等温度，平衡准确性和多样性
        if self.max_tokens is None:
            self.max_tokens = 500


class LLMContextAnalysisProvider(
    LLMModuleProvider[ContextAnalysisResult, ContextAnalysisConfig]
):
    """基于大模型的情境分析提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for context analysis")
                return False

            self.is_initialized = True
            logger.info("LLM context analysis provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize context analysis provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> ContextAnalysisResult:
        """处理情境分析业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Context analysis provider not initialized")

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
            logger.error(f"Context analysis failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备情境分析提示词变量"""
        # 提取背景信息
        background = ""
        temporal_context = ""
        
        if context:
            background = context.get("background", "")
            temporal_context = context.get("temporal_context", "")
            
            # 如果没有明确的时间情境，尝试从其他字段推断
            if not temporal_context:
                temporal_context = context.get("time_context", "当前时间")

        return {
            "query": input_data,
            "background": background or "用户未提供具体背景信息",
            "temporal_context": temporal_context or "当前时间情境",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> ContextAnalysisResult:
        """解析LLM响应"""
        try:
            # 使用基类的JSON提取方法
            parsed = self._extract_json_from_response(response)

            # 解析任务类型
            task_type_str = parsed.get("task_type", "analytical").lower()
            task_type = TaskType.ANALYTICAL  # 默认值
            for task_enum in TaskType:
                if task_enum.value in task_type_str:
                    task_type = task_enum
                    break

            # 解析紧急程度
            urgency = parsed.get("urgency_level", 0.5)
            if urgency < 0.3:
                urgency_level = UrgencyLevel.LOW
            elif urgency < 0.7:
                urgency_level = UrgencyLevel.MEDIUM
            else:
                urgency_level = UrgencyLevel.HIGH

            # 解析复杂度
            complexity = parsed.get("complexity_score", 0.5)
            if complexity < 0.3:
                complexity_level = ComplexityLevel.LOW
            elif complexity < 0.7:
                complexity_level = ComplexityLevel.MEDIUM
            else:
                complexity_level = ComplexityLevel.HIGH

            # 提取资源约束
            resource_constraints = parsed.get("resource_constraints", {})
            if not isinstance(resource_constraints, dict):
                resource_constraints = {
                    "time_pressure": 0.5,
                    "knowledge_gap": 0.5,
                    "tool_availability": 0.5,
                }

            # 提取社交情境
            social_context = parsed.get("social_context", {})
            if not isinstance(social_context, dict):
                social_context = {
                    "collaboration_needed": False,
                    "audience_type": "self",
                    "communication_formality": 0.5,
                }

            # 提取环境因素
            environmental_factors = parsed.get("environmental_factors", [])
            if not isinstance(environmental_factors, list):
                environmental_factors = []

            return ContextAnalysisResult(
                task_type=task_type,
                urgency_level=urgency_level,
                complexity_level=complexity_level,
                resource_constraints=resource_constraints,
                social_context=social_context,
                environmental_factors=environmental_factors,
                recommended_approach=parsed.get("recommended_approach", "建议采用标准分析方法"),
                context_summary=parsed.get("context_summary", "情境分析摘要"),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.8))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_input,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse context analysis response: {e}")
            # 返回默认结果而不是抛出异常，确保系统鲁棒性
            return ContextAnalysisResult(
                task_type=TaskType.ANALYTICAL,
                urgency_level=UrgencyLevel.MEDIUM,
                complexity_level=ComplexityLevel.MEDIUM,
                resource_constraints={
                    "time_pressure": 0.5,
                    "knowledge_gap": 0.5,
                    "tool_availability": 0.5,
                },
                social_context={
                    "collaboration_needed": False,
                    "audience_type": "self",
                    "communication_formality": 0.5,
                },
                environmental_factors=[],
                recommended_approach="采用标准分析方法处理",
                context_summary="情境分析遇到解析问题，使用默认评估",
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_query": original_input,
                    "error": str(e),
                },
            )


class ContextAnalysisManager(LLMModuleManager[ContextAnalysisResult, ContextAnalysisConfig]):
    """情境分析管理器"""

    def __init__(self):
        super().__init__("context_analysis")

    async def analyze_context_async(
        self,
        query: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ContextAnalysisResult:
        """分析情境 - 提供向后兼容的方法名"""
        return await self.process(query, provider_name, context)