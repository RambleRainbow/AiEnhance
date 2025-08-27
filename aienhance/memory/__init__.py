"""
记忆系统抽象接口模块
提供统一的记忆系统接口，支持Graphiti、Mem0等不同实现
"""

from .adapters import GraphitiHttpAdapter, GraphitiNativeAdapter, Mem0Adapter
from .interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemoryResult,
    MemorySystem,
    MemorySystemConfig,
    MemorySystemFactory,
    MemoryType,
    UserContext,
    create_memory_entry,
    create_user_context,
)

__all__ = [
    # Core Interfaces
    "MemorySystem",
    "MemoryEntry",
    "MemoryQuery",
    "MemoryResult",
    "UserContext",
    "MemoryType",
    "MemorySystemConfig",
    "MemorySystemFactory",
    "create_user_context",
    "create_memory_entry",
    # Adapters
    "Mem0Adapter",
    "GraphitiHttpAdapter",
    "GraphitiNativeAdapter",
]
