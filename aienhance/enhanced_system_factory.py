"""
分层认知系统工厂
现代化的分层架构系统创建和管理
"""

import logging
from typing import Any

from .core.layered_cognitive_system import LayeredCognitiveSystem
from .core.layered_system_factory import LayeredSystemFactory
from .llm.interfaces import ModelConfig
from .memory.interfaces import MemorySystemConfig

logger = logging.getLogger(__name__)


# ===== 分层认知系统工厂函数 (推荐使用) =====


def create_layered_system(
    system_type: str = "educational",
    memory_system_type: str = "graphiti",
    llm_provider: str = "ollama",
    llm_model_name: str = "qwen3:8b",
    llm_api_key: str | None = None,
    llm_api_base: str | None = None,
    llm_temperature: float = 0.7,
    llm_max_tokens: int | None = None,
    embedding_provider: str | None = None,
    embedding_model_name: str | None = None,
    use_unified_llm: bool = True,
    **kwargs,
) -> LayeredCognitiveSystem:
    """
    创建分层认知系统（推荐使用）

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
        **kwargs,
    )


def create_educational_layered_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "educational",
    **kwargs,
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
        memory_config=MemorySystemConfig(system_type="graphiti"),
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get("llm_temperature", 0.7),
            max_tokens=kwargs.get("llm_max_tokens", 800),
        ),
    )


def create_research_layered_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "research",
    **kwargs,
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
        memory_config=MemorySystemConfig(system_type="graphiti"),
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get("llm_temperature", 0.8),
            max_tokens=kwargs.get("llm_max_tokens", 1200),
        ),
    )


def create_creative_layered_system(
    model_name: str = "qwen3:8b",
    ollama_base: str = "http://localhost:11434",
    system_type: str = "creative",
    **kwargs,
) -> LayeredCognitiveSystem:
    """
    创建创意场景的分层认知系统

    Args:
        model_name: 模型名称
        ollama_base: Ollama服务地址
        system_type: 系统类型
        **kwargs: 其他参数

    Returns:
        LayeredCognitiveSystem: 创意特化的分层认知系统
    """

    return LayeredSystemFactory.create_creative_layered_system(
        memory_config=MemorySystemConfig(system_type="graphiti"),
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get("llm_temperature", 0.9),
            max_tokens=kwargs.get("llm_max_tokens", 1000),
        ),
    )


def create_lightweight_layered_system(
    model_name: str = "qwen3:8b", ollama_base: str = "http://localhost:11434", **kwargs
) -> LayeredCognitiveSystem:
    """
    创建轻量级分层认知系统

    Args:
        model_name: 模型名称
        ollama_base: Ollama服务地址
        **kwargs: 其他参数

    Returns:
        LayeredCognitiveSystem: 轻量级分层认知系统
    """

    return LayeredSystemFactory.create_lightweight_layered_system(
        llm_config=ModelConfig(
            provider="ollama",
            model_name=model_name,
            api_base=ollama_base,
            temperature=kwargs.get("llm_temperature", 0.7),
            max_tokens=kwargs.get("llm_max_tokens", 600),
        )
    )


def get_layered_system_info() -> dict[str, Any]:
    """
    获取分层系统信息

    Returns:
        Dict: 分层系统信息
    """
    return {
        "available_system_types": LayeredSystemFactory.get_available_system_types(),
        "system_descriptions": {
            system_type: LayeredSystemFactory.get_system_type_info(system_type)
            for system_type in LayeredSystemFactory.get_available_system_types()
        },
        "version": "2.0.0",
        "architecture": "Layered Cognitive System",
        "layers": ["perception", "cognition", "behavior", "collaboration"],
    }


def get_system_info() -> dict[str, Any]:
    """
    获取系统信息

    Returns:
        Dict: 系统信息
    """

    return {
        "enhanced_factory_version": "2.0.0",  # 升级到2.0，专注分层架构
        "architecture": {
            "layered_architecture": True,
            "recommended_architecture": "layered",
        },
        "supported_memory_systems": ["graphiti", "mem0"],
        "supported_llm_providers": ["ollama", "openai", "anthropic", "azure"],
        "available_system_types": LayeredSystemFactory.get_available_system_types(),
        "features": {
            "unified_llm_integration": True,
            "flexible_configuration": True,
            "layered_architecture": True,
            "explicit_layer_objects": True,
            "information_flow_tracking": True,
            "streaming_output": True,
        },
    }


def get_layered_system_info_detailed(system_type: str = None) -> dict[str, Any]:
    """
    获取详细的分层系统信息

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
                    "collaboration": "协作层：多元观点、认知挑战、辩证思考",
                },
                "information_flow": "感知层 → 认知层 → 行为层 → 协作层",
                "key_features": [
                    "显式层级对象",
                    "明确的信息流",
                    "独立的层级配置",
                    "模块化设计",
                    "可扩展架构",
                    "流式输出支持",
                ],
            },
        }
