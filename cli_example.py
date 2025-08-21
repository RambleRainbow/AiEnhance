#!/usr/bin/env python3
"""
AiEnhance 命令行工具
简单的命令行界面，快速体验记忆-认知协同系统
"""

import aienhance
import asyncio
import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class AiEnhanceCliTool:
    """AiEnhance命令行工具"""

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
        """初始化系统"""
        try:
            if use_memory:
                # 完整系统配置，使用统一LLM模式
                self.system = aienhance.create_ollama_mirix_system(
                    model_name="qwen3:8b",
                    ollama_base="http://localhost:11434",
                    system_type=system_type,
                    llm_temperature=temperature,
                    llm_max_tokens=800,
                    embedding_provider="ollama",
                    embedding_model_name="bge-m3:latest"
                )
            else:
                # 简化配置，仅使用LLM功能
                print("⚠️  简化模式：仅启用LLM功能，不包含记忆系统")
                self.system = aienhance.create_system(
                    system_type=system_type,
                    llm_provider="ollama",
                    llm_model_name="qwen3:8b",
                    llm_temperature=temperature,
                    llm_max_tokens=800
                )
            return True
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            # 如果完整模式失败，尝试简化模式
            if use_memory:
                print("🔄 尝试简化模式...")
                return await self.initialize_system(system_type, temperature, use_memory=False)
            return False

    async def single_query(self, query, system_type="educational", temperature=0.7, show_details=False):
        """单次查询 - 默认使用流式输出"""
        print("🔧 初始化系统...")
        if not await self.initialize_system(system_type, temperature):
            return

        print("🤔 处理查询中...")
        try:
            # 使用异步上下文管理器确保资源清理
            async with self.system:
                # 默认使用流式处理
                print("\n" + "="*50)
                print("🤖 AI实时回答:")
                print("="*50)
                
                content_parts = []
                async for chunk in self.system.process_stream(
                    query=query,
                    user_id="cli_user",
                    context={"source": "cli"}
                ):
                    print(chunk, end="", flush=True)
                    # 收集内容用于详细信息显示
                    if not chunk.startswith(("🚀", "🧠", "💾", "⚙️", "🤝", "✅", "❌", "⚠️", "🎯")):
                        content_parts.append(chunk)

                if show_details:
                    # 获取系统状态用于详细信息显示
                    status = self.system.get_system_status()
                    print("\n" + "="*50)
                    print("📊 详细信息:")
                    print("="*50)
                    print(f"🔍 系统状态:")
                    print(f"   系统类型: {system_type}")
                    print(f"   LLM配置: {status.get('components', {}).get('llm_provider', {}).get('provider', 'None')}")
                    print(f"   响应长度: {len(''.join(content_parts))}字符")
                    print(f"   流式输出: ✅ 已启用")

        except Exception as e:
            print(f"❌ 查询处理失败: {e}")

    async def interactive_mode(self, system_type="educational", temperature=0.7):
        """交互模式"""
        print("🚀 AiEnhance 交互模式")
        print("="*50)
        print("💡 提示:")
        print("  • 直接输入问题，按回车发送")
        print("  • 输入 'quit' 或 'exit' 退出")
        print("  • 输入 'clear' 清屏")
        print("  • 输入 'status' 查看系统状态")
        print("="*50)

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
                elif user_input.lower() == 'status':
                    status = self.system.get_system_status()
                    print(f"📊 系统状态: {status}")
                    continue
                elif not user_input:
                    continue

                # 处理查询 - 使用流式输出
                print("🤔 思考中...")
                print(f"🤖 AI: ", end="", flush=True)
                
                content_parts = []
                async for chunk in self.system.process_stream(
                    query=user_input,
                    user_id="interactive_user",
                    context={"session": session_count}
                ):
                    # 过滤掉系统状态信息，只显示AI生成的内容
                    if not chunk.startswith(("🚀", "🧠", "💾", "⚙️", "🤝", "✅", "❌", "⚠️", "🎯")):
                        print(chunk, end="", flush=True)
                        content_parts.append(chunk)
                
                if not content_parts:
                    print("(无法生成响应)")
                else:
                    print(f"\n    ⚙️ [流式输出, 长度{len(''.join(content_parts))}字符]")

                session_count += 1

            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 处理错误: {e}")

    async def demo_mode(self):
        """演示模式"""
        print("🎮 AiEnhance 演示模式")
        print("="*50)

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
            print(f"{i}️⃣ {category}演示")
            print(f"👤 用户: {query}")
            print("🤔 AI思考中...")

            try:
                print(f"🤖 AI: ", end="", flush=True)
                
                content_parts = []
                async for chunk in self.system.process_stream(
                    query=query,
                    user_id="demo_user",
                    context={"demo_type": category}
                ):
                    # 只显示AI生成的内容，过滤掉处理状态信息
                    if not chunk.startswith(("🚀", "🧠", "💾", "⚙️", "🤝", "✅", "❌", "⚠️", "🎯")):
                        print(chunk, end="", flush=True)
                        content_parts.append(chunk)

                if not content_parts:
                    print("(无响应生成)")
                else:
                    print(f"\n📊 流式输出: 长度{len(''.join(content_parts))}字符")

                print("-" * 50)

                # 短暂停顿
                if i < len(demo_queries):
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"❌ 演示失败: {e}")
                print("-" * 50)

        print("🎉 演示完成！")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AiEnhance 命令行工具 - 记忆-认知协同系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ai.py "什么是人工智能？"                    # 单次查询
  python ai.py -i                                    # 交互模式  
  python ai.py -d                                    # 演示模式
  python ai.py "解释深度学习" --type research        # 研究模式查询
  python ai.py "创意写作" --temp 0.9 --details       # 高创造性 + 详细信息
        """
    )

    # 位置参数
    parser.add_argument('query', nargs='?', help='要处理的查询问题')

    # 可选参数
    parser.add_argument('-i', '--interactive',
                        action='store_true', help='启动交互模式')
    parser.add_argument('-d', '--demo', action='store_true', help='运行演示模式')
    parser.add_argument('--type', choices=['default', 'educational', 'research'],
                        default='educational', help='系统类型 (默认: educational)')
    parser.add_argument('--temp', type=float, default=0.7,
                        help='温度参数 0.0-1.0 (默认: 0.7)')
    parser.add_argument('--details', action='store_true', help='显示详细的处理信息')

    args = parser.parse_args()

    # 创建工具实例
    tool = AiEnhanceCliTool()

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
        await tool.interactive_mode(args.type, args.temp)
    elif args.demo:
        await tool.demo_mode()
    elif args.query:
        await tool.single_query(args.query, args.type, args.temp, args.details)
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n💡 快速开始:")
        print('  python ai.py "你好，请介绍一下人工智能"')
        print("  python ai.py -i  # 进入交互模式")
        print("  python ai.py -d  # 查看演示")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
