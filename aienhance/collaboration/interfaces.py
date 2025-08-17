"""
协作层接口定义
定义协作层各组件的数据结构和接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Enum
from enum import Enum


class PerspectiveType(Enum):
    """视角类型"""
    OPPOSING = "opposing"          # 对立观点
    ALTERNATIVE = "alternative"    # 替代方案
    MULTI_DISCIPLINARY = "multi_disciplinary"  # 多学科视角
    STAKEHOLDER = "stakeholder"    # 利益相关者视角
    TEMPORAL = "temporal"          # 时间维度视角
    CONTEXTUAL = "contextual"      # 情境视角


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
    BLIND_SPOT_DETECTION = "blind_spot_detection"     # 盲点检测
    COMPLEXITY_EXPANSION = "complexity_expansion"      # 复杂性扩展
    CREATIVE_PROVOCATION = "creative_provocation"      # 创意激发


@dataclass
class PerspectiveRequest:
    """视角生成请求"""
    content: str                           # 待分析的内容
    user_position: Optional[str] = None    # 用户的立场/观点
    perspective_types: List[PerspectiveType] = None  # 请求的视角类型
    disciplines: List[DisciplineCategory] = None     # 请求的学科视角
    depth_level: str = "moderate"          # 深度级别: shallow, moderate, deep
    max_perspectives: int = 3              # 最大视角数量
    context: Optional[Dict[str, Any]] = None  # 上下文信息


@dataclass 
class Perspective:
    """单个视角"""
    perspective_type: PerspectiveType
    title: str                             # 视角标题
    description: str                       # 视角描述
    key_arguments: List[str]               # 关键论据
    supporting_evidence: List[str]         # 支持证据
    discipline: Optional[DisciplineCategory] = None  # 相关学科
    stakeholder: Optional[str] = None      # 利益相关者
    confidence: float = 0.8                # 可信度
    relevance_score: float = 0.8           # 相关性评分


@dataclass
class PerspectiveResult:
    """视角生成结果"""
    perspectives: List[Perspective]
    synthesis: Optional[str] = None        # 综合分析
    dialectical_tensions: List[str] = None # 辩证冲突点
    integration_suggestions: List[str] = None  # 整合建议
    generation_metadata: Dict[str, Any] = None


@dataclass
class ChallengeRequest:
    """认知挑战请求"""
    content: str                           # 待挑战的内容
    user_reasoning: Optional[str] = None   # 用户的推理过程
    challenge_types: List[ChallengeType] = None  # 挑战类型
    intensity_level: str = "moderate"      # 挑战强度: gentle, moderate, strong
    focus_areas: List[str] = None          # 重点关注领域
    context: Optional[Dict[str, Any]] = None


@dataclass
class Challenge:
    """单个认知挑战"""
    challenge_type: ChallengeType
    title: str                             # 挑战标题
    description: str                       # 挑战描述
    questions: List[str]                   # 挑战性问题
    alternative_frameworks: List[str]      # 替代框架
    hidden_assumptions: List[str]          # 隐藏假设
    potential_biases: List[str]            # 潜在偏见
    expansion_directions: List[str]        # 扩展方向


@dataclass
class ChallengeResult:
    """认知挑战结果"""
    challenges: List[Challenge]
    meta_reflection: Optional[str] = None  # 元认知反思
    growth_opportunities: List[str] = None # 成长机会
    next_steps: List[str] = None          # 下一步建议
    challenge_metadata: Dict[str, Any] = None


@dataclass
class CollaborationContext:
    """协作上下文"""
    user_id: str
    session_id: str
    interaction_history: List[Dict[str, Any]] = None
    user_cognitive_profile: Optional[Dict[str, Any]] = None  # 用户认知画像
    collaboration_preferences: Dict[str, Any] = None         # 协作偏好
    current_task_context: Optional[Dict[str, Any]] = None    # 当前任务上下文


class PerspectiveGenerator(ABC):
    """视角生成器抽象接口"""
    
    @abstractmethod
    async def generate_perspectives(self, request: PerspectiveRequest, 
                                   context: CollaborationContext) -> PerspectiveResult:
        """生成多元视角"""
        pass
    
    @abstractmethod
    async def synthesize_perspectives(self, perspectives: List[Perspective]) -> str:
        """综合多个视角"""
        pass


class CognitiveChallenger(ABC):
    """认知挑战器抽象接口"""
    
    @abstractmethod
    async def generate_challenges(self, request: ChallengeRequest,
                                 context: CollaborationContext) -> ChallengeResult:
        """生成认知挑战"""
        pass
    
    @abstractmethod
    async def adapt_challenge_intensity(self, base_challenge: Challenge,
                                       user_response: str) -> Challenge:
        """适应挑战强度"""
        pass


class CollaborationOrchestrator(ABC):
    """协作编排器抽象接口"""
    
    @abstractmethod
    async def orchestrate_collaboration(self, content: str, 
                                       context: CollaborationContext) -> Dict[str, Any]:
        """编排协作过程"""
        pass
    
    @abstractmethod
    async def update_user_cognitive_profile(self, context: CollaborationContext,
                                          interaction_data: Dict[str, Any]) -> bool:
        """更新用户认知画像"""
        pass