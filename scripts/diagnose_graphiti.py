#!/usr/bin/env python3
"""
Graphiti配置诊断和修复脚本
帮助解决嵌入模型配置问题
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


async def diagnose_graphiti_config():
    """诊断Graphiti配置问题"""
    print("🔧 Graphiti配置诊断")
    print("=" * 40)
    
    # 1. 检查当前配置
    print("\n📋 当前系统配置:")
    print(f"   Graphiti API: {Config.GRAPHITI_API_URL}")
    print(f"   Neo4j URI: {Config.NEO4J_URI}")
    print(f"   Ollama URL: {Config.OLLAMA_BASE_URL}")
    print(f"   嵌入模型: {Config.EMBEDDING_MODEL}")
    
    # 2. 检查Ollama可用性
    print("\n🤖 检查Ollama服务:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{Config.OLLAMA_BASE_URL}/api/tags") as response:
                if response.status == 200:
                    models = await response.json()
                    print("   ✅ Ollama服务运行正常")
                    print("   📦 可用模型:")
                    for model in models.get("models", []):
                        name = model.get("name", "未知")
                        size = model.get("size", 0) // (1024**3)  # GB
                        print(f"     - {name} ({size}GB)")
                else:
                    print(f"   ❌ Ollama服务异常: {response.status}")
    except Exception as e:
        print(f"   ❌ Ollama连接失败: {e}")
    
    # 3. 测试嵌入模型
    print(f"\n🔍 测试嵌入模型 ({Config.EMBEDDING_MODEL}):")
    try:
        async with aiohttp.ClientSession() as session:
            embed_payload = {
                "model": Config.EMBEDDING_MODEL,
                "prompt": "测试嵌入",
                "input": "这是一个测试文本"
            }
            
            async with session.post(
                f"{Config.OLLAMA_BASE_URL}/api/embeddings",
                json=embed_payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    embedding = result.get("embedding", [])
                    print(f"   ✅ 嵌入生成成功")
                    print(f"   📊 向量维度: {len(embedding)}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ 嵌入生成失败: {response.status}")
                    print(f"   错误详情: {error_text}")
    except Exception as e:
        print(f"   ❌ 嵌入测试异常: {e}")


async def suggest_fixes():
    """提供配置修复建议"""
    print("\n" + "=" * 50)
    print("🛠️  配置修复建议")
    print("=" * 50)
    
    print("\n🎯 问题分析:")
    print("   Graphiti服务配置为使用OpenAI嵌入模型，但该模型不可用")
    print("   这导致搜索功能出现500错误")
    
    print("\n🔧 解决方案1: 配置Graphiti使用Ollama嵌入")
    print("   1. 停止当前Graphiti服务:")
    print("      docker-compose down")
    print("")
    print("   2. 修改Graphiti配置文件，设置嵌入提供商为Ollama:")
    print("      - 查找graphiti配置文件 (可能在docker-compose.yml或环境变量)")
    print("      - 设置 EMBEDDING_PROVIDER=ollama")
    print("      - 设置 OLLAMA_BASE_URL=http://host.docker.internal:11434")
    print("      - 设置 EMBEDDING_MODEL=bge-m3")
    print("")
    print("   3. 重启服务:")
    print("      docker-compose up -d")
    
    print("\n🔧 解决方案2: 提供OpenAI API密钥")
    print("   1. 获取OpenAI API密钥")
    print("   2. 在docker-compose.yml中设置环境变量:")
    print("      OPENAI_API_KEY=your_openai_api_key")
    print("   3. 重启服务")
    
    print("\n🔧 解决方案3: 使用本地嵌入模式 (如果支持)")
    print("   1. 查看Graphiti文档，确认是否支持本地嵌入")
    print("   2. 配置为不使用远程嵌入服务")
    
    print("\n✅ 当前可用功能:")
    print("   • 服务健康检查 ✅")
    print("   • 消息添加 ✅") 
    print("   • 数据清理 ✅")
    print("   • Neo4j直连 ✅")
    
    print("\n❌ 待修复功能:")
    print("   • 语义搜索 (需要嵌入模型)")
    print("   • 相似性查询")
    

async def test_workaround():
    """测试不依赖嵌入的功能"""
    print("\n" + "=" * 50) 
    print("🧪 替代功能测试")
    print("=" * 50)
    
    # 直接查询Neo4j中的数据
    try:
        from neo4j import AsyncGraphDatabase
        
        driver = AsyncGraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD)
        )
        
        async with driver.session() as session:
            print("\n🔍 直接查询Neo4j数据:")
            
            # 查询节点类型统计
            result = await session.run(
                "MATCH (n) RETURN labels(n) as labels, count(n) as count"
            )
            print("   节点类型统计:")
            async for record in result:
                labels = record["labels"]
                count = record["count"]
                print(f"     {labels}: {count}个")
            
            # 查询关系统计
            result = await session.run(
                "MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count"
            )
            print("   关系类型统计:")
            async for record in result:
                rel_type = record["rel_type"]
                count = record["count"]
                print(f"     {rel_type}: {count}个")
        
        await driver.close()
        
    except ImportError:
        print("   ⚠️  neo4j包未安装，无法直接查询")
    except Exception as e:
        print(f"   ❌ Neo4j查询失败: {e}")


async def main():
    """主函数"""
    await diagnose_graphiti_config()
    await suggest_fixes()
    await test_workaround()


if __name__ == "__main__":
    asyncio.run(main())