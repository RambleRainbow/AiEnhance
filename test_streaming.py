#!/usr/bin/env python3
"""
测试LLM流式调用功能
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

import aienhance

def setup_logging():
    """设置日志配置"""
    log_level = "INFO"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    
    # 设置 aienhance 模块的日志级别
    aienhance_logger = logging.getLogger('aienhance')
    aienhance_logger.setLevel(getattr(logging, log_level))
    
    return logging.getLogger(__name__)

logger = setup_logging()

async def test_streaming():
    """测试流式功能"""
    print("🧪 测试LLM流式调用功能")
    print("=" * 60)
    
    try:
        # 创建系统
        logger.info("创建教育系统...")
        system = aienhance.create_educational_system(
            llm_provider="ollama",
            llm_model_name="qwen3:8b",
            memory_provider="none",  # 简化测试，不使用记忆系统
            config={
                "temperature": 0.7,
                "max_tokens": None,  # 无长度限制
                "ollama_base_url": "http://localhost:11434",
            }
        )
        
        # 初始化
        logger.info("初始化系统...")
        success = await system.initialize()
        if not success:
            print("❌ 系统初始化失败")
            return
            
        print("✅ 系统初始化成功，开始测试流式响应...")
        
        # 测试问题
        test_query = "请详细解释什么是机器学习，包括其主要类型、应用场景和发展趋势"
        
        print(f"\n📝 测试问题: {test_query}")
        print("\n🔄 开始流式处理...")
        print("-" * 60)
        
        # 处理查询
        result = await system.process(
            user_id="test_user",
            query=test_query,
            session_context={"test_mode": True}
        )
        
        print("-" * 60)
        
        if result.success:
            print("✅ 流式处理完成")
            print(f"📊 处理结果长度: {len(str(result.data))}")
            
            # 显示最终响应
            final_response = result.data.get("layer_outputs", {}).get("behavior", {}).get("adapted_response", {})
            if final_response:
                response_content = final_response.get("response_content", "无响应内容")
                print(f"📝 最终响应长度: {len(response_content)}")
                print(f"🎯 响应预览: {response_content[:200]}...")
            else:
                print("⚠️ 未找到最终响应")
                
        else:
            print(f"❌ 处理失败: {result.error_message}")
            
    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_streaming())
    except KeyboardInterrupt:
        print("\n👋 测试中断")
    except Exception as e:
        print(f"❌ 测试错误: {e}")