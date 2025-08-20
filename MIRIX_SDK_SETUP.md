# MIRIX SDK 集成指南

本项目已从复杂的Docker/HTTP配置模式迁移到简化的MIRIX Python SDK模式。

## 快速开始

### 1. 安装依赖

```bash
# 安装MIRIX SDK
pip install mirix

# 或者安装项目依赖（已包含mirix）
pip install -e .
```

### 2. 配置API密钥

MIRIX SDK使用Google Gemini 2.0 Flash模型，需要Google API密钥：

```bash
# 设置环境变量
export GOOGLE_API_KEY="your-google-api-key"

# 或在.env文件中设置
echo "GOOGLE_API_KEY=your-google-api-key" >> .env
```

### 3. 使用新的SDK配置

现在系统默认使用 `mirix_sdk` 适配器：

```python
import aienhance

# 创建使用MIRIX SDK的系统
system = aienhance.create_system(
    system_type="educational",
    memory_system_type="mirix_sdk",  # 使用SDK适配器
    llm_provider="ollama",
    llm_model_name="qwen3:8b"
)
```

## 配置对比

### 旧配置（Docker/HTTP模式）
```python
# 需要复杂的Docker配置
memory_system_type="mirix"  # 或 "mirix_http"
# 需要运行Docker容器
# 需要配置PostgreSQL
# 需要复杂的HTTP API设置
```

### 新配置（SDK模式）
```python
# 简单的SDK配置
memory_system_type="mirix_sdk"
# 只需要Google API密钥
# 无需Docker或数据库设置
# 云端托管的记忆系统
```

## 主要优势

### 🚀 简化部署
- **无需Docker**: 不再需要复杂的容器化配置
- **无需数据库**: 不需要本地PostgreSQL设置
- **即装即用**: `pip install mirix` 后立即可用

### ☁️ 云端记忆
- **托管服务**: 记忆存储在MIRIX云端
- **高可用性**: 无需担心本地服务故障
- **自动备份**: 云端自动处理数据备份

### 🔧 维护成本降低
- **无基础设施**: 不需要维护Docker容器
- **自动更新**: MIRIX SDK自动获得最新功能
- **简化调试**: 减少了本地服务相关的问题

## 环境变量配置

在`.env`文件中添加：

```bash
# MIRIX SDK配置
GOOGLE_API_KEY=your-google-api-key-here

# 其他配置保持不变
OLLAMA_HOST=http://localhost:11434
```

## 代码示例

### 基本使用
```python
from aienhance.memory.adapters.mirix_sdk_adapter import MirixSdkAdapter
from aienhance.memory.interfaces import MemorySystemConfig, UserContext, MemoryEntry, MemoryType
import asyncio

async def main():
    # 配置
    config = MemorySystemConfig(
        api_key="your-google-api-key"
    )
    
    # 初始化适配器
    adapter = MirixSdkAdapter(config)
    await adapter.initialize()
    
    # 添加记忆
    user_context = UserContext(user_id="test_user", session_id="session_1")
    memory = MemoryEntry(
        content="用户喜欢学习人工智能",
        memory_type=MemoryType.SEMANTIC,
        user_context=user_context
    )
    
    memory_id = await adapter.add_memory(memory)
    print(f"记忆已添加: {memory_id}")
    
    # 对话
    response = await adapter.chat_with_memory(
        "告诉我关于机器学习的内容",
        user_context
    )
    print(f"AI回复: {response}")

asyncio.run(main())
```

### 在AiEnhance中使用
```python
import aienhance
import asyncio

async def main():
    # 创建系统
    system = aienhance.create_system(
        system_type="educational",
        memory_system_type="mirix_sdk",
        llm_provider="ollama",
        llm_model_name="qwen3:8b"
    )
    
    # 处理查询
    async with system:
        response = await system.process_query(
            query="什么是深度学习？",
            user_id="demo_user"
        )
        print(response.content)

asyncio.run(main())
```

## 迁移指南

### 从Docker模式迁移

1. **停止Docker服务**
   ```bash
   docker-compose down
   ```

2. **安装MIRIX SDK**
   ```bash
   pip install mirix
   ```

3. **更新配置**
   ```python
   # 旧配置
   memory_system_type="mirix"
   
   # 新配置
   memory_system_type="mirix_sdk"
   ```

4. **设置API密钥**
   ```bash
   export GOOGLE_API_KEY="your-key"
   ```

5. **测试新配置**
   ```bash
   python ai.py "测试MIRIX SDK集成"
   ```

## 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保安装了MIRIX
   pip install mirix
   ```

2. **API密钥错误**
   ```bash
   # 检查环境变量
   echo $GOOGLE_API_KEY
   ```

3. **连接测试失败**
   ```python
   # 在Python中测试
   from mirix import Mirix
   agent = Mirix(api_key="your-key")
   response = agent.add("test message")
   print(response)
   ```

## 配置文件示例

### .env.example
```bash
# MIRIX SDK配置
GOOGLE_API_KEY=your-google-api-key-here

# Ollama配置
OLLAMA_HOST=http://localhost:11434

# 日志配置
LOG_LEVEL=INFO
```

## 性能对比

| 特性 | Docker模式 | SDK模式 |
|------|------------|---------|
| 启动时间 | 30-60秒 | 1-3秒 |
| 内存占用 | 高（Docker+DB） | 低（仅SDK） |
| 配置复杂度 | 高 | 低 |
| 维护成本 | 高 | 低 |
| 网络依赖 | 本地网络 | 互联网 |
| 数据位置 | 本地 | 云端 |

推荐在开发和生产环境中都使用SDK模式，除非有特殊的本地部署需求。