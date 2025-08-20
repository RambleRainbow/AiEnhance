"""
AiEnhance - 记忆-认知协同系统
开发AI增强的认知-AI记忆系统设计,基于认知多层次:感知层,认知层,行为层
"""

__version__ = "0.1.0"

from .core import (
    MemoryCognitiveSystem,
    SystemFactory,
    SystemResponse,
    # 新的分层架构
    LayeredCognitiveSystem,
    LayeredSystemFactory,
    PerceptionLayer,
    CognitionLayer,
    BehaviorLayer,
    CollaborationLayer,
    IPerceptionLayer,
    ICognitionLayer,
    IBehaviorLayer,
    ICollaborationLayer,
    ICognitiveLayers,
    UserProfile,
    ContextProfile,
    InformationFlow,
    ProcessingStatus
)
from .enhanced_system_factory import (
    create_enhanced_system,
    create_mirix_unified_system,
    create_ollama_mirix_system,
    create_openai_mirix_system,
    create_preset_system,
    get_system_info,
    # 新的分层架构工厂函数
    create_layered_system,
    create_educational_layered_system,
    create_research_layered_system,
    create_creative_layered_system,
    create_lightweight_layered_system,
    get_layered_system_info
)
from .memory import (
    MemorySystemFactory,
    MemorySystemConfig,
    MemoryType,
    create_user_context,
    create_memory_entry
)
from .llm import (
    LLMProviderFactory,
    EmbeddingProviderFactory,
    ModelConfig,
    MessageRole,
    create_model_config,
    create_chat_message
)

# 便捷接口
__all__ = [
    # 传统架构
    'MemoryCognitiveSystem',
    'SystemFactory',
    'SystemResponse',
    
    # 新的分层架构
    'LayeredCognitiveSystem',
    'LayeredSystemFactory',
    'PerceptionLayer',
    'CognitionLayer',
    'BehaviorLayer',
    'CollaborationLayer',
    'IPerceptionLayer',
    'ICognitionLayer',
    'IBehaviorLayer',
    'ICollaborationLayer',
    'ICognitiveLayers',
    'UserProfile',
    'ContextProfile',
    'InformationFlow',
    'ProcessingStatus',
    
    # 记忆系统
    'MemorySystemFactory',
    'MemorySystemConfig',
    'MemoryType',
    'create_user_context',
    'create_memory_entry',
    
    # LLM系统
    'LLMProviderFactory',
    'EmbeddingProviderFactory',
    'ModelConfig',
    'MessageRole',
    'create_model_config',
    'create_chat_message',
    
    # 工厂函数
    'create_enhanced_system',
    'create_mirix_unified_system',
    'create_ollama_mirix_system',
    'create_openai_mirix_system',
    'create_preset_system',
    'create_layered_system',
    'create_educational_layered_system',
    'create_research_layered_system',
    'create_creative_layered_system',
    'create_lightweight_layered_system',
    'get_system_info',
    'get_layered_system_info',
    
    # 便捷函数
    'create_system',
    'create_memory_system',
    '__version__'
]

# 便捷工厂函数
def create_system(system_type: str = "default", 
                 memory_system_type: str = None, 
                 llm_provider: str = None,
                 embedding_provider: str = None,
                 **kwargs):
    """
    便捷创建系统
    
    Args:
        system_type: 系统类型 ('default', 'educational', 'research')
        memory_system_type: 记忆系统类型 ('mirix', 'mem0', 'graphiti')
        llm_provider: LLM提供商 ('ollama', 'openai', 'anthropic')
        embedding_provider: 嵌入提供商 ('ollama', 'openai')
        **kwargs: 其他配置参数
    
    Returns:
        MemoryCognitiveSystem: 系统实例
    """
    # 分离不同类型的配置参数
    memory_kwargs = {}
    llm_kwargs = {}
    embedding_kwargs = {}
    
    # 根据参数前缀分离配置
    for key, value in kwargs.items():
        if key.startswith('memory_'):
            memory_kwargs[key[7:]] = value  # 去掉 'memory_' 前缀
        elif key.startswith('llm_'):
            llm_kwargs[key[4:]] = value  # 去掉 'llm_' 前缀
        elif key.startswith('embedding_'):
            embedding_kwargs[key[10:]] = value  # 去掉 'embedding_' 前缀
        else:
            # 常用参数自动分配
            if key in ['api_key', 'api_base', 'model_name', 'temperature', 'max_tokens']:
                llm_kwargs[key] = value
    
    # 创建记忆系统配置
    memory_config = None
    if memory_system_type:
        memory_config = MemorySystemConfig(
            system_type=memory_system_type,
            **memory_kwargs
        )
    
    # 创建LLM配置
    llm_config = None
    if llm_provider:
        llm_config = ModelConfig(
            provider=llm_provider,
            **llm_kwargs
        )
    
    # 创建嵌入模型配置
    embedding_config = None
    if embedding_provider:
        embedding_config = ModelConfig(
            provider=embedding_provider,
            **embedding_kwargs
        )
    
    # 创建认知系统
    if system_type == "educational":
        return SystemFactory.create_educational_system(memory_config, llm_config, embedding_config)
    elif system_type == "research":
        return SystemFactory.create_research_system(memory_config, llm_config, embedding_config)
    else:
        return SystemFactory.create_default_system(memory_config, llm_config, embedding_config)


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