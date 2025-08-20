#!/usr/bin/env python3
"""
测试MIRIX SDK集成
验证新的MIRIX SDK适配器是否正常工作
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aienhance.memory.adapters.mirix_sdk_adapter import MirixSdkAdapter
from aienhance.memory.interfaces import (
    MemorySystemConfig, UserContext, MemoryEntry, 
    MemoryQuery, MemoryType
)


class MirixSdkTester:
    """MIRIX SDK测试器"""
    
    def __init__(self):
        self.adapter = None
        
    async def test_initialization(self):
        """测试初始化"""
        print("🔧 测试MIRIX SDK初始化...")
        
        # 检查API密钥
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ 未设置GOOGLE_API_KEY环境变量")
            print("💡 请设置: export GOOGLE_API_KEY='your-api-key'")
            return False
        
        # 配置适配器
        config = MemorySystemConfig(api_key=api_key)
        self.adapter = MirixSdkAdapter(config)
        
        # 初始化
        try:
            success = await self.adapter.initialize()
            if success:
                print("✅ MIRIX SDK初始化成功")
                return True
            else:
                print("❌ MIRIX SDK初始化失败")
                return False
        except Exception as e:
            print(f"❌ 初始化异常: {e}")
            return False
    
    async def test_memory_operations(self):
        """测试记忆操作"""
        print("\n📝 测试记忆操作...")
        
        if not self.adapter or not self.adapter.is_initialized:
            print("❌ 适配器未初始化")
            return False
        
        user_context = UserContext(
            user_id="test_user_sdk",
            session_id="test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        
        try:
            # 测试添加记忆
            print("  ➡️ 添加测试记忆...")
            test_memory = MemoryEntry(
                content="这是一个MIRIX SDK集成测试。用户喜欢学习人工智能和机器学习。",
                memory_type=MemoryType.SEMANTIC,
                user_context=user_context,
                timestamp=datetime.now(),
                metadata={"test": True, "version": "sdk"}
            )
            
            memory_id = await self.adapter.add_memory(test_memory)
            print(f"  ✅ 记忆已添加，ID: {memory_id}")
            
            # 测试搜索记忆
            print("  🔍 搜索相关记忆...")
            query = MemoryQuery(
                query="人工智能学习",
                user_context=user_context,
                limit=5
            )
            
            search_result = await self.adapter.search_memories(query)
            print(f"  ✅ 找到 {len(search_result.memories)} 条相关记忆")
            print(f"  ⏱️ 查询时间: {search_result.query_time:.2f}秒")
            
            if search_result.memories:
                print("  📋 记忆内容预览:")
                for i, memory in enumerate(search_result.memories[:2], 1):
                    preview = memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
                    print(f"    {i}. {preview}")
            
            return True
            
        except Exception as e:
            print(f"❌ 记忆操作失败: {e}")
            return False
    
    async def test_chat_functionality(self):
        """测试对话功能"""
        print("\n💬 测试对话功能...")
        
        if not self.adapter or not self.adapter.is_initialized:
            print("❌ 适配器未初始化")
            return False
        
        user_context = UserContext(
            user_id="test_user_sdk",
            session_id="chat_test_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        
        try:
            # 测试带记忆的对话
            test_message = "请告诉我关于机器学习的基础概念"
            print(f"  👤 用户: {test_message}")
            print("  🤔 AI思考中...")
            
            response = await self.adapter.chat_with_memory(
                message=test_message,
                user_context=user_context,
                save_interaction=True
            )
            
            print(f"  🤖 AI: {response[:200]}..." if len(response) > 200 else f"  🤖 AI: {response}")
            print("  ✅ 对话功能正常")
            
            return True
            
        except Exception as e:
            print(f"❌ 对话功能失败: {e}")
            return False
    
    async def test_system_info(self):
        """测试系统信息"""
        print("\n📊 测试系统信息...")
        
        if not self.adapter:
            print("❌ 适配器未创建")
            return False
        
        try:
            info = self.adapter.get_system_info()
            print("  ✅ 系统信息:")
            print(f"    系统类型: {info['system_type']}")
            print(f"    初始化状态: {info['initialized']}")
            print(f"    功能特性: {', '.join(k for k, v in info['features'].items() if v)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取系统信息失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        if self.adapter:
            await self.adapter.cleanup()
            print("🧹 资源已清理")


async def main():
    """主测试函数"""
    print("🚀 MIRIX SDK 集成测试")
    print("=" * 50)
    
    tester = MirixSdkTester()
    
    try:
        # 运行测试
        tests = [
            ("初始化测试", tester.test_initialization),
            ("记忆操作测试", tester.test_memory_operations),
            ("对话功能测试", tester.test_chat_functionality),
            ("系统信息测试", tester.test_system_info),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name}异常: {e}")
                results.append((test_name, False))
        
        # 显示测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{len(results)} 个测试通过")
        
        if passed == len(results):
            print("🎉 所有测试通过！MIRIX SDK集成成功！")
        else:
            print("⚠️ 部分测试失败，请检查配置和网络连接")
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试已中断")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")