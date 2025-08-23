"""
基于LLM语义理解的用户建模器实现
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..llm.interfaces import ChatMessage, LLMProvider, MessageRole
from .user_modeling_interfaces import (
    CognitiveProfile,
    CognitiveStyle,
    InteractionProfile,
    KnowledgeProfile,
    ThinkingMode,
    UserModeler,
    UserModelerFactory,
    UserProfile,
)

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """领域类型枚举"""

    GENERAL = "general"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    BUSINESS = "business"


@dataclass
class AnalysisContext:
    """分析上下文"""

    user_query: str
    user_history: list[str]
    domain_type: DomainType
    additional_context: dict[str, Any] | None = None


class SemanticUserModeler(UserModeler):
    """基于LLM语义理解的用户建模器"""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.user_profiles: dict[str, UserProfile] = {}

    async def create_user_profile(
        self, user_id: str, initial_data: dict[str, Any]
    ) -> UserProfile:
        """创建基于语义分析的用户画像"""
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
            return self._create_default_profile(user_id)

    async def update_user_profile(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> UserProfile:
        """动态更新用户画像"""
        if user_id not in self.user_profiles:
            return await self.create_user_profile(user_id, interaction_data)

        # TODO: 实现增量更新逻辑
        current_profile = self.user_profiles[user_id]
        current_profile.updated_at = datetime.now().isoformat()

        logger.info(f"用户 {user_id} 的画像已更新")
        return current_profile

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        """获取用户画像"""
        return self.user_profiles.get(user_id)

    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "semantic_user_modeler",
            "llm_provider": self.llm_provider.config.provider,
            "llm_model": self.llm_provider.config.model_name,
            "supported_domains": [dt.value for dt in DomainType],
            "user_count": len(self.user_profiles),
        }

    def _prepare_analysis_context(
        self, initial_data: dict[str, Any]
    ) -> AnalysisContext:
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

        return AnalysisContext(
            user_query=user_query,
            user_history=user_history,
            domain_type=domain_type,
            additional_context=initial_data.get("session_context"),
        )

    def _detect_domain_type(self, query: str, history: list[str]) -> DomainType:
        """智能检测领域类型"""
        all_text = f"{query} {' '.join(history)}".lower()

        # 定义领域关键词
        domain_keywords = {
            DomainType.TECHNICAL: [
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
            ],
            DomainType.ACADEMIC: [
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
            ],
            DomainType.CREATIVE: [
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
            ],
            DomainType.EDUCATIONAL: [
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
            ],
            DomainType.BUSINESS: [
                "商业",
                "管理",
                "营销",
                "经济",
                "市场",
                "策略",
                "企业",
                "商务",
                "投资",
                "财务",
            ],
        }

        # 计算匹配度
        scores = {}
        for domain_type, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in all_text)
            scores[domain_type] = score

        # 选择得分最高的领域
        max_domain = max(scores, key=scores.get)
        return max_domain if scores[max_domain] > 0 else DomainType.GENERAL

    async def _analyze_cognitive_profile(
        self, context: AnalysisContext
    ) -> dict[str, Any]:
        """分析认知能力维度"""
        prompt = self._generate_cognitive_analysis_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=500
        )

        return self._parse_cognitive_response(response.content)

    async def _analyze_knowledge_profile(
        self, context: AnalysisContext
    ) -> dict[str, Any]:
        """分析知识结构维度"""
        prompt = self._generate_knowledge_analysis_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=600
        )

        return self._parse_knowledge_response(response.content)

    async def _analyze_interaction_profile(
        self, context: AnalysisContext
    ) -> dict[str, Any]:
        """分析交互模式维度"""
        prompt = self._generate_interaction_analysis_prompt(context)

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(
            messages, temperature=0.3, max_tokens=400
        )

        return self._parse_interaction_response(response.content)

    def _generate_cognitive_analysis_prompt(self, context: AnalysisContext) -> str:
        """生成认知分析提示词"""
        domain_specific = self._get_domain_cognitive_guidance(context.domain_type)
        history_text = "\n".join([f"- {h}" for h in context.user_history[-5:]])

        return f"""
