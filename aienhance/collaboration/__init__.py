"""
协作层模块 - 实现人机深度认知协作
通过辩证视角生成、认知挑战适应等机制增强认知协同
"""

from .dialectical_perspective import DialecticalPerspectiveGenerator
from .cognitive_challenge import CognitiveChallenge
from .collaborative_coordinator import CollaborativeCoordinator
from .interfaces import (
    PerspectiveRequest,
    PerspectiveResult,
    ChallengeRequest,
    ChallengeResult,
    CollaborationContext
)

__all__ = [
    'DialecticalPerspectiveGenerator',
    'CognitiveChallenge', 
    'CollaborativeCoordinator',
    'PerspectiveRequest',
    'PerspectiveResult',
    'ChallengeRequest',
    'ChallengeResult',
    'CollaborationContext'
]