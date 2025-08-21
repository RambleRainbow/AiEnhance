"""
个性化认知适配模块 - 对应设计文档第6.1节
确保系统输出与用户的认知特征高度匹配，实现真正的个性化交互
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..cognition.memory_activation import MemoryFragment
from ..perception.user_modeling import CognitiveStyle, UserProfile


class InformationDensity(Enum):
    """信息密度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OutputStructure(Enum):
    """输出结构类型"""
    LINEAR = "linear"  # 线性结构
    HIERARCHICAL = "hierarchical"  # 层次结构
    NETWORK = "network"  # 网络结构


class ConceptGranularity(Enum):
    """概念粒度"""
    MACRO = "macro"  # 宏观层
    MESO = "meso"  # 中观层
    MICRO = "micro"  # 微观层


@dataclass
class OutputConfiguration:
    """输出配置"""
    information_density: InformationDensity
    structure_type: OutputStructure
    concept_granularity: ConceptGranularity
    cognitive_load_limit: float
    personalization_level: float


@dataclass
class AdaptedContent:
    """适配后的内容"""
    content: str
    structure_type: OutputStructure
    density_level: InformationDensity
    granularity: ConceptGranularity
    cognitive_load: float
    adaptation_confidence: float
    metadata: dict[str, Any] | None = None


class AdaptiveOutputModule(ABC):
    """适应性输出模块基类"""

    @abstractmethod
    def adapt_output(self, content: list[MemoryFragment],
                    user_profile: UserProfile,
                    context: dict[str, Any]) -> AdaptedContent:
        """适配输出"""
        pass


