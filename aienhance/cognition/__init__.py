"""
认知层模块 - 对应设计文档第5章
包含多层次记忆激活、语义补充、类比推理等核心认知功能

重构后的认知层采用新的层-模块-子模块架构。
"""

# 新架构的主要入口点
from .cognition_layer import CognitionLayer
from .memory_activation import MemoryFragment

__all__ = [
    # 新架构 - 推荐使用
    "CognitionLayer",
    "MemoryFragment",
]
