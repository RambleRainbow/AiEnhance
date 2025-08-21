# 🚀 AiEnhance 快速开始指南

## 🛠️ 安装

```bash
# 克隆项目
git clone <项目地址>
cd AiEnhance

# 安装依赖（推荐使用UV）
uv sync

# 或使用pip
pip install -e .
```

## ⚡ 快速使用

### 命令行模式

```bash
# 单次查询
uv run python cli_example.py "什么是人工智能？"

# 交互模式
uv run python cli_example.py -i

# 查看帮助
uv run python cli_example.py --help
```

### Web界面模式

```bash
# 启动Gradio界面
uv run python gradio_interface.py

# 浏览器访问
# http://localhost:7860
```

## 🔧 前置要求

### Ollama设置
```bash
# 安装Ollama
brew install ollama  # macOS
# 或下载安装包：https://ollama.ai

# 启动服务
ollama serve

# 安装模型
ollama pull qwen3:8b
ollama pull bge-m3:latest
```

## 📁 项目结构

```
AiEnhance/
├── cli_example.py         # ✅ 命令行界面
├── gradio_interface.py    # ✅ Web界面
├── aienhance/             # 核心包
├── tests/                 # 测试文件
├── scripts/               # 辅助脚本
└── docker/                # Docker配置
```

## 🎯 主要功能

- **🔍 感知层**: 用户建模、情境分析
- **🧠 认知层**: 记忆激活、语义增强
- **🎯 行为层**: 自适应输出生成
- **🤝 协作层**: 多视角协作增强

## 💡 使用技巧

1. **首次使用**: 先运行CLI确保系统正常
2. **无记忆模式**: 如果MIRIX不可用，系统会自动降级
3. **Web界面**: 提供完整的可视化分层处理过程
4. **开发模式**: 使用 `uv run ruff check .` 进行代码检查

## 🆘 常见问题

**Q: 命令找不到？**
A: 使用 `uv run python cli_example.py` 而不是 `uv run aienhance`

**Q: Ollama连接失败？**  
A: 确保 `ollama serve` 正在运行，并检查端口11434

**Q: Gradio启动失败？**
A: 检查依赖是否完整：`uv sync`

更多问题请查看 [README.md](README.md) 或提交Issue。