"""
分层认知系统
实现感知层、认知层、行为层、协作层的统一管理和信息流控制
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
import logging

from .layer_interfaces import (
    ICognitiveLayers, SystemResponse, InformationFlow, ProcessingStatus,
    PerceptionInput, CognitionInput, BehaviorInput, CollaborationInput
)
from .perception_layer import PerceptionLayer
from .cognition_layer import CognitionLayer
from .behavior_layer import BehaviorLayer
from .collaboration_layer import CollaborationLayer
from ..memory.interfaces import MemorySystem, MemoryQuery, create_user_context, MemoryType
from ..llm.interfaces import LLMProvider

logger = logging.getLogger(__name__)


class LayeredCognitiveSystem(ICognitiveLayers):
    """分层认知系统主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 memory_system: Optional[MemorySystem] = None,
                 llm_provider: Optional[LLMProvider] = None):
        """
        初始化分层认知系统
        
        Args:
            config: 系统配置
            memory_system: 记忆系统
            llm_provider: 大语言模型提供商
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.llm_provider = llm_provider
        
        # 核心层对象
        self.perception_layer: Optional[PerceptionLayer] = None
        self.cognition_layer: Optional[CognitionLayer] = None
        self.behavior_layer: Optional[BehaviorLayer] = None
        self.collaboration_layer: Optional[CollaborationLayer] = None
        
        # 系统状态
        self.is_initialized = False
        self.layers_initialized = {}
        
        # 信息流记录
        self.information_flows: List[InformationFlow] = []
        self.max_flow_history = 1000  # 最大信息流历史记录数
        
        # 性能统计
        self.processing_statistics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'average_processing_time': 0.0,
            'layer_performance': {}
        }
        
    async def initialize_layers(self) -> bool:
        """初始化所有层"""
        try:
            logger.info("Initializing Layered Cognitive System...")
            
            # 1. 初始化感知层
            logger.info("Initializing Perception Layer...")
            self.perception_layer = PerceptionLayer(
                config=self.config.get('perception', {}),
                memory_system=self.memory_system
            )
            perception_success = await self.perception_layer.initialize()
            self.layers_initialized['perception'] = perception_success
            
            if perception_success:
                logger.info("✅ Perception Layer initialized successfully")
            else:
                logger.error("❌ Perception Layer initialization failed")
                return False
            
            # 2. 初始化认知层
            logger.info("Initializing Cognition Layer...")
            self.cognition_layer = CognitionLayer(
                config=self.config.get('cognition', {})
            )
            cognition_success = await self.cognition_layer.initialize()
            self.layers_initialized['cognition'] = cognition_success
            
            if cognition_success:
                logger.info("✅ Cognition Layer initialized successfully")
            else:
                logger.error("❌ Cognition Layer initialization failed")
                return False
            
            # 3. 初始化行为层
            logger.info("Initializing Behavior Layer...")
            self.behavior_layer = BehaviorLayer(
                config=self.config.get('behavior', {}),
                llm_provider=self.llm_provider
            )
            behavior_success = await self.behavior_layer.initialize()
            self.layers_initialized['behavior'] = behavior_success
            
            if behavior_success:
                logger.info("✅ Behavior Layer initialized successfully")
            else:
                logger.error("❌ Behavior Layer initialization failed")
                return False
            
            # 4. 初始化协作层（可选）
            if self.config.get('enable_collaboration', True) and self.llm_provider:
                logger.info("Initializing Collaboration Layer...")
                self.collaboration_layer = CollaborationLayer(
                    config=self.config.get('collaboration', {}),
                    llm_provider=self.llm_provider,
                    memory_system=self.memory_system
                )
                collaboration_success = await self.collaboration_layer.initialize()
                self.layers_initialized['collaboration'] = collaboration_success
                
                if collaboration_success:
                    logger.info("✅ Collaboration Layer initialized successfully")
                else:
                    logger.warning("⚠️ Collaboration Layer initialization failed, continuing without collaboration")
            else:
                logger.info("⏭️ Collaboration Layer disabled or LLM not available")
                self.layers_initialized['collaboration'] = False
            
            self.is_initialized = True
            logger.info("🎉 Layered Cognitive System initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Layered Cognitive System: {e}")
            self.is_initialized = False
            return False
    
    async def process_through_layers(self, query: str, user_id: str, 
                                   context: Dict[str, Any]) -> SystemResponse:
        """
        通过各层处理用户查询
        
        Args:
            query: 用户查询
            user_id: 用户ID
            context: 上下文信息
            
        Returns:
            SystemResponse: 系统响应
        """
        if not self.is_initialized:
            raise RuntimeError("Layered Cognitive System not initialized")
        
        start_time = datetime.now()
        processing_metadata = {
            'query': query,
            'user_id': user_id,
            'timestamp': start_time.isoformat(),
            'processing_steps': [],
            'layer_timings': {},
            'information_flows': []
        }
        
        try:
            logger.info(f"🚀 Starting layered processing for user: {user_id}")
            self.processing_statistics['total_queries'] += 1
            
            # ==================== 感知层处理 ====================
            layer_start = datetime.now()
            processing_metadata['processing_steps'].append('perception_start')
            
            perception_input = PerceptionInput(
                query=query,
                user_id=user_id,
                context=context,
                historical_data=await self._get_user_historical_data(user_id)
            )
            
            self._record_information_flow('system', 'perception', perception_input, 'input')
            
            perception_output = await self.perception_layer.process(perception_input)
            
            self._record_information_flow('perception', 'system', perception_output, 'output')
            
            layer_end = datetime.now()
            perception_time = (layer_end - layer_start).total_seconds()
            processing_metadata['layer_timings']['perception'] = perception_time
            processing_metadata['processing_steps'].append('perception_complete')
            
            if perception_output.status != ProcessingStatus.COMPLETED:
                raise RuntimeError(f"Perception layer failed: {perception_output.error_message}")
            
            logger.info(f"✅ Perception layer completed in {perception_time:.3f}s")
            
            # ==================== 认知层处理 ====================
            layer_start = datetime.now()
            processing_metadata['processing_steps'].append('cognition_start')
            
            # 获取外部记忆
            external_memories = await self._retrieve_external_memories(query, user_id, context)
            
            cognition_input = CognitionInput(
                query=query,
                user_profile=perception_output.user_profile,
                context_profile=perception_output.context_profile,
                external_memories=external_memories,
                perception_insights=perception_output.perception_insights
            )
            
            self._record_information_flow('perception', 'cognition', cognition_input, 'input')
            
            cognition_output = await self.cognition_layer.process(cognition_input)
            
            self._record_information_flow('cognition', 'system', cognition_output, 'output')
            
            layer_end = datetime.now()
            cognition_time = (layer_end - layer_start).total_seconds()
            processing_metadata['layer_timings']['cognition'] = cognition_time
            processing_metadata['processing_steps'].append('cognition_complete')
            
            if cognition_output.status != ProcessingStatus.COMPLETED:
                raise RuntimeError(f"Cognition layer failed: {cognition_output.error_message}")
            
            logger.info(f"✅ Cognition layer completed in {cognition_time:.3f}s")
            
            # ==================== 行为层处理 ====================
            layer_start = datetime.now()
            processing_metadata['processing_steps'].append('behavior_start')
            
            behavior_input = BehaviorInput(
                query=query,
                user_profile=perception_output.user_profile,
                context_profile=perception_output.context_profile,
                cognition_output=cognition_output,
                generation_requirements=context.get('generation_requirements', {})
            )
            
            self._record_information_flow('cognition', 'behavior', behavior_input, 'input')
            
            behavior_output = await self.behavior_layer.process(behavior_input)
            
            self._record_information_flow('behavior', 'system', behavior_output, 'output')
            
            layer_end = datetime.now()
            behavior_time = (layer_end - layer_start).total_seconds()
            processing_metadata['layer_timings']['behavior'] = behavior_time
            processing_metadata['processing_steps'].append('behavior_complete')
            
            if behavior_output.status != ProcessingStatus.COMPLETED:
                raise RuntimeError(f"Behavior layer failed: {behavior_output.error_message}")
            
            logger.info(f"✅ Behavior layer completed in {behavior_time:.3f}s")
            
            # ==================== 协作层处理（可选）====================
            collaboration_output = None
            if self.collaboration_layer and self.layers_initialized.get('collaboration', False):
                layer_start = datetime.now()
                processing_metadata['processing_steps'].append('collaboration_start')
                
                collaboration_input = CollaborationInput(
                    query=query,
                    user_profile=perception_output.user_profile,
                    context_profile=perception_output.context_profile,
                    behavior_output=behavior_output,
                    collaboration_context=context.get('collaboration_context', {})
                )
                
                self._record_information_flow('behavior', 'collaboration', collaboration_input, 'input')
                
                try:
                    collaboration_output = await self.collaboration_layer.process(collaboration_input)
                    
                    self._record_information_flow('collaboration', 'system', collaboration_output, 'output')
                    
                    layer_end = datetime.now()
                    collaboration_time = (layer_end - layer_start).total_seconds()
                    processing_metadata['layer_timings']['collaboration'] = collaboration_time
                    processing_metadata['processing_steps'].append('collaboration_complete')
                    
                    logger.info(f"✅ Collaboration layer completed in {collaboration_time:.3f}s")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Collaboration layer failed, continuing without collaboration: {e}")
                    processing_metadata['collaboration_error'] = str(e)
                    processing_metadata['processing_steps'].append('collaboration_failed')
            else:
                processing_metadata['processing_steps'].append('collaboration_skipped')
            
            # ==================== 后处理和记忆保存 ====================
            processing_metadata['processing_steps'].append('postprocessing_start')
            
            # 保存处理结果到记忆系统
            if self.memory_system:
                try:
                    await self._save_processing_results(
                        query, user_id, context, perception_output,
                        cognition_output, behavior_output, collaboration_output
                    )
                    processing_metadata['processing_steps'].append('memory_saved')
                except Exception as e:
                    logger.warning(f"Failed to save processing results: {e}")
                    processing_metadata['memory_save_error'] = str(e)
            
            # 更新用户画像
            try:
                interaction_data = self._extract_interaction_data(
                    query, behavior_output, processing_metadata
                )
                await self.perception_layer.update_user_profile(user_id, interaction_data)
                processing_metadata['processing_steps'].append('profile_updated')
            except Exception as e:
                logger.warning(f"Failed to update user profile: {e}")
                processing_metadata['profile_update_error'] = str(e)
            
            # 计算总处理时间
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            processing_metadata['total_processing_time'] = total_processing_time
            processing_metadata['processing_steps'].append('completed')
            
            # 更新统计信息
            self._update_processing_statistics(total_processing_time, processing_metadata, True)
            
            # 构建最终响应
            final_content = behavior_output.adapted_content.content
            
            # 如果协作层产生了增强内容，使用它
            if (collaboration_output and 
                collaboration_output.enhanced_content and 
                collaboration_output.status == ProcessingStatus.COMPLETED):
                final_content = collaboration_output.enhanced_content
            
            response = SystemResponse(
                content=final_content,
                perception_output=perception_output,
                cognition_output=cognition_output,
                behavior_output=behavior_output,
                collaboration_output=collaboration_output,
                processing_metadata=processing_metadata
            )
            
            logger.info(f"🎉 Layered processing completed successfully in {total_processing_time:.3f}s")
            self.processing_statistics['successful_queries'] += 1
            
            return response
            
        except Exception as e:
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Layered processing failed: {e}")
            processing_metadata['error'] = str(e)
            processing_metadata['total_processing_time'] = total_processing_time
            processing_metadata['processing_steps'].append('error')
            
            # 更新统计信息
            self._update_processing_statistics(total_processing_time, processing_metadata, False)
            self.processing_statistics['failed_queries'] += 1
            
            raise RuntimeError(f"Layered processing failed: {e}")
    
    async def process_stream(self, query: str, user_id: str, 
                           context: Dict[str, Any]) -> AsyncIterator[str]:
        """
        流式处理用户查询
        
        Args:
            query: 用户查询
            user_id: 用户ID
            context: 上下文信息
            
        Yields:
            str: 流式处理步骤信息或内容
        """
        if not self.is_initialized:
            raise RuntimeError("Layered Cognitive System not initialized")
        
        try:
            yield "🚀 开始分层认知处理...\n"
            
            # ==================== 感知层处理 ====================
            yield "🧠 感知层：分析用户查询和上下文...\n"
            
            perception_input = PerceptionInput(
                query=query,
                user_id=user_id,
                context=context,
                historical_data=await self._get_user_historical_data(user_id)
            )
            
            perception_output = await self.perception_layer.process(perception_input)
            
            if perception_output.status == ProcessingStatus.COMPLETED:
                yield "✅ 感知层处理完成\n"
            else:
                yield f"❌ 感知层处理失败: {perception_output.error_message}\n"
                return
            
            # ==================== 认知层处理 ====================
            yield "💾 认知层：激活记忆和推理分析...\n"
            
            external_memories = await self._retrieve_external_memories(query, user_id, context)
            
            cognition_input = CognitionInput(
                query=query,
                user_profile=perception_output.user_profile,
                context_profile=perception_output.context_profile,
                external_memories=external_memories,
                perception_insights=perception_output.perception_insights
            )
            
            cognition_output = await self.cognition_layer.process(cognition_input)
            
            if cognition_output.status == ProcessingStatus.COMPLETED:
                yield "✅ 认知层处理完成\n"
            else:
                yield f"❌ 认知层处理失败: {cognition_output.error_message}\n"
                return
            
            # ==================== 行为层处理 ====================
            yield "⚙️ 行为层：生成个性化响应...\n"
            
            behavior_input = BehaviorInput(
                query=query,
                user_profile=perception_output.user_profile,
                context_profile=perception_output.context_profile,
                cognition_output=cognition_output,
                generation_requirements=context.get('generation_requirements', {})
            )
            
            # 检查是否支持流式生成
            if (self.behavior_layer.llm_initialized and 
                hasattr(self.behavior_layer.llm_provider, 'chat_stream')):
                
                yield "🤖 开始AI内容生成...\n"
                
                # 流式生成内容
                async for chunk in self.behavior_layer.generate_response_stream(behavior_input):
                    yield chunk
                
                yield "\n✅ 行为层处理完成\n"
            else:
                # 非流式处理
                behavior_output = await self.behavior_layer.process(behavior_input)
                
                if behavior_output.status == ProcessingStatus.COMPLETED:
                    yield behavior_output.adapted_content.content
                    yield "\n✅ 行为层处理完成\n"
                else:
                    yield f"❌ 行为层处理失败: {behavior_output.error_message}\n"
                    return
            
            # ==================== 协作层处理（可选）====================
            if self.collaboration_layer and self.layers_initialized.get('collaboration', False):
                yield "🤝 协作层：生成多元观点和认知挑战...\n"
                
                # 协作层通常不支持流式处理，快速完成
                try:
                    collaboration_input = CollaborationInput(
                        query=query,
                        user_profile=perception_output.user_profile,
                        context_profile=perception_output.context_profile,
                        behavior_output=behavior_output,
                        collaboration_context=context.get('collaboration_context', {})
                    )
                    
                    collaboration_output = await self.collaboration_layer.process(collaboration_input)
                    
                    if collaboration_output.status == ProcessingStatus.COMPLETED:
                        yield "✅ 协作层处理完成\n"
                        
                        # 如果有增强内容，输出差异部分
                        if collaboration_output.enhanced_content:
                            original_content = behavior_output.adapted_content.content
                            if collaboration_output.enhanced_content != original_content:
                                # 输出协作增强的部分
                                enhanced_part = collaboration_output.enhanced_content[len(original_content):]
                                if enhanced_part:
                                    yield enhanced_part
                    else:
                        yield f"⚠️ 协作层处理失败，继续处理: {collaboration_output.error_message}\n"
                        
                except Exception as e:
                    yield f"⚠️ 协作层处理异常，继续处理: {e}\n"
            
            yield "\n🎯 分层认知处理完成！\n"
            
            # 异步保存结果（不阻塞流式输出）
            asyncio.create_task(self._async_save_stream_results(
                query, user_id, context, perception_output, cognition_output
            ))
            
        except Exception as e:
            yield f"\n❌ 处理失败: {e}\n"
    
    async def _get_user_historical_data(self, user_id: str) -> Optional[List[Any]]:
        """获取用户历史数据"""
        try:
            if not self.memory_system:
                return None
            
            user_context = create_user_context(user_id)
            user_memories = await self.memory_system.get_user_memories(user_context, limit=20)
            
            return user_memories.memories
            
        except Exception as e:
            logger.warning(f"Failed to get user historical data: {e}")
            return None
    
    async def _retrieve_external_memories(self, query: str, user_id: str, 
                                        context: Dict[str, Any]) -> List[Any]:
        """检索外部记忆"""
        try:
            if not self.memory_system:
                return []
            
            user_context = create_user_context(user_id, context.get('session_id'))
            memory_query = MemoryQuery(
                query=query,
                user_context=user_context,
                limit=20,
                similarity_threshold=0.6
            )
            
            memory_result = await self.memory_system.search_memories(memory_query)
            return memory_result.memories
            
        except Exception as e:
            logger.warning(f"Failed to retrieve external memories: {e}")
            return []
    
    def _record_information_flow(self, from_layer: str, to_layer: str, 
                                data: Any, flow_type: str):
        """记录层间信息流"""
        try:
            flow = InformationFlow(
                from_layer=from_layer,
                to_layer=to_layer,
                data=data,
                flow_type=flow_type,
                timestamp=datetime.now().isoformat()
            )
            
            self.information_flows.append(flow)
            
            # 限制信息流历史记录数量
            if len(self.information_flows) > self.max_flow_history:
                self.information_flows = self.information_flows[-self.max_flow_history:]
                
        except Exception as e:
            logger.warning(f"Failed to record information flow: {e}")
    
    async def _save_processing_results(self, query: str, user_id: str, context: Dict[str, Any],
                                     perception_output, cognition_output, 
                                     behavior_output, collaboration_output):
        """保存处理结果到记忆系统"""
        try:
            if not self.memory_system:
                return
            
            user_context = create_user_context(user_id, context.get('session_id'))
            
            # 保存用户查询
            from ..memory.interfaces import create_memory_entry
            
            query_memory = create_memory_entry(
                content=f"用户查询: {query}",
                memory_type=MemoryType.EPISODIC,
                user_context=user_context,
                metadata={
                    "type": "user_query",
                    "processing_layers": ["perception", "cognition", "behavior", "collaboration"],
                    "user_profile": perception_output.user_profile.__dict__,
                    "context_profile": perception_output.context_profile.__dict__
                }
            )
            await self.memory_system.add_memory(query_memory)
            
            # 保存系统响应
            response_memory = create_memory_entry(
                content=f"系统响应: {behavior_output.adapted_content.content}",
                memory_type=MemoryType.EPISODIC,
                user_context=user_context,
                metadata={
                    "type": "system_response",
                    "adaptation_strategy": behavior_output.adapted_content.adaptation_strategy,
                    "cognitive_load": behavior_output.adapted_content.cognitive_load,
                    "quality_metrics": behavior_output.quality_metrics,
                    "collaboration_enhanced": collaboration_output is not None
                }
            )
            await self.memory_system.add_memory(response_memory)
            
            # 保存重要的认知洞察
            if hasattr(cognition_output, 'cognitive_insights'):
                insights = cognition_output.cognitive_insights
                if insights.get('knowledge_gaps'):
                    for gap in insights['knowledge_gaps'][:3]:
                        gap_memory = create_memory_entry(
                            content=f"知识缺口: {gap}",
                            memory_type=MemoryType.SEMANTIC,
                            user_context=user_context,
                            metadata={
                                "type": "knowledge_gap",
                                "query": query,
                                "cognitive_load": insights.get('cognitive_load', 0.5)
                            }
                        )
                        await self.memory_system.add_memory(gap_memory)
            
        except Exception as e:
            logger.error(f"Failed to save processing results: {e}")
    
    async def _async_save_stream_results(self, query: str, user_id: str, context: Dict[str, Any],
                                       perception_output, cognition_output):
        """异步保存流式处理结果"""
        try:
            await self._save_processing_results(
                query, user_id, context, perception_output, cognition_output, 
                None, None  # 流式处理时可能没有完整的behavior和collaboration输出
            )
        except Exception as e:
            logger.error(f"Failed to save stream results: {e}")
    
    def _extract_interaction_data(self, query: str, behavior_output, 
                                processing_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """提取交互数据用于更新用户画像"""
        return {
            'query': query,
            'response_quality': behavior_output.quality_metrics.get('overall_quality', 0.7),
            'cognitive_load': behavior_output.adapted_content.cognitive_load,
            'processing_time': processing_metadata.get('total_processing_time', 0.0),
            'adaptation_strategy': behavior_output.adapted_content.adaptation_strategy,
            'personalization_level': behavior_output.adapted_content.personalization_level
        }
    
    def _update_processing_statistics(self, processing_time: float, 
                                    metadata: Dict[str, Any], success: bool):
        """更新处理统计信息"""
        try:
            # 更新平均处理时间
            total_queries = self.processing_statistics['total_queries']
            current_avg = self.processing_statistics['average_processing_time']
            new_avg = (current_avg * (total_queries - 1) + processing_time) / total_queries
            self.processing_statistics['average_processing_time'] = new_avg
            
            # 更新层级性能统计
            layer_timings = metadata.get('layer_timings', {})
            for layer, timing in layer_timings.items():
                if layer not in self.processing_statistics['layer_performance']:
                    self.processing_statistics['layer_performance'][layer] = {
                        'total_time': 0.0,
                        'call_count': 0,
                        'average_time': 0.0
                    }
                
                layer_stats = self.processing_statistics['layer_performance'][layer]
                layer_stats['total_time'] += timing
                layer_stats['call_count'] += 1
                layer_stats['average_time'] = layer_stats['total_time'] / layer_stats['call_count']
                
        except Exception as e:
            logger.warning(f"Failed to update processing statistics: {e}")
    
    def get_layer_status(self, layer_name: str) -> Dict[str, Any]:
        """获取指定层的状态"""
        layer_map = {
            'perception': self.perception_layer,
            'cognition': self.cognition_layer,
            'behavior': self.behavior_layer,
            'collaboration': self.collaboration_layer
        }
        
        layer = layer_map.get(layer_name)
        if layer and hasattr(layer, 'get_status'):
            return layer.get_status()
        else:
            return {
                'layer_name': layer_name,
                'exists': layer is not None,
                'initialized': self.layers_initialized.get(layer_name, False)
            }
    
    def get_information_flows(self) -> List[InformationFlow]:
        """获取信息流记录"""
        return self.information_flows.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统整体状态"""
        return {
            'system_initialized': self.is_initialized,
            'layers_initialized': self.layers_initialized.copy(),
            'processing_statistics': self.processing_statistics.copy(),
            'information_flow_count': len(self.information_flows),
            'layer_status': {
                'perception': self.get_layer_status('perception'),
                'cognition': self.get_layer_status('cognition'),
                'behavior': self.get_layer_status('behavior'),
                'collaboration': self.get_layer_status('collaboration')
            },
            'dependencies': {
                'memory_system': self.memory_system is not None,
                'llm_provider': self.llm_provider is not None
            }
        }
    
    async def cleanup_all_layers(self) -> None:
        """清理所有层资源"""
        try:
            logger.info("Cleaning up all layers...")
            
            # 清理各个层
            cleanup_tasks = []
            
            if self.perception_layer:
                cleanup_tasks.append(self.perception_layer.cleanup())
            
            if self.cognition_layer:
                cleanup_tasks.append(self.cognition_layer.cleanup())
            
            if self.behavior_layer:
                cleanup_tasks.append(self.behavior_layer.cleanup())
            
            if self.collaboration_layer:
                cleanup_tasks.append(self.collaboration_layer.cleanup())
            
            # 并行清理
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            # 清理系统状态
            self.information_flows.clear()
            self.is_initialized = False
            self.layers_initialized.clear()
            
            logger.info("All layers cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup all layers: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if not self.is_initialized:
            await self.initialize_layers()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup_all_layers()