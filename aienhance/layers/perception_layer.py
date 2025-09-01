"""
感知层实现
处理用户查询感知、用户建模、情境分析等功能
"""

import logging
from datetime import datetime
from typing import Any

from ..memory.interfaces import create_user_context
from ..modules.user_modeling import (
    CognitiveAnalysisManager,
    LearningStyleManager,
    UserModelingConfig,
    LLMCognitiveAnalysisProvider,
    LLMLearningStyleProvider,
)
from ..modules.context_analysis import (
    ContextAnalysisManager,
    ContextAnalysisConfig,
    LLMContextAnalysisProvider,
)
from ..modules.domain_inference import (
    DomainInferenceConfig,
    DomainInferenceManager,
    LLMDomainInferenceProvider,
)
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

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        memory_system: Any | None = None,
        llm_provider: Any | None = None,
    ):
        """
        初始化感知层

        Args:
            config: 感知层配置
            memory_system: 记忆系统（用于获取用户历史数据）
            llm_provider: LLM提供商（用于语义分析）
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.llm_provider = llm_provider
        self.is_initialized = False

        # 核心组件
        self.cognitive_analysis_manager: CognitiveAnalysisManager | None = None
        self.learning_style_manager: LearningStyleManager | None = None
        self.context_analyzer: ContextAnalysisManager | None = None
        self.domain_inference_manager: DomainInferenceManager | None = None

        # 运行时状态
        self.processing_count = 0
        self.last_processing_time = 0.0

    async def initialize(self) -> bool:
        """初始化感知层组件"""
        try:
            logger.info("Initializing Perception Layer...")

            # 初始化用户建模器（LLM语义分析）
            self.cognitive_analysis_manager = CognitiveAnalysisManager()
            self.learning_style_manager = LearningStyleManager()
            
            if self.llm_provider:
                # 认知特征分析提供商
                cognitive_config = UserModelingConfig(
                    llm_provider=self.llm_provider,
                    analysis_type="cognitive",
                    temperature=0.3
                )
                cognitive_provider = LLMCognitiveAnalysisProvider(cognitive_config)
                await self.cognitive_analysis_manager.register_provider("default", cognitive_provider)
                
                # 学习风格分析提供商
                learning_config = UserModelingConfig(
                    llm_provider=self.llm_provider,
                    analysis_type="learning_style",
                    temperature=0.3
                )
                learning_provider = LLMLearningStyleProvider(learning_config)
                await self.learning_style_manager.register_provider("default", learning_provider)
            
            logger.info("User modeling components initialized")

            # 初始化情境分析器
            self.context_analyzer = ContextAnalysisManager()
            
            if self.llm_provider:
                context_config = ContextAnalysisConfig(
                    llm_provider=self.llm_provider,
                    temperature=0.3
                )
                context_provider = LLMContextAnalysisProvider(context_config)
                await self.context_analyzer.register_provider("default", context_provider)
            
            logger.info("Context analyzer initialized")

            # 初始化领域推断管理器
            self.domain_inference_manager = DomainInferenceManager()
            await self._initialize_domain_inference()

            self.is_initialized = True
            logger.info("Perception Layer initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Perception Layer: {e}")
            self.is_initialized = False
            return False

    async def _initialize_domain_inference(self) -> None:
        """初始化领域推断系统"""
        try:
            # 获取领域推断配置
            domain_config = self.config.get("domain_inference", {})

            # 确定使用哪个LLM提供商（可以与主LLM不同）
            domain_llm_provider = domain_config.get("llm_provider", self.llm_provider)
            if not domain_llm_provider:
                logger.error("No LLM provider configured for domain inference")
                return False

            # 创建领域推断配置
            inference_config = DomainInferenceConfig(
                llm_provider=domain_llm_provider,
                model_name=domain_config.get("model_name"),
                temperature=domain_config.get("temperature", 0.1),
                max_tokens=domain_config.get("max_tokens", 300),
                timeout=domain_config.get("timeout", 10),
                custom_domains=domain_config.get("custom_domains"),
            )

            # 创建和注册LLM提供商
            llm_provider = LLMDomainInferenceProvider(inference_config)
            success = await self.domain_inference_manager.register_provider(
                "llm_primary", llm_provider
            )

            if success:
                logger.info("Domain inference with LLM provider initialized")
            else:
                logger.error("Failed to initialize LLM domain inference")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize domain inference: {e}")
            # 不抛出异常，允许感知层在没有领域推断的情况下运行

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
            "input_query": input_data.query,
            "user_id": input_data.user_id,
            "processing_id": f"perception_{self.processing_count}",
            "steps": [],
        }

        try:
            logger.info(f"Processing perception input for user: {input_data.user_id}")
            processing_metadata["steps"].append("started")

            # 1. 用户画像处理
            user_profile = await self._process_user_profile(
                input_data.user_id,
                input_data.query,
                input_data.context,
                input_data.historical_data,
            )
            processing_metadata["steps"].append("user_profile_generated")

            # 2. 情境分析
            context_profile = await self._process_context_analysis(
                input_data.query, input_data.context, user_profile
            )
            processing_metadata["steps"].append("context_analysis_completed")

            # 3. 感知洞察生成
            perception_insights = await self._generate_perception_insights(
                input_data, user_profile, context_profile
            )
            processing_metadata["steps"].append("perception_insights_generated")

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
                    "user_profile": user_profile,
                    "context_profile": context_profile,
                    "perception_insights": perception_insights,
                },
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                user_profile=user_profile,
                context_profile=context_profile,
                perception_insights=perception_insights,
            )

            logger.info(f"Perception processing completed in {processing_time:.3f}s")
            return output

        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.error(f"Perception processing failed: {e}")
            processing_metadata["error"] = str(e)
            processing_metadata["steps"].append("error")

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
                    updated_at=datetime.now().isoformat(),
                ),
                context_profile=ContextProfile(
                    task_type="unknown",
                    complexity_level=0.5,
                    domain_characteristics={},
                    environmental_factors={},
                ),
                perception_insights={},
            )

    async def _process_user_profile(
        self,
        user_id: str,
        query: str,
        context: dict[str, Any],
        historical_data: list[Any] | None,
    ) -> UserProfile:
        """处理用户画像 - 使用LLM语义分析"""
        try:
            logger.info(f"Processing user profile for: {user_id}")
            
            # 准备用户分析上下文
            analysis_context = {
                "domain_context": context.get("domain", ""),
                "historical_data": str(historical_data or [])[:1000],  # 限制长度
            }

            # 从记忆系统获取用户历史数据
            if self.memory_system:
                try:
                    user_context = create_user_context(user_id)
                    user_memories = await self.memory_system.get_user_memories(
                        user_context, limit=10
                    )
                    if user_memories and hasattr(user_memories, 'memories'):
                        memory_context = [str(mem)[:200] for mem in user_memories.memories[:5]]
                        analysis_context["historical_data"] = "\n".join(memory_context)
                except Exception as e:
                    logger.warning(f"Failed to get user memories: {e}")

            # LLM认知特征分析
            if self.cognitive_analysis_manager:
                cognitive_result = await self.cognitive_analysis_manager.process(
                    query, context=analysis_context
                )
            else:
                # 默认认知特征
                from ..modules.user_modeling import ThinkingMode, CognitiveAnalysisResult
                cognitive_result = CognitiveAnalysisResult(
                    thinking_mode=ThinkingMode.ANALYTICAL,
                    cognitive_complexity=0.5,
                    abstraction_level=0.5,
                    creativity_tendency=0.5,
                    reasoning_preference="标准逻辑推理",
                    confidence=0.3,
                    analysis_basis="未启用LLM分析"
                )

            # LLM学习风格分析
            if self.learning_style_manager:
                learning_result = await self.learning_style_manager.process(
                    query, context=analysis_context
                )
            else:
                # 默认学习风格
                from ..modules.user_modeling import (
                    ProcessingPreference, LearningPace, FeedbackStyle, 
                    KnowledgeConstruction, LearningStyleResult
                )
                learning_result = LearningStyleResult(
                    processing_preference=ProcessingPreference.VISUAL,
                    learning_pace=LearningPace.GRADUAL,
                    feedback_style=FeedbackStyle.GUIDED,
                    knowledge_construction=KnowledgeConstruction.LINEAR,
                    interaction_density=0.5,
                    detail_preference=0.5,
                    example_preference=0.7,
                    explanation="未启用LLM分析"
                )

            # 转换为接口格式
            return UserProfile(
                user_id=user_id,
                cognitive_characteristics={
                    "thinking_mode": cognitive_result.thinking_mode.value,
                    "cognitive_complexity": cognitive_result.cognitive_complexity,
                    "abstraction_level": cognitive_result.abstraction_level,
                    "creativity_tendency": cognitive_result.creativity_tendency,
                    "reasoning_preference": cognitive_result.reasoning_preference,
                },
                knowledge_profile={
                    "core_domains": [context.get("domain", "general")],
                    "edge_domains": [],
                    "knowledge_depth": cognitive_result.cognitive_complexity,
                },
                interaction_preferences={
                    "cognitive_style": learning_result.processing_preference.value,
                    "information_density_preference": learning_result.detail_preference,
                    "processing_speed": learning_result.interaction_density,
                    "feedback_style": learning_result.feedback_style.value,
                    "learning_pace": learning_result.learning_pace.value,
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Failed to process user profile: {e}")
            # 返回默认画像
            return UserProfile(
                user_id=user_id,
                cognitive_characteristics={
                    "thinking_mode": "linear",
                    "cognitive_complexity": 0.5,
                    "abstraction_level": 0.5,
                    "creativity_tendency": 0.5,
                },
                knowledge_profile={
                    "core_domains": ["general"],
                    "edge_domains": [],
                    "knowledge_depth": 0.5,
                },
                interaction_preferences={
                    "cognitive_style": "structured",
                    "information_density_preference": 0.5,
                    "processing_speed": 0.5,
                },
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

    async def _process_context_analysis(
        self, query: str, context: dict[str, Any], user_profile: UserProfile
    ) -> ContextProfile:
        """处理情境分析 - 使用LLM语义分析"""
        try:
            logger.info("Processing context analysis")
            
            # 准备情境分析上下文
            enhanced_context = {
                "background": context.get("background", ""),
                "temporal_context": context.get("temporal_context", "当前时间"),
                "user_cognitive_style": user_profile.cognitive_characteristics.get("thinking_mode", "analytical"),
                "user_complexity_level": user_profile.cognitive_characteristics.get("cognitive_complexity", 0.5)
            }

            # LLM情境分析
            if self.context_analyzer:
                context_result = await self.context_analyzer.process(
                    query, context=enhanced_context
                )
            else:
                # 默认情境分析
                from ..modules.context_analysis import TaskType, UrgencyLevel, ComplexityLevel, ContextAnalysisResult
                context_result = ContextAnalysisResult(
                    task_type=TaskType.ANALYTICAL,
                    urgency_level=UrgencyLevel.MEDIUM,
                    complexity_level=ComplexityLevel.MEDIUM,
                    resource_constraints={
                        "time_pressure": 0.5,
                        "knowledge_gap": 0.5,
                        "tool_availability": 0.5,
                    },
                    social_context={
                        "collaboration_needed": False,
                        "audience_type": "self",
                        "communication_formality": 0.5,
                    },
                    environmental_factors=[],
                    recommended_approach="采用标准分析方法处理",
                    context_summary="未启用LLM分析的默认情境",
                    confidence=0.3
                )

            # 转换为接口格式
            return ContextProfile(
                task_type=context_result.task_type.value,
                complexity_level=context_result.complexity_level.value if hasattr(context_result.complexity_level, 'value') else 0.5,
                domain_characteristics={
                    "primary_domain": context.get("domain", "general"),
                    "secondary_domains": [],
                    "interdisciplinary_score": 0.5,
                },
                environmental_factors={
                    "urgency_level": context_result.urgency_level.value if hasattr(context_result.urgency_level, 'value') else "medium",
                    "resource_constraints": context_result.resource_constraints,
                    "social_context": context_result.social_context,
                    "recommended_approach": context_result.recommended_approach,
                },
            )

        except Exception as e:
            logger.error(f"Failed to process context analysis: {e}")
            # 返回默认情境画像
            return ContextProfile(
                task_type="general_inquiry",
                complexity_level=0.5,
                domain_characteristics={
                    "primary_domain": "general",
                    "secondary_domains": [],
                    "interdisciplinary_score": 0.0,
                },
                environmental_factors={
                    "urgency_level": 0.5,
                    "resource_constraints": {},
                    "social_context": "individual",
                },
            )

    async def _generate_perception_insights(
        self,
        input_data: PerceptionInput,
        user_profile: UserProfile,
        context_profile: ContextProfile,
    ) -> dict[str, Any]:
        """生成感知洞察"""
        try:
            insights = {
                "user_readiness": self._assess_user_readiness(
                    user_profile, context_profile
                ),
                "cognitive_match": self._assess_cognitive_match(
                    user_profile, context_profile
                ),
                "adaptation_suggestions": self._generate_adaptation_suggestions(
                    user_profile, context_profile
                ),
                "processing_preferences": self._extract_processing_preferences(
                    user_profile, input_data.context
                ),
                "domain_familiarity": self._assess_domain_familiarity(
                    user_profile, context_profile
                ),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate perception insights: {e}")
            return {
                "user_readiness": 0.5,
                "cognitive_match": 0.5,
                "adaptation_suggestions": [],
                "processing_preferences": {},
                "domain_familiarity": 0.5,
            }

    def _assess_user_readiness(
        self, user_profile: UserProfile, context_profile: ContextProfile
    ) -> float:
        """评估用户就绪程度"""
        cognitive_complexity = user_profile.cognitive_characteristics.get(
            "cognitive_complexity", 0.5
        )
        
        # 确保cognitive_complexity是数值类型
        if isinstance(cognitive_complexity, str):
            cognitive_complexity = 0.5
        
        task_complexity = context_profile.complexity_level
        
        # 将字符串类型的复杂度转换为数值
        if isinstance(task_complexity, str):
            complexity_map = {"low": 0.3, "medium": 0.5, "high": 0.8}
            task_complexity = complexity_map.get(task_complexity.lower(), 0.5)
        elif not isinstance(task_complexity, (int, float)):
            task_complexity = 0.5

        # 简单的就绪程度评估
        readiness = min(1.0, cognitive_complexity / max(0.1, task_complexity))
        return readiness

    def _assess_cognitive_match(
        self, user_profile: UserProfile, context_profile: ContextProfile
    ) -> float:
        """评估认知匹配度"""
        user_thinking = user_profile.cognitive_characteristics.get(
            "thinking_mode", "linear"
        )
        task_type = context_profile.task_type

        # 简单的匹配度评估逻辑
        match_score = 0.7  # 默认匹配度

        if (
            task_type in ["creative_task", "open_exploration"]
            and "creative" in user_thinking
        ):
            match_score = 0.9
        elif (
            task_type in ["analytical_task", "problem_solving"]
            and "analytical" in user_thinking
        ):
            match_score = 0.9

        return match_score

    def _generate_adaptation_suggestions(
        self, user_profile: UserProfile, context_profile: ContextProfile
    ) -> list[str]:
        """生成适配建议"""
        suggestions = []

        cognitive_complexity = user_profile.cognitive_characteristics.get(
            "cognitive_complexity", 0.5
        )
        
        # 确保cognitive_complexity是数值类型
        if isinstance(cognitive_complexity, str):
            cognitive_complexity = 0.5
            
        task_complexity = context_profile.complexity_level
        
        # 将字符串类型的复杂度转换为数值
        if isinstance(task_complexity, str):
            complexity_map = {"low": 0.3, "medium": 0.5, "high": 0.8}
            task_complexity = complexity_map.get(task_complexity.lower(), 0.5)
        elif not isinstance(task_complexity, (int, float)):
            task_complexity = 0.5

        if task_complexity > cognitive_complexity + 0.2:
            suggestions.append("简化表述，降低认知负荷")
            suggestions.append("提供渐进式解释")
        elif cognitive_complexity > task_complexity + 0.2:
            suggestions.append("增加深度和细节")
            suggestions.append("提供扩展思考")

        return suggestions

    def _extract_processing_preferences(
        self, user_profile: UserProfile, context: dict[str, Any]
    ) -> dict[str, Any]:
        """提取处理偏好"""
        preferences = {
            "preferred_density": user_profile.interaction_preferences.get(
                "information_density_preference", 0.5
            ),
            "preferred_speed": user_profile.interaction_preferences.get(
                "processing_speed", 0.5
            ),
            "cognitive_style": user_profile.interaction_preferences.get(
                "cognitive_style", "structured"
            ),
        }

        return preferences

    def _assess_domain_familiarity(
        self, user_profile: UserProfile, context_profile: ContextProfile
    ) -> float:
        """评估领域熟悉度"""
        user_domains = user_profile.knowledge_profile.get("core_domains", [])
        primary_domain = context_profile.domain_characteristics.get(
            "primary_domain", ""
        )

        if primary_domain in user_domains:
            return 0.8
        elif primary_domain in user_profile.knowledge_profile.get("edge_domains", []):
            return 0.5
        else:
            return 0.2

    async def _extract_initial_user_data(
        self, query: str, context: dict[str, Any], historical_data: list[Any] | None
    ) -> dict[str, Any]:
        """从查询和上下文中提取初始用户数据"""
        initial_data = {
            "initial_query": query,
            "context": context,
            "inferred_domains": await self._infer_domains_from_query(query, context),
            "cognitive_style": "linear",  # 默认值
        }

        if historical_data:
            initial_data["historical_context"] = historical_data

        return initial_data

    async def _infer_domains_from_query(
        self, query: str, context: dict[str, Any] | None = None
    ) -> list[str]:
        """从查询中推断涉及的领域 - 使用大模型进行智能推断"""
        if not self.domain_inference_manager:
            raise RuntimeError("Domain inference manager not configured")

        # 使用大模型进行领域推断
        result = await self.domain_inference_manager.infer_domains(
            query=query, context=context
        )

        # 合并主要领域和次要领域
        all_domains = result.primary_domains + result.secondary_domains
        logger.info(f"LLM domain inference result: {all_domains}")
        logger.debug(f"Reasoning: {result.reasoning}")
        return all_domains

    async def update_user_profile(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> bool:
        """更新用户画像"""
        try:
            if not self.user_modeler:
                return False

            await self.user_modeler.update_user_profile(user_id, interaction_data)
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
                    "thinking_mode": profile.cognitive.thinking_mode.value,
                    "cognitive_complexity": profile.cognitive.cognitive_complexity,
                    "abstraction_level": profile.cognitive.abstraction_level,
                    "creativity_tendency": profile.cognitive.creativity_tendency,
                },
                knowledge_profile={
                    "core_domains": profile.knowledge.core_domains,
                    "edge_domains": profile.knowledge.edge_domains,
                    "knowledge_depth": profile.knowledge.knowledge_depth,
                },
                interaction_preferences={
                    "cognitive_style": profile.interaction.cognitive_style.value,
                    "information_density_preference": profile.interaction.information_density_preference,
                    "processing_speed": profile.interaction.processing_speed,
                },
                created_at=profile.created_at,
                updated_at=profile.updated_at,
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

            # 清理领域推断管理器
            if self.domain_inference_manager:
                await self.domain_inference_manager.cleanup()

            self.is_initialized = False
            logger.info("Perception Layer cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup Perception Layer: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取感知层状态"""
        return {
            "layer_name": "perception",
            "initialized": self.is_initialized,
            "processing_count": self.processing_count,
            "last_processing_time": self.last_processing_time,
            "components": {
                "user_modeler": self.user_modeler is not None,
                "context_analyzer": self.context_analyzer is not None,
            },
            "user_profiles_count": len(self.user_modeler.user_profiles)
            if self.user_modeler
            else 0,
        }
