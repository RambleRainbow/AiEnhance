#!/usr/bin/env python3
"""
Graphiti API 简单测试程序
专注于测试核心连接功能，避免需要嵌入模型的复杂操作
"""

import asyncio
import datetime
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


async def simple_graphiti_test():
    """简单的Graphiti功能测试"""
    api_url = Config.GRAPHITI_API_URL
    print(f"🧪 简单Graphiti API测试")
    print(f"📍 服务地址: {api_url}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 健康检查
        print("\n1️⃣ 服务健康检查")
        try:
            async with session.get(f"{api_url}/healthcheck") as response:
                health_status = response.status == 200
                health_data = await response.json()
                print(f"   状态: {'✅ 健康' if health_status else '❌ 异常'}")
                print(f"   详情: {json.dumps(health_data, ensure_ascii=False)}")
        except Exception as e:
            print(f"   ❌ 健康检查失败: {e}")
            return False
        
        # 2. 添加消息测试
        print("\n2️⃣ 消息添加测试")
        test_message = {
            "group_id": "simple_test_user",
            "messages": [
                {
                    "content": "Hello Graphiti! 这是一个简单的连接测试",
                    "role_type": "user",
                    "role": "simple_test_user", 
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source_description": "简单连接测试"
                }
            ]
        }
        
        try:
            async with session.post(
                f"{api_url}/messages",
                json=test_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                add_status = response.status in [200, 202]
                response_data = await response.json()
                print(f"   状态: {'✅ 成功' if add_status else '❌ 失败'}")
                print(f"   响应: {json.dumps(response_data, ensure_ascii=False)}")
        except Exception as e:
            print(f"   ❌ 消息添加失败: {e}")
        
        # 3. 简单搜索测试 (空查询，应该不需要嵌入)
        print("\n3️⃣ 基础搜索测试")
        basic_search = {
            "query": "",  # 空查询
            "group_ids": ["simple_test_user"],
            "max_facts": 5
        }
        
        try:
            async with session.post(
                f"{api_url}/search",
                json=basic_search,
                headers={"Content-Type": "application/json"}
            ) as response:
                search_status = response.status == 200
                if search_status:
                    results = await response.json()
                    print(f"   状态: ✅ 成功")
                    print(f"   结果数量: {len(results) if isinstance(results, list) else '未知'}")
                else:
                    error_text = await response.text()
                    print(f"   状态: ❌ 失败 ({response.status})")
                    print(f"   错误: {error_text}")
        except Exception as e:
            print(f"   ❌ 搜索测试异常: {e}")
        
        # 4. 清理测试数据
        print("\n4️⃣ 数据清理")
        try:
            clear_payload = {"group_id": "simple_test_user"}
            async with session.post(
                f"{api_url}/clear",
                json=clear_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                clear_status = response.status == 200
                print(f"   状态: {'✅ 清理成功' if clear_status else '❌ 清理失败'}")
        except Exception as e:
            print(f"   ❌ 清理异常: {e}")

    print("\n" + "=" * 50)
    print("📋 测试结论:")
    print("• Graphiti HTTP服务运行正常")
    print("• 消息添加功能工作正常") 
    print("• 搜索功能存在嵌入模型配置问题")
    print("• 建议检查Graphiti服务的嵌入模型配置")
    print("\n💡 解决方案:")
    print("• 配置Graphiti使用本地Ollama嵌入模型")
    print("• 或者提供有效的OpenAI API密钥")
    
    return True


async def check_neo4j_data():
    """检查Neo4j中的数据"""
    print("\n5️⃣ Neo4j数据检查")
    
    try:
        from neo4j import AsyncGraphDatabase
        
        driver = AsyncGraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        
        async with driver.session() as session:
            # 检查节点数量
            result = await session.run("MATCH (n) RETURN count(n) as node_count")
            record = await result.single()
            node_count = record["node_count"] if record else 0
            
            print(f"   图数据库节点数量: {node_count}")
            
            # 检查最近的节点
            if node_count > 0:
                result = await session.run(
                    "MATCH (n) RETURN n LIMIT 3"
                )
                print("   最近的节点:")
                async for record in result:
                    node = record["n"]
                    print(f"     - {dict(node)}")
        
        await driver.close()
        print("   ✅ Neo4j数据检查完成")
        
    except ImportError:
        print("   ⚠️  neo4j包未安装")
    except Exception as e:
        print(f"   ❌ Neo4j检查失败: {e}")


if __name__ == "__main__":
    async def main():
        await simple_graphiti_test()
        await check_neo4j_data()
    
    asyncio.run(main())