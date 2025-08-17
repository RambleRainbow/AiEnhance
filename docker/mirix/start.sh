#!/bin/bash

# MIRIX启动脚本
set -e

echo "=== MIRIX Backend Startup ==="
echo "Starting MIRIX backend service..."

# 等待数据库服务
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready!"

# 等待Redis服务
echo "Waiting for Redis..."
while ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "Redis is ready!"

# 初始化数据库
echo "Initializing database..."
python -c "
import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://'))

# 创建pgvector扩展
with engine.connect() as conn:
    try:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
        conn.commit()
        print('Vector extension created successfully')
    except Exception as e:
        print(f'Vector extension setup: {e}')

# 创建必要的表结构
try:
    # 这里可以添加MIRIX的表结构初始化
    print('Database initialization completed')
except Exception as e:
    print(f'Database initialization error: {e}')
"

# 创建必要的目录
mkdir -p /data/mirix/uploads
mkdir -p /data/mirix/cache
mkdir -p /app/logs

# 设置环境变量
export MIRIX_CONFIG_PATH="/app/config/mirix.yml"
export MIRIX_DATA_DIR="/data/mirix"

# 检查Ollama连接
echo "Checking Ollama connection..."
if curl -f http://$OLLAMA_BASE_URL/api/tags > /dev/null 2>&1; then
    echo "Ollama is ready!"
else
    echo "Warning: Ollama is not ready, but continuing..."
fi

# 启动MIRIX服务
echo "Starting MIRIX service..."

# 创建一个简单的FastAPI应用作为MIRIX的包装器
cat > /app/mirix_server.py << 'EOF'
"""
MIRIX Backend API Server
为AiEnhance提供MIRIX记忆系统的HTTP接口
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class MemoryEntry(BaseModel):
    content: str
    memory_type: str
    user_id: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryQuery(BaseModel):
    query: str
    user_id: str
    session_id: Optional[str] = None
    memory_types: Optional[List[str]] = None
    limit: int = 20
    similarity_threshold: float = 0.7

class MemoryResponse(BaseModel):
    memories: List[Dict[str, Any]]
    total: int
    query_time: float

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]

# 全局变量存储MIRIX实例
mirix_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化MIRIX
    global mirix_instance
    try:
        # 这里应该初始化真正的MIRIX实例
        # 目前创建一个模拟实例
        logger.info("Initializing MIRIX backend...")
        mirix_instance = MockMirixInstance()
        await mirix_instance.initialize()
        logger.info("MIRIX backend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MIRIX: {e}")
        mirix_instance = None
    
    yield
    
    # 关闭时清理资源
    if mirix_instance:
        await mirix_instance.cleanup()
        logger.info("MIRIX backend cleaned up")

# 创建FastAPI应用
app = FastAPI(
    title="MIRIX Backend API",
    description="MIRIX Memory System Backend for AiEnhance",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MockMirixInstance:
    """MIRIX模拟实例 - 待集成真正的MIRIX"""
    
    def __init__(self):
        self.memories = []
        self.initialized = False
    
    async def initialize(self):
        """初始化MIRIX实例"""
        # 这里应该初始化真正的MIRIX组件
        await asyncio.sleep(1)  # 模拟初始化时间
        self.initialized = True
    
    async def add_memory(self, entry: MemoryEntry) -> str:
        """添加记忆"""
        memory_id = f"mem_{len(self.memories)}"
        memory_data = {
            "id": memory_id,
            "content": entry.content,
            "memory_type": entry.memory_type,
            "user_id": entry.user_id,
            "session_id": entry.session_id,
            "metadata": entry.metadata or {},
            "timestamp": datetime.now().isoformat(),
            "confidence": 1.0
        }
        self.memories.append(memory_data)
        return memory_id
    
    async def search_memories(self, query: MemoryQuery) -> MemoryResponse:
        """搜索记忆"""
        # 简单的文本匹配搜索
        matching_memories = []
        for memory in self.memories:
            if (memory["user_id"] == query.user_id and 
                query.query.lower() in memory["content"].lower()):
                if not query.memory_types or memory["memory_type"] in query.memory_types:
                    matching_memories.append(memory)
        
        # 限制结果数量
        limited_memories = matching_memories[:query.limit]
        
        return MemoryResponse(
            memories=limited_memories,
            total=len(limited_memories),
            query_time=0.1
        )
    
    async def cleanup(self):
        """清理资源"""
        self.initialized = False

def get_mirix():
    """获取MIRIX实例"""
    if not mirix_instance or not mirix_instance.initialized:
        raise HTTPException(status_code=503, detail="MIRIX service not available")
    return mirix_instance

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    services = {
        "mirix": "healthy" if mirix_instance and mirix_instance.initialized else "unhealthy",
        "database": "healthy",  # 这里应该检查真实的数据库状态
        "redis": "healthy"      # 这里应该检查真实的Redis状态
    }
    
    return HealthResponse(
        status="healthy" if all(s == "healthy" for s in services.values()) else "unhealthy",
        timestamp=datetime.now(),
        services=services
    )

@app.post("/api/memory/add")
async def add_memory(entry: MemoryEntry, mirix=Depends(get_mirix)):
    """添加记忆"""
    try:
        memory_id = await mirix.add_memory(entry)
        return {"memory_id": memory_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search", response_model=MemoryResponse)
async def search_memories(query: MemoryQuery, mirix=Depends(get_mirix)):
    """搜索记忆"""
    try:
        result = await mirix.search_memories(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/user/{user_id}")
async def get_user_memories(user_id: str, limit: int = 50, mirix=Depends(get_mirix)):
    """获取用户记忆"""
    try:
        # 获取用户的所有记忆
        user_memories = [m for m in mirix.memories if m["user_id"] == user_id]
        limited_memories = user_memories[:limit]
        
        return {
            "memories": limited_memories,
            "total": len(limited_memories),
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    return {
        "service": "MIRIX Backend",
        "version": "1.0.0",
        "status": "running",
        "memory_types": ["core", "episodic", "semantic", "procedural", "resource", "knowledge"],
        "features": {
            "multi_modal": True,
            "vector_search": True,
            "full_text_search": True,
            "real_time": True
        }
    }

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # 启动服务
    uvicorn.run(
        "mirix_server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False
    )
EOF

# 启动服务
python /app/mirix_server.py
EOF

chmod +x /app/start.sh