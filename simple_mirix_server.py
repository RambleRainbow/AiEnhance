#!/usr/bin/env python3
"""
简单的MIRIX兼容服务器
用于快速测试和开发，不需要Docker
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
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

# 简单的内存存储
memories_store = []

# 创建FastAPI应用
app = FastAPI(
    title="Simple MIRIX Backend",
    description="简化的MIRIX兼容服务器",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        services={
            "mirix": "healthy",
            "storage": "memory",
            "database": "mock"
        }
    )

@app.post("/api/memory/add")
async def add_memory(entry: MemoryEntry):
    """添加记忆"""
    memory_id = f"mem_{len(memories_store)}_{int(datetime.now().timestamp())}"
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
    memories_store.append(memory_data)
    logger.info(f"Added memory: {memory_id}")
    return {"memory_id": memory_id, "status": "success"}

@app.post("/api/memory/search", response_model=MemoryResponse)
async def search_memories(query: MemoryQuery):
    """搜索记忆"""
    matching_memories = []
    query_lower = query.query.lower()
    
    for memory in memories_store:
        if (memory["user_id"] == query.user_id and 
            query_lower in memory["content"].lower()):
            if not query.memory_types or memory["memory_type"] in query.memory_types:
                matching_memories.append(memory)
    
    # 按时间戳排序
    matching_memories.sort(key=lambda x: x["timestamp"], reverse=True)
    limited_memories = matching_memories[:query.limit]
    
    logger.info(f"Search '{query.query}' returned {len(limited_memories)} results")
    
    return MemoryResponse(
        memories=limited_memories,
        total=len(limited_memories),
        query_time=0.01
    )

@app.get("/api/memory/user/{user_id}")
async def get_user_memories(user_id: str, limit: int = 50):
    """获取用户记忆"""
    user_memories = [m for m in memories_store if m["user_id"] == user_id]
    user_memories.sort(key=lambda x: x["timestamp"], reverse=True)
    limited_memories = user_memories[:limit]
    
    return {
        "memories": limited_memories,
        "total": len(limited_memories),
        "user_id": user_id
    }

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    return {
        "service": "Simple MIRIX Backend",
        "version": "1.0.0-dev",
        "status": "running",
        "storage": "memory",
        "memory_count": len(memories_store),
        "memory_types": ["core", "episodic", "semantic", "procedural", "resource", "knowledge"],
        "features": {
            "multi_modal": False,
            "vector_search": False,
            "full_text_search": True,
            "real_time": True,
            "persistent": False
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Simple MIRIX Backend Server...")
    print("📝 This is a development server for testing purposes")
    print("🔗 Health check: http://localhost:8000/health")
    print("📖 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_mirix_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )