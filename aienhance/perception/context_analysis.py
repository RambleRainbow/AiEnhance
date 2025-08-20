"""
情境分析模块 - 对应设计文档第4.2节
识别用户当前所处的任务场景和问题意图，为认知层的记忆激活提供方向性指导
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskType(Enum):
    """任务类型 - 对应设计文档第4.2.1节"""
    EXPLORATORY = "exploratory"  # 探索型任务
    ANALYTICAL = "analytical"  # 分析型任务
    CREATIVE = "creative"  # 创新型任务
    RETRIEVAL = "retrieval"  # 检索型任务


class TimeDimension(Enum):
    """时间维度"""
    HISTORICAL = "historical"  # 历史导向
    CURRENT = "current"  # 当前导向
    FUTURE = "future"  # 未来导向


class AbstractionLevel(Enum):
    """抽象层次"""
    OPERATIONAL = "operational"  # 操作层面
    CONCEPTUAL = "conceptual"  # 概念层面
    META = "meta"  # 元层面


class PurposeType(Enum):
    """目的类型"""
    UNDERSTANDING = "understanding"  # 理解型需求
    APPLICATION = "application"  # 应用型需求
    VERIFICATION = "verification"  # 验证型思考
    EXPLORATION = "exploration"  # 探索型思考


@dataclass
class TaskCharacteristics:
    """任务特征 - 对应设计文档第4.2.1节"""
    task_type: TaskType
    openness_level: float  # 开放性程度 (0-1)
    structure_requirement: float  # 结构化需求 (0-1)
    creativity_requirement: float  # 创造性需求 (0-1)
    cross_domain_level: float  # 跨领域程度 (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可JSON序列化的字典"""
        return {
            "task_type": self.task_type.value if self.task_type else None,
            "openness_level": self.openness_level,
            "structure_requirement": self.structure_requirement,
            "creativity_requirement": self.creativity_requirement,
            "cross_domain_level": self.cross_domain_level
        }


@dataclass
class ContextualElements:
    """情境要素 - 对应设计文档第4.2.2节"""
    time_dimension: TimeDimension
    domain_scope: List[str]  # 涉及的领域范围
    abstraction_level: AbstractionLevel
    purpose_type: PurposeType
    urgency_level: float  # 时效性要求 (0-1)
    complexity_level: float  # 复杂度 (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可JSON序列化的字典"""
        return {
            "time_dimension": self.time_dimension.value if self.time_dimension else None,
            "domain_scope": self.domain_scope,
            "abstraction_level": self.abstraction_level.value if self.abstraction_level else None,
            "purpose_type": self.purpose_type.value if self.purpose_type else None,
            "urgency_level": self.urgency_level,
            "complexity_level": self.complexity_level
        }


@dataclass
class CognitiveNeeds:
    """认知需求 - 对应设计文档第4.2.3节"""
    knowledge_supplement: List[str]  # 知识补充需求
    thinking_framework: List[str]  # 思维框架需求
    creativity_stimulation: List[str]  # 创意激发需求
    support_priority: float  # 支持优先级 (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可JSON序列化的字典"""
        return {
            "knowledge_supplement": self.knowledge_supplement,
            "thinking_framework": self.thinking_framework,
            "creativity_stimulation": self.creativity_stimulation,
            "support_priority": self.support_priority
        }


@dataclass
class ContextProfile:
    """完整情境画像"""
    task_characteristics: TaskCharacteristics
    contextual_elements: ContextualElements
    cognitive_needs: CognitiveNeeds
    confidence_score: float  # 分析置信度 (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可JSON序列化的字典"""
        return {
            "task_characteristics": self.task_characteristics.to_dict() if self.task_characteristics else None,
            "contextual_elements": self.contextual_elements.to_dict() if self.contextual_elements else None,
            "cognitive_needs": self.cognitive_needs.to_dict() if self.cognitive_needs else None,
            "confidence_score": self.confidence_score
        }


class ContextAnalysisModule(ABC):
    """情境分析模块基类"""
    
    @abstractmethod
    def identify_task_type(self, query: str, context: Dict[str, Any]) -> TaskCharacteristics:
        """识别任务类型和特征"""
        pass
    
    @abstractmethod
    def extract_contextual_elements(self, query: str, context: Dict[str, Any]) -> ContextualElements:
        """提取情境要素"""
        pass
    
    @abstractmethod
    def predict_cognitive_needs(self, task_characteristics: TaskCharacteristics, 
                              contextual_elements: ContextualElements) -> CognitiveNeeds:
        """预测认知需求"""
        pass


