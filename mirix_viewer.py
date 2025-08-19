#!/usr/bin/env python3
"""
MIRIX记忆内容查看器
提供简单的Web界面来查看和管理MIRIX中的记忆内容
"""

import asyncio
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import json

app = FastAPI(title="MIRIX记忆查看器", description="查看和管理MIRIX记忆内容的Web界面")

# 模板配置
templates = Jinja2Templates(directory="templates")

# MIRIX API配置
MIRIX_BASE_URL = "http://localhost:8000"

async def get_mirix_client():
    """获取MIRIX API客户端"""
    return httpx.AsyncClient(base_url=MIRIX_BASE_URL, timeout=30.0)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def check_mirix_health():
    """检查MIRIX服务健康状态"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MIRIX_BASE_URL}/health")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MIRIX服务不可用: {str(e)}")

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MIRIX_BASE_URL}/api/system/info")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"无法获取系统信息: {str(e)}")

@app.get("/api/memories/user/{user_id}")
async def get_user_memories(user_id: str, limit: int = 50):
    """获取用户记忆"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MIRIX_BASE_URL}/api/memory/user/{user_id}?limit={limit}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户记忆失败: {str(e)}")

@app.post("/api/memories/search")
async def search_memories(query_data: Dict[str, Any]):
    """搜索记忆"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MIRIX_BASE_URL}/api/memory/search", json=query_data)
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索记忆失败: {str(e)}")

@app.get("/api/memories/stats")
async def get_memory_stats():
    """获取记忆统计信息"""
    try:
        # 获取一些用户的记忆来计算统计信息
        users = ["cli_user", "interactive_user", "demo_user"]
        total_memories = 0
        user_stats = {}
        
        async with httpx.AsyncClient() as client:
            for user in users:
                try:
                    response = await client.get(f"{MIRIX_BASE_URL}/api/memory/user/{user}?limit=1000")
                    data = response.json()
                    count = len(data.get("memories", []))
                    user_stats[user] = count
                    total_memories += count
                except:
                    user_stats[user] = 0
        
        return {
            "total_memories": total_memories,
            "user_stats": user_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 启动MIRIX记忆查看器...")
    print("🌐 访问地址: http://localhost:9000")
    print("📊 查看MIRIX记忆内容和统计信息")
    print("⚠️  请确保MIRIX服务在localhost:8000运行")
    
    uvicorn.run(
        "mirix_viewer:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )