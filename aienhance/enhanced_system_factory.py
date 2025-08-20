"""
增强的系统工厂
支持LLM注入的MIRIX集成，实现真正的统一大模型管理
"""

from typing import Optional, Dict, Any
import logging

from .core.memory_cognitive_system import MemoryCognitiveSystem
from .core.layered_cognitive_system import LayeredCognitiveSystem
from .core.layered_system_factory import LayeredSystemFactory
from .memory.interfaces import MemorySystemConfig
from .memory.adapters.mirix_unified_adapter import MirixUnifiedAdapter
from .llm.interfaces import LLMProvider, LLMProviderFactory, ModelConfig

logger = logging.getLogger(__name__)


def create_enhanced_system(
    system_type: str = "educational",
    memory_system_type: str = "mirix_unified",
    llm_provider: str = "ollama",
    llm_model_name: str = "qwen3:8b",
    llm_api_key: Optional[str] = None,
    llm_api_base: Optional[str] = None,
    llm_temperature: float = 0.7,
    llm_max_tokens: Optional[int] = None,
    embedding_provider: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    mirix_api_key: Optional[str] = None,
    use_unified_llm: bool = True,
    **kwargs
) -> MemoryCognitiveSystem:
    """
    创建增强的记忆-认知协同系统
    
    支持两种MIRIX集成模式：
    1. 统一模式 (推荐): MIRIX使用项目的LLM抽象层
    2. 独立模式: MIRIX使用自己的大模型配置
    
    Args:
        system_type: 系统类型
        memory_system_type: 记忆系统类型，推荐使用"mirix_unified"
        llm_provider: LLM提供商
        llm_model_name: LLM模型名称
        llm_api_key: LLM API密钥
        llm_api_base: LLM API基础URL
        llm_temperature: 温度参数
        llm_max_tokens: 最大token数
        embedding_provider: 嵌入模型提供商
        embedding_model_name: 嵌入模型名称
        mirix_api_key: MIRIX API密钥（独立模式需要）
        use_unified_llm: 是否使用统一LLM模式
        **kwargs: 其他参数
        
    Returns:
        MemoryCognitiveSystem: 系统实例
    """
    
    logger.info(f"创建增强系统: {system_type}, 记忆系统: {memory_system_type}")
    
    # 创建LLM提供商
    llm_config = ModelConfig(
        provider=llm_provider,
        model_name=llm_model_name,
        api_key=llm_api_key,
        api_base=llm_api_base,
        temperature=llm_temperature,
        max_tokens=llm_max_tokens
    )
    
    llm_provider_instance = LLMProviderFactory.create_provider(llm_config)
    
    # 创建嵌入提供商（如果指定）
    embedding_provider_instance = None
    if embedding_provider and embedding_model_name:
        embedding_config = ModelConfig(
            provider=embedding_provider,
            model_name=embedding_model_name,
            api_key=llm_api_key,  # 通常使用相同的API密钥
            api_base=llm_api_base
        )
        
        from .llm.interfaces import EmbeddingProviderFactory
        embedding_provider_instance = EmbeddingProviderFactory.create_provider(embedding_config)
    
    # 配置记忆系统
    if memory_system_type == "mirix_unified":
        if use_unified_llm:
            # 统一模式：使用项目的LLM抽象
            memory_config = MemorySystemConfig(
                system_type=memory_system_type,
                api_key=mirix_api_key  # 可能为None，统一模式优先使用LLM配置
            )
            
            # 创建带LLM注入的记忆系统
            memory_system = MirixUnifiedAdapter(memory_config, llm_provider_instance)
            
            logger.info(f"使用统一LLM模式: {llm_provider}/{llm_model_name}")
        else:
            # 独立模式：MIRIX使用自己的配置
            if not mirix_api_key:
                raise ValueError("独立模式需要MIRIX API密钥")
                
            memory_config = MemorySystemConfig(
                system_type=memory_system_type,
                api_key=mirix_api_key
            )
            
            memory_system = MirixUnifiedAdapter(memory_config)
            logger.info("使用MIRIX独立模式")
    else:
        # 其他记忆系统类型
        memory_config = MemorySystemConfig(
            system_type=memory_system_type,
            api_key=mirix_api_key
        )
        
        from .memory.interfaces import MemorySystemFactory
        memory_system = MemorySystemFactory.create_system(memory_config)
    
    # 创建系统实例
    system = MemoryCognitiveSystem(
        system_type=system_type,
        memory_system=memory_system,
        llm_provider=llm_provider_instance,
        embedding_provider=embedding_provider_instance,
        **kwargs
    )
    
    return system


