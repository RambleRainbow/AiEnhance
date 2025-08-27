"""
AiEnhance - 记忆-认知协同系统
开发AI增强的认知-AI记忆系统设计,基于认知多层次:感知层,认知层,行为层
"""

__version__ = "0.1.0"

from .core import (
    BehaviorLayer,
    CognitionLayer,
    CollaborationLayer,
    ContextProfile,
    IBehaviorLayer,
    ICognitionLayer,
    ICognitiveLayers,
    ICollaborationLayer,
    InformationFlow,
    IPerceptionLayer,
    # 分层架构 (推荐)
    LayeredCognitiveSystem,
    LayeredSystemFactory,
    PerceptionLayer,
    ProcessingStatus,
    UserProfile,
)
from .enhanced_system_factory import (
    create_creative_layered_system,
    create_educational_layered_system,
    # 分层架构工厂函数 (推荐)
    create_layered_system,
    create_lightweight_layered_system,
    create_research_layered_system,
    get_layered_system_info,
    get_system_info,
)
from .llm import (
    EmbeddingProviderFactory,
    LLMProviderFactory,
    MessageRole,
    ModelConfig,
    create_chat_message,
    create_model_config,
)
from .memory import (
    MemorySystemConfig,
    MemorySystemFactory,
    MemoryType,
    create_memory_entry,
    create_user_context,
)

# 便捷接口
__all__ = [
    # 分层架构 (核心)
    "LayeredCognitiveSystem",
    "LayeredSystemFactory",
    "PerceptionLayer",
    "CognitionLayer",
    "BehaviorLayer",
    "CollaborationLayer",
    "IPerceptionLayer",
    "ICognitionLayer",
    "IBehaviorLayer",
    "ICollaborationLayer",
    "ICognitiveLayers",
    "UserProfile",
    "ContextProfile",
    "InformationFlow",
    "ProcessingStatus",
    # 记忆系统
    "MemorySystemFactory",
    "MemorySystemConfig",
    "MemoryType",
    "create_user_context",
    "create_memory_entry",
    # LLM系统
    "LLMProviderFactory",
    "EmbeddingProviderFactory",
    "ModelConfig",
    "MessageRole",
    "create_model_config",
    "create_chat_message",
    # 分层系统工厂函数
    "create_layered_system",
    "create_educational_layered_system",
    "create_research_layered_system",
    "create_creative_layered_system",
    "create_lightweight_layered_system",
    "get_layered_system_info",
    "get_system_info",
    # 便捷函数
    "create_memory_system",
    "__version__",
]


# 便捷工厂函数 - 现在推荐使用 create_layered_system
def create_memory_system(system_type: str, **kwargs):
    """
    便捷创建记忆系统

    Args:
        system_type: 记忆系统类型 ('graphiti', 'mem0')
        **kwargs: 配置参数

    Returns:
        MemorySystem: 记忆系统实例
    """
    config = MemorySystemConfig(system_type=system_type, **kwargs)
    return MemorySystemFactory.create_memory_system(config)
