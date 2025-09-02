"""
感知层模块 - 对应设计文档第4章
包含用户建模和情境分析等核心感知功能

重构后的感知层采用新的层-模块-子模块架构，
主要入口点是PerceptionLayer类。
"""

# 新架构的主要入口点
from .perception_layer import PerceptionLayer

__all__ = [
    "PerceptionLayer",
]
