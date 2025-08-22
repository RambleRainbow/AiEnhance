"""
协作层接口定义
定义协作层各组件的数据结构和接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class PerspectiveType(Enum):
    """视角类型"""

    OPPOSING = "opposing"  # 对立观点
    ALTERNATIVE = "alternative"  # 替代方案
    MULTI_DISCIPLINARY = "multi_disciplinary"  # 多学科视角
    STAKEHOLDER = "stakeholder"  # 利益相关者视角
    TEMPORAL = "temporal"  # 时间维度视角
    CONTEXTUAL = "contextual"  # 情境视角


class DisciplineCategory(Enum):
    """学科类别"""

    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    BIOLOGY = "biology"
    PSYCHOLOGY = "psychology"
    ECONOMICS = "economics"
    SOCIOLOGY = "sociology"
    ENGINEERING = "engineering"
    PHILOSOPHY = "philosophy"
    HISTORY = "history"
    ARTS = "arts"
    COMPUTER_SCIENCE = "computer_science"
    COGNITIVE_SCIENCE = "cognitive_science"


class ChallengeType(Enum):
    """认知挑战类型"""

    ASSUMPTION_QUESTIONING = "assumption_questioning"  # 假设质疑
    BLIND_SPOT_DETECTION = "blind_spot_detection"  # 盲点检测
    COMPLEXITY_EXPANSION = "complexity_expansion"  # 复杂性扩展
    CREATIVE_PROVOCATION = "creative_provocation"  # 创意激发


@dataclass
class PerspectiveRequest:
    """视角生成请求"""

    content: str  # 待分析的内容
    user_position: str | None = None  # 用户的立场/观点
    perspective_types: list[PerspectiveType] = None  # 请求的视角类型
    disciplines: list[DisciplineCategory] = None  # 请求的学科视角
    depth_level: str = "moderate"  # 深度级别: shallow, moderate, deep
    max_perspectives: int = 3  # 最大视角数量
    context: dict[str, Any] | None = None  # 上下文信息


@dataclass
class Perspective:
    """单个视角"""

    perspective_type: PerspectiveType
    title: str  # 视角标题
    description: str  # 视角描述
    key_arguments: list[str]  # 关键论据
    supporting_evidence: list[str]  # 支持证据
    discipline: DisciplineCategory | None = None  # 相关学科
    stakeholder: str | None = None  # 利益相关者
    confidence: float = 0.8  # 可信度
    relevance_score: float = 0.8  # 相关性评分


@dataclass
class PerspectiveResult:
    """视角生成结果"""

    perspectives: list[Perspective]
    synthesis: str | None = None  # 综合分析
    dialectical_tensions: list[str] = None  # 辩证冲突点
    integration_suggestions: list[str] = None  # 整合建议
    generation_metadata: dict[str, Any] = None


@dataclass
class ChallengeRequest:
    """认知挑战请求"""

    content: str  # 待挑战的内容
    user_reasoning: str | None = None  # 用户的推理过程
    challenge_types: list[ChallengeType] = None  # 挑战类型
    intensity_level: str = "moderate"  # 挑战强度: gentle, moderate, strong
    focus_areas: list[str] = None  # 重点关注领域
    context: dict[str, Any] | None = None


@dataclass
class Challenge:
    """单个认知挑战"""

    challenge_type: ChallengeType
    title: str  # 挑战标题
    description: str  # 挑战描述
    questions: list[str]  # 挑战性问题
    alternative_frameworks: list[str]  # 替代框架
    hidden_assumptions: list[str]  # 隐藏假设
    potential_biases: list[str]  # 潜在偏见
    expansion_directions: list[str]  # 扩展方向


@dataclass
class ChallengeResult:
    """认知挑战结果"""

    challenges: list[Challenge]
    meta_reflection: str | None = None  # 元认知反思
    growth_opportunities: list[str] = None  # 成长机会
    next_steps: list[str] = None  # 下一步建议
    challenge_metadata: dict[str, Any] = None


@dataclass
class CollaborationContext:
    """协作上下文"""

    user_id: str
    session_id: str
    interaction_history: list[dict[str, Any]] = None
    user_cognitive_profile: dict[str, Any] | None = None  # 用户认知画像
    collaboration_preferences: dict[str, Any] = None  # 协作偏好
    current_task_context: dict[str, Any] | None = None  # 当前任务上下文


class PerspectiveGenerator(ABC):
    """视角生成器抽象接口"""

    @abstractmethod
    async def generate_perspectives(
        self, request: PerspectiveRequest, context: CollaborationContext
    ) -> PerspectiveResult:
        """生成多元视角"""
        pass

    @abstractmethod
    async def synthesize_perspectives(self, perspectives: list[Perspective]) -> str:
        """综合多个视角"""
        pass


class CognitiveChallenger(ABC):
    """认知挑战器抽象接口"""

    @abstractmethod
    async def generate_challenges(
        self, request: ChallengeRequest, context: CollaborationContext
    ) -> ChallengeResult:
        """生成认知挑战"""
        pass

    @abstractmethod
    async def adapt_challenge_intensity(
        self, base_challenge: Challenge, user_response: str
    ) -> Challenge:
        """适应挑战强度"""
        pass


class CollaborationOrchestrator(ABC):
    """协作编排器抽象接口"""

    @abstractmethod
    async def orchestrate_collaboration(
        self, content: str, context: CollaborationContext
    ) -> dict[str, Any]:
        """编排协作过程"""
        pass

    @abstractmethod
    async def update_user_cognitive_profile(
        self, context: CollaborationContext, interaction_data: dict[str, Any]
    ) -> bool:
        """更新用户认知画像"""
        pass
