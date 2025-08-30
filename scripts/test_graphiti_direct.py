#!/usr/bin/env python3
"""
直接测试Graphiti搜索API
绕过适配器直接调用API来诊断问题
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


async def test_graphiti_search_direct():
    """直接测试Graphiti搜索API"""
    api_url = Config.GRAPHITI_API_URL
    test_user = "direct_test_user"
    
    print("🔬 直接Graphiti API搜索测试")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # 1. 添加测试消息
        print("\n1️⃣ 添加测试消息")
        test_message = {
            "group_id": test_user,
            "messages": [{
                "content": "Python是一个优秀的编程语言，特别适合AI开发",
                "role_type": "user",
                "role": test_user,
                "timestamp": datetime.datetime.now().isoformat(),
                "source_description": "直接API测试"
            }]
        }
        
        try:
            async with session.post(
                f"{api_url}/messages",
                json=test_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [200, 202]:
                    result = await response.json()
                    print(f"   ✅ 消息已添加: {result.get('message')}")
                else:
                    print(f"   ❌ 添加失败: {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ 添加异常: {e}")
            return
        
        # 2. 等待处理
        print("\n2️⃣ 等待消息处理...")
        await asyncio.sleep(5)
        
        # 3. 测试不同类型的搜索
        print("\n3️⃣ 测试搜索功能")
        
        search_tests = [
            ("Python", "关键词搜索"),
            ("编程语言", "中文搜索"),  
            ("", "空查询搜索"),
            ("AI开发", "组合词搜索")
        ]
        
        for query, description in search_tests:
            print(f"\n   测试: {description} - '{query}'")
            
            search_payload = {
                "query": query,
                "group_ids": [test_user],
                "max_facts": 5
            }
            
            try:
                async with session.post(
                    f"{api_url}/search",
                    json=search_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    print(f"     状态码: {response.status}")
                    
                    if response.status == 200:
                        try:
                            results = await response.json()
                            print(f"     结果数量: {len(results) if isinstance(results, list) else '未知类型'}")
                            
                            if isinstance(results, list) and results:
                                # 显示第一个结果
                                first = results[0]
                                content = first.get('content', str(first))[:50]
                                score = first.get('score', 'N/A')
                                print(f"     首个结果: {content}... (分数: {score})")
                            elif isinstance(results, list):
                                print("     ✅ 搜索成功但无结果")
                            else:
                                print(f"     ⚠️  非预期结果类型: {type(results)}")
                                
                        except json.JSONDecodeError as e:
                            response_text = await response.text()
                            print(f"     ❌ JSON解析失败: {e}")
                            print(f"     原始响应: {response_text[:200]}...")
                            
                    else:
                        error_text = await response.text()
                        print(f"     ❌ 搜索失败")
                        print(f"     错误响应: {error_text[:200]}...")
                        
            except asyncio.TimeoutError:
                print("     ❌ 请求超时")
            except Exception as e:
                print(f"     ❌ 搜索异常: {e}")
        
        # 4. 清理
        print("\n4️⃣ 清理测试数据")
        try:
            clear_payload = {"group_id": test_user}
            async with session.post(
                f"{api_url}/clear",
                json=clear_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("   ✅ 清理完成")
                else:
                    print(f"   ⚠️  清理状态: {response.status}")
        except Exception as e:
            print(f"   ❌ 清理失败: {e}")


async def main():
    """主函数"""
    await test_graphiti_search_direct()


if __name__ == "__main__":
    asyncio.run(main())