class InformationDensityController(AdaptiveOutputModule):
    """信息密度控制器 - 对应设计文档第6.1.1节"""

    def adapt_output(self, content: list[MemoryFragment],
                    user_profile: UserProfile,
                    context: dict[str, Any]) -> AdaptedContent:
        """控制信息密度"""
        # 评估用户认知能力
        cognitive_capacity = self._assess_cognitive_capacity(user_profile)

        # 评估任务需求
        task_requirements = self._assess_task_requirements(context)

        # 评估当前认知状态
        cognitive_state = self._assess_cognitive_state(context)

        # 动态调控信息密度
        optimal_density = self._determine_optimal_density(
            cognitive_capacity, task_requirements, cognitive_state
        )

        # 调整内容密度
        adapted_content = self._adjust_content_density(content, optimal_density)

        return AdaptedContent(
            content=adapted_content,
            structure_type=OutputStructure.LINEAR,
            density_level=optimal_density,
            granularity=ConceptGranularity.MESO,
            cognitive_load=self._calculate_cognitive_load(adapted_content),
            adaptation_confidence=0.8
        )

    def _assess_cognitive_capacity(self, user_profile: UserProfile) -> float:
        """评估用户认知能力"""
        # TODO: 基于用户画像评估认知处理能力

        if not user_profile or not user_profile.cognitive:
            return 0.5  # 默认中等能力

        cognitive = user_profile.cognitive

        # 综合考虑抽象思维能力、认知复杂度等
        capacity_score = (
            cognitive.abstraction_level * 0.4 +
            cognitive.cognitive_complexity * 0.4 +
            cognitive.creativity_tendency * 0.2
        )

        return min(1.0, max(0.0, capacity_score))

    def _assess_task_requirements(self, context: dict[str, Any]) -> dict[str, float]:
        """评估任务需求"""
        # TODO: 分析任务对信息密度的要求

        task_context = context.get('task_context')
        if not task_context:
            return {'overview': 0.3, 'analysis': 0.5, 'decision': 0.7}

        # 根据任务类型确定信息密度需求
        task_type = getattr(task_context, 'task_type', 'general')

        density_requirements = {
            'overview': 0.3,  # 概览任务：突出要点，隐藏细节
            'analysis': 0.7,  # 深入分析：展开论述，提供证据
            'decision': 0.5   # 快速决策：精炼信息，直达结论
        }

        return {task_type: density_requirements.get(task_type, 0.5)}

    def _assess_cognitive_state(self, context: dict[str, Any]) -> str:
        """评估当前认知状态"""
        # TODO: 实时评估用户认知状态

        cognitive_load_indicators = context.get('cognitive_load_indicators', {})

        if cognitive_load_indicators.get('high_load', False):
            return 'high_load'
        elif cognitive_load_indicators.get('fatigue', False):
            return 'fatigue'
        else:
            return 'optimal'

    def _determine_optimal_density(self, capacity: float, requirements: dict[str, float],
                                 state: str) -> InformationDensity:
        """确定最优信息密度"""
        # 基于用户能力、任务需求和认知状态确定最优密度

        base_density = capacity * 0.6 + max(requirements.values()) * 0.4

        # 根据认知状态调整
        if state == 'high_load':
            base_density *= 0.7  # 降低密度
        elif state == 'fatigue':
            base_density *= 0.5  # 大幅降低密度
        elif state == 'optimal':
            base_density *= 1.0  # 保持密度

        # 映射到密度级别
        if base_density < 0.33:
            return InformationDensity.LOW
        elif base_density < 0.67:
            return InformationDensity.MEDIUM
        else:
            return InformationDensity.HIGH

    def _adjust_content_density(self, content: list[MemoryFragment],
                              density: InformationDensity) -> str:
        """调整内容密度"""
        # TODO: 根据密度级别调整内容的详细程度

        if not content:
            return ""

        if density == InformationDensity.LOW:
            # 低密度：只保留核心要点
            return self._extract_key_points(content)
        elif density == InformationDensity.MEDIUM:
            # 中等密度：适度展开
            return self._moderate_expansion(content)
        else:
            # 高密度：详细展开
            return self._detailed_expansion(content)

    def _extract_key_points(self, content: list[MemoryFragment]) -> str:
        """提取关键要点"""
        # TODO: 实现关键要点提取算法
        key_points = []
        for fragment in content[:3]:  # 只取前3个最重要的片段
            key_points.append(f"• {fragment.content[:100]}...")
        return "\n".join(key_points)

    def _moderate_expansion(self, content: list[MemoryFragment]) -> str:
        """适度展开"""
        # TODO: 实现适度展开算法
        expanded_content = []
        for fragment in content[:5]:  # 取前5个片段
            expanded_content.append(fragment.content)
        return "\n\n".join(expanded_content)

    def _detailed_expansion(self, content: list[MemoryFragment]) -> str:
        """详细展开"""
        # TODO: 实现详细展开算法
        detailed_content = []
        for fragment in content:  # 使用所有片段
            detailed_content.append(f"**{fragment.source}**: {fragment.content}")
        return "\n\n".join(detailed_content)

    def _calculate_cognitive_load(self, content: str) -> float:
        """计算认知负荷"""
        # TODO: 基于内容复杂度计算认知负荷

        # 简单的启发式计算
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')

        if sentence_count == 0:
            return 0.5

        avg_sentence_length = word_count / sentence_count

        # 根据平均句长估算认知负荷
        if avg_sentence_length < 10:
            return 0.3
        elif avg_sentence_length < 20:
            return 0.5
        else:
            return 0.8