请分析用户的认知特征，包括：
1. 思维模式 (analytical/intuitive/creative)
2. 认知复杂度 (0.0-1.0)
3. 抽象思维能力 (0.0-1.0)
4. 创造性思维倾向 (0.0-1.0)
5. 推理偏好描述

{domain_specific}

用户当前问句：{context.user_query}

用户历史交互：{history_text}

请以JSON格式返回分析结果：
{{
    "thinking_mode": "analytical|intuitive|creative",
    "cognitive_complexity": 0.0-1.0,
    "abstraction_level": 0.0-1.0,
    "creativity_tendency": 0.0-1.0,
    "reasoning_preference": "推理偏好描述"
}}
        """.strip()

    def _generate_knowledge_analysis_prompt(self, context: AnalysisContext) -> str:
        """生成知识分析提示词"""
        domain_specific = self._get_domain_knowledge_guidance(context.domain_type)
        history_text = "\n".join([f"- {h}" for h in context.user_history[-8:]])

        return f"""
请分析用户的知识结构特征，包括：
1. 核心专业领域
2. 边缘接触领域
3. 各领域知识深度评估
4. 跨域知识连接能力
5. 知识边界和盲点识别

{domain_specific}

用户当前问句：{context.user_query}

用户历史交互：{history_text}

请以JSON格式返回分析结果：
{{
    "core_domains": ["核心专业领域"],
    "edge_domains": ["边缘接触领域"],
    "knowledge_depth": {{"领域名": 深度值}},
    "cross_domain_ability": 0.0-1.0,
    "knowledge_boundaries": ["知识边界"]
}}
        """.strip()

    def _generate_interaction_analysis_prompt(self, context: AnalysisContext) -> str:
        """生成交互分析提示词"""
        domain_specific = self._get_domain_interaction_guidance(context.domain_type)
        history_text = "\n".join([f"- {h}" for h in context.user_history[-6:]])

        return f"""
请分析用户的交互模式特征，包括：
1. 认知风格 (linear/network/hierarchical)
2. 信息密度偏好 (0.0-1.0)
3. 信息处理速度 (0.0-1.0)
4. 反馈偏好描述
5. 学习风格描述

{domain_specific}

用户当前问句：{context.user_query}

用户历史交互：{history_text}

