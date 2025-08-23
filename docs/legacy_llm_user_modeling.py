"""
基于LLM语义理解的现代用户建模模块
使用提示词工程和模板系统实现准确性与适应性的平衡
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..llm.interfaces import ChatMessage, LLMProvider, MessageRole
from .user_modeling import (
    CognitiveProfile,
    CognitiveStyle,
    InteractionProfile,
    KnowledgeProfile,
    ThinkingMode,
    UserProfile,
)

logger = logging.getLogger(__name__)


class PromptTemplate(ABC):
    """提示词模板抽象基类"""

    @abstractmethod
    def generate_prompt(self, context: dict[str, Any]) -> str:
        """生成具体的提示词"""
        pass

    @abstractmethod
    def parse_response(self, response: str) -> dict[str, Any]:
        """解析LLM响应"""
        pass


class DomainType(Enum):
    """领域类型枚举"""

    GENERAL = "general"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    BUSINESS = "business"


@dataclass
class PromptContext:
    """提示词上下文"""

    user_query: str
    user_history: list[str]
    domain_type: DomainType
    analysis_type: str  # cognitive, knowledge, interaction
    additional_context: dict[str, Any] | None = None


class CognitiveAnalysisPrompt(PromptTemplate):
    """认知能力分析提示词模板"""

    def __init__(self, domain_type: DomainType = DomainType.GENERAL):
        self.domain_type = domain_type

        # 元结构：认知分析的核心框架
        self.meta_structure = """
        请分析用户的认知特征，包括：
        1. 思维模式 (analytical/intuitive/creative)
        2. 认知复杂度 (0.0-1.0)
        3. 抽象思维能力 (0.0-1.0)
        4. 创造性思维倾向 (0.0-1.0)
        5. 推理偏好描述
        """

        # 领域特化提示词模板
        self.domain_templates = {
            DomainType.TECHNICAL: """
            技术领域认知分析要点：
            - 关注逻辑推理和系统性思维
            - 评估对复杂技术概念的理解深度
            - 分析问题分解和解决方案构建能力
            - 注意技术术语使用的准确性和深度
            """,
            DomainType.ACADEMIC: """
            学术领域认知分析要点：
            - 重视批判性思维和证据导向推理
            - 评估理论概念的掌握和应用能力
            - 分析跨学科连接和综合分析能力
            - 关注学术表达的严谨性和逻辑性
            """,
            DomainType.CREATIVE: """
            创意领域认知分析要点：
            - 强调发散思维和联想能力
            - 评估创新性和原创性思考
            - 分析美学感知和表达能力
            - 注重直觉思维和灵感捕捉能力
            """,
            DomainType.EDUCATIONAL: """
            教育领域认知分析要点：
            - 关注学习策略和知识建构模式
            - 评估元认知意识和反思能力
            - 分析概念理解的深度和广度
            - 注意学习动机和认知负荷管理
            """,
            DomainType.GENERAL: """
            通用认知分析要点：
            - 平衡分析各项认知能力
            - 注重思维模式的多样性表现
            - 评估一般智力和适应能力
            - 关注常识推理和日常问题解决
            """,
        }

    def generate_prompt(self, context: PromptContext) -> str:
        domain_prompt = self.domain_templates.get(
            context.domain_type, self.domain_templates[DomainType.GENERAL]
        )

        history_text = "\n".join([f"- {h}" for h in context.user_history[-5:]])

        return f"""
{self.meta_structure}

{domain_prompt}

用户当前问句：
{context.user_query}

用户历史交互（最近5条）：
{history_text}

