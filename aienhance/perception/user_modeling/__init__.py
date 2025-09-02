"""
用户建模模块

包含三个子模块：
- 认知能力维度建模子模块
- 知识结构维度建模子模块
- 交互模式维度建模子模块
"""

from .cognitive_ability_modeling import CognitiveAbilityModelingSubModule
from .knowledge_structure_modeling import KnowledgeStructureModelingSubModule
from .interaction_pattern_modeling import InteractionPatternModelingSubModule
from .user_modeling_module import UserModelingModule

# 为了向后兼容，提供一些基础类的占位符
class CognitiveProfile:
    pass

class CognitiveStyle:
    pass

class DynamicUserModeler:
    pass

class InteractionProfile:
    pass

class KnowledgeProfile:
    pass

class ThinkingMode:
    pass

class UserProfile:
    pass

__all__ = [
    # 新架构
    'CognitiveAbilityModelingSubModule',
    'KnowledgeStructureModelingSubModule', 
    'InteractionPatternModelingSubModule',
    'UserModelingModule',
    # 向后兼容
    'CognitiveProfile',
    'CognitiveStyle',
    'DynamicUserModeler',
    'InteractionProfile',
    'KnowledgeProfile',
    'ThinkingMode',
    'UserProfile'
]