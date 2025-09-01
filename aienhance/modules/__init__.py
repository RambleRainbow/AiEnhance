"""
业务模块概念实现
包含各种LLM驱动的业务模块，如领域推断、情境分析、用户建模等
"""

from .adaptive_output import AdaptiveOutputManager, ContentOptimizationManager
from .collaborative_reasoning import (
    ChallengeGenerationManager,
    MultiPerspectiveManager,
)
from .context_analysis import ContextAnalysisManager
from .domain_inference import DomainInferenceManager
from .memory_activation import MemoryActivationManager, SemanticEnhancementManager
from .user_modeling import CognitiveAnalysisManager, LearningStyleManager

__all__ = [
    # 感知层模块
    "DomainInferenceManager",
    "ContextAnalysisManager",
    "CognitiveAnalysisManager",
    "LearningStyleManager",
    
    # 认知层模块
    "MemoryActivationManager", 
    "SemanticEnhancementManager",
    
    # 行为层模块
    "AdaptiveOutputManager",
    "ContentOptimizationManager",
    
    # 协作层模块
    "MultiPerspectiveManager",
    "ChallengeGenerationManager",
]