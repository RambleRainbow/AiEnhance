"""
认知需求预测子模块

基于设计文档第4.2.3节，通过大模型分析用户在当前任务下的认知需求，
预测所需的思维模式、推理策略和支持类型。
"""

import logging
from typing import Any

from aienhance.core.base_architecture import (
    BaseSubModule,
    ProcessingContext,
)

logger = logging.getLogger(__name__)


class CognitiveNeedsPredictionSubModule(BaseSubModule):
    """认知需求预测子模块"""

    def __init__(self, llm_adapter=None, config: dict[str, Any] | None = None):
        super().__init__("cognitive_needs_prediction", llm_adapter, config)

    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Cognitive Needs Prediction SubModule")

    # 使用基类的标准化process方法，只需实现抽象方法

    def _get_output_schema(self) -> dict:
        """获取认知需求预测的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "primary_cognitive_strategy": {
                    "type": "string",
                    "enum": [
                        "analytical_reasoning",
                        "creative_synthesis",
                        "pattern_recognition",
                        "systematic_decomposition",
                        "intuitive_exploration",
                        "comparative_analysis",
                        "causal_reasoning",
                    ],
                },
                "secondary_cognitive_strategies": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "thinking_modes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "application_context": {"type": "string"},
                            "expected_contribution": {"type": "string"},
                        },
                        "required": [
                            "mode",
                            "priority",
                            "application_context",
                            "expected_contribution",
                        ],
                    },
                },
                "memory_activation_patterns": {
                    "type": "object",
                    "properties": {
                        "semantic_activation": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "depth_level": {
                                    "type": "string",
                                    "enum": [
                                        "surface",
                                        "functional",
                                        "conceptual",
                                        "deep",
                                    ],
                                },
                                "domain_areas": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "concept_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "required",
                                "depth_level",
                                "domain_areas",
                                "concept_types",
                            ],
                        },
                        "episodic_activation": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "temporal_scope": {
                                    "type": "string",
                                    "enum": [
                                        "recent",
                                        "historical",
                                        "contextual",
                                        "comprehensive",
                                    ],
                                },
                                "experience_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "relevance_criteria": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "required",
                                "temporal_scope",
                                "experience_types",
                                "relevance_criteria",
                            ],
                        },
                        "procedural_activation": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "skill_categories": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "complexity_level": {
                                    "type": "string",
                                    "enum": [
                                        "basic",
                                        "intermediate",
                                        "advanced",
                                        "expert",
                                    ],
                                },
                                "application_domains": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "required",
                                "skill_categories",
                                "complexity_level",
                                "application_domains",
                            ],
                        },
                    },
                    "required": [
                        "semantic_activation",
                        "episodic_activation",
                        "procedural_activation",
                    ],
                },
                "reasoning_requirements": {
                    "type": "object",
                    "properties": {
                        "logical_reasoning": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "reasoning_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "complexity": {
                                    "type": "string",
                                    "enum": [
                                        "simple",
                                        "moderate",
                                        "complex",
                                        "multi_layered",
                                    ],
                                },
                                "chain_length": {
                                    "type": "string",
                                    "enum": ["short", "medium", "long", "extended"],
                                },
                            },
                            "required": [
                                "required",
                                "reasoning_types",
                                "complexity",
                                "chain_length",
                            ],
                        },
                        "analogical_reasoning": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "source_domains": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "mapping_complexity": {
                                    "type": "string",
                                    "enum": [
                                        "direct",
                                        "structural",
                                        "system",
                                        "pragmatic",
                                    ],
                                },
                                "abstraction_level": {
                                    "type": "string",
                                    "enum": [
                                        "concrete",
                                        "functional",
                                        "relational",
                                        "system",
                                    ],
                                },
                            },
                            "required": [
                                "required",
                                "source_domains",
                                "mapping_complexity",
                                "abstraction_level",
                            ],
                        },
                        "creative_reasoning": {
                            "type": "object",
                            "properties": {
                                "required": {"type": "boolean"},
                                "creativity_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "divergence_level": {
                                    "type": "string",
                                    "enum": [
                                        "focused",
                                        "moderate",
                                        "broad",
                                        "unlimited",
                                    ],
                                },
                                "synthesis_complexity": {
                                    "type": "string",
                                    "enum": ["simple", "moderate", "complex", "novel"],
                                },
                            },
                            "required": [
                                "required",
                                "creativity_types",
                                "divergence_level",
                                "synthesis_complexity",
                            ],
                        },
                    },
                    "required": [
                        "logical_reasoning",
                        "analogical_reasoning",
                        "creative_reasoning",
                    ],
                },
                "support_requirements": {
                    "type": "object",
                    "properties": {
                        "intensity_level": {
                            "type": "string",
                            "enum": [
                                "minimal",
                                "moderate",
                                "substantial",
                                "comprehensive",
                            ],
                        },
                        "guidance_types": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "scaffolding_needs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "priority": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"],
                                    },
                                    "description": {"type": "string"},
                                },
                                "required": ["type", "priority", "description"],
                            },
                        },
                        "interaction_style": {
                            "type": "string",
                            "enum": [
                                "directive",
                                "collaborative",
                                "facilitative",
                                "supportive",
                            ],
                        },
                    },
                    "required": [
                        "intensity_level",
                        "guidance_types",
                        "scaffolding_needs",
                        "interaction_style",
                    ],
                },
                "adaptation_indicators": {
                    "type": "object",
                    "properties": {
                        "user_expertise_level": {
                            "type": "string",
                            "enum": ["novice", "intermediate", "advanced", "expert"],
                        },
                        "cognitive_load_tolerance": {
                            "type": "string",
                            "enum": ["low", "moderate", "high", "very_high"],
                        },
                        "preferred_processing_speed": {
                            "type": "string",
                            "enum": [
                                "slow_thorough",
                                "moderate",
                                "fast_efficient",
                                "adaptive",
                            ],
                        },
                        "learning_orientation": {
                            "type": "string",
                            "enum": [
                                "exploration",
                                "understanding",
                                "application",
                                "mastery",
                            ],
                        },
                    },
                    "required": [
                        "user_expertise_level",
                        "cognitive_load_tolerance",
                        "preferred_processing_speed",
                        "learning_orientation",
                    ],
                },
                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "prediction_rationale": {"type": "string"},
            },
            "required": [
                "primary_cognitive_strategy",
                "secondary_cognitive_strategies",
                "thinking_modes",
                "memory_activation_patterns",
                "reasoning_requirements",
                "support_requirements",
                "adaptation_indicators",
                "confidence_score",
                "prediction_rationale",
            ],
        }

    async def _build_analysis_prompt(
        self, query: str, session_context: dict[str, Any], user_id: str
    ) -> str:
        """构建认知需求预测提示词"""

        # 获取历史上下文和用户信息
        conversation_history = session_context.get("conversation_history", [])
        user_profile = session_context.get("user_profile", {})
        user_profile["user_id"] = user_id  # 使用user_id参数

        # 获取之前模块的分析结果（从session_context中获取）
        user_modeling_result = session_context.get("user_modeling_result", {})
        task_analysis_result = session_context.get("task_analysis_result", {})

        prompt = f"""
