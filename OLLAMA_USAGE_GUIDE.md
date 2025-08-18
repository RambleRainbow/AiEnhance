# AiEnhance + Ollama 使用指南

## 🎯 概述

本指南介绍如何将AiEnhance记忆-认知协同系统与Ollama qwen3:8b模型集成，实现完整的智能对话和认知增强功能。

## 🛠️ 环境准备

### 1. 安装Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 下载 https://ollama.ai/download/windows
```

### 2. 启动Ollama服务

```bash
ollama serve
```

### 3. 安装推荐模型

```bash
# 安装LLM模型
ollama pull qwen3:8b

# 安装嵌入模型（可选）
ollama pull bge-m3
```

### 4. 验证安装

```bash
# 检查可用模型
ollama list

# 测试模型
ollama run qwen3:8b "你好"
```

## 🚀 快速开始

### 基础用法

```python
import asyncio
import aienhance

async def basic_usage():
    # 创建系统 - 最简配置
    system = aienhance.create_system(
        system_type="educational",    # 教育模式
        llm_provider="ollama",        # 使用Ollama
        llm_model_name="qwen3:8b"     # qwen3:8b模型
    )
    
    # 处理查询
    response = await system.process_query(
        query="什么是人工智能？",
        user_id="user123"
    )
    
    # 查看结果
    print(f"AI回答: {response.content}")
    print(f"思维模式: {response.user_profile.cognitive.thinking_mode.value}")
    print(f"适配密度: {response.adaptation_info.density_level.value}")

# 运行
asyncio.run(basic_usage())
```

### 完整配置

```python
import aienhance

# 创建完整配置的系统
system = aienhance.create_system(
    # 系统类型
    system_type="educational",           # default | educational | research
    
    # LLM配置
    llm_provider="ollama",
    llm_model_name="qwen3:8b",
    llm_api_base="http://localhost:11434",
    llm_temperature=0.7,                 # 0.0-1.0，越高越有创造性
    llm_max_tokens=1000,                 # 最大输出长度
    
    # 嵌入模型配置（可选）
    embedding_provider="ollama",
    embedding_model_name="bge-m3",
    embedding_api_base="http://localhost:11434"
)
```

## 📚 系统配置类型

### 1. 默认系统 (default)

```python
system = aienhance.create_system(
    system_type="default",
    llm_provider="ollama",
    llm_model_name="qwen3:8b",
    llm_temperature=0.5              # 平衡的创造性
)
```

**特点：**
- 均衡的输出密度
- 适中的认知负荷
- 通用场景适用

### 2. 教育系统 (educational)

```python
system = aienhance.create_system(
    system_type="educational",
    llm_provider="ollama", 
    llm_model_name="qwen3:8b",
    llm_temperature=0.3              # 较低温度，更稳定
)
```

**特点：**
- 低密度输出，易于理解
- 支持协作层功能
- 循序渐进的解释方式
- 自适应难度调整

### 3. 研究系统 (research)

```python
system = aienhance.create_system(
    system_type="research",
    llm_provider="ollama",
    llm_model_name="qwen3:8b", 
    llm_temperature=0.8              # 较高温度，更有创造性
)
```

**特点：**
- 高密度输出，信息丰富
- 支持类比推理
- 创造性关联
- 深度分析能力

## 🎮 实际使用示例

### 示例1：教育对话

```python
import asyncio
import aienhance

async def educational_chat():
    system = aienhance.create_system(
        system_type="educational",
        llm_provider="ollama",
        llm_model_name="qwen3:8b",
        llm_temperature=0.3
    )
    
    queries = [
        "什么是机器学习？我是初学者",
        "监督学习和无监督学习有什么区别？",
        "请举个深度学习的实际应用例子"
    ]
    
    for query in queries:
        response = await system.process_query(
            query=query,
            user_id="student001"
        )
        
        print(f"👤 学生: {query}")
        print(f"🤖 老师: {response.content}")
        print(f"📊 适配: {response.adaptation_info.density_level.value}密度")
        print("-" * 50)

asyncio.run(educational_chat())
```

### 示例2：研究助手

```python
async def research_assistant():
    system = aienhance.create_system(
        system_type="research",
        llm_provider="ollama",
        llm_model_name="qwen3:8b",
        llm_temperature=0.8
    )
    
    response = await system.process_query(
        query="分析深度学习在医疗影像诊断中的最新进展和挑战",
        user_id="researcher001",
        context={"domain": "medical_ai"}
    )
    
    print(f"🔬 研究分析: {response.content}")
    print(f"🧠 认知负荷: {response.adaptation_info.cognitive_load:.2f}")

