"""
重构后的系统工厂

基于设计文档的层-模块-子模块三层式结构创建认知系统，
替代原有的系统工厂，提供更符合设计规范的系统构建方式。
"""

from typing import Dict, Any, Optional
import logging
from aienhance.core.base_architecture import CognitiveSystem
from aienhance.perception.perception_layer import PerceptionLayer
from aienhance.cognition.cognition_layer import CognitionLayer
from aienhance.behavior.behavior_layer import BehaviorLayer
from aienhance.collaboration.collaboration_layer import CollaborationLayer

# 引入适配器
from aienhance.llm.adapters.ollama_adapter import OllamaLLMAdapter
from aienhance.llm.adapters.openai_adapter import OpenAILLMAdapter
from aienhance.llm.adapters.anthropic_adapter import AnthropicLLMAdapter
from aienhance.llm.interfaces import ModelConfig
from aienhance.memory.adapters.graphiti_http_adapter import GraphitiHttpAdapter
from aienhance.memory.adapters.mem0_adapter import Mem0Adapter
from aienhance.memory.interfaces import MemorySystemConfig

logger = logging.getLogger(__name__)


def create_restructured_cognitive_system(
    system_type: str = "educational",
    llm_provider: str = "ollama",
    llm_model_name: str = "qwen3:8b",
    memory_provider: str = "graphiti",
    enable_collaboration_layer: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> CognitiveSystem:
    """
    创建重构后的认知系统
    
    Args:
        system_type: 系统类型 (educational, research, creative, lightweight)
        llm_provider: LLM提供商 (ollama, openai, anthropic)
        llm_model_name: LLM模型名称
        memory_provider: 记忆系统提供商 (graphiti, mem0, none)
        enable_collaboration_layer: 是否启用协作层
        config: 额外配置
        
    Returns:
        CognitiveSystem: 配置完成的认知系统实例
    """
    
    if config is None:
        config = {}
    
    # 根据系统类型调整配置
    system_config = _get_system_type_config(system_type)
    config.update(system_config)
    
    try:
        # 创建LLM适配器
        llm_adapter = _create_llm_adapter(llm_provider, llm_model_name, config)
        logger.info(f"Created LLM adapter: {llm_provider} with model {llm_model_name}")
        
        # 创建记忆适配器
        memory_adapter = _create_memory_adapter(memory_provider, config) if memory_provider != "none" else None
        if memory_adapter:
            logger.info(f"Created memory adapter: {memory_provider}")
        
        # 创建四个认知层
        layers = []
        
        # 1. 感知层（必需）
        perception_layer = PerceptionLayer(llm_adapter, memory_adapter, config)
        layers.append(perception_layer)
        
        # 2. 认知层（必需）
        cognition_layer = CognitionLayer(llm_adapter, memory_adapter, config)
        layers.append(cognition_layer)
        
        # 3. 行为层（必需）
        behavior_layer = BehaviorLayer(llm_adapter, memory_adapter, config)
        layers.append(behavior_layer)
        
        # 4. 协作层（可选）
        if enable_collaboration_layer:
            collaboration_layer = CollaborationLayer(llm_adapter, memory_adapter, config)
            layers.append(collaboration_layer)
        
        # 创建认知系统
        system = CognitiveSystem(layers, config)
        
        # 存储适配器引用供后续初始化
        system._llm_adapter = llm_adapter
        system._memory_adapter = memory_adapter
        
        logger.info(f"Successfully created restructured cognitive system with {len(layers)} layers")
        return system
        
    except Exception as e:
        logger.error(f"Failed to create restructured cognitive system: {e}")
        raise


def _get_system_type_config(system_type: str) -> Dict[str, Any]:
    """根据系统类型获取配置"""
    
    configs = {
        "educational": {
            "temperature": 0.7,
            "max_tokens": None,  # 无长度限制，避免截断
            "enable_metacognitive_guidance": True,
            "cognitive_challenge_level": "moderate",
            "explanation_detail_level": "detailed"
        },
        "research": {
            "temperature": 0.6,
            "max_tokens": None,  # 无长度限制，避免截断
            "enable_dialectical_perspectives": True,
            "analogy_depth": "deep",
            "evidence_requirement": "strict"
        },
        "creative": {
            "temperature": 0.9,
            "max_tokens": None,  # 无长度限制，避免截断
            "enable_creative_associations": True,
            "thinking_diversity": "high",
            "exploration_tendency": "strong"
        },
        "lightweight": {
            "temperature": 0.5,
            "max_tokens": None,  # 无长度限制，避免截断
            "enable_collaboration_layer": False,
            "simplified_processing": True,
            "response_conciseness": "high"
        }
    }
    
    return configs.get(system_type, configs["educational"])


def _create_llm_adapter(provider: str, model_name: str, config: Dict[str, Any]):
    """创建LLM适配器"""
    
    if provider == "ollama":
        model_config = ModelConfig(
            provider=provider,
            model_name=model_name,
            api_base=config.get("ollama_base_url", "http://localhost:11434"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", None)
        )
        return OllamaLLMAdapter(model_config)
    elif provider == "openai":
        model_config = ModelConfig(
            provider=provider,
            model_name=model_name,
            api_key=config.get("openai_api_key"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", None)
        )
        return OpenAILLMAdapter(model_config)
    elif provider == "anthropic":
        model_config = ModelConfig(
            provider=provider,
            model_name=model_name,
            api_key=config.get("anthropic_api_key"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", None)
        )
        return AnthropicLLMAdapter(model_config)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def _create_memory_adapter(provider: str, config: Dict[str, Any]):
    """创建记忆适配器"""
    
    if provider == "graphiti":
        memory_config = MemorySystemConfig(
            system_type="graphiti_http",
            api_base_url=config.get("graphiti_api_url", "http://localhost:8000"),
            custom_config={
                "neo4j_uri": config.get("neo4j_uri", "bolt://localhost:7687"),
                "neo4j_user": config.get("neo4j_user", "neo4j"),
                "neo4j_password": config.get("neo4j_password", "neo4j_passwd")
            }
        )
        return GraphitiHttpAdapter(memory_config)
    elif provider == "mem0":
        memory_config = MemorySystemConfig(
            system_type="mem0",
            custom_config=config.get("mem0_config", {})
        )
        return Mem0Adapter(memory_config)
    else:
        raise ValueError(f"Unsupported memory provider: {provider}")


# 便捷函数
def create_educational_system(**kwargs) -> CognitiveSystem:
    """创建教育导向的认知系统"""
    return create_restructured_cognitive_system(system_type="educational", **kwargs)


def create_research_system(**kwargs) -> CognitiveSystem:
    """创建研究导向的认知系统"""
    return create_restructured_cognitive_system(system_type="research", **kwargs)


def create_creative_system(**kwargs) -> CognitiveSystem:
    """创建创意导向的认知系统"""
    return create_restructured_cognitive_system(system_type="creative", **kwargs)


def create_lightweight_system(**kwargs) -> CognitiveSystem:
    """创建轻量级认知系统"""
    return create_restructured_cognitive_system(
        system_type="lightweight", 
        enable_collaboration_layer=False, 
        **kwargs
    )


# 与现有配置系统的兼容性支持
def create_system_from_config(config_dict: Dict[str, Any]) -> CognitiveSystem:
    """从配置字典创建系统"""
    
    system_type = config_dict.get("system_type", "educational")
    llm_provider = config_dict.get("llm_provider", "ollama")
    llm_model = config_dict.get("llm_model", "qwen3:8b")
    memory_provider = config_dict.get("memory_provider", "graphiti")
    enable_collaboration = config_dict.get("enable_collaboration_layer", True)
    
    return create_restructured_cognitive_system(
        system_type=system_type,
        llm_provider=llm_provider,
        llm_model_name=llm_model,
        memory_provider=memory_provider,
        enable_collaboration_layer=enable_collaboration,
        config=config_dict
    )


async def initialize_system_async(system: CognitiveSystem) -> bool:
    """异步初始化系统"""
    try:
        success = await system.initialize()
        if success:
            logger.info("Restructured cognitive system initialized successfully")
        else:
            logger.warning("System initialization completed with some warnings")
        return success
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        return False


# 使用示例和测试函数
async def create_and_test_system(query: str = "如何提高学习效率？") -> Dict[str, Any]:
    """创建并测试重构后的系统"""
    
    try:
        # 创建系统
        system = create_educational_system(
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            memory_provider="none"  # 测试时不使用记忆系统
        )
        
        # 初始化
        success = await initialize_system_async(system)
        if not success:
            return {"error": "System initialization failed"}
        
        # 测试处理
        result = await system.process(
            user_id="test_user",
            query=query,
            session_context={}
        )
        
        if result.success:
            return {
                "status": "success",
                "layers_processed": list(result.data.get("layer_outputs", {}).keys()),
                "final_response": result.data.get("layer_outputs", {}).get("behavior", {}).get("adapted_response", {}),
                "processing_metadata": result.metadata
            }
        else:
            return {
                "status": "processing_failed",
                "error": result.error_message,
                "metadata": result.metadata
            }
            
    except Exception as e:
        logger.error(f"System test failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import asyncio
    
    async def main():
        test_result = await create_and_test_system()
        print("系统测试结果：")
        print(test_result)
    
    asyncio.run(main())