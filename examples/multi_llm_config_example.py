#!/usr/bin/env python3
"""
多LLM配置示例
展示如何为不同业务功能配置不同的LLM模型
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from aienhance.core.multi_llm_config import (
    MultiLLMConfigManager,
    LLMModelConfig,
    BusinessFunctionLLMConfig,
    create_config_from_dict,
    DOMAIN_INFERENCE_OPTIMIZED_CONFIG,
    CREATIVE_TASK_CONFIG,
    ANALYTICAL_TASK_CONFIG
)
from aienhance.core.domain_inference import (
    DomainInferenceConfig,
    DomainInferenceManager,
    LLMDomainInferenceProvider
)


# 示例配置字典 - 可以从配置文件加载
EXAMPLE_MULTI_LLM_CONFIG = {
    "default": {
        "provider": "ollama",
        "model_name": "qwen3:8b",
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
        "max_tokens": 800,
        "timeout": 30
    },
    "business_functions": {
        "domain_inference": {
            "primary": {
                "provider": "ollama",
                "model_name": "qwen3:8b",
                "base_url": "http://localhost:11434", 
                "temperature": 0.1,  # 低温度确保分类一致性
                "max_tokens": 300,   # 较少token用于分类
                "timeout": 10,
                "custom_params": {
                    "system_prompt": "你是一个专业的领域分析专家"
                }
            },
            "fallback": {
                "provider": "ollama", 
                "model_name": "qwen3:4b",  # 更小的备选模型
                "base_url": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 300,
                "timeout": 8
            },
            "enabled": True,
            "custom_config": {
                "fallback_to_keywords": True,
                "custom_domains": ["technology", "science", "education", "business", "art", "health"]
            }
        },
        "creative_generation": {
            "primary": {
                "provider": "ollama",
                "model_name": "qwen3:32b",  # 大模型用于创意任务
                "base_url": "http://localhost:11434",
                "temperature": 0.8,  # 高温度增加创造性
                "max_tokens": 1200,
                "timeout": 45
            },
            "enabled": True
        },
        "analytical_reasoning": {
            "primary": {
                "provider": "ollama",
                "model_name": "qwen3:14b",  # 中等模型用于分析
                "base_url": "http://localhost:11434", 
                "temperature": 0.3,  # 中等温度平衡准确性和灵活性
                "max_tokens": 1000,
                "timeout": 30
            },
            "enabled": True
        },
        "user_modeling": {
            "primary": {
                "provider": "ollama",
                "model_name": "qwen3:8b",  # 默认模型
                "base_url": "http://localhost:11434",
                "temperature": 0.5,
                "max_tokens": 600,
                "timeout": 20
            },
            "enabled": False  # 暂时禁用，使用默认配置
        }
    }
}


async def demonstrate_multi_llm_config():
    """演示多LLM配置管理"""
    print("🔧 多LLM配置管理演示")
    print("=" * 50)
    
    # 从字典创建配置管理器
    config_manager = create_config_from_dict(EXAMPLE_MULTI_LLM_CONFIG)
    
    print("\n1️⃣ 配置概览:")
    print(f"   已配置业务功能: {config_manager.list_configured_functions()}")
    
    # 展示不同业务功能的配置
    functions_to_test = ["domain_inference", "creative_generation", "analytical_reasoning", "user_modeling"]
    
    print("\n2️⃣ 业务功能LLM配置:")
    for func_name in functions_to_test:
        config = config_manager.get_config_for_function(func_name)
        fallback = config_manager.get_fallback_config_for_function(func_name)
        
        print(f"\n   📌 {func_name}:")
        if config:
            print(f"      主要模型: {config.provider}/{config.model_name}")
            print(f"      温度: {config.temperature}, 最大token: {config.max_tokens}")
        if fallback:
            print(f"      备选模型: {fallback.provider}/{fallback.model_name}")
        if not config and not fallback:
            print("      使用默认配置")
    
    return config_manager


async def test_domain_inference_with_config(config_manager: MultiLLMConfigManager):
    """测试使用配置的领域推断功能"""
    print("\n" + "=" * 50)
    print("🧪 领域推断功能测试")
    print("=" * 50)
    
    # 获取领域推断的配置
    domain_config = config_manager.get_config_for_function("domain_inference")
    if not domain_config:
        print("   ❌ 未找到领域推断配置")
        return
    
    # 模拟LLM提供商 (在实际使用中这应该是真正的LLM实例)
    class MockLLMProvider:
        def __init__(self, config: LLMModelConfig):
            self.config = config
        
        async def generate_async(self, messages, **kwargs):
            # 模拟LLM响应
            query_content = messages[0]["content"]
            if "编程" in query_content or "AI" in query_content:
                return {
                    "content": '''
                    {
                        "primary_domains": ["technology"],
                        "secondary_domains": ["education"],
                        "confidence_scores": {"technology": 0.9, "education": 0.6},
                        "interdisciplinary": true,
                        "reasoning": "查询涉及编程和AI技术，主要属于技术领域，同时涉及学习相关内容。"
                    }
                    '''
                }
            else:
                return {
                    "content": '''
                    {
                        "primary_domains": ["general"],
                        "secondary_domains": [],
                        "confidence_scores": {"general": 0.7},
                        "interdisciplinary": false,
                        "reasoning": "查询内容较为通用，未检测到特定专业领域特征。"
                    }
                    '''
                }
    
    try:
        # 创建模拟的LLM提供商
        mock_llm = MockLLMProvider(domain_config)
        
        # 创建领域推断配置
        inference_config = DomainInferenceConfig(
            llm_provider=mock_llm,
            model_name=domain_config.model_name,
            temperature=domain_config.temperature,
            max_tokens=domain_config.max_tokens,
            timeout=domain_config.timeout
        )
        
        # 创建领域推断提供商
        provider = LLMDomainInferenceProvider(inference_config)
        await provider.initialize()
        
        # 测试查询
        test_queries = [
            "如何学习Python编程和机器学习？",
            "今天天气怎么样？",
            "如何设计一个高效的算法？"
        ]
        
        print(f"\n   使用模型: {domain_config.provider}/{domain_config.model_name}")
        print(f"   温度: {domain_config.temperature}, 最大token: {domain_config.max_tokens}")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   测试{i}: {query}")
            try:
                result = await provider.infer_domains(query)
                print(f"   结果: 主要领域 = {result.primary_domains}")
                print(f"         次要领域 = {result.secondary_domains}")
                print(f"         跨学科 = {result.interdisciplinary}")
                print(f"         推理 = {result.reasoning}")
            except Exception as e:
                print(f"   ❌ 推断失败: {e}")
        
        await provider.cleanup()
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")


async def demonstrate_configuration_flexibility():
    """演示配置的灵活性"""
    print("\n" + "=" * 50)
    print("⚙️  配置灵活性演示")
    print("=" * 50)
    
    # 创建配置管理器
    manager = MultiLLMConfigManager()
    
    # 动态添加配置
    print("\n1️⃣ 动态配置管理:")
    
    # 设置默认配置
    default_config = LLMModelConfig(
        provider="ollama",
        model_name="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7,
        max_tokens=800
    )
    manager.set_default_config(default_config)
    print("   ✅ 设置默认配置")
    
    # 添加专门的业务功能配置
    specialized_configs = [
        BusinessFunctionLLMConfig(
            function_name="sentiment_analysis",
            primary_model=LLMModelConfig(
                provider="ollama",
                model_name="qwen3:4b",
                temperature=0.2,  # 低温度用于情感分析
                max_tokens=200
            )
        ),
        BusinessFunctionLLMConfig(
            function_name="text_generation", 
            primary_model=LLMModelConfig(
                provider="ollama",
                model_name="qwen3:32b",
                temperature=0.9,  # 高温度用于文本生成
                max_tokens=1500
            ),
            fallback_model=LLMModelConfig(
                provider="ollama", 
                model_name="qwen3:14b",
                temperature=0.9,
                max_tokens=1200
            )
        )
    ]
    
    for config in specialized_configs:
        manager.register_business_function(config)
        print(f"   ✅ 注册业务功能: {config.function_name}")
    
    print(f"\n2️⃣ 配置状态:")
    print(f"   已配置功能: {manager.list_configured_functions()}")
    
    # 演示配置获取
    print(f"\n3️⃣ 配置获取演示:")
    for func_name in ["sentiment_analysis", "text_generation", "undefined_function"]:
        config = manager.get_config_for_function(func_name)
        if config:
            print(f"   {func_name}: {config.provider}/{config.model_name} (T={config.temperature})")
        else:
            print(f"   {func_name}: 使用默认配置")
    
    # 演示功能启用/禁用
    print(f"\n4️⃣ 功能控制演示:")
    print(f"   禁用sentiment_analysis: {manager.disable_function('sentiment_analysis')}")
    print(f"   当前启用功能: {manager.list_configured_functions()}")
    print(f"   重新启用sentiment_analysis: {manager.enable_function('sentiment_analysis')}")
    print(f"   当前启用功能: {manager.list_configured_functions()}")


async def main():
    """主函数"""
    print("🚀 多模型协同调度配置系统演示")
    print("=" * 70)
    
    # 基本配置演示
    config_manager = await demonstrate_multi_llm_config()
    
    # 领域推断测试
    await test_domain_inference_with_config(config_manager)
    
    # 配置灵活性演示
    await demonstrate_configuration_flexibility()
    
    print("\n" + "=" * 70)
    print("✨ 演示完成!")
    print("💡 这个系统支持:")
    print("   • 为每个业务功能配置独立的LLM模型")
    print("   • 主要模型和备选模型配置")
    print("   • 运行时动态启用/禁用功能") 
    print("   • 灵活的参数配置 (温度、token限制等)")
    print("   • 从配置文件或字典加载配置")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())