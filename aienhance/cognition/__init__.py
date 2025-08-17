"""
认知层模块 - 对应设计文档第5章
包含多层次记忆激活、语义补充、类比推理等核心认知功能
"""

from .memory_activation import (
    MemoryFragment,
    ActivationResult,
    MultiLevelMemoryActivator,
    SurfaceActivator,
    DeepActivator,
    MetaActivator,
    ActivationLevel,
    RelationType
)

from .semantic_enhancement import (
    ConceptGap,
    SemanticBridge,
    IntegrationResult,
    IntegratedSemanticEnhancer,
    ConceptGapIdentifier,
    SemanticBridgeBuilder,
    ContextualIntegrator,
    GapType,
    BridgingStrategy,
    IntegrationLevel
)

from .analogy_reasoning import (
    AnalogyMapping,
    ThinkingFramework,
    CreativeAssociation,
    IntegratedAnalogyReasoner,
    AnalogyRetriever,
    ThinkingFrameworkMatcher,
    CreativeAssociationGenerator,
    SimilarityType,
    FrameworkType,
    AssociationType
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