#!/usr/bin/env python3
"""
测试MIRIX连接的简单脚本
用于验证MIRIX服务是否正常运行
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_mirix_connection():
    """测试MIRIX连接"""
    print("🔍 测试MIRIX服务连接...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 1. 测试健康检查
            print("📋 检查MIRIX健康状态...")
            health_response = await client.get("http://localhost:8000/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ MIRIX服务状态: {health_data.get('status')}")
                print(f"📊 服务组件: {health_data.get('services', {})}")
            else:
                print(f"❌ 健康检查失败: HTTP {health_response.status_code}")
                return False
            
            # 2. 测试系统信息
            print("\n📋 获取系统信息...")
            info_response = await client.get("http://localhost:8000/api/system/info")
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                print(f"✅ 服务名称: {info_data.get('service')}")
                print(f"📂 支持的记忆类型: {info_data.get('memory_types', [])}")
                print(f"🔧 功能特性: {info_data.get('features', {})}")
            else:
                print(f"⚠️  系统信息获取失败: HTTP {info_response.status_code}")
            
            # 3. 测试记忆添加（可选）
            print("\n📝 测试记忆添加功能...")
            memory_data = {
                "content": "这是一个测试记忆条目",
                "memory_type": "episodic",
                "user_id": "test_user",
                "session_id": "test_session",
                "metadata": {
                    "test": True,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            add_response = await client.post(
                "http://localhost:8000/api/memory/add",
                json=memory_data
            )
            
            if add_response.status_code == 200:
                add_result = add_response.json()
                print(f"✅ 记忆添加成功: {add_result.get('memory_id')}")
                
                # 4. 测试记忆搜索
                print("\n🔍 测试记忆搜索功能...")
                search_data = {
                    "query": "测试",
                    "user_id": "test_user",
                    "limit": 10
                }
                
                search_response = await client.post(
                    "http://localhost:8000/api/memory/search",
                    json=search_data
                )
                
                if search_response.status_code == 200:
                    search_result = search_response.json()
                    print(f"✅ 搜索成功，找到 {len(search_result.get('memories', []))} 条记忆")
                else:
                    print(f"⚠️  记忆搜索失败: HTTP {search_response.status_code}")
                
            else:
                print(f"⚠️  记忆添加失败: HTTP {add_response.status_code}")
            
            print("\n🎉 MIRIX服务连接测试完成！")
            return True
            
    except httpx.ConnectError:
        print("❌ 无法连接到MIRIX服务 (http://localhost:8000)")
        print("💡 请确保MIRIX服务已启动:")
        print("   ./start-dev.sh  # 或")
        print("   docker compose up -d")
        return False
    except httpx.TimeoutException:
        print("❌ 连接MIRIX服务超时")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("=" * 50)
    print("🧪 MIRIX 连接测试工具")
    print("=" * 50)
    
    success = await test_mirix_connection()
    
    if success:
        print("\n✅ 测试通过！MIRIX服务运行正常")
        print("💡 现在可以运行主应用: python ai.py")
    else:
        print("\n❌ 测试失败！请检查MIRIX服务状态")
        print("💡 启动服务: ./start-dev.sh")

if __name__ == "__main__":
    asyncio.run(main())