class LogicalStructureAdapter(AdaptiveOutputModule):
    """逻辑结构适配器 - 对应设计文档第6.1.2节"""

    def adapt_output(self, content: list[MemoryFragment],
                    user_profile: UserProfile,
                    context: dict[str, Any]) -> AdaptedContent:
        """适配逻辑结构"""
        # 识别用户思维模式
        thinking_style = self._identify_thinking_style(user_profile)

        # 选择匹配的表达形式
        expression_form = self._select_expression_form(user_profile)

        # 重组内容结构
        restructured_content = self._restructure_content(content, thinking_style, expression_form)

        return AdaptedContent(
            content=restructured_content,
            structure_type=self._map_style_to_structure(thinking_style),
            density_level=InformationDensity.MEDIUM,
            granularity=ConceptGranularity.MESO,
            cognitive_load=0.5,
            adaptation_confidence=0.85
        )

    def _identify_thinking_style(self, user_profile: UserProfile) -> CognitiveStyle:
        """识别用户思维模式"""
        if not user_profile or not user_profile.interaction:
            return CognitiveStyle.LINEAR

        return user_profile.interaction.cognitive_style

    def _select_expression_form(self, user_profile: UserProfile) -> str:
        """选择表达形式"""
        # TODO: 根据用户偏好选择表达形式

        if not user_profile or not user_profile.cognitive:
            return "logical"

        # 根据创造性思维倾向选择表达形式
        if user_profile.cognitive.creativity_tendency > 0.7:
            return "visual"  # 视觉型用户：图表、类比、形象化表达
        elif user_profile.cognitive.abstraction_level > 0.7:
            return "logical"  # 逻辑型用户：公式化、符号化、形式化
        else:
            return "narrative"  # 听觉型用户：对话式、韵律感、故事化

    def _restructure_content(self, content: list[MemoryFragment],
                           thinking_style: CognitiveStyle,
                           expression_form: str) -> str:
        """重组内容结构"""
        if thinking_style == CognitiveStyle.LINEAR:
            return self._linear_structure(content, expression_form)
        elif thinking_style == CognitiveStyle.NETWORK:
            return self._network_structure(content, expression_form)
        else:  # HIERARCHICAL
            return self._hierarchical_structure(content, expression_form)

    def _linear_structure(self, content: list[MemoryFragment], expression_form: str) -> str:
        """线性结构组织"""
        # TODO: 按时间或因果顺序组织，明确的开始、中间、结束，步步推进的论证方式

        if not content:
            return ""

        structured_parts = [
            "## 背景概述",
            self._format_content_for_expression(content[0], expression_form) if content else "",
            "",
            "## 核心分析",
            "\n".join([self._format_content_for_expression(f, expression_form) for f in content[1:3]]),
            "",
            "## 结论总结",
            self._format_content_for_expression(content[-1], expression_form) if len(content) > 1 else ""
        ]

        return "\n".join(filter(None, structured_parts))

    def _network_structure(self, content: list[MemoryFragment], expression_form: str) -> str:
        """网络结构组织"""
        # TODO: 多中心的信息组织，丰富的交叉引用，支持非线性探索

        if not content:
            return ""

        # 创建多个信息中心
        centers = self._identify_information_centers(content)

        structured_parts = []
        for i, center in enumerate(centers):
            structured_parts.append(f"### 关联点 {i+1}: {center['theme']}")
            structured_parts.append(self._format_content_for_expression(center['content'], expression_form))

            # 添加交叉引用
            if center.get('related_points'):
                structured_parts.append(f"*相关联系: {', '.join(center['related_points'])}*")

            structured_parts.append("")

        return "\n".join(structured_parts)

    def _hierarchical_structure(self, content: list[MemoryFragment], expression_form: str) -> str:
        """层次结构组织"""
        # TODO: 清晰的层级结构，从总到分的展开，便于把握全局

        if not content:
            return ""

        # 按重要性和抽象层次组织
        hierarchy = self._build_content_hierarchy(content)

        structured_parts = []

        # 第一层：总体概述
        structured_parts.extend([
            "# 总体概述",
            self._format_content_for_expression(hierarchy.get('overview', content[0]), expression_form),
            ""
        ])

        # 第二层：主要方面
        if 'main_aspects' in hierarchy:
            structured_parts.append("## 主要方面")
            for aspect in hierarchy['main_aspects']:
                structured_parts.extend([
                    f"### {aspect['title']}",
                    self._format_content_for_expression(aspect['content'], expression_form),
                    ""
                ])

        # 第三层：具体细节
        if 'details' in hierarchy:
            structured_parts.append("## 具体细节")
            for detail in hierarchy['details']:
                structured_parts.extend([
                    f"- {self._format_content_for_expression(detail, expression_form)}",
                    ""
                ])

        return "\n".join(structured_parts)

    def _format_content_for_expression(self, fragment: MemoryFragment, expression_form: str) -> str:
        """根据表达形式格式化内容"""
        if expression_form == "visual":
            return f"📊 {fragment.content}"
        elif expression_form == "logical":
            return f"⟹ {fragment.content}"
        else:  # narrative
            return f"💬 {fragment.content}"

    def _map_style_to_structure(self, style: CognitiveStyle) -> OutputStructure:
        """映射思维风格到输出结构"""
        mapping = {
            CognitiveStyle.LINEAR: OutputStructure.LINEAR,
            CognitiveStyle.NETWORK: OutputStructure.NETWORK,
            CognitiveStyle.HIERARCHICAL: OutputStructure.HIERARCHICAL
        }
        return mapping.get(style, OutputStructure.LINEAR)

    # Helper methods (TODO: implement)
    def _identify_information_centers(self, content: list[MemoryFragment]) -> list[dict[str, Any]]:
        """识别信息中心"""
        centers = []
        for i, fragment in enumerate(content[:3]):  # 最多3个中心
            centers.append({
                'theme': f"主题{i+1}",
                'content': fragment,
                'related_points': [f"关联点{j+1}" for j in range(len(content)) if j != i][:2]
            })
        return centers

    def _build_content_hierarchy(self, content: list[MemoryFragment]) -> dict[str, Any]:
        """构建内容层次"""
        if not content:
            return {}

        hierarchy = {
            'overview': content[0],
            'main_aspects': [
                {'title': f"方面{i+1}", 'content': fragment}
                for i, fragment in enumerate(content[1:4])
            ],
            'details': content[4:] if len(content) > 4 else []
        }

        return hierarchy


