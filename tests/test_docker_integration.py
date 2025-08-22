#!/usr/bin/env python3
"""
Docker集成测试脚本
测试MIRIX后端服务与AiEnhance的集成
"""

import asyncio
import sys
from datetime import datetime

import httpx


async def test_service_health():
    """测试服务健康状态"""
    print("🔍 测试服务健康状态...")

    services = {
        "AiEnhance主应用": "http://localhost:8080/health",
        "MIRIX后端": "http://localhost:8000/health",
        "Ollama": "http://localhost:11434/api/tags",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for service_name, url in services.items():
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"✅ {service_name}: 健康")
                else:
                    print(f"⚠️ {service_name}: 状态码 {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name}: 连接失败 - {e}")


async def test_mirix_api():
    """测试MIRIX API"""
    print("\n🧠 测试MIRIX API...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 测试添加记忆
            memory_data = {
                "content": "这是一个测试记忆：人工智能是模拟人类智能的技术",
                "memory_type": "semantic",
                "user_id": "test_user_001",
                "session_id": "test_session_001",
                "metadata": {
                    "source": "docker_test",
                    "timestamp": datetime.now().isoformat(),
                },
            }

            print("📝 添加测试记忆...")
            response = await client.post(
                "http://localhost:8000/api/memory/add", json=memory_data
            )

            if response.status_code == 200:
                result = response.json()
                memory_id = result.get("memory_id")
                print(f"✅ 记忆添加成功: {memory_id}")

                # 测试搜索记忆
                print("🔍 搜索测试记忆...")
                search_data = {
                    "query": "人工智能",
                    "user_id": "test_user_001",
                    "limit": 5,
                    "similarity_threshold": 0.5,
                }

                search_response = await client.post(
                    "http://localhost:8000/api/memory/search", json=search_data
                )

                if search_response.status_code == 200:
                    search_result = search_response.json()
                    memories = search_result.get("memories", [])
                    print(f"✅ 搜索成功，找到 {len(memories)} 条记忆")

                    for i, mem in enumerate(memories[:2], 1):
                        print(f"   {i}. {mem.get('content', 'N/A')[:50]}...")
                else:
                    print(f"❌ 搜索失败: {search_response.status_code}")

            else:
                print(f"❌ 添加记忆失败: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ MIRIX API测试失败: {e}")


async def test_aienhance_api():
    """测试AiEnhance API"""
    print("\n🤖 测试AiEnhance API...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 测试查询处理
            query_data = {
                "query": "什么是机器学习？请简要解释。",
                "user_id": "test_user_002",
                "session_id": "test_session_002",
                "context": {"source": "docker_integration_test"},
            }

            print("💭 发送查询请求...")
            response = await client.post(
                "http://localhost:8080/api/query", json=query_data
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "")
                processing_metadata = result.get("processing_metadata", {})
                system_info = result.get("system_info", {})

                print("✅ 查询处理成功")
                print(f"📄 响应内容: {content[:200]}...")
                print(f"🔧 处理步骤: {processing_metadata.get('processing_steps', [])}")
                print(
                    f"🧠 激活记忆数: {system_info.get('activated_memories_count', 0)}"
                )
                print(f"🤖 LLM生成: {system_info.get('llm_generated', False)}")

                # 测试系统状态
                print("\n📊 获取系统状态...")
                status_response = await client.get(
                    "http://localhost:8080/api/system/status"
                )

                if status_response.status_code == 200:
                    status = status_response.json()
                    print("✅ 系统状态获取成功")
                    print(f"   - 初始化: {status.get('initialized', False)}")
                    print(f"   - 用户数: {status.get('user_count', 0)}")
                    print(f"   - 会话数: {status.get('session_count', 0)}")

                    memory_system = status.get("memory_system", {})
                    if memory_system:
                        print(
                            f"   - 记忆系统: {memory_system.get('system_type', 'none')}"
                        )

                    llm_provider = status.get("llm_provider", {})
                    if llm_provider:
                        print(f"   - LLM提供商: {llm_provider.get('provider', 'none')}")
                else:
                    print(f"⚠️ 系统状态获取失败: {status_response.status_code}")

            else:
                print(f"❌ 查询处理失败: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ AiEnhance API测试失败: {e}")


async def test_ollama_integration():
    """测试Ollama集成"""
    print("\n🦙 测试Ollama集成...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 检查可用模型
            response = await client.get("http://localhost:11434/api/tags")

            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama连接成功，可用模型数量: {len(models)}")

                for model in models[:3]:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0)
                    print(f"   - {name} ({size // (1024 * 1024 * 1024):.1f}GB)")

                # 测试简单生成（如果有模型）
                if models:
                    print("\n🔄 测试LLM生成...")
                    generate_data = {
                        "model": models[0].get("name"),
                        "prompt": "Hello, how are you?",
                        "stream": False,
                    }

                    gen_response = await client.post(
                        "http://localhost:11434/api/generate", json=generate_data
                    )

                    if gen_response.status_code == 200:
                        result = gen_response.json()
                        response_text = result.get("response", "")
                        print(f"✅ LLM生成成功: {response_text[:100]}...")
                    else:
                        print(f"⚠️ LLM生成失败: {gen_response.status_code}")

            else:
                print(f"❌ Ollama连接失败: {response.status_code}")

        except Exception as e:
            print(f"❌ Ollama测试失败: {e}")


async def test_end_to_end():
    """端到端集成测试"""
    print("\n🔄 端到端集成测试...")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # 创建一个特定配置的系统
            system_config = {
                "system_type": "educational",
                "memory_system_type": "mirix",
                "llm_provider": "ollama",
                "config": {
                    "memory_api_base": "http://localhost:8000",
                    "llm_api_base": "http://localhost:11434",
                    "llm_model_name": "qwen3:8b",
                },
            }

            print("🛠️ 创建测试系统...")
            create_response = await client.post(
                "http://localhost:8080/api/system/create", json=system_config
            )

            if create_response.status_code == 200:
                system_info = create_response.json()
                system_id = system_info.get("system_id")
                print(f"✅ 系统创建成功: {system_id}")

                # 进行多轮对话测试
                conversations = [
                    "请介绍一下深度学习的基本概念",
                    "深度学习和传统机器学习有什么区别？",
                    "能举个神经网络的具体例子吗？",
                ]

                user_id = "e2e_test_user"
                session_id = "e2e_test_session"

                for i, query in enumerate(conversations, 1):
                    print(f"\n💬 对话 {i}: {query}")

                    query_data = {
                        "query": query,
                        "user_id": user_id,
                        "session_id": session_id,
                        "system_type": "educational",
                    }

                    response = await client.post(
                        "http://localhost:8080/api/query", json=query_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("content", "")
                        metadata = result.get("processing_metadata", {})

                        print(f"✅ 响应: {content[:150]}...")
                        print(
                            f"🔧 处理时间: {len(metadata.get('processing_steps', []))} 步骤"
                        )
                    else:
                        print(f"❌ 对话失败: {response.status_code}")

                # 检查用户画像
                print("\n👤 检查用户画像...")
                profile_response = await client.get(
                    f"http://localhost:8080/api/user/{user_id}/profile"
                )

                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print("✅ 用户画像获取成功")
                    print(f"   - 用户ID: {profile.get('user_id')}")
                    print(f"   - 创建时间: {profile.get('created_at')}")
                elif profile_response.status_code == 404:
                    print("ℹ️ 用户画像尚未建立（正常情况）")
                else:
                    print(f"⚠️ 用户画像获取失败: {profile_response.status_code}")

            else:
                print(f"❌ 系统创建失败: {create_response.status_code}")
                print(create_response.text)

        except Exception as e:
            print(f"❌ 端到端测试失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 Docker集成测试开始")
    print("=" * 60)

    try:
        await test_service_health()
        await test_mirix_api()
        await test_aienhance_api()
        await test_ollama_integration()
        await test_end_to_end()

        print("\n" + "=" * 60)
        print("🎉 Docker集成测试完成！")
        print("\n💡 如果所有测试都通过，说明Docker部署成功！")
        print("🌐 你可以通过 http://localhost:8080 访问AiEnhance系统")

    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