def create_mirix_unified_system(
    llm_provider: str = "ollama",
    llm_model_name: str = "qwen3:8b",
    llm_api_key: Optional[str] = None,
    llm_api_base: Optional[str] = "http://localhost:11434",
    system_type: str = "educational",
    **kwargs
) -> MemoryCognitiveSystem:
    """
    创建MIRIX统一系统的便捷函数
    
    自动配置为使用统一LLM模式，无需额外的MIRIX API密钥
    
    Args:
        llm_provider: LLM提供商
        llm_model_name: LLM模型名称
        llm_api_key: LLM API密钥
        llm_api_base: LLM API基础URL
        system_type: 系统类型
        **kwargs: 其他参数
        
    Returns:
        MemoryCognitiveSystem: 配置好的系统实例
    """
    
    return create_enhanced_system(
        system_type=system_type,
        memory_system_type="mirix_unified",
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        llm_api_key=llm_api_key,
        llm_api_base=llm_api_base,
        use_unified_llm=True,
        **kwargs
    )


def create_ollama_mirix_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "educational",
    **kwargs
) -> MemoryCognitiveSystem:
    """
    创建Ollama + MIRIX统一系统的便捷函数
    
    Args:
        model_name: Ollama模型名称
        ollama_base: Ollama服务地址
        system_type: 系统类型
        **kwargs: 其他参数
        
    Returns:
        MemoryCognitiveSystem: 配置好的系统实例
    """
    
    return create_mirix_unified_system(
        llm_provider="ollama",
        llm_model_name=model_name,
        llm_api_base=ollama_base,
        system_type=system_type,
        **kwargs
    )


def create_openai_mirix_system(
    model_name: str = "gpt-4",
    api_key: str = None,
    system_type: str = "educational",
    **kwargs
) -> MemoryCognitiveSystem:
    """
    创建OpenAI + MIRIX统一系统的便捷函数
    
    Args:
        model_name: OpenAI模型名称
        api_key: OpenAI API密钥
        system_type: 系统类型
        **kwargs: 其他参数
        
    Returns:
        MemoryCognitiveSystem: 配置好的系统实例
    """
    
    return create_mirix_unified_system(
        llm_provider="openai",
        llm_model_name=model_name,
        llm_api_key=api_key,
        system_type=system_type,
        **kwargs
    )


# 系统配置预设
SYSTEM_PRESETS = {
    "ollama_qwen": {
        "llm_provider": "ollama",
        "llm_model_name": "qwen3:8b",
        "llm_api_base": "http://localhost:11434"
    },
    "ollama_llama": {
        "llm_provider": "ollama", 
        "llm_model_name": "llama3.3:8b",
        "llm_api_base": "http://localhost:11434"
    },
    "openai_gpt4": {
        "llm_provider": "openai",
        "llm_model_name": "gpt-4",
        "llm_api_base": "https://api.openai.com/v1"
    },
    "anthropic_claude": {
        "llm_provider": "anthropic",
        "llm_model_name": "claude-3-sonnet-20240229"
    }
}


def create_preset_system(preset_name: str, api_key: Optional[str] = None, **kwargs) -> MemoryCognitiveSystem:
    """
    使用预设配置创建系统
    
    Args:
        preset_name: 预设名称
        api_key: API密钥
        **kwargs: 其他参数
        
    Returns:
        MemoryCognitiveSystem: 系统实例
    """
    
    if preset_name not in SYSTEM_PRESETS:
        raise ValueError(f"未知的预设: {preset_name}, 可用预设: {list(SYSTEM_PRESETS.keys())}")
    
    preset_config = SYSTEM_PRESETS[preset_name].copy()
    preset_config.update(kwargs)
    
    if api_key:
        preset_config["llm_api_key"] = api_key
    
    return create_mirix_unified_system(**preset_config)


# ===== 新的分层架构支持 =====

