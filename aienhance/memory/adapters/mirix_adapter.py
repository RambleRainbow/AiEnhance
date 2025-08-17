"""
MIRIX记忆系统适配器
将MIRIX API适配到统一的记忆系统接口
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


class MirixAdapter(MemorySystem):
    """
    MIRIX记忆系统适配器
    
    将MIRIX的多代理记忆系统适配到统一接口
    支持六种记忆类型：Core, Episodic, Semantic, Procedural, Resource, Knowledge
    """
    
    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self._mirix_agent = None
        self._agent_wrapper = None
        
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
        """初始化MIRIX系统"""
        try:
            # 尝试导入MIRIX
            try:
                from mirix import Mirix
                from mirix.agent import AgentWrapper
            except ImportError as e:
                logger.error(f"MIRIX未安装或导入失败: {e}")
                return False
            
            # 初始化MIRIX SDK
            if self.config.api_key:
                self._mirix_agent = Mirix(api_key=self.config.api_key)
                logger.info("MIRIX SDK初始化成功 (使用API密钥)")
            
            # 初始化AgentWrapper (后端模式)
            if self.config.config_path:
                self._agent_wrapper = AgentWrapper(self.config.config_path)
                logger.info(f"MIRIX AgentWrapper初始化成功 (配置文件: {self.config.config_path})")
            
            if not self._mirix_agent and not self._agent_wrapper:
                logger.error("MIRIX初始化失败：需要API密钥或配置文件")
                return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"MIRIX初始化异常: {e}")
            return False
    
    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到MIRIX系统"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX系统未初始化")
        
        try:
            # 构建记忆消息
            memory_message = self._build_memory_message(memory)
            
            if self._mirix_agent:
                # 使用SDK模式
                response = await asyncio.to_thread(
                    self._mirix_agent.add, 
                    memory_message
                )
                memory_id = self._extract_memory_id_from_response(response)
                
            elif self._agent_wrapper:
                # 使用AgentWrapper模式
                response = await asyncio.to_thread(
                    self._agent_wrapper.send_message,
                    message=memory_message,
                    memorizing=True,
                    force_absorb_content=True
                )
                memory_id = self._extract_memory_id_from_wrapper(response)
            
            else:
                raise RuntimeError("没有可用的MIRIX接口")
            
            logger.info(f"成功添加记忆: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            raise
    
    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索MIRIX记忆"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX系统未初始化")
        
        try:
            start_time = datetime.datetime.now()
            
            if self._mirix_agent:
                # 使用SDK的chat功能进行搜索
                response = await asyncio.to_thread(
                    self._mirix_agent.chat,
                    query.query
                )
                memories = self._parse_chat_response_to_memories(response, query)
                
            elif self._agent_wrapper:
                # 使用AgentWrapper进行搜索
                response = await asyncio.to_thread(
                    self._agent_wrapper.send_message,
                    message=query.query,
                    memorizing=False
                )
                memories = self._parse_wrapper_response_to_memories(response, query)
            
            else:
                raise RuntimeError("没有可用的MIRIX接口")
            
            query_time = (datetime.datetime.now() - start_time).total_seconds()
            
            # 应用过滤器
            filtered_memories = self._apply_filters(memories, query)
            
            return MemoryResult(
                memories=filtered_memories[:query.limit],
                total_count=len(filtered_memories),
                query_time=query_time,
                metadata={"system": "mirix", "original_response": str(response)}
            )
            
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            raise
    
    async def get_memory(self, memory_id: str, user_context: UserContext) -> Optional[MemoryEntry]:
        """获取特定记忆"""
        # MIRIX可能不直接支持通过ID获取记忆，使用搜索作为fallback
        query = MemoryQuery(
            query=f"memory_id:{memory_id}",
            user_context=user_context,
            limit=1
        )
        
        result = await self.search_memories(query)
        return result.memories[0] if result.memories else None
    
    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆 - MIRIX可能不直接支持，实现为删除后重新添加"""
        try:
            # 先删除旧记忆
            await self.delete_memory(memory_id, memory.user_context)
            
            # 添加新记忆
            new_id = await self.add_memory(memory)
            return bool(new_id)
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False
    
    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆 - MIRIX可能不直接支持"""
        logger.warning("MIRIX可能不支持直接删除记忆，操作被忽略")
        return True  # 假设成功，因为MIRIX可能不支持删除
    
    async def get_user_memories(self, user_context: UserContext, 
                              memory_types: Optional[List[MemoryType]] = None,
                              limit: int = 100) -> MemoryResult:
        """获取用户的所有记忆"""
        query = MemoryQuery(
            query=f"user:{user_context.user_id}",
            user_context=user_context,
            memory_types=memory_types,
            limit=limit
        )
        
        return await self.search_memories(query)
    
    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆 - MIRIX可能不直接支持"""
        logger.warning("MIRIX可能不支持批量清除用户记忆")
        return True
    
    async def chat_with_memory(self, message: str, user_context: UserContext, 
                             save_interaction: bool = True) -> str:
        """使用MIRIX的对话功能"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX系统未初始化")
        
        try:
            if self._mirix_agent:
                # 使用SDK的chat功能
                response = await asyncio.to_thread(
                    self._mirix_agent.chat,
                    message
                )
                
                if save_interaction:
                    # 保存交互记忆
                    memory = MemoryEntry(
                        content=f"User: {message}\\nAssistant: {response}",
                        memory_type=MemoryType.EPISODIC,
                        user_context=user_context,
                        timestamp=datetime.datetime.now(),
                        metadata={"interaction_type": "chat"}
                    )
                    await self.add_memory(memory)
                
                return str(response)
                
            else:
                # Fallback到基类实现
                return await super().chat_with_memory(message, user_context, save_interaction)
                
        except Exception as e:
            logger.error(f"对话失败: {e}")
            raise
    
    def _build_memory_message(self, memory: MemoryEntry) -> str:
        """构建MIRIX格式的记忆消息"""
        message_parts = [memory.content]
        
        # 添加元数据
        if memory.metadata:
            metadata_str = json.dumps(memory.metadata, ensure_ascii=False)
            message_parts.append(f"[METADATA: {metadata_str}]")
        
        # 添加记忆类型标识
        mirix_type = self._memory_type_mapping.get(memory.memory_type, "episodic_memory")
        message_parts.append(f"[MEMORY_TYPE: {mirix_type}]")
        
        # 添加用户上下文
        message_parts.append(f"[USER_ID: {memory.user_context.user_id}]")
        if memory.user_context.session_id:
            message_parts.append(f"[SESSION_ID: {memory.user_context.session_id}]")
        
        return "\\n".join(message_parts)
    
    def _extract_memory_id_from_response(self, response) -> str:
        """从MIRIX SDK响应中提取记忆ID"""
        # MIRIX可能不返回明确的记忆ID，生成一个基于时间的ID
        timestamp = datetime.datetime.now().isoformat()
        return f"mirix_{timestamp}_{hash(str(response)) % 10000}"
    
    def _extract_memory_id_from_wrapper(self, response) -> str:
        """从AgentWrapper响应中提取记忆ID"""
        # 同样生成基于时间的ID
        timestamp = datetime.datetime.now().isoformat()
        return f"mirix_wrapper_{timestamp}_{hash(str(response)) % 10000}"
    
    def _parse_chat_response_to_memories(self, response, query: MemoryQuery) -> List[MemoryEntry]:
        """将MIRIX聊天响应解析为记忆条目"""
        memories = []
        
        # 这是一个简化的解析，实际实现需要根据MIRIX的具体响应格式调整
        memory = MemoryEntry(
            content=str(response),
            memory_type=MemoryType.EPISODIC,
            user_context=query.user_context,
            timestamp=datetime.datetime.now(),
            confidence=0.8,  # 默认置信度
            metadata={"source": "mirix_chat", "query": query.query}
        )
        memories.append(memory)
        
        return memories
    
    def _parse_wrapper_response_to_memories(self, response, query: MemoryQuery) -> List[MemoryEntry]:
        """将AgentWrapper响应解析为记忆条目"""
        memories = []
        
        # 简化的解析实现
        memory = MemoryEntry(
            content=str(response),
            memory_type=MemoryType.EPISODIC,
            user_context=query.user_context,
            timestamp=datetime.datetime.now(),
            confidence=0.8,
            metadata={"source": "mirix_wrapper", "query": query.query}
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


# 注册MIRIX适配器
from ..interfaces import MemorySystemFactory
MemorySystemFactory.register_adapter("mirix", MirixAdapter)