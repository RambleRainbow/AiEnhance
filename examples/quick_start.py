#!/usr/bin/env python3
"""
AiEnhance 快速开始示例
最简单的使用方式，展示如何快速集成Ollama qwen3:8b
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aienhance


async def quick_start_demo():
    """快速开始演示"""
    print("🚀 AiEnhance 快速开始")
    print("=" * 40)
    
    # 1. 创建系统 - 一行代码即可
    print("1️⃣ 创建智能系统...")
    system = aienhance.create_system(
        system_type="educational",    # 教育模式
        llm_provider="ollama",        # 使用Ollama
        llm_model_name="qwen3:8b",    # qwen3:8b模型
        llm_temperature=0.7           # 适中的创造性
    )
    print("   ✅ 系统创建成功！")
    
    # 2. 处理查询 - 异步调用
    print("\n2️⃣ 处理智能查询...")
    response = await system.process_query(
        query="什么是人工智能？请简单解释一下",
        user_id="quickstart_user"
    )
    
    # 3. 显示结果
    print("\n3️⃣ 查看智能响应...")
    if response.content:
        print(f"🤖 AI回答:")
        print(f"   {response.content}")
        print(f"\n📊 响应信息:")
        print(f"   • 响应长度: {len(response.content)}字符")
        
        # 显示用户建模信息
        if hasattr(response, 'user_profile'):
            print(f"   • 思维模式: {response.user_profile.cognitive.thinking_mode.value}")
        
        # 显示适配信息  
        if hasattr(response, 'adaptation_info'):
            print(f"   • 输出密度: {response.adaptation_info.density_level.value}")
            print(f"   • 认知负荷: {response.adaptation_info.cognitive_load:.2f}")
    else:
        print("⚠️ 未生成内容，请检查Ollama服务是否正常运行")
    
    print("\n🎉 快速开始演示完成！")


async def interactive_demo():
    """交互式演示"""
    print("\n💬 交互式对话模式")
    print("=" * 40)
    print("提示：输入 'quit' 退出")
    
    # 创建系统
    system = aienhance.create_system(
        system_type="educational",
        llm_provider="ollama", 
        llm_model_name="qwen3:8b",
        llm_temperature=0.7
    )
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 处理查询
            print("🤔 思考中...")
            response = await system.process_query(
                query=user_input,
                user_id="interactive_user"
            )
            
            # 显示响应
            if response.content:
                print(f"🤖 AI: {response.content}")
            else:
                print("🤖 AI: (无法生成响应，请检查服务状态)")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"❌ 处理错误: {e}")


async def main():
    """主函数"""
    print("🎯 选择演示模式:")
    print("1. 快速演示 (自动)")
    print("2. 交互对话 (手动)")
    
    try:
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            await quick_start_demo()
        elif choice == "2":
            await interactive_demo()
        else:
            print("❌ 无效选择，运行默认演示")
            await quick_start_demo()
            
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())