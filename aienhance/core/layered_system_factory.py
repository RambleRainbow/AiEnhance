"""
分层系统工厂
提供便捷的分层认知系统创建方法
"""

from typing import Dict, Optional, Any, List
from .layered_cognitive_system import LayeredCognitiveSystem
from ..memory.interfaces import MemorySystemConfig, MemorySystemFactory
from ..llm.interfaces import ModelConfig, LLMProviderFactory
import logging

logger = logging.getLogger(__name__)


class LayeredSystemFactory:
    """分层系统工厂类"""
    
    @staticmethod
    def create_layered_system(
        config: Optional[Dict[str, Any]] = None,
        memory_config: Optional[MemorySystemConfig] = None,
        llm_config: Optional[ModelConfig] = None
    ) -> LayeredCognitiveSystem:
        """
        创建分层认知系统
        
        Args:
            config: 系统配置
            memory_config: 记忆系统配置
            llm_config: LLM配置
            
        Returns:
            LayeredCognitiveSystem: 分层认知系统实例
        """
        try:
            # 创建LLM提供商（先创建，用于记忆系统）
            llm_provider = None
            if llm_config:
                try:
                    llm_provider = LLMProviderFactory.create_provider(llm_config)
                    logger.info("LLM provider created successfully")
                except Exception as e:
                    logger.warning(f"Failed to create LLM provider: {e}")
            
            # 创建记忆系统（传递LLM提供商）
            memory_system = None
            if memory_config:
                try:
                    memory_system = MemorySystemFactory.create_memory_system(memory_config, llm_provider)
                    logger.info("Memory system created successfully")
                except Exception as e:
                    logger.warning(f"Failed to create memory system: {e}")
            
            # 创建分层认知系统
            system = LayeredCognitiveSystem(
                config=config,
                memory_system=memory_system,
                llm_provider=llm_provider
            )
            
            logger.info("Layered cognitive system created successfully")
            return system
            
        except Exception as e:
            logger.error(f"Failed to create layered system: {e}")
            raise
    
    @staticmethod
    def create_educational_layered_system(
        memory_config: Optional[MemorySystemConfig] = None,
        llm_config: Optional[ModelConfig] = None
    ) -> LayeredCognitiveSystem:
        """
        创建教育场景特化的分层系统
        
        Args:
            memory_config: 记忆系统配置
            llm_config: LLM配置
            
        Returns:
            LayeredCognitiveSystem: 教育特化的分层认知系统
        """
        educational_config = {
            'system_type': 'educational',
            'enable_collaboration': True,
            'perception': {
                'user_adaptation_weight': 0.8,  # 更重视用户适配
                'domain_analysis_enabled': True
            },
            'cognition': {
                'memory_activation': {
                    'surface_weight': 0.2,
                    'deep_weight': 0.5,
                    'meta_weight': 0.3
                },
                'semantic_enhancement': {
                    'gap_identification_threshold': 0.3,  # 更低阈值，更积极补充
                    'bridge_confidence_threshold': 0.5
                }
            },
            'behavior': {
                'adaptive_output': {
                    'default_density': 'low',  # 教育场景偏好低密度
                    'default_granularity': 'macro',  # 从宏观开始
                    'personalization_weight': 0.9
                }
            },
            'collaboration': {
                'enable_dialectical_perspective': True,
                'enable_cognitive_challenge': True,
                'challenge_intensity_multiplier': 0.8  # 适度挑战
            }
        }
        
        return LayeredSystemFactory.create_layered_system(
            educational_config, memory_config, llm_config
        )
    
    @staticmethod
    def create_research_layered_system(
        memory_config: Optional[MemorySystemConfig] = None,
        llm_config: Optional[ModelConfig] = None
    ) -> LayeredCognitiveSystem:
        """
        创建研究场景特化的分层系统
        
        Args:
            memory_config: 记忆系统配置
            llm_config: LLM配置
            
        Returns:
            LayeredCognitiveSystem: 研究特化的分层认知系统
        """
        research_config = {
            'system_type': 'research',
            'enable_collaboration': True,
            'perception': {
                'domain_depth_analysis': True,
                'interdisciplinary_detection': True
            },
            'cognition': {
                'memory_activation': {
                    'surface_weight': 0.2,
                    'deep_weight': 0.6,
                    'meta_weight': 0.2
                },
                'semantic_enhancement': {
                    'gap_identification_threshold': 0.4,
                    'bridge_confidence_threshold': 0.7
                },
                'analogy_reasoning': {
                    'enable_creative_associations': True,
                    'cross_domain_weight': 0.8
                }
            },
            'behavior': {
                'adaptive_output': {
                    'default_density': 'high',  # 研究场景需要高密度信息
                    'default_granularity': 'micro',  # 关注细节
                    'depth_enhancement': True
                }
            },
            'collaboration': {
                'enable_dialectical_perspective': True,
                'enable_cognitive_challenge': True,
                'perspective_diversity_weight': 0.9,
                'challenge_intensity_multiplier': 1.2  # 高强度挑战
            }
        }
        
        return LayeredSystemFactory.create_layered_system(
            research_config, memory_config, llm_config
        )
    
    @staticmethod
    def create_creative_layered_system(
        memory_config: Optional[MemorySystemConfig] = None,
        llm_config: Optional[ModelConfig] = None
    ) -> LayeredCognitiveSystem:
        """
        创建创意场景特化的分层系统
        
        Args:
            memory_config: 记忆系统配置
            llm_config: LLM配置
            
        Returns:
            LayeredCognitiveSystem: 创意特化的分层认知系统
        """
        creative_config = {
            'system_type': 'creative',
            'enable_collaboration': True,
            'perception': {
                'creativity_bias': 0.8,
                'open_ended_preference': True
            },
            'cognition': {
                'memory_activation': {
                    'surface_weight': 0.3,
                    'deep_weight': 0.3,
                    'meta_weight': 0.4  # 更重视元认知
                },
                'semantic_enhancement': {
                    'creative_gap_filling': True,
                    'unconventional_bridges': True
                },
                'analogy_reasoning': {
                    'enable_creative_associations': True,
                    'cross_domain_weight': 0.9,
                    'novelty_bias': 0.8
                }
            },
            'behavior': {
                'adaptive_output': {
                    'default_density': 'medium',
                    'default_granularity': 'meso',
                    'creativity_enhancement': True
                }
            },
            'collaboration': {
                'enable_dialectical_perspective': True,
                'enable_cognitive_challenge': True,
                'perspective_novelty_weight': 0.9,
                'challenge_creativity_bias': 0.8
            }
        }
        
        return LayeredSystemFactory.create_layered_system(
            creative_config, memory_config, llm_config
        )
    
    @staticmethod
    def create_lightweight_layered_system(
        llm_config: Optional[ModelConfig] = None
    ) -> LayeredCognitiveSystem:
        """
        创建轻量级分层系统（仅核心功能）
        
        Args:
            llm_config: LLM配置
            
        Returns:
            LayeredCognitiveSystem: 轻量级分层认知系统
        """
        lightweight_config = {
            'system_type': 'lightweight',
            'enable_collaboration': False,  # 禁用协作层
            'perception': {
                'basic_user_modeling': True,
                'simple_context_analysis': True
            },
            'cognition': {
                'memory_activation': {
                    'surface_weight': 0.5,
                    'deep_weight': 0.3,
                    'meta_weight': 0.2
                },
                'semantic_enhancement': {
                    'basic_gap_filling': True
                },
                'analogy_reasoning': {
                    'simple_analogies': True
                }
            },
            'behavior': {
                'adaptive_output': {
                    'default_density': 'medium',
                    'default_granularity': 'meso',
                    'basic_adaptation': True
                }
            }
        }
        
        return LayeredSystemFactory.create_layered_system(
            lightweight_config, None, llm_config  # 不使用记忆系统
        )
    
    @staticmethod
    def create_from_enhanced_factory_config(
        system_type: str = "educational",
        memory_system_type: str = "mirix_unified", 
        llm_provider: str = "ollama",
        llm_model_name: str = "qwen3:8b",
        **kwargs
    ) -> LayeredCognitiveSystem:
        """
        从增强工厂配置创建分层系统（兼容现有API）
        
        Args:
            system_type: 系统类型
            memory_system_type: 记忆系统类型
            llm_provider: LLM提供商
            llm_model_name: LLM模型名称
            **kwargs: 其他配置参数
            
        Returns:
            LayeredCognitiveSystem: 分层认知系统
        """
        try:
            # 构建记忆系统配置
            memory_config = None
            if memory_system_type:
                memory_config = MemorySystemConfig(system_type=memory_system_type)
            
            # 构建LLM配置
            llm_config = None
            if llm_provider and llm_model_name:
                from ..llm.interfaces import create_model_config
                llm_config = create_model_config(
                    provider=llm_provider,
                    model_name=llm_model_name,
                    api_base=kwargs.get('llm_api_base'),
                    api_key=kwargs.get('llm_api_key'),
                    temperature=kwargs.get('llm_temperature', 0.7),
                    max_tokens=kwargs.get('llm_max_tokens', 800)
                )
            
            # 根据系统类型选择创建方法
            if system_type == "educational":
                return LayeredSystemFactory.create_educational_layered_system(
                    memory_config, llm_config
                )
            elif system_type == "research":
                return LayeredSystemFactory.create_research_layered_system(
                    memory_config, llm_config
                )
            elif system_type == "creative":
                return LayeredSystemFactory.create_creative_layered_system(
                    memory_config, llm_config
                )
            elif system_type == "lightweight":
                return LayeredSystemFactory.create_lightweight_layered_system(
                    llm_config
                )
            else:
                # 默认创建基础系统
                return LayeredSystemFactory.create_layered_system(
                    {'system_type': system_type}, memory_config, llm_config
                )
                
        except Exception as e:
            logger.error(f"Failed to create layered system from enhanced factory config: {e}")
            raise
    
    @staticmethod
    def get_available_system_types() -> List[str]:
        """获取可用的系统类型"""
        return [
            'educational',
            'research', 
            'creative',
            'lightweight',
            'default'
        ]
    
    @staticmethod
    def get_system_type_info(system_type: str) -> Dict[str, Any]:
        """获取系统类型信息"""
        system_info = {
            'educational': {
                'description': '教育场景特化系统，注重学习引导和认知挑战',
                'features': ['低密度信息输出', '渐进式解释', '认知挑战', '多元观点'],
                'collaboration_enabled': True,
                'use_cases': ['教学辅助', '学习指导', '知识传授']
            },
            'research': {
                'description': '研究场景特化系统，提供深度分析和跨领域关联',
                'features': ['高密度信息输出', '深度分析', '跨领域连接', '创新推理'],
                'collaboration_enabled': True,
                'use_cases': ['学术研究', '文献分析', '理论探索']
            },
            'creative': {
                'description': '创意场景特化系统，激发创新思维和发散联想',
                'features': ['创意激发', '发散思维', '跨领域类比', '新颖观点'],
                'collaboration_enabled': True,
                'use_cases': ['创意写作', '设计思考', '头脑风暴']
            },
            'lightweight': {
                'description': '轻量级系统，提供基础认知功能',
                'features': ['快速响应', '低资源消耗', '基础适配', '简化处理'],
                'collaboration_enabled': False,
                'use_cases': ['快速问答', '基础咨询', '简单任务']
            },
            'default': {
                'description': '默认通用系统，平衡各项功能',
                'features': ['通用功能', '中等复杂度', '标准适配', '全功能支持'],
                'collaboration_enabled': True,
                'use_cases': ['通用对话', '综合咨询', '多场景应用']
            }
        }
        
        return system_info.get(system_type, {
            'description': '未知系统类型',
            'features': [],
            'collaboration_enabled': False,
            'use_cases': []
        })