#!/usr/bin/env python3
"""
测试LLM-based领域推断系统
验证新的领域推断功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from aienhance.core.domain_inference import (
    DomainInferenceConfig,
    DomainInferenceManager,
    LLMDomainInferenceProvider,
    DomainInferenceResult
)
from aienhance.core.multi_llm_config import (
    MultiLLMConfigManager,
    LLMModelConfig,
    BusinessFunctionLLMConfig
)
from aienhance.core.perception_layer import PerceptionLayer
from aienhance.core.layer_interfaces import PerceptionInput
from aienhance.llm.adapters.ollama_adapter import OllamaLLMAdapter
from aienhance.llm.interfaces import ModelConfig


class MockLLMProvider:
    """模拟LLM提供商，用于测试"""
    
    def __init__(self, model_name: str = "mock_model"):
        self.model_name = model_name
    
    async def generate_async(self, messages, **kwargs):
        """模拟异步生成"""
        # 处理不同的消息格式
        if isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], dict):
                query_content = messages[0].get("content", "")
            else:
                # 如果是ChatMessage对象，获取其内容
                query_content = getattr(messages[0], 'content', str(messages[0]))
        else:
            query_content = str(messages)
        
        # 从完整的提示中提取实际的用户查询
        user_query = ""
        if "用户查询:" in query_content:
            # 提取 "用户查询:" 后面的内容
            query_start = query_content.find("用户查询:") + len("用户查询:")
            query_end = query_content.find("\n\n", query_start)
            if query_end == -1:
                query_end = len(query_content)
            user_query = query_content[query_start:query_end].strip()
        else:
            user_query = query_content
        
        
        # 根据提取的用户查询返回不同的领域推断结果
        if any(keyword in user_query.lower() for keyword in ["编程", "python", "ai", "算法", "技术", "programming", "algorithm", "开发", "人工智能", "机器学习"]):
            return {
                "content": '''
                {
                    "primary_domains": ["technology"],
                    "secondary_domains": ["education"],
                    "confidence_scores": {"technology": 0.9, "education": 0.6},
                    "interdisciplinary": true,
                    "reasoning": "查询涉及技术和编程内容，主要属于技术领域，同时涉及学习相关内容。"
                }
                '''
            }
        elif any(keyword in user_query.lower() for keyword in ["商业", "营销", "管理", "business", "marketing", "经济"]):
            return {
                "content": '''
                {
                    "primary_domains": ["business"],
                    "secondary_domains": ["psychology", "economics"],
                    "confidence_scores": {"business": 0.85, "psychology": 0.5, "economics": 0.6},
                    "interdisciplinary": true,
                    "reasoning": "查询涉及商业管理，是典型的跨学科内容，结合了商业、心理学和经济学。"
                }
                '''
            }
        elif any(keyword in user_query.lower() for keyword in ["艺术", "设计", "创作", "art", "design", "作品"]):
            return {
                "content": '''
                {
                    "primary_domains": ["art"],
                    "secondary_domains": ["psychology"],
                    "confidence_scores": {"art": 0.8, "psychology": 0.4},
                    "interdisciplinary": false,
                    "reasoning": "查询主要涉及艺术创作相关内容。"
                }
                '''
            }
        elif any(keyword in user_query.lower() for keyword in ["天气", "weather", "今天"]):
            return {
                "content": '''
                {
                    "primary_domains": ["general"],
                    "secondary_domains": [],
                    "confidence_scores": {"general": 0.7},
                    "interdisciplinary": false,
                    "reasoning": "查询内容较为通用，属于日常生活类问题。"
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
    
    async def chat(self, messages, **kwargs):
        """提供chat接口兼容性"""
        result = await self.generate_async(messages, **kwargs)
        return result["content"]


async def test_domain_inference_basic():
    """测试基础领域推断功能"""
    print("🧪 测试1: 基础领域推断功能")
    print("-" * 40)
    
    # 创建模拟LLM提供商
    mock_llm = MockLLMProvider()
    
    # 创建领域推断配置
    config = DomainInferenceConfig(
        llm_provider=mock_llm,
        model_name="mock_model",
        temperature=0.1,
        max_tokens=300,
        timeout=10
    )
    
    # 创建领域推断提供商
    provider = LLMDomainInferenceProvider(config)
    success = await provider.initialize()
    
    if not success:
        print("   ❌ 初始化失败")
        return False
    
    # 测试查询
    test_cases = [
        ("如何学习Python编程？", ["technology"]),
        ("如何进行商业营销？", ["business"]), 
        ("如何创作艺术作品？", ["art"]),
        ("今天天气怎么样？", ["general"])
    ]
    
    all_passed = True
    
    for query, expected_domains in test_cases:
        try:
            result = await provider.infer_domains(query)
            
            # 检查是否包含预期领域
            all_domains = result.primary_domains + result.secondary_domains
            has_expected = any(domain in all_domains for domain in expected_domains)
            
            status = "✅" if has_expected else "❌"
            print(f"   {status} 查询: {query}")
            print(f"      预期: {expected_domains}")
            print(f"      结果: {result.primary_domains} + {result.secondary_domains}")
            print(f"      推理: {result.reasoning}")
            
            if not has_expected:
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ 查询失败: {query} - {e}")
            all_passed = False
    
    await provider.cleanup()
    
    print(f"\n   测试结果: {'✅ 全部通过' if all_passed else '❌ 部分失败'}")
    return all_passed


async def test_domain_inference_manager():
    """测试领域推断管理器"""
    print("\n🧪 测试2: 领域推断管理器")
    print("-" * 40)
    
    manager = DomainInferenceManager()
    
    # 注册多个提供商
    providers = [
        ("primary", MockLLMProvider("primary_model")),
        ("fallback", MockLLMProvider("fallback_model"))
    ]
    
    for name, mock_llm in providers:
        config = DomainInferenceConfig(
            llm_provider=mock_llm,
            model_name=f"mock_{name}",
            temperature=0.1,
            max_tokens=300
        )
        
        provider = LLMDomainInferenceProvider(config)
        success = await manager.register_provider(name, provider)
        
        status = "✅" if success else "❌"
        print(f"   {status} 注册提供商: {name}")
    
    # 测试使用不同提供商
    test_query = "如何开发AI算法？"
    
    try:
        # 使用主要提供商
        result1 = await manager.infer_domains(test_query, provider_name="primary")
        print(f"   ✅ 主要提供商推断: {result1.primary_domains}")
        
        # 使用备选提供商
        result2 = await manager.infer_domains(test_query, provider_name="fallback")
        print(f"   ✅ 备选提供商推断: {result2.primary_domains}")
        
        # 使用默认提供商
        result3 = await manager.infer_domains(test_query)
        print(f"   ✅ 默认提供商推断: {result3.primary_domains}")
        
    except Exception as e:
        print(f"   ❌ 推断测试失败: {e}")
        return False
    
    # 清理
    await manager.cleanup()
    print("   ✅ 管理器清理完成")
    
    return True


async def test_perception_layer_integration():
    """测试感知层集成"""
    print("\n🧪 测试3: 感知层集成测试")
    print("-" * 40)
    
    try:
        # 创建模拟LLM提供商
        mock_llm = MockLLMProvider("perception_test")
        
        # 感知层配置，包含领域推断配置
        perception_config = {
            'domain_inference': {
                'llm_provider': mock_llm,
                'model_name': 'mock_perception_model',
                'temperature': 0.1,
                'max_tokens': 300,
                'timeout': 10,
                'custom_domains': ['technology', 'science', 'education', 'business', 'art']
            }
        }
        
        # 创建感知层
        perception_layer = PerceptionLayer(
            config=perception_config,
            memory_system=None,  # 暂不使用记忆系统
            llm_provider=mock_llm
        )
        
        # 初始化感知层
        success = await perception_layer.initialize()
        if not success:
            print("   ❌ 感知层初始化失败")
            return False
        
        print("   ✅ 感知层初始化成功")
        
        # 创建测试输入
        test_input = PerceptionInput(
            query="我想学习如何设计和开发人工智能算法，特别是机器学习相关的技术",
            user_id="test_user_001", 
            context={"session_type": "learning", "complexity_level": "intermediate"},
            historical_data=None
        )
        
        # 处理感知层输入
        output = await perception_layer.process(test_input)
        
        if output.status.name == "COMPLETED":
            print("   ✅ 感知层处理成功")
            
            # 检查用户画像中的推断领域
            if 'inferred_domains' in str(output.data):
                print("   ✅ 领域推断已集成到用户画像中")
            else:
                print("   ⚠️  领域推断未在用户画像中找到")
            
            # 显示部分结果
            if output.user_profile:
                print(f"   用户ID: {output.user_profile.user_id}")
                print(f"   知识领域: {output.user_profile.knowledge_profile}")
            
        else:
            print(f"   ❌ 感知层处理失败: {output.error_message}")
            return False
        
        # 清理
        await perception_layer.cleanup()
        print("   ✅ 感知层清理完成")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 感知层集成测试失败: {e}")
        return False


async def test_multi_llm_config_integration():
    """测试多LLM配置集成"""
    print("\n🧪 测试4: 多LLM配置集成")
    print("-" * 40)
    
    try:
        # 创建多LLM配置管理器
        config_manager = MultiLLMConfigManager()
        
        # 设置默认配置
        default_config = LLMModelConfig(
            provider="mock",
            model_name="default_model",
            temperature=0.7,
            max_tokens=800
        )
        config_manager.set_default_config(default_config)
        print("   ✅ 设置默认配置")
        
        # 注册领域推断专用配置
        domain_inference_config = BusinessFunctionLLMConfig(
            function_name="domain_inference",
            primary_model=LLMModelConfig(
                provider="mock",
                model_name="domain_specialized_model",
                temperature=0.1,  # 低温度用于分类任务
                max_tokens=300,
                timeout=10
            ),
            fallback_model=LLMModelConfig(
                provider="mock",
                model_name="domain_fallback_model", 
                temperature=0.1,
                max_tokens=200,
                timeout=8
            )
        )
        
        config_manager.register_business_function(domain_inference_config)
        print("   ✅ 注册领域推断专用配置")
        
        # 获取并验证配置
        retrieved_config = config_manager.get_config_for_function("domain_inference")
        if retrieved_config:
            print(f"   ✅ 获取配置: {retrieved_config.provider}/{retrieved_config.model_name}")
            print(f"      参数: T={retrieved_config.temperature}, Max={retrieved_config.max_tokens}")
        else:
            print("   ❌ 配置获取失败")
            return False
        
        # 获取备选配置
        fallback_config = config_manager.get_fallback_config_for_function("domain_inference")
        if fallback_config:
            print(f"   ✅ 备选配置: {fallback_config.provider}/{fallback_config.model_name}")
        
        # 测试功能控制
        print("   ✅ 功能控制测试:")
        print(f"      禁用功能: {config_manager.disable_function('domain_inference')}")
        print(f"      启用功能: {config_manager.enable_function('domain_inference')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 多LLM配置集成测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 LLM-based领域推断系统测试套件")
    print("=" * 60)
    
    tests = [
        ("基础领域推断", test_domain_inference_basic),
        ("领域推断管理器", test_domain_inference_manager), 
        ("感知层集成", test_perception_layer_integration),
        ("多LLM配置集成", test_multi_llm_config_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"   ✅ {test_name} - 通过")
            else:
                print(f"   ❌ {test_name} - 失败")
        except Exception as e:
            print(f"   ❌ {test_name} - 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! LLM-based领域推断系统工作正常")
    else:
        print("⚠️  部分测试失败，请检查实现")
    
    print("\n💡 系统特性:")
    print("   • 使用大模型进行智能领域推断，替代简单关键词匹配")
    print("   • 支持多模型配置，为不同业务功能使用不同LLM")
    print("   • 支持主要模型和备选模型配置")
    print("   • 集成到感知层，自动进行领域推断")
    print("   • 简化的单一实现路径，专注LLM推断")
    
    return passed == total


async def main():
    """主函数"""
    success = await run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())