请以JSON格式返回分析结果：
{{
    "cognitive_style": "linear|network|hierarchical",
    "information_density_preference": 0.0-1.0,
    "processing_speed": 0.0-1.0,
    "feedback_preference": "反馈偏好描述",
    "learning_style": "学习风格描述"
}}
        """.strip()

    def _get_domain_cognitive_guidance(self, domain_type: DomainType) -> str:
        """获取领域特定的认知分析指导"""
        guidance_map = {
            DomainType.TECHNICAL: "技术领域：关注逻辑推理、系统性思维、问题分解能力",
            DomainType.ACADEMIC: "学术领域：重视批判性思维、证据导向推理、理论应用",
            DomainType.CREATIVE: "创意领域：强调发散思维、联想能力、美学感知",
            DomainType.EDUCATIONAL: "教育领域：关注学习策略、元认知意识、概念理解",
            DomainType.BUSINESS: "商业领域：注重决策思维、风险评估、战略规划",
            DomainType.GENERAL: "通用领域：平衡分析各项认知能力",
        }
        return guidance_map.get(domain_type, guidance_map[DomainType.GENERAL])

    def _get_domain_knowledge_guidance(self, domain_type: DomainType) -> str:
        """获取领域特定的知识分析指导"""
        guidance_map = {
            DomainType.TECHNICAL: "技术领域：识别技术栈熟悉度、算法理解深度、系统设计能力",
            DomainType.ACADEMIC: "学术领域：确定学科背景、研究方法掌握、跨学科整合能力",
            DomainType.CREATIVE: "创意领域：评估美学理论了解度、创作技法、文化素养水平",
            DomainType.EDUCATIONAL: "教育领域：分析学科知识结构、学习策略、知识迁移能力",
            DomainType.BUSINESS: "商业领域：评估商业知识、管理经验、市场理解深度",
            DomainType.GENERAL: "通用领域：评估常识知识广度和深度",
        }
        return guidance_map.get(domain_type, guidance_map[DomainType.GENERAL])

    def _get_domain_interaction_guidance(self, domain_type: DomainType) -> str:
        """获取领域特定的交互分析指导"""
        guidance_map = {
            DomainType.TECHNICAL: "技术领域：关注对代码、文档、技术图表的偏好",
            DomainType.ACADEMIC: "学术领域：分析对理论深度、证据质量的需求",
            DomainType.CREATIVE: "创意领域：评估对灵感激发、美学表达的重视",
            DomainType.EDUCATIONAL: "教育领域：识别学习节奏、认知负荷承受力",
            DomainType.BUSINESS: "商业领域：分析决策速度、风险承受度偏好",
            DomainType.GENERAL: "通用领域：平衡评估各种交互模式偏好",
        }
        return guidance_map.get(domain_type, guidance_map[DomainType.GENERAL])

    def _parse_cognitive_response(self, response: str) -> dict[str, Any]:
        """解析认知分析响应"""
        try:
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
                return self._get_default_cognitive_result()

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"解析认知分析响应失败: {e}")
            return self._get_default_cognitive_result()

    def _parse_knowledge_response(self, response: str) -> dict[str, Any]:
        """解析知识分析响应"""
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
            logger.warning(f"解析知识分析响应失败: {e}")
            return self._get_default_knowledge_result()

    def _parse_interaction_response(self, response: str) -> dict[str, Any]:
        """解析交互分析响应"""
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
            logger.warning(f"解析交互分析响应失败: {e}")
            return self._get_default_interaction_result()

    def _validate_thinking_mode(self, mode: str) -> str:
        """验证思维模式"""
        valid_modes = ["analytical", "intuitive", "creative"]
        return mode if mode in valid_modes else "analytical"

    def _validate_cognitive_style(self, style: str) -> str:
        """验证认知风格"""
        valid_styles = ["linear", "network", "hierarchical"]
        return style if style in valid_styles else "linear"

    def _get_default_cognitive_result(self) -> dict[str, Any]:
        """获取默认认知分析结果"""
        return {
            "thinking_mode": "analytical",
            "cognitive_complexity": 0.5,
            "abstraction_level": 0.5,
            "creativity_tendency": 0.5,
            "reasoning_preference": "平衡推理模式",
        }

    def _get_default_knowledge_result(self) -> dict[str, Any]:
        """获取默认知识分析结果"""
        return {
            "core_domains": ["general"],
            "edge_domains": [],
            "knowledge_depth": {"general": 0.5},
            "cross_domain_ability": 0.5,
            "knowledge_boundaries": [],
        }

    def _get_default_interaction_result(self) -> dict[str, Any]:
        """获取默认交互分析结果"""
        return {
            "cognitive_style": "linear",
            "information_density_preference": 0.5,
            "processing_speed": 0.5,
            "feedback_preference": "平衡反馈",
            "learning_style": "适应性学习",
        }

    def _build_complete_profile(
        self,
        user_id: str,
        cognitive_result: dict[str, Any],
        knowledge_result: dict[str, Any],
        interaction_result: dict[str, Any],
    ) -> UserProfile:
        """构建完整用户画像"""
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
        """创建默认用户画像"""
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


# 注册语义用户建模器
UserModelerFactory.register_modeler("semantic", SemanticUserModeler)
