"""
感知层模块 - 对应设计文档第4章
包含用户建模和情境分析等核心感知功能

重构后的感知层采用新的层-模块-子模块架构，
主要入口点是PerceptionLayer类。
"""

# 新架构的主要入口点
from .perception_layer import PerceptionLayer
from .user_modeling.user_modeling_module import UserModelingModule  
from .context_analysis.context_analysis_module import ContextAnalysisModule

# 保留原有的导入以维持向后兼容性
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
    # 新架构 - 推荐使用
    "PerceptionLayer",
    "UserModelingModule",
    "ContextAnalysisModule",
    # 原有架构 - 向后兼容
    "UserProfile",
    "CognitiveProfile",
    "KnowledgeProfile",
    "InteractionProfile",
    "DynamicUserModeler",
    "CognitiveStyle",
    "ThinkingMode",
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
