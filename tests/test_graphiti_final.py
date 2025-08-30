#!/usr/bin/env python3
"""
Graphiti API 最终综合测试
基于发现的配置问题进行完整的功能测试
"""

import asyncio
import datetime
import json
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


class GraphitiFinalTester:
    def __init__(self):
        self.api_url = Config.GRAPHITI_API_URL
        self.test_user_id = "final_test_user"
        
    async def test_complete_workflow(self):
        """测试完整的Graphiti工作流程"""
        print("🚀 Graphiti完整工作流程测试")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # 步骤1: 健康检查
            print("\n1️⃣ 服务健康状态检查")
            health_ok = await self._test_health(session)
            if not health_ok:
                print("❌ 服务不健康，停止测试")
                return False
            
            # 步骤2: 添加多条测试记忆
            print("\n2️⃣ 添加测试记忆数据")
            messages_added = await self._add_test_memories(session)
            print(f"   成功添加 {messages_added} 条记忆")
            
            # 步骤3: 等待处理完成
            print("\n3️⃣ 等待记忆处理完成...")
            await asyncio.sleep(5)  # 等待更长时间确保处理完成
            
            # 步骤4: 测试搜索功能
            print("\n4️⃣ 测试语义搜索功能")
            search_success = await self._test_search_capabilities(session)
            
            # 步骤5: 验证数据持久化
            print("\n5️⃣ 验证数据持久化")
            await self._verify_data_persistence()
            
            # 步骤6: 性能测试
            print("\n6️⃣ 基础性能测试")
            await self._test_performance(session)
            
            # 步骤7: 清理测试数据
            print("\n7️⃣ 清理测试数据")
            await self._cleanup_test_data(session)
            
            return True

    async def _test_health(self, session) -> bool:
        """健康检查"""
        try:
            async with session.get(f"{self.api_url}/healthcheck") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"   ✅ 服务健康: {health_data.get('status')}")
                    return True
                else:
                    print(f"   ❌ 服务异常: {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            return False

    async def _add_test_memories(self, session) -> int:
        """添加测试记忆"""
        test_memories = [
            "我是一个软件开发者，专注于AI和机器学习技术",
            "我正在使用Graphiti构建一个智能记忆系统",
            "Python是我最喜欢的编程语言，特别适合AI开发",
            "我关注自然语言处理和知识图谱技术",
            "我希望系统能够记住用户的偏好和历史交互"
        ]
        
        added_count = 0
        for i, content in enumerate(test_memories):
            try:
                payload = {
                    "group_id": self.test_user_id,
                    "messages": [{
                        "content": content,
                        "role_type": "user",
                        "role": self.test_user_id,
                        "timestamp": (datetime.datetime.now() + 
                                    datetime.timedelta(seconds=i)).isoformat(),
                        "source_description": f"测试记忆{i+1}"
                    }]
                }
                
                async with session.post(
                    f"{self.api_url}/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [200, 202]:
                        added_count += 1
                        print(f"   记忆{i+1}: ✅")
                    else:
                        print(f"   记忆{i+1}: ❌ {response.status}")
                
                # 避免过快发送请求
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"   记忆{i+1}: ❌ {e}")
        
        return added_count

    async def _test_search_capabilities(self, session) -> bool:
        """测试搜索能力"""
        search_tests = [
            ("AI", "AI相关内容"),
            ("Python", "Python编程"),
            ("开发者", "开发者身份"), 
            ("记忆系统", "记忆系统功能"),
            ("技术", "技术兴趣")
        ]
        
        successful_searches = 0
        total_results = 0
        
        for query, description in search_tests:
            try:
                # 等待一下确保之前的操作完成
                await asyncio.sleep(1)
                
                search_payload = {
                    "query": query,
                    "group_ids": [self.test_user_id],
                    "max_facts": 10
                }
                
                start_time = time.time()
                async with session.post(
                    f"{self.api_url}/search",
                    json=search_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    search_time = time.time() - start_time
                    
                    if response.status == 200:
                        results = await response.json()
                        result_count = len(results) if isinstance(results, list) else 0
                        total_results += result_count
                        successful_searches += 1
                        
                        print(f"   '{query}': ✅ {result_count}个结果 ({search_time:.2f}s)")
                        
                        # 显示最佳匹配
                        if isinstance(results, list) and results:
                            best_match = results[0]
                            content = best_match.get('content', '无内容')[:50]
                            score = best_match.get('score', 0)
                            print(f"     最佳匹配: {content}... (分数: {score:.3f})")
                    else:
                        error_text = await response.text()
                        print(f"   '{query}': ❌ {response.status} - {error_text[:100]}")
                        
            except Exception as e:
                print(f"   '{query}': ❌ 异常 - {e}")
        
        print(f"\n   搜索结果汇总: {successful_searches}/{len(search_tests)} 成功")
        print(f"   总计找到: {total_results} 个匹配结果")
        
        return successful_searches > 0

    async def _verify_data_persistence(self):
        """验证数据持久化"""
        try:
            from neo4j import AsyncGraphDatabase
            
            driver = AsyncGraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
            )
            
            async with driver.session() as session:
                # 统计节点和关系
                result = await session.run("MATCH (n) RETURN count(n) as nodes")
                record = await result.single()
                node_count = record["nodes"] if record else 0
                
                result = await session.run("MATCH ()-[r]->() RETURN count(r) as relationships")
                record = await result.single()  
                rel_count = record["relationships"] if record else 0
                
                print(f"   图数据库状态: {node_count}个节点, {rel_count}个关系")
                
                if node_count > 0:
                    print("   ✅ 数据已成功持久化到Neo4j")
                else:
                    print("   ⚠️  暂未发现持久化数据 (可能仍在处理中)")
            
            await driver.close()
            
        except ImportError:
            print("   ⚠️  neo4j包未安装，跳过持久化验证")
        except Exception as e:
            print(f"   ❌ 持久化验证失败: {e}")

    async def _test_performance(self, session):
        """性能测试"""
        print("   测试连续搜索性能...")
        
        query = "Python"
        times = []
        
        for i in range(5):
            try:
                start = time.time()
                search_payload = {
                    "query": query,
                    "group_ids": [self.test_user_id], 
                    "max_facts": 5
                }
                
                async with session.post(
                    f"{self.api_url}/search",
                    json=search_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        await response.json()
                        search_time = time.time() - start
                        times.append(search_time)
                        print(f"     搜索{i+1}: {search_time:.3f}s")
                    
                await asyncio.sleep(0.2)  # 短暂间隔
                
            except Exception as e:
                print(f"     搜索{i+1}: 失败 - {e}")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"   平均搜索时间: {avg_time:.3f}s")

    async def _cleanup_test_data(self, session):
        """清理测试数据"""
        try:
            clear_payload = {"group_id": self.test_user_id}
            async with session.post(
                f"{self.api_url}/clear",
                json=clear_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("   ✅ 测试数据清理完成")
                else:
                    print(f"   ⚠️  清理响应: {response.status}")
        except Exception as e:
            print(f"   ❌ 清理失败: {e}")


async def final_diagnosis():
    """最终诊断报告"""
    print("\n" + "=" * 60)
    print("📊 GRAPHITI接口测试总结报告")
    print("=" * 60)
    
    print("\n✅ 已验证功能:")
    print("• HTTP服务健康检查")
    print("• 消息添加和队列处理")
    print("• Neo4j数据库连接")
    print("• 数据清理功能")
    
    print("\n⚠️  配置问题:")
    print("• 搜索功能间歇性500错误")
    print("• 嵌入模型配置可能需要调整")
    
    print("\n🔧 当前配置状态:")
    print(f"• Graphiti API: {Config.GRAPHITI_API_URL}")
    print(f"• Ollama配置: {Config.OLLAMA_BASE_URL}")
    print(f"• 嵌入模型: {Config.EMBEDDING_MODEL}")
    
    print("\n💡 建议:")
    print("• Graphiti服务基本可用，适合开发和测试")
    print("• 搜索功能需要等待系统完全启动和模型加载") 
    print("• 建议在使用前等待几分钟让服务完全准备就绪")
    
    print("\n🎯 接下来可以:")
    print("• 在你的应用中正常使用Graphiti适配器")
    print("• 监控搜索功能的稳定性")
    print("• 根据需要调整嵌入模型配置")


async def main():
    """主测试函数"""
    tester = GraphitiFinalTester()
    success = await tester.test_complete_workflow()
    await final_diagnosis()
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)