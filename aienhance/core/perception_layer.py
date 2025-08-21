"""
感知层实现
处理用户查询感知、用户建模、情境分析等功能
"""

import logging
from datetime import datetime
from typing import Any

from ..memory.interfaces import create_user_context
from ..perception import DynamicUserModeler, IntegratedContextAnalyzer
from .layer_interfaces import (
    ContextProfile,
    IPerceptionLayer,
    PerceptionInput,
    PerceptionOutput,
    ProcessingStatus,
    UserProfile,
)

logger = logging.getLogger(__name__)


class PerceptionLayer(IPerceptionLayer):
    """感知层具体实现"""

    def __init__(self, config: dict[str, Any] | None = None,
                 memory_system: Any | None = None):
        """
        初始化感知层
        
        Args:
            config: 感知层配置
            memory_system: 记忆系统（用于获取用户历史数据）
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.is_initialized = False

        # 核心组件
        self.user_modeler: DynamicUserModeler | None = None
        self.context_analyzer: IntegratedContextAnalyzer | None = None

        # 运行时状态
        self.processing_count = 0
        self.last_processing_time = 0.0

    async def initialize(self) -> bool:
        """初始化感知层组件"""
        try:
            logger.info("Initializing Perception Layer...")

            # 初始化用户建模器
            self.user_modeler = DynamicUserModeler()
            logger.info("User modeler initialized")

            # 初始化情境分析器
            self.context_analyzer = IntegratedContextAnalyzer()
            logger.info("Context analyzer initialized")

            self.is_initialized = True
            logger.info("Perception Layer initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Perception Layer: {e}")
            self.is_initialized = False
            return False

    async def process(self, input_data: PerceptionInput) -> PerceptionOutput:
        """
        处理感知层输入，生成用户画像和情境分析
        
        Args:
            input_data: 感知层输入数据
            
        Returns:
            PerceptionOutput: 感知层处理结果
        """
        if not self.is_initialized:
            raise RuntimeError("Perception Layer not initialized")

        start_time = datetime.now()
        processing_metadata = {
            'input_query': input_data.query,
            'user_id': input_data.user_id,
            'processing_id': f"perception_{self.processing_count}",
            'steps': []
        }

        try:
            logger.info(f"Processing perception input for user: {input_data.user_id}")
            processing_metadata['steps'].append('started')

            # 1. 用户画像处理
            user_profile = await self._process_user_profile(
                input_data.user_id,
                input_data.query,
                input_data.context,
                input_data.historical_data
            )
            processing_metadata['steps'].append('user_profile_generated')

            # 2. 情境分析
            context_profile = await self._process_context_analysis(
                input_data.query,
                input_data.context,
                user_profile
            )
            processing_metadata['steps'].append('context_analysis_completed')

            # 3. 感知洞察生成
            perception_insights = await self._generate_perception_insights(
                input_data, user_profile, context_profile
            )
            processing_metadata['steps'].append('perception_insights_generated')

            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.last_processing_time = processing_time
            self.processing_count += 1

            # 构建输出
            output = PerceptionOutput(
                layer_name="perception",
                status=ProcessingStatus.COMPLETED,
                data={
                    'user_profile': user_profile,
                    'context_profile': context_profile,
                    'perception_insights': perception_insights
                },
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                user_profile=user_profile,
                context_profile=context_profile,
                perception_insights=perception_insights
            )

            logger.info(f"Perception processing completed in {processing_time:.3f}s")
            return output

        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.error(f"Perception processing failed: {e}")
            processing_metadata['error'] = str(e)
            processing_metadata['steps'].append('error')

            # 返回错误状态的输出
            return PerceptionOutput(
                layer_name="perception",
                status=ProcessingStatus.ERROR,
                data={},
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                error_message=str(e),
                user_profile=UserProfile(
                    user_id=input_data.user_id,
                    cognitive_characteristics={},
                    knowledge_profile={},
                    interaction_preferences={},
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ),
                context_profile=ContextProfile(
                    task_type="unknown",
                    complexity_level=0.5,
                    domain_characteristics={},
                    environmental_factors={}
                ),
                perception_insights={}
            )

    async def _process_user_profile(self, user_id: str, query: str,
                                  context: dict[str, Any],
                                  historical_data: list[Any] | None) -> UserProfile:
        """处理用户画像"""
        try:
            # 获取或创建用户画像
            existing_profile = self.user_modeler.get_user_profile(user_id)

            if existing_profile:
                logger.info(f"Found existing user profile for: {user_id}")
                # 转换为接口定义的UserProfile格式
                return UserProfile(
                    user_id=existing_profile.user_id,
                    cognitive_characteristics={
                        'thinking_mode': existing_profile.cognitive.thinking_mode.value,
                        'cognitive_complexity': existing_profile.cognitive.cognitive_complexity,
                        'abstraction_level': existing_profile.cognitive.abstraction_level,
                        'creativity_tendency': existing_profile.cognitive.creativity_tendency
                    },
                    knowledge_profile={
                        'core_domains': existing_profile.knowledge.core_domains,
                        'edge_domains': existing_profile.knowledge.edge_domains,
                        'knowledge_depth': existing_profile.knowledge.knowledge_depth
                    },
                    interaction_preferences={
                        'cognitive_style': existing_profile.interaction.cognitive_style.value,
                        'information_density_preference': existing_profile.interaction.information_density_preference,
                        'processing_speed': existing_profile.interaction.processing_speed
                    },
                    created_at=existing_profile.created_at,
                    updated_at=existing_profile.updated_at
                )
            else:
                # 创建新用户画像
                logger.info(f"Creating new user profile for: {user_id}")
                initial_data = await self._extract_initial_user_data(
                    query, context, historical_data
                )

                # 从记忆系统获取用户历史数据
                if self.memory_system:
                    try:
                        user_context = create_user_context(user_id)
                        user_memories = await self.memory_system.get_user_memories(
                            user_context, limit=50
                        )
                        initial_data['memory_context'] = user_memories.memories
                    except Exception as e:
                        logger.warning(f"Failed to get user memories: {e}")

                new_profile = self.user_modeler.create_user_profile(
                    user_id, initial_data
                )

                # 转换为接口格式
                return UserProfile(
                    user_id=new_profile.user_id,
                    cognitive_characteristics={
                        'thinking_mode': new_profile.cognitive.thinking_mode.value,
                        'cognitive_complexity': new_profile.cognitive.cognitive_complexity,
                        'abstraction_level': new_profile.cognitive.abstraction_level,
                        'creativity_tendency': new_profile.cognitive.creativity_tendency
                    },
                    knowledge_profile={
                        'core_domains': new_profile.knowledge.core_domains,
                        'edge_domains': new_profile.knowledge.edge_domains,
                        'knowledge_depth': new_profile.knowledge.knowledge_depth
                    },
                    interaction_preferences={
                        'cognitive_style': new_profile.interaction.cognitive_style.value,
                        'information_density_preference': new_profile.interaction.information_density_preference,
                        'processing_speed': new_profile.interaction.processing_speed
                    },
                    created_at=new_profile.created_at,
                    updated_at=new_profile.updated_at
                )

        except Exception as e:
            logger.error(f"Failed to process user profile: {e}")
            # 返回默认画像
            return UserProfile(
                user_id=user_id,
                cognitive_characteristics={
                    'thinking_mode': 'linear',
                    'cognitive_complexity': 0.5,
                    'abstraction_level': 0.5,
                    'creativity_tendency': 0.5
                },
                knowledge_profile={
                    'core_domains': ['general'],
                    'edge_domains': [],
                    'knowledge_depth': 0.5
                },
                interaction_preferences={
                    'cognitive_style': 'structured',
                    'information_density_preference': 0.5,
                    'processing_speed': 0.5
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

    async def _process_context_analysis(self, query: str, context: dict[str, Any],
                                      user_profile: UserProfile) -> ContextProfile:
        """处理情境分析"""
        try:
            # 增强上下文（添加用户画像信息）
            enhanced_context = {
                **context,
                'user_profile': user_profile
            }

            # 使用情境分析器
            context_result = self.context_analyzer.analyze_context(
                query, enhanced_context
            )

            # 转换为接口格式
            return ContextProfile(
                task_type=context_result.task_characteristics.task_type.value,
                complexity_level=context_result.task_characteristics.complexity_level,
                domain_characteristics={
                    'primary_domain': context_result.domain_characteristics.primary_domain,
                    'secondary_domains': context_result.domain_characteristics.secondary_domains,
                    'interdisciplinary_score': context_result.domain_characteristics.interdisciplinary_score
                },
                environmental_factors={
                    'urgency_level': context_result.environmental_factors.urgency_level,
                    'resource_constraints': context_result.environmental_factors.resource_constraints,
                    'social_context': context_result.environmental_factors.social_context
                }
            )

        except Exception as e:
            logger.error(f"Failed to process context analysis: {e}")
            # 返回默认情境画像
            return ContextProfile(
                task_type="general_inquiry",
                complexity_level=0.5,
                domain_characteristics={
                    'primary_domain': 'general',
                    'secondary_domains': [],
                    'interdisciplinary_score': 0.0
                },
                environmental_factors={
                    'urgency_level': 0.5,
                    'resource_constraints': {},
                    'social_context': 'individual'
                }
            )

    async def _generate_perception_insights(self, input_data: PerceptionInput,
                                          user_profile: UserProfile,
                                          context_profile: ContextProfile) -> dict[str, Any]:
        """生成感知洞察"""
        try:
            insights = {
                'user_readiness': self._assess_user_readiness(user_profile, context_profile),
                'cognitive_match': self._assess_cognitive_match(user_profile, context_profile),
                'adaptation_suggestions': self._generate_adaptation_suggestions(
                    user_profile, context_profile
                ),
                'processing_preferences': self._extract_processing_preferences(
                    user_profile, input_data.context
                ),
                'domain_familiarity': self._assess_domain_familiarity(
                    user_profile, context_profile
                )
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate perception insights: {e}")
            return {
                'user_readiness': 0.5,
                'cognitive_match': 0.5,
                'adaptation_suggestions': [],
                'processing_preferences': {},
                'domain_familiarity': 0.5
            }

    def _assess_user_readiness(self, user_profile: UserProfile,
                              context_profile: ContextProfile) -> float:
        """评估用户就绪程度"""
        cognitive_complexity = user_profile.cognitive_characteristics.get('cognitive_complexity', 0.5)
        task_complexity = context_profile.complexity_level

        # 简单的就绪程度评估
        readiness = min(1.0, cognitive_complexity / max(0.1, task_complexity))
        return readiness

    def _assess_cognitive_match(self, user_profile: UserProfile,
                               context_profile: ContextProfile) -> float:
        """评估认知匹配度"""
        user_thinking = user_profile.cognitive_characteristics.get('thinking_mode', 'linear')
        task_type = context_profile.task_type

        # 简单的匹配度评估逻辑
        match_score = 0.7  # 默认匹配度

        if task_type in ['creative_task', 'open_exploration'] and 'creative' in user_thinking:
            match_score = 0.9
        elif task_type in ['analytical_task', 'problem_solving'] and 'analytical' in user_thinking:
            match_score = 0.9

        return match_score

    def _generate_adaptation_suggestions(self, user_profile: UserProfile,
                                       context_profile: ContextProfile) -> list[str]:
        """生成适配建议"""
        suggestions = []

        cognitive_complexity = user_profile.cognitive_characteristics.get('cognitive_complexity', 0.5)
        task_complexity = context_profile.complexity_level

        if task_complexity > cognitive_complexity + 0.2:
            suggestions.append("简化表述，降低认知负荷")
            suggestions.append("提供渐进式解释")
        elif cognitive_complexity > task_complexity + 0.2:
            suggestions.append("增加深度和细节")
            suggestions.append("提供扩展思考")

        return suggestions

    def _extract_processing_preferences(self, user_profile: UserProfile,
                                      context: dict[str, Any]) -> dict[str, Any]:
        """提取处理偏好"""
        preferences = {
            'preferred_density': user_profile.interaction_preferences.get(
                'information_density_preference', 0.5
            ),
            'preferred_speed': user_profile.interaction_preferences.get(
                'processing_speed', 0.5
            ),
            'cognitive_style': user_profile.interaction_preferences.get(
                'cognitive_style', 'structured'
            )
        }

        return preferences

    def _assess_domain_familiarity(self, user_profile: UserProfile,
                                 context_profile: ContextProfile) -> float:
        """评估领域熟悉度"""
        user_domains = user_profile.knowledge_profile.get('core_domains', [])
        primary_domain = context_profile.domain_characteristics.get('primary_domain', '')

        if primary_domain in user_domains:
            return 0.8
        elif primary_domain in user_profile.knowledge_profile.get('edge_domains', []):
            return 0.5
        else:
            return 0.2

    async def _extract_initial_user_data(self, query: str, context: dict[str, Any],
                                       historical_data: list[Any] | None) -> dict[str, Any]:
        """从查询和上下文中提取初始用户数据"""
        initial_data = {
            'initial_query': query,
            'context': context,
            'inferred_domains': self._infer_domains_from_query(query),
            'cognitive_style': 'linear'  # 默认值
        }

        if historical_data:
            initial_data['historical_context'] = historical_data

        return initial_data

    def _infer_domains_from_query(self, query: str) -> list[str]:
        """从查询中推断涉及的领域"""
        # 简单的关键词匹配
        domain_keywords = {
            'technology': ['技术', '科技', '编程', 'AI', '人工智能', '软件'],
            'education': ['教育', '学习', '教学', '培训'],
            'science': ['科学', '研究', '实验', '理论'],
            'business': ['商业', '管理', '营销', '经济'],
            'art': ['艺术', '设计', '创作', '美学']
        }

        detected_domains = []
        query_lower = query.lower()

        for domain, keywords in domain_keywords.items():
            if any(keyword.lower() in query_lower for keyword in keywords):
                detected_domains.append(domain)

        return detected_domains if detected_domains else ['general']

    async def update_user_profile(self, user_id: str,
                                interaction_data: dict[str, Any]) -> bool:
        """更新用户画像"""
        try:
            if not self.user_modeler:
                return False

            self.user_modeler.update_user_profile(user_id, interaction_data)
            logger.info(f"Updated user profile for: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            return False

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        try:
            if not self.user_modeler:
                return None

            profile = self.user_modeler.get_user_profile(user_id)
            if not profile:
                return None

            # 转换为接口格式
            return UserProfile(
                user_id=profile.user_id,
                cognitive_characteristics={
                    'thinking_mode': profile.cognitive.thinking_mode.value,
                    'cognitive_complexity': profile.cognitive.cognitive_complexity,
                    'abstraction_level': profile.cognitive.abstraction_level,
                    'creativity_tendency': profile.cognitive.creativity_tendency
                },
                knowledge_profile={
                    'core_domains': profile.knowledge.core_domains,
                    'edge_domains': profile.knowledge.edge_domains,
                    'knowledge_depth': profile.knowledge.knowledge_depth
                },
                interaction_preferences={
                    'cognitive_style': profile.interaction.cognitive_style.value,
                    'information_density_preference': profile.interaction.information_density_preference,
                    'processing_speed': profile.interaction.processing_speed
                },
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )

        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None

    async def cleanup(self) -> None:
        """清理感知层资源"""
        try:
            logger.info("Cleaning up Perception Layer resources...")

            # 清理用户建模器
            if self.user_modeler:
                # 如果有需要清理的资源
                pass

            # 清理情境分析器
            if self.context_analyzer:
                # 如果有需要清理的资源
                pass

            self.is_initialized = False
            logger.info("Perception Layer cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup Perception Layer: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取感知层状态"""
        return {
            'layer_name': 'perception',
            'initialized': self.is_initialized,
            'processing_count': self.processing_count,
            'last_processing_time': self.last_processing_time,
            'components': {
                'user_modeler': self.user_modeler is not None,
                'context_analyzer': self.context_analyzer is not None
            },
            'user_profiles_count': len(self.user_modeler.user_profiles) if self.user_modeler else 0
        }
