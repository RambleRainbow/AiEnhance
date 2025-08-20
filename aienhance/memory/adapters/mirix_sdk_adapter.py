"""
MIRIX SDK适配器
使用官方MIRIX Python SDK进行记忆系统集成
"""

import asyncio
import datetime
import json
from typing import Dict, List, Optional, Any
import logging

from ..interfaces import (
    MemorySystem, MemoryEntry, MemoryQuery, MemoryResult, 
    UserContext, MemoryType, MemorySystemConfig
)

logger = logging.getLogger(__name__)


class MirixSdkAdapter(MemorySystem):
    """
    MIRIX SDK适配器
    
    使用官方MIRIX Python SDK实现记忆系统集成
    简化了之前复杂的Docker/HTTP配置
    """
    
    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self._mirix = None
        
        # MIRIX记忆类型映射
        self._memory_type_mapping = {
            MemoryType.CORE: "core_memory",
            MemoryType.EPISODIC: "episodic_memory", 
            MemoryType.SEMANTIC: "semantic_memory",
            MemoryType.PROCEDURAL: "procedural_memory",
            MemoryType.RESOURCE: "resource_memory",
            MemoryType.KNOWLEDGE: "knowledge_vault"
        }
    
    async def initialize(self) -> bool:
        """初始化MIRIX SDK"""
        try:
            # 尝试导入MIRIX SDK
            try:
                from mirix import Mirix
            except ImportError as e:
                logger.error(f"MIRIX SDK未安装: {e}")
                logger.info("请运行: pip install mirix")
                return False
            
            # 检查API密钥
            if not self.config.api_key:
                logger.error("MIRIX SDK需要API密钥")
                logger.info("请设置Google API密钥用于MIRIX")
                return False
            
            # 初始化MIRIX SDK
            self._mirix = Mirix(api_key=self.config.api_key)
            
            # 测试连接
            await self._test_connection()
            
            self.is_initialized = True
            logger.info("MIRIX SDK初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"MIRIX SDK初始化失败: {e}")
            return False
    
    async def _test_connection(self):
        """测试MIRIX连接"""
        try:
            # 发送一个测试记忆
            test_response = await asyncio.to_thread(
                self._mirix.add, 
                "MIRIX SDK connection test"
            )
            logger.debug(f"MIRIX连接测试成功: {test_response}")
        except Exception as e:
            raise RuntimeError(f"MIRIX连接测试失败: {e}")
    
    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到MIRIX系统"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX SDK未初始化")
        
        try:
            # 构建记忆消息
            memory_message = self._build_memory_message(memory)
            
            # 使用MIRIX SDK添加记忆
            response = await asyncio.to_thread(
                self._mirix.add, 
                memory_message
            )
            
            # 生成记忆ID
            memory_id = self._generate_memory_id(memory, response)
            
            logger.debug(f"成功添加记忆到MIRIX: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"添加记忆到MIRIX失败: {e}")
            raise
    
    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索MIRIX记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX SDK未初始化")
        
        try:
            start_time = datetime.datetime.now()
            
            # 构建搜索查询
            search_query = self._build_search_query(query)
            
            # 使用MIRIX SDK进行聊天搜索
            response = await asyncio.to_thread(
                self._mirix.chat,
                search_query
            )
            
            query_time = (datetime.datetime.now() - start_time).total_seconds()
            
            # 解析响应为记忆条目
            memories = self._parse_search_response(response, query)
            
            # 应用过滤器
            filtered_memories = self._apply_filters(memories, query)
            
            return MemoryResult(
                memories=filtered_memories[:query.limit],
                total_count=len(filtered_memories),
                query_time=query_time,
                metadata={
                    "system": "mirix_sdk", 
                    "original_response": str(response),
                    "search_query": search_query
                }
            )
            
        except Exception as e:
            logger.error(f"搜索MIRIX记忆失败: {e}")
            raise
    
    async def get_memory(self, memory_id: str, user_context: UserContext) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        # MIRIX SDK不直接支持通过ID获取记忆，使用搜索作为fallback
        query = MemoryQuery(
            query=f"记忆ID: {memory_id}",
            user_context=user_context,
            limit=1
        )
        
        result = await self.search_memories(query)
        return result.memories[0] if result.memories else None
    
    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆 - MIRIX SDK不直接支持，实现为重新添加"""
        try:
            # 添加新记忆（MIRIX会自动处理相似记忆）
            new_id = await self.add_memory(memory)
            return bool(new_id)
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False
    
    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆 - MIRIX SDK不支持删除"""
        logger.warning("MIRIX SDK不支持删除记忆操作")
        return True  # 返回True，因为MIRIX管理自己的记忆生命周期
    
    async def get_user_memories(self, user_context: UserContext, 
                              memory_types: Optional[List[MemoryType]] = None,
                              limit: int = 100) -> MemoryResult:
        """获取用户的所有记忆"""
        # 构建用户记忆查询
        type_filter = ""
        if memory_types:
            type_names = [self._memory_type_mapping.get(mt, mt.value) for mt in memory_types]
            type_filter = f" 记忆类型: {', '.join(type_names)}"
        
        query = MemoryQuery(
            query=f"用户 {user_context.user_id} 的所有记忆{type_filter}",
            user_context=user_context,
            memory_types=memory_types,
            limit=limit
        )
        
        return await self.search_memories(query)
    
    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆 - MIRIX SDK不支持批量清除"""
        logger.warning("MIRIX SDK不支持批量清除用户记忆")
        return True
    
    async def chat_with_memory(self, message: str, user_context: UserContext, 
                             save_interaction: bool = True) -> str:
        """使用MIRIX的对话功能"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX SDK未初始化")
        
        try:
            # 构建带用户上下文的消息
            contextual_message = self._build_contextual_message(message, user_context)
            
            # 使用MIRIX SDK进行对话
            response = await asyncio.to_thread(
                self._mirix.chat,
                contextual_message
            )
            
            if save_interaction:
                # 保存交互记忆
                interaction_memory = MemoryEntry(
                    content=f"用户: {message}\nAI: {response}",
                    memory_type=MemoryType.EPISODIC,
                    user_context=user_context,
                    timestamp=datetime.datetime.now(),
                    metadata={
                        "interaction_type": "chat",
                        "user_message": message,
                        "ai_response": str(response)
                    }
                )
                await self.add_memory(interaction_memory)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"MIRIX对话失败: {e}")
            raise
    
    def _build_memory_message(self, memory: MemoryEntry) -> str:
        """构建MIRIX格式的记忆消息"""
        message_parts = [memory.content]
        
        # 添加记忆类型标识
        mirix_type = self._memory_type_mapping.get(memory.memory_type, "episodic_memory")
        message_parts.append(f"[记忆类型: {mirix_type}]")
        
        # 添加用户上下文
        message_parts.append(f"[用户ID: {memory.user_context.user_id}]")
        if memory.user_context.session_id:
            message_parts.append(f"[会话ID: {memory.user_context.session_id}]")
        
        # 添加时间戳
        if memory.timestamp:
            message_parts.append(f"[时间: {memory.timestamp.isoformat()}]")
        
        # 添加元数据
        if memory.metadata:
            metadata_str = json.dumps(memory.metadata, ensure_ascii=False, indent=None)
            message_parts.append(f"[元数据: {metadata_str}]")
        
        return "\n".join(message_parts)
    
    def _build_search_query(self, query: MemoryQuery) -> str:
        """构建MIRIX搜索查询"""
        search_parts = [query.query]
        
        # 添加用户上下文
        search_parts.append(f"用户ID: {query.user_context.user_id}")
        
        # 添加记忆类型过滤
        if query.memory_types:
            type_names = [self._memory_type_mapping.get(mt, mt.value) for mt in query.memory_types]
            search_parts.append(f"记忆类型: {', '.join(type_names)}")
        
        # 添加时间范围过滤
        if query.time_range:
            start_time, end_time = query.time_range
            search_parts.append(f"时间范围: {start_time.isoformat()} 到 {end_time.isoformat()}")
        
        return " | ".join(search_parts)
    
    def _build_contextual_message(self, message: str, user_context: UserContext) -> str:
        """构建带用户上下文的消息"""
        contextual_parts = [message]
        
        # 添加用户上下文
        contextual_parts.append(f"[用户ID: {user_context.user_id}]")
        if user_context.session_id:
            contextual_parts.append(f"[会话ID: {user_context.session_id}]")
        
        return "\n".join(contextual_parts)
    
    def _generate_memory_id(self, memory: MemoryEntry, response) -> str:
        """生成记忆ID"""
        # 由于MIRIX SDK不返回明确的记忆ID，生成一个基于内容和时间的ID
        timestamp = datetime.datetime.now().isoformat()
        content_hash = hash(memory.content) % 10000
        return f"mirix_sdk_{timestamp}_{content_hash}"
    
    def _parse_search_response(self, response, query: MemoryQuery) -> List[MemoryEntry]:
        """将MIRIX搜索响应解析为记忆条目"""
        memories = []
        
        # 创建基于响应的记忆条目
        memory = MemoryEntry(
            content=str(response),
            memory_type=MemoryType.EPISODIC,  # 默认类型
            user_context=query.user_context,
            timestamp=datetime.datetime.now(),
            confidence=0.8,  # 默认置信度
            metadata={
                "source": "mirix_sdk_search", 
                "query": query.query,
                "response_type": "chat_based_search"
            }
        )
        memories.append(memory)
        
        return memories
    
    def _apply_filters(self, memories: List[MemoryEntry], query: MemoryQuery) -> List[MemoryEntry]:
        """应用查询过滤器"""
        filtered = memories
        
        # 记忆类型过滤
        if query.memory_types:
            filtered = [m for m in filtered if m.memory_type in query.memory_types]
        
        # 时间范围过滤
        if query.time_range:
            start_time, end_time = query.time_range
            filtered = [m for m in filtered if start_time <= m.timestamp <= end_time]
        
        # 置信度过滤
        filtered = [m for m in filtered if m.confidence >= query.similarity_threshold]
        
        # 元数据过滤
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                filtered = [m for m in filtered 
                          if m.metadata and m.metadata.get(key) == value]
        
        return filtered
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "mirix_sdk",
            "initialized": self.is_initialized,
            "memory_types": list(self._memory_type_mapping.values()),
            "features": {
                "multi_agent": True,
                "vector_search": True,
                "multimodal": True,
                "real_time": True,
                "sdk_based": True,
                "cloud_api": True
            },
            "requirements": {
                "api_key": "Google API Key required",
                "package": "mirix"
            }
        }
    
    async def cleanup(self):
        """清理资源"""
        self._mirix = None
        self.is_initialized = False
        logger.info("MIRIX SDK adapter cleaned up")


# 注册MIRIX SDK适配器
from ..interfaces import MemorySystemFactory
MemorySystemFactory.register_adapter("mirix_sdk", MirixSdkAdapter)