"""
记忆-认知协同系统核心 - 对应设计文档整体架构
整合感知层、认知层、行为层、协作层的完整系统
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..perception import (
    DynamicUserModeler, 
    IntegratedContextAnalyzer,
    UserProfile,
    ContextProfile
)
from ..cognition import (
    MultiLevelMemoryActivator,
    IntegratedSemanticEnhancer,
    IntegratedAnalogyReasoner,
    MemoryFragment,
    ActivationResult,
    IntegrationResult
)
from ..behavior.adaptive_output import (
    IntegratedAdaptiveOutput,
    AdaptedContent
)
from ..memory import (
    MemorySystem,
    MemorySystemFactory,
    MemorySystemConfig,
    MemoryEntry,
    MemoryQuery,
    UserContext,
    MemoryType,
    create_user_context,
    create_memory_entry
)


@dataclass
class SystemResponse:
    """系统响应"""
    content: str
    user_profile: UserProfile
    context_profile: ContextProfile
    activated_memories: List[ActivationResult]
    semantic_enhancement: IntegrationResult
    analogy_reasoning: Dict[str, Any]
    adaptation_info: AdaptedContent
    processing_metadata: Dict[str, Any]


class MemoryCognitiveSystem:
    """
    记忆-认知协同系统主类
    实现设计文档中的四层架构和核心功能
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, memory_config: Optional[MemorySystemConfig] = None):
        """
        初始化系统
        
        Args:
            config: 系统配置参数
            memory_config: 记忆系统配置
        """
        self.config = config or {}
        self.memory_config = memory_config
        
        # 初始化各层模块
        self._initialize_perception_layer()
        self._initialize_cognition_layer()
        self._initialize_behavior_layer()
        self._initialize_memory_layer()
        # self._initialize_collaboration_layer()  # TODO: 实现协作层
        
        # 系统状态
        self.is_initialized = True
        self.session_history = []
    
    def _initialize_perception_layer(self):
        """初始化感知层"""
        self.user_modeler = DynamicUserModeler()
        self.context_analyzer = IntegratedContextAnalyzer()
    
    def _initialize_cognition_layer(self):
        """初始化认知层"""
        self.memory_activator = MultiLevelMemoryActivator()
        self.semantic_enhancer = IntegratedSemanticEnhancer()
        self.analogy_reasoner = IntegratedAnalogyReasoner()
    
    def _initialize_behavior_layer(self):
        """初始化行为层"""
        self.adaptive_output = IntegratedAdaptiveOutput()
    
    def _initialize_memory_layer(self):
        """初始化记忆层"""
        if self.memory_config:
            try:
                self.memory_system = MemorySystemFactory.create_memory_system(self.memory_config)
                # 异步初始化将在首次使用时进行
                self._memory_initialized = False
            except Exception as e:
                print(f"记忆系统初始化失败: {e}")
                self.memory_system = None
                self._memory_initialized = False
        else:
            self.memory_system = None
            self._memory_initialized = False
    
    async def process_query(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> SystemResponse:
        """
        处理用户查询 - 系统主要接口
        
        对应设计文档的完整处理流程：
        感知层 -> 认知层 -> 行为层 -> 输出
        
        Args:
            query: 用户查询
            user_id: 用户ID
            context: 额外上下文信息
            
        Returns:
            SystemResponse: 完整的系统响应
        """
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        context = context or {}
        processing_metadata = {
            'query': query,
            'user_id': user_id,
            'timestamp': self._get_timestamp(),
            'processing_steps': []
        }
        
        try:
            # ==================== 记忆系统初始化 ====================
            if self.memory_system and not self._memory_initialized:
                await self.memory_system.initialize()
                self._memory_initialized = True
                processing_metadata['processing_steps'].append('memory_initialized')
            
            # ==================== 感知层处理 ====================
            processing_metadata['processing_steps'].append('perception_start')
            
            # 1.1 用户建模 - 结合记忆系统的用户数据
            user_profile = self.user_modeler.get_user_profile(user_id)
            if not user_profile:
                # 为新用户创建初始画像
                initial_data = self._extract_initial_user_data(query, context)
                
                # 从记忆系统获取用户历史数据
                if self.memory_system:
                    user_context = create_user_context(user_id)
                    user_memories = await self.memory_system.get_user_memories(user_context, limit=50)
                    initial_data['memory_context'] = user_memories.memories
                
                user_profile = self.user_modeler.create_user_profile(user_id, initial_data)
            
            # 1.2 情境分析
            enhanced_context = {**context, 'user_profile': user_profile}
            context_profile = self.context_analyzer.analyze_context(query, enhanced_context)
            
            processing_metadata['processing_steps'].append('perception_complete')
            
            # ==================== 认知层处理 ====================
            processing_metadata['processing_steps'].append('cognition_start')
            
            # 2.0 记忆检索 - 从外部记忆系统获取相关记忆
            relevant_memories = []
            if self.memory_system:
                user_context = create_user_context(user_id, context.get('session_id'))
                memory_query = MemoryQuery(
                    query=query,
                    user_context=user_context,
                    limit=20,
                    similarity_threshold=0.6
                )
                memory_result = await self.memory_system.search_memories(memory_query)
                relevant_memories = memory_result.memories
                processing_metadata['processing_steps'].append('memory_retrieved')
            
            # 2.1 多层次记忆激活 - 整合外部记忆和内部激活
            cognitive_context = {
                'user_profile': user_profile,
                'context_profile': context_profile,
                'external_memories': relevant_memories,
                **enhanced_context
            }
            activation_results = self.memory_activator.activate_comprehensive_memories(query, cognitive_context)
            
            # 2.2 语义补充
            all_fragments = []
            for result in activation_results:
                all_fragments.extend(result.fragments)
            
            # 添加外部记忆作为片段
            for memory in relevant_memories:
                # 转换记忆为记忆片段格式
                fragment = self._convert_memory_to_fragment(memory)
                if fragment:
                    all_fragments.append(fragment)
            
            semantic_result = self.semantic_enhancer.enhance_comprehensive_semantics(
                all_fragments, cognitive_context
            )
            
            # 2.3 类比推理
            analogy_result = self.analogy_reasoner.comprehensive_analogy_reasoning(query, cognitive_context)
            
            processing_metadata['processing_steps'].append('cognition_complete')
            
            # ==================== 行为层处理 ====================
            processing_metadata['processing_steps'].append('behavior_start')
            
            # 3.1 个性化适配
            adapted_output = self.adaptive_output.comprehensive_adaptation(
                semantic_result.enhanced_fragments,
                user_profile,
                cognitive_context
            )
            
            processing_metadata['processing_steps'].append('behavior_complete')
            
            # ==================== 协作层处理 (TODO) ====================
            # 4.1 辩证视角生成
            # 4.2 认知挑战适应
            # 4.3 交互式思维可视化
            
            # ==================== 响应构建 ====================
            response = SystemResponse(
                content=adapted_output.content,
                user_profile=user_profile,
                context_profile=context_profile,
                activated_memories=activation_results,
                semantic_enhancement=semantic_result,
                analogy_reasoning=analogy_result,
                adaptation_info=adapted_output,
                processing_metadata=processing_metadata
            )
            
            # ==================== 记忆保存 ====================
            if self.memory_system:
                try:
                    # 保存用户查询
                    user_context = create_user_context(user_id, context.get('session_id'))
                    
                    query_memory = create_memory_entry(
                        content=f"用户查询: {query}",
                        memory_type=MemoryType.EPISODIC,
                        user_context=user_context,
                        metadata={
                            "type": "user_query",
                            "context_profile": context_profile.__dict__ if context_profile else {},
                            "processing_metadata": processing_metadata
                        }
                    )
                    await self.memory_system.add_memory(query_memory)
                    
                    # 保存系统响应
                    response_memory = create_memory_entry(
                        content=f"系统响应: {response.content}",
                        memory_type=MemoryType.EPISODIC,
                        user_context=user_context,
                        metadata={
                            "type": "system_response",
                            "adaptation_info": adapted_output.__dict__,
                            "activated_memories_count": len(relevant_memories)
                        }
                    )
                    await self.memory_system.add_memory(response_memory)
                    
                    # 保存重要的语义增强结果
                    if semantic_result and hasattr(semantic_result, 'enhanced_fragments'):
                        for fragment in semantic_result.enhanced_fragments[:5]:  # 只保存前5个重要片段
                            semantic_memory = create_memory_entry(
                                content=f"语义增强: {fragment.content if hasattr(fragment, 'content') else str(fragment)}",
                                memory_type=MemoryType.SEMANTIC,
                                user_context=user_context,
                                metadata={
                                    "type": "semantic_enhancement",
                                    "query": query,
                                    "confidence": getattr(fragment, 'confidence', 0.8)
                                }
                            )
                            await self.memory_system.add_memory(semantic_memory)
                    
                    processing_metadata['processing_steps'].append('memory_saved')
                    
                except Exception as e:
                    print(f"保存记忆失败: {e}")
                    processing_metadata['memory_save_error'] = str(e)
            
            # 更新用户画像
            self._update_user_profile(user_id, query, response)
            
            # 记录会话历史
            self.session_history.append({
                'query': query,
                'response': response,
                'timestamp': processing_metadata['timestamp']
            })
            
            return response
            
        except Exception as e:
            processing_metadata['error'] = str(e)
            processing_metadata['processing_steps'].append('error')
            raise RuntimeError(f"System processing failed: {e}")
    
    def _extract_initial_user_data(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """从查询和上下文中提取初始用户数据"""
        # TODO: 实现更智能的用户数据提取
        return {
            'initial_query': query,
            'context': context,
            'inferred_domains': self._infer_domains_from_query(query),
            'cognitive_style': 'linear'  # 默认值
        }
    
    def _infer_domains_from_query(self, query: str) -> List[str]:
        """从查询中推断涉及的领域"""
        # TODO: 实现基于NLP的领域识别
        return ['general']
    
    def _update_user_profile(self, user_id: str, query: str, response: SystemResponse):
        """更新用户画像"""
        interaction_data = {
            'query': query,
            'response_quality': self._assess_response_quality(response),
            'cognitive_load': response.adaptation_info.cognitive_load,
            'processing_time': self._calculate_processing_time(response.processing_metadata),
            'domains': self._extract_domains_from_response(response)
        }
        
        self.user_modeler.update_user_profile(user_id, interaction_data)
    
    def _assess_response_quality(self, response: SystemResponse) -> float:
        """评估响应质量"""
        # TODO: 实现响应质量评估算法
        return 0.8
    
    def _calculate_processing_time(self, metadata: Dict[str, Any]) -> float:
        """计算处理时间"""
        # TODO: 实现处理时间计算
        return 1.0
    
    def _extract_domains_from_response(self, response: SystemResponse) -> List[str]:
        """从响应中提取涉及的领域"""
        # TODO: 分析响应内容涉及的知识领域
        return ['general']
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _convert_memory_to_fragment(self, memory: MemoryEntry):
        """将外部记忆转换为内部记忆片段格式"""
        try:
            # 创建简化的记忆片段
            # 这里需要根据实际的MemoryFragment结构进行调整
            fragment = type('MemoryFragment', (), {
                'content': memory.content,
                'confidence': memory.confidence,
                'source': 'external_memory',
                'memory_type': memory.memory_type.value,
                'timestamp': memory.timestamp,
                'metadata': memory.metadata or {}
            })()
            
            return fragment
            
        except Exception as e:
            print(f"转换记忆片段失败: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            'initialized': self.is_initialized,
            'session_count': len(self.session_history),
            'user_count': len(self.user_modeler.user_profiles),
            'config': self.config
        }
        
        # 添加记忆系统状态
        if self.memory_system:
            status['memory_system'] = self.memory_system.get_system_info()
            status['memory_initialized'] = self._memory_initialized
        else:
            status['memory_system'] = None
            status['memory_initialized'] = False
        
        return status
    
    def reset_session(self):
        """重置会话"""
        self.session_history.clear()
    
    def export_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """导出用户画像"""
        profile = self.user_modeler.get_user_profile(user_id)
        if profile:
            return {
                'user_id': profile.user_id,
                'cognitive': {
                    'thinking_mode': profile.cognitive.thinking_mode.value,
                    'cognitive_complexity': profile.cognitive.cognitive_complexity,
                    'abstraction_level': profile.cognitive.abstraction_level,
                    'creativity_tendency': profile.cognitive.creativity_tendency
                },
                'knowledge': {
                    'core_domains': profile.knowledge.core_domains,
                    'edge_domains': profile.knowledge.edge_domains,
                    'knowledge_depth': profile.knowledge.knowledge_depth
                },
                'interaction': {
                    'cognitive_style': profile.interaction.cognitive_style.value,
                    'information_density_preference': profile.interaction.information_density_preference,
                    'processing_speed': profile.interaction.processing_speed
                },
                'created_at': profile.created_at,
                'updated_at': profile.updated_at
            }
        return None


class SystemFactory:
    """系统工厂类 - 用于创建和配置系统实例"""
    
    @staticmethod
    def create_default_system(memory_config: Optional[MemorySystemConfig] = None) -> MemoryCognitiveSystem:
        """创建默认配置的系统"""
        default_config = {
            'memory_activation': {
                'surface_weight': 0.3,
                'deep_weight': 0.4,
                'meta_weight': 0.3
            },
            'semantic_enhancement': {
                'gap_identification_threshold': 0.5,
                'bridge_confidence_threshold': 0.6
            },
            'adaptive_output': {
                'default_density': 'medium',
                'default_granularity': 'meso'
            }
        }
        
        return MemoryCognitiveSystem(default_config, memory_config)
    
    @staticmethod
    def create_system_from_config(config_path: str) -> MemoryCognitiveSystem:
        """从配置文件创建系统"""
        # TODO: 实现配置文件加载
        return SystemFactory.create_default_system()
    
    @staticmethod
    def create_educational_system(memory_config: Optional[MemorySystemConfig] = None) -> MemoryCognitiveSystem:
        """创建教育场景特化的系统"""
        educational_config = {
            'memory_activation': {
                'surface_weight': 0.2,
                'deep_weight': 0.5,
                'meta_weight': 0.3
            },
            'semantic_enhancement': {
                'gap_identification_threshold': 0.3,  # 更低阈值，更积极补充
                'bridge_confidence_threshold': 0.5
            },
            'adaptive_output': {
                'default_density': 'low',  # 教育场景偏好低密度
                'default_granularity': 'macro'  # 从宏观开始
            },
            'collaboration': {
                'enable_dialectical_perspective': True,
                'enable_cognitive_challenge': True
            }
        }
        
        return MemoryCognitiveSystem(educational_config, memory_config)
    
    @staticmethod
    def create_research_system(memory_config: Optional[MemorySystemConfig] = None) -> MemoryCognitiveSystem:
        """创建研究场景特化的系统"""
        research_config = {
            'memory_activation': {
                'surface_weight': 0.2,
                'deep_weight': 0.6,
                'meta_weight': 0.2
            },
            'semantic_enhancement': {
                'gap_identification_threshold': 0.4,
                'bridge_confidence_threshold': 0.7
            },
            'adaptive_output': {
                'default_density': 'high',  # 研究场景需要高密度信息
                'default_granularity': 'micro'  # 关注细节
            },
            'analogy_reasoning': {
                'enable_creative_associations': True,
                'cross_domain_weight': 0.8
            }
        }
        
        return MemoryCognitiveSystem(research_config, memory_config)