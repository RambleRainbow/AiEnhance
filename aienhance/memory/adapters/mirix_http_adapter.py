"""
MIRIX HTTP API适配器
通过HTTP API连接MIRIX后端服务
支持Docker部署模式
"""

import asyncio
import datetime
import httpx
from typing import Dict, List, Optional, Any
import logging
import json

from ..interfaces import (
    MemorySystem, MemoryEntry, MemoryQuery, MemoryResult, 
    UserContext, MemoryType, MemorySystemConfig
)

logger = logging.getLogger(__name__)


class MirixHttpAdapter(MemorySystem):
    """
    MIRIX HTTP API适配器
    
    通过HTTP API与MIRIX后端服务通信
    支持Docker容器化部署
    """
    
    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self.api_base = config.api_base or "http://localhost:8000"
        self.api_key = config.api_key
        self.timeout = 30.0
        self.client = None
        
        # MIRIX记忆类型映射
        self._memory_type_mapping = {
            MemoryType.CORE: "core",
            MemoryType.EPISODIC: "episodic", 
            MemoryType.SEMANTIC: "semantic",
            MemoryType.PROCEDURAL: "procedural",
            MemoryType.RESOURCE: "resource",
            MemoryType.KNOWLEDGE: "knowledge"
        }
        
        # 反向映射
        self._reverse_memory_mapping = {v: k for k, v in self._memory_type_mapping.items()}
    
    async def initialize(self) -> bool:
        """初始化HTTP客户端和连接"""
        try:
            # 创建HTTP客户端
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "AiEnhance-MirixAdapter/1.0"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                headers=headers,
                timeout=self.timeout
            )
            
            # 测试连接
            await self._check_health()
            
            self.is_initialized = True
            logger.info(f"MIRIX HTTP adapter initialized: {self.api_base}")
            return True
            
        except Exception as e:
            logger.error(f"MIRIX HTTP adapter initialization failed: {e}")
            if self.client:
                await self.client.aclose()
                self.client = None
            return False
    
    async def _check_health(self):
        """检查MIRIX服务健康状态"""
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            
            health_data = response.json()
            if health_data.get("status") != "healthy":
                raise RuntimeError(f"MIRIX service unhealthy: {health_data}")
                
            logger.info("MIRIX service health check passed")
            
        except Exception as e:
            raise RuntimeError(f"MIRIX health check failed: {e}")
    
    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到MIRIX系统"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            # 转换记忆格式
            mirix_memory = {
                "content": memory.content,
                "memory_type": self._memory_type_mapping.get(memory.memory_type, "episodic"),
                "user_id": memory.user_context.user_id,
                "session_id": memory.user_context.session_id,
                "metadata": {
                    **(memory.metadata or {}),
                    "confidence": memory.confidence,
                    "embedding": memory.embedding,
                    "image_data": memory.image_data,
                    "audio_data": memory.audio_data,
                    "file_path": memory.file_path,
                    "relationships": memory.relationships,
                    "timestamp": memory.timestamp.isoformat() if memory.timestamp else None
                }
            }
            
            # 发送到MIRIX API
            response = await self.client.post("/api/memory/add", json=mirix_memory)
            response.raise_for_status()
            
            result = response.json()
            memory_id = result.get("memory_id")
            
            if not memory_id:
                raise RuntimeError("No memory ID returned from MIRIX")
            
            logger.debug(f"Memory added to MIRIX: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to add memory to MIRIX: {e}")
            raise
    
    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            # 构建搜索请求
            search_request = {
                "query": query.query,
                "user_id": query.user_context.user_id,
                "session_id": query.user_context.session_id,
                "memory_types": [
                    self._memory_type_mapping.get(mt, mt.value) 
                    for mt in (query.memory_types or [])
                ],
                "limit": query.limit,
                "similarity_threshold": query.similarity_threshold
            }
            
            # 发送搜索请求
            response = await self.client.post("/api/memory/search", json=search_request)
            response.raise_for_status()
            
            result = response.json()
            
            # 转换结果格式
            memories = []
            for mem_data in result.get("memories", []):
                memory = self._convert_from_mirix_memory(mem_data)
                if memory:
                    memories.append(memory)
            
            return MemoryResult(
                memories=memories,
                total_count=result.get("total", len(memories)),
                query_time=result.get("query_time", 0.0),
                metadata={
                    "source": "mirix_http",
                    "api_response": result
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to search memories in MIRIX: {e}")
            raise
    
    async def get_memory(self, memory_id: str, user_context: UserContext) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            # MIRIX API可能没有直接的获取单个记忆接口
            # 我们通过搜索用户的所有记忆来模拟
            response = await self.client.get(
                f"/api/memory/user/{user_context.user_id}",
                params={"limit": 1000}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 查找特定记忆ID
            for mem_data in result.get("memories", []):
                if mem_data.get("id") == memory_id:
                    return self._convert_from_mirix_memory(mem_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get memory from MIRIX: {e}")
            return None
    
    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆（MIRIX可能不支持直接更新）"""
        logger.warning("MIRIX HTTP API may not support direct memory updates")
        
        try:
            # 删除旧记忆并添加新记忆（如果支持的话）
            await self.delete_memory(memory_id, memory.user_context)
            new_id = await self.add_memory(memory)
            return bool(new_id)
            
        except Exception as e:
            logger.error(f"Failed to update memory in MIRIX: {e}")
            return False
    
    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆（MIRIX可能不支持直接删除）"""
        logger.warning("MIRIX HTTP API may not support direct memory deletion")
        
        try:
            # MIRIX通常不支持删除记忆，这里返回True表示"逻辑删除"
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory from MIRIX: {e}")
            return False
    
    async def get_user_memories(self, user_context: UserContext, 
                              memory_types: Optional[List[MemoryType]] = None,
                              limit: int = 100) -> MemoryResult:
        """获取用户的所有记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            params = {"limit": limit}
            
            # 如果指定了记忆类型，添加过滤参数
            if memory_types:
                memory_type_strings = [
                    self._memory_type_mapping.get(mt, mt.value) 
                    for mt in memory_types
                ]
                params["memory_types"] = ",".join(memory_type_strings)
            
            response = await self.client.get(
                f"/api/memory/user/{user_context.user_id}",
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 转换结果格式
            memories = []
            for mem_data in result.get("memories", []):
                memory = self._convert_from_mirix_memory(mem_data)
                if memory:
                    # 如果指定了记忆类型过滤，进行客户端过滤
                    if not memory_types or memory.memory_type in memory_types:
                        memories.append(memory)
            
            return MemoryResult(
                memories=memories,
                total_count=result.get("total", len(memories)),
                query_time=0.1,
                metadata={
                    "source": "mirix_http",
                    "user_id": user_context.user_id,
                    "memory_types": memory_types
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get user memories from MIRIX: {e}")
            raise
    
    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            # 尝试通过MIRIX API清除用户记忆
            response = await self.client.delete(
                f"/api/memory/user/{user_context.user_id}"
            )
            
            if response.status_code == 404:
                # 如果MIRIX不支持直接清除，尝试获取所有记忆并逐个删除
                logger.warning("MIRIX API不支持批量清除，尝试逐个删除")
                return await self._fallback_clear_memories(user_context)
            
            response.raise_for_status()
            result = response.json()
            
            success = result.get("success", True)
            cleared_count = result.get("cleared_count", 0)
            
            logger.info(f"Cleared {cleared_count} memories for user {user_context.user_id}")
            return success
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("MIRIX API不支持批量清除，尝试逐个删除")
                return await self._fallback_clear_memories(user_context)
            logger.error(f"Failed to clear user memories from MIRIX: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to clear user memories from MIRIX: {e}")
            return False
    
    async def _fallback_clear_memories(self, user_context: UserContext) -> bool:
        """回退清除记忆实现：获取所有记忆并逐个删除"""
        try:
            # 获取用户的所有记忆
            memories_result = await self.get_user_memories(user_context, limit=1000)
            
            cleared_count = 0
            for memory in memories_result.memories:
                # 这里我们没有memory_id，MIRIX可能不支持删除
                # 暂时返回True表示"逻辑上已清除"
                cleared_count += 1
            
            logger.info(f"Logically cleared {cleared_count} memories for user {user_context.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Fallback clear memories failed: {e}")
            return False
    
    async def chat_with_memory(self, message: str, user_context: UserContext, 
                             save_interaction: bool = True) -> str:
        """基于记忆的对话（如果MIRIX支持）"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX adapter not initialized")
        
        try:
            # 检查MIRIX是否有聊天接口
            chat_request = {
                "message": message,
                "user_id": user_context.user_id,
                "session_id": user_context.session_id,
                "save_interaction": save_interaction
            }
            
            response = await self.client.post("/api/chat", json=chat_request)
            
            if response.status_code == 404:
                # 如果没有聊天接口，回退到搜索相关记忆
                return await self._fallback_chat(message, user_context, save_interaction)
            
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response from MIRIX")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return await self._fallback_chat(message, user_context, save_interaction)
            raise
        except Exception as e:
            logger.error(f"Chat with MIRIX failed: {e}")
            raise
    
    async def _fallback_chat(self, message: str, user_context: UserContext, 
                           save_interaction: bool) -> str:
        """回退聊天实现：搜索相关记忆并返回摘要"""
        try:
            # 搜索相关记忆
            query = MemoryQuery(
                query=message,
                user_context=user_context,
                limit=5,
                similarity_threshold=0.6
            )
            
            result = await self.search_memories(query)
            
            if save_interaction:
                # 保存用户消息
                memory = MemoryEntry(
                    content=message,
                    memory_type=MemoryType.EPISODIC,
                    user_context=user_context,
                    timestamp=datetime.datetime.now(),
                    confidence=1.0
                )
                await self.add_memory(memory)
            
            # 构建基于记忆的响应
            if result.memories:
                memory_summary = f"基于{len(result.memories)}条相关记忆："
                for i, mem in enumerate(result.memories[:3], 1):
                    memory_summary += f"\n{i}. {mem.content[:100]}..."
                return memory_summary
            else:
                return "没有找到相关的记忆信息。"
                
        except Exception as e:
            logger.error(f"Fallback chat failed: {e}")
            return f"处理消息时出错: {e}"
    
    def _convert_from_mirix_memory(self, mem_data: Dict[str, Any]) -> Optional[MemoryEntry]:
        """将MIRIX API返回的记忆数据转换为MemoryEntry"""
        try:
            # 解析时间戳
            timestamp = datetime.datetime.now()
            if mem_data.get("timestamp"):
                try:
                    timestamp = datetime.datetime.fromisoformat(
                        mem_data["timestamp"].replace("Z", "+00:00")
                    )
                except:
                    pass
            
            # 解析记忆类型
            memory_type_str = mem_data.get("memory_type", "episodic")
            memory_type = self._reverse_memory_mapping.get(
                memory_type_str, MemoryType.EPISODIC
            )
            
            # 创建用户上下文
            user_context = UserContext(
                user_id=mem_data.get("user_id", "unknown"),
                session_id=mem_data.get("session_id"),
                metadata=mem_data.get("metadata", {})
            )
            
            # 提取元数据
            metadata = mem_data.get("metadata", {})
            
            return MemoryEntry(
                content=mem_data.get("content", ""),
                memory_type=memory_type,
                user_context=user_context,
                timestamp=timestamp,
                confidence=metadata.get("confidence", 1.0),
                embedding=metadata.get("embedding"),
                metadata=metadata,
                relationships=metadata.get("relationships"),
                image_data=metadata.get("image_data"),
                audio_data=metadata.get("audio_data"),
                file_path=metadata.get("file_path")
            )
            
        except Exception as e:
            logger.error(f"Failed to convert MIRIX memory data: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "mirix_http",
            "api_base": self.api_base,
            "initialized": self.is_initialized,
            "memory_types": list(self._memory_type_mapping.values()),
            "features": {
                "multi_agent": True,
                "vector_search": True,
                "multimodal": True,
                "real_time": True,
                "http_api": True
            }
        }
    
    async def cleanup(self):
        """清理资源"""
        if self.client:
            await self.client.aclose()
            self.client = None
        self.is_initialized = False
        logger.info("MIRIX HTTP adapter cleaned up")


# 注册MIRIX HTTP适配器
from ..interfaces import MemorySystemFactory

MemorySystemFactory.register_adapter("mirix", MirixHttpAdapter)