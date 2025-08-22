"""
认知系统核心模块
提供记忆-认知协同系统的核心功能
"""

# 新的分层架构
from .behavior_layer import BehaviorLayer
from .cognition_layer import CognitionLayer
from .collaboration_layer import CollaborationLayer
from .layer_interfaces import (
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
from .perception_layer import PerceptionLayer

__all__ = [
    # 分层架构接口
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
    # 分层架构实现
    "PerceptionLayer",
    "CognitionLayer",
    "BehaviorLayer",
    "CollaborationLayer",
    "LayeredCognitiveSystem",
    "LayeredSystemFactory",
]
