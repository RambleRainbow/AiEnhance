#!/usr/bin/env python3
"""
AiEnhance 流式命令行工具
支持实时流式输出，提升长时间处理的用户体验
"""

import aienhance
import asyncio
import sys
import argparse
from pathlib import Path
from typing import AsyncIterator
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class AiEnhanceStreamingCliTool:
    """AiEnhance流式命令行工具"""

    def __init__(self):
        self.system = None

    async def check_ollama(self):
        """检查Ollama服务状态"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=3.0)
                if response.status_code == 200:
                    return True
                return False
        except:
            return False

    async def initialize_system(self, system_type="educational", temperature=0.7, use_memory=True):
        """初始化分层认知系统"""
        try:
            if use_memory:
                # 使用新的分层认知系统，包含完整功能
                print(f"🧠 正在初始化分层认知系统 (类型: {system_type})...")
                if system_type == "educational":
                    self.system = aienhance.create_educational_layered_system(
                        model_name="qwen3:8b",
                        llm_temperature=temperature,
                        llm_max_tokens=800
                    )
                elif system_type == "research":
                    self.system = aienhance.create_research_layered_system(
                        model_name="qwen3:8b",
                        llm_temperature=temperature,
                        llm_max_tokens=800
                    )
                else:
                    # 使用通用分层系统
                    self.system = aienhance.create_layered_system(
                        system_type=system_type,
                        memory_system_type="mirix_unified",
                        llm_provider="ollama",
                        llm_model_name="qwen3:8b",
                        llm_temperature=temperature,
                        llm_max_tokens=800
                    )
            else:
                # 简化配置，仅使用LLM功能
                print("⚠️  简化模式：仅启用LLM功能，不包含记忆系统")
                # 创建轻量级分层系统（不使用记忆）
                self.system = aienhance.create_layered_system(
                    system_type="lightweight",
                    llm_provider="ollama",
                    llm_model_name="qwen3:8b",
                    llm_temperature=temperature,
                    llm_max_tokens=800
                )
            
            # 初始化分层系统
            success = await self.system.initialize_layers()
            if success:
                print("✅ 分层认知系统初始化完成")
                print("   📋 感知层: 用户建模与上下文分析")
                print("   🧠 认知层: 记忆激活与语义增强")
                print("   🎯 行为层: 内容适配与生成")
                if system_type != "lightweight":
                    print("   🤝 协作层: 多元观点与认知挑战")
                return True
            else:
                print("❌ 分层系统初始化失败")
                return False
        except Exception as e:
            print(f"❌ 分层系统初始化失败: {e}")
            # 如果完整模式失败，尝试简化模式
            if use_memory:
                print("🔄 尝试轻量级模式...")
                return await self.initialize_system(system_type, temperature, use_memory=False)
            return False

    async def stream_query_processing(self, query: str, user_id: str, context: dict) -> AsyncIterator[str]:
        """流式处理查询，使用分层系统的处理方法"""
        
        try:
            # 检查是否有流式处理方法
            if hasattr(self.system, 'process_stream'):
                # 使用系统的流式处理方法
                async for chunk in self.system.process_stream(
                    query=query,
                    user_id=user_id,
                    context=context,
                    yield_steps=True
                ):
                    yield chunk
            else:
                # 使用标准处理方法，模拟流式输出
                yield "📋 感知层处理中...\n"
                
                yield "🧠 认知层激活记忆...\n"
                yield "🎯 行为层适配内容...\n"
                
                # 处理查询
                result = await self.system.process_through_layers(
                    query=query,
                    user_id=user_id,
                    context=context
                )
                
                if result and hasattr(result, 'final_output'):
                    # 获取最终输出内容
                    content = result.final_output
                    
                    # 模拟流式输出，按句子分割
                    import re
                    sentences = re.split(r'[。！？\n]', content)
                    for sentence in sentences:
                        if sentence.strip():
                            yield sentence.strip() + "。"
                            await asyncio.sleep(0.08)  # 模拟流式延迟
                    
                    yield "\n"
                    
                    # 如果有协作层信息
                    if hasattr(result, 'collaboration_output') and result.collaboration_output:
                        collab_out = result.collaboration_output
                        if hasattr(collab_out, 'enhanced_content') and collab_out.enhanced_content:
                            yield "\n🤝 协作增强:\n"
                            enhanced_sentences = re.split(r'[。！？\n]', collab_out.enhanced_content)
                            for sentence in enhanced_sentences[:3]:  # 限制协作内容长度
                                if sentence.strip():
                                    yield sentence.strip() + "。"
                                    await asyncio.sleep(0.05)
                            yield "\n"
                else:
                    yield "抱歉，系统处理出现问题。请检查配置或稍后重试。\n"
                
        except Exception as e:
            yield f"❌ 分层系统处理失败: {e}\n"


    async def single_query_stream(self, query, system_type="educational", temperature=0.7, show_progress=True):
        """单次流式查询"""
        print("🔧 初始化系统...")
        if not await self.initialize_system(system_type, temperature):
            return

        if show_progress:
            print("🚀 开始流式处理...\n")
        
        try:
            # 流式处理查询
            async for chunk in self.stream_query_processing(
                query=query,
                user_id="cli_user",
                context={"source": "cli_streaming"}
            ):
                print(chunk, end='', flush=True)
                
            # 资源将在系统退出时自动清理
                
        except Exception as e:
            print(f"\n❌ 查询处理失败: {e}")

    async def interactive_mode_stream(self, system_type="educational", temperature=0.7):
        """流式交互模式"""
        print("🚀 AiEnhance 流式交互模式")
        print("=" * 50)
        print("💡 提示:")
        print("  • 直接输入问题，按回车发送")
        print("  • 输入 'quit' 或 'exit' 退出")
        print("  • 输入 'clear' 清屏")
        print("=" * 50)

        # 初始化系统
        print("🔧 初始化系统...")
        if not await self.initialize_system(system_type, temperature):
            return
        print(f"✅ 系统初始化成功 (类型: {system_type}, 温度: {temperature})")

        session_count = 0

        while True:
            try:
                # 获取用户输入
                user_input = input(f"\n[{session_count}] 👤 您: ").strip()

                # 处理特殊命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见！感谢使用AiEnhance")
                    break
                elif user_input.lower() == 'clear':
                    import os
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not user_input:
                    continue

                # 开始流式处理
                print(f"\n🤖 AI: ", end='', flush=True)
                start_time = time.time()
                
                try:
                    async for chunk in self.stream_query_processing(
                        query=user_input,
                        user_id="interactive_user",
                        context={"session": session_count}
                    ):
                        # 只输出内容，不输出处理步骤
                        if not chunk.startswith(('🧠', '💾', '🔄', '🤖', '📝', '🎯')):
                            print(chunk, end='', flush=True)
                    
                    end_time = time.time()
                    print(f"\n    ⏱️ 处理时间: {end_time - start_time:.1f}秒")
                    
                except Exception as e:
                    print(f"\n❌ 处理错误: {e}")

                session_count += 1

            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 交互错误: {e}")

    async def demo_mode_stream(self):
        """流式演示模式"""
        print("🎮 AiEnhance 流式演示模式")
        print("=" * 50)

        # 演示查询
        demo_queries = [
            ("基础问答", "你好，请介绍一下自己"),
            ("知识解释", "什么是机器学习？请简单解释"),
            ("创意思维", "设计一个智能家居系统的基本方案"),
            ("问题分析", "分析一下远程工作的利弊")
        ]

        # 初始化系统
        print("🔧 初始化演示系统...")
        if not await self.initialize_system("educational", 0.7):
            return
        print("✅ 系统就绪\n")

        for i, (category, query) in enumerate(demo_queries, 1):
            print(f"\n{i}️⃣ {category}演示")
            print("-" * 30)
            print(f"👤 用户: {query}")
            print(f"🤖 AI: ", end='', flush=True)

            try:
                async for chunk in self.stream_query_processing(
                    query=query,
                    user_id="demo_user",
                    context={"demo_type": category}
                ):
                    # 只输出AI回答内容
                    if not chunk.startswith(('🧠', '💾', '🔄', '🤖', '📝', '🎯')):
                        print(chunk, end='', flush=True)

                print("\n" + "-" * 50)

                # 短暂停顿
                if i < len(demo_queries):
                    await asyncio.sleep(2)

            except Exception as e:
                print(f"\n❌ 演示失败: {e}")
                print("-" * 50)

        print("\n🎉 流式演示完成！")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AiEnhance 流式命令行工具 - 记忆-认知协同系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ai_streaming.py "什么是人工智能？"                    # 流式单次查询
  python ai_streaming.py -i                                    # 流式交互模式  
  python ai_streaming.py -d                                    # 流式演示模式
  python ai_streaming.py "解释深度学习" --type research        # 研究模式查询
  python ai_streaming.py "创意写作" --temp 0.9 --no-progress   # 无进度显示
        """
    )

    # 位置参数
    parser.add_argument('query', nargs='?', help='要处理的查询问题')

    # 可选参数
    parser.add_argument('-i', '--interactive',
                        action='store_true', help='启动流式交互模式')
    parser.add_argument('-d', '--demo', action='store_true', help='运行流式演示模式')
    parser.add_argument('--type', 
                        choices=['educational', 'research', 'creative', 'lightweight'],
                        default='educational', help='分层系统类型 (默认: educational)')
    parser.add_argument('--temp', type=float, default=0.7,
                        help='温度参数 0.0-1.0 (默认: 0.7)')
    parser.add_argument('--no-progress', action='store_true', help='不显示处理进度')

    args = parser.parse_args()

    # 创建工具实例
    tool = AiEnhanceStreamingCliTool()

    # 检查Ollama服务
    print("🔍 检查Ollama服务状态...")
    if not await tool.check_ollama():
        print("❌ Ollama服务未运行或模型未安装")
        print("💡 请确保:")
        print("   1. Ollama服务运行: ollama serve")
        print("   2. 模型已安装: ollama pull qwen3:8b")
        return
    print("✅ Ollama服务正常")

    # 根据参数选择模式
    if args.interactive:
        await tool.interactive_mode_stream(args.type, args.temp)
    elif args.demo:
        await tool.demo_mode_stream()
    elif args.query:
        await tool.single_query_stream(args.query, args.type, args.temp, not args.no_progress)
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n💡 快速开始:")
        print('  python ai_streaming.py "你好，请介绍一下人工智能"')
        print("  python ai_streaming.py -i  # 进入流式交互模式")
        print("  python ai_streaming.py -d  # 查看流式演示")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序错误: {e}")