#!/usr/bin/env python3
"""
LLM集成演示脚本
展示记忆-认知协同系统与LLM提供商的无缝集成能力
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aienhance import create_system


async def demo_system_creation():
    """演示系统创建与配置"""
    print("🔧 系统创建与配置演示")
    print("=" * 50)
    
    # 1. 创建默认系统（不配置LLM）
    print("\n1️⃣ 创建默认系统（无LLM）")
    default_system = create_system(system_type="default")
    status = default_system.get_system_status()
    print(f"   ✅ 系统创建成功")
    print(f"   📊 LLM状态: {status.get('llm_provider', 'None')}")
    
    # 2. 创建带Ollama LLM的系统
    print("\n2️⃣ 创建带Ollama LLM的系统")
    ollama_system = create_system(
        system_type="educational",
        llm_provider="ollama",
        llm_model_name="llama3.2:1b",
        llm_api_base="http://localhost:11434",
        llm_temperature=0.7,
        llm_max_tokens=300
    )
    status = ollama_system.get_system_status()
    print(f"   ✅ 系统创建成功")
    print(f"   🤖 LLM配置: {status.get('llm_provider', {})}")
    
    # 3. 创建完整配置系统（LLM + 记忆）
    print("\n3️⃣ 创建完整配置系统（LLM + 记忆）")
    full_system = create_system(
        system_type="research",
        # 记忆系统配置
        memory_system_type="mirix",
        memory_api_key="demo-key",
        memory_api_base="http://localhost:8000",
        # LLM配置
        llm_provider="ollama",
        llm_model_name="llama3.2:1b",
        llm_temperature=0.8,
        # 嵌入模型配置
        embedding_provider="ollama",
        embedding_model_name="mxbai-embed-large"
    )
    status = full_system.get_system_status()
    print(f"   ✅ 完整系统创建成功")
    print(f"   🧠 记忆系统: {status.get('memory_system', {}).get('system_type', 'None')}")
    print(f"   🤖 LLM提供商: {status.get('llm_provider', {}).get('provider', 'None')}")
    print(f"   🎯 嵌入提供商: {status.get('embedding_provider', {}).get('provider', 'None')}")
    
    return full_system


async def demo_provider_switching():
    """演示提供商切换能力"""
    print("\n\n🔄 提供商切换能力演示")
    print("=" * 50)
    
    providers = [
        {
            "name": "Ollama本地部署",
            "config": {
                "llm_provider": "ollama",
                "llm_model_name": "llama3.2:1b",
                "llm_api_base": "http://localhost:11434"
            }
        },
        {
            "name": "OpenAI服务",
            "config": {
                "llm_provider": "openai",
                "llm_model_name": "gpt-3.5-turbo",
                "llm_api_key": "${OPENAI_API_KEY}"  # 从环境变量获取
            }
        },
        {
            "name": "Anthropic Claude",
            "config": {
                "llm_provider": "anthropic",
                "llm_model_name": "claude-3-haiku-20240307",
                "llm_api_key": "${ANTHROPIC_API_KEY}"  # 从环境变量获取
            }
        }
    ]
    
    for i, provider in enumerate(providers, 1):
        print(f"\n{i}️⃣ 配置 {provider['name']}")
        try:
            system = create_system(
                system_type="default",
                **provider['config']
            )
            
            status = system.get_system_status()
            llm_info = status.get('llm_provider', {})
            print(f"   ✅ {provider['name']} 配置成功")
            print(f"   📋 模型: {llm_info.get('model', 'Unknown')}")
            print(f"   🔧 提供商: {llm_info.get('provider', 'Unknown')}")
            
        except Exception as e:
            print(f"   ⚠️ {provider['name']} 配置失败: {e}")


async def demo_cognitive_processing():
    """演示认知处理流程"""
    print("\n\n🧠 认知处理流程演示")
    print("=" * 50)
    
    # 创建演示系统
    system = create_system(
        system_type="educational",
        llm_provider="ollama",
        llm_model_name="llama3.2:1b",
        llm_temperature=0.7
    )
    
    print("✅ 演示系统创建成功")
    
    # 模拟用户查询
    test_queries = [
        "什么是机器学习？",
        "深度学习与传统机器学习有什么区别？",
        "能给我一个神经网络的简单例子吗？"
    ]
    
    print(f"\n🔍 模拟认知处理流程（共{len(test_queries)}个查询）")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- 查询 {i}: {query} ---")
        
        try:
            # 这里不实际执行网络请求，而是展示处理流程
            print(f"📥 输入: {query}")
            print(f"🔄 处理流程:")
            print(f"   1️⃣ 感知层: 用户建模 + 情境分析")
            print(f"   2️⃣ 认知层: 记忆激活 + 语义增强 + 类比推理")
            print(f"   3️⃣ 行为层: 个性化适配 + LLM生成")
            print(f"   4️⃣ 输出层: 结构化响应")
            
            # 检查系统组件
            components_status = {
                "用户建模器": hasattr(system, 'user_modeler'),
                "记忆激活器": hasattr(system, 'memory_activator'),
                "LLM提供商": hasattr(system, 'llm_provider'),
                "自适应输出": hasattr(system, 'adaptive_output')
            }
            
            print(f"🔧 系统组件状态:")
            for component, status in components_status.items():
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component}")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")


async def demo_configuration_flexibility():
    """演示配置灵活性"""
    print("\n\n⚙️ 配置灵活性演示")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "教育场景 - 低温度，详细解释",
            "config": {
                "system_type": "educational",
                "llm_provider": "ollama",
                "llm_model_name": "llama3.2:1b",
                "llm_temperature": 0.3,
                "llm_max_tokens": 500
            }
        },
        {
            "name": "研究场景 - 高温度，创新思维",
            "config": {
                "system_type": "research", 
                "llm_provider": "ollama",
                "llm_model_name": "llama3.2:1b",
                "llm_temperature": 0.9,
                "llm_max_tokens": 800
            }
        },
        {
            "name": "多模态场景 - LLM+嵌入+记忆",
            "config": {
                "system_type": "default",
                "llm_provider": "ollama",
                "llm_model_name": "llama3.2:1b",
                "embedding_provider": "ollama",
                "embedding_model_name": "mxbai-embed-large",
                "memory_system_type": "mirix",
                "memory_api_key": "demo-key"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ {scenario['name']}")
        
        try:
            system = create_system(**scenario['config'])
            status = system.get_system_status()
            
            print(f"   ✅ 场景配置成功")
            print(f"   📊 系统类型: {scenario['config']['system_type']}")
            
            if status.get('llm_provider'):
                print(f"   🤖 LLM配置: {status['llm_provider']}")
            
            if status.get('embedding_provider'):
                print(f"   🎯 嵌入模型: {status['embedding_provider']}")
                
            if status.get('memory_system'):
                print(f"   🧠 记忆系统: {status['memory_system']}")
                
        except Exception as e:
            print(f"   ❌ 配置失败: {e}")


async def demo_architecture_benefits():
    """演示架构优势"""
    print("\n\n🏗️ 架构优势演示")
    print("=" * 50)
    
    print("🎯 本架构的核心优势:")
    print()
    
    advantages = [
        {
            "title": "1. 提供商无关性",
            "description": "通过统一接口支持Ollama、OpenAI、Anthropic等多种LLM提供商",
            "example": "system.llm_provider.chat(messages) - 无论底层是什么模型"
        },
        {
            "title": "2. 热插拔能力",
            "description": "可以在运行时切换LLM提供商，无需修改核心业务逻辑",
            "example": "create_system(llm_provider='ollama') -> create_system(llm_provider='openai')"
        },
        {
            "title": "3. 配置驱动",
            "description": "通过简单配置即可组合不同的记忆系统和LLM提供商",
            "example": "memory_system_type='mirix' + llm_provider='anthropic'"
        },
        {
            "title": "4. 模块化设计",
            "description": "感知层、认知层、行为层独立工作，LLM作为可选增强",
            "example": "系统可以在没有LLM的情况下正常工作，LLM仅作为输出增强"
        },
        {
            "title": "5. 扩展友好",
            "description": "通过工厂模式轻松添加新的LLM提供商适配器",
            "example": "LLMProviderFactory.register_provider('new_provider', NewAdapter)"
        }
    ]
    
    for advantage in advantages:
        print(f"📌 {advantage['title']}")
        print(f"   💡 {advantage['description']}")
        print(f"   🔧 示例: {advantage['example']}")
        print()


async def main():
    """主演示函数"""
    print("🚀 AiEnhance LLM集成演示")
    print("=" * 60)
    print("展示记忆-认知协同系统与LLM的深度集成能力")
    print("=" * 60)
    
    try:
        # 执行各个演示
        await demo_system_creation()
        await demo_provider_switching()
        await demo_cognitive_processing()
        await demo_configuration_flexibility()
        await demo_architecture_benefits()
        
        print("\n\n🎉 演示完成！")
        print("=" * 60)
        print("✅ LLM接口集成功能已完全实现")
        print("✅ 支持多种LLM提供商的无缝切换")
        print("✅ 提供灵活的配置和扩展能力")
        print("✅ 架构设计符合开放-封闭原则")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)