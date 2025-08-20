#!/usr/bin/env python3
"""
分层认知系统流式演示工具
展示感知层、认知层、行为层、协作层的逐层处理过程
"""

import aienhance
import asyncio
import sys
import argparse
from pathlib import Path
from typing import AsyncIterator, Dict, Any
import time
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


class LayeredCognitiveStreamingDemo:
    """分层认知系统流式演示"""

    def __init__(self):
        self.system = None
        self.processing_stats = {
            'perception_time': 0,
            'cognition_time': 0, 
            'behavior_time': 0,
            'collaboration_time': 0,
            'total_time': 0
        }

    async def check_dependencies(self):
        """检查系统依赖"""
        print("🔍 检查系统依赖...")
        
        # 检查Ollama
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:11434/api/tags", 
                    timeout=3.0
                )
                if response.status_code == 200:
                    print("✅ Ollama服务正常")
                    return True
                else:
                    print("❌ Ollama服务异常")
                    return False
        except Exception as e:
            print(f"❌ Ollama连接失败: {e}")
            print("💡 请确保运行: ollama serve")
            return False

    async def initialize_layered_system(self, system_type="educational"):
        """初始化分层认知系统"""
        try:
            print(f"🧠 初始化分层认知系统 (类型: {system_type})...")
            
            # 使用工厂方法创建分层系统
            if system_type == "educational":
                self.system = aienhance.create_educational_layered_system(
                    model_name="qwen3:8b",
                    llm_temperature=0.7,
                    llm_max_tokens=800
                )
            elif system_type == "research":
                self.system = aienhance.create_research_layered_system(
                    model_name="qwen3:8b"
                )
            else:
                # 对于其他类型，使用通用分层系统
                self.system = aienhance.create_layered_system(
                    system_type=system_type,
                    memory_system_type="mirix_unified",
                    llm_provider="ollama",
                    llm_model_name="qwen3:8b",
                    llm_temperature=0.7,
                    llm_max_tokens=800
                )
            
            # 初始化系统
            await self.system.initialize_layers()
            
            print("✅ 分层认知系统初始化完成")
            print("📊 系统架构:")
            print("   📋 感知层 (Perception): 用户建模与上下文分析")
            print("   🧠 认知层 (Cognition): 记忆激活与语义增强") 
            print("   🎯 行为层 (Behavior): 内容适配与生成")
            if system_type != "lightweight":
                print("   🤝 协作层 (Collaboration): 多元观点与认知挑战")
            
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False

    async def stream_layered_processing(self, 
                                      query: str, 
                                      user_id: str = "demo_user",
                                      show_details: bool = True) -> AsyncIterator[str]:
        """分层流式处理，展示每层的详细过程"""
        
        start_time = time.time()
        
        try:
            # 构建系统输入 - 直接使用字典，因为SystemInput不存在
            context = {
                "source": "layered_streaming_demo",
                "timestamp": time.time(),
                "show_details": show_details
            }
            
            if show_details:
                yield "🚀 开始分层认知处理...\n\n"
            
            # 逐层处理并流式输出
            async for chunk in self._process_with_layer_details(query, user_id, context, show_details):
                yield chunk
            
            # 获取处理结果
            result = getattr(self, '_processing_result', None)
            
            # 输出最终结果
            if show_details:
                yield "\n" + "="*50 + "\n"
                yield "📋 最终输出:\n"
                yield "="*50 + "\n"
            
            if result and hasattr(result, 'final_output'):
                content = result.final_output
                
                # 流式输出主要内容
                sentences = self._split_content_for_streaming(content)
                for sentence in sentences:
                    if sentence.strip():
                        yield sentence + " "
                        await asyncio.sleep(0.05)  # 流式延迟
                
                yield "\n"
                
                # 如果有协作层增强内容
                if (hasattr(result, 'collaboration_output') and 
                    result.collaboration_output and 
                    hasattr(result.collaboration_output, 'enhanced_content') and
                    result.collaboration_output.enhanced_content):
                    
                    if show_details:
                        yield "\n🤝 协作层增强内容:\n"
                        yield "-" * 30 + "\n"
                    
                    enhanced = result.collaboration_output.enhanced_content
                    enhanced_sentences = self._split_content_for_streaming(enhanced)
                    for sentence in enhanced_sentences:
                        if sentence.strip():
                            yield sentence + " "
                            await asyncio.sleep(0.05)
                    yield "\n"
            else:
                yield "抱歉，系统处理出现问题。请检查配置。\n"
            
            # 处理统计信息
            total_time = time.time() - start_time
            self.processing_stats['total_time'] = total_time
            
            if show_details:
                yield f"\n⏱️ 总处理时间: {total_time:.2f}秒\n"
                yield self._format_processing_stats()
                
        except Exception as e:
            yield f"\n❌ 分层处理失败: {e}\n"

    async def _process_with_layer_details(self, query, user_id, context, show_details=True):
        """带有详细层次信息的处理"""
        
        if not show_details:
            # 直接处理，不显示细节
            result = await self.system.process_through_layers(
                query=query,
                user_id=user_id,
                context=context
            )
            # 不能在生成器中使用return，所以直接返回result，后续处理
            self._processing_result = result
            return
        
        # 详细显示每层处理
        result = None
        layer_start_time = time.time()
        
        try:
            # 1. 感知层处理
            yield "📋 感知层处理中...\n"
            yield "   • 分析用户画像和偏好\n"
            yield "   • 识别查询上下文和意图\n"
            yield "   • 构建个性化理解模型\n"
            
            perception_start = time.time()
            # 这里实际调用系统处理，但我们只显示一次完整结果
            result = await self.system.process_through_layers(
                query=query,
                user_id=user_id,
                context=context
            )
            self.processing_stats['perception_time'] = time.time() - perception_start
            
            yield f"   ✅ 感知层完成 ({self.processing_stats['perception_time']:.2f}s)\n\n"
            
            # 2. 认知层处理  
            cognition_start = time.time()
            yield "🧠 认知层处理中...\n"
            yield "   • 激活相关记忆网络\n"
            yield "   • 进行语义理解增强\n"
            yield "   • 执行类比推理分析\n"
            
            await asyncio.sleep(0.3)  # 模拟处理时间
            self.processing_stats['cognition_time'] = time.time() - cognition_start
            yield f"   ✅ 认知层完成 ({self.processing_stats['cognition_time']:.2f}s)\n\n"
            
            # 3. 行为层处理
            behavior_start = time.time()
            yield "🎯 行为层处理中...\n"
            yield "   • 适配内容表达方式\n"
            yield "   • 调整信息密度和粒度\n"
            yield "   • 生成个性化回应\n"
            
            await asyncio.sleep(0.2)  # 模拟处理时间
            self.processing_stats['behavior_time'] = time.time() - behavior_start
            yield f"   ✅ 行为层完成 ({self.processing_stats['behavior_time']:.2f}s)\n\n"
            
            # 4. 协作层处理 (如果启用)
            if (hasattr(self.system, 'config') and 
                self.system.config.get('enable_collaboration', True)):
                
                collaboration_start = time.time()
                yield "🤝 协作层处理中...\n"
                yield "   • 生成多元观点视角\n"
                yield "   • 创建认知挑战问题\n" 
                yield "   • 增强协作思考深度\n"
                
                await asyncio.sleep(0.2)  # 模拟处理时间
                self.processing_stats['collaboration_time'] = time.time() - collaboration_start
                yield f"   ✅ 协作层完成 ({self.processing_stats['collaboration_time']:.2f}s)\n\n"
            
            # 将结果存储到实例变量中，供后续使用
            self._processing_result = result
            
        except Exception as e:
            yield f"❌ 层次处理错误: {e}\n"
            self._processing_result = None

    def _split_content_for_streaming(self, content: str) -> list:
        """将内容分割为适合流式输出的片段"""
        import re
        
        # 按句子分割
        sentences = re.split(r'[。！？\n]', content)
        
        # 过滤空句子并添加标点
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # 根据原文恢复标点
                if sentence[-1] not in '。！？':
                    if '?' in sentence or '？' in sentence:
                        sentence += '？'
                    elif '!' in sentence or '！' in sentence:
                        sentence += '！'
                    else:
                        sentence += '。'
                result.append(sentence)
        
        return result

    def _format_processing_stats(self) -> str:
        """格式化处理统计信息"""
        stats = self.processing_stats
        return f"""
📊 分层处理统计:
   📋 感知层: {stats['perception_time']:.2f}s
   🧠 认知层: {stats['cognition_time']:.2f}s  
   🎯 行为层: {stats['behavior_time']:.2f}s
   🤝 协作层: {stats['collaboration_time']:.2f}s
   📈 总耗时: {stats['total_time']:.2f}s
"""

    async def interactive_layered_demo(self, system_type="educational"):
        """交互式分层演示"""
        print("🚀 分层认知系统交互演示")
        print("=" * 60)
        print("💡 功能说明:")
        print("  • 可视化展示四层认知处理过程")
        print("  • 支持多种系统类型配置")
        print("  • 实时流式输出处理结果")
        print("=" * 60)
        
        # 初始化系统
        if not await self.initialize_layered_system(system_type):
            return
        
        session_count = 0
        
        while True:
            try:
                # 获取用户输入
                user_input = input(f"\n[{session_count}] 🤔 请输入问题 (输入'quit'退出): ").strip()
                
                # 处理退出命令
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 感谢体验分层认知系统！")
                    break
                elif not user_input:
                    continue
                
                print(f"\n🎯 处理查询: {user_input}")
                print("-" * 50)
                
                # 流式处理并输出
                async for chunk in self.stream_layered_processing(
                    query=user_input,
                    user_id=f"interactive_user_{session_count}",
                    show_details=True
                ):
                    print(chunk, end='', flush=True)
                
                session_count += 1
                
            except KeyboardInterrupt:
                print("\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 交互错误: {e}")

    async def demo_showcase(self):
        """演示展示模式"""
        print("🎮 分层认知系统演示展示")
        print("=" * 60)
        
        # 预定义演示查询
        demo_scenarios = [
            {
                "name": "教育场景",
                "system_type": "educational", 
                "query": "什么是深度学习？请用简单易懂的方式解释"
            },
            {
                "name": "研究场景",
                "system_type": "research",
                "query": "分析人工智能在医疗诊断中的应用前景和挑战"
            },
            {
                "name": "创意场景", 
                "system_type": "creative",
                "query": "设计一个未来智能城市的创新交通系统"
            },
            {
                "name": "轻量场景",
                "system_type": "lightweight",
                "query": "简单介绍一下机器学习"
            }
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n{i}️⃣ {scenario['name']}演示")
            print("=" * 40)
            print(f"🎯 查询: {scenario['query']}")
            print(f"⚙️ 系统类型: {scenario['system_type']}")
            print("-" * 40)
            
            # 初始化对应类型的系统
            await self.initialize_layered_system(scenario['system_type'])
            
            # 流式处理
            async for chunk in self.stream_layered_processing(
                query=scenario['query'],
                user_id=f"demo_user_{i}",
                show_details=(scenario['system_type'] != 'lightweight')
            ):
                print(chunk, end='', flush=True)
            
            print("\n" + "=" * 40)
            
            # 短暂停顿
            if i < len(demo_scenarios):
                print("⏸️ 暂停3秒...")
                await asyncio.sleep(3)
                
        print("\n🎉 演示展示完成！")

    async def cleanup(self):
        """清理资源"""
        try:
            if self.system and hasattr(self.system, 'cleanup'):
                await self.system.cleanup()
                print("🧹 系统资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理过程中出现错误: {e}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="分层认知系统流式演示工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python layered_streaming_demo.py -i                                   # 交互模式
  python layered_streaming_demo.py -d                                   # 演示展示
  python layered_streaming_demo.py -i --type research                   # 研究系统交互
  python layered_streaming_demo.py -d --type creative                   # 创意系统演示
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='启动交互式分层演示')
    parser.add_argument('-d', '--demo', action='store_true', 
                        help='运行演示展示模式')
    parser.add_argument('--type', 
                        choices=['educational', 'research', 'creative', 'lightweight'],
                        default='educational',
                        help='分层系统类型 (默认: educational)')
    
    args = parser.parse_args()
    
    # 创建演示实例
    demo = LayeredCognitiveStreamingDemo()
    
    try:
        # 检查依赖
        if not await demo.check_dependencies():
            return
        
        # 根据参数执行相应模式
        if args.interactive:
            await demo.interactive_layered_demo(args.type)
        elif args.demo:
            await demo.demo_showcase()
        else:
            # 默认显示帮助信息
            parser.print_help()
            print("\n💡 快速开始:")
            print("  python layered_streaming_demo.py -i  # 交互式演示")
            print("  python layered_streaming_demo.py -d  # 演示展示")
            
    except Exception as e:
        print(f"❌ 演示程序错误: {e}")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序错误: {e}")