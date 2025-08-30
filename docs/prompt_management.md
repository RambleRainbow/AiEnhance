# 集中式提示词管理系统

## 概述

提示词管理系统为AiEnhance项目提供统一的LLM提示词模板管理和渲染服务。作为系统中变更最频繁的内容，提示词需要在一个一致性好、可读性强的环境下进行精细管理。

## 主要特性

- ✅ **集中式管理**: 所有提示词模板统一存储和管理
- ✅ **版本控制**: 支持模板版本管理和向后兼容
- ✅ **分类组织**: 按业务功能分类组织模板
- ✅ **变量渲染**: 灵活的模板变量替换系统
- ✅ **元数据支持**: 包含描述、推荐参数等元数据
- ✅ **扩展性**: 可轻松添加新模板和类别

## 系统架构

```
┌─────────────────────────────────────────────┐
│            提示词管理层 (Prompt Layer)        │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐ │
│  │      PromptManager (接口)              │ │
│  │  ┌──────────────────────────────────┐  │ │
│  │  │   StaticPromptManager (实现)     │  │ │
│  │  │                                  │  │ │
│  │  │  ┌─────────────────────────────┐ │  │ │
│  │  │  │     模板分类存储结构        │ │  │ │
│  │  │  │ • domain_inference          │ │  │ │
│  │  │  │ • user_modeling             │ │  │ │
│  │  │  │ • cognitive_analysis        │ │  │ │
│  │  │  └─────────────────────────────┘ │  │ │
│  │  └──────────────────────────────────┘  │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         业务层调用 (Business Layer)          │
├─────────────────────────────────────────────┤
│ • DomainInferenceProvider                   │
│ • UserModelingProvider                      │
│ • CognitiveAnalysisProvider                 │
└─────────────────────────────────────────────┘
```

## 快速开始

### 1. 基本使用

```python
from aienhance.core.prompts import render_prompt, get_prompt_template

# 渲染提示词
prompt = render_prompt(
    name="domain_inference_basic",
    variables={
        "domains": "technology, science, education",
        "query": "如何学习Python编程？",
        "context": {"level": "beginner"}
    }
)

# 获取模板信息
template = get_prompt_template("domain_inference_basic")
print(f"模板版本: {template.version}")
print(f"推荐温度: {template.temperature}")
```

### 2. 列出可用模板

```python
from aienhance.core.prompts import list_available_prompts

# 列出所有模板
all_prompts = list_available_prompts()

# 按类别列出
domain_prompts = list_available_prompts("domain_inference")
user_prompts = list_available_prompts("user_modeling")
```

### 3. 添加自定义模板

```python
from aienhance.core.prompts import get_prompt_manager, PromptTemplate

manager = get_prompt_manager()

custom_template = PromptTemplate(
    name="custom_analysis",
    version="1.0",
    template="分析以下内容：{content}\n要求：{requirements}",
    description="自定义分析模板",
    variables=["content", "requirements"],
    category="custom",
    temperature=0.3,
    max_tokens=400
)

success = manager.add_template(custom_template)
```

## 内置模板库

### 领域推断 (domain_inference)

#### domain_inference_basic
- **用途**: 基础领域推断，识别查询涉及的专业领域
- **变量**: `domains`, `query`, `context_section`
- **推荐参数**: T=0.1, Max=300

#### domain_inference_advanced
- **用途**: 高级跨学科领域分析，提供详细的领域深度评估
- **变量**: `domains`, `query`, `context`
- **推荐参数**: T=0.2, Max=500

### 用户建模 (user_modeling)

#### cognitive_analysis
- **用途**: 用户认知特征分析，识别思维模式和认知复杂度
- **变量**: `domain_context`, `current_query`, `historical_data`
- **推荐参数**: T=0.3, Max=400

#### learning_style_analysis
- **用途**: 学习风格识别，分析用户的学习偏好和习惯
- **变量**: `query`, `domain`, `interaction_history`
- **推荐参数**: T=0.4, Max=450

### 认知分析 (cognitive_analysis)

#### context_analysis
- **用途**: 用户情境分析，评估任务环境和约束条件
- **变量**: `query`, `background`, `temporal_context`
- **推荐参数**: T=0.3, Max=500

#### complexity_assessment
- **用途**: 问题复杂度评估，分析认知负荷和解决难度
- **变量**: `problem_description`, `domain_scope`, `user_background`
- **推荐参数**: T=0.2, Max=400

## 模板设计规范

### 1. 结构化设计

```python
# 好的模板设计示例
template = """你是一个专业的{expert_type}。请分析以下{analysis_target}：

{input_content}

分析要求：
{requirements}

请以JSON格式输出结果：
{output_format}

请确保输出有效的JSON格式。"""
```

### 2. 变量命名约定

- **输入类变量**: `query`, `content`, `input_data`
- **上下文类变量**: `context`, `background`, `historical_data`
- **配置类变量**: `domains`, `requirements`, `constraints`
- **输出类变量**: `output_format`, `example_output`

### 3. 输出格式规范

