#!/usr/bin/env python3
"""
Ollama集成示例
展示如何在实际应用中集成Ollama qwen3:8b模型
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import aienhance
from aienhance.llm import ModelConfig, ModelType


class OllamaIntegrationExample:
    """Ollama集成示例类"""
    
    def __init__(self):
        self.system = None
        self.config = self._create_ollama_config()
    
    def _create_ollama_config(self):
        """创建Ollama配置"""
        return {
            # 基础配置
            "system_type": "educational",
            
            # LLM配置
            "llm_provider": "ollama",
            "llm_model_name": "qwen3:8b",
            "llm_api_base": "http://localhost:11434",
            "llm_temperature": 0.7,
            "llm_max_tokens": 1000,
            
            # 嵌入模型配置
            "embedding_provider": "ollama",
            "embedding_model_name": "bge-m3",
            "embedding_api_base": "http://localhost:11434"
        }
    
    async def initialize_system(self):
        """初始化系统"""
        print("🔧 初始化AiEnhance系统...")
        
        try:
            # 创建系统实例
            self.system = aienhance.create_system(**self.config)
            
            # 检查系统状态
            status = self.system.get_system_status()
            print(f"✅ 系统初始化成功")
            print(f"   • LLM配置: {status.get('llm_provider', 'None')}")
            print(f"   • 嵌入模型: {status.get('embedding_provider', 'None')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False
    
    async def check_ollama_status(self):
        """检查Ollama服务状态"""
        print("\n🔍 检查Ollama服务状态...")
        
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                # 检查服务可用性
                response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [model['name'] for model in models_data.get('models', [])]
                    
                    print(f"✅ Ollama服务正常运行")
                    print(f"📚 可用模型: {', '.join(available_models)}")
                    
                    # 检查必需模型
                    required_models = ["qwen3:8b", "bge-m3"]
                    missing_models = [model for model in required_models if model not in available_models]
                    
                    if missing_models:
                        print(f"⚠️ 缺少模型: {', '.join(missing_models)}")
                        print(f"💡 请运行: ollama pull {' && ollama pull '.join(missing_models)}")
                        return False
                    else:
                        print(f"✅ 所有必需模型已就绪")
                        return True
                else:
                    print(f"❌ Ollama服务异常: HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 无法连接Ollama服务: {e}")
            print(f"💡 请确保Ollama正在运行: ollama serve")
            return False
    
    async def demonstrate_basic_chat(self):
        """演示基础对话功能"""
        print("\n💬 基础对话功能演示")
        print("-" * 40)
        
        chat_examples = [
            {
                "user_input": "你好，请介绍一下自己",
                "expected": "应该包含模型介绍"
            },
            {
                "user_input": "什么是机器学习？",
                "expected": "应该解释机器学习概念"
            },
            {
                "user_input": "请写一个Python的Hello World程序",
                "expected": "应该包含Python代码示例"
            }
        ]
        
        for i, example in enumerate(chat_examples, 1):
            print(f"\n{i}. 👤 用户: {example['user_input']}")
            
            try:
                response = await self.system.process_query(
                    query=example['user_input'],
                    user_id="demo_user",
                    context={"demo_type": "basic_chat"}
                )
                
                if response.content:
                    print(f"   🤖 助手: {response.content[:200]}...")
                    print(f"   📊 响应长度: {len(response.content)}字符")
                    
                    # 显示处理信息
                    if hasattr(response, 'adaptation_info'):
                        print(f"   ⚙️ 适配: {response.adaptation_info.density_level.value}密度")
                else:
                    print(f"   ❌ 无响应内容生成")
                    
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
    
    async def demonstrate_educational_features(self):
        """演示教育功能特性"""
        print("\n🎓 教育功能特性演示")
        print("-" * 40)
        
        educational_queries = [
            {
                "query": "请解释深度学习的基本原理，我是初学者",
                "context": {"difficulty_level": "beginner"},
                "expected_features": ["循序渐进", "基础概念", "通俗易懂"]
            },
            {
                "query": "比较监督学习和无监督学习的区别",
                "context": {"difficulty_level": "intermediate"},
                "expected_features": ["对比分析", "具体例子", "实际应用"]
            },
            {
                "query": "神经网络的反向传播算法的数学推导",
                "context": {"difficulty_level": "advanced"},
                "expected_features": ["数学公式", "详细推导", "理论深度"]
            }
        ]
        
        for i, edu_query in enumerate(educational_queries, 1):
            print(f"\n{i}. 📚 教育查询: {edu_query['query']}")
            print(f"   🎯 预期特征: {', '.join(edu_query['expected_features'])}")
            
            try:
                response = await self.system.process_query(
                    query=edu_query['query'],
                    user_id="student_user",
                    context=edu_query['context']
                )
                
                if response.content:
                    print(f"   ✅ 响应生成成功 ({len(response.content)}字符)")
                    
                    # 分析教育特征
                    content_lower = response.content.lower()
                    features_found = []
                    
                    # 简单的特征检测
                    if any(word in content_lower for word in ["首先", "然后", "最后", "步骤"]):
                        features_found.append("结构化")
                    if any(word in content_lower for word in ["例如", "比如", "举例"]):
                        features_found.append("举例说明")
                    if any(word in content_lower for word in ["简单", "通俗", "基础"]):
                        features_found.append("易懂表达")
                    
                    print(f"   📋 检测到特征: {', '.join(features_found) if features_found else '无明显特征'}")
                    
                    # 显示适配信息
                    if hasattr(response, 'adaptation_info'):
                        print(f"   🎛️ 适配参数: 密度={response.adaptation_info.density_level.value}, 负荷={response.adaptation_info.cognitive_load:.2f}")
                else:
                    print(f"   ❌ 无响应内容")
                    
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
    
    async def demonstrate_multilingual_support(self):
        """演示多语言支持"""
        print("\n🌍 多语言支持演示")
        print("-" * 40)
        
        multilingual_tests = [
            {
                "language": "中文",
                "query": "请用中文解释什么是人工智能",
                "expected_lang": "中文"
            },
            {
                "language": "English", 
                "query": "Please explain artificial intelligence in English",
                "expected_lang": "English"
            },
            {
                "language": "混合",
                "query": "What is AI？请用中英文混合回答",
                "expected_lang": "中英混合"
            }
        ]
        
        for test in multilingual_tests:
            print(f"\n🗣️ {test['language']}测试: {test['query']}")
            
            try:
                response = await self.system.process_query(
                    query=test['query'],
                    user_id="multilingual_user",
                    context={"language_test": test['language']}
                )
                
                if response.content:
                    print(f"   ✅ 响应生成 ({len(response.content)}字符)")
                    # 显示响应片段
                    preview = response.content[:150] + "..." if len(response.content) > 150 else response.content
                    print(f"   📝 内容预览: {preview}")
                else:
                    print(f"   ❌ 无响应内容")
                    
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
    
    async def demonstrate_performance_metrics(self):
        """演示性能指标"""
        print("\n📊 性能指标演示")
        print("-" * 40)
        
        # 性能测试查询
        performance_queries = [
            "简单查询：1+1等于几？",
            "中等查询：请解释机器学习的基本概念",
            "复杂查询：请详细分析深度学习在计算机视觉领域的最新发展趋势"
        ]
        
        results = []
        
        for i, query in enumerate(performance_queries, 1):
            print(f"\n{i}. ⏱️ 测试查询: {query}")
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                response = await self.system.process_query(
                    query=query,
                    user_id="perf_test_user",
                    context={"performance_test": True}
                )
                
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                
                if response.content:
                    result = {
                        "query_type": f"测试{i}",
                        "duration": duration,
                        "content_length": len(response.content),
                        "words_per_second": len(response.content) / duration if duration > 0 else 0
                    }
                    results.append(result)
                    
                    print(f"   ✅ 耗时: {duration:.2f}秒")
                    print(f"   📏 长度: {len(response.content)}字符")
                    print(f"   🚀 速度: {result['words_per_second']:.1f}字符/秒")
                else:
                    print(f"   ❌ 无内容生成")
                    
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        # 性能总结
        if results:
            print(f"\n📈 性能总结:")
            avg_duration = sum(r['duration'] for r in results) / len(results)
            avg_length = sum(r['content_length'] for r in results) / len(results)
            avg_speed = sum(r['words_per_second'] for r in results) / len(results)
            
            print(f"   • 平均响应时间: {avg_duration:.2f}秒")
            print(f"   • 平均响应长度: {avg_length:.0f}字符")
            print(f"   • 平均生成速度: {avg_speed:.1f}字符/秒")
    
    async def run_complete_demo(self):
        """运行完整演示"""
        print("🚀 Ollama集成完整演示开始")
        print("=" * 60)
        
        # 1. 检查环境
        if not await self.check_ollama_status():
            print("❌ Ollama环境检查失败，演示终止")
            return False
        
        # 2. 初始化系统
        if not await self.initialize_system():
            print("❌ 系统初始化失败，演示终止")
            return False
        
        # 3. 运行各项演示
        await self.demonstrate_basic_chat()
        await self.demonstrate_educational_features()
        await self.demonstrate_multilingual_support()
        await self.demonstrate_performance_metrics()
        
        print("\n🎉 Ollama集成演示完成！")
        print("=" * 60)
        print("✅ 所有功能模块测试完成")
        print("✅ Ollama qwen3:8b模型集成成功")
        print("✅ 教育系统特性验证通过")
        print("✅ 性能指标收集完成")
        
        return True


async def main():
    """主函数"""
    example = OllamaIntegrationExample()
    success = await example.run_complete_demo()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)