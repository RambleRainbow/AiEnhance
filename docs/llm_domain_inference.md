# LLM-based 领域推断系统

## 概述

本系统将感知层中的简单关键词匹配领域推断升级为基于大模型的智能推断，支持多模型协同调度架构，为不同业务功能提供可配置的LLM服务。

## 主要特性

- ✅ **智能领域推断**: 使用大模型替代关键词匹配，提供更准确的领域识别
- ✅ **多模型支持**: 为不同业务功能配置独立的LLM模型和参数
- ✅ **优雅降级**: 支持回退到关键词匹配机制
- ✅ **灵活配置**: 支持主要模型和备选模型配置
- ✅ **异步架构**: 完全异步实现，支持高并发
- ✅ **集成友好**: 无缝集成到现有感知层

## 系统架构

```
┌─────────────────────────────────────────────┐
│              感知层 (Perception Layer)        │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐ │
│  │    领域推断管理器 (DomainInferenceManager) │ │
│  │                                        │ │
│  │  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ LLM Provider │  │ LLM Provider │    │ │
│  │  │   (Primary)  │  │ (Fallback)   │    │ │
│  │  └──────────────┘  └──────────────┘    │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│        多LLM配置管理器 (MultiLLMConfigManager)  │
├─────────────────────────────────────────────┤
│ • domain_inference: qwen3:8b (T=0.1)       │
│ • creative_generation: qwen3:32b (T=0.8)   │
│ • analytical_reasoning: qwen3:14b (T=0.3)  │
│ • user_modeling: qwen3:8b (T=0.5)          │
└─────────────────────────────────────────────┘
```

## 快速开始

### 1. 基本使用

```python
from aienhance.core.domain_inference import (
    DomainInferenceConfig,
    DomainInferenceManager,
    LLMDomainInferenceProvider
)

# 创建配置
config = DomainInferenceConfig(
    llm_provider=your_llm_provider,
    model_name="qwen3:8b",
    temperature=0.1,
    max_tokens=300,
    timeout=10
)

# 创建并初始化提供商
provider = LLMDomainInferenceProvider(config)
await provider.initialize()

# 推断领域
result = await provider.infer_domains("如何学习Python编程？")
print(f"主要领域: {result.primary_domains}")
print(f"推理过程: {result.reasoning}")
```

### 2. 多模型配置

```python
from aienhance.core.multi_llm_config import (
    MultiLLMConfigManager,
    LLMModelConfig,
    BusinessFunctionLLMConfig
)

# 创建配置管理器
config_manager = MultiLLMConfigManager()

# 设置默认配置
default_config = LLMModelConfig(
    provider="ollama",
    model_name="qwen3:8b",
    temperature=0.7,
    max_tokens=800
)
config_manager.set_default_config(default_config)

# 为领域推断配置专门的模型
domain_config = BusinessFunctionLLMConfig(
    function_name="domain_inference",
    primary_model=LLMModelConfig(
        provider="ollama",
        model_name="qwen3:8b",
        temperature=0.1,  # 低温度确保一致性
        max_tokens=300
    )
)
config_manager.register_business_function(domain_config)
```

### 3. 集成到感知层

```python
from aienhance.core.perception_layer import PerceptionLayer

# 感知层配置
perception_config = {
    'domain_inference': {
        'llm_provider': your_llm_provider,
        'model_name': 'qwen3:8b',
        'temperature': 0.1,
        'max_tokens': 300,
        'fallback_to_keywords': True,
        'custom_domains': ['technology', 'science', 'education', 'business', 'art']
    }
}

# 创建感知层
perception_layer = PerceptionLayer(
    config=perception_config,
    memory_system=memory_system,
    llm_provider=main_llm_provider
)

await perception_layer.initialize()
```

## 配置选项

### DomainInferenceConfig

| 参数 | 类型 | 默认值 | 描述 |
|------|------|-------|------|
| `llm_provider` | Any | 必需 | LLM提供商实例 |
| `model_name` | str | None | 特定模型名称 |
| `temperature` | float | 0.1 | 温度参数（建议低温度） |
| `max_tokens` | int | 300 | 最大输出token数 |
| `timeout` | int | 10 | 请求超时时间 |
| `fallback_to_keywords` | bool | True | 是否回退到关键词匹配 |
| `custom_domains` | List[str] | None | 自定义领域列表 |

### 推荐配置

**领域推断**:
```python
{
    "provider": "ollama",
    "model_name": "qwen3:8b",
    "temperature": 0.1,  # 低温度确保一致性
    "max_tokens": 300,   # 较少token用于分类
    "timeout": 10
}
```

**创意任务**:
```python
{
    "provider": "ollama", 
    "model_name": "qwen3:32b",  # 更大模型
    "temperature": 0.8,         # 高温度增加创造性
    "max_tokens": 1200,
    "timeout": 30
}
```

