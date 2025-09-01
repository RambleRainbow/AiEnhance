"""
用户建模模块 - 基于LLM的重构版本
使用大模型进行用户认知特征分析和学习风格识别
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from ..core.llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """思维模式"""

    ANALYTICAL = "analytical"  # 分析型
    INTUITIVE = "intuitive"  # 直觉型
    CREATIVE = "creative"  # 创造型


class ProcessingPreference(Enum):
    """信息处理偏好"""

    VISUAL = "visual"  # 视觉型
    AUDITORY = "auditory"  # 听觉型
    KINESTHETIC = "kinesthetic"  # 动手型


class LearningPace(Enum):
    """学习节奏"""

    FAST = "fast"  # 快速型
    GRADUAL = "gradual"  # 渐进型
    DEEP = "deep"  # 深入型


class FeedbackStyle(Enum):
    """反馈接收方式"""

    DIRECT = "direct"  # 直接型
    GUIDED = "guided"  # 引导型
    EXPLORATORY = "exploratory"  # 探索型


class KnowledgeConstruction(Enum):
    """知识建构方式"""

    LINEAR = "linear"  # 线性型
    NETWORK = "network"  # 网络型
    ITERATIVE = "iterative"  # 循环型


@dataclass
class CognitiveAnalysisResult:
    """认知特征分析结果"""

    thinking_mode: ThinkingMode
    cognitive_complexity: float  # 认知复杂度 (0.0-1.0)
    abstraction_level: float  # 抽象思维能力 (0.0-1.0)
    creativity_tendency: float  # 创造性思维倾向 (0.0-1.0)
    reasoning_preference: str  # 推理偏好描述
    confidence: float  # 分析置信度
    analysis_basis: str  # 分析依据
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LearningStyleResult:
    """学习风格分析结果"""

    processing_preference: ProcessingPreference
    learning_pace: LearningPace
    feedback_style: FeedbackStyle
    knowledge_construction: KnowledgeConstruction
    interaction_density: float  # 交互密度偏好 (0.0-1.0)
    detail_preference: float  # 细节偏好 (0.0-1.0)
    example_preference: float  # 示例偏好 (0.0-1.0)
    explanation: str  # 学习风格分析说明
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserModelingConfig(LLMModuleConfig):
    """用户建模配置"""

    analysis_type: str = "cognitive"  # "cognitive" 或 "learning_style"

    def __post_init__(self):
        if not self.prompt_template_name:
            if self.analysis_type == "cognitive":
                self.prompt_template_name = "cognitive_analysis"
            else:
                self.prompt_template_name = "learning_style_analysis"
        if self.temperature is None:
            self.temperature = 0.3  # 中等温度，平衡准确性和个性化
        if self.max_tokens is None:
            self.max_tokens = 450


class LLMCognitiveAnalysisProvider(
    LLMModuleProvider[CognitiveAnalysisResult, UserModelingConfig]
):
    """基于大模型的认知特征分析提供商"""

    @classmethod
    def get_cognitive_analysis_schema(cls) -> dict[str, Any]:
        """获取认知分析的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "thinking_mode": {
                    "type": "string",
                    "enum": [
                        "analytical",
                        "creative",
                        "critical",
                        "holistic",
                        "sequential",
                    ],
                    "description": "思维模式类型",
                },
                "cognitive_complexity": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "认知复杂度评分",
                },
                "abstraction_level": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "抽象思维能力评分",
                },
                "creativity_tendency": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "创造性思维倾向评分",
                },
                "reasoning_preference": {
                    "type": "string",
                    "description": "推理偏好的详细描述",
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "分析结果的置信度",
                },
                "analysis_basis": {"type": "string", "description": "分析依据的说明"},
            },
            "required": [
                "thinking_mode",
                "cognitive_complexity",
                "abstraction_level",
                "creativity_tendency",
                "reasoning_preference",
                "confidence",
                "analysis_basis",
            ],
        }

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for cognitive analysis")
                return False

            self.is_initialized = True
            logger.info("LLM cognitive analysis provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize cognitive analysis provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> CognitiveAnalysisResult:
        """处理认知特征分析业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Cognitive analysis provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            # 使用JSON Schema确保结构化输出
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name,
                variables,
                json_schema=self.get_cognitive_analysis_schema(),
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Cognitive analysis failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备认知分析提示词变量"""
        domain_context = ""
        historical_data = ""

        if context:
            domain_context = context.get("domain_context", "")
            historical_data = context.get("historical_data", "")

        return {
            "current_query": input_data,
            "domain_context": domain_context or "用户当前查询的领域背景",
            "historical_data": historical_data or "暂无历史交互数据",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> CognitiveAnalysisResult:
        """解析认知分析LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 检查是否解析出错
            if "error" in parsed:
                logger.warning(f"LLM response parsing had errors: {parsed['error']}")
                # 如果有提取的文本，尝试从中获取信息
                if "extracted_text" in parsed:
                    extracted_text = parsed["extracted_text"]
                    # 简单的关键词分析作为fallback
                    thinking_mode = (
                        ThinkingMode.CREATIVE
                        if "创造" in extracted_text or "创新" in extracted_text
                        else ThinkingMode.ANALYTICAL
                    )
                    return CognitiveAnalysisResult(
                        thinking_mode=thinking_mode,
                        cognitive_complexity=0.6 if "复杂" in extracted_text else 0.5,
                        abstraction_level=0.6 if "抽象" in extracted_text else 0.5,
                        creativity_tendency=0.7 if "创造" in extracted_text else 0.5,
                        reasoning_preference=f"基于文本分析: {extracted_text[:100]}",
                        confidence=0.4,
                        analysis_basis="从非结构化响应中提取",
                        metadata={
                            "provider": "llm_text_extract",
                            "model": self.config.model_name,
                            "original_query": original_input,
                            "parse_error": parsed.get("parse_error", ""),
                        },
                    )

            # 解析思维模式
            thinking_mode_str = parsed.get("thinking_mode", "analytical").lower()
            thinking_mode = ThinkingMode.ANALYTICAL
            for mode_enum in ThinkingMode:
                if mode_enum.value in thinking_mode_str:
                    thinking_mode = mode_enum
                    break

            return CognitiveAnalysisResult(
                thinking_mode=thinking_mode,
                cognitive_complexity=min(
                    1.0, max(0.0, parsed.get("cognitive_complexity", 0.5))
                ),
                abstraction_level=min(
                    1.0, max(0.0, parsed.get("abstraction_level", 0.5))
                ),
                creativity_tendency=min(
                    1.0, max(0.0, parsed.get("creativity_tendency", 0.5))
                ),
                reasoning_preference=parsed.get("reasoning_preference", "逻辑推理为主"),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                analysis_basis=parsed.get(
                    "analysis_basis", "基于查询内容的认知模式分析"
                ),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_input,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse cognitive analysis response: {e}")
            return CognitiveAnalysisResult(
                thinking_mode=ThinkingMode.ANALYTICAL,
                cognitive_complexity=0.5,
                abstraction_level=0.5,
                creativity_tendency=0.5,
                reasoning_preference="标准逻辑推理",
                confidence=0.3,
                analysis_basis="解析错误，使用默认认知特征",
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_query": original_input,
                    "error": str(e),
                },
            )


class LLMLearningStyleProvider(
    LLMModuleProvider[LearningStyleResult, UserModelingConfig]
):
    """基于大模型的学习风格分析提供商"""

    @classmethod
    def get_learning_style_schema(cls) -> dict[str, Any]:
        """获取学习风格分析的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "processing_preference": {
                    "type": "string",
                    "enum": ["visual", "auditory", "kinesthetic"],
                    "description": "信息处理偏好类型",
                },
                "learning_pace": {
                    "type": "string",
                    "enum": ["fast", "gradual", "deep"],
                    "description": "学习节奏偏好",
                },
                "feedback_style": {
                    "type": "string",
                    "enum": ["direct", "guided", "exploratory"],
                    "description": "反馈接收方式偏好",
                },
                "knowledge_construction": {
                    "type": "string",
                    "enum": ["linear", "network", "iterative"],
                    "description": "知识建构方式偏好",
                },
                "interaction_density": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "交互密度偏好评分",
                },
                "detail_preference": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "细节关注度偏好评分",
                },
                "example_preference": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "示例需求偏好评分",
                },
                "explanation": {
                    "type": "string",
                    "description": "学习风格分析的详细说明",
                },
            },
            "required": [
                "processing_preference",
                "learning_pace",
                "feedback_style",
                "knowledge_construction",
                "interaction_density",
                "detail_preference",
                "example_preference",
                "explanation",
            ],
        }

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for learning style analysis")
                return False

            self.is_initialized = True
            logger.info("LLM learning style analysis provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize learning style provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> LearningStyleResult:
        """处理学习风格分析业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Learning style analysis provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            # 使用JSON Schema确保结构化输出
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name,
                variables,
                json_schema=self.get_learning_style_schema(),
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Learning style analysis failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备学习风格分析提示词变量"""
        domain = ""
        interaction_history = ""

        if context:
            domain = context.get("domain", "")
            interaction_history = context.get("interaction_history", "")

        return {
            "query": input_data,
            "domain": domain or "通用领域",
            "interaction_history": interaction_history or "暂无历史交互记录",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> LearningStyleResult:
        """解析学习风格分析LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 检查是否解析出错
            if "error" in parsed:
                logger.warning(f"LLM response parsing had errors: {parsed['error']}")
                # 如果有提取的文本，尝试基于文本内容推断学习风格
                if "extracted_text" in parsed:
                    extracted_text = parsed["extracted_text"]
                    # 简单的关键词分析
                    processing_pref = (
                        ProcessingPreference.VISUAL
                        if "视觉" in extracted_text or "图像" in extracted_text
                        else ProcessingPreference.VISUAL
                    )
                    return LearningStyleResult(
                        processing_preference=processing_pref,
                        learning_pace=LearningPace.GRADUAL,
                        feedback_style=FeedbackStyle.GUIDED,
                        knowledge_construction=KnowledgeConstruction.LINEAR,
                        interaction_density=0.5,
                        detail_preference=0.5,
                        example_preference=0.7,
                        explanation=f"基于文本分析的学习风格推断: {extracted_text[:100]}",
                        metadata={
                            "provider": "llm_text_extract",
                            "model": self.config.model_name,
                            "original_query": original_input,
                            "parse_error": parsed.get("parse_error", ""),
                        },
                    )

            # 解析各种枚举类型
            processing_pref_str = parsed.get("processing_preference", "visual").lower()
            processing_preference = ProcessingPreference.VISUAL
            for pref_enum in ProcessingPreference:
                if pref_enum.value in processing_pref_str:
                    processing_preference = pref_enum
                    break

            learning_pace_str = parsed.get("learning_pace", "gradual").lower()
            learning_pace = LearningPace.GRADUAL
            for pace_enum in LearningPace:
                if pace_enum.value in learning_pace_str:
                    learning_pace = pace_enum
                    break

            feedback_style_str = parsed.get("feedback_style", "guided").lower()
            feedback_style = FeedbackStyle.GUIDED
            for style_enum in FeedbackStyle:
                if style_enum.value in feedback_style_str:
                    feedback_style = style_enum
                    break

            knowledge_const_str = parsed.get("knowledge_construction", "linear").lower()
            knowledge_construction = KnowledgeConstruction.LINEAR
            for const_enum in KnowledgeConstruction:
                if const_enum.value in knowledge_const_str:
                    knowledge_construction = const_enum
                    break

            return LearningStyleResult(
                processing_preference=processing_preference,
                learning_pace=learning_pace,
                feedback_style=feedback_style,
                knowledge_construction=knowledge_construction,
                interaction_density=min(
                    1.0, max(0.0, parsed.get("interaction_density", 0.5))
                ),
                detail_preference=min(
                    1.0, max(0.0, parsed.get("detail_preference", 0.5))
                ),
                example_preference=min(
                    1.0, max(0.0, parsed.get("example_preference", 0.7))
                ),
                explanation=parsed.get("explanation", "学习风格分析结果"),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_input,
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse learning style response: {e}")
            return LearningStyleResult(
                processing_preference=ProcessingPreference.VISUAL,
                learning_pace=LearningPace.GRADUAL,
                feedback_style=FeedbackStyle.GUIDED,
                knowledge_construction=KnowledgeConstruction.LINEAR,
                interaction_density=0.5,
                detail_preference=0.5,
                example_preference=0.7,
                explanation="解析错误，使用默认学习风格设置",
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_query": original_input,
                    "error": str(e),
                },
            )


class CognitiveAnalysisManager(
    LLMModuleManager[CognitiveAnalysisResult, UserModelingConfig]
):
    """认知特征分析管理器"""

    def __init__(self):
        super().__init__("cognitive_analysis")


class LearningStyleManager(LLMModuleManager[LearningStyleResult, UserModelingConfig]):
    """学习风格分析管理器"""

    def __init__(self):
        super().__init__("learning_style_analysis")
