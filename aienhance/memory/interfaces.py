"""
记忆系统通用抽象接口定义
基于MIRIX、Mem0、Graphiti等系统的共同模式设计
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import datetime


class MemoryType(Enum):
    """记忆类型枚举 - 基于MIRIX的记忆分类"""
    CORE = "core"              # 核心记忆 - 基本事实和身份信息
    EPISODIC = "episodic"      # 情节记忆 - 特定事件和经历
    SEMANTIC = "semantic"      # 语义记忆 - 知识和概念
    PROCEDURAL = "procedural"  # 程序记忆 - 技能和步骤
    RESOURCE = "resource"      # 资源记忆 - 工具和资料
    KNOWLEDGE = "knowledge"    # 知识库 - 结构化知识


@dataclass
class UserContext:
    """用户上下文信息"""
    user_id: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MemoryEntry:
    """记忆条目 - 统一的记忆数据结构"""
    content: str
    memory_type: MemoryType
    user_context: UserContext
    timestamp: datetime.datetime
    confidence: float = 1.0
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    relationships: Optional[Dict[str, Any]] = None  # For graph-based systems like Graphiti
    
    # 可选的多模态数据
    image_data: Optional[bytes] = None
    audio_data: Optional[bytes] = None
    file_path: Optional[str] = None


@dataclass
class MemoryQuery:
    """记忆查询参数"""
    query: str
    user_context: UserContext
    memory_types: Optional[List[MemoryType]] = None
    limit: int = 10
    similarity_threshold: float = 0.7
    time_range: Optional[tuple[datetime.datetime, datetime.datetime]] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    include_relationships: bool = False  # For graph-based queries


@dataclass
class MemoryResult:
    """记忆查询结果"""
    memories: List[MemoryEntry]
    total_count: int
    query_time: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MemorySystemConfig:
    """记忆系统配置"""
    system_type: str  # "mirix", "mem0", "graphiti", etc.
    api_key: Optional[str] = None
    api_base: Optional[str] = None  # 添加api_base字段
    config_path: Optional[str] = None
    database_url: Optional[str] = None
    embedding_model: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class MemorySystem(ABC):
    """
    记忆系统抽象基类
    
    定义所有记忆系统必须实现的核心接口，确保系统间的可替换性
    参考MIRIX、Mem0、Graphiti等系统的共同模式设计
    """
    
    def __init__(self, config: MemorySystemConfig):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化记忆系统"""
        pass
    
    @abstractmethod
    async def add_memory(self, memory: MemoryEntry) -> str:
        """
        添加记忆
        
        Args:
            memory: 记忆条目
            
        Returns:
            str: 记忆ID
        """
        pass
    
    @abstractmethod
    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """
        搜索记忆
        
        Args:
            query: 查询参数
            
        Returns:
            MemoryResult: 搜索结果
        """
        pass
    
    @abstractmethod
    async def get_memory(self, memory_id: str, user_context: UserContext) -> Optional[MemoryEntry]:
        """
        获取特定记忆
        
        Args:
            memory_id: 记忆ID
            user_context: 用户上下文
            
        Returns:
            Optional[MemoryEntry]: 记忆条目
        """
        pass
    
    @abstractmethod
    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """
        更新记忆
        
        Args:
            memory_id: 记忆ID
            memory: 新的记忆内容
            
        Returns:
            bool: 更新成功
        """
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆ID
            user_context: 用户上下文
            
        Returns:
            bool: 删除成功
        """
        pass
    
    @abstractmethod
    async def get_user_memories(self, user_context: UserContext, 
                              memory_types: Optional[List[MemoryType]] = None,
                              limit: int = 100) -> MemoryResult:
        """
        获取用户的所有记忆
        
        Args:
            user_context: 用户上下文
            memory_types: 记忆类型过滤
            limit: 结果限制
            
        Returns:
            MemoryResult: 用户记忆
        """
        pass
    
    @abstractmethod
    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """
        清除用户记忆
        
        Args:
            user_context: 用户上下文
            
        Returns:
            bool: 清除成功
        """
        pass
    
    # 可选的高级功能接口
    
    async def chat_with_memory(self, message: str, user_context: UserContext, 
                             save_interaction: bool = True) -> str:
        """
        基于记忆的对话接口 (类似Mem0的chat方法)
        
        Args:
            message: 用户消息
            user_context: 用户上下文
            save_interaction: 是否保存交互
            
        Returns:
            str: 响应消息
        """
        # 默认实现：搜索相关记忆并返回
        query = MemoryQuery(
            query=message,
            user_context=user_context,
            limit=5
        )
        
        result = await self.search_memories(query)
        
        if save_interaction:
            # 保存用户消息为记忆
            memory = MemoryEntry(
                content=message,
                memory_type=MemoryType.EPISODIC,
                user_context=user_context,
                timestamp=datetime.datetime.now()
            )
            await self.add_memory(memory)
        
        return f"基于{len(result.memories)}条相关记忆的响应"
    
    async def get_memory_stats(self, user_context: UserContext) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Args:
            user_context: 用户上下文
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {}
        for memory_type in MemoryType:
            query = MemoryQuery(
                query="",
                user_context=user_context,
                memory_types=[memory_type],
                limit=0  # 只获取计数
            )
            result = await self.search_memories(query)
            stats[memory_type.value] = result.total_count
        
        return stats
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": self.config.system_type,
            "initialized": self.is_initialized,
            "config": self.config.custom_config or {}
        }


class MemorySystemFactory:
    """记忆系统工厂类"""
    
    _adapters = {}
    
    @classmethod
    def register_adapter(cls, system_type: str, adapter_class):
        """注册记忆系统适配器"""
        cls._adapters[system_type] = adapter_class
    
    @classmethod
    def create_memory_system(cls, config: MemorySystemConfig) -> MemorySystem:
        """
        创建记忆系统实例
        
        Args:
            config: 系统配置
            
        Returns:
            MemorySystem: 记忆系统实例
        """
        system_type = config.system_type.lower()
        
        if system_type not in cls._adapters:
            raise ValueError(f"不支持的记忆系统类型: {system_type}")
        
        adapter_class = cls._adapters[system_type]
        return adapter_class(config)
    
    @classmethod
    def get_supported_systems(cls) -> List[str]:
        """获取支持的记忆系统类型"""
        return list(cls._adapters.keys())


# 便捷函数
def create_user_context(user_id: str, session_id: Optional[str] = None, 
                       agent_id: Optional[str] = None, **kwargs) -> UserContext:
    """创建用户上下文的便捷函数"""
    return UserContext(
        user_id=user_id,
        session_id=session_id,
        agent_id=agent_id,
        metadata=kwargs if kwargs else None
    )


def create_memory_entry(content: str, memory_type: MemoryType, 
                       user_context: UserContext, **kwargs) -> MemoryEntry:
    """创建记忆条目的便捷函数"""
    return MemoryEntry(
        content=content,
        memory_type=memory_type,
        user_context=user_context,
        timestamp=datetime.datetime.now(),
        **kwargs
    )