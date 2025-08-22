#!/usr/bin/env python3
"""
简单的系统测试
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import aienhance


async def simple_test():
    """简单测试"""
    print("🧪 简单系统测试")

    # 1. 创建系统（不配置LLM）
    print("1. 创建基础系统...")
    system = aienhance.create_system("default")
    print("   ✅ 系统创建成功")

    # 2. 测试基础查询处理
    print("2. 测试基础查询...")
    response = await system.process_query(query="测试查询", user_id="test_user")
    print("   ✅ 查询处理完成")
    print(
        f"   📊 处理步骤: {' → '.join(response.processing_metadata.get('processing_steps', []))}"
    )
    print(f"   👤 用户画像: {response.user_profile.cognitive.thinking_mode.value}")
    print(f"   ⚙️ 适配信息: {response.adaptation_info.density_level.value}")

    # 3. 创建带LLM的系统（测试配置）
    print("3. 测试LLM配置...")
    try:
        llm_system = aienhance.create_system(
            system_type="educational", llm_provider="ollama", llm_model_name="qwen3:8b"
        )
        print("   ✅ LLM系统配置成功")

        status = llm_system.get_system_status()
        print(f"   📋 LLM状态: {status.get('llm_provider', 'None')}")

    except Exception as e:
        print(f"   ⚠️ LLM配置问题: {e}")

    print("🎉 简单测试完成")


if __name__ == "__main__":
    asyncio.run(simple_test())