请基于语义分析，以JSON格式返回用户认知特征：
{{
    "thinking_mode": "analytical|intuitive|creative",
    "cognitive_complexity": 0.0-1.0,
    "abstraction_level": 0.0-1.0,
    "creativity_tendency": 0.0-1.0,
    "reasoning_preference": "推理偏好的详细描述",
    "analysis_confidence": 0.0-1.0,
    "domain_indicators": ["识别到的专业领域"],
    "cognitive_patterns": ["观察到的认知模式"]
}}
        """.strip()

    def parse_response(self, response: str) -> dict[str, Any]:
        try:
            # 提取JSON内容
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)

                # 验证和标准化数据
                result["thinking_mode"] = self._validate_thinking_mode(
                    result.get("thinking_mode", "analytical")
                )
                result["cognitive_complexity"] = max(
                    0.0, min(1.0, float(result.get("cognitive_complexity", 0.5)))
                )
                result["abstraction_level"] = max(
                    0.0, min(1.0, float(result.get("abstraction_level", 0.5)))
                )
                result["creativity_tendency"] = max(
                    0.0, min(1.0, float(result.get("creativity_tendency", 0.5)))
                )

                return result
            else:
                logger.warning("无法从响应中提取有效JSON")
                return self._get_default_cognitive_result()

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"解析认知分析响应失败: {e}")
            return self._get_default_cognitive_result()

    def _validate_thinking_mode(self, mode: str) -> str:
        valid_modes = ["analytical", "intuitive", "creative"]
        return mode if mode in valid_modes else "analytical"

    def _get_default_cognitive_result(self) -> dict[str, Any]:
        return {
            "thinking_mode": "analytical",
            "cognitive_complexity": 0.5,
            "abstraction_level": 0.5,
            "creativity_tendency": 0.5,
            "reasoning_preference": "平衡的推理模式",
            "analysis_confidence": 0.3,
            "domain_indicators": [],
            "cognitive_patterns": [],
        }


class KnowledgeAnalysisPrompt(PromptTemplate):
    """知识结构分析提示词模板"""

    def __init__(self, domain_type: DomainType = DomainType.GENERAL):
        self.domain_type = domain_type

        self.meta_structure = """
        请分析用户的知识结构特征，包括：
        1. 核心专业领域
        2. 边缘接触领域
        3. 各领域知识深度评估
        4. 跨域知识连接能力
        5. 知识边界和盲点识别
        """

        self.domain_templates = {
            DomainType.TECHNICAL: """
            技术知识分析要点：
            - 识别具体技术栈和工具熟悉度
            - 评估编程语言、框架、算法理解深度
            - 分析系统设计和架构思维能力
            - 判断技术趋势跟踪和学习能力
            """,
            DomainType.ACADEMIC: """
            学术知识分析要点：
            - 确定学科专业背景和研究方向
            - 评估理论基础和研究方法掌握
            - 分析文献阅读和批判性思维能力
            - 判断跨学科知识整合能力
            """,
            DomainType.CREATIVE: """
            创意知识分析要点：
            - 识别艺术、设计、文学等创意领域背景
            - 评估美学理论和创作技法了解度
            - 分析文化素养和审美认知水平
            - 判断创意表达和媒介运用能力
            """,
            DomainType.EDUCATIONAL: """
            教育知识分析要点：
            - 确定教育背景和学习经历
            - 评估学科知识结构和概念理解
            - 分析学习策略和知识建构模式
            - 判断知识迁移和应用能力
            """,
            DomainType.GENERAL: """
            通用知识分析要点：
            - 评估常识性知识广度和深度
            - 分析多领域知识的平衡性
            - 判断信息获取和处理能力
            - 识别知识更新和学习习惯
            """,
        }

    def generate_prompt(self, context: PromptContext) -> str:
        domain_prompt = self.domain_templates.get(
            context.domain_type, self.domain_templates[DomainType.GENERAL]
        )

        history_text = "\n".join([f"- {h}" for h in context.user_history[-10:]])

        return f"""
{self.meta_structure}

{domain_prompt}

用户当前问句：
{context.user_query}

用户历史交互（最近10条）：
{history_text}