class TaskTypeIdentifier(ContextAnalysisModule):
    """任务类型识别器 - 实现设计文档第4.2.1节功能"""
    
    def identify_task_type(self, query: str, context: Dict[str, Any]) -> TaskCharacteristics:
        """
        识别用户任务的认知类型，为系统匹配合适的支持策略与资源提供任务导向基础
        
        基于用户画像和查询内容进行任务特征识别
        """
        # 获取用户画像信息
        user_profile = context.get('user_profile')
        
        task_type = self._classify_task_type(query, user_profile)
        
        return TaskCharacteristics(
            task_type=task_type,
            openness_level=self._assess_openness(query, user_profile),
            structure_requirement=self._assess_structure_need(query, user_profile),
            creativity_requirement=self._assess_creativity_need(query, user_profile),
            cross_domain_level=self._assess_cross_domain(query, user_profile)
        )
    
    def _classify_task_type(self, query: str, user_profile=None) -> TaskType:
        """分类任务类型"""
        # 基于查询关键词进行基础分类
        if any(keyword in query for keyword in ["如何看待", "可能有哪些", "有什么", "探索"]):
            return TaskType.EXPLORATORY
        elif any(keyword in query for keyword in ["分析", "比较", "原因", "评估"]):
            return TaskType.ANALYTICAL
        elif any(keyword in query for keyword in ["创新", "应用于", "结合", "设计"]):
            return TaskType.CREATIVE
        else:
            return TaskType.RETRIEVAL
    
    def _assess_openness(self, query: str, user_profile=None) -> float:
        """评估问题开放性"""
        openness = 0.5
        
        # 基于问句类型评估开放性
        if any(keyword in query for keyword in ["如何", "为什么", "可能"]):
            openness += 0.3
        elif "?" in query or "？" in query:
            openness += 0.2
        
        # 基于用户认知复杂度调整
        if user_profile and hasattr(user_profile, 'cognitive'):
            if user_profile.cognitive.cognitive_complexity > 0.7:
                openness += 0.1  # 高认知复杂度用户喜欢开放性问题
        
        return min(1.0, openness)
    
    def _assess_structure_need(self, query: str, user_profile=None) -> float:
        """评估结构化需求"""
        structure_need = 0.5
        
        # 基于查询关键词评估结构化需求
        if any(keyword in query for keyword in ["步骤", "流程", "框架", "系统"]):
            structure_need += 0.3
        
        # 基于用户思维模式调整
        if user_profile and hasattr(user_profile, 'cognitive'):
            if user_profile.cognitive.thinking_mode.value == 'analytical':
                structure_need += 0.2
        
        return min(1.0, structure_need)
    
    def _assess_creativity_need(self, query: str, user_profile=None) -> float:
        """评估创造性需求"""
        creativity_need = 0.3
        
        # 基于查询关键词评估创造性需求
        if any(keyword in query for keyword in ["创新", "创意", "新的", "独特"]):
            creativity_need += 0.4
        elif any(keyword in query for keyword in ["结合", "融合", "应用"]):
            creativity_need += 0.2
        
        # 基于用户创造性倾向调整
        if user_profile and hasattr(user_profile, 'cognitive'):
            creativity_need += user_profile.cognitive.creativity_tendency * 0.3
        
        return min(1.0, creativity_need)
    
    def _assess_cross_domain(self, query: str, user_profile=None) -> float:
        """评估跨领域程度"""
        cross_domain = 0.3
        
        # 基于查询关键词评估跨领域程度
        if any(keyword in query for keyword in ["结合", "应用于", "跨", "融合"]):
            cross_domain += 0.4
        
        # 基于用户知识结构调整
        if user_profile and hasattr(user_profile, 'knowledge'):
            cross_domain += user_profile.knowledge.cross_domain_ability * 0.3
        
        return min(1.0, cross_domain)
    
    def extract_contextual_elements(self, query: str, context: Dict[str, Any]) -> ContextualElements:
        """提取情境要素"""
        return ContextualElements(
            time_dimension=TimeDimension.CURRENT,
            domain_scope=["general"],
            abstraction_level=AbstractionLevel.MESO,
            purpose_type=PurposeType.UNDERSTANDING,
            stakeholder_complexity=0.5
        )
    
    def predict_cognitive_needs(self, task_characteristics: TaskCharacteristics, 
                              contextual_elements: ContextualElements) -> CognitiveNeeds:
        """预测认知需求"""
        return CognitiveNeeds(
            memory_activation_needs={
                "surface": 0.3,
                "deep": 0.4,
                "meta": 0.3
            },
            semantic_bridging_needs={
                "gap_identification": True,
                "concept_bridging": True,
                "knowledge_integration": True
            },
            analogical_reasoning_needs={
                "enable_analogy": True,
                "cross_domain_activation": 0.5,
                "creative_association": 0.3
            }
        )


