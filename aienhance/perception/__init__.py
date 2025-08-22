"""
感知层模块 - 对应设计文档第4章
包含用户建模和情境分析等核心感知功能
"""

from .context_analysis import (
    AbstractionLevel,
    CognitiveNeeds,
    ContextProfile,
    ContextualElements,
    IntegratedContextAnalyzer,
    PurposeType,
    TaskCharacteristics,
    TaskType,
    TimeDimension,
)
from .user_modeling import (
    CognitiveProfile,
    CognitiveStyle,
    DynamicUserModeler,
    InteractionProfile,
    KnowledgeProfile,
    ThinkingMode,
    UserProfile,
)

__all__ = [
    # User Modeling
    "UserProfile",
    "CognitiveProfile",
    "KnowledgeProfile",
    "InteractionProfile",
    "DynamicUserModeler",
    "CognitiveStyle",
    "ThinkingMode",
    # Context Analysis
    "ContextProfile",
    "TaskCharacteristics",
    "ContextualElements",
    "CognitiveNeeds",
    "IntegratedContextAnalyzer",
    "TaskType",
    "TimeDimension",
    "AbstractionLevel",
    "PurposeType",
]
