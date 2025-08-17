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
from .memory import (
    MemorySystemFactory,
    MemorySystemConfig,
    MemoryType,
    create_user_context,
    create_memory_entry
)

# 便捷接口
__all__ = [
    'MemoryCognitiveSystem',
    'SystemFactory',
    'SystemResponse',
    'MemorySystemFactory',
    'MemorySystemConfig',
    'MemoryType',
    'create_user_context',
    'create_memory_entry',
    '__version__'
]

# 便捷工厂函数
def create_system(system_type: str = "default", memory_system_type: str = None, **memory_kwargs):
    """
    便捷创建系统
    
    Args:
        system_type: 系统类型 ('default', 'educational', 'research')
        memory_system_type: 记忆系统类型 ('mirix', 'mem0', 'graphiti')
        **memory_kwargs: 记忆系统配置参数
    
    Returns:
        MemoryCognitiveSystem: 系统实例
    """
    # 创建记忆系统配置
    memory_config = None
    if memory_system_type:
        memory_config = MemorySystemConfig(
            system_type=memory_system_type,
            **memory_kwargs
        )
    
    # 创建认知系统
    if system_type == "educational":
        return SystemFactory.create_educational_system(memory_config)
    elif system_type == "research":
        return SystemFactory.create_research_system(memory_config)
    else:
        return SystemFactory.create_default_system(memory_config)


def create_memory_system(system_type: str, **kwargs):
    """
    便捷创建记忆系统
    
    Args:
        system_type: 记忆系统类型 ('mirix', 'mem0', 'graphiti')
        **kwargs: 配置参数
    
    Returns:
        MemorySystem: 记忆系统实例
    """
    config = MemorySystemConfig(system_type=system_type, **kwargs)
    return MemorySystemFactory.create_memory_system(config)