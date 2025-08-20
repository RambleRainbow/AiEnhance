"""
用户建模模块 - 对应设计文档第4.1节
构建多维度的动态用户画像，为实现个性化记忆激活提供基础
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class CognitiveStyle(Enum):
    """认知风格枚举"""
    LINEAR = "linear"  # 线性思维
    NETWORK = "network"  # 网状思维
    HIERARCHICAL = "hierarchical"  # 层次思维


class ThinkingMode(Enum):
    """思维模式枚举"""
    ANALYTICAL = "analytical"  # 分析型
    INTUITIVE = "intuitive"  # 直觉型
    CREATIVE = "creative"  # 创造型


@dataclass
class CognitiveProfile:
    """认知能力画像 - 对应设计文档第4.1.1节"""
    thinking_mode: ThinkingMode
    cognitive_complexity: float  # 认知复杂度评估 (0-1)
    abstraction_level: float  # 抽象思维能力 (0-1)
    creativity_tendency: float  # 创造性思维倾向 (0-1)
    reasoning_preference: str  # 推理偏好描述


@dataclass
class KnowledgeProfile:
    """知识结构画像 - 对应设计文档第4.1.2节"""
    core_domains: List[str]  # 核心专业领域
    edge_domains: List[str]  # 边缘接触领域
    knowledge_depth: Dict[str, float]  # 各领域知识深度 (0-1)
    cross_domain_ability: float  # 跨域知识连接能力 (0-1)
    knowledge_boundaries: List[str]  # 知识边界和盲点


@dataclass
class InteractionProfile:
    """交互模式画像 - 对应设计文档第4.1.3节"""
    cognitive_style: CognitiveStyle
    information_density_preference: float  # 信息密度偏好 (0-1)
    processing_speed: float  # 信息处理速度 (0-1)
    feedback_preference: str  # 反馈偏好
    learning_style: str  # 学习风格


@dataclass
class UserProfile:
    """完整用户画像"""
    user_id: str
    cognitive: CognitiveProfile
    knowledge: KnowledgeProfile
    interaction: InteractionProfile
    created_at: str
    updated_at: str


class UserModelingModule(ABC):
    """用户建模模块基类"""
    
    @abstractmethod
    def build_cognitive_profile(self, user_data: Dict[str, Any]) -> CognitiveProfile:
        """构建认知能力维度画像"""
        pass
    
    @abstractmethod
    def build_knowledge_profile(self, user_data: Dict[str, Any]) -> KnowledgeProfile:
        """构建知识结构维度画像"""
        pass
    
    @abstractmethod
    def build_interaction_profile(self, user_data: Dict[str, Any]) -> InteractionProfile:
        """构建交互模式维度画像"""
        pass
    
    @abstractmethod
    def update_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """动态更新用户画像"""
        pass


class CognitiveProfileBuilder(UserModelingModule):
    """认知能力画像构建器 - 实现设计文档第4.1.1节功能"""
    
    def build_cognitive_profile(self, user_data: Dict[str, Any]) -> CognitiveProfile:
        """
        评估用户的抽象思维能力、逻辑推理偏好、概念联想习惯等认知特征
        
        基于记忆数据和当前查询分析用户的认知特征
        """
        # 基于查询复杂度评估认知复杂度
        query_complexity = user_data.get('query_complexity', 0.5)
        complexity_evolution = user_data.get('complexity_evolution', 'stable_complexity')
        
        # 评估认知复杂度
        cognitive_complexity = query_complexity
        if complexity_evolution == 'increasing_complexity':
            cognitive_complexity = min(1.0, cognitive_complexity + 0.2)
        elif complexity_evolution == 'decreasing_complexity':
            cognitive_complexity = max(0.1, cognitive_complexity - 0.1)
        
        # 基于表达偏好推断思维模式
        expressed_preferences = user_data.get('expressed_preferences', [])
        thinking_mode = self._infer_thinking_mode(expressed_preferences, user_data)
        
        # 基于历史领域评估抽象水平
        historical_domains = user_data.get('historical_domains', {})
        abstraction_level = self._assess_abstraction_level(historical_domains, query_complexity)
        
        # 基于交互模式评估创造性倾向
        creativity_tendency = self._assess_creativity_tendency(user_data)
        
        # 推理偏好分析
        reasoning_preference = self._analyze_reasoning_preference(user_data)
        
        return CognitiveProfile(
            thinking_mode=thinking_mode,
            cognitive_complexity=cognitive_complexity,
            abstraction_level=abstraction_level,
            creativity_tendency=creativity_tendency,
            reasoning_preference=reasoning_preference
        )
    
    def _infer_thinking_mode(self, preferences: List[str], user_data: Dict[str, Any]) -> ThinkingMode:
        """基于偏好推断思维模式"""
        if 'step_by_step' in preferences:
            return ThinkingMode.ANALYTICAL
        elif 'example_based' in preferences:
            return ThinkingMode.INTUITIVE
        elif user_data.get('communication_style') == 'creative':
            return ThinkingMode.CREATIVE
        else:
            return ThinkingMode.ANALYTICAL
    
    def _assess_abstraction_level(self, domains: Dict[str, int], complexity: float) -> float:
        """评估抽象思维水平"""
        # 技术领域需要更高抽象思维
        tech_domains = ['artificial_intelligence', 'programming', 'data_science']
        tech_score = sum(domains.get(domain, 0) for domain in tech_domains)
        
        base_level = complexity
        if tech_score > 0:
            base_level += 0.3
        
        return min(1.0, base_level)
    
    def _assess_creativity_tendency(self, user_data: Dict[str, Any]) -> float:
        """评估创造性思维倾向"""
        communication_style = user_data.get('communication_style', 'direct')
        interaction_depth = user_data.get('interaction_depth_preference', 'light_engagement')
        
        creativity = 0.5  # 基础值
        
        if communication_style == 'verbose':
            creativity += 0.2
        if interaction_depth == 'deep_engagement':
            creativity += 0.2
        
        return min(1.0, creativity)
    
    def _analyze_reasoning_preference(self, user_data: Dict[str, Any]) -> str:
        """分析推理偏好"""
        preferences = user_data.get('expressed_preferences', [])
        
        if 'detailed_explanation' in preferences:
            return "演绎推理为主，偏好详细论证"
        elif 'example_based' in preferences:
            return "归纳推理为主，偏好实例说明"
        elif 'step_by_step' in preferences:
            return "逻辑推理为主，偏好步骤分解"
        else:
            return "混合推理模式"
    
    def build_knowledge_profile(self, user_data: Dict[str, Any]) -> KnowledgeProfile:
        """构建知识结构维度画像"""
        return KnowledgeProfile(
            core_domains=["general"],
            edge_domains=[],
            knowledge_depth={"general": 0.5},
            cross_domain_ability=0.5,
            knowledge_boundaries=[]
        )
    
    def build_interaction_profile(self, user_data: Dict[str, Any]) -> InteractionProfile:
        """构建交互模式维度画像"""
        return InteractionProfile(
            cognitive_style=CognitiveStyle.LINEAR,
            information_density_preference=0.5,
            processing_speed=0.5,
            feedback_preference="balanced",
            learning_style="visual"
        )
    
    def update_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """动态更新用户画像"""
        # TODO: 实现动态更新逻辑
        pass
    
    def analyze_thinking_patterns(self, dialogue_history: List[str]) -> Dict[str, float]:
        """分析用户思维模式"""
        # TODO: 分析问题表述方式、论证结构、概念使用习惯
        return {}
    
    def assess_cognitive_complexity(self, responses: List[str]) -> float:
        """评估认知复杂度"""
        # TODO: 分析处理多层次概念、理解抽象关系的表现
        return 0.0


class KnowledgeProfileBuilder(UserModelingModule):
    """知识结构画像构建器 - 实现设计文档第4.1.2节功能"""
    
    def build_knowledge_profile(self, user_data: Dict[str, Any]) -> KnowledgeProfile:
        """
        获取用户的专业背景、身份、能力等信息，分析经验深度、知识框架
        
        基于记忆数据和当前查询分析用户的知识结构特征
        """
        # 从历史领域分析核心专业领域
        historical_domains = user_data.get('historical_domains', {})
        core_domains = self._identify_core_domains(historical_domains, user_data)
        
        # 识别边缘接触领域
        edge_domains = self._identify_edge_domains(historical_domains, user_data)
        
        # 评估各领域知识深度
        knowledge_depth = self._assess_knowledge_depth(historical_domains, user_data)
        
        # 分析跨域知识连接能力
        cross_domain_ability = self._assess_cross_domain_ability(user_data)
        
        # 识别知识边界和盲点
        knowledge_boundaries = self._identify_knowledge_boundaries(user_data)
        
        return KnowledgeProfile(
            core_domains=core_domains,
            edge_domains=edge_domains,
            knowledge_depth=knowledge_depth,
            cross_domain_ability=cross_domain_ability,
            knowledge_boundaries=knowledge_boundaries
        )
    
    def _identify_core_domains(self, historical_domains: Dict[str, int], user_data: Dict[str, Any]) -> List[str]:
        """识别用户的核心专业领域"""
        core_domains = []
        
        # 基于历史查询频率识别核心领域
        if historical_domains:
            total_queries = sum(historical_domains.values())
            for domain, count in historical_domains.items():
                if count >= 3 or (total_queries > 0 and count / total_queries >= 0.3):
                    core_domains.append(domain)
        
        # 基于当前查询中的专业术语判断
        domain_indicators = user_data.get('domain_indicators', [])
        for domain in domain_indicators:
            if domain not in core_domains:
                core_domains.append(domain)
        
        # 如果没有明确的专业领域，标记为通用
        if not core_domains:
            core_domains = ["通用知识"]
            
        return core_domains
    
    def _identify_edge_domains(self, historical_domains: Dict[str, int], user_data: Dict[str, Any]) -> List[str]:
        """识别边缘接触领域"""
        edge_domains = []
        
        if historical_domains:
            total_queries = sum(historical_domains.values())
            for domain, count in historical_domains.items():
                # 有接触但不是核心领域的算作边缘领域
                if 1 <= count < 3 and (total_queries == 0 or count / total_queries < 0.3):
                    edge_domains.append(domain)
        
        return edge_domains
    
    def _assess_knowledge_depth(self, historical_domains: Dict[str, int], user_data: Dict[str, Any]) -> Dict[str, float]:
        """评估各领域知识深度"""
        knowledge_depth = {}
        
        # 基于查询复杂度和历史频率评估深度
        query_complexity = user_data.get('query_complexity', 0.5)
        
        for domain, count in historical_domains.items():
            # 基础深度基于查询频率
            base_depth = min(0.9, count * 0.1)
            
            # 根据查询复杂度调整
            adjusted_depth = base_depth + (query_complexity * 0.3)
            
            knowledge_depth[domain] = min(1.0, adjusted_depth)
        
        # 为当前查询涉及的领域设置深度
        domain_indicators = user_data.get('domain_indicators', [])
        for domain in domain_indicators:
            if domain not in knowledge_depth:
                knowledge_depth[domain] = query_complexity
        
        return knowledge_depth
    
    def _assess_cross_domain_ability(self, user_data: Dict[str, Any]) -> float:
        """评估跨域知识连接能力"""
        historical_domains = user_data.get('historical_domains', {})
        domain_count = len(historical_domains)
        
        # 基于涉及领域数量评估跨域能力
        cross_domain_base = min(0.8, domain_count * 0.15)
        
        # 基于查询复杂度调整
        query_complexity = user_data.get('query_complexity', 0.5)
        if query_complexity > 0.7:  # 复杂查询通常需要跨域思考
            cross_domain_base += 0.2
        
        return min(1.0, cross_domain_base)
    
    def _identify_knowledge_boundaries(self, user_data: Dict[str, Any]) -> List[str]:
        """识别知识边界和盲点"""
        boundaries = []
        
        # 基于用户未涉及的主要技术领域推断知识边界
        all_tech_domains = [
            'artificial_intelligence', 'programming', 'data_science', 
            'machine_learning', 'web_development', 'mobile_development',
            'database_systems', 'network_security', 'cloud_computing'
        ]
        
        historical_domains = user_data.get('historical_domains', {})
        covered_domains = set(historical_domains.keys())
        
        for domain in all_tech_domains:
            if domain not in covered_domains:
                boundaries.append(domain)
        
        # 限制边界列表长度
        return boundaries[:5]
    
    def build_cognitive_profile(self, user_data: Dict[str, Any]) -> CognitiveProfile:
        """构建认知能力维度画像"""
        return CognitiveProfile(
            thinking_mode=ThinkingMode.ANALYTICAL,
            cognitive_complexity=0.7,
            abstraction_level=0.6,
            creativity_tendency=0.5,
            reasoning_preference="演绎推理为主"
        )
    
    def build_interaction_profile(self, user_data: Dict[str, Any]) -> InteractionProfile:
        """构建交互模式维度画像"""
        return InteractionProfile(
            cognitive_style=CognitiveStyle.LINEAR,
            information_density_preference=0.5,
            processing_speed=0.5,
            feedback_preference="balanced",
            learning_style="visual"
        )
    
    def update_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """动态更新用户画像"""
        # TODO: 实现动态更新逻辑
        pass
    
    def map_domain_knowledge(self, interactions: List[Dict]) -> Dict[str, float]:
        """映射领域知识"""
        # TODO: 识别用户在不同知识领域的专业程度
        return {}
    
    def identify_knowledge_boundaries(self, feedback_data: List[Dict]) -> List[str]:
        """识别知识边界"""
        # TODO: 通过交互中的理解反馈，动态标记用户的知识边界和盲点
        return []


class InteractionProfileBuilder(UserModelingModule):
    """交互模式画像构建器 - 实现设计文档第4.1.3节功能"""
    
    def build_interaction_profile(self, user_data: Dict[str, Any]) -> InteractionProfile:
        """
        了解用户的思维节奏、信息接受偏好、认知负荷阈值
        
        基于记忆数据和当前查询分析用户的交互模式特征
        """
        # 分析认知风格
        cognitive_style = self._analyze_cognitive_style(user_data)
        
        # 评估信息密度偏好
        info_density_preference = self._assess_info_density_preference(user_data)
        
        # 评估信息处理速度
        processing_speed = self._assess_processing_speed(user_data)
        
        # 确定反馈偏好
        feedback_preference = self._determine_feedback_preference(user_data)
        
        # 识别学习风格
        learning_style = self._identify_learning_style(user_data)
        
        return InteractionProfile(
            cognitive_style=cognitive_style,
            information_density_preference=info_density_preference,
            processing_speed=processing_speed,
            feedback_preference=feedback_preference,
            learning_style=learning_style
        )
    
    def _analyze_cognitive_style(self, user_data: Dict[str, Any]) -> CognitiveStyle:
        """分析认知风格"""
        expressed_preferences = user_data.get('expressed_preferences', [])
        query_complexity = user_data.get('query_complexity', 0.5)
        interaction_depth = user_data.get('interaction_depth_preference', 'light_engagement')
        
        # 基于偏好和复杂度推断认知风格
        if 'step_by_step' in expressed_preferences:
            return CognitiveStyle.LINEAR
        elif query_complexity > 0.7 and interaction_depth == 'deep_engagement':
            return CognitiveStyle.NETWORK  # 复杂问题需要网状思维
        elif len(user_data.get('historical_domains', {})) > 3:
            return CognitiveStyle.HIERARCHICAL  # 多领域用户倾向层次思维
        else:
            return CognitiveStyle.LINEAR
    
    def _assess_info_density_preference(self, user_data: Dict[str, Any]) -> float:
        """评估信息密度偏好"""
        communication_style = user_data.get('communication_style', 'direct')
        expressed_preferences = user_data.get('expressed_preferences', [])
        query_complexity = user_data.get('query_complexity', 0.5)
        
        # 基础信息密度偏好
        density_preference = 0.5
        
        # 根据交流风格调整
        if communication_style == 'verbose':
            density_preference += 0.2  # 详细表达者喜欢高密度信息
        elif communication_style == 'direct':
            density_preference += 0.1  # 直接表达者适度偏好高密度
        
        # 根据明确偏好调整
        if 'detailed_explanation' in expressed_preferences:
            density_preference += 0.3
        elif 'simple_explanation' in expressed_preferences:
            density_preference -= 0.2
        
        # 根据查询复杂度调整
        if query_complexity > 0.7:
            density_preference += 0.1  # 复杂查询者通常能处理更高密度信息
        
        return min(1.0, max(0.1, density_preference))
    
    def _assess_processing_speed(self, user_data: Dict[str, Any]) -> float:
        """评估信息处理速度"""
        query_complexity = user_data.get('query_complexity', 0.5)
        memory_count = user_data.get('memory_count', 0)
        complexity_evolution = user_data.get('complexity_evolution', 'stable_complexity')
        
        # 基础处理速度
        processing_speed = 0.5
        
        # 基于查询复杂度调整
        processing_speed += query_complexity * 0.3
        
        # 基于历史记忆数量调整（经验丰富者处理速度更快）
        if memory_count > 20:
            processing_speed += 0.2
        elif memory_count > 10:
            processing_speed += 0.1
        
        # 基于复杂度演化趋势调整
        if complexity_evolution == 'increasing_complexity':
            processing_speed += 0.1  # 逐渐提高复杂度说明处理能力强
        
        return min(1.0, max(0.2, processing_speed))
    
    def _determine_feedback_preference(self, user_data: Dict[str, Any]) -> str:
        """确定反馈偏好"""
        expressed_preferences = user_data.get('expressed_preferences', [])
        communication_style = user_data.get('communication_style', 'direct')
        
        if 'detailed_explanation' in expressed_preferences:
            return "详细反馈"
        elif 'example_based' in expressed_preferences:
            return "示例导向反馈"
        elif communication_style == 'direct':
            return "简洁反馈"
        else:
            return "平衡反馈"
    
    def _identify_learning_style(self, user_data: Dict[str, Any]) -> str:
        """识别学习风格"""
        expressed_preferences = user_data.get('expressed_preferences', [])
        domain_indicators = user_data.get('domain_indicators', [])
        
        # 基于偏好识别学习风格
        if 'example_based' in expressed_preferences:
            return "实例学习"
        elif 'step_by_step' in expressed_preferences:
            return "结构化学习"
        elif any(domain in ['programming', 'data_science'] for domain in domain_indicators):
            return "实践导向学习"
        else:
            return "概念导向学习"
    
    def build_cognitive_profile(self, user_data: Dict[str, Any]) -> CognitiveProfile:
        """构建认知能力维度画像"""
        return CognitiveProfile(
            thinking_mode=ThinkingMode.ANALYTICAL,
            cognitive_complexity=0.7,
            abstraction_level=0.6,
            creativity_tendency=0.5,
            reasoning_preference="演绎推理为主"
        )
    
    def build_knowledge_profile(self, user_data: Dict[str, Any]) -> KnowledgeProfile:
        """构建知识结构维度画像"""
        return KnowledgeProfile(
            core_domains=["general"],
            edge_domains=[],
            knowledge_depth={"general": 0.5},
            cross_domain_ability=0.5,
            knowledge_boundaries=[]
        )
    
    def update_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """动态更新用户画像"""
        # TODO: 实现动态更新逻辑
        pass
    
    def monitor_processing_speed(self, response_times: List[float]) -> float:
        """监测信息处理速度"""
        # TODO: 监测用户对不同复杂度信息的响应时间和理解深度
        return 0.0
    
    def analyze_attention_patterns(self, interaction_log: List[Dict]) -> CognitiveStyle:
        """分析注意力模式"""
        # TODO: 识别用户是偏好深度聚焦还是广度扫描的注意力分配方式
        return CognitiveStyle.LINEAR


class DynamicUserModeler:
    """动态用户建模器 - 整合所有维度的用户画像"""
    
    def __init__(self):
        self.cognitive_builder = CognitiveProfileBuilder()
        self.knowledge_builder = KnowledgeProfileBuilder()
        self.interaction_builder = InteractionProfileBuilder()
        self.user_profiles: Dict[str, UserProfile] = {}
    
    def create_user_profile(self, user_id: str, initial_data: Dict[str, Any]) -> UserProfile:
        """
        创建完整的用户画像
        
        Args:
            user_id: 用户ID
            initial_data: 初始数据，包含：
                - query: 用户当前问句
                - memory_context: 从记忆系统获取的用户历史数据
                - session_context: 会话上下文信息
        """
        from datetime import datetime
        
        # 增强初始数据，包含记忆分析
        enhanced_data = self._enhance_with_memory_analysis(initial_data)
        
        cognitive = self.cognitive_builder.build_cognitive_profile(enhanced_data)
        knowledge = self.knowledge_builder.build_knowledge_profile(enhanced_data)
        interaction = self.interaction_builder.build_interaction_profile(enhanced_data)
        
        profile = UserProfile(
            user_id=user_id,
            cognitive=cognitive,
            knowledge=knowledge,
            interaction=interaction,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.user_profiles[user_id] = profile
        return profile
    
    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
        """动态更新用户画像"""
        if user_id not in self.user_profiles:
            return self.create_user_profile(user_id, interaction_data)
        
        # TODO: 实现增量更新逻辑
        profile = self.user_profiles[user_id]
        # 更新各个维度的画像
        profile.updated_at = ""  # TODO: 更新时间戳
        
        return profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        return self.user_profiles.get(user_id)
    
    def _enhance_with_memory_analysis(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于记忆数据增强用户信息分析
        
        Args:
            initial_data: 包含query和memory_context的初始数据
            
        Returns:
            增强后的用户数据，包含从记忆中提取的用户特征
        """
        enhanced_data = initial_data.copy()
        memory_context = initial_data.get('memory_context', [])
        current_query = initial_data.get('query', '')
        
        # 从当前问句中提取用户信息
        query_insights = self._extract_user_info_from_query(current_query)
        enhanced_data.update(query_insights)
        
        # 从历史记忆中分析用户特征
        if memory_context:
            memory_insights = self._analyze_memory_patterns(memory_context)
            enhanced_data.update(memory_insights)
        
        return enhanced_data
    
    def _extract_user_info_from_query(self, query: str) -> Dict[str, Any]:
        """
        从用户问句中提取用户信息和偏好
        
        分析用户的表达方式、询问类型、语言复杂度等
        """
        insights = {
            'query_complexity': self._assess_query_complexity(query),
            'expressed_preferences': self._extract_preferences(query),
            'domain_indicators': self._identify_domain_knowledge(query),
            'communication_style': self._analyze_communication_style(query)
        }
        return insights
    
    def _analyze_memory_patterns(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析用户的历史记忆模式，提取用户特征
        
        从用户的历史交互中分析：
        - 兴趣领域和专业背景
        - 认知偏好和思维模式
        - 交互习惯和信息密度偏好
        """
        if not memories:
            return {}
        
        # 分析查询历史中的领域分布
        query_memories = [m for m in memories if m.get('metadata', {}).get('type') == 'user_query']
        domain_pattern = self._extract_domain_pattern(query_memories)
        
        # 分析交互频率和深度
        interaction_pattern = self._analyze_interaction_depth(memories)
        
        # 分析表达复杂度变化趋势
        complexity_evolution = self._track_complexity_evolution(query_memories)
        
        return {
            'historical_domains': domain_pattern,
            'interaction_depth_preference': interaction_pattern,
            'complexity_evolution': complexity_evolution,
            'memory_count': len(memories)
        }
    
    def _assess_query_complexity(self, query: str) -> float:
        """评估查询复杂度 (0-1)"""
        # 基于句子长度、从句数量、专业词汇等评估
        words = query.split()
        word_count = len(words)
        
        # 简单的复杂度评估算法
        complexity = min(1.0, word_count / 50.0)  # 基础长度评估
        
        # 检查复杂句式
        complex_indicators = ['因为', '但是', '然而', '尽管', '虽然', '如果', '因此']
        if any(indicator in query for indicator in complex_indicators):
            complexity += 0.2
        
        # 检查专业术语（简化版）
        technical_terms = ['算法', '机器学习', '人工智能', '深度学习', '神经网络']
        if any(term in query for term in technical_terms):
            complexity += 0.3
            
        return min(1.0, complexity)
    
    def _extract_preferences(self, query: str) -> List[str]:
        """从查询中提取表达的偏好"""
        preferences = []
        
        # 检查明确的偏好表达
        if '简单' in query or '简明' in query:
            preferences.append('simple_explanation')
        if '详细' in query or '深入' in query:
            preferences.append('detailed_explanation')
        if '例子' in query or '举例' in query:
            preferences.append('example_based')
        if '步骤' in query or '流程' in query:
            preferences.append('step_by_step')
            
        return preferences
    
    def _identify_domain_knowledge(self, query: str) -> List[str]:
        """识别查询中体现的领域知识"""
        domains = []
        
        # 技术领域
        if any(term in query for term in ['编程', '代码', '算法', '数据结构']):
            domains.append('programming')
        if any(term in query for term in ['机器学习', 'AI', '人工智能', '深度学习']):
            domains.append('artificial_intelligence')
        if any(term in query for term in ['数据库', 'SQL', '数据分析']):
            domains.append('data_science')
            
        return domains
    
    def _analyze_communication_style(self, query: str) -> str:
        """分析交流风格"""
        if len(query) > 100:
            return 'verbose'
        elif '?' in query or '？' in query:
            return 'questioning'
        elif any(word in query for word in ['请', '麻烦', '谢谢']):
            return 'polite'
        else:
            return 'direct'
    
    def _extract_domain_pattern(self, query_memories: List[Dict[str, Any]]) -> Dict[str, int]:
        """从历史查询中提取领域模式"""
        domain_count = {}
        
        for memory in query_memories:
            content = memory.get('content', '')
            domains = self._identify_domain_knowledge(content)
            for domain in domains:
                domain_count[domain] = domain_count.get(domain, 0) + 1
                
        return domain_count
    
    def _analyze_interaction_depth(self, memories: List[Dict[str, Any]]) -> str:
        """分析交互深度偏好"""
        if len(memories) > 20:
            return 'deep_engagement'
        elif len(memories) > 5:
            return 'moderate_engagement'
        else:
            return 'light_engagement'
    
    def _track_complexity_evolution(self, query_memories: List[Dict[str, Any]]) -> str:
        """跟踪复杂度演化趋势"""
        if len(query_memories) < 3:
            return 'insufficient_data'
            
        complexities = [self._assess_query_complexity(m.get('content', '')) for m in query_memories[-5:]]
        
        if len(complexities) >= 2:
            trend = complexities[-1] - complexities[0]
            if trend > 0.2:
                return 'increasing_complexity'
            elif trend < -0.2:
                return 'decreasing_complexity'
        
        return 'stable_complexity'