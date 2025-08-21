#!/usr/bin/env python3
"""
Ollama集成测试
测试AiEnhance系统与Ollama qwen3:8b的集成
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import aienhance


async def test_ollama_integration():
    """测试Ollama集成"""
    print("🧪 Ollama集成测试")
    print("=" * 50)

    # 1. 检查Ollama服务
    print("1️⃣ 检查Ollama服务状态...")
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                print(f"   ✅ Ollama服务正常，可用模型: {', '.join(available_models)}")

                # 检查必需模型
                if "qwen3:8b" not in available_models:
                    print("   ⚠️ 未找到qwen3:8b模型")
                    print("   💡 请运行: ollama pull qwen3:8b")
                    return False
                else:
                    print("   ✅ qwen3:8b模型已就绪")
            else:
                print(f"   ❌ Ollama服务异常: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ 无法连接Ollama: {e}")
        print("   💡 请确保Ollama正在运行: ollama serve")
        return False

    # 2. 创建AiEnhance系统
    print("\n2️⃣ 创建AiEnhance系统...")
    try:
        system = aienhance.create_system(
            system_type="educational",
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            llm_api_base="http://localhost:11434",
            llm_temperature=0.7,
            llm_max_tokens=500
        )
        print("   ✅ 系统创建成功")

        # 检查系统状态
        status = system.get_system_status()
        print(f"   📊 系统状态: 已初始化={status.get('initialized', False)}")

    except Exception as e:
        print(f"   ❌ 系统创建失败: {e}")
        return False

    # 3. 测试基础查询
    print("\n3️⃣ 测试基础查询功能...")
    test_queries = [
        "你好",
        "什么是人工智能？",
        "请用一句话解释机器学习"
    ]

    successful_tests = 0
    for i, query in enumerate(test_queries, 1):
        print(f"\n   测试 {i}: {query}")
        try:
            response = await system.process_query(
                query=query,
                user_id="test_user",
                context={"test_number": i}
            )

            if response.content:
                print(f"   ✅ 响应成功 ({len(response.content)}字符)")
                print(f"      内容预览: {response.content[:100]}...")
                successful_tests += 1

                # 显示处理信息
                if hasattr(response, 'processing_metadata'):
                    metadata = response.processing_metadata
                    steps = ' → '.join(metadata.get('processing_steps', []))
                    print(f"      处理步骤: {steps}")

                # 显示适配信息
                if hasattr(response, 'adaptation_info'):
                    adapt = response.adaptation_info
                    print(f"      适配参数: {adapt.density_level.value}密度, 负荷={adapt.cognitive_load:.2f}")

            else:
                print("   ⚠️ 无内容生成")

        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

    # 4. 测试结果统计
    print("\n4️⃣ 测试结果统计")
    print(f"   成功: {successful_tests}/{len(test_queries)}")

    if successful_tests == len(test_queries):
        print("   🎉 所有测试通过！")
        return True
    elif successful_tests > 0:
        print("   ⚠️ 部分测试通过")
        return True
    else:
        print("   ❌ 所有测试失败")
        return False


async def test_system_configurations():
    """测试不同系统配置"""
    print("\n🔧 系统配置测试")
    print("=" * 50)

    configurations = [
        {
            "name": "默认系统",
            "config": {
                "system_type": "default",
                "llm_provider": "ollama",
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.5
            }
        },
        {
            "name": "教育系统",
            "config": {
                "system_type": "educational",
                "llm_provider": "ollama",
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.3
            }
        },
        {
            "name": "研究系统",
            "config": {
                "system_type": "research",
                "llm_provider": "ollama",
                "llm_model_name": "qwen3:8b",
                "llm_temperature": 0.8
            }
        }
    ]

    test_query = "请解释深度学习"
    successful_configs = 0

    for config_info in configurations:
        print(f"\n🧪 测试 {config_info['name']}")
        try:
            system = aienhance.create_system(**config_info['config'])
            response = await system.process_query(
                query=test_query,
                user_id="config_test_user"
            )

            if response.content:
                print("   ✅ 配置工作正常")
                print(f"   📏 响应长度: {len(response.content)}字符")

                if hasattr(response, 'adaptation_info'):
                    adapt = response.adaptation_info
                    print(f"   ⚙️ 适配: {adapt.density_level.value}密度")

                successful_configs += 1
            else:
                print("   ⚠️ 无内容生成")

        except Exception as e:
            print(f"   ❌ 配置失败: {e}")

    print(f"\n📊 配置测试结果: {successful_configs}/{len(configurations)} 成功")
    return successful_configs > 0


async def main():
    """主测试函数"""
    print("🚀 AiEnhance + Ollama 集成测试开始")
    print("=" * 60)

    try:
        # 1. 基础集成测试
        basic_success = await test_ollama_integration()

        # 2. 配置测试
        config_success = await test_system_configurations()

        # 3. 总结
        print("\n" + "=" * 60)
        print("📋 测试总结")
        print("=" * 60)
        print(f"✅ 基础集成测试: {'通过' if basic_success else '失败'}")
        print(f"✅ 配置测试: {'通过' if config_success else '失败'}")

        if basic_success and config_success:
            print("\n🎉 所有测试通过！AiEnhance与Ollama集成成功")
            print("💡 现在可以使用以下方式启动完整系统:")
            print("   • python examples/quick_start.py")
            print("   • python demo_complete_system.py")
            return True
        else:
            print("\n⚠️ 部分测试失败，请检查配置")
            return False

    except Exception as e:
        print(f"\n❌ 测试过程出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
