"""
AiEnhance主应用 - HTTP API服务
提供记忆-认知协同系统的RESTful API接口
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 导入AiEnhance模块
from aienhance import create_system

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据模型
class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str | None = None
    context: dict[str, Any] | None = None
    system_type: str | None = None

class QueryResponse(BaseModel):
    content: str
    user_id: str
    session_id: str | None = None
    processing_metadata: dict[str, Any]
    system_info: dict[str, Any]

class SystemCreateRequest(BaseModel):
    system_type: str = "default"
    memory_system_type: str | None = None
    llm_provider: str | None = None
    embedding_provider: str | None = None
    config: dict[str, Any] | None = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: dict[str, str]
    system_info: dict[str, Any]

# 全局变量
systems_cache = {}
default_system = None
mirix_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global default_system, mirix_client

    # 启动时初始化
    logger.info("Initializing AiEnhance application...")

    try:
        # 初始化HTTP客户端
        mirix_client = httpx.AsyncClient(
            base_url=os.getenv("MIRIX_API_URL", "http://mirix-backend:8000"),
            timeout=30.0
        )

        # 等待MIRIX服务可用
        await wait_for_mirix()

        # 创建默认系统
        default_system = create_system(
            system_type=os.getenv("DEFAULT_SYSTEM_TYPE", "educational"),
            memory_system_type=os.getenv("DEFAULT_MEMORY_SYSTEM", "mirix"),
            llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
            memory_api_base=os.getenv("MIRIX_API_URL", "http://mirix-backend:8000"),
            llm_api_base=os.getenv("OLLAMA_API_URL", "http://ollama:11434"),
            llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b")
        )

        logger.info("AiEnhance application initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize AiEnhance: {e}")
        default_system = None

    yield

    # 关闭时清理资源
    if mirix_client:
        await mirix_client.aclose()
    logger.info("AiEnhance application cleaned up")

async def wait_for_mirix(max_retries=30, delay=2):
    """等待MIRIX服务可用"""
    for i in range(max_retries):
        try:
            response = await mirix_client.get("/health")
            if response.status_code == 200:
                logger.info("MIRIX service is ready")
                return
        except Exception:
            logger.info(f"Waiting for MIRIX service... ({i+1}/{max_retries})")
            await asyncio.sleep(delay)

    raise RuntimeError("MIRIX service not available after waiting")

# 创建FastAPI应用
app = FastAPI(
    title="AiEnhance API",
    description="Memory-Cognitive Collaborative System API",
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

def get_system(system_type: str = "default"):
    """获取或创建系统实例"""
    if system_type == "default" and default_system:
        return default_system

    if system_type in systems_cache:
        return systems_cache[system_type]

    # 创建新系统实例
    try:
        system = create_system(
            system_type=system_type,
            memory_system_type=os.getenv("DEFAULT_MEMORY_SYSTEM", "mirix"),
            llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "ollama"),
            memory_api_base=os.getenv("MIRIX_API_URL", "http://mirix-backend:8000"),
            llm_api_base=os.getenv("OLLAMA_API_URL", "http://ollama:11434"),
            llm_model_name=os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b")
        )
        systems_cache[system_type] = system
        return system
    except Exception as e:
        logger.error(f"Failed to create system {system_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create system: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AiEnhance - Memory-Cognitive System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .feature { margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }
            .api-link { color: #3498db; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🧠 AiEnhance</h1>
            <p>欢迎使用AiEnhance记忆-认知协同系统！</p>
            
            <div class="feature">
                <h3>🔧 核心功能</h3>
                <ul>
                    <li>多层次认知处理（感知、认知、行为、协作）</li>
                    <li>MIRIX多智能体记忆系统</li>
                    <li>多LLM提供商支持（Ollama、OpenAI、Anthropic）</li>
                    <li>个性化用户建模和适应性输出</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>📚 API文档</h3>
                <p>访问 <a href="/docs" class="api-link">Swagger UI</a> 查看完整API文档</p>
                <p>访问 <a href="/redoc" class="api-link">ReDoc</a> 查看替代文档</p>
            </div>
            
            <div class="feature">
                <h3>💡 快速开始</h3>
                <p>发送POST请求到 <code>/api/query</code> 开始对话：</p>
                <pre>{"query": "什么是人工智能？", "user_id": "user123"}</pre>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    services = {"aienhance": "healthy"}

    # 检查MIRIX服务
    try:
        response = await mirix_client.get("/health")
        services["mirix"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services["mirix"] = "unhealthy"

    # 检查Ollama服务
    try:
        ollama_url = os.getenv("OLLAMA_API_URL", "http://ollama:11434")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags")
            services["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services["ollama"] = "unhealthy"

    # 获取系统信息
    system_info = {}
    if default_system:
        status = default_system.get_system_status()
        system_info = {
            "initialized": status.get("initialized", False),
            "user_count": status.get("user_count", 0),
            "session_count": status.get("session_count", 0),
            "memory_system": status.get("memory_system", {}).get("system_type", "none"),
            "llm_provider": status.get("llm_provider", {}).get("provider", "none")
        }

    return HealthResponse(
        status="healthy" if all(s == "healthy" for s in services.values()) else "degraded",
        timestamp=datetime.now(),
        services=services,
        system_info=system_info
    )

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """处理用户查询"""
    try:
        # 获取系统实例
        system = get_system(request.system_type or "default")

        # 处理查询
        response = await system.process_query(
            query=request.query,
            user_id=request.user_id,
            context=request.context or {}
        )

        # 获取系统信息
        system_status = system.get_system_status()

        return QueryResponse(
            content=response.content,
            user_id=request.user_id,
            session_id=request.session_id,
            processing_metadata=response.processing_metadata,
            system_info={
                "system_type": request.system_type or "default",
                "processing_steps": response.processing_metadata.get("processing_steps", []),
                "activated_memories_count": len(response.activated_memories),
                "llm_generated": response.adaptation_info.metadata.get("llm_generated", False) if hasattr(response.adaptation_info, 'metadata') and response.adaptation_info.metadata else False
            }
        )

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/create")
async def create_new_system(request: SystemCreateRequest):
    """创建新的系统实例"""
    try:
        # 创建系统配置
        config_params = request.config or {}

        # 添加服务URL配置
        config_params.update({
            "memory_api_base": os.getenv("MIRIX_API_URL", "http://mirix-backend:8000"),
            "llm_api_base": os.getenv("OLLAMA_API_URL", "http://ollama:11434")
        })

        # 创建系统
        system = create_system(
            system_type=request.system_type,
            memory_system_type=request.memory_system_type,
            llm_provider=request.llm_provider,
            embedding_provider=request.embedding_provider,
            **config_params
        )

        # 缓存系统实例
        cache_key = f"{request.system_type}_{request.memory_system_type}_{request.llm_provider}"
        systems_cache[cache_key] = system

        return {
            "system_id": cache_key,
            "status": "created",
            "config": {
                "system_type": request.system_type,
                "memory_system_type": request.memory_system_type,
                "llm_provider": request.llm_provider,
                "embedding_provider": request.embedding_provider
            }
        }

    except Exception as e:
        logger.error(f"System creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/status")
async def get_system_status(system_type: str = "default"):
    """获取系统状态"""
    try:
        system = get_system(system_type)
        status = system.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{user_id}/profile")
async def get_user_profile(user_id: str, system_type: str = "default"):
    """获取用户画像"""
    try:
        system = get_system(system_type)
        profile = system.export_user_profile(user_id)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/reset")
async def reset_system_session(system_type: str = "default"):
    """重置系统会话"""
    try:
        system = get_system(system_type)
        system.reset_session()
        return {"status": "session_reset", "system_type": system_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def get_api_info():
    """获取API信息"""
    return {
        "service": "AiEnhance API",
        "version": "1.0.0",
        "description": "Memory-Cognitive Collaborative System",
        "features": {
            "multi_layer_architecture": True,
            "memory_systems": ["mirix", "mem0", "graphiti"],
            "llm_providers": ["ollama", "openai", "anthropic"],
            "real_time_processing": True,
            "user_personalization": True
        },
        "endpoints": {
            "query": "/api/query",
            "system_create": "/api/system/create",
            "system_status": "/api/system/status",
            "user_profile": "/api/user/{user_id}/profile",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    # 获取配置
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8080"))
    log_level = os.getenv("LOG_LEVEL", "info")

    # 启动服务
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False
    )
