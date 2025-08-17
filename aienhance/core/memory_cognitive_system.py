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
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化系统
        
        Args:
            config: 系统配置参数
        """
        self.config = config or {}
        
        # 初始化各层模块
        self._initialize_perception_layer()
        self._initialize_cognition_layer()
        self._initialize_behavior_layer()
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
    
    def process_query(self, query: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> SystemResponse:
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
            # ==================== 感知层处理 ====================
            processing_metadata['processing_steps'].append('perception_start')
            
            # 1.1 用户建模
            user_profile = self.user_modeler.get_user_profile(user_id)
            if not user_profile:
                # 为新用户创建初始画像
                initial_data = self._extract_initial_user_data(query, context)
                user_profile = self.user_modeler.create_user_profile(user_id, initial_data)
            
            # 1.2 情境分析
            enhanced_context = {**context, 'user_profile': user_profile}
            context_profile = self.context_analyzer.analyze_context(query, enhanced_context)
            
            processing_metadata['processing_steps'].append('perception_complete')
            
            # ==================== 认知层处理 ====================
            processing_metadata['processing_steps'].append('cognition_start')
            
            # 2.1 多层次记忆激活
            cognitive_context = {
                'user_profile': user_profile,
                'context_profile': context_profile,
                **enhanced_context
            }
            activation_results = self.memory_activator.activate_comprehensive_memories(query, cognitive_context)
            
            # 2.2 语义补充
            all_fragments = []
            for result in activation_results:
                all_fragments.extend(result.fragments)
            
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'initialized': self.is_initialized,
            'session_count': len(self.session_history),
            'user_count': len(self.user_modeler.user_profiles),
            'config': self.config
        }
    
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
    def create_default_system() -> MemoryCognitiveSystem:
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
        
        return MemoryCognitiveSystem(default_config)
    
    @staticmethod
    def create_system_from_config(config_path: str) -> MemoryCognitiveSystem:
        """从配置文件创建系统"""
        # TODO: 实现配置文件加载
        return SystemFactory.create_default_system()
    
    @staticmethod
    def create_educational_system() -> MemoryCognitiveSystem:
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
        
        return MemoryCognitiveSystem(educational_config)
    
    @staticmethod
    def create_research_system() -> MemoryCognitiveSystem:
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
        
        return MemoryCognitiveSystem(research_config)