class ConceptGranularityController(AdaptiveOutputModule):
    """概念粒度调节器 - 对应设计文档第6.1.3节"""

    def adapt_output(self, content: list[MemoryFragment],
                    user_profile: UserProfile,
                    context: dict[str, Any]) -> AdaptedContent:
        """调节概念粒度"""
        # 评估用户当前理解水平
        understanding_level = self._assess_understanding_level(user_profile, context)

        # 确定最适合的粒度层次
        optimal_granularity = self._determine_optimal_granularity(understanding_level, context)

        # 调整内容粒度
        granularity_adjusted_content = self._adjust_concept_granularity(content, optimal_granularity)

        return AdaptedContent(
            content=granularity_adjusted_content,
            structure_type=OutputStructure.HIERARCHICAL,
            density_level=InformationDensity.MEDIUM,
            granularity=optimal_granularity,
            cognitive_load=0.6,
            adaptation_confidence=0.75
        )

    def _assess_understanding_level(self, user_profile: UserProfile, context: dict[str, Any]) -> str:
        """评估理解水平"""
        # TODO: 基于用户画像和交互历史评估当前理解水平

        interaction_history = context.get('interaction_history', [])

        if not user_profile or not interaction_history:
            return 'initial'  # 初次接触

        # 分析用户的知识深度和交互模式
        knowledge_depth = getattr(user_profile.knowledge, 'knowledge_depth', {})
        current_domain = context.get('current_domain', 'general')

        domain_knowledge = knowledge_depth.get(current_domain, 0.0)

        if domain_knowledge > 0.8:
            return 'expert'
        elif domain_knowledge > 0.5:
            return 'intermediate'
        else:
            return 'beginner'

    def _determine_optimal_granularity(self, understanding_level: str,
                                     context: dict[str, Any]) -> ConceptGranularity:
        """确定最优粒度"""
        task_phase = context.get('task_phase', 'exploration')

        # 动态粒度选择策略
        if understanding_level == 'expert':
            if task_phase == 'application':
                return ConceptGranularity.MICRO  # 专家应用：聚焦具体操作
            else:
                return ConceptGranularity.MESO   # 专家理解：中观概念
        elif understanding_level == 'intermediate':
            return ConceptGranularity.MESO       # 中级用户：适度细化
        else:  # beginner
            if task_phase == 'initial':
                return ConceptGranularity.MACRO  # 初学者首次：宏观概览
            else:
                return ConceptGranularity.MESO   # 初学者深入：逐步细化

    def _adjust_concept_granularity(self, content: list[MemoryFragment],
                                  granularity: ConceptGranularity) -> str:
        """调整概念粒度"""
        if granularity == ConceptGranularity.MACRO:
            return self._macro_level_content(content)
        elif granularity == ConceptGranularity.MESO:
            return self._meso_level_content(content)
        else:  # MICRO
            return self._micro_level_content(content)

    def _macro_level_content(self, content: list[MemoryFragment]) -> str:
        """宏观层内容：领域全貌、核心理念"""
        if not content:
            return ""

        # 提取最高层次的概念和理念
        macro_concepts = []

        macro_concepts.append("## 核心理念")
        macro_concepts.append(f"本领域的核心思想是: {content[0].content[:200]}...")

        if len(content) > 1:
            macro_concepts.append("\n## 整体框架")
            macro_concepts.append(f"总体框架包括: {content[1].content[:200]}...")

        return "\n".join(macro_concepts)

    def _meso_level_content(self, content: list[MemoryFragment]) -> str:
        """中观层内容：主要概念、关键联系"""
        if not content:
            return ""

        meso_content = []

        meso_content.append("## 主要概念")
        for i, fragment in enumerate(content[:3]):
            meso_content.append(f"### 概念 {i+1}")
            meso_content.append(fragment.content)
            meso_content.append("")

        if len(content) > 3:
            meso_content.append("## 关键联系")
            meso_content.append("这些概念之间的主要联系包括:")
            for fragment in content[3:5]:
                meso_content.append(f"- {fragment.content[:100]}...")

        return "\n".join(meso_content)

    def _micro_level_content(self, content: list[MemoryFragment]) -> str:
        """微观层内容：具体细节、操作要素"""
        if not content:
            return ""

        micro_content = []

        micro_content.append("## 具体细节")
        for i, fragment in enumerate(content):
            micro_content.append(f"### 细节 {i+1}: {fragment.source}")
            micro_content.append(f"**内容**: {fragment.content}")
            micro_content.append(f"**相关性**: {fragment.relevance_score:.2f}")
            micro_content.append("")

        return "\n".join(micro_content)


