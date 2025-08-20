"""
认知系统核心模块
提供记忆-认知协同系统的核心功能
"""

# 新的分层架构
from .layer_interfaces import (
    IPerceptionLayer,
    ICognitionLayer, 
    IBehaviorLayer,
    ICollaborationLayer,
    ICognitiveLayers,
    SystemResponse,
    UserProfile,
    ContextProfile,
    InformationFlow,
    ProcessingStatus
)

from .perception_layer import PerceptionLayer
from .cognition_layer import CognitionLayer
from .behavior_layer import BehaviorLayer
from .collaboration_layer import CollaborationLayer
from .layered_cognitive_system import LayeredCognitiveSystem
from .layered_system_factory import LayeredSystemFactory

# 向后兼容的旧架构
from .memory_cognitive_system import (
    MemoryCognitiveSystem,
    SystemFactory
)

__all__ = [
    # 新的分层架构接口
    'IPerceptionLayer',
    'ICognitionLayer',
    'IBehaviorLayer', 
    'ICollaborationLayer',
    'ICognitiveLayers',
    'SystemResponse',
    'UserProfile',
    'ContextProfile',
    'InformationFlow',
    'ProcessingStatus',
    
    # 新的分层架构实现
    'PerceptionLayer',
    'CognitionLayer',
    'BehaviorLayer',
    'CollaborationLayer',
    'LayeredCognitiveSystem',
    
    # 向后兼容
    'MemoryCognitiveSystem',
    'SystemFactory'
]