asyncio.run(research_assistant())
```

### 示例3：多轮对话

```python
async def multi_turn_conversation():
    system = aienhance.create_system(
        system_type="default",
        llm_provider="ollama",
        llm_model_name="qwen3:8b"
    )
    
    user_id = "conversation_user"
    
    conversations = [
        "请介绍一下Python编程语言",
        "Python有哪些主要的应用领域？",
        "能推荐一些Python学习资源吗？"
    ]
    
    for i, query in enumerate(conversations, 1):
        response = await system.process_query(
            query=query,
            user_id=user_id,
            context={"turn": i}
        )
        
        print(f"第{i}轮对话:")
        print(f"👤 用户: {query}")
        print(f"🤖 助手: {response.content}")
        print(f"📈 用户画像更新: {response.user_profile.cognitive.thinking_mode.value}")
        print()

asyncio.run(multi_turn_conversation())
```

## 🔧 高级配置

### 性能优化

```python
# 快速响应配置
fast_system = aienhance.create_system(
    system_type="default",
    llm_provider="ollama",
    llm_model_name="qwen3:8b",
    llm_temperature=0.3,
    llm_max_tokens=300               # 限制输出长度
)

# 高质量输出配置
quality_system = aienhance.create_system(
    system_type="research", 
    llm_provider="ollama",
    llm_model_name="qwen3:8b",
    llm_temperature=0.7,
    llm_max_tokens=2000              # 允许长输出
)
```

### 错误处理

```python
async def robust_query_processing():
    system = aienhance.create_system(
        system_type="educational",
        llm_provider="ollama",
        llm_model_name="qwen3:8b"
    )
    
    try:
        response = await system.process_query(
            query="复杂的技术问题",
            user_id="user123"
        )
        
        if response.content:
            print(f"成功: {response.content}")
        else:
            print("警告: 无内容生成")
            
    except Exception as e:
        print(f"错误: {e}")
        # 降级处理或重试逻辑
```

## 📊 性能监控

```python
import time

async def performance_monitoring():
    system = aienhance.create_system(
        system_type="default",
        llm_provider="ollama", 
        llm_model_name="qwen3:8b"
    )
    
    start_time = time.time()
    
    response = await system.process_query(
        query="测试查询",
        user_id="perf_user"
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"响应时间: {duration:.2f}秒")
    print(f"响应长度: {len(response.content)}字符")
    print(f"生成速度: {len(response.content)/duration:.1f}字符/秒")
```

## 🚨 故障排除

### 常见问题

#### 1. Ollama连接失败
```
❌ 无法连接Ollama服务
```

**解决方案:**
```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 启动Ollama服务
ollama serve
```

#### 2. 模型未找到
```
❌ 模型qwen3:8b不存在
```

**解决方案:**
```bash
# 拉取模型
ollama pull qwen3:8b

# 验证模型
ollama list
```

#### 3. 响应为空
```
⚠️ response.content为空
```

**可能原因:**
- Ollama服务不稳定
- 模型加载中
- 查询过于复杂

**解决方案:**
- 检查Ollama日志
- 简化查询内容
- 调整temperature参数

#### 4. 响应速度慢
```
⚠️ 响应时间过长
```

**优化方案:**
- 减少max_tokens参数
- 降低temperature
- 使用更小的模型

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 创建系统时启用调试
system = aienhance.create_system(
    system_type="default",
    llm_provider="ollama",
    llm_model_name="qwen3:8b",
    debug=True  # 如果支持调试模式
)
```

## 📝 最佳实践

### 1. 模型选择
- **轻量级应用**: 使用较小模型或降低max_tokens
- **高质量需求**: 使用qwen3:8b等大模型
- **多语言支持**: 选择支持目标语言的模型

### 2. 温度设置
- **事实查询**: temperature=0.1-0.3
- **创意内容**: temperature=0.7-0.9
- **平衡模式**: temperature=0.5-0.7

### 3. 系统类型选择
- **教学场景**: educational系统
- **研究分析**: research系统  
- **通用对话**: default系统

### 4. 性能优化
- 合理设置max_tokens
- 使用连接池（如适用）
- 实现响应缓存
- 监控系统资源

## 🔗 相关链接

- [Ollama官网](https://ollama.ai/)
- [qwen3模型文档](https://github.com/QwenLM/Qwen)
- [AiEnhance项目README](./README.md)
- [开发模式启动指南](./start-dev.sh)

---

🎉 现在您已经准备好使用AiEnhance + Ollama构建智能应用了！