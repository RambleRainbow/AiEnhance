"""
协作协调器
统筹协作层各模块，实现人机深度认知协作的整体编排
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .interfaces import (
    CollaborationOrchestrator, CollaborationContext,
    PerspectiveRequest, PerspectiveType, ChallengeRequest, ChallengeType
)
from .dialectical_perspective import DialecticalPerspectiveGenerator
from .cognitive_challenge import CognitiveChallenge
from ..llm.interfaces import LLMProvider
from ..memory.interfaces import MemorySystem, MemoryEntry, UserContext, MemoryType

logger = logging.getLogger(__name__)


class CollaborativeCoordinator(CollaborationOrchestrator):
    """
    协作协调器
    
    统筹辩证视角生成、认知挑战、用户建模等功能，
    实现人机之间的深度认知协作
    """
    
    def __init__(self, llm_provider: LLMProvider, memory_system: Optional[MemorySystem] = None):
        self.llm_provider = llm_provider
        self.memory_system = memory_system
        
        # 初始化协作模块
        self.perspective_generator = DialecticalPerspectiveGenerator(llm_provider, memory_system)
        self.cognitive_challenger = CognitiveChallenge(llm_provider, memory_system)
        
        # 协作配置
        self.collaboration_config = {
            "enable_dialectical_perspective": True,
            "enable_cognitive_challenge": True,
            "enable_user_modeling": True,
            "enable_adaptive_intensity": True,
            "max_perspectives": 3,
            "max_challenges": 3,
            "default_challenge_intensity": "moderate"
        }
        
        # 用户认知画像存储
        self.user_cognitive_profiles = {}
    
    async def orchestrate_collaboration(self, content: str, 
                                       context: CollaborationContext) -> Dict[str, Any]:
        """编排协作过程"""
        try:
            collaboration_result = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "user_id": context.user_id,
                "session_id": context.session_id,
                "perspectives": None,
                "challenges": None,
                "synthesis": None,
                "collaboration_insights": None,
                "next_collaboration_steps": None
            }
            
            # 1. 分析内容和用户上下文
            content_analysis = await self._analyze_collaboration_needs(content, context)
            
            # 2. 获取或更新用户认知画像
            user_profile = await self._get_user_cognitive_profile(context)
            
            # 3. 决定协作策略
            collaboration_strategy = await self._determine_collaboration_strategy(
                content_analysis, user_profile
            )
            
            # 4. 生成辩证视角（如果启用）
            if collaboration_strategy.get("enable_perspectives", True):
                perspectives_result = await self._generate_collaborative_perspectives(
                    content, context, collaboration_strategy
                )
                collaboration_result["perspectives"] = perspectives_result
            
            # 5. 生成认知挑战（如果启用）
            if collaboration_strategy.get("enable_challenges", True):
                challenges_result = await self._generate_collaborative_challenges(
                    content, context, collaboration_strategy
                )
                collaboration_result["challenges"] = challenges_result
            
            # 6. 综合协作洞察
            collaboration_insights = await self._synthesize_collaboration_insights(
                collaboration_result, user_profile
            )
            collaboration_result["collaboration_insights"] = collaboration_insights
            
            # 7. 提供下一步协作建议
            next_steps = await self._generate_collaboration_next_steps(
                collaboration_result, user_profile
            )
            collaboration_result["next_collaboration_steps"] = next_steps
            
            # 8. 更新用户认知画像
            await self.update_user_cognitive_profile(context, {
                "interaction_content": content,
                "collaboration_result": collaboration_result,
                "engagement_level": content_analysis.get("complexity_level", "moderate")
            })
            
            # 9. 保存协作记忆（如果有记忆系统）
            if self.memory_system:
                await self._save_collaboration_memory(collaboration_result, context)
            
            return collaboration_result
            
        except Exception as e:
            logger.error(f"Failed to orchestrate collaboration: {e}")
            return {
                "content": content,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_collaboration_needs(self, content: str, 
                                         context: CollaborationContext) -> Dict[str, Any]:
        """分析协作需求"""
        prompt = f"""
分析以下内容的协作需求：

内容：{content}

请评估：
1. 内容的复杂性水平（简单/中等/复杂）
2. 是否需要多视角分析
3. 是否需要认知挑战
4. 用户可能的认知盲点
5. 协作的优先级和重点

