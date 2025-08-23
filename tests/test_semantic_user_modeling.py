#!/usr/bin/env python3
"""
测试新的基于LLM的语义用户建模功能
"""

import asyncio
import logging
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath("."))

from aienhance.enhanced_system_factory import create_layered_system
from aienhance.llm.interfaces import create_model_config
from aienhance.memory.interfaces import MemorySystemConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_semantic_user_modeling():
    """测试语义用户建模功能"""

    print("🚀 启动语义用户建模测试")
    print("=" * 60)

    try:
        # 1. 创建系统配置
        print("1. 创建系统配置...")

        # LLM配置 - 使用本地Ollama
        llm_config = create_model_config(
            provider="ollama",
            model_name="qwen3:8b",
            api_base="http://localhost:11434",
            temperature=0.3,
            max_tokens=800,
        )

        # 记忆系统配置 - 使用MIRIX统一模式
        memory_config = MemorySystemConfig(system_type="mirix_unified")

        # 创建分层认知系统
        print("2. 创建分层认知系统（使用语义用户建模）...")
        system = create_layered_system(
            system_type="educational",
            memory_config=memory_config,
            llm_config=llm_config,
        )

        # 初始化系统
        print("3. 初始化系统...")
        success = await system.initialize_layers()
        if not success:
            print("❌ 系统初始化失败")
            return

        print("✅ 系统初始化成功")

        # 4. 准备测试数据
        test_queries = [
            {
                "user_id": "test_user_1",
                "query": "请详细解释深度学习中的注意力机制原理，我想从数学原理到实际应用都了解清楚。",
                "context": {"domain": "technical", "urgency": "medium"},
                "description": "技术深度学习查询",
            },
            {
                "user_id": "test_user_2",
                "query": "能否简单说明一下什么是人工智能？我是初学者。",
                "context": {"domain": "educational", "urgency": "low"},
                "description": "初学者教育查询",
            },
            {
                "user_id": "test_user_3",
                "query": "我想要设计一个创新的用户界面，能帮我brainstorm一些前沿的交互概念吗？",
                "context": {"domain": "creative", "urgency": "high"},
                "description": "创意设计查询",
            },
        ]

        print("\n4. 执行语义用户建模测试...")
        print("-" * 60)

        for i, test_case in enumerate(test_queries, 1):
            print(f"\n测试案例 {i}: {test_case['description']}")
            print(f"查询: {test_case['query'][:50]}...")

            try:
                # 处理查询并生成用户画像
                response = await system.process_through_layers(
                    query=test_case["query"],
                    user_id=test_case["user_id"],
                    context=test_case["context"],
                )

                if response.status == "success":
                    # 分析生成的用户画像
                    user_profile = response.perception_output.user_profile

                    print("✅ 用户画像生成成功:")
                    print(f"   认知特征: {user_profile.cognitive_characteristics}")
                    print(f"   知识领域: {user_profile.knowledge_profile}")
                    print(f"   交互偏好: {user_profile.interaction_preferences}")

                    # 检查是否使用了语义分析
                    perception_meta = response.perception_output.metadata
                    if "语义分析" in str(perception_meta):
                        print("   🧠 使用了LLM语义分析")
                    else:
                        print("   📝 使用了传统规则分析")

                    # 显示最终响应
                    print(f"   最终响应: {response.final_response[:100]}...")

                else:
                    print(f"❌ 处理失败: {response.error_message}")

            except Exception as e:
                print(f"❌ 测试案例执行失败: {e}")

        # 5. 测试用户画像更新功能
        print(f"\n5. 测试用户画像增量更新...")
        print("-" * 60)

        try:
            # 为第一个用户添加更多交互数据
            update_query = (
                "现在我想了解transformer架构的具体实现细节，包括多头注意力的计算过程。"
            )

            response = await system.process_through_layers(
                query=update_query,
                user_id="test_user_1",
                context={"domain": "technical", "follow_up": True},
            )

            if response.status == "success":
                updated_profile = response.perception_output.user_profile
                print("✅ 用户画像更新成功")
                print(
                    f"   更新后认知复杂度: {updated_profile.cognitive_characteristics.get('cognitive_complexity', 'N/A')}"
                )
                print(f"   更新后知识深度: {updated_profile.knowledge_profile}")
            else:
                print("❌ 用户画像更新失败")

        except Exception as e:
            print(f"❌ 用户画像更新测试失败: {e}")

        # 6. 系统信息统计
        print(f"\n6. 系统统计信息...")
        print("-" * 60)

        try:
            system_status = system.get_system_status()
            print(
                f"处理查询总数: {system_status['processing_statistics']['total_queries']}"
            )
            print(
                f"成功查询数量: {system_status['processing_statistics']['successful_queries']}"
            )
            print(
                f"平均处理时间: {system_status['processing_statistics']['average_processing_time']:.3f}s"
            )

            # 显示感知层状态
            perception_status = system.perception_layer.get_status()
            print(f"用户画像数量: {perception_status['user_profiles_count']}")

            if (
                system.perception_layer.user_modeler
                and system.perception_layer.user_modeler.modeler_type == "semantic"
            ):
                print("✅ 使用语义分析用户建模")
            else:
                print("📝 使用传统规则用户建模")

        except Exception as e:
            print(f"⚠️ 无法获取系统统计: {e}")

    except Exception as e:
        print(f"❌ 测试过程发生错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # 清理资源
        try:
            if "system" in locals():
                await system.cleanup()
                print("\n✅ 系统资源清理完成")
        except Exception as e:
            print(f"⚠️ 资源清理时出现问题: {e}")


def main():
    """主函数"""
    print("🔬 语义用户建模系统测试")
    print("测试LLM驱动的用户画像生成vs传统规则匹配方法")
    print()

    # 检查环境
    if not os.path.exists("aienhance"):
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)

    # 运行异步测试
    try:
        asyncio.run(test_semantic_user_modeling())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")


if __name__ == "__main__":
    main()
