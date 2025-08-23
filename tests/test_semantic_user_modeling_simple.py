#!/usr/bin/env python3
"""
简单的语义用户建模功能测试
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath("."))

from aienhance.perception.semantic_user_modeler import SemanticUserModeler
from aienhance.llm.adapters.ollama_adapter import OllamaLLMAdapter
from aienhance.llm.interfaces import ModelConfig


async def test_simple_user_modeling():
    """简单的用户建模测试"""
    print("🧠 测试基于LLM的语义用户建模")
    print("=" * 50)

    try:
        # 1. 创建LLM提供商
        print("1. 创建LLM提供商...")
        config = ModelConfig(
            provider="ollama",
            model_name="qwen3:8b",
            api_base="http://localhost:11434",
            temperature=0.3,
            max_tokens=500,
        )

        llm_provider = OllamaLLMAdapter(config)
        await llm_provider.initialize()
        print("✅ LLM提供商初始化成功")

        # 2. 创建语义用户建模器
        print("2. 创建语义用户建模器...")
        modeler = SemanticUserModeler(llm_provider)
        print("✅ 语义用户建模器创建成功")

        # 3. 测试用户画像创建
        print("3. 测试用户画像创建...")

        test_data = {
            "query": "请详细解释深度学习中的注意力机制原理，包括数学公式和代码实现。",
            "memory_context": [
                {"content": "什么是机器学习？", "metadata": {"type": "user_query"}},
                {
                    "content": "解释一下神经网络的反向传播算法",
                    "metadata": {"type": "user_query"},
                },
                {
                    "content": "PyTorch中如何实现卷积神经网络？",
                    "metadata": {"type": "user_query"},
                },
            ],
        }

        print(f"用户查询: {test_data['query']}")
        print("历史记录: 3条技术相关查询")

        # 创建用户画像
        user_profile = await modeler.create_user_profile("test_user", test_data)

        print("\n✅ 用户画像创建成功!")
        print(f"认知特征:")
        print(f"  思维模式: {user_profile.cognitive.thinking_mode.value}")
        print(f"  认知复杂度: {user_profile.cognitive.cognitive_complexity:.2f}")
        print(f"  抽象思维: {user_profile.cognitive.abstraction_level:.2f}")
        print(f"  创造性: {user_profile.cognitive.creativity_tendency:.2f}")

        print(f"知识结构:")
        print(f"  核心领域: {user_profile.knowledge.core_domains}")
        print(f"  知识深度: {user_profile.knowledge.knowledge_depth}")
        print(f"  跨域能力: {user_profile.knowledge.cross_domain_ability:.2f}")

        print(f"交互偏好:")
        print(f"  认知风格: {user_profile.interaction.cognitive_style.value}")
        print(
            f"  信息密度偏好: {user_profile.interaction.information_density_preference:.2f}"
        )
        print(f"  处理速度: {user_profile.interaction.processing_speed:.2f}")

        # 4. 测试不同领域的用户建模
        print("\n4. 测试不同领域的用户建模...")

        creative_data = {
            "query": "我想设计一个创新的艺术装置，能给我一些灵感吗？",
            "memory_context": [
                {
                    "content": "最新的数字艺术趋势有哪些？",
                    "metadata": {"type": "user_query"},
                },
                {
                    "content": "如何用AI生成抽象艺术？",
                    "metadata": {"type": "user_query"},
                },
            ],
        }

        creative_profile = await modeler.create_user_profile(
            "creative_user", creative_data
        )

        print("🎨 创意用户画像:")
        print(f"  思维模式: {creative_profile.cognitive.thinking_mode.value}")
        print(f"  核心领域: {creative_profile.knowledge.core_domains}")
        print(f"  创造性倾向: {creative_profile.cognitive.creativity_tendency:.2f}")

        print("\n✅ 语义用户建模测试完成!")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


def main():
    """主函数"""
    print("🔬 简单语义用户建模测试")
    print("测试LLM驱动的用户画像生成功能")
    print()

    # 运行测试
    try:
        asyncio.run(test_simple_user_modeling())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")


if __name__ == "__main__":
    main()
