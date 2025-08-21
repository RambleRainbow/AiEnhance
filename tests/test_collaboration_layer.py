#!/usr/bin/env python3
"""
协作层测试脚本
测试辩证视角生成、认知挑战等功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aienhance.collaboration import (
    ChallengeRequest,
    ChallengeType,
    CognitiveChallenge,
    CollaborationContext,
    CollaborativeCoordinator,
    DialecticalPerspectiveGenerator,
    PerspectiveRequest,
    PerspectiveType,
)
from aienhance.llm import LLMProviderFactory
from aienhance.llm.interfaces import ModelConfig, ModelType


async def test_dialectical_perspective():
    """测试辩证视角生成"""
    print("=" * 60)
    print("🎭 测试辩证视角生成")
    print("=" * 60)

    try:
        # 创建LLM提供商（使用ollama作为测试）
        llm_config = ModelConfig(
            provider="ollama",
            model_name="qwen3:8b",
            model_type=ModelType.CHAT,
            api_base="http://localhost:11434",
            temperature=0.7
        )

        llm_provider = LLMProviderFactory.create_provider(llm_config)
        await llm_provider.initialize()

        # 创建视角生成器
        perspective_generator = DialecticalPerspectiveGenerator(llm_provider)

        # 测试内容
        test_content = "人工智能将会完全替代人类的工作，这是技术发展的必然趋势。"

        # 创建协作上下文
        context = CollaborationContext(
            user_id="test_user",
            session_id="test_session"
        )

        # 创建视角请求
        request = PerspectiveRequest(
            content=test_content,
            user_position="支持AI替代人类工作",
            perspective_types=[PerspectiveType.OPPOSING, PerspectiveType.MULTI_DISCIPLINARY],
            max_perspectives=3
        )

        # 生成视角
        print(f"📝 分析内容: {test_content}")
        print("🔄 生成多元视角...")

        result = await perspective_generator.generate_perspectives(request, context)

        print(f"\n🎯 生成了 {len(result.perspectives)} 个视角:")

        for i, perspective in enumerate(result.perspectives, 1):
            print(f"\n{i}. {perspective.title}")
            print(f"   类型: {perspective.perspective_type.value}")
            print(f"   描述: {perspective.description}")
            print("   关键论据:")
            for j, arg in enumerate(perspective.key_arguments, 1):
                print(f"     {j}) {arg}")
            print(f"   相关性评分: {perspective.relevance_score:.2f}")

        if result.synthesis:
            print("\n🔄 综合分析:")
            print(result.synthesis)

        if result.dialectical_tensions:
            print("\n⚡ 辩证冲突点:")
            for tension in result.dialectical_tensions:
                print(f"   • {tension}")

        print("✅ 辩证视角生成测试完成")
        return True

    except Exception as e:
        print(f"❌ 辩证视角生成测试失败: {e}")
        return False


async def test_cognitive_challenge():
    """测试认知挑战"""
    print("\n" + "=" * 60)
    print("🧠 测试认知挑战")
    print("=" * 60)

    try:
        # 创建LLM提供商
        llm_config = ModelConfig(
            provider="ollama",
            model_name="qwen3:8b",
            model_type=ModelType.CHAT,
            api_base="http://localhost:11434",
            temperature=0.7
        )

        llm_provider = LLMProviderFactory.create_provider(llm_config)
        await llm_provider.initialize()

        # 创建认知挑战器
        cognitive_challenger = CognitiveChallenge(llm_provider)

        # 测试内容
        test_content = "远程工作提高了员工的工作效率，应该成为所有公司的标准做法。"
        user_reasoning = "因为员工可以避免通勤时间，有更好的工作环境，所以效率更高。"

        # 创建协作上下文
        context = CollaborationContext(
            user_id="test_user",
            session_id="test_session"
        )

        # 创建挑战请求
        request = ChallengeRequest(
            content=test_content,
            user_reasoning=user_reasoning,
            challenge_types=[
                ChallengeType.ASSUMPTION_QUESTIONING,
                ChallengeType.BLIND_SPOT_DETECTION,
                ChallengeType.COMPLEXITY_EXPANSION
            ],
            intensity_level="moderate"
        )

        # 生成挑战
        print(f"📝 分析内容: {test_content}")
        print(f"🤔 用户推理: {user_reasoning}")
        print("🔄 生成认知挑战...")

        result = await cognitive_challenger.generate_challenges(request, context)

        print(f"\n🎯 生成了 {len(result.challenges)} 个认知挑战:")

        for i, challenge in enumerate(result.challenges, 1):
            print(f"\n{i}. {challenge.title}")
            print(f"   类型: {challenge.challenge_type.value}")
            print(f"   描述: {challenge.description}")
            print("   挑战性问题:")
            for j, question in enumerate(challenge.questions, 1):
                print(f"     {j}) {question}")

            if challenge.alternative_frameworks:
                print(f"   替代框架: {', '.join(challenge.alternative_frameworks)}")

        if result.meta_reflection:
            print("\n🤯 元认知反思:")
            print(result.meta_reflection)

        if result.growth_opportunities:
            print("\n🌱 成长机会:")
            for opportunity in result.growth_opportunities:
                print(f"   • {opportunity}")

        print("✅ 认知挑战测试完成")
        return True

    except Exception as e:
        print(f"❌ 认知挑战测试失败: {e}")
        return False


async def test_collaborative_coordinator():
    """测试协作协调器"""
    print("\n" + "=" * 60)
    print("🤝 测试协作协调器")
    print("=" * 60)

    try:
        # 创建LLM提供商
        llm_config = ModelConfig(
            provider="ollama",
            model_name="qwen3:8b",
            model_type=ModelType.CHAT,
            api_base="http://localhost:11434",
            temperature=0.7
        )

        llm_provider = LLMProviderFactory.create_provider(llm_config)
        await llm_provider.initialize()

        # 创建协作协调器
        coordinator = CollaborativeCoordinator(llm_provider)

        # 测试内容
        test_content = "区块链技术将彻底改变金融行业，传统银行将失去存在的意义。"

        # 创建协作上下文
        context = CollaborationContext(
            user_id="test_user",
            session_id="test_session",
            collaboration_preferences={
                "enable_perspectives": True,
                "enable_challenges": True,
                "challenge_intensity": "moderate"
            }
        )

        # 编排协作过程
        print(f"📝 分析内容: {test_content}")
        print("🔄 编排协作过程...")

        result = await coordinator.orchestrate_collaboration(test_content, context)

        print("\n🎯 协作结果:")
        print(f"   时间戳: {result.get('timestamp')}")
        print(f"   用户ID: {result.get('user_id')}")

        # 显示视角结果
        perspectives = result.get('perspectives')
        if perspectives and not perspectives.get('error'):
            print(f"\n🎭 生成视角: {len(perspectives.get('perspectives', []))} 个")
            for i, p in enumerate(perspectives.get('perspectives', []), 1):
                print(f"   {i}. {p.get('title', 'N/A')}")

        # 显示挑战结果
        challenges = result.get('challenges')
        if challenges and not challenges.get('error'):
            print(f"\n🧠 认知挑战: {len(challenges.get('challenges', []))} 个")
            for i, c in enumerate(challenges.get('challenges', []), 1):
                print(f"   {i}. {c.get('title', 'N/A')}")

        # 显示协作洞察
        insights = result.get('collaboration_insights')
        if insights:
            print("\n💡 协作洞察:")
            print(f"   协作效果: {insights.get('collaboration_effectiveness', 'N/A')}")
            print(f"   学习机会: {insights.get('learning_opportunities', [])}")
            print(f"   个性化建议: {insights.get('personalized_recommendations', [])}")

        # 显示下一步建议
        next_steps = result.get('next_collaboration_steps')
        if next_steps:
            print("\n🚀 下一步建议:")
            for step in next_steps:
                print(f"   • {step}")

        print("✅ 协作协调器测试完成")
        return True

    except Exception as e:
        print(f"❌ 协作协调器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 协作层功能测试开始")
    print("=" * 60)

    results = []

    # 检查Ollama是否可用
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            if response.status_code != 200:
                print("❌ Ollama服务不可用，请先启动Ollama")
                return
    except Exception as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        print("请确保Ollama正在运行: docker compose up -d ollama")
        return

    # 执行测试
    tests = [
        ("辩证视角生成", test_dialectical_perspective),
        ("认知挑战", test_cognitive_challenge),
        ("协作协调器", test_collaborative_coordinator)
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n⏹️ 测试被用户中断")
            break
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results.append((test_name, False))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有协作层功能测试通过！")
        print("\n💡 协作层已成功实现，包括:")
        print("   • 辩证视角生成 (多学科视角、对立观点)")
        print("   • 认知挑战 (假设质疑、盲点检测、复杂性扩展)")
        print("   • 协作协调 (整体编排、用户建模、适应性调整)")
    else:
        print("⚠️ 部分测试失败，请检查实现")


if __name__ == "__main__":
    asyncio.run(main())
