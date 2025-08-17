"""
AiEnhance - 记忆-认知协同系统
开发AI增强的认知-AI记忆系统设计,基于认知多层次:感知层,认知层,行为层
"""

__version__ = "0.1.0"

from .core import (
    MemoryCognitiveSystem,
    SystemFactory,
    SystemResponse
)

# 便捷接口
__all__ = [
    'MemoryCognitiveSystem',
    'SystemFactory',
    'SystemResponse',
    '__version__'
]

# 便捷工厂函数
def create_system(system_type: str = "default"):
    """
    便捷创建系统
    
    Args:
        system_type: 系统类型 ('default', 'educational', 'research')
    
    Returns:
        MemoryCognitiveSystem: 系统实例
    """
    if system_type == "educational":
        return SystemFactory.create_educational_system()
    elif system_type == "research":
        return SystemFactory.create_research_system()
    else:
        return SystemFactory.create_default_system()