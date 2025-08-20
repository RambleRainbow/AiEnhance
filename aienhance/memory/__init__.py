"""
记忆系统抽象接口模块
提供统一的记忆系统接口，支持MIRIX、Mem0、Graphiti等不同实现
"""

from .interfaces import (
    MemorySystem,
    MemoryEntry,
    MemoryQuery,
    MemoryResult,
    UserContext,
    MemoryType,
    MemorySystemConfig,
    MemorySystemFactory,
    create_user_context,
    create_memory_entry
)

from .adapters import (
    MirixUnifiedAdapter,
    MirixLLMBridge,
    Mem0Adapter, 
    GraphitiAdapter
)

__all__ = [
    # Core Interfaces
    'MemorySystem',
    'MemoryEntry',
    'MemoryQuery',
    'MemoryResult',
    'UserContext',
    'MemoryType',
    'MemorySystemConfig',
    'MemorySystemFactory',
    'create_user_context',
    'create_memory_entry',
    
    # Adapters
    'MirixUnifiedAdapter',
    'MirixLLMBridge',
    'Mem0Adapter',
    'GraphitiAdapter'
]