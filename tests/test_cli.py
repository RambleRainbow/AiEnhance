#!/usr/bin/env python3
"""
简化测试版本的CLI工具
用于验证修复后的参数配置
"""

import asyncio

import aienhance


async def main():
    print("🔍 测试修复后的参数配置...")

    try:
        # 测试简化版本（无记忆系统）
        print("📝 创建简化系统（仅LLM）...")
        system = aienhance.create_system(
            system_type="educational",
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            llm_temperature=0.7,
            llm_max_tokens=800,
        )
        print("✅ 简化系统创建成功")

        # 测试查询
        print("🤔 测试查询处理...")
        async with system:
            response = await system.process_query(
                query="你好，请简单介绍一下自己",
                user_id="test_user",
                context={"source": "test"},
            )

            print("\n" + "=" * 50)
            print("🤖 AI回答:")
            print("=" * 50)
            print(response.content)
            print("\n✅ 测试成功！参数修复已生效")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
