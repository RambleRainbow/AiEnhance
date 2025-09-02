"""
认知层模块 - 对应设计文档第5章
包含多层次记忆激活、语义补充、类比推理等核心认知功能

重构后的认知层采用新的层-模块-子模块架构。
"""

# 新架构的主要入口点
from .cognition_layer import CognitionLayer

from .analogy_reasoning import (
    AnalogyMapping,
    AnalogyRetriever,
    AssociationType,
    CreativeAssociation,
    CreativeAssociationGenerator,
    FrameworkType,
    IntegratedAnalogyReasoner,
    SimilarityType,
    ThinkingFramework,
    ThinkingFrameworkMatcher,
)
from .memory_activation import (
    ActivationLevel,
    ActivationResult,
    DeepActivator,
    MemoryFragment,
    MetaActivator,
    MultiLevelMemoryActivator,
    RelationType,
    SurfaceActivator,
)
from .semantic_enhancement import (
    BridgingStrategy,
    ConceptGap,
    ConceptGapIdentifier,
    ContextualIntegrator,
    GapType,
    IntegratedSemanticEnhancer,
    IntegrationLevel,
    IntegrationResult,
    SemanticBridge,
    SemanticBridgeBuilder,
)

__all__ = [
    # 新架构 - 推荐使用
    "CognitionLayer",
    # 原有架构 - 向后兼容
    "MemoryFragment",
    "ActivationResult",
    "MultiLevelMemoryActivator",
    "SurfaceActivator",
    "DeepActivator",
    "MetaActivator",
    "ActivationLevel",
    "RelationType",
    "ConceptGap",
    "SemanticBridge",
    "IntegrationResult",
    "IntegratedSemanticEnhancer",
    "ConceptGapIdentifier",
    "SemanticBridgeBuilder",
    "ContextualIntegrator",
    "GapType",
    "BridgingStrategy",
    "IntegrationLevel",
    "AnalogyMapping",
    "ThinkingFramework",
    "CreativeAssociation",
    "IntegratedAnalogyReasoner",
    "AnalogyRetriever",
    "ThinkingFrameworkMatcher",
    "CreativeAssociationGenerator",
    "SimilarityType",
    "FrameworkType",
    "AssociationType",
]
