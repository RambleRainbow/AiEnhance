"""
情境分析模块
"""

from .context_analysis_module import ContextAnalysisModule

# 为了向后兼容，提供一些基础类的占位符
class AbstractionLevel:
    pass

class CognitiveNeeds:
    pass

class ContextProfile:
    pass

class ContextualElements:
    pass

class IntegratedContextAnalyzer:
    pass

class PurposeType:
    pass

class TaskCharacteristics:
    pass

class TaskType:
    pass

class TimeDimension:
    pass

__all__ = [
    'ContextAnalysisModule',
    'AbstractionLevel',
    'CognitiveNeeds', 
    'ContextProfile',
    'ContextualElements',
    'IntegratedContextAnalyzer',
    'PurposeType',
    'TaskCharacteristics',
    'TaskType',
    'TimeDimension'
]