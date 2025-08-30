#!/usr/bin/env python3
"""
Graphiti API 详细诊断程序
更深入地测试Graphiti的各项功能和潜在问题
"""

import asyncio
import datetime
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


async def test_graphiti_detailed():
    """详细的Graphiti API测试"""
    api_url = Config.GRAPHITI_API_URL
    test_user_id = "detailed_test_user"
    
    print(f"🔍 详细测试Graphiti API: {api_url}")
    
    async with aiohttp.ClientSession() as session:
        # 1. 健康检查
        print("\n1️⃣ 健康检查...")
        try:
            async with session.get(f"{api_url}/healthcheck") as response:
                health_data = await response.json()
                print(f"   状态: {response.status}")
                print(f"   响应: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"   健康检查失败: {e}")
            return
        
        # 2. 添加测试消息
        print("\n2️⃣ 添加测试消息...")
        test_messages = [
            {
                "content": "我喜欢编程，特别是Python和机器学习",
                "role_type": "user",
                "role": test_user_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "source_description": "用户偏好信息"
            },
            {
                "content": "我正在开发一个AI增强系统，使用Graphiti作为记忆系统",
                "role_type": "user", 
                "role": test_user_id,
                "timestamp": (datetime.datetime.now() + datetime.timedelta(seconds=1)).isoformat(),
                "source_description": "项目信息"
            },
            {
                "content": "我需要测试记忆系统的搜索和检索功能",
                "role_type": "user",
                "role": test_user_id, 
                "timestamp": (datetime.datetime.now() + datetime.timedelta(seconds=2)).isoformat(),
                "source_description": "当前任务"
            }
        ]
        
        for i, message in enumerate(test_messages):
            try:
                payload = {
                    "group_id": test_user_id,
                    "messages": [message]
                }
                
                async with session.post(
                    f"{api_url}/messages",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    result = await response.json()
                    print(f"   消息{i+1}: {response.status} - {result.get('message', 'No message')}")
                    
                # 短暂延迟以避免速率限制
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   消息{i+1}失败: {e}")
        
        # 3. 等待处理并尝试搜索
        print("\n3️⃣ 等待消息处理并测试搜索...")
        await asyncio.sleep(3)  # 等待3秒让消息处理完成
        
        search_queries = [
            "编程",
            "Python", 
            "AI增强系统",
            "测试",
            ""  # 空查询测试
        ]
        
        for query_text in search_queries:
            try:
                search_payload = {
                    "query": query_text,
                    "group_ids": [test_user_id],
                    "max_facts": 10
                }
                
                async with session.post(
                    f"{api_url}/search",
                    json=search_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        results = await response.json()
                        result_count = len(results) if isinstance(results, list) else "未知"
                        print(f"   搜索 '{query_text}': ✅ {result_count}个结果")
                        
                        # 显示前2个结果的详细信息
                        if isinstance(results, list) and results:
                            for idx, result in enumerate(results[:2]):
                                content = result.get('content', result.get('text', str(result)))
                                score = result.get('score', result.get('similarity', 'N/A'))
                                print(f"     结果{idx+1}: {content[:60]}... (分数: {score})")
                    else:
                        error_text = await response.text()
                        print(f"   搜索 '{query_text}': ❌ {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"   搜索 '{query_text}'异常: {e}")
        
        # 4. 测试其他端点
        print("\n4️⃣ 测试其他可用端点...")
        
        # 检查是否有stats端点
        try:
            async with session.get(f"{api_url}/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"   统计信息: ✅")
                    print(f"   数据: {json.dumps(stats, indent=2, ensure_ascii=False)}")
                else:
                    print(f"   统计信息: ❌ {response.status}")
        except Exception as e:
            print(f"   统计信息异常: {e}")
        
        # 5. 清理测试数据
        print("\n5️⃣ 清理测试数据...")
        try:
            clear_payload = {"group_id": test_user_id}
            async with session.post(
                f"{api_url}/clear",
                json=clear_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("   清理: ✅ 成功")
                else:
                    print(f"   清理: ❌ {response.status}")
        except Exception as e:
            print(f"   清理异常: {e}")


async def test_neo4j_connection():
    """测试Neo4j连接 (如果bolt驱动可用)"""
    print("\n6️⃣ 测试Neo4j直连...")
    
    try:
        # 尝试导入neo4j驱动
        from neo4j import AsyncGraphDatabase
        
        uri = Config.NEO4J_URI
        user = Config.NEO4J_USER
        password = Config.NEO4J_PASSWORD
        
        print(f"   连接到: {uri}")
        
        driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        
        async with driver.session() as session:
            # 简单查询测试
            result = await session.run("RETURN 'Neo4j连接成功' as message, datetime() as timestamp")
            record = await result.single()
            
            if record:
                print(f"   ✅ Neo4j连接成功")
                print(f"   消息: {record['message']}")
                print(f"   时间戳: {record['timestamp']}")
            else:
                print("   ❌ 查询无结果")
                
        await driver.close()
        
    except ImportError:
        print("   ⚠️  neo4j驱动未安装，跳过直连测试")
    except Exception as e:
        print(f"   ❌ Neo4j连接失败: {e}")


async def main():
    """主函数"""
    print("=" * 70)
    print("🧪 GRAPHITI API 详细诊断测试")
    print("=" * 70)
    
    await test_graphiti_detailed()
    await test_neo4j_connection()
    
    print("\n" + "=" * 70)
    print("🏁 测试完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())