请基于语义分析用户的知识结构，以JSON格式返回：
{{
    "core_domains": ["核心专业领域列表"],
    "edge_domains": ["边缘接触领域列表"],
    "knowledge_depth": {{"领域名": 深度值(0.0-1.0)}},
    "cross_domain_ability": 0.0-1.0,
    "knowledge_boundaries": ["知识边界和盲点"],
    "expertise_indicators": ["专业能力指标"],
    "learning_patterns": ["学习模式特征"],
    "analysis_confidence": 0.0-1.0
}}
        """.strip()

    def parse_response(self, response: str) -> dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)

                # 标准化数据
                result["core_domains"] = result.get("core_domains", ["general"])
                result["edge_domains"] = result.get("edge_domains", [])
                result["knowledge_depth"] = result.get(
                    "knowledge_depth", {"general": 0.5}
                )
                result["cross_domain_ability"] = max(
                    0.0, min(1.0, float(result.get("cross_domain_ability", 0.5)))
                )
                result["knowledge_boundaries"] = result.get("knowledge_boundaries", [])

                return result
            else:
                return self._get_default_knowledge_result()

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"解析知识分析响应失败: {e}")
            return self._get_default_knowledge_result()

    def _get_default_knowledge_result(self) -> dict[str, Any]:
        return {
            "core_domains": ["general"],
            "edge_domains": [],
            "knowledge_depth": {"general": 0.5},
            "cross_domain_ability": 0.5,
            "knowledge_boundaries": [],
            "expertise_indicators": [],
            "learning_patterns": [],
            "analysis_confidence": 0.3,
        }


class InteractionAnalysisPrompt(PromptTemplate):
    """交互模式分析提示词模板"""

    def __init__(self, domain_type: DomainType = DomainType.GENERAL):
        self.domain_type = domain_type

        self.meta_structure = """
        请分析用户的交互模式特征，包括：
        1. 认知风格 (linear/network/hierarchical)
        2. 信息密度偏好 (0.0-1.0)
        3. 信息处理速度 (0.0-1.0)
        4. 反馈偏好描述
        5. 学习风格描述
        """

        self.domain_templates = {
            DomainType.TECHNICAL: """
            技术交互分析要点：
            - 关注代码、文档、技术图表的偏好
            - 分析对技术细节和实现步骤的需求
            - 评估对抽象概念vs具体实例的偏好
            - 判断调试和问题解决的交互模式
            """,
            DomainType.EDUCATIONAL: """
            教育交互分析要点：
            - 识别学习节奏和认知负荷承受力
            - 分析对解释深度和示例需求的偏好
            - 评估对反馈频率和指导方式的期望
            - 判断主动探索vs被动接受的倾向
            """,
            DomainType.CREATIVE: """
            创意交互分析要点：
            - 关注对灵感激发和创意引导的需求
            - 分析对开放性讨论vs结构化指导的偏好
            - 评估对美学表达和情感共鸣的重视
            - 判断实验性探索vs系统性学习的倾向
            """,
            DomainType.GENERAL: """
            通用交互分析要点：
            - 平衡评估各种交互模式偏好
            - 分析信息组织和呈现方式偏好
            - 评估交互深度和广度的期望
            - 判断正式vs非正式交流风格倾向
            """,
        }

    def generate_prompt(self, context: PromptContext) -> str:
        domain_prompt = self.domain_templates.get(
            context.domain_type, self.domain_templates[DomainType.GENERAL]
        )

        history_text = "\n".join([f"- {h}" for h in context.user_history[-8:]])

        return f"""
{self.meta_structure}

{domain_prompt}

用户当前问句：
{context.user_query}

用户历史交互（最近8条）：
{history_text}