class ContextualElementExtractor(ContextAnalysisModule):
    """情境要素提取器 - 实现设计文档第4.2.2节功能"""
    
    def extract_contextual_elements(self, query: str, context: Dict[str, Any]) -> ContextualElements:
        """
        提取任务情境中的关键维度，构建问题理解框架
        
        基于用户画像和查询内容进行情境要素分析
        """
        user_profile = context.get('user_profile')
        
        return ContextualElements(
            time_dimension=self._analyze_time_dimension(query),
            domain_scope=self._analyze_domain_scope(query, user_profile),
            abstraction_level=self._analyze_abstraction_level(query, user_profile),
            purpose_type=self._analyze_purpose_type(query, user_profile),
            urgency_level=self._assess_urgency(query, context),
            complexity_level=self._assess_complexity(query, user_profile)
        )
    
    def _analyze_time_dimension(self, query: str) -> TimeDimension:
        """分析时间维度"""
        # TODO: 判断任务是否与特定时间窗口紧密相关
        # 历史背景相关性、未来导向程度
        
        if any(keyword in query for keyword in ["历史", "过去", "发展过程"]):
            return TimeDimension.HISTORICAL
        elif any(keyword in query for keyword in ["未来", "预测", "规划"]):
            return TimeDimension.FUTURE
        else:
            return TimeDimension.CURRENT
    
    def _analyze_domain_scope(self, query: str, user_profile=None) -> List[str]:
        """分析领域范围"""
        domains = ["通用"]
        
        # 从用户画像中获取领域信息
        if user_profile and hasattr(user_profile, 'knowledge'):
            if user_profile.knowledge.core_domains:
                domains = user_profile.knowledge.core_domains.copy()
        
        # 基于查询内容补充领域
        if any(term in query for term in ['编程', '代码', '算法']):
            if 'programming' not in domains:
                domains.append('programming')
        elif any(term in query for term in ['AI', '机器学习', '深度学习']):
            if 'artificial_intelligence' not in domains:
                domains.append('artificial_intelligence')
        
        return domains
    
    def _analyze_abstraction_level(self, query: str, user_profile=None) -> AbstractionLevel:
        """分析抽象层次"""
        # 基于查询关键词判断抽象层次
        if any(keyword in query for keyword in ["具体", "步骤", "操作", "实现"]):
            return AbstractionLevel.OPERATIONAL
        elif any(keyword in query for keyword in ["理论", "框架", "模型", "原理"]):
            return AbstractionLevel.META
        else:
            # 基于用户抽象思维能力调整
            if user_profile and hasattr(user_profile, 'cognitive'):
                if user_profile.cognitive.abstraction_level > 0.7:
                    return AbstractionLevel.META
            return AbstractionLevel.CONCEPTUAL
    
    def _analyze_purpose_type(self, query: str, user_profile=None) -> PurposeType:
        """分析目的类型"""
        if any(keyword in query for keyword in ["如何", "怎么", "实现", "应用"]):
            return PurposeType.APPLICATION
        elif any(keyword in query for keyword in ["验证", "检查", "测试"]):
            return PurposeType.VERIFICATION
        elif any(keyword in query for keyword in ["探索", "发现", "可能"]):
            return PurposeType.EXPLORATION
        else:
            return PurposeType.UNDERSTANDING
    
    def _assess_urgency(self, query: str, context: Dict[str, Any]) -> float:
        """评估时效性要求"""
        urgency = 0.5
        
        # 基于查询关键词判断紧急性
        if any(keyword in query for keyword in ["紧急", "立即", "马上", "急需"]):
            urgency += 0.4
        elif any(keyword in query for keyword in ["快速", "尽快"]):
            urgency += 0.2
        
        return min(1.0, urgency)
    
    def _assess_complexity(self, query: str, user_profile=None) -> float:
        """评估复杂度"""
        # 基于查询长度和专业术语评估复杂度
        words = query.split()
        complexity = min(0.8, len(words) / 30.0)
        
        # 基于专业术语增加复杂度
        technical_terms = ['算法', '机器学习', '深度学习', '神经网络', '数据结构']
        if any(term in query for term in technical_terms):
            complexity += 0.3
        
        # 基于用户认知复杂度调整
        if user_profile and hasattr(user_profile, 'cognitive'):
            if user_profile.cognitive.cognitive_complexity > 0.7:
                complexity += 0.1  # 高认知用户能处理更复杂的任务
        
        return min(1.0, complexity)
    
    def identify_task_type(self, query: str, context: Dict[str, Any]) -> TaskCharacteristics:
        """识别任务类型和特征"""
        return TaskCharacteristics(
            task_type=TaskType.ANALYTICAL,
            openness_level=0.5,
            structure_need=0.5,
            creativity_need=0.5,
            cross_domain_degree=0.5
        )
    
    def predict_cognitive_needs(self, task_characteristics: TaskCharacteristics, 
                              contextual_elements: ContextualElements) -> CognitiveNeeds:
        """预测认知需求"""
        return CognitiveNeeds(
            memory_activation_needs={
                "surface": 0.3,
                "deep": 0.4,
                "meta": 0.3
            },
            semantic_bridging_needs={
                "gap_identification": True,
                "concept_bridging": True,
                "knowledge_integration": True
            },
            analogical_reasoning_needs={
                "enable_analogy": True,
                "cross_domain_activation": 0.5,
                "creative_association": 0.3
            }
        )