你是一位认知需求分析专家，需要基于用户查询、任务类型和用户特征，预测用户的认知需求和所需的思维支持。

当前用户问题：{query}

任务分析结果：{task_analysis_result}

用户画像信息：{user_modeling_result}

用户历史信息：{user_profile}

历史对话样本：{conversation_history[-3:] if conversation_history else []}

请从以下维度分析用户的认知需求，并输出JSON格式结果：

## 分析维度

### 1. 主要认知策略识别
根据任务类型和用户特征，确定最适合的认知处理策略：
- **分析推理 (analytical_reasoning)**: 逻辑分解、系统分析
- **创意综合 (creative_synthesis)**: 创新思考、概念整合
- **模式识别 (pattern_recognition)**: 规律发现、类型归纳
- **系统分解 (systematic_decomposition)**: 结构化拆解、层次分析
- **直觉探索 (intuitive_exploration)**: 开放性思考、灵感激发
- **比较分析 (comparative_analysis)**: 对比评估、差异识别
- **因果推理 (causal_reasoning)**: 原因分析、影响评估

### 2. 思维模式需求
确定需要激活的具体思维模式及其优先级：
- 批判性思维、系统思维、设计思维、辩证思维等
- 每种思维模式的应用场景和预期贡献

### 3. 记忆激活模式
预测需要激活的记忆类型和深度：
- **语义记忆**: 概念知识、领域知识的激活需求
- **情景记忆**: 经验、案例、历史事件的激活需求
- **程序记忆**: 技能、方法、操作流程的激活需求

