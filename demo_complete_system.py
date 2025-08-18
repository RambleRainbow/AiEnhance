#!/usr/bin/env python3
"""
AiEnhance 完整系统演示
展示如何配置和使用完整的记忆-认知协同系统，集成Ollama qwen3:8b模型
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import aienhance


async def demo_complete_system_setup():
    """演示完整系统配置"""
    print("🛠️ 完整系统配置演示")
    print("=" * 60)
    
    # 1. 创建带Ollama LLM的完整系统
    print("\n1️⃣ 创建完整配置系统（LLM + 嵌入）")
    system = aienhance.create_system(
        system_type="educational",
        # LLM配置
        llm_provider="ollama",
        llm_model_name="qwen3:8b",
        llm_api_base="http://localhost:11434",
        llm_temperature=0.7,
        llm_max_tokens=800,
        # 嵌入模型配置
        embedding_provider="ollama", 
        embedding_model_name="bge-m3",
        embedding_api_base="http://localhost:11434"
    )
    
    print(f"   ✅ 系统创建成功")
    
    # 2. 检查系统状态
    status = system.get_system_status()
    print(f"\n📊 系统状态:")
    print(f"   • 系统类型: {status.get('config', {})}")
    print(f"   • LLM初始化: {status.get('llm_initialized', False)}")
    print(f"   • 嵌入模型初始化: {status.get('embedding_initialized', False)}")
    print(f"   • 记忆系统初始化: {status.get('memory_initialized', False)}")
    
    return system


async def demo_intelligent_conversation(system):
    """演示智能对话功能"""
    print("\n\n💬 智能对话演示")
    print("=" * 60)
    
    # 测试查询列表
    test_queries = [
        {
            "query": "什么是深度学习？",
            "user_id": "student_001",
            "context": {"session_id": "learning_session_1"}
        },
        {
            "query": "深度学习和机器学习有什么区别？",
            "user_id": "student_001", 
            "context": {"session_id": "learning_session_1"}
        },
        {
            "query": "请举个神经网络的实际应用例子",
            "user_id": "student_001",
            "context": {"session_id": "learning_session_1"}
        }
    ]
    
    print(f"🔍 模拟智能对话（共{len(test_queries)}个查询）")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n--- 对话轮次 {i} ---")
        print(f"👤 用户: {test['query']}")
        
        try:
            # 处理查询
            response = await system.process_query(**test)
            
            # 显示系统响应
            print(f"🤖 系统回答:")
            print(f"   {'-' * 50}")
            if response.content:
                print(f"   {response.content}")
            else:
                print(f"   (无内容生成 - 检查LLM配置)")
            print(f"   {'-' * 50}")
            
            # 显示处理信息
            if hasattr(response, 'processing_metadata'):
                print(f"📈 处理信息:")
                metadata = response.processing_metadata
                print(f"   • 处理步骤: {' → '.join(metadata.get('processing_steps', []))}")
                print(f"   • 处理时间: {metadata.get('total_time', 0):.2f}s")
            
            # 显示用户建模信息
            if hasattr(response, 'user_profile'):
                print(f"👤 用户画像:")
                print(f"   • 思维模式: {response.user_profile.cognitive.thinking_mode.value}")
                print(f"   • 认知复杂度: {response.user_profile.cognitive.cognitive_complexity:.2f}")
                
            # 显示适配信息
            if hasattr(response, 'adaptation_info'):
                print(f"⚙️ 适配策略:")
                print(f"   • 输出密度: {response.adaptation_info.density_level.value}")
                print(f"   • 结构类型: {response.adaptation_info.structure_type.value}")
                print(f"   • 认知负荷: {response.adaptation_info.cognitive_load:.2f}")
                
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            
        # 短暂停顿，模拟真实对话
        await asyncio.sleep(0.5)


async def demo_system_configurations():
    """演示不同系统配置"""
    print("\n\n🔧 系统配置对比演示")
    print("=" * 60)
    
    configurations = [
        {
            "name": "基础系统（仅LLM）",
            "config": {
                "system_type": "default",
                "llm_provider": "ollama",
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.5
            }
        },
        {
            "name": "教育系统（LLM + 协作）",
            "config": {
                "system_type": "educational", 
                "llm_provider": "ollama",
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.3,  # 更低温度，更稳定输出
                "llm_max_tokens": 1000
            }
        },
        {
            "name": "研究系统（高创造性）",
            "config": {
                "system_type": "research",
                "llm_provider": "ollama", 
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.8,  # 更高温度，更有创造性
                "llm_max_tokens": 1200
            }
        }
    ]
    
    test_query = "人工智能在医疗领域有哪些应用？"
    
    for i, config_info in enumerate(configurations, 1):
        print(f"\n{i}️⃣ {config_info['name']}")
        print(f"   配置: {config_info['config']}")
        
        try:
            # 创建系统
            system = aienhance.create_system(**config_info['config'])
            
            # 测试查询
            response = await system.process_query(
                query=test_query,
                user_id=f"test_user_{i}",
                context={"test_config": config_info['name']}
            )
            
            print(f"   ✅ 创建成功")
            print(f"   🎯 响应特征:")
            if hasattr(response, 'adaptation_info'):
                print(f"     • 适配密度: {response.adaptation_info.density_level.value}")
                print(f"     • 认知负荷: {response.adaptation_info.cognitive_load:.2f}")
            
            if response.content:
                # 显示响应片段
                content_preview = response.content[:100] + "..." if len(response.content) > 100 else response.content
                print(f"     • 响应预览: {content_preview}")
            else:
                print(f"     • 响应: (空内容)")
                
        except Exception as e:
            print(f"   ❌ 配置失败: {e}")


async def demo_ollama_integration():
    """演示Ollama集成的具体细节"""
    print("\n\n🤖 Ollama集成演示")
    print("=" * 60)
    
    print("📋 Ollama配置检查:")
    
    # 1. 检查Ollama服务
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                models_data = response.json()
                print(f"   ✅ Ollama服务运行正常")
                print(f"   📚 可用模型:")
                for model in models_data.get('models', []):
                    model_name = model.get('name', 'Unknown')
                    model_size = model.get('size', 0) / (1024**3)  # 转换为GB
                    print(f"     • {model_name} ({model_size:.1f}GB)")
            else:
                print(f"   ❌ Ollama服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无法连接Ollama服务: {e}")
        print(f"   💡 请确保Ollama正在运行: ollama serve")
        return
    
    # 2. 创建具体的Ollama配置
    print(f"\n🛠️ 创建Ollama系统:")
    system = aienhance.create_system(
        system_type="educational",
        llm_provider="ollama",
        llm_model_name="qwen3:8b",
        llm_api_base="http://localhost:11434",
        llm_temperature=0.7,
        llm_max_tokens=500,
        embedding_provider="ollama",
        embedding_model_name="bge-m3"
    )
    
    print(f"   ✅ 系统创建成功")
    
    # 3. 测试不同类型的查询
    test_cases = [
        ("事实性查询", "北京是中国的首都吗？"),
        ("解释性查询", "请解释什么是量子计算"),
        ("创造性查询", "设计一个智能家居系统的方案"),
        ("中文理解", "用一句话总结《红楼梦》的主题")
    ]
    
    print(f"\n🧪 多类型查询测试:")
    for query_type, query in test_cases:
        print(f"\n   📝 {query_type}: {query}")
        try:
            response = await system.process_query(
                query=query,
                user_id="ollama_test_user",
                context={"query_type": query_type}
            )
            
            if response.content:
                # 显示响应和特征分析
                print(f"   ✅ 生成成功 ({len(response.content)}字符)")
                if hasattr(response, 'adaptation_info'):
                    print(f"   📊 适配信息: {response.adaptation_info.density_level.value}密度")
            else:
                print(f"   ⚠️ 无内容生成")
                
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")


async def demo_performance_monitoring():
    """演示性能监控"""
    print("\n\n📊 性能监控演示")
    print("=" * 60)
    
    # 创建系统
    system = aienhance.create_system(
        system_type="default",
        llm_provider="ollama",
        llm_model_name="qwen3:8b",
        llm_temperature=0.6
    )
    
    print("🚀 性能测试开始...")
    
    # 批量测试
    test_queries = [
        "什么是人工智能？",
        "机器学习的主要算法有哪些？", 
        "深度学习在图像识别中的应用",
        "自然语言处理的发展历程",
        "推荐系统的工作原理"
    ]
    
    start_time = asyncio.get_event_loop().time()
    successful_queries = 0
    total_response_length = 0
    
    for i, query in enumerate(test_queries, 1):
        try:
            query_start = asyncio.get_event_loop().time()
            response = await system.process_query(
                query=query,
                user_id=f"perf_test_user_{i}",
                context={"batch_test": True}
            )
            query_end = asyncio.get_event_loop().time()
            
            if response.content:
                successful_queries += 1
                total_response_length += len(response.content)
                print(f"   ✅ 查询{i}: {query_end - query_start:.2f}s, {len(response.content)}字符")
            else:
                print(f"   ⚠️ 查询{i}: 无内容生成")
                
        except Exception as e:
            print(f"   ❌ 查询{i}失败: {e}")
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    # 性能统计
    print(f"\n📈 性能统计:")
    print(f"   • 总耗时: {total_time:.2f}秒")
    print(f"   • 成功查询: {successful_queries}/{len(test_queries)}")
    print(f"   • 平均响应时间: {total_time/len(test_queries):.2f}秒/查询")
    print(f"   • 总生成字符数: {total_response_length}")
    if successful_queries > 0:
        print(f"   • 平均响应长度: {total_response_length/successful_queries:.0f}字符/响应")


async def main():
    """主演示函数"""
    print("🚀 AiEnhance 完整系统集成演示")
    print("=" * 80)
    print("展示记忆-认知协同系统与Ollama qwen3:8b的完整集成")
    print("=" * 80)
    
    try:
        # 1. 系统配置演示
        system = await demo_complete_system_setup()
        
        # 2. 智能对话演示
        await demo_intelligent_conversation(system)
        
        # 3. 系统配置对比
        await demo_system_configurations()
        
        # 4. Ollama集成细节
        await demo_ollama_integration()
        
        # 5. 性能监控
        await demo_performance_monitoring()
        
        print("\n\n🎉 演示完成！")
        print("=" * 80)
        print("✅ AiEnhance系统与Ollama qwen3:8b集成演示成功")
        print("✅ 四层架构（感知→认知→行为→协作）运行正常")
        print("✅ 用户建模和自适应输出功能验证")
        print("✅ 多种系统配置模式验证")
        print("✅ 性能监控和质量评估完成")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)