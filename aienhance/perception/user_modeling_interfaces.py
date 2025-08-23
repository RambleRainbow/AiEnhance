"""
用户建模系统接口定义
定义标准接口，支持多种用户建模实现方式
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class CognitiveStyle(Enum):
    """认知风格枚举"""

    LINEAR = "linear"  # 线性思维
    NETWORK = "network"  # 网状思维
    HIERARCHICAL = "hierarchical"  # 层次思维


class ThinkingMode(Enum):
    """思维模式枚举"""

    ANALYTICAL = "analytical"  # 分析型
    INTUITIVE = "intuitive"  # 直觉型
    CREATIVE = "creative"  # 创造型


@dataclass
class CognitiveProfile:
    """认知能力画像"""

    thinking_mode: ThinkingMode
    cognitive_complexity: float  # 认知复杂度评估 (0-1)
    abstraction_level: float  # 抽象思维能力 (0-1)
    creativity_tendency: float  # 创造性思维倾向 (0-1)
    reasoning_preference: str  # 推理偏好描述


@dataclass
class KnowledgeProfile:
    """知识结构画像"""

    core_domains: list[str]  # 核心专业领域
    edge_domains: list[str]  # 边缘接触领域
    knowledge_depth: dict[str, float]  # 各领域知识深度 (0-1)
    cross_domain_ability: float  # 跨域知识连接能力 (0-1)
    knowledge_boundaries: list[str]  # 知识边界和盲点


@dataclass
class InteractionProfile:
    """交互模式画像"""

    cognitive_style: CognitiveStyle
    information_density_preference: float  # 信息密度偏好 (0-1)
    processing_speed: float  # 信息处理速度 (0-1)
    feedback_preference: str  # 反馈偏好
    learning_style: str  # 学习风格


@dataclass
class UserProfile:
    """完整用户画像"""

    user_id: str
    cognitive: CognitiveProfile
    knowledge: KnowledgeProfile
    interaction: InteractionProfile
    created_at: str
    updated_at: str


class UserModeler(ABC):
    """用户建模器接口"""

    @abstractmethod
    async def create_user_profile(
        self, user_id: str, initial_data: dict[str, Any]
    ) -> UserProfile:
        """创建用户画像"""
        pass

    @abstractmethod
    async def update_user_profile(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> UserProfile:
        """更新用户画像"""
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        pass

    @abstractmethod
    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        pass


class UserModelerFactory:
    """用户建模器工厂"""

    _modelers: dict[str, type[UserModeler]] = {}

    @classmethod
    def register_modeler(cls, modeler_type: str, modeler_class: type[UserModeler]):
        """注册用户建模器实现"""
        cls._modelers[modeler_type] = modeler_class

    @classmethod
    def create_modeler(
        cls, modeler_type: str = "semantic", llm_provider=None, **kwargs
    ) -> UserModeler:
        """创建用户建模器实例"""
        if modeler_type not in cls._modelers:
            raise ValueError(f"不支持的用户建模器类型: {modeler_type}")

        modeler_class = cls._modelers[modeler_type]

        # 传递必要的参数
        if modeler_type == "semantic":
            if llm_provider is None:
                raise ValueError("SemanticUserModeler requires an llm_provider")
            return modeler_class(llm_provider, **kwargs)
        else:
            return modeler_class(**kwargs)

    @classmethod
    def get_available_modelers(cls) -> list[str]:
        """获取可用的建模器类型"""
        return list(cls._modelers.keys())
