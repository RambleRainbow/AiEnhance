"""
感知层主类

基于设计文档第四章，感知层作为整个系统的前端，负责理解当前用户的情境和状态，
为后续记忆激活提供精准线索。该层的设计充分考虑了人类认知的私有性特征，
力图通过多维度建模来捕捉用户独特的认知背景和当前需求。
"""

from typing import Dict, Any
import logging
from aienhance.core.base_architecture import BaseLayer, ProcessingContext, ProcessingResult
from .user_modeling.user_modeling_module import UserModelingModule
from .context_analysis.context_analysis_module import ContextAnalysisModule

logger = logging.getLogger(__name__)


class PerceptionLayer(BaseLayer):
    """感知层"""
    
    def __init__(self, llm_adapter=None, memory_adapter=None, config: Dict[str, Any] = None):
        # 创建模块
        modules = [
            UserModelingModule(llm_adapter, memory_adapter, config),
            ContextAnalysisModule(llm_adapter, config)
        ]
        
        super().__init__("perception", modules, config)
        self.llm_adapter = llm_adapter
        self.memory_adapter = memory_adapter
        
    async def _initialize_impl(self):
        """层初始化实现"""
        logger.info("Initializing Perception Layer")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理感知层逻辑"""
        try:
            # 并行处理两个模块
            module_results = await self.process_modules(context)
            
            # 整合感知层输出
            integrated_perception = await self._integrate_perception_output(
                module_results, context
            )
            
            return ProcessingResult(
                success=True,
                data={
                    "perception_output": integrated_perception,
                    "user_cognitive_profile": integrated_perception.get("user_profile", {}),
                    "situation_analysis": integrated_perception.get("context_analysis", {}),
                    "cognitive_support_recommendations": integrated_perception.get("support_recommendations", [])
                },
                metadata={
                    "layer": "perception",
                    "successful_modules": [name for name, result in module_results.items() if result.success],
                    "perception_confidence": integrated_perception.get("overall_confidence", 0.5)
                }
            )
            
        except Exception as e:
            logger.error(f"Perception layer processing failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _integrate_perception_output(self, module_results: Dict[str, ProcessingResult], 
                                          context: ProcessingContext) -> Dict[str, Any]:
        """整合感知层的集成输出"""
        
        integrated_output = {
            "user_profile": {},
            "context_analysis": {},
            "support_recommendations": [],
            "perception_summary": {},
            "overall_confidence": 0.0
        }
        
        # 整合用户建模结果
        user_modeling_result = module_results.get("user_modeling")
        if user_modeling_result and user_modeling_result.success:
            integrated_output["user_profile"] = user_modeling_result.data.get("user_profile", {})
            integrated_output["perception_summary"]["user_modeling_status"] = "成功"
        
        # 整合情境分析结果  
        context_analysis_result = module_results.get("context_analysis")
        if context_analysis_result and context_analysis_result.success:
            integrated_output["context_analysis"] = context_analysis_result.data.get("context_analysis", {})
            integrated_output["perception_summary"]["context_analysis_status"] = "成功"
        
        # 生成认知支持建议
        integrated_output["support_recommendations"] = await self._generate_cognitive_support_recommendations(
            integrated_output["user_profile"],
            integrated_output["context_analysis"],
            context
        )
        
        # 计算整体置信度
        confidence_scores = []
        for result in module_results.values():
            if result.success and hasattr(result.data, 'get') and result.data.get("confidence_score"):
                confidence_scores.append(result.data["confidence_score"])
        
        if confidence_scores:
            integrated_output["overall_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        return integrated_output
    
    async def _generate_cognitive_support_recommendations(self, 
                                                         user_profile: Dict[str, Any],
                                                         context_analysis: Dict[str, Any],
                                                         context: ProcessingContext) -> list:
        """基于用户画像和情境分析生成认知支持建议"""
        
        recommendations = []
        
        # 基于用户认知能力的建议
        cognitive_abilities = user_profile.get("cognitive_abilities", {})
        if cognitive_abilities:
            thinking_style = cognitive_abilities.get("thinking_style", {})
            if thinking_style.get("abstract_vs_concrete", {}).get("score", 0.5) > 0.7:
                recommendations.append("用户偏好抽象思维，可以提供更多概念性和理论性内容")
            elif thinking_style.get("abstract_vs_concrete", {}).get("score", 0.5) < 0.3:
                recommendations.append("用户偏好具体思维，应提供更多实例和具体案例")
        
        # 基于任务类型的建议
        task_analysis = context_analysis.get("task_analysis", {})
        primary_task = task_analysis.get("primary_task_type")
        if primary_task == "exploratory":
            recommendations.append("探索型任务：提供多角度视角和启发性问题")
        elif primary_task == "analytical": 
            recommendations.append("分析型任务：提供结构化思维框架和逻辑工具")
        elif primary_task == "creative":
            recommendations.append("创新型任务：激发联想和提供跨域案例")
        
        # 基于交互模式的建议
        interaction_patterns = user_profile.get("interaction_patterns", {})
        if interaction_patterns:
            info_processing = interaction_patterns.get("information_processing", {})
            complexity_pref = info_processing.get("complexity_preference", {})
            if complexity_pref.get("level") == "complex":
                recommendations.append("用户能接受复杂信息，可以提供深入详细的分析")
            elif complexity_pref.get("level") == "simple":
                recommendations.append("用户偏好简单信息，应分步骤渐进式展开")
        
        # 默认建议
        if not recommendations:
            recommendations = [
                "基于当前信息提供平衡的认知支持",
                "观察用户反馈并动态调整策略"
            ]
        
        return recommendations