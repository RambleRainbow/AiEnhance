# AiEnhance - 记忆-认知协同系统

一个基于深度学习和认知科学的AI认知增强系统，实现记忆-认知协同处理。

## 概述

本项目实现了一个完整的记忆-认知协同系统，超越传统RAG（Retrieval-Augmented Generation）模式，构建具备"记忆过滤与重构能力、语义显化与联想能力、认知补全与放大能力"的智能系统。

## 核心特性

### 🏗️ 四层架构
- **感知层** - 用户建模和情境分析
- **认知层** - 记忆激活、语义增强、类比推理
- **行为层** - 自适应输出
- **协作层** - 人机认知协作

### 🧠 核心能力
- **多元化记忆** - 支持多种记忆系统（MIRIX SDK、Mem0、Graphiti）
- **简化部署** - MIRIX SDK集成，无需复杂Docker配置  
- **灵活LLM** - 多LLM提供商支持（Ollama、OpenAI、Anthropic）
- **认知协作** - 辩证视角、认知挑战、用户建模
- **即装即用** - pip install即可开始使用

## 设计理念

系统设计立足于以下核心理念：

1. **记忆驱动** - 以记忆为核心的认知处理
2. **协同增强** - AI与人类共构认知体系
3. **适应性** - 根据用户特征动态调整

## 技术栈

- **语言**: Python 3.12.9
- **包管理**: uv
- **代码质量**: ruff
- **版本控制**: Git
- **容器化**: Docker + Docker Compose
- **AI框架**: Ollama (本地LLM)

## 🚀 快速开始

### 环境要求

- Python 3.12.9+
- UV包管理器（推荐）或pip
- Ollama (本地LLM服务)

### 安装

```bash
# 使用UV包管理器（推荐）
git clone https://github.com/your-username/AiEnhance.git
cd AiEnhance
uv sync

# 或使用传统pip方式
pip install -e .
```

### 运行示例

#### 命令行界面
```bash
# 使用UV
uv run python cli_example.py "什么是人工智能？"
uv run python cli_example.py -i  # 交互模式

# 或使用传统方式
python cli_example.py "什么是人工智能？"
```

#### Gradio Web界面
```bash
# 使用UV
uv run python gradio_interface.py

# 或使用传统方式  
python gradio_interface.py
```

访问 `http://localhost:7860` 开始使用Web界面。

### Ollama设置

首次使用需要安装和配置Ollama：

```bash
# 安装Ollama
# macOS
brew install ollama

# Linux  
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 安装推荐模型
ollama pull qwen3:8b
ollama pull bge-m3:latest
```

## 📁 项目结构

```
AiEnhance/
├── aienhance/              # 核心包
│   ├── core/              # 核心系统
│   ├── perception/        # 感知层
│   ├── cognition/         # 认知层
│   ├── behavior/          # 行为层
│   ├── collaboration/     # 协作层
│   ├── memory/            # 记忆系统适配器
│   └── llm/               # LLM适配器
├── cli_example.py         # 命令行示例
├── gradio_interface.py    # Web界面
├── tests/                 # 测试文件
├── scripts/               # 辅助脚本
├── docker/                # Docker配置
└── docs/                  # 文档
```

## 开发

### 代码质量检查
```bash
uv run ruff check .    # 代码检查
uv run ruff format .   # 代码格式化
```

### 运行测试
```bash
uv run python -m pytest tests/
```

## 使用示例

### Python API

```python
import aienhance

# 创建系统
system = aienhance.create_layered_system(
    system_type="educational",
    llm_provider="ollama",
    llm_model_name="qwen3:8b"
)

# 处理查询
response = await system.process_query(
    query="什么是人工智能？",
    user_id="user123"
)

print(response.content)
```

## 文档

- [Gradio界面使用指南](GRADIO_INTERFACE.md)
- [系统设计文档](docs/design/memory-cognitive-system-design.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)