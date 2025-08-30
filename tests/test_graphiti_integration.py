#!/usr/bin/env python3
"""
Graphiti API 测试程序
测试Graphiti服务的连接性和基本功能
"""

import asyncio
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config
from aienhance.memory.interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemorySystemConfig,
    MemoryType,
    UserContext,
)
from aienhance.memory.adapters.graphiti_http_adapter import GraphitiHttpAdapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GraphitiAPITester:
    """Graphiti API测试器"""
    
    def __init__(self):
        self.api_url = Config.GRAPHITI_API_URL
        self.session = None
        self.test_user_id = "test_user_001"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_health_check(self) -> bool:
        """测试健康检查接口"""
        print("\n🔍 测试1: Graphiti服务健康检查")
        try:
            async with self.session.get(f"{self.api_url}/healthcheck") as response:
                status_code = response.status
                response_text = await response.text()
                
                print(f"   状态码: {status_code}")
                print(f"   响应内容: {response_text}")
                
                if status_code == 200:
                    print("   ✅ 健康检查通过")
                    return True
                else:
                    print("   ❌ 健康检查失败")
                    return False
                    
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            return False

    async def test_direct_api_endpoints(self) -> Dict[str, Any]:
        """直接测试API端点"""
        print("\n🔍 测试2: 直接API端点测试")
        results = {}
        
        # 测试根端点
        try:
            async with self.session.get(f"{self.api_url}/") as response:
                print(f"   根端点状态: {response.status}")
                results["root_endpoint"] = response.status == 200
        except Exception as e:
            print(f"   根端点错误: {e}")
            results["root_endpoint"] = False

        # 测试messages端点 (POST)
        test_message = {
            "group_id": self.test_user_id,
            "messages": [
                {
                    "content": "这是一个测试消息",
                    "role_type": "user", 
                    "role": self.test_user_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source_description": "API连接测试"
                }
            ]
        }
        
        try:
            async with self.session.post(
                f"{self.api_url}/messages",
                json=test_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Messages端点状态: {response.status}")
                if response.status in [200, 202]:
                    response_data = await response.json()
                    print(f"   Messages响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                    results["messages_endpoint"] = True
                else:
                    error_text = await response.text()
                    print(f"   Messages端点错误: {error_text}")
                    results["messages_endpoint"] = False
        except Exception as e:
            print(f"   Messages端点异常: {e}")
            results["messages_endpoint"] = False

        # 测试search端点
        search_payload = {
            "query": "测试",
            "group_ids": [self.test_user_id],
            "max_facts": 5
        }
        
        try:
            async with self.session.post(
                f"{self.api_url}/search",
                json=search_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"   Search端点状态: {response.status}")
                if response.status == 200:
                    search_results = await response.json()
                    print(f"   Search结果数量: {len(search_results) if isinstance(search_results, list) else '未知'}")
                    results["search_endpoint"] = True
                else:
                    error_text = await response.text()
                    print(f"   Search端点错误: {error_text}")
                    results["search_endpoint"] = False
        except Exception as e:
            print(f"   Search端点异常: {e}")
            results["search_endpoint"] = False
            
        return results

    async def test_adapter_integration(self) -> Dict[str, Any]:
        """测试通过适配器的集成"""
        print("\n🔍 测试3: Graphiti适配器集成测试")
        results = {}
        
        # 创建配置
        config = MemorySystemConfig(
            system_type="graphiti_http",
            api_base_url=self.api_url
        )
        
        # 创建适配器
        adapter = GraphitiHttpAdapter(config)
        
        try:
            # 初始化适配器
            init_success = await adapter.initialize()
            print(f"   适配器初始化: {'✅ 成功' if init_success else '❌ 失败'}")
            results["adapter_init"] = init_success
            
            if not init_success:
                return results
            
            # 创建测试用户上下文
            user_context = UserContext(
                user_id=self.test_user_id,
                session_id="test_session_001",
                agent_id="test_agent",
                metadata={"test": True, "testing": True}
            )
            
            # 测试添加记忆
            test_memory = MemoryEntry(
                content="这是一个测试记忆条目，用于验证Graphiti API功能",
                memory_type=MemoryType.EPISODIC,
                user_context=user_context,
                timestamp=datetime.datetime.now(),
                confidence=1.0,
                metadata={"test_type": "api_connectivity"}
            )
            
            try:
                memory_id = await adapter.add_memory(test_memory)
                print(f"   记忆添加: ✅ 成功 (ID: {memory_id})")
                results["add_memory"] = True
                results["memory_id"] = memory_id
            except Exception as e:
                print(f"   记忆添加: ❌ 失败 ({e})")
                results["add_memory"] = False
            
            # 测试搜索记忆 
            search_query = MemoryQuery(
                query="测试记忆",
                user_context=user_context,
                limit=10,
                similarity_threshold=0.1
            )
            
            try:
                search_result = await adapter.search_memories(search_query)
                print(f"   记忆搜索: ✅ 成功")
                print(f"   搜索结果数量: {search_result.total_count}")
                print(f"   查询时间: {search_result.query_time:.3f}秒")
                
                if search_result.memories:
                    print(f"   首个结果内容: {search_result.memories[0].content[:50]}...")
                
                results["search_memory"] = True
                results["search_count"] = search_result.total_count
            except Exception as e:
                print(f"   记忆搜索: ❌ 失败 ({e})")
                results["search_memory"] = False
            
            # 测试获取用户记忆
            try:
                user_memories = await adapter.get_user_memories(user_context, limit=5)
                print(f"   用户记忆获取: ✅ 成功")
                print(f"   用户记忆数量: {user_memories.total_count}")
                results["get_user_memories"] = True
            except Exception as e:
                print(f"   用户记忆获取: ❌ 失败 ({e})")
                results["get_user_memories"] = False
            
        finally:
            # 清理资源
            await adapter.cleanup()
            print("   🧹 适配器资源已清理")
            
        return results

    async def test_service_availability(self) -> Dict[str, Any]:
        """测试服务可用性"""
        print("\n🔍 测试4: 服务可用性检查")
        results = {}
        
        # 检查Graphiti服务
        try:
            async with self.session.get(f"{self.api_url}/healthcheck", timeout=5) as response:
                results["graphiti_service"] = response.status == 200
                print(f"   Graphiti服务: {'✅ 运行中' if results['graphiti_service'] else '❌ 不可用'}")
        except Exception as e:
            results["graphiti_service"] = False
            print(f"   Graphiti服务: ❌ 连接失败 ({e})")
        
        # 检查Neo4j (如果可访问)
        neo4j_url = "http://localhost:7474"
        try:
            async with self.session.get(neo4j_url, timeout=5) as response:
                results["neo4j_browser"] = response.status == 200
                print(f"   Neo4j浏览器: {'✅ 可访问' if results['neo4j_browser'] else '❌ 不可访问'}")
        except Exception as e:
            results["neo4j_browser"] = False
            print(f"   Neo4j浏览器: ❌ 连接失败")
            
        return results

    def print_test_summary(self, all_results: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "="*60)
        print("📊 GRAPHITI API 测试报告")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_results in all_results.items():
            print(f"\n🔸 {test_name.upper()}:")
            if isinstance(test_results, dict):
                for key, value in test_results.items():
                    total_tests += 1
                    if value:
                        passed_tests += 1
                        print(f"   ✅ {key}: 通过")
                    else:
                        print(f"   ❌ {key}: 失败")
            else:
                total_tests += 1
                if test_results:
                    passed_tests += 1
                    print(f"   ✅ 通过")
                else:
                    print(f"   ❌ 失败")
        
        print(f"\n📈 总体结果: {passed_tests}/{total_tests} 测试通过")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！Graphiti API运行正常")
        elif passed_tests > 0:
            print("⚠️  部分测试通过，可能存在配置问题")
        else:
            print("🚨 所有测试失败，请检查Graphiti服务状态")
            
        print("\n🛠️  故障排除建议:")
        print("   • 确保Docker服务运行: docker-compose up -d")
        print("   • 检查端口占用: lsof -i :8000 -i :7687 -i :7474")
        print("   • 查看服务日志: docker-compose logs graphiti")


async def main():
    """主测试函数"""
    print("🚀 开始Graphiti API连接测试")
    print(f"📍 测试目标: {Config.GRAPHITI_API_URL}")
    
    async with GraphitiAPITester() as tester:
        all_results = {}
        
        # 执行各项测试
        health_result = await tester.test_health_check()
        all_results["health_check"] = health_result
        
        api_results = await tester.test_direct_api_endpoints()
        all_results["api_endpoints"] = api_results
        
        adapter_results = await tester.test_adapter_integration()
        all_results["adapter_integration"] = adapter_results
        
        service_results = await tester.test_service_availability()
        all_results["service_availability"] = service_results
        
        # 打印测试摘要
        tester.print_test_summary(all_results)


if __name__ == "__main__":
    asyncio.run(main())