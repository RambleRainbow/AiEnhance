# 🧠 AiEnhance Gradio 可视化界面

分层认知系统的Web可视化界面，提供全面的系统监控、各层输出展示和MIRIX记忆系统集成。

## 🚀 快速开始

### 使用UV包管理器（推荐）

```bash
# 安装依赖
uv sync

# 启动Gradio界面
uv run aienhance-gradio
```

### 使用传统方式

```bash
# 激活虚拟环境并安装依赖
pip install -e .

# 启动Gradio界面
python gradio_interface.py
```

界面将在 `http://localhost:7860` 启动。

## ✨ 功能特性

### 🎛️ **系统配置**
- **多种系统类型**: Educational、Research、Creative、Lightweight
- **LLM提供商支持**: Ollama、OpenAI、Anthropic、Google AI
- **参数调节**: 温度、模型选择、实时配置
- **状态监控**: 初始化状态和系统信息展示

### 💬 **分层处理可视化**
- **感知层输出**: 用户建模、上下文分析、领域识别
- **认知层输出**: 记忆激活、语义增强、推理结果、知识整合
- **行为层输出**: 响应生成、输出优化、质量评估
- **协作层输出**: 多代理协调、资源整合、协作优化
- **实时处理**: 流式显示各层处理过程

### 🧠 **MIRIX记忆系统**
- **状态监控**: 记忆系统初始化状态和统计信息
- **记忆搜索**: 基于关键词的智能记忆检索
- **可视化分析**: 
  - 📊 记忆类型分布图
  - 📈 记忆创建时间线
  - 📉 置信度分析图表
  - 🕸️ 记忆关系网络图
- **Web界面集成**: 嵌入原生MIRIX Web界面

### 📊 **系统监控**
- **性能指标**: 处理时间、响应质量、资源使用
- **实时状态**: 各组件运行状态监控
- **错误追踪**: 详细的错误信息和调试支持

## 🚀 快速开始

### 1. 安装依赖
```bash
# 自动安装（推荐）
python start_gradio.py

# 手动安装
pip install gradio plotly pandas requests
```

### 2. 启动界面
```bash
# 方式一：使用启动脚本（推荐）
python start_gradio.py

# 方式二：直接启动
python gradio_interface.py
```

### 3. 访问界面
打开浏览器访问：`http://localhost:7860`

## 🎯 使用指南

### 系统初始化
1. 进入 **"🎛️ 系统配置"** 选项卡
2. 选择系统类型（推荐：Educational）
3. 配置LLM提供商（默认：Ollama）
4. 设置模型名称（默认：qwen3:8b）
5. 调整温度参数（默认：0.7）
6. 点击 **"🚀 初始化系统"**

### 查询处理
1. 进入 **"💬 分层处理可视化"** 选项卡
2. 在查询输入框中输入问题
3. 点击 **"🔄 开始处理"**
4. 观察各层的实时输出：
   - 🔍 感知层：用户适配和上下文理解
   - 🧠 认知层：记忆检索和知识整合  
   - 🎯 行为层：响应生成和优化
   - 🤝 协作层：多代理协调（如果启用）

### MIRIX记忆分析
1. 进入 **"🧠 MIRIX记忆系统"** 选项卡
2. 点击 **"🔄 刷新记忆状态"** 查看系统状态
3. 使用 **"🔍 搜索记忆"** 功能查找相关记忆
4. 进入 **"📈 记忆分析图表"** 子选项卡
5. 点击 **"📊 生成记忆仪表板"** 查看可视化图表

### MIRIX Web界面集成
1. 确保MIRIX服务正在运行
2. 进入 **"🌐 MIRIX Web界面"** 子选项卡
3. 输入MIRIX Web界面URL（默认：http://localhost:3000）
4. 点击 **"🚀 加载MIRIX界面"**
5. 在嵌入的iframe中直接操作MIRIX原生界面

## 📋 系统要求

### 最低要求
- Python 3.8+
- 内存: 4GB+
- 存储: 2GB+

### 推荐配置
- Python 3.10+
- 内存: 8GB+
- 存储: 5GB+
- GPU: NVIDIA GPU（用于本地LLM加速）

## 🔧 配置说明

### LLM提供商配置

#### Ollama（推荐用于本地部署）
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动服务
ollama serve

# 下载模型
ollama pull qwen3:8b
```

#### OpenAI
- 需要API密钥
- 在系统配置中选择 "openai"
- 输入模型名称如 "gpt-4" 或 "gpt-3.5-turbo"

#### Anthropic
- 需要API密钥
- 在系统配置中选择 "anthropic" 
- 输入模型名称如 "claude-3-sonnet-20240229"

### MIRIX集成配置

#### SDK模式（统一LLM）
- 自动使用项目的LLM配置
- 无需额外的Google API密钥
- 推荐用于开发和测试

#### 独立模式
- 需要单独的MIRIX API密钥
- 使用MIRIX自带的大模型配置
- 适用于生产环境

## 🐛 故障排除

### 常见问题

1. **Gradio界面无法启动**
   ```bash
   pip install --upgrade gradio
   python start_gradio.py
   ```

2. **Ollama连接失败**
   ```bash
   # 检查服务状态
   ps aux | grep ollama
   
   # 重启服务
   ollama serve
   ```

3. **MIRIX记忆系统初始化失败**
   - 检查是否已安装MIRIX SDK: `pip install mirix`
   - 确认LLM配置正确
   - 查看系统日志获取详细错误信息

4. **图表显示异常**
   ```bash
   pip install --upgrade plotly pandas
   ```

### 性能优化

1. **减少内存使用**
   - 选择 "lightweight" 系统类型
   - 降低记忆查询限制
   - 使用较小的LLM模型

2. **提升响应速度**
   - 使用本地Ollama服务
   - 启用GPU加速
   - 调整温度参数到较低值

## 📚 扩展功能

### 自定义可视化
- 修改 `mirix_frontend_integration.py` 添加新的图表类型
- 扩展分析维度和数据展示方式

### 集成其他记忆系统
- 添加Mem0、Graphiti等适配器的可视化支持
- 实现多记忆系统对比分析

### API接口
- Gradio支持API模式，可以通过REST API调用界面功能
- 适用于与其他系统集成

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Gradio](https://gradio.app/) - 出色的机器学习界面框架
- [Plotly](https://plotly.com/) - 强大的可视化库
- [MIRIX](https://mirix.ai/) - 先进的记忆系统
- [Ollama](https://ollama.ai/) - 本地LLM运行平台