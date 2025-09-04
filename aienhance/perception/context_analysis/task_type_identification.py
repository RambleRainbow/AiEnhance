"""
任务类型识别子模块

基于设计文档第4.2.1节，通过大模型分析用户查询的任务类型和特征，
为后续认知处理提供任务导向的指导。
"""

import logging
from typing import Any

from aienhance.core.base_architecture import (
    BaseSubModule,
    ProcessingContext,
)

logger = logging.getLogger(__name__)


class TaskTypeIdentificationSubModule(BaseSubModule):
    """任务类型识别子模块"""

    def __init__(self, llm_adapter=None, config: dict[str, Any] | None = None):
        super().__init__("task_type_identification", llm_adapter, config)

    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Task Type Identification SubModule")

    # 使用基类的标准化process方法，只需实现抽象方法

    def _get_output_schema(self) -> dict:
        """获取任务类型分析的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "primary_task_type": {
                    "type": "string",
                    "enum": [
                        "analytical",
                        "creative",
                        "exploratory",
                        "retrieval",
                        "problem_solving",
                        "learning",
                        "decision_making",
                    ],
                },
                "secondary_task_types": {"type": "array", "items": {"type": "string"}},
                "task_categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "relevance_score": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                            },
                            "indicators": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["category", "relevance_score", "indicators"],
                    },
                },
                "task_complexity": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "string",
                            "enum": ["simple", "medium", "complex", "expert"],
                        },
                        "dimensions": {
                            "type": "object",
                            "properties": {
                                "cognitive_load": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "domain_specificity": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "multi_step_reasoning": {"type": "boolean"},
                                "creative_thinking_required": {"type": "boolean"},
                            },
                            "required": [
                                "cognitive_load",
                                "domain_specificity",
                                "multi_step_reasoning",
                                "creative_thinking_required",
                            ],
                        },
                    },
                    "required": ["level", "dimensions"],
                },
                "intent_analysis": {
                    "type": "object",
                    "properties": {
                        "primary_intent": {"type": "string"},
                        "secondary_intents": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "goal_clarity": {
                            "type": "string",
                            "enum": ["clear", "moderate", "vague", "ambiguous"],
                        },
                        "urgency_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "scope_analysis": {
                            "type": "object",
                            "properties": {
                                "breadth": {
                                    "type": "string",
                                    "enum": [
                                        "narrow",
                                        "focused",
                                        "broad",
                                        "comprehensive",
                                    ],
                                },
                                "depth": {
                                    "type": "string",
                                    "enum": [
                                        "surface",
                                        "functional",
                                        "detailed",
                                        "expert",
                                    ],
                                },
                                "time_horizon": {
                                    "type": "string",
                                    "enum": [
                                        "immediate",
                                        "short_term",
                                        "long_term",
                                        "ongoing",
                                    ],
                                },
                            },
                            "required": ["breadth", "depth", "time_horizon"],
                        },
                    },
                    "required": [
                        "primary_intent",
                        "secondary_intents",
                        "goal_clarity",
                        "urgency_indicators",
                        "scope_analysis",
                    ],
                },
                "processing_requirements": {
                    "type": "object",
                    "properties": {
                        "memory_activation_needs": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "reasoning_patterns_required": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "information_sources_needed": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "output_format_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "memory_activation_needs",
                        "reasoning_patterns_required",
                        "information_sources_needed",
                        "output_format_preferences",
                    ],
                },
                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "analysis_notes": {"type": "string"},
            },
            "required": [
                "primary_task_type",
                "secondary_task_types",
                "task_categories",
                "task_complexity",
                "intent_analysis",
                "processing_requirements",
                "confidence_score",
                "analysis_notes",
            ],
        }

    async def _build_analysis_prompt(
        self, query: str, session_context: dict[str, Any], user_id: str
    ) -> str:
        """构建任务类型分析提示词"""

        # 获取历史对话上下文
        conversation_history = session_context.get("conversation_history", [])
        user_profile = session_context.get("user_profile", {})
        user_profile["user_id"] = user_id  # 使用user_id参数
        previous_tasks = session_context.get("previous_task_types", [])

        prompt = f"""
你是一位专业的任务类型分析专家，需要深入分析用户查询的任务类型和处理需求。

当前用户问题：{query}

用户历史信息：{user_profile}

之前的任务类型：{previous_tasks}

