"""
Graphiti记忆系统适配器
将Graphiti知识图谱记忆系统适配到统一接口
"""

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


class GraphitiAdapter(MemorySystem):
    """
    Graphiti记忆系统适配器

    适配Graphiti的时序感知知识图谱记忆系统
    支持实体关系、时间查询、混合搜索等高级功能
    """

    def __init__(self, config: MemorySystemConfig):
        super().__init__(config)
        self._graphiti_client = None

    async def initialize(self) -> bool:
        """初始化Graphiti系统"""
        try:
            # 尝试导入Graphiti
            try:
                from graphiti import Graphiti
            except ImportError as e:
                logger.error(f"Graphiti未安装或导入失败: {e}")
                return False

            # 初始化Graphiti客户端
            init_kwargs = {}

            # 添加数据库配置
            if self.config.database_url:
                init_kwargs["neo4j_uri"] = self.config.database_url

            # 添加自定义配置
            if self.config.custom_config:
                init_kwargs.update(self.config.custom_config)

            self._graphiti_client = Graphiti(**init_kwargs)

            # 初始化图谱
            await self._graphiti_client.build_indices_and_constraints()

            self.is_initialized = True
            logger.info("Graphiti系统初始化成功")
            return True

        except Exception as e:
            logger.error(f"Graphiti初始化异常: {e}")
            return False

    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到Graphiti系统"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            # 构建Graphiti格式的数据
            episode_data = {
                "content": memory.content,
                "timestamp": memory.timestamp,
                "user_id": memory.user_context.user_id,
                "memory_type": memory.memory_type.value,
            }

            # 添加额外的上下文信息
            if memory.user_context.session_id:
                episode_data["session_id"] = memory.user_context.session_id

            if memory.user_context.agent_id:
                episode_data["agent_id"] = memory.user_context.agent_id

            # 添加元数据
            if memory.metadata:
                episode_data["metadata"] = memory.metadata

            # 添加关系信息 (如果有)
            if memory.relationships:
                episode_data["relationships"] = memory.relationships

            # 调用Graphiti的add_episode方法
            result = await self._graphiti_client.add_episode(episode_data)

            # 提取记忆ID
            memory_id = self._extract_memory_id_from_result(result)

            logger.info(f"成功添加Graphiti记忆: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"添加Graphiti记忆失败: {e}")
            raise

    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """搜索Graphiti记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            start_time = datetime.datetime.now()

            # 准备Graphiti搜索参数
            search_kwargs = {
                "query": query.query,
                "limit": query.limit,
                "user_id": query.user_context.user_id,
            }

            # 添加时间范围 (Graphiti支持时序查询)
            if query.time_range:
                start_timestamp, end_timestamp = query.time_range
                search_kwargs["timestamp_range"] = (start_timestamp, end_timestamp)

            # 添加实体关系查询 (如果需要)
            if query.include_relationships:
                search_kwargs["include_entities"] = True
                search_kwargs["include_relationships"] = True

            # 添加元数据过滤
            if query.metadata_filters:
                search_kwargs["metadata_filter"] = query.metadata_filters

            # 执行混合搜索 (语义 + BM25)
            search_results = await self._graphiti_client.hybrid_search(**search_kwargs)

            query_time = (datetime.datetime.now() - start_time).total_seconds()

            # 转换搜索结果为MemoryEntry
            memories = self._convert_search_results_to_memories(search_results, query)

            # 应用额外过滤器
            filtered_memories = self._apply_filters(memories, query)

            return MemoryResult(
                memories=filtered_memories,
                total_count=len(filtered_memories),
                query_time=query_time,
                metadata={
                    "system": "graphiti",
                    "search_type": "hybrid",
                    "original_results": search_results,
                },
            )

        except Exception as e:
            logger.error(f"搜索Graphiti记忆失败: {e}")
            raise

    async def get_memory(
        self, memory_id: str, user_context: UserContext
    ) -> MemoryEntry | None:
        """获取特定记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            # Graphiti通过节点ID获取记忆
            result = await self._graphiti_client.get_node(
                node_id=memory_id, user_id=user_context.user_id
            )

            if result:
                return self._convert_graphiti_node_to_entry(result, user_context)

            return None

        except Exception as e:
            logger.error(f"获取Graphiti记忆失败: {e}")
            return None

    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            # Graphiti支持节点更新
            update_data = {
                "node_id": memory_id,
                "content": memory.content,
                "timestamp": memory.timestamp,
                "user_id": memory.user_context.user_id,
            }

            if memory.metadata:
                update_data["metadata"] = memory.metadata

            if memory.relationships:
                update_data["relationships"] = memory.relationships

            result = await self._graphiti_client.update_node(update_data)

            return bool(result)

        except Exception as e:
            logger.error(f"更新Graphiti记忆失败: {e}")
            return False

    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            result = await self._graphiti_client.delete_node(
                node_id=memory_id, user_id=user_context.user_id
            )

            return bool(result)

        except Exception as e:
            logger.error(f"删除Graphiti记忆失败: {e}")
            return False

    async def get_user_memories(
        self,
        user_context: UserContext,
        memory_types: list[MemoryType] | None = None,
        limit: int = 100,
    ) -> MemoryResult:
        """获取用户的所有记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            # 构建Cypher查询获取用户所有记忆
            cypher_query = """
            MATCH (n:Memory {user_id: $user_id})
            RETURN n
            ORDER BY n.timestamp DESC
            LIMIT $limit
            """

            query_params = {"user_id": user_context.user_id, "limit": limit}

            # 添加记忆类型过滤
            if memory_types:
                memory_type_values = [mt.value for mt in memory_types]
                cypher_query = cypher_query.replace(
                    "MATCH (n:Memory {user_id: $user_id})",
                    "MATCH (n:Memory {user_id: $user_id}) WHERE n.memory_type IN $memory_types",
                )
                query_params["memory_types"] = memory_type_values

            results = await self._graphiti_client.run_cypher_query(
                cypher_query, query_params
            )

            # 转换结果
            memories = [
                self._convert_graphiti_node_to_entry(result["n"], user_context)
                for result in results
            ]

            return MemoryResult(
                memories=memories,
                total_count=len(memories),
                query_time=0.0,
                metadata={"system": "graphiti", "method": "cypher_query"},
            )

        except Exception as e:
            logger.error(f"获取用户记忆失败: {e}")
            raise

    async def clear_user_memories(self, user_context: UserContext) -> bool:
        """清除用户记忆"""
        if not self.is_initialized:
            raise RuntimeError("Graphiti系统未初始化")

        try:
            # 使用Cypher查询删除用户所有记忆
            cypher_query = """
            MATCH (n:Memory {user_id: $user_id})
            DETACH DELETE n
            RETURN count(n) as deleted_count
            """

            result = await self._graphiti_client.run_cypher_query(
                cypher_query, {"user_id": user_context.user_id}
            )

            deleted_count = result[0]["deleted_count"] if result else 0
            logger.info(f"清除了 {deleted_count} 条用户记忆")

            return True

        except Exception as e:
            logger.error(f"清除用户记忆失败: {e}")
            return False

    # Graphiti特有的高级功能

    async def get_entity_timeline(
        self, entity_name: str, user_context: UserContext
    ) -> list[MemoryEntry]:
        """获取实体的时间线记忆"""
        try:
            timeline_data = await self._graphiti_client.get_entity_timeline(
                entity_name=entity_name, user_id=user_context.user_id
            )

            memories = [
                self._convert_graphiti_timeline_to_entry(item, user_context)
                for item in timeline_data
            ]

            return memories

        except Exception as e:
            logger.error(f"获取实体时间线失败: {e}")
            return []

    async def query_relationships(
        self, query: str, user_context: UserContext
    ) -> dict[str, Any]:
        """查询实体关系"""
        try:
            relationships = await self._graphiti_client.query_relationships(
                query=query, user_id=user_context.user_id
            )

            return {
                "relationships": relationships,
                "query": query,
                "user_id": user_context.user_id,
            }

        except Exception as e:
            logger.error(f"查询关系失败: {e}")
            return {}

    def _extract_memory_id_from_result(self, result) -> str:
        """从Graphiti结果中提取记忆ID"""
        if isinstance(result, dict):
            return result.get(
                "node_id",
                result.get("id", f"graphiti_{datetime.datetime.now().isoformat()}"),
            )
        elif hasattr(result, "id"):
            return str(result.id)
        else:
            return f"graphiti_{datetime.datetime.now().isoformat()}_{hash(str(result)) % 10000}"

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
                confidence = graphiti_result.get(
                    "score", graphiti_result.get("similarity", 1.0)
                )
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
                except:
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

    def _convert_graphiti_node_to_entry(
        self, node, user_context: UserContext
    ) -> MemoryEntry | None:
        """将Graphiti节点转换为MemoryEntry"""
        # 类似于_convert_graphiti_result_to_entry，但处理节点对象
        return self._convert_graphiti_result_to_entry(dict(node), user_context)

    def _convert_graphiti_timeline_to_entry(
        self, timeline_item, user_context: UserContext
    ) -> MemoryEntry:
        """将Graphiti时间线项转换为MemoryEntry"""
        return self._convert_graphiti_result_to_entry(timeline_item, user_context)

    def _apply_filters(
        self, memories: list[MemoryEntry], query: MemoryQuery
    ) -> list[MemoryEntry]:
        """应用查询过滤器"""
        filtered = memories

        # 记忆类型过滤
        if query.memory_types:
            filtered = [m for m in filtered if m.memory_type in query.memory_types]

        # 时间范围过滤 (Graphiti已在查询时处理，这里是额外保险)
        if query.time_range:
            start_time, end_time = query.time_range
            filtered = [m for m in filtered if start_time <= m.timestamp <= end_time]

        # 置信度过滤
        filtered = [m for m in filtered if m.confidence >= query.similarity_threshold]

        return filtered


# 注册Graphiti适配器
from ..interfaces import MemorySystemFactory

MemorySystemFactory.register_adapter("graphiti", GraphitiAdapter)
