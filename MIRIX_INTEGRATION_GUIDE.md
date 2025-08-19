# MIRIX 集成指南

## 概述

MIRIX 是 AiEnhance 系统的记忆后端服务，采用独立的微服务架构部署。本文档详细说明了 MIRIX 与主系统的集成方式。

## 架构说明

### 服务架构图
```
┌─────────────────────┐    HTTP API     ┌─────────────────────┐
│   AiEnhance 主应用   │◄──────────────►│   MIRIX Backend     │
│   (Python进程)       │  localhost:8000 │   (Docker容器)       │
└─────────────────────┘                 └─────────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────────┐
                                         │   PostgreSQL        │
                                         │   + pgvector        │
                                         │   (Docker容器)       │
                                         └─────────────────────┘
                                                   │
                                         ┌─────────────────────┐
                                         │     Redis           │
                                         │   (Docker容器)       │
                                         └─────────────────────┘
```

### 服务组件

#### 1. MIRIX HTTP API Server
- **端口**: 8000
- **协议**: HTTP/REST API
- **功能**: 记忆系统的主要接口
- **部署**: Docker容器
- **健康检查**: `http://localhost:8000/health`

#### 2. PostgreSQL 数据库
- **端口**: 5432
- **扩展**: pgvector (向量相似搜索)
- **数据库**: mirix_memory
- **用户**: mirix/mirix_password

#### 3. Redis 缓存
- **端口**: 6379
- **用途**: 会话存储、查询缓存
- **配置**: 持久化存储

## 启动方式

### 方法一：开发模式启动（推荐）

```bash
# 一键启动所有依赖服务
./start-dev.sh

# 跳过环境检查快速启动
./start-dev.sh --skip-checks
```

### 方法二：Docker 手动启动

```bash
# 构建镜像
docker compose build

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f mirix-backend
```

### 方法三：分步启动（调试用）

```bash
# 1. 仅启动数据库和缓存
docker compose up -d postgres redis

# 2. 启动MIRIX后端
docker compose up -d mirix-backend

# 3. 检查各服务状态
docker compose ps
```

## 服务验证

### 1. 快速连接测试
```bash
# 使用专用测试脚本
python test_mirix_connection.py
```

### 2. 手动API测试
```bash
# 健康检查
curl http://localhost:8000/health

# 系统信息
curl http://localhost:8000/api/system/info

# 添加测试记忆
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "测试记忆",
    "memory_type": "episodic", 
    "user_id": "test_user"
  }'
```

### 3. 数据库直接连接
```bash
# 连接PostgreSQL
docker exec -it aienhance-postgres psql -U mirix -d mirix_memory

# 查看表结构
\dt

# 检查向量扩展
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 4. Redis连接测试
```bash
# 连接Redis
docker exec -it aienhance-redis redis-cli

# 测试连接
ping
```

## 开发工作流程

### 完整开发流程
```bash
# 1. 启动外部依赖服务
./start-dev.sh

# 2. 运行主应用
uv run python main.py

# 3. 测试记忆功能
python test_memory_fix.py

# 4. 使用CLI工具
python ai.py "你好，请介绍一下自己"

# 5. 停止服务
docker compose down
```

### 仅LLM模式（无记忆）
```bash
# 如果不需要记忆功能，可以直接运行
python ai.py "你好"  # 会自动降级到简化模式
```

## 常见问题

### 1. 503 Service Unavailable
```
MIRIX HTTP adapter initialization failed: MIRIX health check failed: 
Server error '503 Service Unavailable' for url 'http://localhost:8000/health'
```

**解决方案**:
- 确保Docker已启动: `docker --version`
- 启动MIRIX服务: `./start-dev.sh`
- 检查服务状态: `docker compose ps`

### 2. Docker连接失败
```
Cannot connect to the Docker daemon at unix:///Users/.../.docker.sock. 
Is the docker daemon running?
```

**解决方案**:
- macOS: `open -a Docker`
- Linux: `sudo systemctl start docker`
- 等待Docker完全启动后重试

### 3. 端口冲突
如果8000端口被占用:
```bash
# 查看端口占用
lsof -i :8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8001:8000"  # 改为8001端口
```

### 4. 数据库初始化失败
```bash
# 清除所有数据重新开始
docker compose down -v
docker compose up -d
```

## API接口说明

### 核心接口

#### 健康检查
```http
GET /health
```

#### 添加记忆
```http
POST /api/memory/add
Content-Type: application/json

{
  "content": "记忆内容",
  "memory_type": "episodic|semantic|core|procedural|resource|knowledge",
  "user_id": "用户ID",
  "session_id": "会话ID (可选)",
  "metadata": {}
}
```

#### 搜索记忆
```http
POST /api/memory/search
Content-Type: application/json

{
  "query": "搜索关键词",
  "user_id": "用户ID", 
  "limit": 20,
  "similarity_threshold": 0.7
}
```

#### 获取用户记忆
```http
GET /api/memory/user/{user_id}?limit=50
```

## 配置文件

### MIRIX配置
配置文件位置: `docker/mirix/mirix_config.yml`

### 环境变量
主要环境变量在 `docker-compose.yml` 中配置:

```yaml
environment:
  - DATABASE_URL=postgresql://mirix:mirix_password@postgres:5432/mirix_memory
  - REDIS_URL=redis://redis:6379/0
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - DEFAULT_LLM_MODEL=qwen3:8b
  - DEFAULT_EMBEDDING_MODEL=bge-m3
```

## 性能优化

### 1. 数据库优化
- 定期清理旧记忆: `DELETE FROM memories WHERE created_at < NOW() - INTERVAL '30 days'`
- 创建适当索引: `CREATE INDEX ON memories USING GIN (embedding)`

### 2. 缓存策略
- Redis缓存热点查询
- 向量搜索结果缓存
- 用户会话状态缓存

### 3. 容器资源限制
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 故障排除

### 日志查看
```bash
# 查看MIRIX服务日志
docker compose logs -f mirix-backend

# 查看数据库日志
docker compose logs -f postgres

# 查看Redis日志
docker compose logs -f redis
```

### 服务重启
```bash
# 重启单个服务
docker compose restart mirix-backend

# 重启所有服务
docker compose restart

# 强制重建
docker compose up -d --force-recreate
```

### 数据清理
```bash
# 清除所有数据并重新开始
docker compose down -v
docker system prune -f
docker compose up -d
```

## 生产部署

### 完整应用栈
```bash
# 使用生产配置启动
docker compose -f docker-compose.full.yml up -d
```

### 安全配置
- 修改默认密码
- 配置防火墙规则
- 启用SSL/TLS
- 设置访问控制

---

**总结**: MIRIX是一个独立的微服务，通过HTTP API与主应用通信。需要单独启动Docker服务栈才能使用完整的记忆功能。如果不需要记忆功能，主应用可以在简化模式下运行。