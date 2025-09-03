"""
行为层主类

基于设计文档第六章，行为层负责将认知层的处理结果转化为对用户有效的交互输出，
是系统"认知放大"理念的直接体现。这一层的设计注重个性化、启发性和元认知支持。
"""

from typing import Dict, Any
import logging
from aienhance.core.base_architecture import BaseLayer, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class BehaviorLayer(BaseLayer):
    """行为层"""
    
    def __init__(self, llm_adapter=None, memory_adapter=None, config: Dict[str, Any] = None):
        # 简化实现，将四个模块的功能整合
        super().__init__("behavior", [], config)
        self.llm_adapter = llm_adapter
        self.memory_adapter = memory_adapter
        
    async def _initialize_impl(self):
        """层初始化实现"""
        logger.info("Initializing Behavior Layer")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理行为层逻辑"""
        try:
            # 获取认知层输出
            cognition_output = context.layer_outputs.get("cognition", {})
            cognitive_insights = cognition_output.get("cognitive_insights", {})
            
            # 获取用户画像
            perception_output = context.layer_outputs.get("perception", {})
            user_profile = perception_output.get("user_cognitive_profile", {})
            
            # 四个模块功能整合
            
            # 1. 个性化认知适配
            personalized_adaptation = await self._personalized_cognitive_adaptation(
                context, user_profile, cognitive_insights
            )
            
            # 2. 行为拟合与认知互补
            behavioral_fitting = await self._behavioral_fitting_and_complement(
                context, user_profile
            )
            
            # 3. 启发式输出策略
            heuristic_output = await self._heuristic_output_strategy(
                context, cognitive_insights
            )
            
            # 4. 元认知引导机制
            metacognitive_guidance = await self._metacognitive_guidance(
                context, user_profile
            )
            
            behavior_output = {
                "personalized_adaptation": personalized_adaptation,
                "behavioral_fitting": behavioral_fitting,
                "heuristic_output": heuristic_output,
                "metacognitive_guidance": metacognitive_guidance,
                "final_response": await self._generate_final_response(
                    context, personalized_adaptation, heuristic_output
                )
            }
            
            return ProcessingResult(
                success=True,
                data={
                    "behavior_output": behavior_output,
                    "adapted_response": behavior_output["final_response"],
                    "output_confidence": 0.8
                },
                metadata={
                    "layer": "behavior",
                    "adaptation_applied": True,
                    "response_style": personalized_adaptation.get("response_style", "balanced")
                }
            )
            
        except Exception as e:
            logger.error(f"Behavior layer processing failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _personalized_cognitive_adaptation(self, context: ProcessingContext,
                                               user_profile: Dict[str, Any],
                                               cognitive_insights: Dict[str, Any]) -> Dict[str, Any]:
        """个性化认知适配"""
        
        adaptation = {
            "information_density": "medium",
            "logical_structure": "hierarchical",
            "concept_granularity": "moderate",
            "response_style": "balanced"
        }
        
        # 基于用户交互模式调整
        interaction_patterns = user_profile.get("interaction_patterns", {})
        if interaction_patterns:
            info_processing = interaction_patterns.get("information_processing", {})
            complexity_pref = info_processing.get("complexity_preference", {})
            
            if complexity_pref.get("level") == "complex":
                adaptation["information_density"] = "high"
                adaptation["concept_granularity"] = "detailed"
            elif complexity_pref.get("level") == "simple":
                adaptation["information_density"] = "low"
                adaptation["concept_granularity"] = "basic"
        
        return adaptation
    
    async def _behavioral_fitting_and_complement(self, context: ProcessingContext,
                                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """行为拟合与认知互补"""
        
        fitting = {
            "thinking_style_match": "balanced",
            "expression_style": "professional",
            "cognitive_complement": []
        }
        
        # 基于用户认知能力提供互补
        cognitive_abilities = user_profile.get("cognitive_abilities", {})
        if cognitive_abilities:
            thinking_style = cognitive_abilities.get("thinking_style", {})
            abstract_score = thinking_style.get("abstract_vs_concrete", {}).get("score", 0.5)
            
            if abstract_score > 0.7:
                fitting["cognitive_complement"].append("提供具体实例补充抽象概念")
            elif abstract_score < 0.3:
                fitting["cognitive_complement"].append("提供抽象框架补充具体经验")
        
        return fitting
    
    async def _heuristic_output_strategy(self, context: ProcessingContext,
                                       cognitive_insights: Dict[str, Any]) -> Dict[str, Any]:
        """启发式输出策略"""
        
        heuristic = {
            "output_type": "structured_response",
            "guidance_cues": [],
            "thinking_paths": [],
            "questioning_approach": "moderate"
        }
        
        # 基于认知洞察提供启发性引导
        insights = cognitive_insights.get("cognitive_insights", [])
        for insight in insights[:3]:
            heuristic["guidance_cues"].append(f"启发：{insight}")
        
        return heuristic
    
    async def _metacognitive_guidance(self, context: ProcessingContext,
                                    user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """元认知引导机制"""
        
        guidance = {
            "cognitive_strategies": ["系统性分析", "多角度思考"],
            "reflection_prompts": [],
            "bias_awareness": []
        }
        
        # 根据问题类型提供元认知引导
        if "分析" in context.query:
            guidance["reflection_prompts"].append("考虑：这个分析是否全面？")
            guidance["cognitive_strategies"].append("结构化分析法")
        
        return guidance
    
    async def _generate_final_response(self, context: ProcessingContext,
                                     adaptation: Dict[str, Any],
                                     heuristic: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终响应"""
        
        final_response = {
            "response_content": "",
            "response_structure": adaptation.get("logical_structure", "hierarchical"),
            "guidance_elements": heuristic.get("guidance_cues", []),
            "interaction_style": adaptation.get("response_style", "balanced")
        }
        
        if self.llm_adapter:
            try:
                # 获取认知层的综合结果
                cognition_output = context.layer_outputs.get("cognition", {})
                
                response_prompt = f"""
基于以下信息生成个性化回答：

用户问题：{context.query}

认知处理结果：{cognition_output.get('cognitive_insights', {})}

适配要求：
- 信息密度：{adaptation.get('information_density', 'medium')}
- 结构偏好：{adaptation.get('logical_structure', 'hierarchical')}
- 概念粒度：{adaptation.get('concept_granularity', 'moderate')}

启发引导：{heuristic.get('guidance_cues', [])}

请生成适合用户的个性化回答，体现认知支持和启发引导。
"""
                
                response_content = await self.llm_adapter.completion(
                    response_prompt
                )
                
                final_response["response_content"] = response_content
                
            except Exception as e:
                logger.warning(f"Final response generation failed: {e}")
                final_response["response_content"] = "基于认知处理结果的个性化回答生成中..."
        
        return final_response