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

## 安装部署

### 环境要求

- Python 3.12.9+
- Docker & Docker Compose
- Ollama (本地LLM服务)

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/AiEnhance.git
cd AiEnhance

# 2. 安装Ollama并启动服务
# macOS
brew install ollama
ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# 3. 安装推荐模型
./setup-ollama.sh

# 4. 启动外部依赖服务 (开发模式)
./start-dev.sh

# 5. 本地运行主应用
uv run python main.py
```

### 开发模式

```bash
# 1. 启动外部依赖服务
./start-dev.sh

# 2. 安装Python依赖
uv sync

# 3. 本地运行主应用
uv run python main.py

# 4. 测试协作功能
uv run python test_collaboration_layer.py

# 5. 代码检查和格式化
uv run ruff check .
uv run ruff format .

# 6. 停止外部依赖服务
docker compose down
```

### 生产部署

```bash
# 完整应用栈部署
./docker-start.sh

# 或手动部署
docker compose -f docker-compose.full.yml up -d
```

## 推荐模型

### LLM模型
- **qwen3:8b** - 通义千问3.0，8B参数，最新一代中文大语言模型

### 嵌入模型
- **bge-m3** - 多语言、多功能、多粒度嵌入模型，支持中英文

### 安装模型

```bash
# 自动安装推荐模型
./setup-ollama.sh

# 手动安装
ollama pull qwen3:8b
ollama pull bge-m3
```

## 项目结构

```
AiEnhance/
├── aienhance/                 # 核心模块
│   ├── perception/           # 感知层
│   ├── cognition/            # 认知层
│   ├── behavior/             # 行为层
│   ├── collaboration/        # 协作层
│   ├── memory/               # 记忆系统
│   ├── llm/                  # LLM接口
│   └── core/                 # 核心系统
├── docker/                   # Docker配置
├── docs/                     # 文档
├── tests/                    # 测试
├── docker-compose.yml        # 服务编排
├── docker-start.sh          # 启动脚本
├── setup-ollama.sh          # 模型安装脚本
└── main.py                  # 主入口
```

## 使用示例

### 基本使用

```python
from aienhance.core import MemoryCognitiveSystem

# 创建系统实例
system = MemoryCognitiveSystem(
    system_type="educational",
    memory_system_type="mirix",
    llm_provider="ollama"
)

# 处理查询
response = await system.process_query(
    query="什么是人工智能？",
    user_id="user123"
)

print(response.content)
```

### Docker部署

```bash
# 启动完整服务栈
./docker-start.sh

# 启动时包含管理界面
./docker-start.sh --with-management

# 查看服务状态
docker compose ps
```

### 协作功能测试

```bash
# 测试协作层功能
python test_collaboration_layer.py

# 测试完整集成
python test_docker_integration.py
```

## 核心功能

### 🎭 辩证视角生成
- 对立观点自动生成
- 多学科视角切换（数学、物理、心理学、经济学、社会学、哲学）
- 利益相关者分析

### 🧠 认知挑战
- **假设质疑** - 识别和挑战核心前提
- **盲点检测** - 发现思维盲点
- **复杂性扩展** - 系统性思维训练
- **创意激发** - 突破思维定势

### 🤝 智能协作
- 用户认知建模
- 协作策略自适应
- 效果评估和优化

### 🐳 企业级部署
- Docker容器化
- 微服务架构
- 健康检查和监控
- 一键部署脚本

## 文档

详细的设计文档和使用指南：

- [系统设计文档](docs/design/memory-cognitive-system-design.md)
- [协作层实现总结](COLLABORATION_LAYER_SUMMARY.md)
- [LLM集成指南](LLM_INTEGRATION_SUMMARY.md)
- [Docker部署指南](DOCKER_DEPLOYMENT.md)

## 开发路线

项目按照以下阶段逐步开发：

1. **第一阶段** - 基础框架 ✅
2. **第二阶段** - 记忆系统集成 ✅
3. **第三阶段** - LLM接口抽象 ✅
4. **第四阶段** - 协作层实现 ✅
5. **第五阶段** - 生产部署优化 🚧

## 技术特色

- **模块化设计** - 高度可扩展的架构
- **多提供商支持** - 灵活的LLM和记忆系统选择
- **认知科学驱动** - 基于认知科学理论的设计
- **企业级** - 生产就绪的部署方案

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

- 项目地址：https://github.com/your-username/AiEnhance
- 问题反馈：[Issues](https://github.com/your-username/AiEnhance/issues)

---

🎉 **恭喜！** 你已经成功设置了一个具备深度认知协作能力的AI系统！