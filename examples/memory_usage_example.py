"""
记忆系统使用示例
展示如何在实际场景中使用AiEnhance的记忆系统集成功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aienhance


async def educational_scenario_example():
    """教育场景使用示例"""
    print("🎓 教育场景 - 个性化学习助手")
    print("=" * 50)
    
    # 创建教育场景的认知系统，集成MIRIX记忆系统
    system = aienhance.create_system(
        system_type="educational",
        memory_system_type="mirix",
        api_key="your-mirix-api-key",  # 实际使用时替换为真实API密钥
        config_path="/path/to/mirix/config.yaml"  # 可选的配置文件路径
    )
    
    print("1. 系统初始化完成")
    status = system.get_system_status()
    print(f"   - 认知系统: {status['initialized']}")
    print(f"   - 记忆系统: {status['memory_system']['system_type']}")
    print(f"   - 配置类型: 教育场景优化 (低密度, 宏观粒度)")
    
    # 模拟学生学习过程
    student_id = "student_alice_001"
    
    print(f"\n2. 学生 {student_id} 开始学习session")
    
    # 学习查询序列
    learning_queries = [
        "什么是机器学习？",
        "监督学习和无监督学习有什么区别？",
        "能给我举个线性回归的例子吗？",
        "我还是不太理解过拟合的概念",
        "你能总结一下我今天学到的内容吗？"
    ]
    
    session_context = {"session_id": "learning_session_001", "subject": "machine_learning"}
    
    for i, query in enumerate(learning_queries, 1):
        print(f"\n   查询 {i}: {query}")
        
        try:
            # 处理查询（注意：实际运行需要安装MIRIX）
            # response = await system.process_query(query, student_id, session_context)
            # print(f"   响应: {response.content[:100]}...")
            # print(f"   记忆激活: {len(response.activated_memories)} 个相关记忆")
            # print(f"   认知负荷: {response.adaptation_info.cognitive_load:.2f}")
            
            print("   [模拟响应] 基于学生历史学习记录，提供个性化解释")
            print("   [模拟记忆] 关联之前的学习内容，建立知识连接")
            
        except Exception as e:
            print(f"   处理出错: {e}")
    
    print("\n3. 学习session总结")
    print("   - 系统自动记录了学生的学习轨迹")
    print("   - 识别了知识薄弱点（过拟合概念）")
    print("   - 建立了概念间的关联关系")


async def research_scenario_example():
    """研究场景使用示例"""
    print("\n🔬 研究场景 - 科研知识助手")
    print("=" * 50)
    
    # 创建研究场景的认知系统，集成Graphiti记忆系统
    system = aienhance.create_system(
        system_type="research",
        memory_system_type="graphiti",
        database_url="neo4j://localhost:7687",
        custom_config={
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "enable_temporal_queries": True
        }
    )
    
    print("1. 研究助手系统初始化")
    status = system.get_system_status()
    print(f"   - 认知系统: {status['initialized']}")
    print(f"   - 记忆系统: {status['memory_system']['system_type']}")
    print(f"   - 配置类型: 研究场景优化 (高密度, 微观粒度)")
    
    researcher_id = "researcher_bob_001"
    
    print(f"\n2. 研究员 {researcher_id} 进行文献调研")
    
    # 研究查询序列
    research_queries = [
        "最新的大语言模型架构有哪些突破？",
        "Transformer注意力机制的理论基础是什么？",
        "多模态学习在2024年有什么新进展？",
        "这些技术如何应用到认知科学研究中？",
        "帮我分析这些技术的潜在研究方向"
    ]
    
    research_context = {
        "session_id": "research_session_001", 
        "project": "cognitive_ai_research",
        "domain": "artificial_intelligence"
    }
    
    for i, query in enumerate(research_queries, 1):
        print(f"\n   研究查询 {i}: {query}")
        
        try:
            # 处理查询（注意：实际运行需要安装Graphiti）
            # response = await system.process_query(query, researcher_id, research_context)
            # print(f"   深度分析: {response.content[:150]}...")
            # print(f"   关联文献: {len(response.activated_memories)} 篇相关论文")
            # print(f"   知识图谱连接: {response.semantic_enhancement}")
            
            print("   [模拟响应] 基于知识图谱，提供深度的跨领域分析")
            print("   [模拟关联] 发现多个相关研究领域的潜在连接")
            
        except Exception as e:
            print(f"   处理出错: {e}")
    
    print("\n3. 研究洞察生成")
    print("   - 构建了多模态AI技术的知识图谱")
    print("   - 识别了认知科学与AI的交叉研究机会")
    print("   - 建议了3个潜在的研究方向")


async def memory_system_comparison():
    """不同记忆系统的对比示例"""
    print("\n⚖️ 记忆系统对比分析")
    print("=" * 50)
    
    # 对比不同记忆系统的特点
    memory_systems = [
        {
            "name": "MIRIX",
            "type": "mirix",
            "features": [
                "多代理记忆架构 (6种记忆类型)",
                "支持多模态输入 (文本、图像、语音)",
                "本地隐私保护存储",
                "PostgreSQL BM25全文搜索",
                "连续视觉数据捕获"
            ],
            "best_for": "个人助手、学习系统、隐私敏感场景",
            "config": {"api_key": "mirix-key", "privacy_mode": True}
        },
        {
            "name": "Mem0",
            "type": "mem0",
            "features": [
                "多层级记忆 (User/Session/Agent)",
                "91%更快的响应速度",
                "90%更低的Token使用",
                "自适应个性化",
                "与主流LLM集成"
            ],
            "best_for": "对话系统、客服机器人、高频交互场景",
            "config": {"model": "gpt-4o-mini", "enable_cache": True}
        },
        {
            "name": "Graphiti",
            "type": "graphiti",
            "features": [
                "时序感知知识图谱",
                "实体关系建模",
                "混合搜索 (语义+BM25)",
                "时间点查询支持",
                "复杂关系推理"
            ],
            "best_for": "研究系统、知识管理、复杂推理场景",
            "config": {"database_url": "neo4j://localhost:7687", "temporal_queries": True}
        }
    ]
    
    for system_info in memory_systems:
        print(f"\n📋 {system_info['name']} 记忆系统")
        print(f"   最适合: {system_info['best_for']}")
        print("   核心特性:")
        for feature in system_info['features']:
            print(f"   • {feature}")
        
        # 创建系统配置示例
        try:
            config = aienhance.MemorySystemConfig(
                system_type=system_info['type'],
                custom_config=system_info['config']
            )
            print(f"   ✅ 配置示例: {config.system_type} - {config.custom_config}")
        except Exception as e:
            print(f"   ❌ 配置错误: {e}")


def integration_guide():
    """集成指南"""
    print("\n📚 集成使用指南")
    print("=" * 50)
    
    print("""