所有涉及结构化输出的模板应该：
- 明确指定JSON格式要求
- 提供清晰的输出示例
- 包含字段说明和数据类型
- 强调格式有效性要求

## 版本管理策略

### 1. 版本号规则

使用语义化版本号：`主版本.次版本`
- **主版本**: 破坏性变更（如变量名变更）
- **次版本**: 功能增加或非破坏性改进

### 2. 向后兼容

```python
# 获取最新版本（推荐）
template = get_prompt_template("domain_inference_basic")

# 获取特定版本（兼容性需求）
template_v1 = get_prompt_template("domain_inference_basic", "1.0")
```

### 3. 废弃策略

- 保留至少2个主版本的向后兼容
- 提供废弃警告和迁移指南
- 在文档中明确标记废弃版本

## 性能优化

### 1. 模板设计优化

```python
# 推荐：简洁明确的模板
template = "分析{content}，输出JSON格式：{format}"

# 避免：过度复杂的嵌套模板
complex_template = """
{%- if condition1 %}
  {%- for item in items %}
    {%- if item.type == 'complex' %}
      // 复杂的嵌套逻辑...
    {%- endif %}
  {%- endfor %}
{%- endif %}
"""
```

### 2. 缓存策略

```python
# 对于频繁使用的模板，可以考虑预渲染缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_template(name: str, version: str = None):
    return get_prompt_template(name, version)
```

### 3. 模板长度控制

- **基础模板**: < 500字符
- **标准模板**: < 1000字符  
- **复杂模板**: < 2000字符
- **超长模板**: 需要特殊审查

## 最佳实践

### 1. 模板开发流程

1. **需求分析** - 明确模板用途和目标
2. **设计草案** - 创建初始模板结构
3. **变量设计** - 定义清晰的变量接口
4. **测试验证** - 多场景测试模板效果
5. **文档编写** - 完善使用说明和示例
6. **版本发布** - 正式注册到系统中

### 2. 质量保证

```python
# 模板质量检查清单
def validate_template(template: PromptTemplate) -> bool:
    checks = [
        len(template.name) > 0,  # 名称非空
        len(template.variables) > 0,  # 有定义变量
        template.temperature >= 0.0 and template.temperature <= 2.0,  # 温度合理
        template.max_tokens > 0,  # token数合理
        len(template.description) > 10,  # 描述详细
    ]
    return all(checks)
```

### 3. 监控和维护

- **效果监控**: 跟踪不同模板的LLM响应质量
- **使用统计**: 记录模板使用频率和场景
- **错误追踪**: 监控模板渲染失败和变量缺失
- **定期审查**: 季度审查模板有效性和改进需求

## 扩展指南

### 1. 添加新业务类别

```python
# 在prompts.py中添加新的初始化方法
def _register_new_category_prompts(self):
    """注册新类别相关提示词"""
    
    new_template = PromptTemplate(
        name="new_category_basic",
        version="1.0",
        template="...",  # 模板内容
        description="新类别基础模板",
        variables=["var1", "var2"],
        category="new_category",
        temperature=0.5,
        max_tokens=400
    )
    
    self._register_template(new_template)

# 在_initialize_default_templates中调用
def _initialize_default_templates(self):
    # 现有初始化...
    self._register_new_category_prompts()
```

### 2. 自定义渲染逻辑

```python
class CustomPromptManager(StaticPromptManager):
    """自定义提示词管理器"""
    
    def render_prompt(self, name: str, variables: Dict[str, Any], version: Optional[str] = None) -> str:
        # 自定义渲染逻辑
        template = self.get_prompt(name, version)
        
        # 添加自定义预处理
        processed_variables = self._preprocess_variables(variables)
        
        # 调用父类方法
        return super().render_prompt(name, processed_variables, version)
    
    def _preprocess_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """自定义变量预处理"""
        # 实现自定义逻辑
        return variables
```

## 故障排除

### 常见问题

1. **模板未找到**
   ```
   ValueError: Prompt template 'xxx' not found
   ```
   解决：检查模板名称拼写，确认模板已注册

2. **变量缺失**
   ```
   ValueError: Missing required variable 'xxx' for prompt 'yyy'
   ```
   解决：检查传入的variables字典，补充缺失变量

3. **版本不存在**
   ```
   ValueError: Version 'x.x' of prompt 'yyy' not found
   ```
   解决：检查版本号，或使用None获取最新版本

### 调试技巧

```python
# 1. 检查模板信息
manager = get_prompt_manager()
info = manager.get_template_info("template_name")
print(f"需要的变量: {info['variables']}")

# 2. 验证渲染结果
try:
    result = render_prompt("template_name", variables)
    print("渲染成功:", result[:100])
except Exception as e:
    print("渲染失败:", e)

# 3. 列出所有可用模板
prompts = list_available_prompts()
print("可用模板:", prompts)
```

## 更新日志

### v1.0.0
- ✅ 初始实现集中式提示词管理
- ✅ 支持基础模板注册和渲染
- ✅ 实现版本管理系统
- ✅ 提供完整的内置模板库
- ✅ 集成到领域推断系统