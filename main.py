"""
AiEnhance 主程序入口
演示记忆-认知协同系统的基本使用方法
"""

import asyncio
import aienhance


async def demo_basic_usage():
    """演示基本用法"""
    print("🧠 AiEnhance - 记忆-认知协同系统演示")
    print("=" * 50)
    
    # 创建系统实例
    print("1. 创建系统实例...")
    system = aienhance.create_system("default")
    
    # 查看系统状态
    status = system.get_system_status()
    print(f"   系统状态: {status}")
    
    # 模拟用户查询
    print("\n2. 处理用户查询...")
    try:
        response = await system.process_query(
            query="什么是人工智能的记忆机制？",
            user_id="demo_user_001",
            context={"session_id": "demo_session"}
        )
        
        print(f"   查询: {response.processing_metadata['query']}")
        print(f"   处理步骤: {' -> '.join(response.processing_metadata['processing_steps'])}")
        print(f"   用户画像: 思维模式={response.user_profile.cognitive.thinking_mode.value}")
        print(f"   任务特征: 类型={response.context_profile.task_characteristics.task_type.value}")
        print(f"   激活的记忆片段数: {sum(len(result.fragments) for result in response.activated_memories)}")
        print(f"   适配信息: 密度={response.adaptation_info.density_level.value}, 结构={response.adaptation_info.structure_type.value}")
        
        print(f"\n   系统响应:")
        print(f"   {'-' * 40}")
        print(f"   {response.content}")
        print(f"   {'-' * 40}")
        
    except Exception as e:
        print(f"   处理出错: {e}")
    
    # 导出用户画像
    print("\n3. 导出用户画像...")
    profile_export = system.export_user_profile("demo_user_001")
    if profile_export:
        print(f"   用户ID: {profile_export['user_id']}")
        print(f"   认知特征: {profile_export['cognitive']}")
        print(f"   知识结构: {profile_export['knowledge']}")
    
    print("\n✅ 演示完成！")


async def demo_different_systems():
    """演示不同类型的系统"""
    print("\n" + "=" * 50)
    print("🎓 不同系统类型演示")
    print("=" * 50)
    
    systems = {
        "default": aienhance.create_system("default"),
        "educational": aienhance.create_system("educational"),
        "research": aienhance.create_system("research")
    }
    
    query = "机器学习中的注意力机制是如何工作的？"
    
    for system_type, system in systems.items():
        print(f"\n🔹 {system_type.upper()} 系统:")
        
        try:
            response = await system.process_query(
                query=query,
                user_id=f"user_{system_type}",
                context={"system_type": system_type}
            )
            
            print(f"   配置: {system.config}")
            print(f"   适配策略: 密度={response.adaptation_info.density_level.value}")
            print(f"   认知负荷: {response.adaptation_info.cognitive_load:.2f}")
            
        except Exception as e:
            print(f"   处理出错: {e}")


async def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 50)
    print("💬 交互模式 (输入 'quit' 退出)")
    print("=" * 50)
    
    system = aienhance.create_system("default")
    user_id = "interactive_user"
    
    while True:
        try:
            query = input("\n请输入您的问题: ").strip()
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
                
            if not query:
                continue
                
            response = await system.process_query(query, user_id)
            
            print(f"\n🤖 系统回答:")
            print(f"{'-' * 40}")
            print(response.content)
            print(f"{'-' * 40}")
            
            # 显示处理信息
            print(f"\n📊 处理信息:")
            print(f"   认知负荷: {response.adaptation_info.cognitive_load:.2f}")
            print(f"   适配置信度: {response.adaptation_info.adaptation_confidence:.2f}")
            print(f"   记忆激活数: {sum(len(r.fragments) for r in response.activated_memories)}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 处理错误: {e}")


async def main():
    """主函数"""
    print(f"🚀 AiEnhance v{aienhance.__version__} - 记忆-认知协同系统")
    
    try:
        # 基本演示
        await demo_basic_usage()
        
        # 不同系统类型演示
        await demo_different_systems()
        
        # 询问是否进入交互模式
        choice = input("\n是否进入交互模式？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            await interactive_mode()
            
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