class IntegratedAdaptiveOutput:
    """集成自适应输出器 - 整合所有个性化适配功能"""

    def __init__(self):
        self.density_controller = InformationDensityController()
        self.structure_adapter = LogicalStructureAdapter()
        self.granularity_controller = ConceptGranularityController()

    def comprehensive_adaptation(self, content: list[MemoryFragment],
                                user_profile: UserProfile,
                                context: dict[str, Any]) -> AdaptedContent:
        """
        综合自适应输出
        对应设计文档第6.1节：个性化认知适配模块
        """
        # 第一步：控制信息密度
        density_result = self.density_controller.adapt_output(content, user_profile, context)

        # 第二步：适配逻辑结构
        structure_result = self.structure_adapter.adapt_output(content, user_profile, context)

        # 第三步：调节概念粒度
        granularity_result = self.granularity_controller.adapt_output(content, user_profile, context)

        # 综合所有适配结果
        final_content = self._integrate_adaptations(
            density_result, structure_result, granularity_result
        )

        return AdaptedContent(
            content=final_content,
            structure_type=structure_result.structure_type,
            density_level=density_result.density_level,
            granularity=granularity_result.granularity,
            cognitive_load=self._calculate_final_cognitive_load(density_result, granularity_result),
            adaptation_confidence=self._calculate_adaptation_confidence([
                density_result, structure_result, granularity_result
            ])
        )

    def _integrate_adaptations(self, density_result: AdaptedContent,
                             structure_result: AdaptedContent,
                             granularity_result: AdaptedContent) -> str:
        """整合多种适配结果"""
        # TODO: 智能融合不同适配器的输出

        # 简化版本：优先使用结构适配的内容，应用密度和粒度的调整
        base_content = structure_result.content

        # 应用密度控制的调整
        if density_result.density_level == InformationDensity.LOW:
            # 进一步简化内容
            lines = base_content.split('\n')
            key_lines = [line for line in lines if line.startswith('#') or line.startswith('•')]
            base_content = '\n'.join(key_lines)

        return base_content

    def _calculate_final_cognitive_load(self, density_result: AdaptedContent,
                                      granularity_result: AdaptedContent) -> float:
        """计算最终认知负荷"""
        return (density_result.cognitive_load + granularity_result.cognitive_load) / 2

    def _calculate_adaptation_confidence(self, results: list[AdaptedContent]) -> float:
        """计算适配置信度"""
        if not results:
            return 0.0

        confidences = [result.adaptation_confidence for result in results]
        return sum(confidences) / len(confidences)
