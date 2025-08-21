# 🛠️ UV环境使用指南

针对uv包管理器的AiEnhance Gradio界面使用说明。

## 🚀 快速开始

### 方法一：自动依赖安装
```bash
# 运行依赖安装脚本
uv run setup_uv_deps.py

# 安装完成后启动演示界面
uv run demo_gradio.py
```

### 方法二：手动安装依赖
```bash
# 使用uv add安装依赖
uv add gradio plotly pandas requests

# 启动界面
uv run demo_gradio.py
```

### 方法三：使用uv pip（如果uv add不工作）
```bash
# 使用uv pip安装
uv pip install gradio plotly pandas requests

# 启动界面
uv run demo_gradio.py
```

## 🎯 推荐启动命令

```bash
# 1. 安装依赖（只需运行一次）
uv run setup_uv_deps.py

# 2. 启动演示界面（推荐）
uv run demo_gradio.py

# 3. 启动完整界面（需要完整系统）
uv run gradio_interface.py
```

## ❓ 问题排查

### 如果遇到"No module named pip"错误
这是因为uv环境中没有pip，解决方案：

1. **使用uv命令安装**：
   ```bash
   uv add gradio plotly pandas
   ```

2. **或使用uv pip**：
   ```bash
   uv pip install gradio plotly pandas
   ```

### 如果依赖安装失败
1. 检查uv版本：
   ```bash
   uv --version
   ```

2. 更新uv：
   ```bash
   pip install --upgrade uv
   ```

3. 手动逐个安装：
   ```bash
   uv add gradio
   uv add plotly  
   uv add pandas
   uv add requests
   ```

## 🔧 环境说明

- **UV环境**: 使用`.venv`虚拟环境
- **包管理**: uv add/remove 命令
- **运行方式**: uv run 命令
- **Python版本**: 3.8+

## 📋 依赖包列表

| 包名 | 用途 | 必需 |
|------|------|------|
| gradio | Web界面框架 | ✅ |
| plotly | 可视化图表 | ✅ |
| pandas | 数据处理 | ✅ |
| requests | HTTP请求 | ✅ |

## 🎪 界面功能

启动后访问 `http://localhost:7860` 查看：

- 🎛️ **系统配置**: 选择系统类型和LLM配置
- 💬 **分层处理**: 查看感知→认知→行为→协作四层输出
- 🧠 **记忆系统**: MIRIX记忆可视化和搜索
- 💡 **使用说明**: 详细的功能介绍

## 🎬 演示模式 vs 完整模式

### 演示模式 (`demo_gradio.py`)
- ✅ 无需额外依赖
- ✅ 展示界面功能和布局
- ✅ 模拟数据演示各层处理
- ✅ 快速体验和展示

### 完整模式 (`gradio_interface.py`)
- 🔧 需要完整AiEnhance系统
- 🔧 需要LLM服务（Ollama等）
- 🔧 需要MIRIX SDK
- ✅ 真实系统功能
- ✅ 实际查询处理
- ✅ 真实记忆系统集成

## 💡 使用建议

1. **首次使用**: 先运行演示模式了解功能
2. **开发测试**: 使用完整模式进行系统开发
3. **演示展示**: 使用演示模式进行功能展示
4. **生产环境**: 配置完整系统后使用完整模式

---

**🎉 现在您可以在uv环境中正常使用AiEnhance Gradio界面了！**