🚀 快速开始:

1. 基础集成 (无外部记忆):
   system = aienhance.create_system("default")

2. 集成MIRIX:
   system = aienhance.create_system(
       system_type="educational",
       memory_system_type="mirix",
       api_key="your-api-key"
   )

3. 集成Mem0:
   system = aienhance.create_system(
       system_type="default", 
       memory_system_type="mem0",
       custom_config={"model": "gpt-4"}
   )

4. 集成Graphiti:
   system = aienhance.create_system(
       system_type="research",
       memory_system_type="graphiti", 
       database_url="neo4j://localhost:7687"
   )

💡 最佳实践:

• 教育场景: 使用MIRIX (多模态、隐私保护)
• 对话系统: 使用Mem0 (高性能、低延迟)  
• 研究分析: 使用Graphiti (知识图谱、复杂推理)

• 认知系统配置选择:
  - educational: 低密度输出、宏观粒度、支持辩证思维
  - research: 高密度输出、微观粒度、跨域类比推理
  - default: 平衡配置、通用场景适用

⚡ 异步处理:
   response = await system.process_query(query, user_id, context)

🔧 系统状态监控:
   status = system.get_system_status()
   print(f"记忆系统: {status['memory_system']}")
""")


async def main():
    """主示例函数"""
    print("🌟 AiEnhance 记忆系统集成使用示例")
    print("=" * 60)
    
    # 教育场景示例
    await educational_scenario_example()
    
    # 研究场景示例  
    await research_scenario_example()
    
    # 记忆系统对比
    await memory_system_comparison()
    
    # 集成指南
    integration_guide()
    
    print("\n" + "=" * 60)
    print("✨ 示例完成! 开始构建你的记忆增强AI系统吧!")


if __name__ == "__main__":
    asyncio.run(main())