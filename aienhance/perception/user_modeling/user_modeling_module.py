"""
用户建模模块主类

基于设计文档第4.1节，构建多维度的动态用户画像，为实现个性化记忆激活提供基础。
该模块不仅关注用户的静态属性，更重要的是捕捉其动态的认知特征和思维模式。
"""

from typing import Dict, Any
import logging
from aienhance.core.base_architecture import BaseModule, ProcessingContext, ProcessingResult
from .cognitive_ability_modeling import CognitiveAbilityModelingSubModule
from .knowledge_structure_modeling import KnowledgeStructureModelingSubModule
from .interaction_pattern_modeling import InteractionPatternModelingSubModule

logger = logging.getLogger(__name__)


class UserModelingModule(BaseModule):
    """用户建模模块"""
    
    def __init__(self, llm_adapter=None, memory_adapter=None, config: Dict[str, Any] = None):
        # 创建子模块
        submodules = [
            CognitiveAbilityModelingSubModule(llm_adapter, config),
            KnowledgeStructureModelingSubModule(llm_adapter, config),
            InteractionPatternModelingSubModule(llm_adapter, config)
        ]
        
        super().__init__("user_modeling", submodules, config)
        self.memory_adapter = memory_adapter
        
    async def _initialize_impl(self):
        """模块初始化实现"""
        logger.info("Initializing User Modeling Module")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理用户建模"""
        try:
            # 并行处理所有子模块
            submodule_results = await self.process_submodules(context)
            
            # 整合各个维度的建模结果
            integrated_profile = await self._integrate_user_profile(
                submodule_results, context
            )
            
            # 更新用户画像到记忆系统
            if self.memory_adapter:
                await self._update_user_profile_in_memory(
                    integrated_profile, context.user_id
                )
            
            return ProcessingResult(
                success=True,
                data={
                    "user_profile": integrated_profile,
                    "submodule_results": {name: result.data for name, result in submodule_results.items() if result.success},
                    "profile_completeness": self._calculate_profile_completeness(integrated_profile),
                    "confidence_score": integrated_profile.get("overall_confidence", 0.5)
                },
                metadata={
                    "module": "user_modeling",
                    "successful_submodules": [name for name, result in submodule_results.items() if result.success],
                    "profile_dimensions": list(integrated_profile.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"User modeling module processing failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _integrate_user_profile(self, submodule_results: Dict[str, ProcessingResult], 
                                    context: ProcessingContext) -> Dict[str, Any]:
        """整合各个维度的用户建模结果"""
        integrated_profile = {
            "user_id": context.user_id,
            "profile_timestamp": context.metadata.get("created_at"),
            "cognitive_abilities": {},
            "knowledge_structure": {},
            "interaction_patterns": {},
            "overall_confidence": 0.0,
            "integration_notes": []
        }
        
        # 提取认知能力维度
        cognitive_result = submodule_results.get("cognitive_ability_modeling")
        if cognitive_result and cognitive_result.success:
            integrated_profile["cognitive_abilities"] = cognitive_result.data.get("cognitive_profile", {})
            integrated_profile["integration_notes"].append("认知能力维度建模成功")
        
        # 提取知识结构维度
        knowledge_result = submodule_results.get("knowledge_structure_modeling")
        if knowledge_result and knowledge_result.success:
            integrated_profile["knowledge_structure"] = knowledge_result.data.get("knowledge_profile", {})
            integrated_profile["integration_notes"].append("知识结构维度建模成功")
        
        # 提取交互模式维度
        interaction_result = submodule_results.get("interaction_pattern_modeling")
        if interaction_result and interaction_result.success:
            integrated_profile["interaction_patterns"] = interaction_result.data.get("interaction_profile", {})
            integrated_profile["integration_notes"].append("交互模式维度建模成功")
        
        # 计算整体置信度
        confidence_scores = []
        for result in submodule_results.values():
            if result.success and "confidence_score" in result.data:
                confidence_scores.append(result.data["confidence_score"])
        
        if confidence_scores:
            integrated_profile["overall_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        # 生成综合用户画像摘要
        integrated_profile["profile_summary"] = await self._generate_profile_summary(
            integrated_profile, context
        )
        
        return integrated_profile
    
    async def _generate_profile_summary(self, profile: Dict[str, Any], 
                                       context: ProcessingContext) -> Dict[str, Any]:
        """生成综合用户画像摘要"""
        
        # 如果没有LLM适配器，返回基础摘要
        if not hasattr(self, 'llm_adapter') or not self.submodules[0].llm_adapter:
            return {
                "summary_text": "用户画像正在构建中",
                "key_characteristics": ["待分析"],
                "recommended_strategies": ["观察和学习用户偏好"]
            }
        
        try:
            summary_prompt = f"""
基于以下用户画像数据，生成简洁的用户特征摘要：

认知能力特征：{profile.get('cognitive_abilities', {})}
知识结构特征：{profile.get('knowledge_structure', {})}  
交互模式特征：{profile.get('interaction_patterns', {})}

请生成JSON格式的摘要：
{{
    "summary_text": "用户的主要认知特征和偏好的简洁描述",
    "key_characteristics": ["特征1", "特征2", "特征3"],
    "recommended_strategies": ["推荐的交互策略1", "策略2", "策略3"],
    "learning_preferences": ["学习偏好1", "偏好2"],
    "communication_style": "建议的沟通风格"
}}
"""
            
            summary_response = await self.submodules[0].process_with_llm(summary_prompt, context)
            
            # 尝试解析JSON响应
            try:
                import json
                json_start = summary_response.find('{')
                json_end = summary_response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(summary_response[json_start:json_end])
            except:
                pass
            
            # 如果解析失败，返回基础摘要
            return {
                "summary_text": summary_response[:200] + "..." if len(summary_response) > 200 else summary_response,
                "key_characteristics": ["基于LLM分析"],
                "recommended_strategies": ["个性化交互"]
            }
            
        except Exception as e:
            logger.warning(f"Profile summary generation failed: {e}")
            return {
                "summary_text": "用户画像摘要生成失败",
                "key_characteristics": ["需要更多交互数据"],
                "recommended_strategies": ["继续观察用户行为模式"]
            }
    
    async def _update_user_profile_in_memory(self, profile: Dict[str, Any], user_id: str):
        """更新用户画像到记忆系统"""
        if not self.memory_adapter:
            return
        
        try:
            # 将用户画像存储到记忆系统
            await self.memory_adapter.store_user_profile(user_id, profile)
            logger.info(f"Updated user profile for {user_id} in memory system")
        except Exception as e:
            logger.warning(f"Failed to update user profile in memory: {e}")
    
    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """计算用户画像完整度"""
        completeness_factors = [
            1.0 if profile.get("cognitive_abilities") else 0.0,
            1.0 if profile.get("knowledge_structure") else 0.0,
            1.0 if profile.get("interaction_patterns") else 0.0,
        ]
        
        return sum(completeness_factors) / len(completeness_factors)