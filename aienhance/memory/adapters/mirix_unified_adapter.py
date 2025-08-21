"""
MIRIX统一适配器
集成LLM桥接功能，支持使用项目统一的大模型抽象
"""

import asyncio
import datetime
import json
import logging
from typing import Any

from ...llm.interfaces import LLMProvider
from ..interfaces import (
    MemoryEntry,
    MemoryQuery,
    MemoryResult,
    MemorySystem,
    MemorySystemConfig,
    MemoryType,
    UserContext,
)
from .mirix_llm_bridge import MirixLLMBridge

logger = logging.getLogger(__name__)


class MirixUnifiedAdapter(MemorySystem):
    """
    MIRIX统一适配器
    
    支持两种模式：
    1. 标准模式：使用MIRIX默认的大模型配置
    2. 统一模式：使用项目的LLM抽象层（推荐）
    """

    def __init__(self, config: MemorySystemConfig, llm_provider: LLMProvider | None = None):
        """
        初始化MIRIX统一适配器
        
        Args:
            config: 记忆系统配置
            llm_provider: 可选的LLM提供商，如果提供则使用统一模式
        """
        super().__init__(config)
        self._mirix = None
        self._llm_provider = llm_provider
        self._llm_bridge = None
        self._use_unified_llm = llm_provider is not None

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
        """初始化MIRIX适配器"""
        try:
            # 尝试导入MIRIX SDK
            try:
                from mirix import Mirix
            except ImportError as e:
                logger.error(f"MIRIX SDK未安装: {e}")
                logger.info("请运行: pip install mirix")
                return False

            if self._use_unified_llm:
                # 统一模式：使用项目的LLM抽象
                success = await self._initialize_unified_mode(Mirix)
            else:
                # 标准模式：使用MIRIX默认配置
                success = await self._initialize_standard_mode(Mirix)

            if success:
                # 测试连接
                await self._test_connection()
                self.is_initialized = True
                mode = "统一模式" if self._use_unified_llm else "标准模式"
                logger.info(f"MIRIX适配器初始化成功 ({mode})")
                return True

            return False

        except Exception as e:
            logger.error(f"MIRIX适配器初始化失败: {e}")
            return False

    async def _initialize_unified_mode(self, Mirix) -> bool:
        """
        初始化统一模式
        
        Args:
            Mirix: MIRIX SDK类
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 确保LLM提供商已初始化
            if not self._llm_provider.is_initialized:
                await self._llm_provider.initialize()

            # 创建LLM桥接器
            self._llm_bridge = MirixLLMBridge(self._llm_provider)

            # 设置环境变量
            self._llm_bridge.setup_environment_variables()

            # 创建MIRIX配置文件
            config_path = self._llm_bridge.create_mirix_config("aienhance_unified")

            # 获取初始化参数
            init_params = self._llm_bridge.get_initialization_params()

            # 初始化MIRIX SDK
            self._mirix = Mirix(**init_params)

            logger.info(f"统一模式初始化成功，使用LLM: {self._llm_provider.config.provider}/{self._llm_provider.config.model_name}")
            return True

        except Exception as e:
            logger.error(f"统一模式初始化失败: {e}")
            return False

    async def _initialize_standard_mode(self, Mirix) -> bool:
        """
        初始化标准模式
        
        Args:
            Mirix: MIRIX SDK类
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 检查API密钥
            if not self.config.api_key:
                logger.error("标准模式需要API密钥")
                logger.info("请设置Google API密钥用于MIRIX")
                return False

            # 使用默认配置初始化MIRIX SDK
            self._mirix = Mirix(api_key=self.config.api_key)

            logger.info("标准模式初始化成功，使用MIRIX默认配置")
            return True

        except Exception as e:
            logger.error(f"标准模式初始化失败: {e}")
            return False

    async def _test_connection(self):
        """测试MIRIX连接"""
        try:
            # 发送一个测试记忆
            test_response = await asyncio.to_thread(
                self._mirix.add,
                "AiEnhance MIRIX connection test"
            )
            logger.debug(f"MIRIX连接测试成功: {test_response}")
        except Exception as e:
            raise RuntimeError(f"MIRIX连接测试失败: {e}")

    async def add_memory(self, memory: MemoryEntry) -> str:
        """添加记忆到MIRIX系统"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX适配器未初始化")

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
            raise RuntimeError("MIRIX适配器未初始化")

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
                    "system": "mirix_unified",
                    "mode": "unified" if self._use_unified_llm else "standard",
                    "llm_provider": self._llm_provider.config.provider if self._llm_provider else "mirix_default",
                    "original_response": str(response),
                    "search_query": search_query
                }
            )

        except Exception as e:
            logger.error(f"搜索MIRIX记忆失败: {e}")
            raise

    async def chat_with_memory(self, message: str, user_context: UserContext,
                             save_interaction: bool = True) -> str:
        """使用MIRIX的对话功能"""
        if not self.is_initialized:
            raise RuntimeError("MIRIX适配器未初始化")

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
                    content=f"用户: {message}\\nAI: {response}",
                    memory_type=MemoryType.EPISODIC,
                    user_context=user_context,
                    timestamp=datetime.datetime.now(),
                    metadata={
                        "interaction_type": "chat",
                        "user_message": message,
                        "ai_response": str(response),
                        "llm_mode": "unified" if self._use_unified_llm else "standard"
                    }
                )
                await self.add_memory(interaction_memory)

            return str(response)

        except Exception as e:
            logger.error(f"MIRIX对话失败: {e}")
            raise

    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        info = {
            "system_type": "mirix_unified",
            "initialized": self.is_initialized,
            "mode": "unified" if self._use_unified_llm else "standard",
            "memory_types": list(self._memory_type_mapping.values()),
            "features": {
                "multi_agent": True,
                "vector_search": True,
                "multimodal": True,
                "real_time": True,
                "sdk_based": True,
                "cloud_api": True,
                "unified_llm": self._use_unified_llm
            }
        }

        if self._use_unified_llm and self._llm_provider:
            info["llm_provider"] = {
                "provider": self._llm_provider.config.provider,
                "model": self._llm_provider.config.model_name,
                "initialized": self._llm_provider.is_initialized
            }
        else:
            info["llm_provider"] = {
                "provider": "mirix_default",
                "model": "gemini-2.0-flash",
                "initialized": self.is_initialized
            }

        return info

    async def cleanup(self):
        """清理资源"""
        if self._llm_bridge:
            self._llm_bridge.cleanup()
            self._llm_bridge = None

        self._mirix = None
        self.is_initialized = False
        logger.info("MIRIX统一适配器已清理")

    # 继承原有的辅助方法
    async def get_memory(self, memory_id: str, user_context: UserContext) -> MemoryEntry | None:
        """获取特定记忆"""
        query = MemoryQuery(
            query=f"记忆ID: {memory_id}",
            user_context=user_context,
            limit=1
        )

        result = await self.search_memories(query)
        return result.memories[0] if result.memories else None

    async def update_memory(self, memory_id: str, memory: MemoryEntry) -> bool:
        """更新记忆"""
        try:
            new_id = await self.add_memory(memory)
            return bool(new_id)
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False

    async def delete_memory(self, memory_id: str, user_context: UserContext) -> bool:
        """删除记忆"""
        logger.warning("MIRIX不支持删除记忆操作")
        return True

    async def get_user_memories(self, user_context: UserContext,
                              memory_types: list[MemoryType] | None = None,
                              limit: int = 100) -> MemoryResult:
        """获取用户的所有记忆"""
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
        """清除用户记忆"""
        logger.warning("MIRIX不支持批量清除用户记忆")
        return True

    # 辅助方法保持不变
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

        return "\\n".join(message_parts)

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

        return "\\n".join(contextual_parts)

    def _generate_memory_id(self, memory: MemoryEntry, response) -> str:
        """生成记忆ID"""
        timestamp = datetime.datetime.now().isoformat()
        content_hash = hash(memory.content) % 10000
        mode = "unified" if self._use_unified_llm else "standard"
        return f"mirix_{mode}_{timestamp}_{content_hash}"

    def _parse_search_response(self, response, query: MemoryQuery) -> list[MemoryEntry]:
        """将MIRIX搜索响应解析为记忆条目"""
        memories = []

        # 创建基于响应的记忆条目
        memory = MemoryEntry(
            content=str(response),
            memory_type=MemoryType.EPISODIC,
            user_context=query.user_context,
            timestamp=datetime.datetime.now(),
            confidence=0.8,
            metadata={
                "source": "mirix_unified_search",
                "query": query.query,
                "mode": "unified" if self._use_unified_llm else "standard",
                "response_type": "chat_based_search"
            }
        )
        memories.append(memory)

        return memories

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

        # 元数据过滤
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                filtered = [m for m in filtered
                          if m.metadata and m.metadata.get(key) == value]

        return filtered


# 注册MIRIX统一适配器
from ..interfaces import MemorySystemFactory

MemorySystemFactory.register_adapter("mirix_unified", MirixUnifiedAdapter)
