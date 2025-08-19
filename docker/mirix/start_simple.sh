#!/bin/bash

# MIRIX启动脚本 - 简化版本，使用Python进行服务检查
set -e

echo "=== MIRIX Backend Startup (Simplified) ==="
echo "Starting MIRIX backend service..."

# 等待服务就绪 - 使用Python脚本
echo "Waiting for dependent services..."
python /app/wait_for_services.py

if [ $? -ne 0 ]; then
    echo "❌ Service readiness check failed"
    exit 1
fi

# 创建必要的目录
mkdir -p /data/mirix/uploads
mkdir -p /data/mirix/cache
mkdir -p /app/logs

# 设置环境变量
export MIRIX_CONFIG_PATH="/app/config/mirix.yml"
export MIRIX_DATA_DIR="/data/mirix"

# 检查Ollama连接 (可选，失败不影响启动)
echo "Checking Ollama connection (optional)..."
if curl -f "${OLLAMA_BASE_URL}/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama is ready!"
else
    echo "⚠️  Ollama is not ready, but continuing..."
fi

# 启动MIRIX服务
echo "Starting MIRIX service..."

# 创建一个简单的FastAPI应用作为MIRIX的包装器
cat > /app/mirix_server.py << 'EOF'
"""
MIRIX Backend API Server - Simplified Version
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
        logger.info("Initializing MIRIX backend...")
        mirix_instance = SimpleMirixInstance()
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

class SimpleMirixInstance:
    """MIRIX简化实例 - 基本功能实现"""
    
    def __init__(self):
        self.memories = []
        self.initialized = False
    
    async def initialize(self):
        """初始化MIRIX实例"""
        await asyncio.sleep(0.5)  # 模拟初始化时间
        self.initialized = True
        logger.info("Simple MIRIX instance initialized")
    
    async def add_memory(self, entry: MemoryEntry) -> str:
        """添加记忆"""
        memory_id = f"mem_{len(self.memories)}_{int(datetime.now().timestamp())}"
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
        logger.info(f"Added memory: {memory_id}")
        return memory_id
    
    async def search_memories(self, query: MemoryQuery) -> MemoryResponse:
        """搜索记忆"""
        # 简单的文本匹配搜索
        matching_memories = []
        query_lower = query.query.lower()
        
        for memory in self.memories:
            if (memory["user_id"] == query.user_id and 
                query_lower in memory["content"].lower()):
                if not query.memory_types or memory["memory_type"] in query.memory_types:
                    matching_memories.append(memory)
        
        # 按时间戳排序（最新的在前）
        matching_memories.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 限制结果数量
        limited_memories = matching_memories[:query.limit]
        
        logger.info(f"Search query '{query.query}' returned {len(limited_memories)} results")
        
        return MemoryResponse(
            memories=limited_memories,
            total=len(limited_memories),
            query_time=0.05  # 模拟查询时间
        )
    
    async def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的所有记忆"""
        user_memories = [m for m in self.memories if m["user_id"] == user_id]
        user_memories.sort(key=lambda x: x["timestamp"], reverse=True)
        return user_memories[:limit]
    
    async def cleanup(self):
        """清理资源"""
        self.initialized = False
        logger.info("MIRIX instance cleaned up")

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
        "database": "healthy",  # 简化：假设数据库健康
        "redis": "healthy"      # 简化：假设Redis健康
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
        logger.error(f"Failed to add memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search", response_model=MemoryResponse)
async def search_memories(query: MemoryQuery, mirix=Depends(get_mirix)):
    """搜索记忆"""
    try:
        result = await mirix.search_memories(query)
        return result
    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/user/{user_id}")
async def get_user_memories(user_id: str, limit: int = 50, mirix=Depends(get_mirix)):
    """获取用户记忆"""
    try:
        memories = await mirix.get_user_memories(user_id, limit)
        
        return {
            "memories": memories,
            "total": len(memories),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Failed to get user memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    return {
        "service": "MIRIX Backend (Simplified)",
        "version": "1.0.0",
        "status": "running",
        "memory_types": ["core", "episodic", "semantic", "procedural", "resource", "knowledge"],
        "features": {
            "multi_modal": False,  # 简化版本不支持
            "vector_search": False,  # 简化版本使用文本搜索
            "full_text_search": True,
            "real_time": True
        }
    }

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    logger.info(f"Starting MIRIX server on {host}:{port}")
    
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
echo "🚀 Starting MIRIX HTTP API server..."
python /app/mirix_server.py