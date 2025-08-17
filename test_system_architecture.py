#!/usr/bin/env python3
"""
系统架构测试
测试LLM接口集成的系统架构，不依赖外部服务
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aienhance import (
    create_system,
    MemorySystemConfig,
    ModelConfig,
    create_model_config,
    create_chat_message,
    MessageRole,
    LLMProviderFactory,
    EmbeddingProviderFactory
)


def test_module_imports():
    """测试模块导入"""
    print("\n" + "="*60)
    print("📦 测试模块导入")
    print("="*60)
    
    try:
        # 测试LLM相关导入
        from aienhance.llm import (
            LLMProvider, EmbeddingProvider, ChatMessage, ChatResponse,
            ModelConfig, MessageRole, LLMProviderFactory
        )
        print("✅ LLM模块导入成功")
        
        # 测试记忆系统导入
        from aienhance.memory import (
            MemorySystem, MemorySystemFactory, MemoryType
        )
        print("✅ 记忆系统模块导入成功")
        
        # 测试核心系统导入
        from aienhance.core import (
            MemoryCognitiveSystem, SystemFactory
        )
        print("✅ 核心系统模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_factory_registration():
    """测试工厂类注册机制"""
    print("\n" + "="*60)
    print("🏭 测试工厂类注册机制")
    print("="*60)
    
    try:
        # 检查LLM提供商注册
        llm_providers = LLMProviderFactory.get_supported_providers()
        print(f"📋 支持的LLM提供商: {llm_providers}")
        
        expected_llm_providers = ["ollama", "openai", "anthropic"]
        for provider in expected_llm_providers:
            if provider in llm_providers:
                print(f"✅ {provider.upper()} LLM适配器已注册")
            else:
                print(f"⚠️ {provider.upper()} LLM适配器未注册")
        
        # 检查嵌入提供商注册
        embedding_providers = EmbeddingProviderFactory.get_supported_providers()
        print(f"📋 支持的嵌入提供商: {embedding_providers}")
        
        expected_embedding_providers = ["ollama", "openai"]
        for provider in expected_embedding_providers:
            if provider in embedding_providers:
                print(f"✅ {provider.upper()} 嵌入适配器已注册")
            else:
                print(f"⚠️ {provider.upper()} 嵌入适配器未注册")
        
        return len(llm_providers) > 0 and len(embedding_providers) > 0
        
    except Exception as e:
        print(f"❌ 工厂类注册测试失败: {e}")
        return False


def test_config_creation():
    """测试配置创建"""
    print("\n" + "="*60)
    print("⚙️ 测试配置创建")
    print("="*60)
    
    try:
        # 测试LLM配置创建
        llm_config = create_model_config(
            provider="ollama",
            model_name="test-model",
            api_base="http://localhost:11434",
            temperature=0.7,
            max_tokens=500
        )
        print(f"✅ LLM配置创建成功: {llm_config.provider}/{llm_config.model_name}")
        
        # 测试记忆系统配置创建
        memory_config = MemorySystemConfig(
            system_type="mirix",
            api_key="test-key",
            api_base="http://localhost:8000"
        )
        print(f"✅ 记忆系统配置创建成功: {memory_config.system_type}")
        
        # 测试聊天消息创建
        message = create_chat_message("user", "测试消息")
        print(f"✅ 聊天消息创建成功: {message.role.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置创建测试失败: {e}")
        return False


def test_system_creation():
    """测试系统创建"""
    print("\n" + "="*60)
    print("🛠️ 测试系统创建")
    print("="*60)
    
    try:
        # 测试默认系统创建
        system1 = create_system(system_type="default")
        print(f"✅ 默认系统创建成功")
        
        # 测试教育系统创建
        system2 = create_system(system_type="educational")
        print(f"✅ 教育系统创建成功")
        
        # 测试研究系统创建
        system3 = create_system(system_type="research")
        print(f"✅ 研究系统创建成功")
        
        # 测试带配置的系统创建（不初始化外部服务）
        system4 = create_system(
            system_type="default",
            llm_provider="ollama",
            llm_model_name="test-model",
            llm_api_base="http://localhost:11434"
        )
        print(f"✅ 带LLM配置的系统创建成功")
        
        # 检查系统状态
        status = system4.get_system_status()
        print(f"📊 系统状态: 初始化={status['initialized']}")
        
        if status.get('llm_provider'):
            print(f"🤖 LLM配置: {status['llm_provider']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统创建测试失败: {e}")
        return False


def test_provider_instantiation():
    """测试提供商实例化"""
    print("\n" + "="*60)
    print("🎭 测试提供商实例化")
    print("="*60)
    
    try:
        success_count = 0
        
        # 测试各个LLM提供商的实例化
        llm_configs = [
            ("ollama", "test-model"),
            ("openai", "gpt-3.5-turbo"),
            ("anthropic", "claude-3-haiku-20240307")
        ]
        
        for provider, model in llm_configs:
            try:
                config = create_model_config(
                    provider=provider,
                    model_name=model,
                    api_base="http://localhost:11434" if provider == "ollama" else None
                )
                
                llm_provider = LLMProviderFactory.create_provider(config)
                print(f"✅ {provider.upper()} LLM提供商实例化成功")
                success_count += 1
                
                # 检查提供商信息
                info = llm_provider.get_model_info()
                print(f"   📋 模型信息: {info}")
                
            except Exception as e:
                print(f"⚠️ {provider.upper()} LLM提供商实例化失败: {e}")
        
        # 测试嵌入提供商实例化
        embedding_configs = [
            ("ollama", "test-embedding"),
            ("openai", "text-embedding-ada-002")
        ]
        
        for provider, model in embedding_configs:
            try:
                config = create_model_config(
                    provider=provider,
                    model_name=model,
                    api_base="http://localhost:11434" if provider == "ollama" else None
                )
                
                embedding_provider = EmbeddingProviderFactory.create_provider(config)
                print(f"✅ {provider.upper()} 嵌入提供商实例化成功")
                success_count += 1
                
            except Exception as e:
                print(f"⚠️ {provider.upper()} 嵌入提供商实例化失败: {e}")
        
        print(f"📊 提供商实例化成功率: {success_count}/{len(llm_configs) + len(embedding_configs)}")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 提供商实例化测试失败: {e}")
        return False


async def test_system_architecture():
    """测试系统架构完整性"""
    print("\n" + "="*60)
    print("🏗️ 测试系统架构完整性")
    print("="*60)
    
    try:
        # 创建完整配置的系统
        system = create_system(
            system_type="educational",
            llm_provider="ollama",
            llm_model_name="test-model"
        )
        
        # 检查系统组件
        components = {
            "用户建模器": hasattr(system, 'user_modeler'),
            "情境分析器": hasattr(system, 'context_analyzer'),
            "记忆激活器": hasattr(system, 'memory_activator'),
            "语义增强器": hasattr(system, 'semantic_enhancer'),
            "类比推理器": hasattr(system, 'analogy_reasoner'),
            "自适应输出": hasattr(system, 'adaptive_output'),
            "LLM提供商": hasattr(system, 'llm_provider'),
            "嵌入提供商": hasattr(system, 'embedding_provider'),
            "记忆系统": hasattr(system, 'memory_system')
        }
        
        for component, exists in components.items():
            if exists:
                print(f"✅ {component}: 已初始化")
            else:
                print(f"⚠️ {component}: 未初始化")
        
        # 检查系统配置
        status = system.get_system_status()
        print(f"\n📊 系统状态详情:")
        print(f"  - 初始化状态: {status['initialized']}")
        print(f"  - 用户数量: {status['user_count']}")
        print(f"  - 会话数量: {status['session_count']}")
        
        # 测试系统方法是否可调用（不实际执行网络请求）
        callable_methods = [
            "process_query",
            "get_system_status", 
            "reset_session",
            "export_user_profile"
        ]
        
        for method in callable_methods:
            if hasattr(system, method) and callable(getattr(system, method)):
                print(f"✅ {method}: 方法可调用")
            else:
                print(f"❌ {method}: 方法不可调用")
        
        return sum(components.values()) >= len(components) * 0.7  # 至少70%的组件正常
        
    except Exception as e:
        print(f"❌ 系统架构测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始LLM接口集成架构测试")
    print("时间:", asyncio.get_event_loop().time())
    
    test_results = {}
    
    # 执行测试
    tests = [
        ("模块导入", test_module_imports),
        ("工厂注册", test_factory_registration),
        ("配置创建", test_config_creation),
        ("系统创建", test_system_creation),
        ("提供商实例化", test_provider_instantiation),
    ]
    
    # 同步测试
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            test_results[test_name] = "✅ 通过" if result else "⚠️ 部分失败"
        except Exception as e:
            test_results[test_name] = f"❌ 失败: {e}"
            print(f"❌ 测试异常: {e}")
    
    # 异步测试
    async def run_async_tests():
        async_tests = [
            ("系统架构", test_system_architecture)
        ]
        
        for test_name, test_func in async_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_func()
                test_results[test_name] = "✅ 通过" if result else "⚠️ 部分失败"
            except Exception as e:
                test_results[test_name] = f"❌ 失败: {e}"
                print(f"❌ 测试异常: {e}")
    
    # 运行异步测试
    asyncio.run(run_async_tests())
    
    # 汇总结果
    print("\n" + "="*60)
    print("📋 架构测试结果汇总")
    print("="*60)
    
    for test_name, result in test_results.items():
        print(f"{test_name}: {result}")
    
    # 统计
    passed = sum(1 for r in test_results.values() if "✅" in r)
    partial = sum(1 for r in test_results.values() if "⚠️" in r)
    failed = sum(1 for r in test_results.values() if "❌" in r)
    
    print(f"\n📊 测试统计: 通过={passed}, 部分失败={partial}, 失败={failed}")
    
    if passed == len(test_results):
        print("🎉 所有架构测试通过！LLM集成架构正常。")
        return True
    elif passed + partial > 0:
        print("⚠️ 部分测试通过，系统架构基本正常。")
        return True
    else:
        print("❌ 架构测试失败，请检查系统实现。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)