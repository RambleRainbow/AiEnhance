"""
记忆系统集成测试脚本
演示如何使用不同的记忆系统与认知框架集成
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import aienhance


async def test_basic_memory_integration():
    """测试基本的记忆系统集成"""
    print("🧠 测试基本记忆系统集成")
    print("=" * 50)
    
    # 创建不带记忆系统的基础系统
    print("1. 创建基础系统 (无记忆系统)")
    basic_system = aienhance.create_system("default")
    
    status = basic_system.get_system_status()
    print(f"   系统状态: 初始化={status['initialized']}, 记忆系统={status['memory_system']}")
    
    # 注意：由于我们将process_query改为async，需要处理这个问题
    print("   基础系统创建成功，但process_query现在是异步的")
    

async def test_mirix_integration():
    """测试MIRIX记忆系统集成"""
    print("\n🔧 测试MIRIX记忆系统集成")
    print("=" * 50)
    
    try:
        # 创建带MIRIX记忆系统的系统
        print("1. 创建MIRIX记忆系统配置")
        mirix_system = aienhance.create_system(
            system_type="default",
            memory_system_type="mirix",
            api_key="test_api_key"  # 这里使用测试API密钥
        )
        
        status = mirix_system.get_system_status()
        print(f"   系统状态: {status}")
        
        print("2. 测试异步查询处理")
        # 由于MIRIX可能未安装，这里只是展示集成方式
        print("   MIRIX集成配置完成 (需要安装MIRIX库才能实际运行)")
        
    except Exception as e:
        print(f"   MIRIX集成测试出错 (预期的): {e}")


async def test_mem0_integration():
    """测试Mem0记忆系统集成"""
    print("\n💾 测试Mem0记忆系统集成")
    print("=" * 50)
    
    try:
        # 创建带Mem0记忆系统的系统
        print("1. 创建Mem0记忆系统配置")
        mem0_system = aienhance.create_system(
            system_type="educational",
            memory_system_type="mem0",
            custom_config={"version": "v1.0"}
        )
        
        status = mem0_system.get_system_status()
        print(f"   系统状态: {status}")
        
        print("2. Mem0集成配置完成 (需要安装Mem0库才能实际运行)")
        
    except Exception as e:
        print(f"   Mem0集成测试出错 (预期的): {e}")


async def test_graphiti_integration():
    """测试Graphiti记忆系统集成"""
    print("\n🌐 测试Graphiti记忆系统集成")
    print("=" * 50)
    
    try:
        # 创建带Graphiti记忆系统的系统
        print("1. 创建Graphiti记忆系统配置")
        graphiti_system = aienhance.create_system(
            system_type="research",
            memory_system_type="graphiti",
            database_url="neo4j://localhost:7687",
            custom_config={"embedding_model": "sentence-transformers"}
        )
        
        status = graphiti_system.get_system_status()
        print(f"   系统状态: {status}")
        
        print("2. Graphiti集成配置完成 (需要安装Graphiti库才能实际运行)")
        
    except Exception as e:
        print(f"   Graphiti集成测试出错 (预期的): {e}")


def test_memory_system_factory():
    """测试记忆系统工厂"""
    print("\n🏭 测试记忆系统工厂")
    print("=" * 50)
    
    # 检查支持的记忆系统类型
    supported_systems = aienhance.MemorySystemFactory.get_supported_systems()
    print(f"支持的记忆系统类型: {supported_systems}")
    
    # 测试创建不同类型的记忆系统配置
    print("\n创建不同记忆系统配置:")
    
    configs = [
        ("mirix", {"api_key": "test_key"}),
        ("mem0", {"custom_config": {"model": "gpt-4"}}),
        ("graphiti", {"database_url": "neo4j://localhost:7687"})
    ]
    
    for system_type, kwargs in configs:
        try:
            config = aienhance.MemorySystemConfig(system_type=system_type, **kwargs)
            print(f"   ✅ {system_type}: {config.system_type} - {config.custom_config}")
        except Exception as e:
            print(f"   ❌ {system_type}: {e}")


def test_memory_data_structures():
    """测试记忆数据结构"""
    print("\n📊 测试记忆数据结构")
    print("=" * 50)
    
    # 测试创建用户上下文
    user_context = aienhance.create_user_context(
        user_id="test_user_001",
        session_id="session_123",
        agent_id="agent_ai",
        custom_field="custom_value"
    )
    print(f"用户上下文: {user_context}")
    
    # 测试创建记忆条目
    memory_entry = aienhance.create_memory_entry(
        content="这是一个测试记忆",
        memory_type=aienhance.MemoryType.EPISODIC,
        user_context=user_context,
        confidence=0.9,
        metadata={"test": True}
    )
    print(f"记忆条目: 类型={memory_entry.memory_type.value}, 内容='{memory_entry.content[:20]}...', 置信度={memory_entry.confidence}")
    
    # 测试记忆类型
    print(f"\n支持的记忆类型:")
    for memory_type in aienhance.MemoryType:
        print(f"   - {memory_type.value}: {memory_type.name}")


async def main():
    """主测试函数"""
    print("🚀 AiEnhance 记忆系统集成测试")
    print("=" * 60)
    
    # 基础测试
    await test_basic_memory_integration()
    
    # 各记忆系统集成测试
    await test_mirix_integration()
    await test_mem0_integration() 
    await test_graphiti_integration()
    
    # 工厂和数据结构测试
    test_memory_system_factory()
    test_memory_data_structures()
    
    print("\n" + "=" * 60)
    print("✅ 记忆系统集成测试完成")
    print("\n💡 使用说明:")
    print("1. 安装对应的记忆系统库 (mirix, mem0, graphiti)")
    print("2. 配置相应的API密钥和数据库连接")
    print("3. 使用 aienhance.create_system() 创建带记忆的系统")
    print("4. 调用 await system.process_query() 进行记忆增强的查询处理")


if __name__ == "__main__":
    asyncio.run(main())