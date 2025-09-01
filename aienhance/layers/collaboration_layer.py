"""
协作层实现
处理多元观点生成、认知挑战、辩证思考等协作功能
"""

import logging
from datetime import datetime
from typing import Any

from ..modules.collaborative_reasoning import (
    MultiPerspectiveManager,
    ChallengeGenerationManager,
    CollaborativeReasoningConfig,
    LLMMultiPerspectiveProvider,
    LLMChallengeGenerationProvider,
)
from .layer_interfaces import (
    CognitiveChallenge,
    CollaborationInput,
    CollaborationOutput,
    ICollaborationLayer,
    PerspectiveGeneration,
    ProcessingStatus,
)

logger = logging.getLogger(__name__)


class CollaborationLayer(ICollaborationLayer):
    """协作层具体实现"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        llm_provider: Any | None = None,
        memory_system: Any | None = None,
    ):
        """
        初始化协作层

        Args:
            config: 协作层配置
            llm_provider: 大语言模型提供商
            memory_system: 记忆系统
        """
        self.config = config or {}
        self.llm_provider = llm_provider
        self.memory_system = memory_system
        self.is_initialized = False

        # 核心组件
        self.perspective_manager: MultiPerspectiveManager | None = None
        self.challenge_manager: ChallengeGenerationManager | None = None

        # 运行时状态
        self.processing_count = 0
        self.last_processing_time = 0.0
        self.collaboration_history = []  # 协作历史记录

    async def initialize(self) -> bool:
        """初始化协作层组件"""
        try:
            logger.info("Initializing Collaboration Layer...")

            # 检查依赖
            if not self.llm_provider:
                logger.warning("No LLM provider available for collaboration layer")
                return False

            # 初始化多元观点管理器
            self.perspective_manager = MultiPerspectiveManager()
            
            if self.llm_provider:
                perspective_config = CollaborativeReasoningConfig(
                    llm_provider=self.llm_provider,
                    reasoning_type="multi_perspective",
                    temperature=0.6
                )
                perspective_provider = LLMMultiPerspectiveProvider(perspective_config)
                await self.perspective_manager.register_provider("default", perspective_provider)
            
            logger.info("Perspective manager initialized")

            # 初始化认知挑战管理器
            self.challenge_manager = ChallengeGenerationManager()
            
            if self.llm_provider:
                challenge_config = CollaborativeReasoningConfig(
                    llm_provider=self.llm_provider,
                    reasoning_type="challenge_generation",
                    temperature=0.7
                )
                challenge_provider = LLMChallengeGenerationProvider(challenge_config)
                await self.challenge_manager.register_provider("default", challenge_provider)
            
            logger.info("Challenge manager initialized")

            self.is_initialized = True
            logger.info("Collaboration Layer initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Collaboration Layer: {e}")
            self.is_initialized = False
            return False

    async def process(self, input_data: CollaborationInput) -> CollaborationOutput:
        """
        处理协作层输入，生成多元观点和认知挑战

        Args:
            input_data: 协作层输入数据

        Returns:
            CollaborationOutput: 协作层处理结果
        """
        if not self.is_initialized:
            raise RuntimeError("Collaboration Layer not initialized")

        start_time = datetime.now()
        processing_metadata = {
            "input_query": input_data.query,
            "user_id": input_data.user_profile.user_id,
            "processing_id": f"collaboration_{self.processing_count}",
            "steps": [],
        }

        try:
            logger.info(
                f"Processing collaboration input for user: {input_data.user_profile.user_id}"
            )
            processing_metadata["steps"].append("started")

            # 1. 生成多元观点
            perspective_generation = await self.generate_perspectives(
                input_data.query,
                {
                    "user_profile": input_data.user_profile,
                    "context_profile": input_data.context_profile,
                    "behavior_output": input_data.behavior_output,
                    "collaboration_context": input_data.collaboration_context,
                },
            )
            processing_metadata["steps"].append("perspective_generation_completed")

            # 2. 创建认知挑战
            cognitive_challenge = await self.create_cognitive_challenges(
                input_data.behavior_output.adapted_content.content,
                input_data.user_profile,
            )
            processing_metadata["steps"].append("cognitive_challenge_completed")

            # 3. 编排协作过程
            enhanced_collaboration = await self.orchestrate_collaboration(input_data)
            processing_metadata["steps"].append("collaboration_orchestration_completed")

            # 4. 生成协作洞察
            collaboration_insights = await self._generate_collaboration_insights(
                input_data,
                perspective_generation,
                cognitive_challenge,
                enhanced_collaboration,
            )
            processing_metadata["steps"].append("collaboration_insights_generated")

            # 5. 检查是否需要增强内容
            enhanced_content = None
            if self._should_enhance_content(
                perspective_generation, cognitive_challenge
            ):
                enhanced_content = await self._enhance_content_with_collaboration(
                    input_data.behavior_output.adapted_content.content,
                    perspective_generation,
                    cognitive_challenge,
                )
                processing_metadata["steps"].append("content_enhancement_completed")

            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.last_processing_time = processing_time
            self.processing_count += 1

            # 记录协作历史
            self.collaboration_history.append(
                {
                    "timestamp": end_time.isoformat(),
                    "user_id": input_data.user_profile.user_id,
                    "query": input_data.query,
                    "perspectives_count": len(perspective_generation.perspectives),
                    "challenges_count": len(cognitive_challenge.challenges),
                }
            )

            # 构建输出
            output = CollaborationOutput(
                layer_name="collaboration",
                status=ProcessingStatus.COMPLETED,
                data={
                    "perspective_generation": perspective_generation,
                    "cognitive_challenge": cognitive_challenge,
                    "collaboration_insights": collaboration_insights,
                    "enhanced_content": enhanced_content,
                },
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                perspective_generation=perspective_generation,
                cognitive_challenge=cognitive_challenge,
                collaboration_insights=collaboration_insights,
                enhanced_content=enhanced_content,
            )

            logger.info(f"Collaboration processing completed in {processing_time:.3f}s")
            return output

        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.error(f"Collaboration processing failed: {e}")
            processing_metadata["error"] = str(e)
            processing_metadata["steps"].append("error")

            # 返回错误状态的输出
            return CollaborationOutput(
                layer_name="collaboration",
                status=ProcessingStatus.ERROR,
                data={},
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                error_message=str(e),
                perspective_generation=PerspectiveGeneration(
                    perspectives=[], perspective_diversity=0.0, generation_metadata={}
                ),
                cognitive_challenge=CognitiveChallenge(
                    challenges=[], challenge_intensity=0.0, educational_value=0.0
                ),
                collaboration_insights={},
                enhanced_content=None,
            )

    async def generate_perspectives(
        self, query: str, context: dict[str, Any]
    ) -> PerspectiveGeneration:
        """生成多元观点 - 使用LLM分析"""
        try:
            logger.info("Generating multiple perspectives with LLM...")

            # 准备多视角分析上下文
            perspective_context = {
                "original_query": query,
                "user_background": str(context.get("user_profile", {}))[:500],
                "domain_context": str(context.get("context_profile", {}))[:500],
                "previous_analysis": str(context.get("behavior_output", {}))[:500],
            }

            # 使用LLM多视角管理器
            if self.perspective_manager:
                perspective_result = await self.perspective_manager.process(
                    query, context=perspective_context
                )
                
                # 转换为接口格式
                perspective_generation = PerspectiveGeneration(
                    perspectives=[{
                        "perspective": p.get("content", ""),
                        "viewpoint": p.get("viewpoint", ""),
                        "confidence": p.get("confidence", 0.7),
                        "rationale": p.get("rationale", "")
                    } for p in perspective_result.perspectives],
                    perspective_diversity=perspective_result.diversity_score,
                    generation_metadata={
                        "provider": "llm",
                        "perspective_count": len(perspective_result.perspectives),
                        "confidence": perspective_result.confidence
                    },
                )
            else:
                # 默认多视角生成
                perspective_generation = PerspectiveGeneration(
                    perspectives=[{
                        "perspective": "标准分析视角",
                        "viewpoint": "analytical",
                        "confidence": 0.5,
                        "rationale": "未启用LLM多视角生成"
                    }],
                    perspective_diversity=0.0,
                    generation_metadata={"error": "LLM多视角管理器未初始化"},
                )

            logger.info(f"Generated {len(perspective_generation.perspectives)} perspectives")
            return perspective_generation

        except Exception as e:
            logger.error(f"Failed to generate perspectives: {e}")
            return PerspectiveGeneration(
                perspectives=[],
                perspective_diversity=0.0,
                generation_metadata={"error": str(e)},
            )

    async def create_cognitive_challenges(
        self, content: str, user_profile
    ) -> CognitiveChallenge:
        """创建认知挑战 - 使用LLM分析"""
        try:
            logger.info("Creating cognitive challenges with LLM...")

            # 准备认知挑战生成上下文
            challenge_context = {
                "content_to_challenge": content,
                "user_cognitive_level": str(getattr(user_profile, 'cognitive_characteristics', {}))[:300],
                "learning_preferences": str(getattr(user_profile, 'interaction_preferences', {}))[:300],
            }

            # 使用LLM认知挑战管理器
            if self.challenge_manager:
                challenge_result = await self.challenge_manager.process(
                    content, context=challenge_context
                )
                
                # 转换为接口格式
                cognitive_challenge = CognitiveChallenge(
                    challenges=[{
                        "challenge": c.get("content", ""),
                        "type": c.get("challenge_type", "general"),
                        "difficulty": c.get("difficulty_level", 0.5),
                        "educational_rationale": c.get("educational_rationale", "")
                    } for c in challenge_result.challenges],
                    challenge_intensity=challenge_result.challenge_intensity,
                    educational_value=challenge_result.educational_value,
                )
            else:
                # 默认认知挑战
                cognitive_challenge = CognitiveChallenge(
                    challenges=[{
                        "challenge": "请深入思考这个问题的不同维度",
                        "type": "analytical",
                        "difficulty": 0.5,
                        "educational_rationale": "未启用LLM挑战生成"
                    }],
                    challenge_intensity=0.3,
                    educational_value=0.3,
                )

            logger.info(f"Created {len(cognitive_challenge.challenges)} cognitive challenges")
            return cognitive_challenge

        except Exception as e:
            logger.error(f"Failed to create cognitive challenges: {e}")
            return CognitiveChallenge(
                challenges=[], challenge_intensity=0.0, educational_value=0.0
            )

    async def orchestrate_collaboration(
        self, input_data: CollaborationInput
    ) -> CollaborationOutput:
        """编排协作过程"""
        try:
            logger.info("Orchestrating collaboration process...")

            if not self.collaborative_coordinator:
                return CollaborationOutput(
                    layer_name="collaboration",
                    status=ProcessingStatus.ERROR,
                    data={"error": "coordinator_not_available"},
                    error_message="coordinator_not_available",
                    collaboration_insights={"error": "coordinator_not_available"}
                )

            # 构建协作上下文
            from ..collaboration.interfaces import CollaborationContext

            collaboration_context = CollaborationContext(
                user_id=input_data.user_profile.user_id,
                session_id=input_data.collaboration_context.get(
                    "session_id", f"session_{input_data.user_profile.user_id}"
                ),
                interaction_history=[],
                user_cognitive_profile=None,
                collaboration_preferences=input_data.collaboration_context.get(
                    "collaboration_preferences", {}
                ),
                current_task_context=input_data.collaboration_context,
            )

            # 使用协作协调器编排过程
            orchestration_result = (
                await self.collaborative_coordinator.orchestrate_collaboration(
                    input_data.query, collaboration_context
                )
            )

            return CollaborationOutput(
                layer_name="collaboration",
                status=ProcessingStatus.COMPLETED,
                data=orchestration_result,
                collaboration_insights=(
                    orchestration_result if isinstance(orchestration_result, dict)
                    else {"result": orchestration_result}
                ),
                enhanced_content=str(orchestration_result)
            )

        except Exception as e:
            logger.error(f"Failed to orchestrate collaboration: {e}")
            return CollaborationOutput(
                layer_name="collaboration",
                status=ProcessingStatus.ERROR,
                data={"error": str(e)},
                error_message=str(e),
                collaboration_insights={"error": str(e)}
            )

    async def _generate_collaboration_insights(
        self,
        input_data: CollaborationInput,
        perspective_generation: PerspectiveGeneration,
        cognitive_challenge: CognitiveChallenge,
        orchestration_result: dict[str, Any],
    ) -> dict[str, Any]:
        """生成协作洞察"""
        try:
            insights = {
                "perspective_analysis": self._analyze_perspectives(
                    perspective_generation
                ),
                "challenge_assessment": self._assess_challenges(
                    cognitive_challenge, input_data.user_profile
                ),
                "collaboration_effectiveness": self._assess_collaboration_effectiveness(
                    perspective_generation, cognitive_challenge, orchestration_result
                ),
                "learning_opportunities": self._identify_learning_opportunities(
                    perspective_generation, cognitive_challenge, input_data.user_profile
                ),
                "cognitive_stretch": self._assess_cognitive_stretch(
                    cognitive_challenge, input_data.user_profile
                ),
                "interdisciplinary_connections": self._identify_interdisciplinary_connections(
                    perspective_generation, input_data.context_profile
                ),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate collaboration insights: {e}")
            return {
                "perspective_analysis": {},
                "challenge_assessment": {},
                "collaboration_effectiveness": 0.5,
                "learning_opportunities": [],
                "cognitive_stretch": 0.5,
                "interdisciplinary_connections": [],
            }

    def _analyze_perspectives(
        self, perspective_generation: PerspectiveGeneration
    ) -> dict[str, Any]:
        """分析观点生成结果"""
        perspectives = perspective_generation.perspectives

        if not perspectives:
            return {"count": 0, "diversity": 0.0, "quality": 0.0}

        # 分析观点类型分布
        perspective_types = {}
        total_confidence = 0.0

        for p in perspectives:
            viewpoint = p.get("viewpoint", "unknown")
            perspective_types[viewpoint] = perspective_types.get(viewpoint, 0) + 1
            total_confidence += p.get("confidence", 0.5)

        avg_confidence = total_confidence / len(perspectives)

        return {
            "count": len(perspectives),
            "diversity": perspective_generation.perspective_diversity,
            "quality": avg_confidence,
            "type_distribution": perspective_types,
            "avg_confidence": avg_confidence,
        }

    def _assess_challenges(
        self, cognitive_challenge: CognitiveChallenge, user_profile
    ) -> dict[str, Any]:
        """评估认知挑战"""
        challenges = cognitive_challenge.challenges

        if not challenges:
            return {"count": 0, "appropriateness": 0.0, "educational_value": 0.0}

        # 评估挑战适宜性
        user_cognitive_level = user_profile.cognitive_characteristics.get(
            "cognitive_complexity", 0.5
        )
        challenge_intensity = cognitive_challenge.challenge_intensity

        # 理想的挑战强度应该略高于用户认知水平
        appropriateness = 1.0 - abs(challenge_intensity - (user_cognitive_level + 0.1))
        appropriateness = max(0.0, min(1.0, appropriateness))

        return {
            "count": len(challenges),
            "appropriateness": appropriateness,
            "intensity": challenge_intensity,
            "educational_value": cognitive_challenge.educational_value,
            "user_cognitive_level": user_cognitive_level,
        }

    def _assess_collaboration_effectiveness(
        self,
        perspective_generation: PerspectiveGeneration,
        cognitive_challenge: CognitiveChallenge,
        orchestration_result: CollaborationOutput,
    ) -> float:
        """评估协作有效性"""
        factors = []

        # 观点生成质量
        perspective_quality = (
            perspective_generation.perspective_diversity
            * len(perspective_generation.perspectives)
            / 5.0
        )
        factors.append(min(1.0, perspective_quality))

        # 认知挑战质量
        challenge_quality = cognitive_challenge.educational_value
        factors.append(challenge_quality)

        # 编排结果质量
        if orchestration_result.status == ProcessingStatus.COMPLETED and not orchestration_result.error_message:
            orchestration_quality = 0.8
        else:
            orchestration_quality = 0.2
        factors.append(orchestration_quality)

        return sum(factors) / len(factors)

    def _identify_learning_opportunities(
        self,
        perspective_generation: PerspectiveGeneration,
        cognitive_challenge: CognitiveChallenge,
        user_profile,
    ) -> list[str]:
        """识别学习机会"""
        opportunities = []

        # 基于观点多样性识别学习机会
        if perspective_generation.perspective_diversity > 0.7:
            opportunities.append("探索不同观点的深层逻辑")
            opportunities.append("练习多角度思维")

        # 基于认知挑战识别学习机会
        if cognitive_challenge.challenge_intensity > 0.6:
            opportunities.append("挑战既有认知框架")
            opportunities.append("发展高阶思维技能")

        # 基于用户画像识别学习机会
        user_domains = user_profile.knowledge_profile.get("core_domains", [])
        if len(user_domains) > 1:
            opportunities.append("建立跨领域知识连接")

        return opportunities

    def _assess_cognitive_stretch(
        self, cognitive_challenge: CognitiveChallenge, user_profile
    ) -> float:
        """评估认知拉伸程度"""
        user_cognitive_level = user_profile.cognitive_characteristics.get(
            "cognitive_complexity", 0.5
        )
        challenge_intensity = cognitive_challenge.challenge_intensity

        # 认知拉伸 = 挑战强度 - 用户认知水平
        stretch = challenge_intensity - user_cognitive_level

        # 理想的拉伸程度在 0.1 到 0.3 之间
        if 0.1 <= stretch <= 0.3:
            return 1.0
        elif stretch < 0.1:
            return stretch / 0.1  # 拉伸不足
        else:
            return max(0.0, 1.0 - (stretch - 0.3) / 0.3)  # 拉伸过度

    def _identify_interdisciplinary_connections(
        self, perspective_generation: PerspectiveGeneration, context_profile
    ) -> list[str]:
        """识别跨学科连接"""
        connections = []

        primary_domain = context_profile.domain_characteristics.get(
            "primary_domain", ""
        )
        secondary_domains = context_profile.domain_characteristics.get(
            "secondary_domains", []
        )

        # 基于观点分析识别跨学科连接
        for perspective in perspective_generation.perspectives:
            viewpoint = perspective.get("viewpoint", "")
            if viewpoint and viewpoint != primary_domain:
                connection = f"{primary_domain} ↔ {viewpoint}"
                if connection not in connections:
                    connections.append(connection)

        # 基于次要领域识别连接
        for domain in secondary_domains:
            if domain != primary_domain:
                connection = f"{primary_domain} ↔ {domain}"
                if connection not in connections:
                    connections.append(connection)

        return connections

    def _should_enhance_content(
        self,
        perspective_generation: PerspectiveGeneration,
        cognitive_challenge: CognitiveChallenge,
    ) -> bool:
        """判断是否需要增强内容"""
        # 如果观点多样性高或认知挑战强度高，则增强内容
        return (
            perspective_generation.perspective_diversity > 0.6
            or cognitive_challenge.challenge_intensity > 0.6
        )

    async def _enhance_content_with_collaboration(
        self,
        original_content: str,
        perspective_generation: PerspectiveGeneration,
        cognitive_challenge: CognitiveChallenge,
    ) -> str:
        """用协作结果增强内容"""
        try:
            enhanced_parts = [original_content]

            # 添加多元观点
            if perspective_generation.perspectives:
                enhanced_parts.append("\n\n## 多元观点")
                for i, perspective in enumerate(
                    perspective_generation.perspectives[:3], 1
                ):
                    enhanced_parts.append(
                        f"{i}. {perspective.get('perspective', '未知观点')}"
                    )

            # 添加认知挑战
            if cognitive_challenge.challenges:
                enhanced_parts.append("\n\n## 思考挑战")
                for i, challenge in enumerate(cognitive_challenge.challenges[:2], 1):
                    enhanced_parts.append(
                        f"{i}. {challenge.get('challenge', '未知挑战')}"
                    )

            return "\n".join(enhanced_parts)

        except Exception as e:
            logger.error(f"Failed to enhance content with collaboration: {e}")
            return original_content

    async def cleanup(self) -> None:
        """清理协作层资源"""
        try:
            logger.info("Cleaning up Collaboration Layer resources...")

            # 清理协作历史（保留最近100条）
            if len(self.collaboration_history) > 100:
                self.collaboration_history = self.collaboration_history[-100:]

            # 清理各个组件
            if self.collaborative_coordinator:
                # 如果有需要清理的资源
                pass

            if self.perspective_generator:
                # 如果有需要清理的资源
                pass

            if self.challenge_generator:
                # 如果有需要清理的资源
                pass

            self.is_initialized = False
            logger.info("Collaboration Layer cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup Collaboration Layer: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取协作层状态"""
        return {
            "layer_name": "collaboration",
            "initialized": self.is_initialized,
            "processing_count": self.processing_count,
            "last_processing_time": self.last_processing_time,
            "collaboration_history_count": len(self.collaboration_history),
            "components": {
                "collaborative_coordinator": self.collaborative_coordinator is not None,
                "perspective_generator": self.perspective_generator is not None,
                "challenge_generator": self.challenge_generator is not None,
            },
            "dependencies": {
                "llm_provider": self.llm_provider is not None,
                "memory_system": self.memory_system is not None,
            },
        }
