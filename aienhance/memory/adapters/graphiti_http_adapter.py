"""
Graphiti HTTP REST API适配器
专门用于通过HTTP REST API访问外部Graphiti服务
"""

import datetime
import logging

from ..interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemoryResult,
    MemorySystem,
    MemorySystemConfig,
    MemorySystemFactory,
    MemoryType,
    UserContext,
)

logger = logging.getLogger(__name__)


class GraphitiHttpAdapter(MemorySystem):
    """
    Graphiti HTTP REST API适配器

    专门用于通过HTTP REST API访问外部Graphiti服务
    适用于Docker容器化部署或远程服务访问场景
    """

    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self._http_session = None

        # 验证必需的配置
        if not config.api_base_url:
            raise ValueError("GraphitiHttpAdapter需要api_base_url配置")

    async def initialize(self) -> bool:
        """初始化HTTP客户端"""
        try:
            import aiohttp

            # 创建HTTP会话
            self._http_session = aiohttp.ClientSession()

            # 测试连接
            async with self._http_session.get(
                f"{self.config.api_base_url}/healthcheck"
            ) as response:
                if response.status == 200:
                    logger.info("成功连接到Graphiti HTTP服务")
                    self.is_initialized = True
                    return True
                else:
                    logger.error(f"Graphiti服务健康检查失败: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"HTTP客户端初始化失败: {e}")
            return False

    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到Graphiti系统"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti HTTP适配器未初始化")

        try:
            # 转换为Graphiti API期望的消息格式
            messages_payload = {
                "group_id": memory.user_context.user_id,
                "messages": [
                    {
                        "content": memory.content,
                        "role_type": "user",
                        "role": memory.user_context.user_id,
                        "timestamp": (
                            memory.timestamp.isoformat()
                            if memory.timestamp
                            else datetime.datetime.now().isoformat()
                        ),
                        "source_description": (
                            f"Memory system entry for {memory.memory_type.value} memory"
                        )
                    }
                ]
            }

            async with self._http_session.post(
                f"{self.config.api_base_url}/messages",
                json=messages_payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status in [200, 202]:  # 202表示已接受处理
                    result = await response.json()
                    memory_id = self._extract_memory_id_from_result(result)
                    logger.info(f"成功添加Graphiti记忆: {memory_id}")
                    return memory_id
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"HTTP请求失败: {response.status}, {error_text}")

        except Exception as e:
            logger.error(f"添加Graphiti记忆失败: {e}")
            raise

    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索Graphiti记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti HTTP适配器未初始化")

        try:
            start_time = datetime.datetime.now()

            # 转换为Graphiti API期望的搜索格式
            search_payload = {
                "query": query.query,
                "group_ids": [query.user_context.user_id],
                "max_facts": query.limit
            }

            async with self._http_session.post(
                f"{self.config.api_base_url}/search",
                json=search_payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    search_results = (
                        result if isinstance(result, list) else result.get("results", [])
                    )
                else:
                    # 搜索失败时返回空结果而不是抛出异常
                    logger.warning(f"搜索请求失败: {response.status}")
                    search_results = []

            query_time = (datetime.datetime.now() - start_time).total_seconds()

            # 转换搜索结果为MemoryEntry
            memories = self._convert_search_results_to_memories(search_results, query)

            # 应用过滤器
            filtered_memories = self._apply_filters(memories, query)

            return MemoryResult(
                memories=filtered_memories,
                total_count=len(filtered_memories),
                query_time=query_time,
                metadata={
                    "system": "graphiti_http",
                    "search_type": "http_rest",
                    "api_url": self.config.api_base_url,
                },
            )

        except Exception as e:
            logger.error(f"搜索Graphiti记忆失败: {e}")
            # 返回空结果而不是抛出异常，让系统继续工作
            return MemoryResult(
                memories=[],
                total_count=0,
                query_time=0.0,
                metadata={"system": "graphiti_http", "error": str(e)},
            )

    async def get_memory(
        self, memory_id: str, user_context: UserContext
    ) -> MemoryEntry | None:
        """获取特定记忆 - HTTP模式下暂不支持"""
        logger.warning("GraphitiHttpAdapter暂不支持get_memory操作")
        return None

    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆 - HTTP模式下暂不支持"""
        logger.warning("GraphitiHttpAdapter暂不支持update_memory操作")
        return False

    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆 - HTTP模式下暂不支持"""
        logger.warning("GraphitiHttpAdapter暂不支持delete_memory操作")
        return False

    async def get_user_memories(
        self,
        user_context: UserContext,
        memory_types: list[MemoryType] | None = None,
        limit: int = 100,
    ) -> MemoryResult:
        """获取用户的所有记忆 - 通过搜索空查询实现"""
        try:
            # 使用空查询搜索该用户的所有记忆
            query = MemoryQuery(
                query="",  # 空查询返回所有结果
                user_context=user_context,
                memory_types=memory_types,
                limit=limit
            )
            
            return await self.search_memories(query)

        except Exception as e:
            logger.error(f"获取用户记忆失败: {e}")
            return MemoryResult(
                memories=[],
                total_count=0,
                query_time=0.0,
                metadata={"system": "graphiti_http", "error": str(e)},
            )

    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆"""
        try:
            # 使用清除API
            clear_payload = {
                "group_id": user_context.user_id
            }
            
            async with self._http_session.post(
                f"{self.config.api_base_url}/clear",
                json=clear_payload,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 200:
                    logger.info(f"成功清除用户 {user_context.user_id} 的记忆")
                    return True
                else:
                    logger.error(f"清除记忆失败: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"清除用户记忆失败: {e}")
            return False

    async def cleanup(self):
        """清理资源"""
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
        self.is_initialized = False
        logger.info("GraphitiHttpAdapter资源已清理")

    # 辅助方法

    def _extract_memory_id_from_result(self, result) -> str:
        """从Graphiti结果中提取记忆ID"""
        if isinstance(result, dict):
            return result.get(
                "node_id",
                result.get("id", f"graphiti_http_{datetime.datetime.now().isoformat()}"),
            )
        elif hasattr(result, "id"):
            return str(result.id)
        else:
            return f"graphiti_http_{datetime.datetime.now().isoformat()}_{hash(str(result)) % 10000}"

    def _convert_search_results_to_memories(
        self, results, query: MemoryQuery
    ) -> list[MemoryEntry]:
        """将Graphiti搜索结果转换为MemoryEntry列表"""
        memories = []

        if not results:
            return memories

        for result in results:
            memory = self._convert_graphiti_result_to_entry(result, query.user_context)
            if memory:
                memories.append(memory)

        return memories

    def _convert_graphiti_result_to_entry(
        self, graphiti_result, user_context: UserContext
    ) -> MemoryEntry | None:
        """将Graphiti搜索结果转换为MemoryEntry"""
        try:
            if isinstance(graphiti_result, dict):
                # 处理搜索结果格式
                content = graphiti_result.get(
                    "content", graphiti_result.get("text", str(graphiti_result))
                )
                confidence = float(graphiti_result.get(
                    "score", graphiti_result.get("similarity", 1.0)
                ))
                metadata = graphiti_result.get("metadata", {})

                # 解析时间戳
                timestamp_str = graphiti_result.get(
                    "timestamp", datetime.datetime.now().isoformat()
                )
                try:
                    if isinstance(timestamp_str, str):
                        timestamp = datetime.datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                    else:
                        timestamp = timestamp_str
                except (ValueError, TypeError):
                    timestamp = datetime.datetime.now()

                # 获取记忆类型
                memory_type_str = graphiti_result.get("memory_type", "episodic")
                memory_type = (
                    MemoryType(memory_type_str)
                    if memory_type_str in [mt.value for mt in MemoryType]
                    else MemoryType.EPISODIC
                )

                # 获取关系信息
                relationships = graphiti_result.get(
                    "relationships", graphiti_result.get("entities")
                )

                return MemoryEntry(
                    content=content,
                    memory_type=memory_type,
                    user_context=user_context,
                    timestamp=timestamp,
                    confidence=confidence,
                    metadata=metadata,
                    relationships=relationships,
                )

            return None

        except Exception as e:
            logger.error(f"转换Graphiti记忆失败: {e}")
            return None

    def _apply_filters(
        self, memories: list[MemoryEntry], query: MemoryQuery
    ) -> list[MemoryEntry]:
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


# 注册Graphiti HTTP适配器
MemorySystemFactory.register_adapter("graphiti_http", GraphitiHttpAdapter)
