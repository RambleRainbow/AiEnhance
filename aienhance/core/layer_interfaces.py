"""
认知系统核心层接口定义
定义感知层、认知层、行为层、协作层的核心抽象接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import asyncio


# ===== 通用数据结构 =====

class ProcessingStatus(Enum):
    """处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class LayerOutput:
    """层输出基类"""
    layer_name: str
    status: ProcessingStatus
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    processing_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class InformationFlow:
    """层间信息流"""
    from_layer: str
    to_layer: str
    data: Any
    flow_type: str  # "input", "output", "feedback"
    timestamp: str


# ===== 感知层接口 =====

@dataclass
class PerceptionInput:
    """感知层输入"""
    query: str
    user_id: str
    context: Dict[str, Any]
    historical_data: Optional[List[Any]] = None


@dataclass
class UserProfile:
    """用户画像（简化版，用于接口定义）"""
    user_id: str
    cognitive_characteristics: Dict[str, Any]
    knowledge_profile: Dict[str, Any]
    interaction_preferences: Dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class ContextProfile:
    """情境画像（简化版，用于接口定义）"""
    task_type: str
    complexity_level: float
    domain_characteristics: Dict[str, Any]
    environmental_factors: Dict[str, Any]


@dataclass
class PerceptionOutput(LayerOutput):
    """感知层输出"""
    user_profile: UserProfile = None
    context_profile: ContextProfile = None
    perception_insights: Dict[str, Any] = field(default_factory=dict)


class IPerceptionLayer(ABC):
    """感知层接口"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化感知层"""
        pass
    
    @abstractmethod
    async def process(self, input_data: PerceptionInput) -> PerceptionOutput:
        """处理感知层输入，生成用户画像和情境分析"""
        pass
    
    @abstractmethod
    async def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> bool:
        """更新用户画像"""
        pass
    
    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


# ===== 认知层接口 =====

@dataclass
class CognitionInput:
    """认知层输入"""
    query: str
    user_profile: UserProfile
    context_profile: ContextProfile
    external_memories: List[Any]
    perception_insights: Dict[str, Any]


@dataclass
class MemoryActivation:
    """记忆激活结果"""
    activated_fragments: List[Any]
    activation_confidence: float
    activation_metadata: Dict[str, Any]


@dataclass
class SemanticEnhancement:
    """语义增强结果"""
    enhanced_content: List[Any]
    semantic_gaps_filled: List[str]
    enhancement_confidence: float


@dataclass
class AnalogyReasoning:
    """类比推理结果"""
    analogies: List[Dict[str, Any]]
    reasoning_chains: List[List[str]]
    confidence_scores: List[float]


@dataclass
class CognitionOutput(LayerOutput):
    """认知层输出"""
    memory_activation: MemoryActivation = None
    semantic_enhancement: SemanticEnhancement = None
    analogy_reasoning: AnalogyReasoning = None
    cognitive_insights: Dict[str, Any] = field(default_factory=dict)


