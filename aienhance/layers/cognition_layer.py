"""
认知层实现
处理记忆激活、语义增强、类比推理等认知功能
"""

import logging
from datetime import datetime
from typing import Any

from ..modules.memory_activation import (
    MemoryActivationManager,
    SemanticEnhancementManager,
    MemoryActivationConfig,
    LLMMemoryActivationProvider,
    LLMSemanticEnhancementProvider,
)
from ..memory.interfaces import MemoryEntry
from .layer_interfaces import (
    AnalogyReasoning,
    CognitionInput,
    CognitionOutput,
    ICognitionLayer,
    MemoryActivation,
    ProcessingStatus,
    SemanticEnhancement,
)

logger = logging.getLogger(__name__)


class CognitionLayer(ICognitionLayer):
    """认知层具体实现"""

    def __init__(
        self, config: dict[str, Any] | None = None, llm_provider: Any | None = None
    ):
        """
        初始化认知层

        Args:
            config: 认知层配置
        """
        self.config = config or {}
        self.llm_provider = llm_provider
        self.is_initialized = False

        # 核心组件
        self.memory_activator: MemoryActivationManager | None = None
        self.semantic_enhancer: SemanticEnhancementManager | None = None
        self.llm_provider: Any | None = None

        # 运行时状态
        self.processing_count = 0
        self.last_processing_time = 0.0
        self.activation_cache = {}  # 激活结果缓存

    async def initialize(self) -> bool:
        """初始化认知层组件"""
        try:
            logger.info("Initializing Cognition Layer...")

            # 初始化记忆激活器
            self.memory_activator = MemoryActivationManager()

            if self.llm_provider:
                logger.info(
                    f"Registering memory activation provider with LLM: {type(self.llm_provider).__name__}"
                )
                # 记忆激活提供商
                activation_config = MemoryActivationConfig(
                    llm_provider=self.llm_provider,
                    activation_type="memory_activation",
                    temperature=0.4,
                )
                activation_provider = LLMMemoryActivationProvider(activation_config)
                registration_success = await self.memory_activator.register_provider(
                    "default", activation_provider
                )

                if not registration_success:
                    logger.error("Failed to register memory activation provider")
                    # 不要失败整个初始化，继续其他组件
                else:
                    logger.info("Memory activation provider registered successfully")
            else:
                logger.warning(
                    "No LLM provider configured, skipping memory activation provider registration"
                )

            logger.info("Memory activator initialized")

            # 初始化语义增强器
            self.semantic_enhancer = SemanticEnhancementManager()

            if self.llm_provider:
                logger.info(
                    f"Registering semantic enhancement provider with LLM: {type(self.llm_provider).__name__}"
                )
                # 语义增强提供商
                enhancement_config = MemoryActivationConfig(
                    llm_provider=self.llm_provider,
                    activation_type="semantic_enhancement",
                    temperature=0.4,
                )
                enhancement_provider = LLMSemanticEnhancementProvider(
                    enhancement_config
                )
                registration_success = await self.semantic_enhancer.register_provider(
                    "default", enhancement_provider
                )

                if not registration_success:
                    logger.error("Failed to register semantic enhancement provider")
                    # 不要失败整个初始化，继续其他组件
                else:
                    logger.info("Semantic enhancement provider registered successfully")
            else:
                logger.warning(
                    "No LLM provider configured, skipping semantic enhancement provider registration"
                )

            logger.info("Semantic enhancer initialized")

            self.is_initialized = True
            logger.info("Cognition Layer initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Cognition Layer: {e}")
            self.is_initialized = False
            return False

    async def process(self, input_data: CognitionInput) -> CognitionOutput:
        """
        处理认知层输入，进行记忆激活、语义增强和类比推理

        Args:
            input_data: 认知层输入数据

        Returns:
            CognitionOutput: 认知层处理结果
        """
        if not self.is_initialized:
            raise RuntimeError("Cognition Layer not initialized")

        start_time = datetime.now()
        processing_metadata = {
            "input_query": input_data.query,
            "user_id": input_data.user_profile.user_id,
            "processing_id": f"cognition_{self.processing_count}",
            "steps": [],
            "external_memories_count": len(input_data.external_memories),
        }

        try:
            logger.info(
                f"Processing cognition input for query: {input_data.query[:50]}..."
            )
            processing_metadata["steps"].append("started")

            # 1. 记忆激活
            memory_activation = await self.activate_memories(
                input_data.query,
                {
                    "user_profile": input_data.user_profile,
                    "context_profile": input_data.context_profile,
                    "external_memories": input_data.external_memories,
                    "perception_insights": input_data.perception_insights,
                },
            )
            processing_metadata["steps"].append("memory_activation_completed")

            # 2. 语义增强
            # 合并内部激活的片段和外部记忆
            all_fragments = list(memory_activation.activated_fragments)

            # 转换外部记忆为片段格式
            for memory in input_data.external_memories:
                fragment = self._convert_memory_to_fragment(memory)
                if fragment:
                    all_fragments.append(fragment)

            semantic_enhancement = await self.enhance_semantics(
                all_fragments,
                {
                    "user_profile": input_data.user_profile,
                    "context_profile": input_data.context_profile,
                    "perception_insights": input_data.perception_insights,
                },
            )
            processing_metadata["steps"].append("semantic_enhancement_completed")

            # 3. 类比推理
            analogy_reasoning = await self.reason_analogies(
                input_data.query,
                {
                    "user_profile": input_data.user_profile,
                    "context_profile": input_data.context_profile,
                    "memory_activation": memory_activation,
                    "semantic_enhancement": semantic_enhancement,
                    "perception_insights": input_data.perception_insights,
                },
            )
            processing_metadata["steps"].append("analogy_reasoning_completed")

            # 4. 生成认知洞察
            cognitive_insights = await self._generate_cognitive_insights(
                input_data, memory_activation, semantic_enhancement, analogy_reasoning
            )
            processing_metadata["steps"].append("cognitive_insights_generated")

            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.last_processing_time = processing_time
            self.processing_count += 1

            # 构建输出
            output = CognitionOutput(
                layer_name="cognition",
                status=ProcessingStatus.COMPLETED,
                data={
                    "memory_activation": memory_activation,
                    "semantic_enhancement": semantic_enhancement,
                    "analogy_reasoning": analogy_reasoning,
                    "cognitive_insights": cognitive_insights,
                },
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                memory_activation=memory_activation,
                semantic_enhancement=semantic_enhancement,
                analogy_reasoning=analogy_reasoning,
                cognitive_insights=cognitive_insights,
            )

            logger.info(f"Cognition processing completed in {processing_time:.3f}s")
            return output

        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            logger.error(f"Cognition processing failed: {e}")
            processing_metadata["error"] = str(e)
            processing_metadata["steps"].append("error")

            # 返回错误状态的输出
            return CognitionOutput(
                layer_name="cognition",
                status=ProcessingStatus.ERROR,
                data={},
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                error_message=str(e),
                memory_activation=MemoryActivation(
                    activated_fragments=[],
                    activation_confidence=0.0,
                    activation_metadata={},
                ),
                semantic_enhancement=SemanticEnhancement(
                    enhanced_content=[],
                    semantic_gaps_filled=[],
                    enhancement_confidence=0.0,
                ),
                analogy_reasoning=AnalogyReasoning(
                    analogies=[], reasoning_chains=[], confidence_scores=[]
                ),
                cognitive_insights={},
            )

    async def activate_memories(
        self, query: str, context: dict[str, Any]
    ) -> MemoryActivation:
        """激活相关记忆 - 使用LLM语义分析"""
        try:
            logger.info("Activating memories with LLM...")

            # 准备记忆激活上下文
            activation_context = {
                "available_memory": "",
                "context_info": f"用户查询: {query}",
                "memory_fragments": context.get("external_memories", []),
            }

            # 从外部记忆构建可用记忆文本
            if context.get("external_memories"):
                memory_texts = []
                for memory in context["external_memories"][:10]:  # 限制数量
                    if hasattr(memory, "content"):
                        memory_texts.append(f"[记忆] {memory.content}")
                    else:
                        memory_texts.append(f"[记忆] {str(memory)}")
                activation_context["available_memory"] = "\n".join(memory_texts)

            # 使用LLM记忆激活器
            if (
                self.memory_activator
                and len(self.memory_activator.get_available_providers()) > 0
            ):
                activation_result = await self.memory_activator.process(
                    query, context=activation_context
                )

                # 转换为接口格式
                memory_activation = MemoryActivation(
                    activated_fragments=activation_result.fragments,
                    activation_confidence=activation_result.confidence,
                    activation_metadata={
                        "activation_level": activation_result.activation_level.value,
                        "total_score": activation_result.total_score,
                        "activation_path": activation_result.activation_path,
                        "semantic_clusters": activation_result.semantic_clusters,
                        "provider": "llm",
                    },
                )
            else:
                # 默认激活结果
                memory_activation = MemoryActivation(
                    activated_fragments=[],
                    activation_confidence=0.3,
                    activation_metadata={"error": "未启用LLM记忆激活"},
                )

            logger.info(
                f"Memory activation completed: {len(memory_activation.activated_fragments)} fragments activated"
            )
            return memory_activation

        except Exception as e:
            logger.error(f"Failed to activate memories: {e}")
            return MemoryActivation(
                activated_fragments=[],
                activation_confidence=0.0,
                activation_metadata={"error": str(e)},
            )

    async def enhance_semantics(
        self, fragments: list[Any], context: dict[str, Any]
    ) -> SemanticEnhancement:
        """语义增强 - 使用LLM语义分析"""
        try:
            logger.info(f"Enhancing semantics for {len(fragments)} fragments...")

            if not fragments:
                return SemanticEnhancement(
                    enhanced_content=[],
                    semantic_gaps_filled=[],
                    enhancement_confidence=0.0,
                )

            # 准备语义增强上下文
            enhancement_context = {
                "original_content": "",
                "memory_context": "",
                "domain_knowledge": context.get("context_profile", {})
                .get("domain_characteristics", {})
                .get("primary_domain", "general"),
            }

            # 构建原始内容文本
            content_texts = []
            for fragment in fragments[:5]:  # 限制数量
                if hasattr(fragment, "content"):
                    content_texts.append(fragment.content)
                else:
                    content_texts.append(str(fragment))
            enhancement_context["original_content"] = "\n".join(content_texts)

            # 使用LLM语义增强器
            if (
                self.semantic_enhancer
                and len(self.semantic_enhancer.get_available_providers()) > 0
            ):
                enhancement_result = await self.semantic_enhancer.process(
                    enhancement_context["original_content"], context=enhancement_context
                )

                # 转换为接口格式
                semantic_enhancement = SemanticEnhancement(
                    enhanced_content=[enhancement_result.enhanced_content],
                    semantic_gaps_filled=[
                        link.get("description", "语义关联")
                        for link in enhancement_result.semantic_links[:3]
                    ],
                    enhancement_confidence=enhancement_result.confidence,
                )
            else:
                # 默认语义增强
                semantic_enhancement = SemanticEnhancement(
                    enhanced_content=[str(f) for f in fragments],
                    semantic_gaps_filled=[],
                    enhancement_confidence=0.3,
                )

            logger.info(
                f"Semantic enhancement completed: {len(semantic_enhancement.enhanced_content)} enhanced items"
            )
            return semantic_enhancement

        except Exception as e:
            logger.error(f"Failed to enhance semantics: {e}")
            return SemanticEnhancement(
                enhanced_content=[str(f) for f in fragments],  # 回退到原始片段
                semantic_gaps_filled=[],
                enhancement_confidence=0.0,
            )

    async def reason_analogies(
        self, query: str, context: dict[str, Any]
    ) -> AnalogyReasoning:
        """类比推理 - 简化实现"""
        try:
            logger.info("Performing simplified analogy reasoning...")

            # 简化的类比推理实现
            # TODO: 可以在未来添加专门的类比推理模块
            reasoning_result = {
                "analogies": [],
                "reasoning_chains": [],
                "confidence_scores": [],
            }

            # 提取类比结果
            analogies = []
            reasoning_chains = []
            confidence_scores = []

            if isinstance(reasoning_result, dict):
                # 处理字典格式的结果
                analogies = reasoning_result.get("analogies", [])
                reasoning_chains = reasoning_result.get("reasoning_chains", [])
                confidence_scores = reasoning_result.get("confidence_scores", [])
            elif hasattr(reasoning_result, "analogies"):
                # 处理对象格式的结果
                analogies = getattr(reasoning_result, "analogies", [])
                reasoning_chains = getattr(reasoning_result, "reasoning_chains", [])
                confidence_scores = getattr(reasoning_result, "confidence_scores", [])
            else:
                # 处理其他格式
                analogies = [{"analogy": str(reasoning_result), "confidence": 0.5}]
                reasoning_chains = [["query", "reasoning", "conclusion"]]
                confidence_scores = [0.5]

            analogy_reasoning = AnalogyReasoning(
                analogies=analogies,
                reasoning_chains=reasoning_chains,
                confidence_scores=confidence_scores,
            )

            logger.info(
                f"Analogy reasoning completed: {len(analogies)} analogies generated"
            )
            return analogy_reasoning

        except Exception as e:
            logger.error(f"Failed to perform analogy reasoning: {e}")
            return AnalogyReasoning(
                analogies=[], reasoning_chains=[], confidence_scores=[]
            )

    async def _generate_cognitive_insights(
        self,
        input_data: CognitionInput,
        memory_activation: MemoryActivation,
        semantic_enhancement: SemanticEnhancement,
        analogy_reasoning: AnalogyReasoning,
    ) -> dict[str, Any]:
        """生成认知洞察"""
        try:
            insights = {
                "cognitive_load": self._assess_cognitive_load(
                    input_data, memory_activation, semantic_enhancement
                ),
                "knowledge_gaps": self._identify_knowledge_gaps(
                    input_data, semantic_enhancement
                ),
                "reasoning_complexity": self._assess_reasoning_complexity(
                    analogy_reasoning
                ),
                "memory_utilization": self._assess_memory_utilization(
                    memory_activation, input_data.external_memories
                ),
                "semantic_coherence": self._assess_semantic_coherence(
                    semantic_enhancement
                ),
                "creative_potential": self._assess_creative_potential(
                    analogy_reasoning, input_data.user_profile
                ),
            }

            return insights

        except Exception as e:
            logger.error(f"Failed to generate cognitive insights: {e}")
            return {
                "cognitive_load": 0.5,
                "knowledge_gaps": [],
                "reasoning_complexity": 0.5,
                "memory_utilization": 0.5,
                "semantic_coherence": 0.5,
                "creative_potential": 0.5,
            }

    def _assess_cognitive_load(
        self,
        input_data: CognitionInput,
        memory_activation: MemoryActivation,
        semantic_enhancement: SemanticEnhancement,
    ) -> float:
        """评估认知负荷"""
        # 基于多个因素评估认知负荷
        factors = []

        # 任务复杂度
        task_complexity = input_data.context_profile.complexity_level
        # 处理可能的字符串类型
        if isinstance(task_complexity, str):
            complexity_map = {"low": 0.3, "medium": 0.5, "high": 0.8}
            task_complexity = complexity_map.get(task_complexity.lower(), 0.5)
        elif not isinstance(task_complexity, (int, float)):
            task_complexity = 0.5
        factors.append(task_complexity)

        # 记忆激活量
        memory_load = min(1.0, len(memory_activation.activated_fragments) / 20.0)
        factors.append(memory_load)

        # 语义增强复杂度
        semantic_load = min(1.0, len(semantic_enhancement.semantic_gaps_filled) / 10.0)
        factors.append(semantic_load)

        # 用户认知能力
        user_cognitive_capacity = input_data.user_profile.cognitive_characteristics.get(
            "cognitive_complexity", 0.5
        )

        # 计算加权平均认知负荷
        raw_load = sum(factors) / len(factors)
        adjusted_load = raw_load / max(0.1, user_cognitive_capacity)

        return min(1.0, adjusted_load)

    def _identify_knowledge_gaps(
        self, input_data: CognitionInput, semantic_enhancement: SemanticEnhancement
    ) -> list[str]:
        """识别知识缺口"""
        gaps = []

        # 从语义增强结果中提取缺口
        gaps.extend(semantic_enhancement.semantic_gaps_filled)

        # 基于用户画像识别潜在缺口
        user_domains = input_data.user_profile.knowledge_profile.get("core_domains", [])
        task_domain = input_data.context_profile.domain_characteristics.get(
            "primary_domain", ""
        )

        if task_domain not in user_domains and task_domain != "general":
            gaps.append(f"领域知识缺口: {task_domain}")

        return gaps

    def _assess_reasoning_complexity(
        self, analogy_reasoning: AnalogyReasoning
    ) -> float:
        """评估推理复杂度"""
        if not analogy_reasoning.reasoning_chains:
            return 0.0

        # 基于推理链长度和置信度评估复杂度
        avg_chain_length = sum(
            len(chain) for chain in analogy_reasoning.reasoning_chains
        ) / len(analogy_reasoning.reasoning_chains)

        avg_confidence = sum(analogy_reasoning.confidence_scores) / max(
            1, len(analogy_reasoning.confidence_scores)
        )

        # 复杂度与推理链长度正相关，与置信度负相关
        complexity = (avg_chain_length / 10.0) * (1.0 - avg_confidence)
        return min(1.0, complexity)

    def _assess_memory_utilization(
        self, memory_activation: MemoryActivation, external_memories: list[Any]
    ) -> float:
        """评估记忆利用率"""
        internal_count = len(memory_activation.activated_fragments)
        external_count = len(external_memories)
        total_count = internal_count + external_count

        if total_count == 0:
            return 0.0

        # 结合激活数量和置信度
        utilization = (total_count / 50.0) * memory_activation.activation_confidence
        return min(1.0, utilization)

    def _assess_semantic_coherence(
        self, semantic_enhancement: SemanticEnhancement
    ) -> float:
        """评估语义连贯性"""
        return semantic_enhancement.enhancement_confidence

    def _assess_creative_potential(
        self, analogy_reasoning: AnalogyReasoning, user_profile
    ) -> float:
        """评估创造潜力"""
        # 基于类比数量和用户创造倾向
        analogy_count = len(analogy_reasoning.analogies)
        user_creativity = user_profile.cognitive_characteristics.get(
            "creativity_tendency", 0.5
        )

        # 类比的多样性和质量
        avg_confidence = sum(analogy_reasoning.confidence_scores) / max(
            1, len(analogy_reasoning.confidence_scores)
        )

        creative_potential = (analogy_count / 10.0) * user_creativity * avg_confidence
        return min(1.0, creative_potential)

    def _convert_memory_to_fragment(self, memory: Any):
        """将外部记忆转换为内部记忆片段格式"""
        try:
            if isinstance(memory, MemoryEntry):
                # 创建简化的记忆片段
                fragment = type(
                    "MemoryFragment",
                    (),
                    {
                        "content": memory.content,
                        "confidence": memory.confidence,
                        "source": "external_memory",
                        "memory_type": memory.memory_type.value
                        if hasattr(memory.memory_type, "value")
                        else str(memory.memory_type),
                        "timestamp": memory.timestamp,
                        "metadata": memory.metadata or {},
                        "activation_method": "external_import",
                    },
                )()

                return fragment
            else:
                # 处理其他格式的记忆对象
                return type(
                    "MemoryFragment",
                    (),
                    {
                        "content": str(memory),
                        "confidence": 0.5,
                        "source": "external_memory",
                        "memory_type": "unknown",
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {},
                        "activation_method": "external_import",
                    },
                )()

        except Exception as e:
            logger.warning(f"Failed to convert memory to fragment: {e}")
            return None

    async def cleanup(self) -> None:
        """清理认知层资源"""
        try:
            logger.info("Cleaning up Cognition Layer resources...")

            # 清理缓存
            self.activation_cache.clear()

            # 清理组件
            if self.memory_activator:
                # 如果有需要清理的资源
                pass

            if self.semantic_enhancer:
                # 如果有需要清理的资源
                pass

            if self.analogy_reasoner:
                # 如果有需要清理的资源
                pass

            self.is_initialized = False
            logger.info("Cognition Layer cleanup completed")

        except Exception as e:
            logger.error(f"Failed to cleanup Cognition Layer: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取认知层状态"""
        return {
            "layer_name": "cognition",
            "initialized": self.is_initialized,
            "processing_count": self.processing_count,
            "last_processing_time": self.last_processing_time,
            "cache_size": len(self.activation_cache),
            "components": {
                "memory_activator": self.memory_activator is not None,
                "semantic_enhancer": self.semantic_enhancer is not None,
                "analogy_reasoner": self.analogy_reasoner is not None,
            },
        }