class CognitiveNeedsPredictor(ContextAnalysisModule):
    """认知需求预测器 - 实现设计文档第4.2.3节功能"""
    
    def predict_cognitive_needs(self, task_characteristics: TaskCharacteristics, 
                              contextual_elements: ContextualElements) -> CognitiveNeeds:
        """
        识别认知障碍，匹配支持资源，辅助用户高效理解与深度思考
        """
        knowledge_needs = self._predict_knowledge_supplement(task_characteristics, contextual_elements)
        framework_needs = self._predict_thinking_framework(task_characteristics, contextual_elements)
        creativity_needs = self._predict_creativity_stimulation(task_characteristics, contextual_elements)
        
        return CognitiveNeeds(
            knowledge_supplement=knowledge_needs,
            thinking_framework=framework_needs,
            creativity_stimulation=creativity_needs,
            support_priority=self._calculate_priority(task_characteristics)
        )
    
    def _predict_knowledge_supplement(self, task_characteristics: TaskCharacteristics, 
                                    contextual_elements: ContextualElements) -> List[str]:
        """预测知识补充需求"""
        needs = []
        
        # 基于任务特征预测知识补充需求
        if task_characteristics.cross_domain_level > 0.7:
            needs.append("跨领域知识背景")
            needs.append("领域间概念映射")
        
        if contextual_elements.abstraction_level == AbstractionLevel.META:
            needs.append("理论框架补充")
            needs.append("元认知知识")
        elif contextual_elements.abstraction_level == AbstractionLevel.OPERATIONAL:
            needs.append("实践方法指导")
            needs.append("操作步骤说明")
        
        if contextual_elements.complexity_level > 0.7:
            needs.append("复杂性处理方法")
            needs.append("系统性分析工具")
        
        # 基于任务类型补充
        if task_characteristics.task_type == TaskType.CREATIVE:
            needs.append("创新方法论")
        elif task_characteristics.task_type == TaskType.ANALYTICAL:
            needs.append("分析方法工具")
        
        return list(set(needs))  # 去重
    
    def _predict_thinking_framework(self, task_characteristics: TaskCharacteristics, 
                                  contextual_elements: ContextualElements) -> List[str]:
        """预测思维框架需求"""
        frameworks = []
        
        # 基于任务类型确定思维框架
        if task_characteristics.task_type == TaskType.ANALYTICAL:
            frameworks.extend(["分析框架", "逻辑推理结构"])
        elif task_characteristics.task_type == TaskType.EXPLORATORY:
            frameworks.extend(["探索性思维框架", "发散思维工具"])
        elif task_characteristics.task_type == TaskType.CREATIVE:
            frameworks.extend(["创新思维框架", "设计思维过程"])
        
        # 基于结构化需求调整
        if task_characteristics.structure_requirement > 0.7:
            frameworks.extend(["结构化思考工具", "系统性分析方法"])
        
        # 基于抽象层次调整
        if contextual_elements.abstraction_level == AbstractionLevel.META:
            frameworks.append("元认知思维框架")
        
        return list(set(frameworks))
    
    def _predict_creativity_stimulation(self, task_characteristics: TaskCharacteristics, 
                                      contextual_elements: ContextualElements) -> List[str]:
        """预测创意激发需求"""
        stimulations = []
        
        # 基于创造性需求提供激发工具
        if task_characteristics.creativity_requirement > 0.5:
            stimulations.extend(["类比案例", "跨域联想"])
            
            if task_characteristics.creativity_requirement > 0.7:
                stimulations.extend(["反常规思维引导", "创新技法应用"])
        
        # 基于跨领域程度调整
        if task_characteristics.cross_domain_level > 0.6:
            stimulations.extend(["跨域知识激活", "概念重组技术"])
        
        # 基于任务开放性调整
        if task_characteristics.openness_level > 0.7:
            stimulations.extend(["发散性思维练习", "多角度视角切换"])
        
        return list(set(stimulations))
    
    def _calculate_priority(self, task_characteristics: TaskCharacteristics) -> float:
        """计算支持优先级"""
        priority = 0.5
        
        # 基于任务复杂度和创造性需求提高优先级
        if task_characteristics.creativity_requirement > 0.7:
            priority += 0.2
        if task_characteristics.cross_domain_level > 0.7:
            priority += 0.2
        if task_characteristics.structure_requirement > 0.8:
            priority += 0.1
        
        return min(1.0, priority)
    
    def identify_task_type(self, query: str, context: Dict[str, Any]) -> TaskCharacteristics:
        """识别任务类型和特征"""
        return TaskCharacteristics(
            task_type=TaskType.ANALYTICAL,
            openness_level=0.5,
            structure_need=0.5,
            creativity_need=0.5,
            cross_domain_degree=0.5
        )
    
    def extract_contextual_elements(self, query: str, context: Dict[str, Any]) -> ContextualElements:
        """提取情境要素"""
        return ContextualElements(
            time_dimension=TimeDimension.CURRENT,
            domain_scope=["general"],
            abstraction_level=AbstractionLevel.MESO,
            purpose_type=PurposeType.UNDERSTANDING,
            stakeholder_complexity=0.5
        )