请基于语义分析用户的交互模式，以JSON格式返回：
{{
    "cognitive_style": "linear|network|hierarchical",
    "information_density_preference": 0.0-1.0,
    "processing_speed": 0.0-1.0,
    "feedback_preference": "反馈偏好描述",
    "learning_style": "学习风格描述",
    "communication_patterns": ["交流模式特征"],
    "interaction_depth_preference": "light|moderate|deep",
    "analysis_confidence": 0.0-1.0
}}
        """.strip()

    def parse_response(self, response: str) -> dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)

                # 验证和标准化
                result["cognitive_style"] = self._validate_cognitive_style(
                    result.get("cognitive_style", "linear")
                )
                result["information_density_preference"] = max(
                    0.0,
                    min(1.0, float(result.get("information_density_preference", 0.5))),
                )
                result["processing_speed"] = max(
                    0.0, min(1.0, float(result.get("processing_speed", 0.5)))
                )

                return result
            else:
                return self._get_default_interaction_result()

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"解析交互分析响应失败: {e}")
            return self._get_default_interaction_result()

    def _validate_cognitive_style(self, style: str) -> str:
        valid_styles = ["linear", "network", "hierarchical"]
        return style if style in valid_styles else "linear"

    def _get_default_interaction_result(self) -> dict[str, Any]:
        return {
            "cognitive_style": "linear",
            "information_density_preference": 0.5,
            "processing_speed": 0.5,
            "feedback_preference": "平衡反馈",
            "learning_style": "适应性学习",
            "communication_patterns": [],
            "interaction_depth_preference": "moderate",
            "analysis_confidence": 0.3,
        }


class LLMSemanticUserModeler:
    """基于LLM语义理解的用户建模器"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.user_profiles: dict[str, UserProfile] = {}

        # 初始化提示词模板
        self.cognitive_prompt = CognitiveAnalysisPrompt()
        self.knowledge_prompt = KnowledgeAnalysisPrompt()
        self.interaction_prompt = InteractionAnalysisPrompt()

    async def create_user_profile(
        self, user_id: str, initial_data: dict[str, Any]
    ) -> UserProfile:
        """
        创建基于语义分析的用户画像

        Args:
            user_id: 用户ID
            initial_data: 初始数据，包含query、memory_context等

        Returns:
            UserProfile: 完整的用户画像
        """
        try:
            # 准备分析上下文
            context = self._prepare_analysis_context(initial_data)

            # 并行执行三个维度的语义分析
            cognitive_result = await self._analyze_cognitive_profile(context)
            knowledge_result = await self._analyze_knowledge_profile(context)
            interaction_result = await self._analyze_interaction_profile(context)

            # 构建完整用户画像
            profile = self._build_complete_profile(
                user_id, cognitive_result, knowledge_result, interaction_result
            )

            self.user_profiles[user_id] = profile
            logger.info(f"成功创建用户 {user_id} 的语义化用户画像")
            return profile

        except Exception as e:
            logger.error(f"创建用户画像失败: {e}")
            # 返回默认画像
            return self._create_default_profile(user_id)

    def _prepare_analysis_context(self, initial_data: dict[str, Any]) -> PromptContext:
        """准备分析上下文"""
        user_query = initial_data.get("query", "")
        memory_context = initial_data.get("memory_context", [])

        # 从记忆中提取历史交互
        user_history = []
        if memory_context:
            user_history = [
                mem.get("content", "")
                for mem in memory_context[-10:]
                if mem.get("metadata", {}).get("type") == "user_query"
            ]

        # 智能识别领域类型
        domain_type = self._detect_domain_type(user_query, user_history)

        return PromptContext(
            user_query=user_query,
            user_history=user_history,
            domain_type=domain_type,
            analysis_type="comprehensive",
            additional_context=initial_data.get("session_context"),
        )

    def _detect_domain_type(self, query: str, history: list[str]) -> DomainType:
        """智能检测领域类型"""
        all_text = f"{query} {' '.join(history)}".lower()

        # 技术领域关键词
        tech_keywords = [
            "编程",
            "代码",
            "算法",
            "开发",
            "python",
            "javascript",
            "数据库",
            "架构",
            "api",
            "框架",
            "系统",
        ]

        # 学术领域关键词
        academic_keywords = [
            "研究",
            "理论",
            "分析",
            "学术",
            "文献",
            "论文",
            "实验",
            "假设",
            "方法论",
            "模型",
        ]

        # 创意领域关键词
        creative_keywords = [
            "设计",
            "创意",
            "艺术",
            "美学",
            "创作",
            "灵感",
            "作品",
            "表现",
            "风格",
            "创新",
        ]

        # 教育领域关键词
        educational_keywords = [
            "学习",
            "教学",
            "教育",
            "课程",
            "知识",
            "理解",
            "掌握",
            "学会",
            "解释",
            "概念",
        ]

        # 计算匹配度
        tech_score = sum(1 for kw in tech_keywords if kw in all_text)
        academic_score = sum(1 for kw in academic_keywords if kw in all_text)
        creative_score = sum(1 for kw in creative_keywords if kw in all_text)
        educational_score = sum(1 for kw in educational_keywords if kw in all_text)

        # 选择得分最高的领域
        scores = {
            DomainType.TECHNICAL: tech_score,
            DomainType.ACADEMIC: academic_score,
            DomainType.CREATIVE: creative_score,
            DomainType.EDUCATIONAL: educational_score,
        }

        max_domain = max(scores, key=scores.get)
        return max_domain if scores[max_domain] > 0 else DomainType.GENERAL

    async def _analyze_cognitive_profile(
        self, context: PromptContext
    ) -> dict[str, Any]:
        """分析认知能力维度"""
        self.cognitive_prompt.domain_type = context.domain_type
        prompt = self.cognitive_prompt.generate_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=500
        )
        response_content = response.content

        return self.cognitive_prompt.parse_response(response_content)

    async def _analyze_knowledge_profile(
        self, context: PromptContext
    ) -> dict[str, Any]:
        """分析知识结构维度"""
        self.knowledge_prompt.domain_type = context.domain_type
        prompt = self.knowledge_prompt.generate_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=600
        )

        return self.knowledge_prompt.parse_response(response.content)

    async def _analyze_interaction_profile(
        self, context: PromptContext
    ) -> dict[str, Any]:
        """分析交互模式维度"""
        self.interaction_prompt.domain_type = context.domain_type
        prompt = self.interaction_prompt.generate_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=400
        )

        return self.interaction_prompt.parse_response(response.content)

    def _build_complete_profile(
        self,
        user_id: str,
        cognitive_result: dict[str, Any],
        knowledge_result: dict[str, Any],
        interaction_result: dict[str, Any],
    ) -> UserProfile:
        """构建完整的用户画像"""
        from datetime import datetime

        # 构建认知画像
        thinking_mode_map = {
            "analytical": ThinkingMode.ANALYTICAL,
            "intuitive": ThinkingMode.INTUITIVE,
            "creative": ThinkingMode.CREATIVE,
        }

        cognitive = CognitiveProfile(
            thinking_mode=thinking_mode_map[cognitive_result["thinking_mode"]],
            cognitive_complexity=cognitive_result["cognitive_complexity"],
            abstraction_level=cognitive_result["abstraction_level"],
            creativity_tendency=cognitive_result["creativity_tendency"],
            reasoning_preference=cognitive_result["reasoning_preference"],
        )

        # 构建知识画像
        knowledge = KnowledgeProfile(
            core_domains=knowledge_result["core_domains"],
            edge_domains=knowledge_result["edge_domains"],
            knowledge_depth=knowledge_result["knowledge_depth"],
            cross_domain_ability=knowledge_result["cross_domain_ability"],
            knowledge_boundaries=knowledge_result["knowledge_boundaries"],
        )

        # 构建交互画像
        cognitive_style_map = {
            "linear": CognitiveStyle.LINEAR,
            "network": CognitiveStyle.NETWORK,
            "hierarchical": CognitiveStyle.HIERARCHICAL,
        }

        interaction = InteractionProfile(
            cognitive_style=cognitive_style_map[interaction_result["cognitive_style"]],
            information_density_preference=interaction_result[
                "information_density_preference"
            ],
            processing_speed=interaction_result["processing_speed"],
            feedback_preference=interaction_result["feedback_preference"],
            learning_style=interaction_result["learning_style"],
        )

        return UserProfile(
            user_id=user_id,
            cognitive=cognitive,
            knowledge=knowledge,
            interaction=interaction,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def _create_default_profile(self, user_id: str) -> UserProfile:
        """创建默认用户画像（降级方案）"""
        from datetime import datetime

        return UserProfile(
            user_id=user_id,
            cognitive=CognitiveProfile(
                thinking_mode=ThinkingMode.ANALYTICAL,
                cognitive_complexity=0.5,
                abstraction_level=0.5,
                creativity_tendency=0.5,
                reasoning_preference="平衡推理模式",
            ),
            knowledge=KnowledgeProfile(
                core_domains=["general"],
                edge_domains=[],
                knowledge_depth={"general": 0.5},
                cross_domain_ability=0.5,
                knowledge_boundaries=[],
            ),
            interaction=InteractionProfile(
                cognitive_style=CognitiveStyle.LINEAR,
                information_density_preference=0.5,
                processing_speed=0.5,
                feedback_preference="平衡反馈",
                learning_style="适应性学习",
            ),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    async def update_user_profile(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> UserProfile:
        """动态更新用户画像（增量语义分析）"""
        if user_id not in self.user_profiles:
            return await self.create_user_profile(user_id, interaction_data)

        # TODO: 实现增量更新逻辑
        # 可以基于新的交互数据，只更新变化的维度
        current_profile = self.user_profiles[user_id]

        # 这里可以添加增量分析逻辑
        logger.info(f"用户 {user_id} 的画像已更新")
        return current_profile

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        return self.user_profiles.get(user_id)

    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "llm_semantic_user_modeling",
            "llm_provider": self.llm_provider.config.provider,
            "llm_model": self.llm_provider.config.model_name,
            "supported_domains": [dt.value for dt in DomainType],
            "analysis_dimensions": ["cognitive", "knowledge", "interaction"],
            "user_count": len(self.user_profiles),
        }
