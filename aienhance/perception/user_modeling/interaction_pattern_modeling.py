"""
交互模式维度建模子模块

基于设计文档第4.1.3节，了解用户的思维节奏、信息接受偏好、认知负荷阈值。
"""

import logging
from datetime import datetime
from typing import Any

from aienhance.core.base_architecture import (
    BaseSubModule,
    ProcessingContext,
    ProcessingResult,
)

logger = logging.getLogger(__name__)


class InteractionPatternModelingSubModule(BaseSubModule):
    """交互模式维度建模子模块"""

    def __init__(self, llm_adapter=None, config=None):
        super().__init__("interaction_pattern_modeling", llm_adapter, config)

    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Interaction Pattern Modeling SubModule")

    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理交互模式维度建模"""
        try:
            # 构建交互模式分析提示词
            analysis_prompt = self._build_interaction_analysis_prompt(
                context.query, context.session_context, context.user_id
            )

            # 获取JSON Schema
            interaction_schema = self._get_interaction_pattern_schema()

            # 使用LLM流式分析用户交互模式（结构化输出）
            logger.info("开始流式交互模式建模分析...")
            analysis_result = ""
            chunk_count = 0
            async for chunk in self.process_with_llm_stream_json(
                analysis_prompt, interaction_schema, context
            ):
                analysis_result += chunk
                chunk_count += 1
                if chunk_count % 10 == 0:
                    logger.debug(
                        f"交互建模已接收 {chunk_count} 个片段，"
                        f"当前长度: {len(analysis_result)}"
                    )

            logger.info(
                f"流式交互建模完成，总共接收 {chunk_count} 个片段，"
                f"总长度: {len(analysis_result)}"
            )

            # 解析JSON结构化数据
            interaction_profile = self._parse_json_output(analysis_result)

            # 添加实时交互数据
            interaction_profile = self._enhance_with_realtime_data(
                interaction_profile, context.session_context
            )

            return ProcessingResult(
                success=True,
                data={
                    "interaction_profile": interaction_profile,
                    "analysis_timestamp": context.metadata.get("created_at"),
                    "interaction_preferences": interaction_profile.get(
                        "preferences_summary", {}
                    ),
                    "cognitive_load_profile": interaction_profile.get(
                        "cognitive_load", {}
                    ),
                },
                metadata={
                    "submodule": "interaction_pattern_modeling",
                    "response_pattern": interaction_profile.get("response_timing", {}),
                    "preferred_complexity": interaction_profile.get(
                        "information_processing", {}
                    ).get("complexity_preference"),
                },
            )

        except Exception as e:
            logger.error(f"Interaction pattern modeling failed: {e}")
            return ProcessingResult(
                success=False, data={}, metadata={"error": str(e)}, error_message=str(e)
            )

    def _get_interaction_pattern_schema(self) -> dict:
        """获取交互模式分析的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "information_processing": {
                    "type": "object",
                    "properties": {
                        "speed_preference": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": [
                                        "fast_response",
                                        "deep_thinking",
                                        "balanced",
                                    ],
                                },
                                "score": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "evidence": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "patterns": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["type", "score", "evidence", "patterns"],
                        },
                        "complexity_preference": {
                            "type": "object",
                            "properties": {
                                "level": {
                                    "type": "string",
                                    "enum": ["simple", "moderate", "complex"],
                                },
                                "tolerance": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "examples": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "breakdown_needs": {"type": "boolean"},
                            },
                            "required": [
                                "level",
                                "tolerance",
                                "examples",
                                "breakdown_needs",
                            ],
                        },
                        "information_density": {
                            "type": "object",
                            "properties": {
                                "preferred_density": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high"],
                                },
                                "adaptation_ability": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "overload_indicators": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "preferred_density",
                                "adaptation_ability",
                                "overload_indicators",
                            ],
                        },
                    },
                    "required": [
                        "speed_preference",
                        "complexity_preference",
                        "information_density",
                    ],
                },
                "attention_patterns": {
                    "type": "object",
                    "properties": {
                        "focus_style": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["deep_focus", "broad_scan", "mixed"],
                                },
                                "sustainability": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "context_switching": {
                                    "type": "string",
                                    "enum": ["frequent", "moderate", "rare"],
                                },
                                "evidence": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "type",
                                "sustainability",
                                "context_switching",
                                "evidence",
                            ],
                        },
                        "engagement_rhythm": {
                            "type": "object",
                            "properties": {
                                "session_length": {
                                    "type": "string",
                                    "enum": ["short", "medium", "long"],
                                },
                                "intensity_pattern": {
                                    "type": "string",
                                    "enum": ["consistent", "variable", "peaks"],
                                },
                                "break_needs": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "optimal_timing": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "session_length",
                                "intensity_pattern",
                                "break_needs",
                                "optimal_timing",
                            ],
                        },
                    },
                    "required": ["focus_style", "engagement_rhythm"],
                },
                "cognitive_load": {
                    "type": "object",
                    "properties": {
                        "multitasking_ability": {
                            "type": "object",
                            "properties": {
                                "score": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "concurrent_concepts": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 10,
                                },
                                "performance_degradation": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "examples": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "score",
                                "concurrent_concepts",
                                "performance_degradation",
                                "examples",
                            ],
                        },
                        "threshold_management": {
                            "type": "object",
                            "properties": {
                                "overload_threshold": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high"],
                                },
                                "recovery_speed": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "warning_signs": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "mitigation_strategies": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "overload_threshold",
                                "recovery_speed",
                                "warning_signs",
                                "mitigation_strategies",
                            ],
                        },
                    },
                    "required": ["multitasking_ability", "threshold_management"],
                },
                "interaction_preferences": {
                    "type": "object",
                    "properties": {
                        "communication_style": {
                            "type": "object",
                            "properties": {
                                "formality": {
                                    "type": "string",
                                    "enum": ["formal", "semi_formal", "casual"],
                                },
                                "detail_level": {
                                    "type": "string",
                                    "enum": ["brief", "moderate", "detailed"],
                                },
                                "structure_preference": {
                                    "type": "string",
                                    "enum": ["linear", "hierarchical", "network"],
                                },
                                "examples": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "formality",
                                "detail_level",
                                "structure_preference",
                                "examples",
                            ],
                        },
                        "feedback_needs": {
                            "type": "object",
                            "properties": {
                                "frequency": {
                                    "type": "string",
                                    "enum": ["high", "medium", "low"],
                                },
                                "type": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "confirmation",
                                            "progress",
                                            "clarification",
                                        ],
                                    },
                                },
                                "timing": {
                                    "type": "string",
                                    "enum": ["immediate", "delayed", "batch"],
                                },
                                "evidence": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["frequency", "type", "timing", "evidence"],
                        },
                        "personalization_level": {
                            "type": "object",
                            "properties": {
                                "desired_level": {
                                    "type": "string",
                                    "enum": ["minimal", "moderate", "high"],
                                },
                                "adaptation_areas": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "flexibility": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                            },
                            "required": [
                                "desired_level",
                                "adaptation_areas",
                                "flexibility",
                            ],
                        },
                    },
                    "required": [
                        "communication_style",
                        "feedback_needs",
                        "personalization_level",
                    ],
                },
                "response_timing": {
                    "type": "object",
                    "properties": {
                        "average_response_time": {
                            "type": "string",
                            "enum": ["快速", "正常", "慢速"],
                        },
                        "variability": {
                            "type": "string",
                            "enum": ["consistent", "variable"],
                        },
                        "context_dependency": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "patterns": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "average_response_time",
                        "variability",
                        "context_dependency",
                        "patterns",
                    ],
                },
                "preferences_summary": {
                    "type": "object",
                    "properties": {
                        "optimal_interaction_mode": {"type": "string"},
                        "key_adaptations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "avoid_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "optimal_interaction_mode",
                        "key_adaptations",
                        "avoid_patterns",
                    ],
                },
                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "analysis_notes": {"type": "string"},
            },
            "required": [
                "information_processing",
                "attention_patterns",
                "cognitive_load",
                "interaction_preferences",
                "response_timing",
                "preferences_summary",
                "confidence_score",
                "analysis_notes",
            ],
        }

    def _build_interaction_analysis_prompt(
        self, query: str, session_context: dict[str, Any], user_id: str  # noqa: ARG002
    ) -> str:
        """构建交互模式分析提示词"""

        conversation_history = session_context.get("conversation_history", [])
        response_times = session_context.get("response_times", [])
        user_feedback = session_context.get("user_feedback", [])

        # 计算交互统计信息
        interaction_stats = self._calculate_interaction_stats(
            conversation_history, response_times
        )

        prompt = f"""
你是一位交互设计和认知科学专家，需要分析用户的交互模式和认知偏好。

当前用户问题：{query}

交互统计信息：{interaction_stats}

用户反馈历史：{user_feedback[-3:] if user_feedback else []}

对话模式样本：{[item.get("query", "") for item in conversation_history[-5:]]}

请从以下维度分析用户的交互模式，并输出JSON格式结果：

## 分析维度

### 1. 信息处理速度和偏好
- 快速响应 vs 深度思考倾向
- 信息消化速度
- 复杂度接受阈值

### 2. 注意力模式和认知节奏
- 深度聚焦 vs 广度扫描
- 注意力持续时间
- 认知切换频率

### 3. 认知负荷管理
- 同时处理多个概念的能力
- 信息过载的阈值
- 优先级处理方式

### 4. 交互偏好和适应性
- 交互频率偏好
- 反馈需求程度
- 个性化程度需求

请基于提供的交互数据进行深入分析，提供结构化的交互模式评估结果：
"""

        return prompt

    def _parse_json_output(self, json_output: str) -> dict[str, Any]:
        """解析JSON Schema约束的LLM输出"""
        import json

        try:
            # 直接解析JSON，因为通过Schema约束应该确保格式正确
            interaction_profile = json.loads(json_output)
            logger.info("成功解析JSON Schema约束的交互模式分析结果")
            return interaction_profile
        except json.JSONDecodeError as e:
            logger.error(f"JSON Schema输出解析失败: {e}")
            logger.warning("回退到默认交互模式画像")
            return self._create_default_interaction_profile(json_output)

    def _calculate_interaction_stats(
        self, conversation_history: list, response_times: list
    ) -> dict[str, Any]:
        """计算交互统计信息"""
        if not conversation_history:
            return {"message": "无足够历史数据"}

        stats = {
            "total_interactions": len(conversation_history),
            "average_query_length": sum(
                len(item.get("query", "")) for item in conversation_history
            )
            / len(conversation_history),
            "session_duration": "未知",
            "interaction_frequency": "未知",
        }

        if response_times:
            stats["average_response_time"] = sum(response_times) / len(response_times)
            stats["response_time_variance"] = (
                "计算方差" if len(response_times) > 1 else "单次响应"
            )

        # 分析对话复杂度
        complex_queries = sum(
            1
            for item in conversation_history
            if len(item.get("query", "")) > 100 or "?" in item.get("query", "")
        )
        stats["complex_query_ratio"] = (
            complex_queries / len(conversation_history) if conversation_history else 0
        )

        return stats

    def _enhance_with_realtime_data(
        self, profile: dict[str, Any], session_context: dict[str, Any]
    ) -> dict[str, Any]:
        """用实时交互数据增强画像"""
        current_session = session_context.get("current_session", {})

        # 添加当前会话的实时指标
        if "session_start_time" in current_session:
            session_duration = datetime.now() - current_session["session_start_time"]
            profile["current_session"] = {
                "duration_minutes": session_duration.total_seconds() / 60,
                "interaction_count": current_session.get("interaction_count", 0),
                "complexity_trend": current_session.get("complexity_trend", "stable"),
            }

        return profile

    def _create_default_interaction_profile(self, analysis_text: str) -> dict[str, Any]:
        """创建默认交互模式画像"""
        return {
            "information_processing": {
                "speed_preference": {
                    "type": "balanced",
                    "score": 0.5,
                    "evidence": ["初始观察"],
                    "patterns": ["待观察"],
                },
                "complexity_preference": {
                    "level": "moderate",
                    "tolerance": 0.5,
                    "examples": [],
                    "breakdown_needs": True,
                },
                "information_density": {
                    "preferred_density": "medium",
                    "adaptation_ability": 0.5,
                    "overload_indicators": [],
                },
            },
            "attention_patterns": {
                "focus_style": {
                    "type": "mixed",
                    "sustainability": 0.5,
                    "context_switching": "moderate",
                    "evidence": ["需要更多观察"],
                },
                "engagement_rhythm": {
                    "session_length": "medium",
                    "intensity_pattern": "consistent",
                    "break_needs": 0.3,
                    "optimal_timing": [],
                },
            },
            "cognitive_load": {
                "multitasking_ability": {
                    "score": 0.5,
                    "concurrent_concepts": 3,
                    "performance_degradation": 0.3,
                    "examples": [],
                },
                "threshold_management": {
                    "overload_threshold": "medium",
                    "recovery_speed": 0.5,
                    "warning_signs": [],
                    "mitigation_strategies": [],
                },
            },
            "interaction_preferences": {
                "communication_style": {
                    "formality": "semi_formal",
                    "detail_level": "moderate",
                    "structure_preference": "hierarchical",
                    "examples": [],
                },
                "feedback_needs": {
                    "frequency": "medium",
                    "type": ["confirmation", "progress"],
                    "timing": "immediate",
                    "evidence": [],
                },
                "personalization_level": {
                    "desired_level": "moderate",
                    "adaptation_areas": [],
                    "flexibility": 0.7,
                },
            },
            "response_timing": {
                "average_response_time": "正常",
                "variability": "consistent",
                "context_dependency": [],
                "patterns": [],
            },
            "preferences_summary": {
                "optimal_interaction_mode": "平衡的交互方式，中等复杂度",
                "key_adaptations": ["观察用户反馈", "逐步调整复杂度"],
                "avoid_patterns": ["信息过载", "过于简化"],
            },
            "confidence_score": 0.3,
            "analysis_notes": f"基于初始交互的交互模式分析: {analysis_text[:200]}...",
        }

