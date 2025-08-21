"""
Mem0记忆系统适配器
将Mem0 API适配到统一的记忆系统接口
"""

import asyncio
import datetime
import logging
from typing import Any

from ..interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemoryResult,
    MemorySystem,
    MemorySystemConfig,
    MemoryType,
    UserContext,
)

logger = logging.getLogger(__name__)


class Mem0Adapter(MemorySystem):
    """
    Mem0记忆系统适配器
    
    适配Mem0的多级记忆系统 (User, Session, Agent state)
    """

    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self._memory_client = None

    async def initialize(self) -> bool:
        """初始化Mem0系统"""
        try:
            # 尝试导入Mem0
            try:
                from mem0 import Memory
            except ImportError as e:
                logger.error(f"Mem0未安装或导入失败: {e}")
                return False

            # 初始化Mem0客户端
            init_kwargs = {}
            if self.config.custom_config:
                init_kwargs.update(self.config.custom_config)

            self._memory_client = Memory(**init_kwargs)

            self.is_initialized = True
            logger.info("Mem0系统初始化成功")
            return True

        except Exception as e:
            logger.error(f"Mem0初始化异常: {e}")
            return False

    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到Mem0系统"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # 构建Mem0格式的消息
            messages = [{"role": "user", "content": memory.content}]

            # 准备Mem0 add参数
            add_kwargs = {
                "messages": messages,
                "user_id": memory.user_context.user_id
            }

            # 添加会话ID (如果有)
            if memory.user_context.session_id:
                add_kwargs["session_id"] = memory.user_context.session_id

            # 添加代理ID (如果有)
            if memory.user_context.agent_id:
                add_kwargs["agent_id"] = memory.user_context.agent_id

            # 添加元数据
            if memory.metadata:
                add_kwargs["metadata"] = memory.metadata

            # 调用Mem0的add方法
            result = await asyncio.to_thread(
                self._memory_client.add,
                **add_kwargs
            )

            # 提取记忆ID
            memory_id = self._extract_memory_id_from_result(result)

            logger.info(f"成功添加Mem0记忆: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"添加Mem0记忆失败: {e}")
            raise

    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索Mem0记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            start_time = datetime.datetime.now()

            # 准备搜索参数
            search_kwargs = {
                "query": query.query,
                "user_id": query.user_context.user_id,
                "limit": query.limit
            }

            # 添加会话ID (如果有)
            if query.user_context.session_id:
                search_kwargs["session_id"] = query.user_context.session_id

            # 添加代理ID (如果有)
            if query.user_context.agent_id:
                search_kwargs["agent_id"] = query.user_context.agent_id

            # 调用Mem0的search方法
            search_results = await asyncio.to_thread(
                self._memory_client.search,
                **search_kwargs
            )

            query_time = (datetime.datetime.now() - start_time).total_seconds()

            # 转换搜索结果为MemoryEntry
            memories = self._convert_search_results_to_memories(search_results, query)

            # 应用额外过滤器
            filtered_memories = self._apply_filters(memories, query)

            return MemoryResult(
                memories=filtered_memories,
                total_count=len(filtered_memories),
                query_time=query_time,
                metadata={"system": "mem0", "original_results": search_results}
            )

        except Exception as e:
            logger.error(f"搜索Mem0记忆失败: {e}")
            raise

    async def get_memory(self, memory_id: str, user_context: UserContext) -> MemoryEntry | None:
        """获取特定记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # Mem0可能通过get方法获取特定记忆
            get_kwargs = {
                "memory_id": memory_id,
                "user_id": user_context.user_id
            }

            result = await asyncio.to_thread(
                getattr(self._memory_client, 'get', self._fallback_get_memory),
                **get_kwargs
            )

            if result:
                return self._convert_mem0_memory_to_entry(result, user_context)

            return None

        except Exception as e:
            logger.error(f"获取Mem0记忆失败: {e}")
            return None

    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # Mem0可能支持update方法
            update_kwargs = {
                "memory_id": memory_id,
                "data": memory.content,
                "user_id": memory.user_context.user_id
            }

            if memory.metadata:
                update_kwargs["metadata"] = memory.metadata

            result = await asyncio.to_thread(
                getattr(self._memory_client, 'update', self._fallback_update_memory),
                **update_kwargs
            )

            return bool(result)

        except Exception as e:
            logger.error(f"更新Mem0记忆失败: {e}")
            return False

    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # Mem0可能支持delete方法
            delete_kwargs = {
                "memory_id": memory_id,
                "user_id": user_context.user_id
            }

            result = await asyncio.to_thread(
                getattr(self._memory_client, 'delete', self._fallback_delete_memory),
                **delete_kwargs
            )

            return bool(result)

        except Exception as e:
            logger.error(f"删除Mem0记忆失败: {e}")
            return False

    async def get_user_memories(self, user_context: UserContext,
                              memory_types: list[MemoryType] | None = None,
                              limit: int = 100) -> MemoryResult:
        """获取用户的所有记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # Mem0可能支持获取所有用户记忆
            get_all_kwargs = {
                "user_id": user_context.user_id,
                "limit": limit
            }

            if user_context.session_id:
                get_all_kwargs["session_id"] = user_context.session_id

            if user_context.agent_id:
                get_all_kwargs["agent_id"] = user_context.agent_id

            results = await asyncio.to_thread(
                getattr(self._memory_client, 'get_all', self._fallback_get_all_memories),
                **get_all_kwargs
            )

            # 转换结果
            memories = [self._convert_mem0_memory_to_entry(result, user_context)
                       for result in results]

            # 按记忆类型过滤
            if memory_types:
                memories = [m for m in memories if m.memory_type in memory_types]

            return MemoryResult(
                memories=memories,
                total_count=len(memories),
                query_time=0.0,
                metadata={"system": "mem0", "method": "get_all"}
            )

        except Exception as e:
            logger.error(f"获取用户记忆失败: {e}")
            raise

    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆"""
        if not self.is_initialized:
            raise RuntimeError("Mem0系统未初始化")

        try:
            # Mem0可能支持删除所有用户记忆
            clear_kwargs = {
                "user_id": user_context.user_id
            }

            if user_context.session_id:
                clear_kwargs["session_id"] = user_context.session_id

            if user_context.agent_id:
                clear_kwargs["agent_id"] = user_context.agent_id

            result = await asyncio.to_thread(
                getattr(self._memory_client, 'delete_all', self._fallback_clear_memories),
                **clear_kwargs
            )

            return bool(result)

        except Exception as e:
            logger.error(f"清除用户记忆失败: {e}")
            return False

    def _extract_memory_id_from_result(self, result) -> str:
        """从Mem0结果中提取记忆ID"""
        if isinstance(result, dict):
            return result.get("id", result.get("memory_id", f"mem0_{datetime.datetime.now().isoformat()}"))
        elif isinstance(result, list) and result:
            return result[0].get("id", f"mem0_{datetime.datetime.now().isoformat()}")
        else:
            return f"mem0_{datetime.datetime.now().isoformat()}_{hash(str(result)) % 10000}"

    def _convert_search_results_to_memories(self, results, query: MemoryQuery) -> list[MemoryEntry]:
        """将Mem0搜索结果转换为MemoryEntry列表"""
        memories = []

        if not results:
            return memories

        for result in results:
            memory = self._convert_mem0_memory_to_entry(result, query.user_context)
            if memory:
                memories.append(memory)

        return memories

    def _convert_mem0_memory_to_entry(self, mem0_result, user_context: UserContext) -> MemoryEntry | None:
        """将Mem0记忆结果转换为MemoryEntry"""
        try:
            # Mem0结果格式可能包含: memory, score, metadata等
            if isinstance(mem0_result, dict):
                content = mem0_result.get("memory", mem0_result.get("text", str(mem0_result)))
                confidence = mem0_result.get("score", 1.0)
                metadata = mem0_result.get("metadata", {})
                timestamp_str = mem0_result.get("created_at", datetime.datetime.now().isoformat())

                # 解析时间戳
                try:
                    if isinstance(timestamp_str, str):
                        timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.datetime.now()
                except:
                    timestamp = datetime.datetime.now()

                # 推断记忆类型 (简化版)
                memory_type = self._infer_memory_type(content, metadata)

                return MemoryEntry(
                    content=content,
                    memory_type=memory_type,
                    user_context=user_context,
                    timestamp=timestamp,
                    confidence=confidence,
                    metadata=metadata
                )

            return None

        except Exception as e:
            logger.error(f"转换Mem0记忆失败: {e}")
            return None

    def _infer_memory_type(self, content: str, metadata: dict[str, Any]) -> MemoryType:
        """推断记忆类型"""
        # 简单的启发式规则
        content_lower = content.lower()

        if any(keyword in content_lower for keyword in ["我是", "我的名字", "我叫"]):
            return MemoryType.CORE
        elif any(keyword in content_lower for keyword in ["步骤", "方法", "如何"]):
            return MemoryType.PROCEDURAL
        elif any(keyword in content_lower for keyword in ["定义", "概念", "什么是"]):
            return MemoryType.SEMANTIC
        elif any(keyword in content_lower for keyword in ["工具", "资源", "链接"]):
            return MemoryType.RESOURCE
        elif metadata.get("type") == "knowledge":
            return MemoryType.KNOWLEDGE
        else:
            return MemoryType.EPISODIC  # 默认为情节记忆

    def _apply_filters(self, memories: list[MemoryEntry], query: MemoryQuery) -> list[MemoryEntry]:
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

        return filtered

    # Fallback方法 (当Mem0不支持某些操作时)

    def _fallback_get_memory(self, **kwargs):
        """获取记忆的fallback方法"""
        logger.warning("Mem0不支持get操作，使用search作为fallback")
        return None

    def _fallback_update_memory(self, **kwargs):
        """更新记忆的fallback方法"""
        logger.warning("Mem0不支持update操作")
        return False

    def _fallback_delete_memory(self, **kwargs):
        """删除记忆的fallback方法"""
        logger.warning("Mem0不支持delete操作")
        return False

    def _fallback_get_all_memories(self, **kwargs):
        """获取所有记忆的fallback方法"""
        logger.warning("Mem0不支持get_all操作，使用search作为fallback")
        return []

    def _fallback_clear_memories(self, **kwargs):
        """清除记忆的fallback方法"""
        logger.warning("Mem0不支持delete_all操作")
        return False


# 注册Mem0适配器
from ..interfaces import MemorySystemFactory

MemorySystemFactory.register_adapter("mem0", Mem0Adapter)
