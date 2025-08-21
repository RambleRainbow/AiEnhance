"""
认知层模块 - 对应设计文档第5章
包含多层次记忆激活、语义补充、类比推理等核心认知功能
"""

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
    # Memory Activation
    'MemoryFragment',
    'ActivationResult',
    'MultiLevelMemoryActivator',
    'SurfaceActivator',
    'DeepActivator',
    'MetaActivator',
    'ActivationLevel',
    'RelationType',

    # Semantic Enhancement
    'ConceptGap',
    'SemanticBridge',
    'IntegrationResult',
    'IntegratedSemanticEnhancer',
    'ConceptGapIdentifier',
    'SemanticBridgeBuilder',
    'ContextualIntegrator',
    'GapType',
    'BridgingStrategy',
    'IntegrationLevel',

    # Analogy Reasoning
    'AnalogyMapping',
    'ThinkingFramework',
    'CreativeAssociation',
    'IntegratedAnalogyReasoner',
    'AnalogyRetriever',
    'ThinkingFrameworkMatcher',
    'CreativeAssociationGenerator',
    'SimilarityType',
    'FrameworkType',
    'AssociationType'
]