class IntegratedContextAnalyzer:
    """集成情境分析器 - 整合所有情境分析功能"""
    
    def __init__(self):
        self.task_identifier = TaskTypeIdentifier()
        self.element_extractor = ContextualElementExtractor()
        self.needs_predictor = CognitiveNeedsPredictor()
    
    def analyze_context(self, query: str, context: Dict[str, Any]) -> ContextProfile:
        """
        综合分析用户当前情境
        对应设计文档第4.3节：感知层的集成输出
        """
        # 识别任务特征
        task_characteristics = self.task_identifier.identify_task_type(query, context)
        
        # 提取情境要素
        contextual_elements = self.element_extractor.extract_contextual_elements(query, context)
        
        # 预测认知需求
        cognitive_needs = self.needs_predictor.predict_cognitive_needs(task_characteristics, contextual_elements)
        
        # 计算分析置信度
        confidence_score = self._calculate_confidence(task_characteristics, contextual_elements)
        
        return ContextProfile(
            task_characteristics=task_characteristics,
            contextual_elements=contextual_elements,
            cognitive_needs=cognitive_needs,
            confidence_score=confidence_score
        )
    
    def _calculate_confidence(self, task_characteristics: TaskCharacteristics, 
                            contextual_elements: ContextualElements) -> float:
        """计算情境分析置信度"""
        # TODO: 基于各个分析模块的确定性计算综合置信度
        return 0.8