### 4. 推理需求分析
确定所需的推理类型和复杂度：
- **逻辑推理**: 演绎、归纳、溯因推理的需求
- **类比推理**: 跨域映射、结构类比的需求
- **创造推理**: 发散思维、概念组合的需求

### 5. 支持需求预测
分析用户需要的认知支持类型和强度：
- 指导类型：指令式、协作式、促进式、支持式
- 支架需求：概念框架、思维工具、分步引导
- 交互风格：适应用户的偏好和能力水平

### 6. 个性化适应指标
基于用户特征调整认知支持：
- 专业水平：新手、中级、高级、专家
- 认知负荷承受能力
- 处理速度偏好
- 学习导向：探索、理解、应用、精通

## 分析原则
1. **任务导向**: 以任务类型和复杂度为主要依据
2. **用户适配**: 结合用户的认知特征和偏好
3. **渐进支持**: 提供适当的认知支架，避免过度或不足
4. **动态调整**: 考虑用户的成长和变化需求

请基于以上框架，深入分析用户的认知需求并生成结构化的JSON输出。
"""

        return prompt

    async def _build_result_data(
        self, parsed_output: dict[str, Any], context: ProcessingContext
    ) -> dict[str, Any]:
        """构建处理结果的数据部分"""
        return {
            "cognitive_needs": parsed_output,
            "analysis_timestamp": context.metadata.get("created_at"),
            "primary_cognitive_strategy": parsed_output.get(
                "primary_cognitive_strategy"
            ),
            "confidence_score": parsed_output.get("confidence_score", 0.7),
        }

    def _build_result_metadata(
        self, parsed_output: dict[str, Any], analysis_prompt: str
    ) -> dict[str, Any]:
        """构建处理结果的元数据部分"""
        return {
            "submodule": "cognitive_needs_prediction",
            "thinking_modes_required": parsed_output.get("thinking_modes", []),
            "support_intensity": parsed_output.get("support_requirements", {}).get(
                "intensity_level", "moderate"
            ),
            "confidence_score": parsed_output.get("confidence_score", 0.7),
            "prompt_tokens": len(analysis_prompt.split()),
        }

    def _create_default_output(self, analysis_text: str = "") -> dict[str, Any]:
        """创建默认认知需求预测结果"""
        return {
            "primary_cognitive_strategy": "analytical_reasoning",
            "secondary_cognitive_strategies": ["pattern_recognition"],
            "thinking_modes": [
                {
                    "mode": "critical_thinking",
                    "priority": "medium",
                    "application_context": "问题分析",
                    "expected_contribution": "逻辑评估",
                }
            ],
            "memory_activation_patterns": {
                "semantic_activation": {
                    "required": True,
                    "depth_level": "functional",
                    "domain_areas": ["general"],
                    "concept_types": ["basic_concepts"],
                },
                "episodic_activation": {
                    "required": False,
                    "temporal_scope": "recent",
                    "experience_types": [],
                    "relevance_criteria": [],
                },
                "procedural_activation": {
                    "required": False,
                    "skill_categories": [],
                    "complexity_level": "basic",
                    "application_domains": [],
                },
            },
            "reasoning_requirements": {
                "logical_reasoning": {
                    "required": True,
                    "reasoning_types": ["deductive"],
                    "complexity": "moderate",
                    "chain_length": "medium",
                },
                "analogical_reasoning": {
                    "required": False,
                    "source_domains": [],
                    "mapping_complexity": "direct",
                    "abstraction_level": "concrete",
                },
                "creative_reasoning": {
                    "required": False,
                    "creativity_types": [],
                    "divergence_level": "focused",
                    "synthesis_complexity": "simple",
                },
            },
            "support_requirements": {
                "intensity_level": "moderate",
                "guidance_types": ["structural_guidance"],
                "scaffolding_needs": [
                    {
                        "type": "conceptual_framework",
                        "priority": "medium",
                        "description": "基础概念框架支持",
                    }
                ],
                "interaction_style": "collaborative",
            },
            "adaptation_indicators": {
                "user_expertise_level": "intermediate",
                "cognitive_load_tolerance": "moderate",
                "preferred_processing_speed": "moderate",
                "learning_orientation": "understanding",
            },
            "confidence_score": 0.5,
            "prediction_rationale": (
                f"基于初始分析的认知需求预测: {analysis_text[:200]}..."
            ),
        }
