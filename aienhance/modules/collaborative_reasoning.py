"""
协作推理模块 - 基于LLM的重构版本  
使用大模型进行多视角生成、认知挑战和协作协调
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core.llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

logger = logging.getLogger(__name__)


class PerspectiveType(Enum):
    """视角类型"""
    
    ANALYTICAL = "analytical"       # 分析型视角
    CREATIVE = "creative"           # 创造型视角
    CRITICAL = "critical"           # 批判型视角
    PRACTICAL = "practical"         # 实用型视角
    THEORETICAL = "theoretical"     # 理论型视角
    ETHICAL = "ethical"             # 伦理型视角


class ChallengeType(Enum):
    """挑战类型"""
    
    ASSUMPTION = "assumption"       # 假设质疑
    LOGIC = "logic"                 # 逻辑挑战
    EVIDENCE = "evidence"           # 证据检验
    ALTERNATIVE = "alternative"     # 替代方案
    IMPLICATION = "implication"     # 推论挑战


class ReasoningStrategy(Enum):
    """推理策略"""
    
    DIALECTICAL = "dialectical"     # 辩证推理
    ANALOGICAL = "analogical"       # 类比推理
    DEDUCTIVE = "deductive"         # 演绎推理
    INDUCTIVE = "inductive"         # 归纳推理
    ABDUCTIVE = "abductive"         # 溯因推理


@dataclass
class Perspective:
    """视角对象"""
    
    perspective_type: PerspectiveType
    content: str
    reasoning: str
    confidence: float
    supporting_evidence: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CognitiveChallenge:
    """认知挑战对象"""
    
    challenge_type: ChallengeType
    target_assumption: str
    challenge_question: str
    alternative_perspective: str
    evidence_analysis: str
    impact_assessment: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MultiPerspectiveResult:
    """多视角生成结果"""
    
    perspectives: List[Perspective]
    synthesis: str  # 视角综合
    conflicts: List[Dict[str, Any]]  # 视角冲突
    complementarities: List[Dict[str, Any]]  # 视角互补
    dominant_theme: str  # 主导主题
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChallengeGenerationResult:
    """挑战生成结果"""
    
    challenges: List[CognitiveChallenge]
    critical_points: List[str]  # 关键质疑点
    reasoning_gaps: List[str]   # 推理漏洞
    improvement_suggestions: List[str]  # 改进建议
    overall_assessment: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CollaborativeReasoningResult:
    """协作推理结果"""
    
    reasoning_strategy: ReasoningStrategy
    collaborative_insights: List[str]
    consensus_points: List[str]  # 共识点
    divergent_points: List[str]  # 分歧点
    synthesized_conclusion: str  # 综合结论
    quality_score: float         # 推理质量评分
    coherence_score: float       # 一致性评分
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CollaborativeReasoningConfig(LLMModuleConfig):
    """协作推理配置"""
    
    reasoning_type: str = "multi_perspective"  # "multi_perspective", "challenge_generation", "collaborative_reasoning"
    max_perspectives: int = 5  # 最大视角数
    challenge_depth: str = "moderate"  # "shallow", "moderate", "deep"
    
    def __post_init__(self):
        if not self.prompt_template_name:
            if self.reasoning_type == "challenge_generation":
                self.prompt_template_name = "cognitive_challenge"
            elif self.reasoning_type == "collaborative_reasoning":
                self.prompt_template_name = "collaborative_reasoning"
            else:
                self.prompt_template_name = "dialectical_perspective"
        if self.temperature is None:
            self.temperature = 0.7  # 高温度，鼓励创造性和多样性
        if self.max_tokens is None:
            self.max_tokens = 800


class LLMMultiPerspectiveProvider(
    LLMModuleProvider[MultiPerspectiveResult, CollaborativeReasoningConfig]
):
    """基于大模型的多视角生成提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for multi-perspective generation")
                return False

            self.is_initialized = True
            logger.info("LLM multi-perspective provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize multi-perspective provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> MultiPerspectiveResult:
        """处理多视角生成业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Multi-perspective provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Multi-perspective generation failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备多视角生成提示词变量"""
        original_query = input_data
        user_background = ""
        domain_context = ""
        previous_analysis = ""
        
        if context:
            user_background = context.get("user_background", context.get("background_info", ""))
            domain_context = context.get("domain_context", "")
            previous_analysis = context.get("previous_analysis", context.get("behavior_output", ""))
            
        return {
            "original_query": original_query,
            "user_background": user_background or "无特定用户背景",
            "domain_context": domain_context or "通用领域", 
            "previous_analysis": previous_analysis or "无先前分析结果",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> MultiPerspectiveResult:
        """解析多视角生成LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析视角列表
            perspectives = []
            perspectives_data = parsed.get("perspectives", [])
            
            for i, persp_data in enumerate(perspectives_data):
                if isinstance(persp_data, dict):
                    # 解析视角类型
                    persp_type_str = persp_data.get("type", "analytical").lower()
                    perspective_type = PerspectiveType.ANALYTICAL
                    for type_enum in PerspectiveType:
                        if type_enum.value in persp_type_str:
                            perspective_type = type_enum
                            break

                    perspective = Perspective(
                        perspective_type=perspective_type,
                        content=persp_data.get("content", ""),
                        reasoning=persp_data.get("reasoning", ""),
                        confidence=min(1.0, max(0.0, persp_data.get("confidence", 0.7))),
                        supporting_evidence=persp_data.get("supporting_evidence", []),
                        metadata=persp_data.get("metadata", {})
                    )
                    perspectives.append(perspective)

            # 解析冲突和互补关系
            conflicts = parsed.get("conflicts", [])
            if not isinstance(conflicts, list):
                conflicts = []

            complementarities = parsed.get("complementarities", [])
            if not isinstance(complementarities, list):
                complementarities = []

            return MultiPerspectiveResult(
                perspectives=perspectives,
                synthesis=parsed.get("synthesis", "多视角综合分析"),
                conflicts=conflicts,
                complementarities=complementarities,
                dominant_theme=parsed.get("dominant_theme", "核心主题"),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_topic": original_input,
                    "perspectives_count": len(perspectives),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse multi-perspective response: {e}")
            # 返回基本的单视角结果作为降级
            return MultiPerspectiveResult(
                perspectives=[
                    Perspective(
                        perspective_type=PerspectiveType.ANALYTICAL,
                        content=f"对「{original_input}」的基础分析视角",
                        reasoning="解析错误时的降级分析",
                        confidence=0.3,
                        supporting_evidence=[],
                        metadata={"fallback": True}
                    )
                ],
                synthesis="解析错误，提供基础分析",
                conflicts=[],
                complementarities=[],
                dominant_theme="基础分析主题",
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_topic": original_input,
                    "error": str(e),
                },
            )


class LLMChallengeGenerationProvider(
    LLMModuleProvider[ChallengeGenerationResult, CollaborativeReasoningConfig]
):
    """基于大模型的认知挑战生成提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for challenge generation")
                return False

            self.is_initialized = True
            logger.info("LLM challenge generation provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize challenge generation provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> ChallengeGenerationResult:
        """处理认知挑战生成业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Challenge generation provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Challenge generation failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备挑战生成提示词变量"""
        content_to_challenge = input_data
        user_cognitive_level = "中等水平"
        learning_preferences = "结构化学习"
        
        if context:
            user_profile = context.get("user_profile")
            if user_profile and hasattr(user_profile, 'cognitive_characteristics'):
                cognitive_chars = user_profile.cognitive_characteristics
                complexity = cognitive_chars.get("cognitive_complexity", 0.5)
                if complexity < 0.3:
                    user_cognitive_level = "基础水平"
                elif complexity > 0.7:
                    user_cognitive_level = "高级水平"
                    
            if user_profile and hasattr(user_profile, 'interaction_preferences'):
                interact_prefs = user_profile.interaction_preferences
                learning_preferences = str(interact_prefs.get("learning_style", "结构化学习"))
            
        return {
            "content_to_challenge": content_to_challenge,
            "user_cognitive_level": user_cognitive_level,
            "learning_preferences": learning_preferences,
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> ChallengeGenerationResult:
        """解析挑战生成LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析挑战列表
            challenges = []
            challenges_data = parsed.get("challenges", [])
            
            for challenge_data in challenges_data:
                if isinstance(challenge_data, dict):
                    # 解析挑战类型
                    challenge_type_str = challenge_data.get("type", "assumption").lower()
                    challenge_type = ChallengeType.ASSUMPTION
                    for type_enum in ChallengeType:
                        if type_enum.value in challenge_type_str:
                            challenge_type = type_enum
                            break

                    challenge = CognitiveChallenge(
                        challenge_type=challenge_type,
                        target_assumption=challenge_data.get("target_assumption", ""),
                        challenge_question=challenge_data.get("challenge_question", ""),
                        alternative_perspective=challenge_data.get("alternative_perspective", ""),
                        evidence_analysis=challenge_data.get("evidence_analysis", ""),
                        impact_assessment=min(1.0, max(0.0, challenge_data.get("impact_assessment", 0.5))),
                        metadata=challenge_data.get("metadata", {})
                    )
                    challenges.append(challenge)

            # 解析其他字段
            critical_points = parsed.get("critical_points", [])
            if not isinstance(critical_points, list):
                critical_points = []

            reasoning_gaps = parsed.get("reasoning_gaps", [])
            if not isinstance(reasoning_gaps, list):
                reasoning_gaps = []

            improvement_suggestions = parsed.get("improvement_suggestions", [])
            if not isinstance(improvement_suggestions, list):
                improvement_suggestions = []

            return ChallengeGenerationResult(
                challenges=challenges,
                critical_points=critical_points,
                reasoning_gaps=reasoning_gaps,
                improvement_suggestions=improvement_suggestions,
                overall_assessment=parsed.get("overall_assessment", "挑战性分析完成"),
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_statement": original_input,
                    "challenges_count": len(challenges),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse challenge generation response: {e}")
            return ChallengeGenerationResult(
                challenges=[],
                critical_points=[],
                reasoning_gaps=[],
                improvement_suggestions=["解析错误，建议重新分析"],
                overall_assessment="解析错误，无法生成有效挑战",
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_statement": original_input,
                    "error": str(e),
                },
            )


class MultiPerspectiveManager(LLMModuleManager[MultiPerspectiveResult, CollaborativeReasoningConfig]):
    """多视角生成管理器"""

    def __init__(self):
        super().__init__("multi_perspective")


class ChallengeGenerationManager(LLMModuleManager[ChallengeGenerationResult, CollaborativeReasoningConfig]):
    """认知挑战生成管理器"""

    def __init__(self):
        super().__init__("challenge_generation")