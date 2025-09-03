#!/usr/bin/env python3
"""
AiEnhance 命令行工具
简单的命令行界面，快速体验记忆-认知协同系统
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

import aienhance

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """设置日志配置"""
    # 从环境变量读取日志级别，默认为INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # 验证日志级别
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        log_level = "INFO"
    
    # 设置日志格式
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # 强制重新配置
    )
    
    # 设置 aienhance 模块的日志级别
    aienhance_logger = logging.getLogger('aienhance')
    aienhance_logger.setLevel(getattr(logging, log_level))
    
    return logging.getLogger(__name__)

# 配置控制台日志输出
logger = setup_logging()


class AiEnhanceCliTool:
    """AiEnhance命令行工具"""

    def __init__(self):
        self.system = None  # type: Optional[aienhance.CognitiveSystem]

    async def check_ollama(self):
        """检查Ollama服务状态"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                response = await client.get(f"{ollama_url}/api/tags", timeout=3.0)
                if response.status_code == 200:
                    return True
                return False
        except:
            return False

    async def initialize_system(
        self, system_type=None, temperature=None, use_memory=None
    ):
        """初始化系统"""
        try:
            # 从环境变量获取默认配置
            system_type = system_type or os.getenv("DEFAULT_SYSTEM_TYPE", "educational")
            temperature = temperature or float(
                os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7")
            )
            use_memory = (
                use_memory
                if use_memory is not None
                else os.getenv("ENABLE_MEMORY_SYSTEM", "true").lower() == "true"
            )
            
            logger.info(f"正在初始化认知系统 - 类型: {system_type}, 温度: {temperature}, 记忆系统: {use_memory}")

            if use_memory:
                # 使用新的层-模块-子模块认知系统，带记忆功能
                if system_type == "educational":
                    self.system = aienhance.create_educational_system(
                        llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
                        llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b"),
                        memory_provider=os.getenv("DEFAULT_MEMORY_SYSTEM", "graphiti"),
                        config={
                            "temperature": temperature,
                            "max_tokens": None,  # 无长度限制，避免截断
                            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        }
                    )
                elif system_type == "research":
                    self.system = aienhance.create_research_system(
                        llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
                        llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b"),
                        memory_provider=os.getenv("DEFAULT_MEMORY_SYSTEM", "graphiti"),
                        config={
                            "temperature": temperature,
                            "max_tokens": None,  # 无长度限制，避免截断
                            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        }
                    )
                elif system_type == "creative":
                    self.system = aienhance.create_creative_system(
                        llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
                        llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b"),
                        memory_provider=os.getenv("DEFAULT_MEMORY_SYSTEM", "graphiti"),
                        config={
                            "temperature": temperature,
                            "max_tokens": None,  # 无长度限制，避免截断
                            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        }
                    )
                else:
                    # 默认使用教育系统
                    self.system = aienhance.create_educational_system(
                        llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
                        llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b"),
                        memory_provider=os.getenv("DEFAULT_MEMORY_SYSTEM", "graphiti"),
                        config={
                            "temperature": temperature,
                            "max_tokens": None,  # 无长度限制，避免截断
                            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        }
                    )
            else:
                # 简化配置，仅使用LLM功能（轻量级系统）
                print("⚠️  简化模式：使用轻量级系统，无记忆功能")
                self.system = aienhance.create_lightweight_system(
                    llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
                    llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b"),
                    config={
                        "llm_temperature": temperature,
                        "llm_max_tokens": None,  # 无长度限制，避免截断
                        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    }
                )

            # 初始化新架构系统
            logger.info("开始系统初始化过程...")
            success = await self.system.initialize()
            if success:
                logger.info("✅ 认知系统初始化完成")
            else:
                logger.warning("⚠️ 系统初始化完成，但存在部分警告")
            return success
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            # 如果完整模式失败，尝试简化模式
            if use_memory:
                print("🔄 尝试简化模式...")
                return await self.initialize_system(
                    system_type, temperature, use_memory=False
                )
            return False

    async def single_query(
        self, query, system_type="educational", temperature=0.7, show_details=False
    ):
        """单次查询 - 默认使用流式输出"""
        print("🔧 初始化系统...")
        if not await self.initialize_system(system_type, temperature):
            return

        print("🤔 处理查询中...")
        logger.info(f"开始处理用户查询: {query[:50]}{'...' if len(query) > 50 else ''}")
        try:
            # 默认使用流式处理
            print("\n" + "=" * 50)
            print("🤖 AI实时回答:")
            print("=" * 50)

            content_parts = []
            result = await self.system.process(
                user_id="cli_user", 
                query=query, 
                session_context={"source": "cli"}
            )
            
            if result.success and "final_response" in result.data:
                print(result.data["final_response"])
            else:
                print("❌ 处理失败:", result.error_message if hasattr(result, 'error_message') else "未知错误")

            if show_details:
                # 获取系统状态用于详细信息显示
                status = self.system.get_system_status()
                print("\n" + "=" * 50)
                print("📊 详细信息:")
                print("=" * 50)
                print("🔍 系统状态:")
                print(f"   系统类型: {system_type}")
                print(
                    f"   LLM配置: {status.get('components', {}).get('llm_provider', {}).get('provider', 'None')}"
                )
                print(f"   响应长度: {len(''.join(content_parts))}字符")
                print("   流式输出: ✅ 已启用")

        except Exception as e:
            print(f"❌ 查询处理失败: {e}")

    async def interactive_mode(self, system_type="educational", temperature=0.7):
        """交互模式"""
        print("🚀 AiEnhance 交互模式")
        print("=" * 50)
        print("💡 提示:")
        print("  • 直接输入问题，按回车发送")
        print("  • 输入 'quit' 或 'exit' 退出")
        print("  • 输入 'clear' 清屏")
        print("  • 输入 'status' 查看系统状态")
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
                if user_input.lower() in ["quit", "exit", "退出", "q"]:
                    print("👋 再见！感谢使用AiEnhance")
                    break
                elif user_input.lower() == "clear":
                    import os

                    os.system("clear" if os.name == "posix" else "cls")
                    continue
                elif user_input.lower() == "status":
                    status = self.system.get_system_status()
                    print(f"📊 系统状态: {status}")
                    continue
                elif not user_input:
                    continue

                # 处理查询 - 使用流式输出
                print("🤔 思考中...")
                print("🤖 AI: ", end="", flush=True)

                content_parts = []
                result = await self.system.process(
                    user_id="interactive_user",
                    query=user_input,
                    session_context={"session": session_count}
                )
                
                if result.success and "final_response" in result.data:
                    print(result.data["final_response"])
                else:
                    print("❌ 处理失败:", result.error_message if hasattr(result, 'error_message') else "未知错误")

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
        print("=" * 50)

        # 演示查询
        demo_queries = [
            ("基础问答", "你好，请介绍一下自己"),
            ("知识解释", "什么是机器学习？请简单解释"),
            ("创意思维", "设计一个智能家居系统的基本方案"),
            ("问题分析", "分析一下远程工作的利弊"),
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
                print("🤖 AI: ", end="", flush=True)

                content_parts = []
                result = await self.system.process(
                    user_id="demo_user",
                    query=query,
                    session_context={"demo_type": category}
                )
                
                if result.success and "final_response" in result.data:
                    print(result.data["final_response"])
                else:
                    print("❌ 处理失败:", result.error_message if hasattr(result, 'error_message') else "未知错误")

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
        """,
    )

    # 位置参数
    parser.add_argument("query", nargs="?", help="要处理的查询问题")

    # 可选参数
    parser.add_argument("-i", "--interactive", action="store_true", help="启动交互模式")
    parser.add_argument("-d", "--demo", action="store_true", help="运行演示模式")
    parser.add_argument(
        "--type",
        choices=["default", "educational", "research"],
        default="educational",
        help="系统类型 (默认: educational)",
    )
    parser.add_argument(
        "--temp", type=float, default=0.7, help="温度参数 0.0-1.0 (默认: 0.7)"
    )
    parser.add_argument("--details", action="store_true", help="显示详细的处理信息")

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
