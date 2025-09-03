"""
情境分析模块主类

基于设计文档第4.2节，识别用户当前所处的任务场景和问题意图，为认知层的记忆激活提供方向性指导。
该模块通过三个子模块协同工作：任务类型识别、认知需求预测、情境要素提取。
"""

import datetime
import logging
from typing import Any

from aienhance.core.base_architecture import (
    BaseModule,
    ProcessingContext,
    ProcessingResult,
)

from .cognitive_needs_prediction import CognitiveNeedsPredictionSubModule
from .context_elements_extraction import ContextElementsExtractionSubModule
from .task_type_identification import TaskTypeIdentificationSubModule

logger = logging.getLogger(__name__)


class ContextAnalysisModule(BaseModule):
    """情境分析模块"""

    def __init__(
        self, llm_adapter=None, memory_adapter=None, config: dict[str, Any] = None
    ):
        # 创建子模块
        submodules = [
            TaskTypeIdentificationSubModule(llm_adapter, config),
            CognitiveNeedsPredictionSubModule(llm_adapter, config),
            ContextElementsExtractionSubModule(llm_adapter, config),
        ]

        super().__init__("context_analysis", submodules, config)
        self.memory_adapter = memory_adapter

    async def _initialize_impl(self):
        """模块初始化实现"""
        logger.info("Initializing Context Analysis Module")

    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理情境分析"""
        try:
            # 顺序处理子模块，因为后续子模块需要前面的结果
            submodule_results = await self._process_submodules_sequentially(context)

            # 整合各个子模块的分析结果
            integrated_analysis = await self._integrate_context_analysis(
                submodule_results, context
            )

            # 更新情境分析到记忆系统（可选）
            if self.memory_adapter:
                await self._update_context_analysis_in_memory(
                    integrated_analysis, context.user_id
                )

            return ProcessingResult(
                success=True,
                data={
                    "context_analysis": integrated_analysis,
                    "submodule_results": {
                        name: result.data
                        for name, result in submodule_results.items()
                        if result.success
                    },
                    "analysis_completeness": self._calculate_analysis_completeness(
                        integrated_analysis
                    ),
                    "confidence_score": integrated_analysis.get(
                        "overall_confidence", 0.7
                    ),
                },
                metadata={
                    "module": "context_analysis",
                    "successful_submodules": [
                        name
                        for name, result in submodule_results.items()
                        if result.success
                    ],
                    "primary_task_type": integrated_analysis.get(
                        "task_analysis", {}
                    ).get("primary_task_type"),
                    "context_complexity": integrated_analysis.get(
                        "context_elements", {}
                    )
                    .get("complexity_assessment", {})
                    .get("overall_complexity", "medium"),
                },
            )

        except Exception as e:
            logger.error(f"Context analysis module processing failed: {e}")
            return ProcessingResult(
                success=False, data={}, metadata={"error": str(e)}, error_message=str(e)
            )

    async def _process_submodules_sequentially(
        self, context: ProcessingContext
    ) -> dict[str, ProcessingResult]:
        """顺序处理子模块，因为存在依赖关系"""
        results = {}

        # 1. 先处理任务类型识别
        task_identification_submodule = self.get_submodule("task_type_identification")
        if task_identification_submodule and task_identification_submodule.is_enabled():
            try:
                result = await task_identification_submodule.process(context)
                results["task_type_identification"] = result
                # 将结果更新到上下文，供后续子模块使用
                if result.success:
                    context.submodule_outputs[
                        "context_analysis.task_type_identification"
                    ] = result.data
            except Exception as e:
                logger.error(f"Task type identification failed: {e}")
                results["task_type_identification"] = ProcessingResult(
                    success=False,
                    data={},
                    metadata={"error": str(e)},
                    error_message=str(e),
                )

        # 2. 处理情境要素提取（可以并行，但放在认知需求预测之前）
        context_extraction_submodule = self.get_submodule("context_elements_extraction")
        if context_extraction_submodule and context_extraction_submodule.is_enabled():
            try:
                result = await context_extraction_submodule.process(context)
                results["context_elements_extraction"] = result
                if result.success:
                    context.submodule_outputs[
                        "context_analysis.context_elements_extraction"
                    ] = result.data
            except Exception as e:
                logger.error(f"Context elements extraction failed: {e}")
                results["context_elements_extraction"] = ProcessingResult(
                    success=False,
                    data={},
                    metadata={"error": str(e)},
                    error_message=str(e),
                )

        # 3. 最后处理认知需求预测（依赖前面的结果）
        cognitive_needs_submodule = self.get_submodule("cognitive_needs_prediction")
        if cognitive_needs_submodule and cognitive_needs_submodule.is_enabled():
            try:
                result = await cognitive_needs_submodule.process(context)
                results["cognitive_needs_prediction"] = result
                if result.success:
                    context.submodule_outputs[
                        "context_analysis.cognitive_needs_prediction"
                    ] = result.data
            except Exception as e:
                logger.error(f"Cognitive needs prediction failed: {e}")
                results["cognitive_needs_prediction"] = ProcessingResult(
                    success=False,
                    data={},
                    metadata={"error": str(e)},
                    error_message=str(e),
                )

        return results

    async def _integrate_context_analysis(
        self, submodule_results: dict[str, ProcessingResult], context: ProcessingContext
    ) -> dict[str, Any]:
        """整合各个子模块的情境分析结果"""
        integrated_analysis = {
            "user_id": context.user_id,
            "analysis_timestamp": context.metadata.get("created_at"),
            "task_analysis": {},
            "context_elements": {},
            "cognitive_needs": {},
            "overall_confidence": 0.0,
            "integration_notes": [],
        }

        # 提取任务类型识别结果
        task_result = submodule_results.get("task_type_identification")
        if task_result and task_result.success:
            integrated_analysis["task_analysis"] = task_result.data.get(
                "task_analysis", {}
            )
            integrated_analysis["integration_notes"].append("任务类型识别成功")

        # 提取情境要素提取结果
        context_result = submodule_results.get("context_elements_extraction")
        if context_result and context_result.success:
            integrated_analysis["context_elements"] = context_result.data.get(
                "context_elements", {}
            )
            integrated_analysis["integration_notes"].append("情境要素提取成功")

        # 提取认知需求预测结果
        cognitive_result = submodule_results.get("cognitive_needs_prediction")
        if cognitive_result and cognitive_result.success:
            integrated_analysis["cognitive_needs"] = cognitive_result.data.get(
                "cognitive_needs", {}
            )
            integrated_analysis["integration_notes"].append("认知需求预测成功")

        # 计算整体置信度
        confidence_scores = []
        for result in submodule_results.values():
            if result.success and "confidence_score" in result.data:
                confidence_scores.append(result.data["confidence_score"])

        if confidence_scores:
            integrated_analysis["overall_confidence"] = sum(confidence_scores) / len(
                confidence_scores
            )

        # 生成综合情境分析摘要
        integrated_analysis["analysis_summary"] = await self._generate_analysis_summary(
            integrated_analysis, context
        )

        return integrated_analysis

    async def _generate_analysis_summary(
        self, analysis: dict[str, Any], context: ProcessingContext
    ) -> dict[str, Any]:
        """生成综合情境分析摘要"""
        return {
            "summary_text": "情境分析完成",
            "key_insights": [
                f"任务类型: {analysis.get('task_analysis', {}).get('primary_task_type', '未识别')}",
                f"复杂度: {analysis.get('context_elements', {}).get('complexity_assessment', {}).get('overall_complexity', '中等')}",
                f"认知策略: {analysis.get('cognitive_needs', {}).get('primary_cognitive_strategy', '分析推理')}",
            ],
            "processing_recommendations": [
                "基于任务类型选择适当的认知策略",
                "根据情境复杂度调整处理深度",
                "结合用户特征提供个性化支持",
            ],
        }

    async def _update_context_analysis_in_memory(
        self, analysis: dict[str, Any], user_id: str
    ):
        """更新情境分析到记忆系统"""
        if not self.memory_adapter:
            return

        try:
            import json

            from aienhance.memory.interfaces import MemoryEntry, MemoryType, UserContext

            user_context = UserContext(user_id=user_id)

            # 序列化analysis，处理datetime对象
            def json_serializer(obj):
                if hasattr(obj, "isoformat"):
                    return obj.isoformat()
                raise TypeError(
                    f"Object of type {type(obj).__name__} is not JSON serializable"
                )

            context_memory = MemoryEntry(
                content=f"Context Analysis: {json.dumps(analysis, ensure_ascii=False, default=json_serializer)}",
                memory_type=MemoryType.SEMANTIC,
                user_context=user_context,
                timestamp=datetime.datetime.now(),
                metadata={"type": "context_analysis", "analysis_version": "1.0"},
            )

            await self.memory_adapter.add_memory(context_memory)
            logger.info(f"Updated context analysis for {user_id} in memory system")
        except Exception as e:
            logger.warning(f"Failed to update context analysis in memory: {e}")

    def _calculate_analysis_completeness(self, analysis: dict[str, Any]) -> float:
        """计算情境分析完整度"""
        completeness_factors = [
            1.0 if analysis.get("task_analysis") else 0.0,
            1.0 if analysis.get("context_elements") else 0.0,
            1.0 if analysis.get("cognitive_needs") else 0.0,
        ]

        return sum(completeness_factors) / len(completeness_factors)