历史对话样本：{conversation_history[-3:] if conversation_history else []}

请从以下维度分析用户的任务类型，并输出JSON格式结果：

## 分析维度

### 1. 主要任务类型识别
- **分析型任务 (analytical)**: 需要分解、比较、评价的任务
- **创造型任务 (creative)**: 需要产生新想法、设计、创新的任务
- **探索型任务 (exploratory)**: 需要调研、了解、发现的任务
- **检索型任务 (retrieval)**: 需要获取特定信息或知识的任务
- **问题解决型 (problem_solving)**: 需要解决具体问题的任务
- **学习型任务 (learning)**: 需要掌握新知识或技能的任务
- **决策型任务 (decision_making)**: 需要做出选择或判断的任务

### 2. 任务复杂度分析
- **认知负荷评估**: 任务对用户认知资源的要求
- **领域专业性**: 任务所需的专业知识程度
- **多步骤推理**: 是否需要复杂的逻辑链条
- **创造性思维**: 是否需要发散性思维

### 3. 意图分析
- **目标清晰度**: 用户目标的明确程度
- **范围界定**: 任务的广度和深度要求
- **时间紧迫性**: 任务的时间敏感性

### 4. 处理需求预测
- **记忆激活需求**: 需要什么类型的背景知识
- **推理模式要求**: 需要什么样的思维方式
- **信息源需求**: 需要什么类型的信息支持
- **输出格式偏好**: 用户可能偏好的回答形式

## 关键分析线索

### 语言指标
- **分析词汇**: "分析"、"比较"、"评价"、"为什么"、"原因"
- **创造词汇**: "设计"、"创新"、"想法"、"如何做"、"方案"
- **探索词汇**: "了解"、"探索"、"可能性"、"什么是"、"有哪些"
- **问题解决词汇**: "解决"、"处理"、"应对"、"改进"、"优化"

### 上下文线索
- **对话历史**: 前面讨论的主题和深度
- **用户背景**: 专业领域和知识水平
- **问题表述**: 问题的具体性和复杂性

请基于以上分析框架，深入分析用户任务并生成结构化的JSON输出。
"""

        return prompt

    async def _build_result_data(
        self, parsed_output: dict[str, Any], context: ProcessingContext
    ) -> dict[str, Any]:
        """构建处理结果的数据部分"""
        return {
            "task_analysis": parsed_output,
            "analysis_timestamp": context.metadata.get("created_at"),
            "primary_task_type": parsed_output.get("primary_task_type"),
            "confidence_score": parsed_output.get("confidence_score", 0.7),
        }

    def _build_result_metadata(
        self, parsed_output: dict[str, Any], analysis_prompt: str
    ) -> dict[str, Any]:
        """构建处理结果的元数据部分"""
        return {
            "submodule": "task_type_identification",
            "task_categories": parsed_output.get("task_categories", []),
            "complexity_level": parsed_output.get("task_complexity", {}).get(
                "level", "medium"
            ),
            "confidence_score": parsed_output.get("confidence_score", 0.7),
            "prompt_tokens": len(analysis_prompt.split()),
        }

    def _create_default_output(self, analysis_text: str = "") -> dict[str, Any]:
        """创建默认任务分析结果"""
        return {
            "primary_task_type": "retrieval",
            "secondary_task_types": [],
            "task_categories": [
                {
                    "category": "general_inquiry",
                    "relevance_score": 0.7,
                    "indicators": ["初始交互"],
                }
            ],
            "task_complexity": {
                "level": "medium",
                "dimensions": {
                    "cognitive_load": 0.5,
                    "domain_specificity": 0.3,
                    "multi_step_reasoning": False,
                    "creative_thinking_required": False,
                },
            },
            "intent_analysis": {
                "primary_intent": "获取信息",
                "secondary_intents": [],
                "goal_clarity": "moderate",
                "urgency_indicators": [],
                "scope_analysis": {
                    "breadth": "focused",
                    "depth": "functional",
                    "time_horizon": "immediate",
                },
            },
            "processing_requirements": {
                "memory_activation_needs": ["基础知识检索"],
                "reasoning_patterns_required": ["直接回答"],
                "information_sources_needed": ["一般知识库"],
                "output_format_preferences": ["结构化文本"],
            },
            "confidence_score": 0.5,
            "analysis_notes": f"基于初始分析的任务类型识别: {analysis_text[:200]}...",
        }
