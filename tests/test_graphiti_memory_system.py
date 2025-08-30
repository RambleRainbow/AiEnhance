#!/usr/bin/env python3
"""
Graphiti记忆系统集成测试
测试Graphiti适配器的完整功能，包括连接性、数据操作和搜索功能
"""

import asyncio
import datetime
import logging
from typing import Dict, Any

# 尝试导入pytest，如果不存在则跳过pytest相关功能
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # 定义基础的pytest替代标记
    class pytest:
        @staticmethod
        def fixture(func):
            return func
        
        @staticmethod
        def skip(reason):
            pass
        
        class mark:
            @staticmethod
            def asyncio(func):
                return func

from aienhance.config import Config
from aienhance.memory.interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemorySystemConfig,
    MemoryType,
    UserContext,
)
from aienhance.memory.adapters.graphiti_http_adapter import GraphitiHttpAdapter

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestGraphitiMemorySystem:
    """Graphiti记忆系统测试类"""
    
    @pytest.fixture
    async def graphiti_adapter(self):
        """创建测试用的Graphiti适配器"""
        config = MemorySystemConfig(
            system_type="graphiti_http",
            api_base_url=Config.GRAPHITI_API_URL
        )
        
        adapter = GraphitiHttpAdapter(config)
        
        # 初始化适配器
        init_success = await adapter.initialize()
        if not init_success:
            pytest.skip("Graphiti服务不可用，跳过测试")
        
        yield adapter
        
        # 清理
        await adapter.cleanup()
    
    @pytest.fixture
    def test_user_context(self):
        """创建测试用户上下文"""
        return UserContext(
            user_id="test_user_graphiti",
            session_id="test_session",
            metadata={"test_environment": True}
        )
    
    @pytest.mark.asyncio
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        config = MemorySystemConfig(
            system_type="graphiti_http",
            api_base_url=Config.GRAPHITI_API_URL
        )
        
        adapter = GraphitiHttpAdapter(config)
        
        # 测试初始化
        init_success = await adapter.initialize()
        assert init_success, "Graphiti适配器初始化应该成功"
        assert adapter.is_initialized, "适配器应该标记为已初始化"
        
        # 清理
        await adapter.cleanup()
        assert not adapter.is_initialized, "清理后适配器应该标记为未初始化"
    
    @pytest.mark.asyncio
    async def test_memory_operations(self, graphiti_adapter, test_user_context):
        """测试记忆操作功能"""
        
        # 测试添加记忆
        test_memory = MemoryEntry(
            content="这是一个用于pytest的测试记忆条目",
            memory_type=MemoryType.EPISODIC,
            user_context=test_user_context,
            timestamp=datetime.datetime.now(),
            confidence=1.0,
            metadata={"test_type": "pytest", "category": "integration"}
        )
        
        memory_id = await graphiti_adapter.add_memory(test_memory)
        assert memory_id, "添加记忆应该返回有效的ID"
        
        # 等待处理
        await asyncio.sleep(2)
        
        # 测试搜索记忆
        search_query = MemoryQuery(
            query="pytest测试",
            user_context=test_user_context,
            limit=5,
            similarity_threshold=0.1
        )
        
        search_result = await graphiti_adapter.search_memories(search_query)
        assert search_result is not None, "搜索应该返回结果对象"
        assert search_result.query_time >= 0, "查询时间应该为非负数"
        
        # 测试获取用户记忆
        user_memories = await graphiti_adapter.get_user_memories(test_user_context)
        assert user_memories is not None, "用户记忆查询应该返回结果"
        
        # 清理测试数据
        clear_success = await graphiti_adapter.clear_user_memories(test_user_context)
        assert clear_success, "清理用户记忆应该成功"


async def run_manual_test():
    """手动运行的完整测试 (非pytest)"""
    print("🧪 Graphiti记忆系统手动测试")
    print("=" * 50)
    
    # 创建配置和适配器
    config = MemorySystemConfig(
        system_type="graphiti_http",
        api_base_url=Config.GRAPHITI_API_URL
    )
    
    adapter = GraphitiHttpAdapter(config)
    
    try:
        # 初始化测试
        print("\n1️⃣ 适配器初始化测试")
        init_success = await adapter.initialize()
        print(f"   初始化状态: {'✅ 成功' if init_success else '❌ 失败'}")
        
        if not init_success:
            print("❌ 适配器初始化失败，停止测试")
            return False
        
        # 创建测试用户
        user_context = UserContext(
            user_id="manual_test_user",
            session_id="manual_session",
            metadata={"manual_test": True}
        )
        
        # 记忆操作测试
        print("\n2️⃣ 记忆操作测试")
        test_memories = [
            "我喜欢使用Python进行数据分析和机器学习",
            "Graphiti是一个强大的图数据库记忆系统",
            "Neo4j提供了excellent的图查询能力"
        ]
        
        memory_ids = []
        for i, content in enumerate(test_memories):
            memory = MemoryEntry(
                content=content,
                memory_type=MemoryType.SEMANTIC,
                user_context=user_context,
                timestamp=datetime.datetime.now(),
                confidence=1.0,
                metadata={"test_index": i}
            )
            
            try:
                memory_id = await adapter.add_memory(memory)
                memory_ids.append(memory_id)
                print(f"   记忆{i+1}: ✅ 已添加 (ID: {memory_id[:20]}...)")
            except Exception as e:
                print(f"   记忆{i+1}: ❌ 失败 ({e})")
        
        # 等待处理
        print("\n3️⃣ 等待记忆处理...")
        await asyncio.sleep(3)
        
        # 搜索测试
        print("\n4️⃣ 搜索功能测试")
        search_queries = ["Python", "Graphiti", "数据分析", "图数据库"]
        
        successful_searches = 0
        for query in search_queries:
            try:
                search_query = MemoryQuery(
                    query=query,
                    user_context=user_context,
                    limit=5,
                    similarity_threshold=0.0
                )
                
                result = await adapter.search_memories(search_query)
                if result.total_count > 0:
                    successful_searches += 1
                    print(f"   '{query}': ✅ {result.total_count}个结果")
                else:
                    print(f"   '{query}': ⚠️  无结果")
                    
            except Exception as e:
                print(f"   '{query}': ❌ 搜索失败 ({e})")
        
        print(f"\n   搜索成功率: {successful_searches}/{len(search_queries)}")
        
        # 清理测试数据
        print("\n5️⃣ 清理测试数据")
        try:
            clear_success = await adapter.clear_user_memories(user_context)
            print(f"   清理状态: {'✅ 成功' if clear_success else '❌ 失败'}")
        except Exception as e:
            print(f"   清理失败: {e}")
        
        print("\n✅ 手动测试完成")
        return True
        
    finally:
        await adapter.cleanup()


async def main():
    """主函数 - 用于直接运行测试"""
    await run_manual_test()


if __name__ == "__main__":
    asyncio.run(main())