def create_layered_system(
    system_type: str = "educational",
    memory_system_type: str = "mirix_unified",
    llm_provider: str = "ollama",
    llm_model_name: str = "qwen3:8b",
    llm_api_key: Optional[str] = None,
    llm_api_base: Optional[str] = None,
    llm_temperature: float = 0.7,
    llm_max_tokens: Optional[int] = None,
    embedding_provider: Optional[str] = None,
    embedding_model_name: Optional[str] = None,
    use_unified_llm: bool = True,
    **kwargs
) -> LayeredCognitiveSystem:
    """
    创建新的分层认知系统（推荐使用）
    
    这是新的分层架构，将感知、认知、行为、协作四层显式化为独立对象。
    相比旧架构，提供更好的模块化、可维护性和扩展性。
    
    Args:
        system_type: 系统类型 ('educational', 'research', 'creative', 'lightweight')
        memory_system_type: 记忆系统类型
        llm_provider: LLM提供商
        llm_model_name: LLM模型名称
        llm_api_key: LLM API密钥
        llm_api_base: LLM API基础URL
        llm_temperature: 温度参数
        llm_max_tokens: 最大token数
        embedding_provider: 嵌入模型提供商
        embedding_model_name: 嵌入模型名称
        use_unified_llm: 是否使用统一LLM
        **kwargs: 其他参数
        
    Returns:
        LayeredCognitiveSystem: 分层认知系统实例
    """
    
    return LayeredSystemFactory.create_from_enhanced_factory_config(
        system_type=system_type,
        memory_system_type=memory_system_type,
        llm_provider=llm_provider,
        llm_model_name=llm_model_name,
        llm_api_key=llm_api_key,
        llm_api_base=llm_api_base,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        embedding_provider=embedding_provider,
        embedding_model_name=embedding_model_name,
        use_unified_llm=use_unified_llm,
        **kwargs
    )


def create_educational_layered_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "educational",
    **kwargs
) -> LayeredCognitiveSystem:
    """
    创建教育场景的分层认知系统
    
    Args:
        model_name: 模型名称
        ollama_base: Ollama服务地址
        system_type: 系统类型
        **kwargs: 其他参数
        
    Returns:
        LayeredCognitiveSystem: 教育特化的分层认知系统
    """
    
    return LayeredSystemFactory.create_educational_layered_system(
        memory_config=MemorySystemConfig(system_type="mirix_unified"),
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get('llm_temperature', 0.7),
            max_tokens=kwargs.get('llm_max_tokens', 800)
        )
    )


def create_research_layered_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "research",
    **kwargs
) -> LayeredCognitiveSystem:
    """
    创建研究场景的分层认知系统
    
    Args:
        model_name: 模型名称
        ollama_base: Ollama服务地址
        system_type: 系统类型
        **kwargs: 其他参数
        
    Returns:
        LayeredCognitiveSystem: 研究特化的分层认知系统
    """
    
    return LayeredSystemFactory.create_research_layered_system(
        memory_config=MemorySystemConfig(system_type="mirix_unified"),
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get('llm_temperature', 0.8),
            max_tokens=kwargs.get('llm_max_tokens', 1200)
        )
    )


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        Dict: 系统信息
    """
    
    return {
        "enhanced_factory_version": "2.0.0",  # 升级到2.0以支持分层架构
        "architecture": {
            "layered_architecture_available": True,
            "legacy_architecture_available": True,
            "recommended_architecture": "layered"
        },
        "supported_memory_systems": ["mirix_unified", "mirix_sdk", "mem0", "graphiti"],
        "supported_llm_providers": ["ollama", "openai", "anthropic", "azure"],
        "available_presets": list(SYSTEM_PRESETS.keys()),
        "available_system_types": LayeredSystemFactory.get_available_system_types(),
        "features": {
            "unified_llm_integration": True,
            "non_invasive_mirix": True,
            "flexible_configuration": True,
            "preset_configurations": True,
            "layered_architecture": True,
            "explicit_layer_objects": True,
            "information_flow_tracking": True
        }
    }


def get_layered_system_info(system_type: str = None) -> Dict[str, Any]:
    """
    获取分层系统信息
    
    Args:
        system_type: 系统类型，如果提供则返回特定类型的信息
        
    Returns:
        Dict: 分层系统信息
    """
    
    if system_type:
        return LayeredSystemFactory.get_system_type_info(system_type)
    else:
        return {
            "available_types": LayeredSystemFactory.get_available_system_types(),
            "type_details": {
                system_type: LayeredSystemFactory.get_system_type_info(system_type)
                for system_type in LayeredSystemFactory.get_available_system_types()
            },
            "architecture_overview": {
                "layers": ["perception", "cognition", "behavior", "collaboration"],
                "layer_descriptions": {
                    "perception": "感知层：用户建模、情境分析、输入理解",
                    "cognition": "认知层：记忆激活、语义增强、类比推理",
                    "behavior": "行为层：内容适配、个性化输出、LLM生成",
                    "collaboration": "协作层：多元观点、认知挑战、辩证思考"
                },
                "information_flow": "感知层 → 认知层 → 行为层 → 协作层",
                "key_features": [
                    "显式层级对象",
                    "明确的信息流",
                    "独立的层级配置",
                    "模块化设计",
                    "可扩展架构"
                ]
            }
        }