# Graphiti 记忆系统测试

本目录包含针对Graphiti记忆系统的完整测试套件。

## 测试文件结构

### 主要测试文件

- **`test_graphiti_memory_system.py`** - 主要的pytest兼容集成测试
  - 包含完整的pytest测试类
  - 支持`pytest`命令直接运行
  - 也可以作为独立脚本运行手动测试

- **`test_graphiti_integration.py`** - 完整的适配器集成测试
  - 测试Graphiti HTTP适配器的所有功能
  - 包括健康检查、消息添加、搜索等

- **`test_graphiti_simple.py`** - 简化的连接测试
  - 快速验证基本连接性
  - 适合日常开发中的快速检查

- **`test_graphiti_detailed.py`** - 详细的诊断测试
  - 深入测试各个API端点
  - 提供详细的错误诊断信息

- **`test_graphiti_final.py`** - 综合工作流测试
  - 模拟完整的使用场景
  - 包含性能测试和数据持久化验证

## 使用方法

### 使用pytest运行测试

```bash
# 运行所有Graphiti测试
uv run pytest tests/test_graphiti*.py -v

# 运行主要集成测试
uv run pytest tests/test_graphiti_memory_system.py -v

# 运行特定测试类
uv run pytest tests/test_graphiti_memory_system.py::TestGraphitiMemorySystem -v
```

### 直接运行测试脚本

```bash
# 运行主要测试
uv run python tests/test_graphiti_memory_system.py

# 运行简单连接测试
uv run python tests/test_graphiti_simple.py

# 运行详细诊断
uv run python tests/test_graphiti_detailed.py

# 运行综合测试
uv run python tests/test_graphiti_final.py
```

## 测试前提条件

1. **Graphiti服务运行中**
   ```bash
   cd /path/to/graphiti
   docker compose up -d
   ```

2. **Ollama服务运行中** (如果使用本地嵌入)
   ```bash
   ollama serve
   ```

3. **必要的模型已下载**
   ```bash
   ollama pull qwen3:8b
   ollama pull bge-m3:latest
   ```

## 测试结果解释

### 成功指标
- ✅ 健康检查通过
- ✅ 消息添加成功
- ✅ 数据库连接正常
- ✅ 清理操作成功

### 常见问题
- ❌ 搜索500错误 → 检查嵌入模型配置
- ⚠️  数据未持久化 → 等待异步处理完成
- ❌ 连接失败 → 确认Graphiti服务状态

## 辅助脚本

相关的诊断和报告脚本位于`scripts/`目录：

- `scripts/diagnose_graphiti.py` - Graphiti配置诊断工具
- `scripts/graphiti_test_report.py` - 生成测试报告

## 测试覆盖范围

- [x] HTTP服务健康检查
- [x] 消息添加和队列处理
- [x] 记忆搜索功能
- [x] Neo4j数据库连接
- [x] 用户数据清理
- [x] 适配器生命周期管理
- [x] 错误处理和恢复
- [x] 性能基准测试