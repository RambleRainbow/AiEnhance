"""
认知系统核心模块
提供记忆-认知协同系统的核心功能

包含两套架构：
1. 重构后的层-模块-子模块架构（推荐使用）
2. 原有的分层架构（向后兼容）
"""

# 重构后的架构 - 推荐使用
from .base_architecture import (
    BaseLayer,
    BaseModule, 
    BaseSubModule,
    CognitiveSystem,
    ProcessingContext,
    ProcessingResult,
    ProcessingPhase
)
from .restructured_system_factory import (
    create_restructured_cognitive_system,
    create_educational_system,
    create_research_system,
    create_creative_system,
    create_lightweight_system,
    create_system_from_config,
    initialize_system_async
)

# 原有的分层架构 - 向后兼容
from ..layers import (
    BehaviorLayer as LegacyBehaviorLayer,
    CognitionLayer as LegacyCognitionLayer,
    CollaborationLayer as LegacyCollaborationLayer,
    PerceptionLayer as LegacyPerceptionLayer,
)
from ..layers.layer_interfaces import (
    ContextProfile,
    IBehaviorLayer,
    ICognitionLayer,
    ICognitiveLayers,
    ICollaborationLayer,
    InformationFlow,
    IPerceptionLayer,
    ProcessingStatus,
    SystemResponse,
    UserProfile,
)
from .layered_cognitive_system import LayeredCognitiveSystem
from .layered_system_factory import LayeredSystemFactory

__all__ = [
    # 重构后的架构 - 推荐使用
    "BaseLayer",
    "BaseModule", 
    "BaseSubModule",
    "CognitiveSystem",
    "ProcessingContext",
    "ProcessingResult",
    "ProcessingPhase",
    "create_restructured_cognitive_system",
    "create_educational_system",
    "create_research_system",
    "create_creative_system",
    "create_lightweight_system",
    "create_system_from_config",
    "initialize_system_async",
    # 原有架构 - 向后兼容
    "IPerceptionLayer",
    "ICognitionLayer",
    "IBehaviorLayer",
    "ICollaborationLayer",
    "ICognitiveLayers",
    "SystemResponse",
    "UserProfile",
    "ContextProfile",
    "InformationFlow",
    "ProcessingStatus",
    "LegacyPerceptionLayer",
    "LegacyCognitionLayer",
    "LegacyBehaviorLayer",
    "LegacyCollaborationLayer",
    "LayeredCognitiveSystem",
    "LayeredSystemFactory",
]
