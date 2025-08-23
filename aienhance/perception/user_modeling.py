"""
用户建模模块 - 现代语义理解驱动的用户画像系统
构建多维度的动态用户画像，为实现个性化记忆激活提供基础
"""

import logging
from typing import Any

from .user_modeling_interfaces import (
    CognitiveProfile,
    CognitiveStyle,
    InteractionProfile,
    KnowledgeProfile,
    ThinkingMode,
    UserModeler,
    UserModelerFactory,
    UserProfile,
)

# 导入具体实现以确保注册
from . import semantic_user_modeler  # noqa: F401

logger = logging.getLogger(__name__)


class DynamicUserModeler:
    """动态用户建模器 - 统一的用户建模接口"""

    def __init__(self, llm_provider=None, modeler_type: str = "semantic"):
        """
        初始化用户建模器

        Args:
            llm_provider: LLM提供商（用于语义分析）
            modeler_type: 建模器类型，默认为"semantic"
        """
        self.llm_provider = llm_provider
        self.modeler_type = modeler_type

        # 创建用户建模器实例
        try:
            self.modeler: UserModeler = UserModelerFactory.create_modeler(
                modeler_type=modeler_type, llm_provider=llm_provider
            )
            logger.info(f"成功创建{modeler_type}用户建模器")
        except Exception as e:
            logger.error(f"创建用户建模器失败: {e}")
            raise

    async def create_user_profile(
        self, user_id: str, initial_data: dict[str, Any]
    ) -> UserProfile:
        """创建完整的用户画像"""
        return await self.modeler.create_user_profile(user_id, initial_data)

    async def update_user_profile(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> UserProfile:
        """动态更新用户画像"""
        return await self.modeler.update_user_profile(user_id, interaction_data)

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        return self.modeler.get_user_profile(user_id)

    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        return self.modeler.get_system_info()

    @property
    def user_profiles(self) -> dict[str, UserProfile]:
        """获取所有用户画像（兼容性接口）"""
        if hasattr(self.modeler, "user_profiles"):
            return self.modeler.user_profiles
        return {}


# 导出公共接口
__all__ = [
    "DynamicUserModeler",
    "UserProfile",
    "CognitiveProfile",
    "KnowledgeProfile",
    "InteractionProfile",
    "CognitiveStyle",
    "ThinkingMode",
    "UserModeler",
    "UserModelerFactory",
]
