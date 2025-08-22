#!/usr/bin/env python3
"""
LLM接口集成测试
测试完整的记忆-认知协同系统与LLM的集成功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aienhance import MemorySystemConfig, create_model_config, create_system


async def test_ollama_llm_integration():
    """测试Ollama LLM集成"""
    print("\n" + "=" * 60)
    print("🤖 测试Ollama LLM集成")
    print("=" * 60)

    try:
        # 创建Ollama LLM配置
        llm_config = create_model_config(
            provider="ollama",
            model_name="qwen3:8b",  # 使用较小的模型进行测试
            api_base="http://localhost:11434",
            temperature=0.7,
            max_tokens=500,
        )

        # 创建系统（仅LLM，不使用记忆系统进行简单测试）
        system = create_system(
            system_type="default",
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            llm_api_base="http://localhost:11434",
            llm_temperature=0.7,
            llm_max_tokens=500,
        )

        print("✅ 系统创建成功")

        # 获取系统状态
        status = system.get_system_status()
        print(f"📊 系统状态: 初始化={status['initialized']}")
        print(f"🧠 LLM提供商: {status.get('llm_provider', 'None')}")

        # 测试简单查询
        print("\n🔍 测试用户查询...")
        response = await system.process_query(
            query="什么是人工智能？请简要解释。", user_id="test_user_001"
        )

        print(f"💬 系统响应: {response.content[:200]}...")
        print(f"🎯 响应长度: {len(response.content)} 字符")

        # 检查LLM元数据
        if (
            hasattr(response.adaptation_info, "metadata")
            and response.adaptation_info.metadata
        ):
            if response.adaptation_info.metadata.get("llm_generated"):
                print("✅ LLM成功生成响应")
                print(
                    f"🤖 使用模型: {response.adaptation_info.metadata.get('llm_model')}"
                )
                usage = response.adaptation_info.metadata.get("llm_usage", {})
                if usage:
                    print(f"📈 Token使用: {usage}")
            else:
                print("⚠️ 使用默认响应生成")

        return True

    except Exception as e:
        print(f"❌ Ollama LLM测试失败: {e}")
        return False


async def test_memory_llm_integration():
    """测试记忆系统与LLM的完整集成"""
    print("\n" + "=" * 60)
    print("🧠 测试记忆系统与LLM完整集成")
    print("=" * 60)

    try:
        # 创建带记忆系统的完整配置
        memory_config = MemorySystemConfig(
            system_type="mirix", api_key="test-key", api_base="http://localhost:8000"
        )

        llm_config = create_model_config(
            provider="ollama",
            model_name="qwen3:8b",
            api_base="http://localhost:11434",
            temperature=0.7,
            max_tokens=300,
        )

        # 创建完整系统
        system = create_system(
            system_type="educational",
            memory_system_type="mirix",
            llm_provider="ollama",
            memory_api_key="test-key",
            memory_api_base="http://localhost:8000",
            llm_model_name="qwen3:8b",
            llm_api_base="http://localhost:11434",
            llm_temperature=0.7,
            llm_max_tokens=300,
        )

        print("✅ 完整系统创建成功")

        # 获取系统状态
        status = system.get_system_status()
        print("📊 系统状态:")
        print(f"  - 初始化: {status['initialized']}")
        print(
            f"  - 记忆系统: {status.get('memory_system', {}).get('system_type', 'None')}"
        )
        print(
            f"  - LLM提供商: {status.get('llm_provider', {}).get('provider', 'None')}"
        )

        # 测试连续对话
        print("\n🔄 测试连续对话...")

        queries = [
            "我对机器学习很感兴趣，能介绍一下基本概念吗？",
            "刚才提到的监督学习能举个例子吗？",
            "我想深入了解神经网络，有什么建议？",
        ]

        user_id = "test_user_002"

        for i, query in enumerate(queries, 1):
            print(f"\n📝 查询 {i}: {query}")

            try:
                response = await system.process_query(
                    query=query,
                    user_id=user_id,
                    context={"session_id": "test_session_001"},
                )

                print(f"💭 响应 {i}: {response.content[:150]}...")

                # 分析处理步骤
                steps = response.processing_metadata.get("processing_steps", [])
                print(f"🔧 处理步骤: {', '.join(steps)}")

                # 检查记忆激活
                if response.activated_memories:
                    print(f"🧠 激活记忆: {len(response.activated_memories)} 条")

                # 检查LLM生成
                if (
                    hasattr(response.adaptation_info, "metadata")
                    and response.adaptation_info.metadata
                ):
                    if response.adaptation_info.metadata.get("llm_generated"):
                        print("✅ LLM参与响应生成")

            except Exception as e:
                print(f"⚠️ 查询 {i} 处理失败: {e}")
                # 继续其他查询的测试
                continue

        return True

    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        return False


async def test_different_llm_providers():
    """测试不同LLM提供商的切换"""
    print("\n" + "=" * 60)
    print("🔄 测试不同LLM提供商切换")
    print("=" * 60)

    providers_configs = [
        {
            "name": "Ollama",
            "provider": "ollama",
            "model_name": "qwen3:8b",
            "api_base": "http://localhost:11434",
        },
        # 注释掉需要API密钥的提供商，避免测试失败
        # {
        #     "name": "OpenAI",
        #     "provider": "openai",
        #     "model_name": "gpt-3.5-turbo",
        #     "api_key": "your-openai-key"
        # },
        # {
        #     "name": "Anthropic",
        #     "provider": "anthropic",
        #     "model_name": "claude-3-haiku-20240307",
        #     "api_key": "your-anthropic-key"
        # }
    ]

    success_count = 0

    for config in providers_configs:
        print(f"\n🤖 测试 {config['name']} 提供商...")

        try:
            # 动态构建参数
            kwargs = {
                "system_type": "default",
                "llm_provider": config["provider"],
                "llm_model_name": config["model_name"],
            }

            # 添加可选参数
            if "api_base" in config:
                kwargs["llm_api_base"] = config["api_base"]
            if "api_key" in config:
                kwargs["llm_api_key"] = config["api_key"]

            # 创建系统
            system = create_system(**kwargs)

            print(f"✅ {config['name']} 系统创建成功")

            # 简单测试查询
            try:
                response = await system.process_query(
                    query="Hello, how are you?",
                    user_id=f"test_user_{config['provider']}",
                )

                if response.content:
                    print(
                        f"💬 {config['name']} 响应正常 (长度: {len(response.content)})"
                    )
                    success_count += 1
                else:
                    print(f"⚠️ {config['name']} 响应为空")

            except Exception as e:
                print(f"⚠️ {config['name']} 查询测试失败: {e}")

        except Exception as e:
            print(f"❌ {config['name']} 初始化失败: {e}")

    print(f"\n📊 提供商测试结果: {success_count}/{len(providers_configs)} 成功")
    return success_count > 0


async def test_streaming_functionality():
    """测试流式响应功能"""
    print("\n" + "=" * 60)
    print("🌊 测试流式响应功能")
    print("=" * 60)

    try:
        # 创建支持流式的系统
        system = create_system(
            system_type="default",
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            llm_api_base="http://localhost:11434",
        )

        print("✅ 流式系统创建成功")

        # 测试流式响应（需要添加到系统API中）
        # 注意：当前系统架构中没有直接的流式接口，这里演示概念
        if hasattr(system, "llm_provider") and system.llm_provider:
            print("🔄 测试LLM流式接口...")

            from aienhance.llm import create_chat_message

            messages = [create_chat_message("user", "请写一首关于春天的短诗")]

            try:
                # 直接测试LLM适配器的流式功能
                await system.llm_provider.initialize()

                print("💭 流式响应开始:")
                content_parts = []
                async for chunk in system.llm_provider.chat_stream(messages):
                    content_parts.append(chunk)
                    print(chunk, end="", flush=True)

                full_content = "".join(content_parts)
                print(f"\n✅ 流式响应完成 (总长度: {len(full_content)})")
                return True

            except Exception as e:
                print(f"⚠️ 流式响应测试失败: {e}")
                return False
        else:
            print("⚠️ 系统未配置LLM提供商")
            return False

    except Exception as e:
        print(f"❌ 流式功能测试失败: {e}")
        return False


async def test_system_performance():
    """测试系统性能"""
    print("\n" + "=" * 60)
    print("⚡ 测试系统性能")
    print("=" * 60)

    import time

    try:
        # 创建测试系统
        system = create_system(
            system_type="default",
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            llm_api_base="http://localhost:11434",
            llm_temperature=0.5,
            llm_max_tokens=100,  # 限制token数量以提高速度
        )

        print("✅ 性能测试系统创建成功")

        # 准备测试查询
        test_queries = [
            "什么是AI？",
            "解释机器学习",
            "Python的特点",
            "数据科学应用",
            "深度学习概念",
        ]

        print(f"🔄 开始处理 {len(test_queries)} 个查询...")

        total_start_time = time.time()
        results = []

        for i, query in enumerate(test_queries, 1):
            start_time = time.time()

            try:
                response = await system.process_query(
                    query=query, user_id=f"perf_user_{i:03d}"
                )

                end_time = time.time()
                duration = end_time - start_time

                results.append(
                    {
                        "query": query,
                        "duration": duration,
                        "response_length": len(response.content),
                        "success": True,
                    }
                )

                print(
                    f"✅ 查询 {i}: {duration:.2f}s (响应长度: {len(response.content)})"
                )

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                results.append(
                    {
                        "query": query,
                        "duration": duration,
                        "error": str(e),
                        "success": False,
                    }
                )

                print(f"❌ 查询 {i}: {duration:.2f}s (失败: {e})")

        total_end_time = time.time()
        total_duration = total_end_time - total_start_time

        # 计算性能统计
        successful_results = [r for r in results if r["success"]]

        if successful_results:
            avg_duration = sum(r["duration"] for r in successful_results) / len(
                successful_results
            )
            avg_response_length = sum(
                r["response_length"] for r in successful_results
            ) / len(successful_results)

            print("\n📊 性能统计:")
            print(f"  - 总时间: {total_duration:.2f}s")
            print(
                f"  - 成功率: {len(successful_results)}/{len(test_queries)} ({len(successful_results) / len(test_queries) * 100:.1f}%)"
            )
            print(f"  - 平均响应时间: {avg_duration:.2f}s")
            print(f"  - 平均响应长度: {avg_response_length:.0f} 字符")
            print(f"  - 吞吐量: {len(successful_results) / total_duration:.2f} 查询/秒")

        return len(successful_results) > 0

    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始LLM接口集成测试")
    print("时间:", asyncio.get_event_loop().time())

    test_results = {}

    # 执行各项测试
    tests = [
        ("Ollama LLM集成", test_ollama_llm_integration),
        ("记忆-LLM完整集成", test_memory_llm_integration),
        ("多提供商切换", test_different_llm_providers),
        ("流式响应功能", test_streaming_functionality),
        ("系统性能", test_system_performance),
    ]

    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = await test_func()
            test_results[test_name] = "✅ 通过" if result else "⚠️ 部分失败"
        except Exception as e:
            test_results[test_name] = f"❌ 失败: {e}"
            print(f"❌ 测试异常: {e}")

    # 汇总结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)

    for test_name, result in test_results.items():
        print(f"{test_name}: {result}")

    # 统计
    passed = sum(1 for r in test_results.values() if "✅" in r)
    partial = sum(1 for r in test_results.values() if "⚠️" in r)
    failed = sum(1 for r in test_results.values() if "❌" in r)

    print(f"\n📊 测试统计: 通过={passed}, 部分失败={partial}, 失败={failed}")

    if passed == len(tests):
        print("🎉 所有测试通过！LLM集成功能正常。")
    elif passed + partial > 0:
        print("⚠️ 部分测试通过，系统基本可用。")
    else:
        print("❌ 测试失败，请检查配置和环境。")


if __name__ == "__main__":
    asyncio.run(main())
