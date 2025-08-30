#!/usr/bin/env python3
"""
测试Ollama嵌入服务兼容性
验证Ollama可以通过OpenAI API兼容接口提供嵌入服务
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


async def test_ollama_embedding_directly():
    """直接测试Ollama嵌入服务"""
    print("🧪 测试Ollama嵌入服务")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # 测试原生Ollama嵌入接口
        print("\n1️⃣ 测试原生Ollama嵌入接口")
        try:
            payload = {
                "model": "nomic-embed-text",
                "prompt": "这是一个测试文本"
            }
            
            async with session.post(
                f"{Config.OLLAMA_BASE_URL}/api/embeddings",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    embedding = result.get("embedding", [])
                    print(f"   ✅ 原生接口成功")
                    print(f"   向量维度: {len(embedding)}")
                else:
                    print(f"   ❌ 原生接口失败: {response.status}")
        except Exception as e:
            print(f"   ❌ 原生接口异常: {e}")
        
        # 测试OpenAI兼容接口
        print("\n2️⃣ 测试OpenAI兼容接口")
        try:
            headers = {
                "Authorization": "Bearer fake_key_for_ollama",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "nomic-embed-text",
                "input": ["这是一个测试文本"]
            }
            
            async with session.post(
                f"{Config.OLLAMA_BASE_URL}/v1/embeddings",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    embeddings = result.get("data", [])
                    if embeddings:
                        embedding = embeddings[0].get("embedding", [])
                        print(f"   ✅ OpenAI兼容接口成功")
                        print(f"   向量维度: {len(embedding)}")
                        print(f"   数据格式: {list(result.keys())}")
                    else:
                        print(f"   ⚠️  OpenAI兼容接口返回空数据")
                else:
                    error_text = await response.text()
                    print(f"   ❌ OpenAI兼容接口失败: {response.status}")
                    print(f"   错误详情: {error_text}")
        except Exception as e:
            print(f"   ❌ OpenAI兼容接口异常: {e}")
        
        # 测试不同模型
        print("\n3️⃣ 测试其他可用嵌入模型")
        embedding_models = ["bge-m3", "nomic-embed-text"]
        
        for model in embedding_models:
            try:
                headers = {
                    "Authorization": "Bearer fake_key_for_ollama",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "input": ["测试文本"]
                }
                
                async with session.post(
                    f"{Config.OLLAMA_BASE_URL}/v1/embeddings",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        embeddings = result.get("data", [])
                        if embeddings:
                            dim = len(embeddings[0].get("embedding", []))
                            print(f"   ✅ {model}: {dim}维")
                        else:
                            print(f"   ⚠️  {model}: 无数据")
                    else:
                        print(f"   ❌ {model}: {response.status}")
            except Exception as e:
                print(f"   ❌ {model}: {e}")


async def test_graphiti_embedding_config():
    """测试Graphiti的嵌入配置"""
    print("\n" + "=" * 40)
    print("🔧 Graphiti嵌入配置分析")
    print("=" * 40)
    
    print("\n当前Docker环境变量:")
    print("  OPENAI_BASE_URL=http://host.docker.internal:11434/v1")
    print("  OPENAI_API_KEY=fake_key_for_ollama")
    print("  EMBEDDER_MODEL_NAME=nomic-embed-text")
    print("  EMBEDDER=openai")
    
    print("\n问题分析:")
    print("  • Graphiti仍在使用text-embedding-3-small模型")
    print("  • 可能需要在代码层面指定嵌入模型名称")
    print("  • 或者需要重建Docker镜像以应用环境变量")
    
    print("\n可能的解决方案:")
    print("  1. 在Graphiti源码中查找默认模型配置")
    print("  2. 检查是否需要设置其他环境变量")
    print("  3. 验证Ollama的OpenAI兼容性")


async def main():
    """主函数"""
    await test_ollama_embedding_directly()
    await test_graphiti_embedding_config()


if __name__ == "__main__":
    asyncio.run(main())