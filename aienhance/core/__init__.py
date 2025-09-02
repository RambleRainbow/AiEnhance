"""
认知系统核心模块
提供记忆-认知协同系统的核心功能

基于层-模块-子模块三层架构设计
"""

# 新架构 - 层-模块-子模块架构
from .base_architecture import (
    BaseLayer,
    BaseModule, 
    BaseSubModule,
    CognitiveSystem,
    ProcessingContext,
    ProcessingResult,
    ProcessingPhase
)
from .restructured_system_factory import (
    create_restructured_cognitive_system,
    create_educational_system,
    create_research_system,
    create_creative_system,
    create_lightweight_system,
    create_system_from_config,
    initialize_system_async
)

# 向后兼容接口已移除，使用新架构

__all__ = [
    # 层-模块-子模块架构
    "BaseLayer",
    "BaseModule", 
    "BaseSubModule",
    "CognitiveSystem",
    "ProcessingContext",
    "ProcessingResult",
    "ProcessingPhase",
    "create_restructured_cognitive_system",
    "create_educational_system",
    "create_research_system",
    "create_creative_system",
    "create_lightweight_system",
    "create_system_from_config",
    "initialize_system_async",
]
