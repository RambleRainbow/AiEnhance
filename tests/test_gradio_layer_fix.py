#!/usr/bin/env python3
"""测试Gradio界面分层处理修复"""

import asyncio

from gradio_interface import LayeredSystemVisualizer


async def test_gradio_layer_processing():
    """测试Gradio界面的分层处理功能"""
    try:
        # 创建可视化器
        visualizer = LayeredSystemVisualizer()

        print("🔍 测试Gradio分层处理修复...")

        # 初始化系统
        result = await visualizer.initialize_system(
            "educational", "ollama", "qwen3:8b", 0.7
        )
        if "✅" in result:
            print("✅ 系统初始化成功")
        else:
            print(f"❌ 系统初始化失败: {result}")
            return False

        # 测试查询处理
        final_response, layer_outputs = await visualizer.process_query_with_layers(
            "什么是人工智能？"
        )

        if "❌" not in final_response:
            print("✅ 分层查询处理成功")
            print(f"📝 最终响应长度: {len(final_response)} 字符")
            print(f"📊 层输出数量: {len(layer_outputs)} 层")

            # 检查各层输出
            for layer_name, output in layer_outputs.items():
                if output and isinstance(output, dict):
                    print(f"  ✅ {layer_name}层: {len(output)} 个输出项")
                else:
                    print(f"  ⚠️ {layer_name}层: 输出为空或格式异常")

            return True
        else:
            print(f"❌ 分层查询处理失败: {final_response}")
            return False

    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_gradio_layer_processing())
    if result:
        print("\n🎉 Gradio分层处理修复测试通过！")
        print("现在可以正常使用Gradio界面的分层处理功能了。")
    else:
        print("\n❌ 测试失败，需要进一步调试。")
