"""
行为层实现
处理内容适配、个性化输出、LLM生成等行为功能
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
import logging

from .layer_interfaces import (
    IBehaviorLayer, BehaviorInput, BehaviorOutput, 
    AdaptedContent, ProcessingStatus
)
from ..behavior.adaptive_output import IntegratedAdaptiveOutput
from ..llm.interfaces import LLMProvider, ChatMessage, create_chat_message

logger = logging.getLogger(__name__)


class BehaviorLayer(IBehaviorLayer):
    """行为层具体实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 llm_provider: Optional[LLMProvider] = None):
        """
        初始化行为层
        
        Args:
            config: 行为层配置
            llm_provider: 大语言模型提供商
        """
        self.config = config or {}
        self.llm_provider = llm_provider
        self.is_initialized = False
        
        # 核心组件
        self.adaptive_output: Optional[IntegratedAdaptiveOutput] = None
        
        # 运行时状态
        self.processing_count = 0
        self.last_processing_time = 0.0
        self.generation_cache = {}  # 生成内容缓存
        self.llm_initialized = False
        
    async def initialize(self) -> bool:
        """初始化行为层组件"""
        try:
            logger.info("Initializing Behavior Layer...")
            
            # 初始化适配输出组件
            self.adaptive_output = IntegratedAdaptiveOutput()
            logger.info("Adaptive output component initialized")
            
            # 初始化LLM提供商
            if self.llm_provider:
                try:
                    await self.llm_provider.initialize()
                    self.llm_initialized = True
                    logger.info("LLM provider initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize LLM provider: {e}")
                    self.llm_initialized = False
            else:
                logger.info("No LLM provider configured")
            
            self.is_initialized = True
            logger.info("Behavior Layer initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Behavior Layer: {e}")
            self.is_initialized = False
            return False
    
    async def process(self, input_data: BehaviorInput) -> BehaviorOutput:
        """
        处理行为层输入，生成适配内容
        
        Args:
            input_data: 行为层输入数据
            
        Returns:
            BehaviorOutput: 行为层处理结果
        """
        if not self.is_initialized:
            raise RuntimeError("Behavior Layer not initialized")
        
        start_time = datetime.now()
        processing_metadata = {
            'input_query': input_data.query,
            'user_id': input_data.user_profile.user_id,
            'processing_id': f"behavior_{self.processing_count}",
            'steps': [],
            'llm_available': self.llm_initialized
        }
        
        try:
            logger.info(f"Processing behavior input for user: {input_data.user_profile.user_id}")
            processing_metadata['steps'].append('started')
            
            # 1. 内容适配
            adapted_content = await self.adapt_content(
                input_data.query,
                input_data.user_profile,
                {
                    'context_profile': input_data.context_profile,
                    'cognition_output': input_data.cognition_output,
                    'generation_requirements': input_data.generation_requirements
                }
            )
            processing_metadata['steps'].append('content_adaptation_completed')
            
            # 2. 生成响应内容
            if self.llm_initialized:
                try:
                    generated_content = await self.generate_response(input_data)
                    adapted_content.content = generated_content
                    adapted_content.adaptation_strategy += " + llm_generated"
                    processing_metadata['steps'].append('llm_generation_completed')
                except Exception as e:
                    logger.warning(f"LLM generation failed, using adapted content: {e}")
                    processing_metadata['llm_generation_error'] = str(e)
            else:
                processing_metadata['steps'].append('llm_generation_skipped')
            
            # 3. 生成质量指标
            quality_metrics = await self._assess_quality_metrics(
                adapted_content, input_data
            )
            processing_metadata['steps'].append('quality_assessment_completed')
            
            # 4. 生成元数据
            generation_metadata = await self._generate_metadata(
                input_data, adapted_content, quality_metrics
            )
            processing_metadata['steps'].append('metadata_generation_completed')
            
            # 计算处理时间
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.last_processing_time = processing_time
            self.processing_count += 1
            
            # 构建输出
            output = BehaviorOutput(
                layer_name="behavior",
                status=ProcessingStatus.COMPLETED,
                data={
                    'adapted_content': adapted_content,
                    'generation_metadata': generation_metadata,
                    'quality_metrics': quality_metrics
                },
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                adapted_content=adapted_content,
                generation_metadata=generation_metadata,
                quality_metrics=quality_metrics
            )
            
            logger.info(f"Behavior processing completed in {processing_time:.3f}s")
            return output
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            logger.error(f"Behavior processing failed: {e}")
            processing_metadata['error'] = str(e)
            processing_metadata['steps'].append('error')
            
            # 返回错误状态的输出
            return BehaviorOutput(
                layer_name="behavior",
                status=ProcessingStatus.ERROR,
                data={},
                metadata=processing_metadata,
                timestamp=end_time.isoformat(),
                processing_time=processing_time,
                error_message=str(e),
                adapted_content=AdaptedContent(
                    content="处理失败，请稍后重试",
                    adaptation_strategy="error_fallback",
                    cognitive_load=0.0,
                    information_density="low",
                    structure_type="simple",
                    personalization_level=0.0
                ),
                generation_metadata={},
                quality_metrics={}
            )
    
    async def adapt_content(self, content: str, user_profile, 
                          context: Dict[str, Any]) -> AdaptedContent:
        """内容适配"""
        try:
            logger.info("Adapting content to user profile...")
            
            # 构建适配上下文
            adaptation_context = {
                'user_profile': user_profile,
                **context
            }
            
            # 使用集成适配输出组件
            if hasattr(context, 'cognition_output') and context['cognition_output']:
                # 如果有认知层输出，使用增强的片段
                cognition_output = context['cognition_output']
                if hasattr(cognition_output, 'semantic_enhancement'):
                    fragments = cognition_output.semantic_enhancement.enhanced_content
                else:
                    fragments = []
                
                adapted_result = self.adaptive_output.comprehensive_adaptation(
                    fragments, user_profile, adaptation_context
                )
            else:
                # 回退到基础适配
                adapted_result = await self._basic_content_adaptation(
                    content, user_profile, adaptation_context
                )
            
            # 转换为接口格式
            if hasattr(adapted_result, 'content'):
                return AdaptedContent(
                    content=adapted_result.content,
                    adaptation_strategy=getattr(adapted_result, 'adaptation_strategy', 'comprehensive'),
                    cognitive_load=getattr(adapted_result, 'cognitive_load', 0.5),
                    information_density=getattr(adapted_result, 'density_level', 'medium'),
                    structure_type=getattr(adapted_result, 'structure_type', 'hierarchical'),
                    personalization_level=getattr(adapted_result, 'adaptation_confidence', 0.7)
                )
            else:
                # 处理其他格式的适配结果
                return AdaptedContent(
                    content=str(adapted_result),
                    adaptation_strategy="fallback",
                    cognitive_load=0.5,
                    information_density="medium",
                    structure_type="simple",
                    personalization_level=0.5
                )
            
        except Exception as e:
            logger.error(f"Failed to adapt content: {e}")
            return AdaptedContent(
                content=content,  # 回退到原始内容
                adaptation_strategy="error_fallback",
                cognitive_load=0.5,
                information_density="medium",
                structure_type="simple",
                personalization_level=0.0
            )
    
    async def _basic_content_adaptation(self, content: str, user_profile,
                                      context: Dict[str, Any]) -> AdaptedContent:
        """基础内容适配（当没有认知层输出时的回退方案）"""
        # 基于用户画像进行简单适配
        cognitive_complexity = user_profile.cognitive_characteristics.get('cognitive_complexity', 0.5)
        thinking_mode = user_profile.cognitive_characteristics.get('thinking_mode', 'linear')
        
        # 调整信息密度
        if cognitive_complexity > 0.7:
            density = "high"
            cognitive_load = 0.6
        elif cognitive_complexity < 0.3:
            density = "low"
            cognitive_load = 0.3
        else:
            density = "medium"
            cognitive_load = 0.5
        
        # 调整结构类型
        if thinking_mode == 'creative':
            structure = "associative"
        elif thinking_mode == 'analytical':
            structure = "hierarchical"
        else:
            structure = "linear"
        
        # 简单的内容调整
        adapted_content = content
        if density == "low":
            adapted_content = f"简要说明：{content[:200]}..."
        elif density == "high":
            adapted_content = f"详细分析：{content}\n\n这涉及多个层面的考虑..."
        
        return AdaptedContent(
            content=adapted_content,
            adaptation_strategy="basic_user_profile",
            cognitive_load=cognitive_load,
            information_density=density,
            structure_type=structure,
            personalization_level=0.6
        )
    
    async def generate_response(self, input_data: BehaviorInput) -> str:
        """生成响应内容"""
        try:
            if not self.llm_initialized:
                raise RuntimeError("LLM provider not initialized")
            
            logger.info("Generating response with LLM...")
            
            # 构建对话消息
            messages = await self._build_chat_messages(input_data)
            
            # 调用LLM生成响应
            response = await self.llm_provider.chat(messages)
            
            logger.info(f"LLM response generated: {len(response.content)} characters")
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    async def generate_response_stream(self, input_data: BehaviorInput) -> AsyncIterator[str]:
        """流式生成响应内容"""
        try:
            if not self.llm_initialized:
                raise RuntimeError("LLM provider not initialized")
            
            logger.info("Starting streaming response generation...")
            
            # 构建对话消息
            messages = await self._build_chat_messages(input_data)
            
            # 流式调用LLM
            async for chunk in self.llm_provider.chat_stream(messages):
                yield chunk
            
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"生成响应时出错: {e}"
    
    async def _build_chat_messages(self, input_data: BehaviorInput) -> List[ChatMessage]:
        """构建LLM对话消息"""
        messages = []
        
        # 系统消息：角色设定和认知指导
        system_prompt = await self._build_system_prompt(input_data)
        messages.append(create_chat_message("system", system_prompt))
        
        # 添加认知上下文
        if input_data.cognition_output:
            context_info = await self._build_cognitive_context(input_data.cognition_output)
            if context_info:
                messages.append(create_chat_message("system", f"认知上下文:\n{context_info}"))
        
        # 用户查询
        messages.append(create_chat_message("user", input_data.query))
        
        return messages
    
    async def _build_system_prompt(self, input_data: BehaviorInput) -> str:
        """构建系统提示"""
        prompt_parts = [
            "你是一个智能的记忆-认知协同系统助手。",
            f"用户认知特征: {input_data.user_profile.cognitive_characteristics}",
            f"任务特征: 类型={input_data.context_profile.task_type}, 复杂度={input_data.context_profile.complexity_level}",
            "请基于用户的认知特征和任务需求，提供个性化的回答。"
        ]
        
        # 根据生成要求调整提示
        generation_reqs = input_data.generation_requirements
        if generation_reqs.get('style') == 'educational':
            prompt_parts.append("请采用教育导向的解释方式，注重循序渐进和概念建构。")
        elif generation_reqs.get('style') == 'research':
            prompt_parts.append("请提供深度分析和跨领域关联，支持学术研究需求。")
        
        # 根据用户偏好调整
        info_density = input_data.user_profile.interaction_preferences.get(
            'information_density_preference', 0.5
        )
        if info_density > 0.7:
            prompt_parts.append("用户偏好详细信息，请提供充分的细节和解释。")
        elif info_density < 0.3:
            prompt_parts.append("用户偏好简洁信息，请保持回答简明扼要。")
        
        return "\n".join(prompt_parts)
    
    async def _build_cognitive_context(self, cognition_output) -> str:
        """构建认知上下文信息"""
        context_parts = []
        
        # 记忆激活信息
        if hasattr(cognition_output, 'memory_activation'):
            activation = cognition_output.memory_activation
            fragment_count = len(activation.activated_fragments)
            if fragment_count > 0:
                context_parts.append(f"激活记忆片段: {fragment_count}个")
        
        # 语义增强信息
        if hasattr(cognition_output, 'semantic_enhancement'):
            enhancement = cognition_output.semantic_enhancement
            if enhancement.semantic_gaps_filled:
                context_parts.append(f"识别知识缺口: {', '.join(enhancement.semantic_gaps_filled[:3])}")
        
        # 类比推理信息
        if hasattr(cognition_output, 'analogy_reasoning'):
            reasoning = cognition_output.analogy_reasoning
            if reasoning.analogies:
                analogy_count = len(reasoning.analogies)
                context_parts.append(f"生成类比: {analogy_count}个")
        
        # 认知洞察
        if hasattr(cognition_output, 'cognitive_insights'):
            insights = cognition_output.cognitive_insights
            cognitive_load = insights.get('cognitive_load', 0.5)
            context_parts.append(f"预估认知负荷: {cognitive_load:.2f}")
        
        return "\n".join(context_parts)
    
    async def _assess_quality_metrics(self, adapted_content: AdaptedContent,
                                    input_data: BehaviorInput) -> Dict[str, float]:
        """评估质量指标"""
        try:
            metrics = {
                'content_length_score': self._assess_content_length(adapted_content.content),
                'personalization_score': adapted_content.personalization_level,
                'cognitive_load_balance': self._assess_cognitive_load_balance(
                    adapted_content, input_data.user_profile
                ),
                'information_density_match': self._assess_density_match(
                    adapted_content, input_data.user_profile
                ),
                'structure_appropriateness': self._assess_structure_match(
                    adapted_content, input_data.user_profile
                ),
                'overall_quality': 0.0  # 将在最后计算
            }
            
            # 计算总体质量得分
            quality_scores = [v for k, v in metrics.items() if k != 'overall_quality']
            metrics['overall_quality'] = sum(quality_scores) / len(quality_scores)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to assess quality metrics: {e}")
            return {
                'content_length_score': 0.5,
                'personalization_score': 0.5,
                'cognitive_load_balance': 0.5,
                'information_density_match': 0.5,
                'structure_appropriateness': 0.5,
                'overall_quality': 0.5
            }
    
    def _assess_content_length(self, content: str) -> float:
        """评估内容长度合适性"""
        length = len(content)
        if 100 <= length <= 1000:
            return 1.0
        elif 50 <= length <= 2000:
            return 0.8
        elif length < 50:
            return 0.3
        else:
            return 0.6
    
    def _assess_cognitive_load_balance(self, adapted_content: AdaptedContent,
                                     user_profile) -> float:
        """评估认知负荷平衡性"""
        user_capacity = user_profile.cognitive_characteristics.get('cognitive_complexity', 0.5)
        content_load = adapted_content.cognitive_load
        
        # 理想情况是内容负荷略低于用户能力
        optimal_ratio = 0.8
        actual_ratio = content_load / max(0.1, user_capacity)
        
        # 计算与最优比例的偏差
        deviation = abs(actual_ratio - optimal_ratio)
        balance_score = max(0.0, 1.0 - deviation * 2)
        
        return balance_score
    
    def _assess_density_match(self, adapted_content: AdaptedContent,
                            user_profile) -> float:
        """评估信息密度匹配度"""
        user_preference = user_profile.interaction_preferences.get(
            'information_density_preference', 0.5
        )
        
        content_density = adapted_content.information_density
        density_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        content_density_value = density_map.get(content_density, 0.5)
        
        # 计算匹配度
        match_score = 1.0 - abs(user_preference - content_density_value)
        return max(0.0, match_score)
    
    def _assess_structure_match(self, adapted_content: AdaptedContent,
                              user_profile) -> float:
        """评估结构匹配度"""
        user_style = user_profile.interaction_preferences.get('cognitive_style', 'structured')
        content_structure = adapted_content.structure_type
        
        # 结构匹配映射
        structure_compatibility = {
            'structured': ['hierarchical', 'linear'],
            'flexible': ['associative', 'hierarchical'],
            'creative': ['associative', 'creative']
        }
        
        compatible_structures = structure_compatibility.get(user_style, ['hierarchical'])
        
        if content_structure in compatible_structures:
            return 1.0
        else:
            return 0.5
    
    async def _generate_metadata(self, input_data: BehaviorInput,
                               adapted_content: AdaptedContent,
                               quality_metrics: Dict[str, float]) -> Dict[str, Any]:
        """生成生成元数据"""
        metadata = {
            'adaptation_strategy': adapted_content.adaptation_strategy,
            'personalization_applied': adapted_content.personalization_level > 0.3,
            'cognitive_load_adjustment': adapted_content.cognitive_load,
            'structure_optimization': adapted_content.structure_type,
            'quality_assessment': quality_metrics,
            'generation_timestamp': datetime.now().isoformat(),
            'user_profile_utilized': {
                'cognitive_characteristics': True,
                'knowledge_profile': len(input_data.user_profile.knowledge_profile) > 0,
                'interaction_preferences': True
            },
            'context_factors': {
                'task_complexity': input_data.context_profile.complexity_level,
                'domain_match': input_data.context_profile.domain_characteristics.get('primary_domain', 'general'),
                'cognitive_insights_used': hasattr(input_data.cognition_output, 'cognitive_insights')
            }
        }
        
        return metadata
    
    async def cleanup(self) -> None:
        """清理行为层资源"""
        try:
            logger.info("Cleaning up Behavior Layer resources...")
            
            # 清理缓存
            self.generation_cache.clear()
            
            # 清理LLM连接
            if self.llm_provider and hasattr(self.llm_provider, 'session'):
                if self.llm_provider.session:
                    await self.llm_provider.session.close()
            
            # 清理适配组件
            if self.adaptive_output:
                # 如果有需要清理的资源
                pass
            
            self.is_initialized = False
            self.llm_initialized = False
            logger.info("Behavior Layer cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup Behavior Layer: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取行为层状态"""
        return {
            'layer_name': 'behavior',
            'initialized': self.is_initialized,
            'llm_initialized': self.llm_initialized,
            'processing_count': self.processing_count,
            'last_processing_time': self.last_processing_time,
            'cache_size': len(self.generation_cache),
            'components': {
                'adaptive_output': self.adaptive_output is not None,
                'llm_provider': self.llm_provider is not None
            },
            'llm_info': self.llm_provider.get_model_info() if self.llm_provider else None
        }