**分析任务**:
```python
{
    "provider": "ollama",
    "model_name": "qwen3:14b",
    "temperature": 0.3,         # 中等温度
    "max_tokens": 1000,
    "timeout": 25
}
```

## API 参考

### DomainInferenceResult

推断结果数据结构：

```python
@dataclass
class DomainInferenceResult:
    primary_domains: List[str]      # 主要领域
    secondary_domains: List[str]    # 次要领域  
    confidence_scores: Dict[str, float]  # 置信度分数
    interdisciplinary: bool         # 是否跨学科
    reasoning: Optional[str]        # 推理过程
    metadata: Optional[Dict[str, Any]]  # 元数据
```

### DomainInferenceProvider

抽象接口：

```python
async def initialize() -> bool
    """初始化提供商"""

async def infer_domains(query: str, context: Optional[Dict] = None) -> DomainInferenceResult
    """推断查询涉及的领域"""

async def cleanup() -> None
    """清理资源"""
```

### DomainInferenceManager

管理器方法：

```python
async def register_provider(name: str, provider: DomainInferenceProvider) -> bool
    """注册领域推断提供商"""

async def infer_domains(query: str, provider_name: Optional[str] = None, context: Optional[Dict] = None) -> DomainInferenceResult
    """推断领域"""

def get_available_providers() -> List[str]
    """获取可用的提供商列表"""

def set_default_provider(name: str) -> bool
    """设置默认提供商"""
```

## 示例用例

### 1. 教育场景

```python
# 学习内容推荐
result = await provider.infer_domains("我想学习机器学习算法")
# 结果: primary_domains=['technology'], secondary_domains=['education', 'mathematics']

# 根据领域调整回答风格
if 'technology' in result.primary_domains:
    # 使用技术术语，提供代码示例
    pass
elif 'education' in result.primary_domains:
    # 使用教学语言，循序渐进
    pass
```

### 2. 内容分类

```python
queries = [
    "如何提高团队管理效率？",
    "人工智能的发展趋势",
    "绘画技巧和色彩搭配"
]

for query in queries:
    result = await provider.infer_domains(query)
    print(f"{query} -> {result.primary_domains}")
    
# 输出:
# 如何提高团队管理效率？ -> ['business']
# 人工智能的发展趋势 -> ['technology'] 
# 绘画技巧和色彩搭配 -> ['art']
```

### 3. 多模型协同

```python
# 不同业务功能使用不同模型
functions = {
    'domain_inference': 'qwen3:8b',    # 快速分类
    'creative_writing': 'qwen3:32b',   # 创意生成
    'code_analysis': 'qwen3:14b',      # 代码分析
    'user_modeling': 'qwen3:8b'        # 用户建模
}

for func_name, expected_model in functions.items():
    config = config_manager.get_config_for_function(func_name)
    print(f"{func_name}: {config.model_name}")
```

## 测试和验证

运行测试套件：

```bash
# 基础功能测试
uv run python tests/test_llm_domain_inference.py

# 配置系统演示
uv run python examples/multi_llm_config_example.py
```

## 性能优化

1. **模型选择**:
   - 分类任务使用较小模型（如qwen3:8b）
   - 创意任务使用大模型（如qwen3:32b）
   - 分析任务使用中等模型（如qwen3:14b）

2. **参数调优**:
   - 低温度（0.1）用于一致性要求高的任务
   - 高温度（0.8）用于创意性任务
   - 限制最大token数以控制延迟

3. **缓存策略**:
   - 考虑对常见查询进行结果缓存
   - 实现查询相似度匹配复用结果

4. **错误处理**:
   - 设置合理的超时时间
   - 实现优雅降级机制
   - 监控推断成功率

## 扩展性

系统设计支持以下扩展：

- **新的LLM提供商**: 实现`DomainInferenceProvider`接口
- **自定义领域**: 通过`custom_domains`参数配置
- **新的业务功能**: 通过`MultiLLMConfigManager`注册
- **复杂推理**: 扩展提示模板和结果解析逻辑

## 最佳实践

1. **配置管理**:
   - 将配置存储在配置文件中，而非硬编码
   - 为不同环境（开发/测试/生产）维护不同配置
   - 定期验证配置的有效性

2. **错误处理**:
   - 始终启用关键词匹配回退
   - 监控LLM调用成功率
   - 记录详细的错误信息用于调试

3. **性能监控**:
   - 监控推断延迟和准确性
   - 收集用户反馈验证推断质量
   - 定期评估不同模型的表现

4. **安全考虑**:
   - 验证输入查询长度
   - 过滤敏感信息
   - 限制API调用频率

## 更新日志

### v1.0.0
- ✅ 初始实现LLM-based领域推断
- ✅ 支持多模型配置管理
- ✅ 集成到感知层
- ✅ 提供回退机制
- ✅ 完整的测试套件和文档