class ICognitionLayer(ABC):
    """认知层接口"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化认知层"""
        pass
    
    @abstractmethod
    async def process(self, input_data: CognitionInput) -> CognitionOutput:
        """处理认知层输入，进行记忆激活、语义增强和类比推理"""
        pass
    
    @abstractmethod
    async def activate_memories(self, query: str, context: Dict[str, Any]) -> MemoryActivation:
        """激活相关记忆"""
        pass
    
    @abstractmethod
    async def enhance_semantics(self, fragments: List[Any], context: Dict[str, Any]) -> SemanticEnhancement:
        """语义增强"""
        pass
    
    @abstractmethod
    async def reason_analogies(self, query: str, context: Dict[str, Any]) -> AnalogyReasoning:
        """类比推理"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


# ===== 行为层接口 =====

@dataclass
class BehaviorInput:
    """行为层输入"""
    query: str
    user_profile: UserProfile
    context_profile: ContextProfile
    cognition_output: CognitionOutput
    generation_requirements: Dict[str, Any]


@dataclass
class AdaptedContent:
    """适配内容"""
    content: str
    adaptation_strategy: str
    cognitive_load: float
    information_density: str
    structure_type: str
    personalization_level: float


@dataclass
class BehaviorOutput(LayerOutput):
    """行为层输出"""
    adapted_content: AdaptedContent = None
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)


class IBehaviorLayer(ABC):
    """行为层接口"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化行为层"""
        pass
    
    @abstractmethod
    async def process(self, input_data: BehaviorInput) -> BehaviorOutput:
        """处理行为层输入，生成适配内容"""
        pass
    
    @abstractmethod
    async def adapt_content(self, content: str, user_profile: UserProfile, 
                          context: Dict[str, Any]) -> AdaptedContent:
        """内容适配"""
        pass
    
    @abstractmethod
    async def generate_response(self, input_data: BehaviorInput) -> str:
        """生成响应内容"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


# ===== 协作层接口 =====

@dataclass
class CollaborationInput:
    """协作层输入"""
    query: str
    user_profile: UserProfile
    context_profile: ContextProfile
    behavior_output: BehaviorOutput
    collaboration_context: Dict[str, Any]


@dataclass
class PerspectiveGeneration:
    """观点生成结果"""
    perspectives: List[Dict[str, Any]]
    perspective_diversity: float
    generation_metadata: Dict[str, Any]


@dataclass
class CognitiveChallenge:
    """认知挑战结果"""
    challenges: List[Dict[str, Any]]
    challenge_intensity: float
    educational_value: float


@dataclass
class CollaborationOutput(LayerOutput):
    """协作层输出"""
    perspective_generation: PerspectiveGeneration = None
    cognitive_challenge: CognitiveChallenge = None
    collaboration_insights: Dict[str, Any] = field(default_factory=dict)
    enhanced_content: Optional[str] = None


class ICollaborationLayer(ABC):
    """协作层接口"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化协作层"""
        pass
    
    @abstractmethod
    async def process(self, input_data: CollaborationInput) -> CollaborationOutput:
        """处理协作层输入，生成多元观点和认知挑战"""
        pass
    
    @abstractmethod
    async def generate_perspectives(self, query: str, context: Dict[str, Any]) -> PerspectiveGeneration:
        """生成多元观点"""
        pass
    
    @abstractmethod
    async def create_cognitive_challenges(self, content: str, user_profile: UserProfile) -> CognitiveChallenge:
        """创建认知挑战"""
        pass
    
    @abstractmethod
    async def orchestrate_collaboration(self, input_data: CollaborationInput) -> CollaborationOutput:
        """编排协作过程"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


# ===== 系统层接口 =====

@dataclass
class SystemResponse:
    """系统响应"""
    content: str
    perception_output: PerceptionOutput
    cognition_output: CognitionOutput
    behavior_output: BehaviorOutput
    collaboration_output: Optional[CollaborationOutput]
    processing_metadata: Dict[str, Any]


class ICognitiveLayers(ABC):
    """认知系统层级管理接口"""
    
    @abstractmethod
    async def initialize_layers(self) -> bool:
        """初始化所有层"""
        pass
    
    @abstractmethod
    async def process_through_layers(self, query: str, user_id: str, 
                                   context: Dict[str, Any]) -> SystemResponse:
        """通过各层处理用户查询"""
        pass
    
    @abstractmethod
    async def process_stream(self, query: str, user_id: str, 
                           context: Dict[str, Any]) -> AsyncIterator[str]:
        """流式处理"""
        pass
    
    @abstractmethod
    def get_layer_status(self, layer_name: str) -> Dict[str, Any]:
        """获取层状态"""
        pass
    
    @abstractmethod
    def get_information_flows(self) -> List[InformationFlow]:
        """获取信息流记录"""
        pass
    
    @abstractmethod
    async def cleanup_all_layers(self) -> None:
        """清理所有层资源"""
        pass