以结构化格式返回分析结果。
"""
        
        from ..llm.interfaces import ChatMessage, MessageRole
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        
        # 解析分析结果
        return self._parse_collaboration_analysis(response.content)
    
    def _parse_collaboration_analysis(self, response: str) -> Dict[str, Any]:
        """解析协作需求分析"""
        analysis = {
            "complexity_level": "moderate",
            "needs_perspectives": True,
            "needs_challenges": True,
            "potential_blind_spots": [],
            "collaboration_priorities": []
        }
        
        # 简单的关键词分析
        if any(word in response.lower() for word in ['复杂', 'complex', '困难', 'difficult']):
            analysis["complexity_level"] = "complex"
        elif any(word in response.lower() for word in ['简单', 'simple', '基本', 'basic']):
            analysis["complexity_level"] = "simple"
        
        if any(word in response.lower() for word in ['视角', 'perspective', '角度', 'angle']):
            analysis["needs_perspectives"] = True
        
        if any(word in response.lower() for word in ['挑战', 'challenge', '质疑', 'question']):
            analysis["needs_challenges"] = True
        
        return analysis
    
    async def _get_user_cognitive_profile(self, context: CollaborationContext) -> Dict[str, Any]:
        """获取用户认知画像"""
        user_id = context.user_id
        
        # 如果已有画像，返回现有画像
        if user_id in self.user_cognitive_profiles:
            return self.user_cognitive_profiles[user_id]
        
        # 创建新的用户认知画像
        default_profile = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "cognitive_preferences": {
                "preferred_challenge_intensity": "moderate",
                "openness_to_perspectives": 0.7,
                "analytical_depth": 0.6,
                "creativity_level": 0.5
            },
            "interaction_history": [],
            "learning_patterns": {
                "engagement_with_challenges": 0.5,
                "perspective_adoption": 0.5,
                "depth_of_reflection": 0.5
            },
            "collaboration_effectiveness": {
                "total_interactions": 0,
                "successful_collaborations": 0,
                "growth_indicators": []
            }
        }
        
        # 如果有记忆系统，尝试从记忆中恢复画像
        if self.memory_system:
            try:
                user_context = UserContext(user_id=user_id, session_id=context.session_id)
                memories = await self.memory_system.get_user_memories(user_context, limit=50)
                
                # 从记忆中分析用户的认知模式
                if memories.memories:
                    cognitive_analysis = await self._analyze_user_cognitive_patterns(memories.memories)
                    default_profile["cognitive_preferences"].update(cognitive_analysis)
                    
            except Exception as e:
                logger.warning(f"Failed to load user cognitive profile from memory: {e}")
        
        self.user_cognitive_profiles[user_id] = default_profile
        return default_profile
    
    async def _analyze_user_cognitive_patterns(self, memories: List) -> Dict[str, float]:
        """从记忆中分析用户认知模式"""
        # 简化的认知模式分析
        patterns = {
            "openness_to_perspectives": 0.7,
            "analytical_depth": 0.6, 
            "creativity_level": 0.5
        }
        
        # 基于记忆内容的简单分析
        total_content = " ".join([mem.content for mem in memories[:10]])
        
        # 分析开放性
        if any(word in total_content.lower() for word in ['确实', '有趣', '思考', '可能']):
            patterns["openness_to_perspectives"] = min(1.0, patterns["openness_to_perspectives"] + 0.2)
        
        # 分析分析深度
        if len(total_content.split()) > 500:  # 用户倾向于详细表达
            patterns["analytical_depth"] = min(1.0, patterns["analytical_depth"] + 0.2)
        
        # 分析创意水平
        if any(word in total_content.lower() for word in ['创新', '创意', '新', '不同']):
            patterns["creativity_level"] = min(1.0, patterns["creativity_level"] + 0.2)
        
        return patterns
    
    async def _determine_collaboration_strategy(self, content_analysis: Dict[str, Any],
                                              user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """确定协作策略"""
        strategy = {
            "enable_perspectives": True,
            "enable_challenges": True,
            "perspective_types": [],
            "challenge_types": [],
            "intensity_level": "moderate"
        }
        
        # 基于内容复杂性调整策略
        complexity = content_analysis.get("complexity_level", "moderate")
        if complexity == "complex":
            strategy["perspective_types"] = [
                PerspectiveType.OPPOSING,
                PerspectiveType.MULTI_DISCIPLINARY,
                PerspectiveType.STAKEHOLDER
            ]
            strategy["challenge_types"] = [
                ChallengeType.ASSUMPTION_QUESTIONING,
                ChallengeType.COMPLEXITY_EXPANSION
            ]
        elif complexity == "simple":
            strategy["perspective_types"] = [PerspectiveType.ALTERNATIVE]
            strategy["challenge_types"] = [ChallengeType.CREATIVE_PROVOCATION]
        else:  # moderate
            strategy["perspective_types"] = [
                PerspectiveType.OPPOSING,
                PerspectiveType.MULTI_DISCIPLINARY
            ]
            strategy["challenge_types"] = [
                ChallengeType.ASSUMPTION_QUESTIONING,
                ChallengeType.BLIND_SPOT_DETECTION
            ]
        
        # 基于用户画像调整强度
        user_prefs = user_profile.get("cognitive_preferences", {})
        preferred_intensity = user_prefs.get("preferred_challenge_intensity", "moderate")
        openness = user_prefs.get("openness_to_perspectives", 0.7)
        
        if openness < 0.5:
            strategy["intensity_level"] = "gentle"
        elif openness > 0.8:
            strategy["intensity_level"] = "strong"
        else:
            strategy["intensity_level"] = preferred_intensity
        
        return strategy
    
    async def _generate_collaborative_perspectives(self, content: str,
                                                 context: CollaborationContext,
                                                 strategy: Dict[str, Any]) -> Dict[str, Any]:
        """生成协作视角"""
        try:
            perspective_request = PerspectiveRequest(
                content=content,
                perspective_types=strategy.get("perspective_types", [PerspectiveType.OPPOSING]),
                max_perspectives=self.collaboration_config["max_perspectives"],
                depth_level=strategy.get("intensity_level", "moderate")
            )
            
            perspectives_result = await self.perspective_generator.generate_perspectives(
                perspective_request, context
            )
            
            return {
                "perspectives": [
                    {
                        "type": p.perspective_type.value,
                        "title": p.title,
                        "description": p.description,
                        "key_arguments": p.key_arguments,
                        "supporting_evidence": p.supporting_evidence,
                        "relevance_score": p.relevance_score
                    }
                    for p in perspectives_result.perspectives
                ],
                "synthesis": perspectives_result.synthesis,
                "dialectical_tensions": perspectives_result.dialectical_tensions,
                "integration_suggestions": perspectives_result.integration_suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to generate collaborative perspectives: {e}")
            return {"error": str(e)}
    
    async def _generate_collaborative_challenges(self, content: str,
                                               context: CollaborationContext,
                                               strategy: Dict[str, Any]) -> Dict[str, Any]:
        """生成协作挑战"""
        try:
            challenge_request = ChallengeRequest(
                content=content,
                challenge_types=strategy.get("challenge_types", [ChallengeType.ASSUMPTION_QUESTIONING]),
                intensity_level=strategy.get("intensity_level", "moderate")
            )
            
            challenges_result = await self.cognitive_challenger.generate_challenges(
                challenge_request, context
            )
            
            return {
                "challenges": [
                    {
                        "type": c.challenge_type.value,
                        "title": c.title,
                        "description": c.description,
                        "questions": c.questions,
                        "alternative_frameworks": c.alternative_frameworks,
                        "expansion_directions": c.expansion_directions
                    }
                    for c in challenges_result.challenges
                ],
                "meta_reflection": challenges_result.meta_reflection,
                "growth_opportunities": challenges_result.growth_opportunities,
                "next_steps": challenges_result.next_steps
            }
            
        except Exception as e:
            logger.error(f"Failed to generate collaborative challenges: {e}")
            return {"error": str(e)}
    
    async def _synthesize_collaboration_insights(self, collaboration_result: Dict[str, Any],
                                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """综合协作洞察"""
        insights = {
            "collaboration_effectiveness": "moderate",
            "user_engagement_prediction": 0.7,
            "learning_opportunities": [],
            "cognitive_growth_indicators": [],
            "personalized_recommendations": []
        }
        
        # 分析视角和挑战的质量
        perspectives = collaboration_result.get("perspectives", {})
        challenges = collaboration_result.get("challenges", {})
        
        if perspectives and not perspectives.get("error"):
            insights["learning_opportunities"].append("多视角思维训练")
            if len(perspectives.get("perspectives", [])) > 2:
                insights["collaboration_effectiveness"] = "high"
        
        if challenges and not challenges.get("error"):
            insights["learning_opportunities"].append("批判性思维发展")
            insights["cognitive_growth_indicators"].append("质疑能力提升")
        
        # 基于用户画像提供个性化建议
        user_prefs = user_profile.get("cognitive_preferences", {})
        if user_prefs.get("creativity_level", 0.5) < 0.6:
            insights["personalized_recommendations"].append("尝试更多创意性思维练习")
        
        if user_prefs.get("analytical_depth", 0.6) < 0.7:
            insights["personalized_recommendations"].append("深入分析论证结构和逻辑关系")
        
        return insights
    
    async def _generate_collaboration_next_steps(self, collaboration_result: Dict[str, Any],
                                               user_profile: Dict[str, Any]) -> List[str]:
        """生成协作下一步建议"""
        next_steps = []
        
        # 基于协作结果的建议
        perspectives = collaboration_result.get("perspectives", {})
        challenges = collaboration_result.get("challenges", {})
        
        if perspectives and not perspectives.get("error"):
            if perspectives.get("integration_suggestions"):
                next_steps.append("尝试整合不同视角，形成更全面的理解")
            if perspectives.get("dialectical_tensions"):
                next_steps.append("深入探讨辩证冲突，寻找平衡点")
        
        if challenges and not challenges.get("error"):
            if challenges.get("next_steps"):
                next_steps.extend(challenges["next_steps"][:2])
        
        # 基于用户画像的个性化建议
        user_prefs = user_profile.get("cognitive_preferences", {})
        learning_patterns = user_profile.get("learning_patterns", {})
        
        if learning_patterns.get("engagement_with_challenges", 0.5) < 0.6:
            next_steps.append("尝试更积极地回应认知挑战")
        
        if learning_patterns.get("depth_of_reflection", 0.5) < 0.6:
            next_steps.append("花更多时间进行深度反思")
        
        # 通用建议
        next_steps.extend([
            "记录思考过程的变化",
            "将新的思维方式应用到其他问题"
        ])
        
        return list(set(next_steps))[:5]  # 去重并限制数量
    
    async def update_user_cognitive_profile(self, context: CollaborationContext,
                                          interaction_data: Dict[str, Any]) -> bool:
        """更新用户认知画像"""
        try:
            user_id = context.user_id
            if user_id not in self.user_cognitive_profiles:
                await self._get_user_cognitive_profile(context)
            
            profile = self.user_cognitive_profiles[user_id]
            
            # 更新时间戳
            profile["updated_at"] = datetime.now().isoformat()
            
            # 更新交互历史
            interaction_summary = {
                "timestamp": datetime.now().isoformat(),
                "content_preview": interaction_data.get("interaction_content", "")[:100],
                "engagement_level": interaction_data.get("engagement_level", "moderate"),
                "collaboration_success": not any(
                    result.get("error") for result in [
                        interaction_data.get("collaboration_result", {}).get("perspectives", {}),
                        interaction_data.get("collaboration_result", {}).get("challenges", {})
                    ]
                )
            }
            
            profile["interaction_history"].append(interaction_summary)
            # 保持历史记录在合理范围内
            if len(profile["interaction_history"]) > 20:
                profile["interaction_history"] = profile["interaction_history"][-20:]
            
            # 更新学习模式
            if interaction_summary["collaboration_success"]:
                profile["collaboration_effectiveness"]["successful_collaborations"] += 1
            profile["collaboration_effectiveness"]["total_interactions"] += 1
            
            # 更新认知偏好（基于交互表现）
            engagement = interaction_data.get("engagement_level", "moderate")
            if engagement == "high":
                profile["cognitive_preferences"]["openness_to_perspectives"] = min(
                    1.0, profile["cognitive_preferences"]["openness_to_perspectives"] + 0.1
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user cognitive profile: {e}")
            return False
    
    async def _save_collaboration_memory(self, collaboration_result: Dict[str, Any],
                                       context: CollaborationContext) -> bool:
        """保存协作记忆"""
        try:
            if not self.memory_system:
                return False
            
            # 创建协作记忆条目
            memory_content = f"协作会话：{collaboration_result['content'][:200]}..."
            
            user_context = UserContext(
                user_id=context.user_id,
                session_id=context.session_id
            )
            
            memory_entry = MemoryEntry(
                content=memory_content,
                memory_type=MemoryType.EPISODIC,
                user_context=user_context,
                timestamp=datetime.now(),
                confidence=0.9,
                metadata={
                    "collaboration_type": "cognitive_enhancement",
                    "perspectives_generated": len(collaboration_result.get("perspectives", {}).get("perspectives", [])),
                    "challenges_generated": len(collaboration_result.get("challenges", {}).get("challenges", [])),
                    "collaboration_insights": collaboration_result.get("collaboration_insights", {})
                }
            )
            
            await self.memory_system.add_memory(memory_entry)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save collaboration memory: {e}")
            return False
    
    def get_collaboration_config(self) -> Dict[str, Any]:
        """获取协作配置"""
        return self.collaboration_config.copy()
    
    def update_collaboration_config(self, config_updates: Dict[str, Any]) -> bool:
        """更新协作配置"""
        try:
            self.collaboration_config.update(config_updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update collaboration config: {e}")
            return False