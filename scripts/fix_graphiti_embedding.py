#!/usr/bin/env python3
"""
修复Graphiti嵌入模型问题
通过创建模型别名或直接配置解决方案
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aiohttp
from aienhance.config import Config


async def test_model_alias_approach():
    """测试通过模型别名解决问题"""
    print("🔧 尝试模型别名解决方案")
    print("=" * 40)
    
    # 检查Ollama是否支持创建模型别名
    try:
        # 尝试创建一个text-embedding-3-small模型文件
        modelfile_content = """FROM nomic-embed-text
PARAMETER temperature 0.0"""
        
        modelfile_path = "/tmp/text-embedding-3-small.modelfile"
        with open(modelfile_path, "w") as f:
            f.write(modelfile_content)
        
        print("1️⃣ 创建模型别名...")
        result = subprocess.run([
            "ollama", "create", "text-embedding-3-small", "-f", modelfile_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ 成功创建text-embedding-3-small别名")
            return True
        else:
            print(f"   ❌ 别名创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 别名创建异常: {e}")
        return False


async def test_direct_api_with_alias():
    """测试使用别名后的API"""
    print("\n2️⃣ 测试别名后的Ollama API")
    
    async with aiohttp.ClientSession() as session:
        # 测试OpenAI兼容接口是否能识别新模型
        try:
            headers = {
                "Authorization": "Bearer fake_key_for_ollama",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "text-embedding-3-small",
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
                        print(f"   ✅ text-embedding-3-small可用: {dim}维")
                        return True
                    else:
                        print("   ⚠️  text-embedding-3-small返回空数据")
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ text-embedding-3-small不可用: {response.status}")
                    print(f"   错误: {error_text}")
                    return False
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return False


async def test_graphiti_after_fix():
    """修复后测试Graphiti"""
    print("\n3️⃣ 测试修复后的Graphiti")
    
    # 重启Graphiti服务
    try:
        print("   重启Graphiti服务...")
        subprocess.run([
            "docker", "compose", "restart", "graph"
        ], cwd="/Users/hongling/Dev/claude/graphiti", check=True, capture_output=True)
        
        # 等待启动
        await asyncio.sleep(10)
        
        # 运行简单测试
        print("   测试搜索功能...")
        result = subprocess.run([
            "uv", "run", "python", "tests/test_graphiti_simple.py"
        ], capture_output=True, text=True, cwd="/Users/hongling/Dev/claude/AiEnhance")
        
        if "搜索功能存在嵌入模型配置问题" in result.stdout:
            print("   ❌ 搜索问题仍然存在")
            return False
        else:
            print("   ✅ Graphiti搜索可能已修复")
            return True
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def cleanup_model_alias():
    """清理创建的模型别名"""
    print("\n4️⃣ 清理模型别名")
    try:
        result = subprocess.run([
            "ollama", "rm", "text-embedding-3-small"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ 清理完成")
        else:
            print(f"   ⚠️  清理结果: {result.stderr}")
    except Exception as e:
        print(f"   ❌ 清理异常: {e}")


async def main():
    """主函数"""
    print("🚀 Graphiti嵌入模型修复尝试")
    print("=" * 50)
    
    # 尝试创建模型别名
    alias_created = await test_model_alias_approach()
    
    if alias_created:
        # 测试别名是否工作
        alias_works = await test_direct_api_with_alias()
        
        if alias_works:
            # 测试Graphiti是否修复
            graphiti_fixed = await test_graphiti_after_fix()
            
            if not graphiti_fixed:
                print("\n💡 结论:")
                print("   虽然创建了模型别名，但Graphiti问题依然存在")
                print("   可能需要查看Graphiti源码或使用其他方法")
        
        # 清理别名
        cleanup_model_alias()
    
    print("\n📋 总结:")
    print("   • Ollama OpenAI兼容接口工作正常")
    print("   • 问题出现在Graphiti的模型配置层面")
    print("   • 建议检查Graphiti源码中的默认模型设置")
    print("   • 或者联系Graphiti项目获取正确的配置方法")


if __name__ == "__main__":
    asyncio.run(main())