"""
情境要素提取子模块

基于设计文档第4.2.2节，通过大模型提取和分析当前情境中的关键要素，
包括时间、空间、主题域、约束条件等影响认知处理的环境因素。
"""

import json
import logging
from typing import Any

from aienhance.core.base_architecture import (
    BaseSubModule,
    ProcessingContext,
    ProcessingResult,
)

logger = logging.getLogger(__name__)


class ContextElementsExtractionSubModule(BaseSubModule):
    """情境要素提取子模块"""

    def __init__(self, llm_adapter=None, config: dict[str, Any] = None):
        super().__init__("context_elements_extraction", llm_adapter, config)

    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Context Elements Extraction SubModule")

    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理情境要素提取"""
        try:
            # 构建情境要素提取提示词
            analysis_prompt = self._build_context_extraction_prompt(
                context.query,
                context.session_context,
                context.user_id,
                context.module_outputs,
            )

            # 获取JSON Schema
            context_schema = self._get_context_elements_schema()

            # 使用LLM流式分析情境要素
            logger.info("开始流式情境要素提取分析...")
            analysis_result = ""
            chunk_count = 0
            async for chunk in self.process_with_llm_stream_json(
                analysis_prompt, context_schema, context
            ):
                analysis_result += chunk
                chunk_count += 1
                if chunk_count % 10 == 0:
                    logger.debug(
                        f"情境要素提取已接收 {chunk_count} 个片段，当前长度: {len(analysis_result)}"
                    )

            logger.info(
                f"流式情境要素提取完成，总共接收 {chunk_count} 个片段，总长度: {len(analysis_result)}"
            )

            # 解析JSON结构化数据
            context_elements = self._parse_json_output(analysis_result)

            return ProcessingResult(
                success=True,
                data={
                    "context_elements": context_elements,
                    "analysis_timestamp": context.metadata.get("created_at"),
                    "primary_domain": context_elements.get("domain_context", {}).get(
                        "primary_domain"
                    ),
                    "context_complexity": context_elements.get(
                        "complexity_assessment", {}
                    ).get("overall_complexity", "medium"),
                    "confidence_score": context_elements.get("confidence_score", 0.7),
                },
                metadata={
                    "submodule": "context_elements_extraction",
                    "domains_identified": len(
                        context_elements.get("domain_context", {}).get(
                            "relevant_domains", []
                        )
                    ),
                    "constraints_count": len(
                        context_elements.get("constraint_analysis", {}).get(
                            "active_constraints", []
                        )
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Context elements extraction failed: {e}")
            return ProcessingResult(
                success=False, data={}, metadata={"error": str(e)}, error_message=str(e)
            )

    def _get_context_elements_schema(self) -> dict:
        """获取情境要素提取的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "temporal_context": {
                    "type": "object",
                    "properties": {
                        "time_sensitivity": {
                            "type": "string",
                            "enum": ["immediate", "urgent", "flexible", "long_term"],
                        },
                        "temporal_scope": {
                            "type": "string",
                            "enum": ["current", "historical", "future", "timeless"],
                        },
                        "deadline_pressure": {
                            "type": "string",
                            "enum": ["none", "low", "moderate", "high"],
                        },
                        "temporal_references": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "time_horizon": {
                            "type": "string",
                            "enum": [
                                "minutes",
                                "hours",
                                "days",
                                "weeks",
                                "months",
                                "years",
                            ],
                        },
                    },
                    "required": [
                        "time_sensitivity",
                        "temporal_scope",
                        "deadline_pressure",
                        "temporal_references",
                        "time_horizon",
                    ],
                },
                "spatial_context": {
                    "type": "object",
                    "properties": {
                        "physical_location": {
                            "type": "string",
                            "enum": [
                                "irrelevant",
                                "local",
                                "regional",
                                "national",
                                "global",
                                "virtual",
                            ],
                        },
                        "cultural_context": {
                            "type": "string",
                            "enum": [
                                "universal",
                                "western",
                                "eastern",
                                "regional",
                                "local",
                                "mixed",
                            ],
                        },
                        "geographic_scope": {
                            "type": "string",
                            "enum": [
                                "point",
                                "local",
                                "regional",
                                "national",
                                "international",
                                "global",
                            ],
                        },
                        "location_specificity": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "environmental_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "physical_location",
                        "cultural_context",
                        "geographic_scope",
                        "location_specificity",
                        "environmental_factors",
                    ],
                },
                "domain_context": {
                    "type": "object",
                    "properties": {
                        "primary_domain": {"type": "string"},
                        "secondary_domains": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "relevant_domains": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "domain_boundaries": {
                            "type": "object",
                            "properties": {
                                "well_defined": {"type": "boolean"},
                                "interdisciplinary": {"type": "boolean"},
                                "emerging_field": {"type": "boolean"},
                                "boundary_clarity": {
                                    "type": "string",
                                    "enum": [
                                        "clear",
                                        "fuzzy",
                                        "overlapping",
                                        "undefined",
                                    ],
                                },
                            },
                            "required": [
                                "well_defined",
                                "interdisciplinary",
                                "emerging_field",
                                "boundary_clarity",
                            ],
                        },
                        "domain_expertise_requirements": {
                            "type": "string",
                            "enum": [
                                "none",
                                "basic",
                                "intermediate",
                                "advanced",
                                "expert",
                            ],
                        },
                        "specialized_vocabulary": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "primary_domain",
                        "secondary_domains",
                        "relevant_domains",
                        "domain_boundaries",
                        "domain_expertise_requirements",
                        "specialized_vocabulary",
                    ],
                },
                "stakeholder_context": {
                    "type": "object",
                    "properties": {
                        "primary_audience": {"type": "string"},
                        "secondary_audiences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "audience_characteristics": {
                            "type": "object",
                            "properties": {
                                "expertise_level": {
                                    "type": "string",
                                    "enum": [
                                        "novice",
                                        "intermediate",
                                        "advanced",
                                        "expert",
                                        "mixed",
                                    ],
                                },
                                "familiarity_with_domain": {
                                    "type": "string",
                                    "enum": [
                                        "none",
                                        "basic",
                                        "moderate",
                                        "high",
                                        "expert",
                                    ],
                                },
                                "role_context": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "decision_authority": {
                                    "type": "string",
                                    "enum": [
                                        "none",
                                        "limited",
                                        "moderate",
                                        "high",
                                        "full",
                                    ],
                                },
                            },
                            "required": [
                                "expertise_level",
                                "familiarity_with_domain",
                                "role_context",
                                "decision_authority",
                            ],
                        },
                        "communication_requirements": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "stakeholder_interests": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "primary_audience",
                        "secondary_audiences",
                        "audience_characteristics",
                        "communication_requirements",
                        "stakeholder_interests",
                    ],
                },
                "constraint_analysis": {
                    "type": "object",
                    "properties": {
                        "active_constraints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "severity": {
                                        "type": "string",
                                        "enum": ["low", "moderate", "high", "critical"],
                                    },
                                    "description": {"type": "string"},
                                    "impact_on_solution": {"type": "string"},
                                },
                                "required": [
                                    "type",
                                    "severity",
                                    "description",
                                    "impact_on_solution",
                                ],
                            },
                        },
                        "resource_limitations": {
                            "type": "object",
                            "properties": {
                                "time_constraints": {"type": "boolean"},
                                "information_availability": {
                                    "type": "string",
                                    "enum": [
                                        "abundant",
                                        "sufficient",
                                        "limited",
                                        "scarce",
                                    ],
                                },
                                "computational_resources": {
                                    "type": "string",
                                    "enum": [
                                        "unlimited",
                                        "ample",
                                        "moderate",
                                        "limited",
                                    ],
                                },
                                "domain_expertise_access": {
                                    "type": "string",
                                    "enum": ["available", "limited", "unavailable"],
                                },
                            },
                            "required": [
                                "time_constraints",
                                "information_availability",
                                "computational_resources",
                                "domain_expertise_access",
                            ],
                        },
                        "regulatory_constraints": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "ethical_considerations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "active_constraints",
                        "resource_limitations",
                        "regulatory_constraints",
                        "ethical_considerations",
                    ],
                },
                "information_landscape": {
                    "type": "object",
                    "properties": {
                        "information_density": {
                            "type": "string",
                            "enum": ["sparse", "moderate", "rich", "overwhelming"],
                        },
                        "information_quality": {
                            "type": "string",
                            "enum": ["poor", "mixed", "good", "excellent"],
                        },
                        "information_sources": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "knowledge_gaps": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "uncertainty_levels": {
                            "type": "object",
                            "properties": {
                                "factual_uncertainty": {
                                    "type": "string",
                                    "enum": ["low", "moderate", "high", "extreme"],
                                },
                                "methodological_uncertainty": {
                                    "type": "string",
                                    "enum": ["low", "moderate", "high", "extreme"],
                                },
                                "predictive_uncertainty": {
                                    "type": "string",
                                    "enum": ["low", "moderate", "high", "extreme"],
                                },
                            },
                            "required": [
                                "factual_uncertainty",
                                "methodological_uncertainty",
                                "predictive_uncertainty",
                            ],
                        },
                    },
                    "required": [
                        "information_density",
                        "information_quality",
                        "information_sources",
                        "knowledge_gaps",
                        "uncertainty_levels",
                    ],
                },
                "complexity_assessment": {
                    "type": "object",
                    "properties": {
                        "overall_complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex", "highly_complex"],
                        },
                        "complexity_sources": {
                            "type": "object",
                            "properties": {
                                "conceptual_complexity": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "relational_complexity": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "dynamic_complexity": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                                "contextual_complexity": {
                                    "type": "number",
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                },
                            },
                            "required": [
                                "conceptual_complexity",
                                "relational_complexity",
                                "dynamic_complexity",
                                "contextual_complexity",
                            ],
                        },
                        "complexity_drivers": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "simplification_opportunities": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "overall_complexity",
                        "complexity_sources",
                        "complexity_drivers",
                        "simplification_opportunities",
                    ],
                },
                "contextual_priorities": {
                    "type": "object",
                    "properties": {
                        "primary_priorities": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "secondary_priorities": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "priority_conflicts": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "trade_off_considerations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "primary_priorities",
                        "secondary_priorities",
                        "priority_conflicts",
                        "trade_off_considerations",
                    ],
                },
                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "extraction_notes": {"type": "string"},
            },
            "required": [
                "temporal_context",
                "spatial_context",
                "domain_context",
                "stakeholder_context",
                "constraint_analysis",
                "information_landscape",
                "complexity_assessment",
                "contextual_priorities",
                "confidence_score",
                "extraction_notes",
            ],
        }

    def _build_context_extraction_prompt(
        self,
        query: str,
        session_context: dict[str, Any],
        user_id: str,
        module_outputs: dict[str, Any],
    ) -> str:
        """构建情境要素提取提示词"""

        # 获取历史上下文和用户信息
        conversation_history = session_context.get("conversation_history", [])
        user_profile = session_context.get("user_profile", {})

        # 获取之前模块的分析结果
        user_modeling_result = module_outputs.get("perception.user_modeling", {})
        task_analysis_result = module_outputs.get(
            "context_analysis.task_type_identification", {}
        )
        cognitive_needs_result = module_outputs.get(
            "context_analysis.cognitive_needs_prediction", {}
        )

        prompt = f"""
你是一位情境要素分析专家，需要深入提取和分析当前情境中影响认知处理的关键环境因素。

当前用户问题：{query}

任务分析结果：{task_analysis_result}

认知需求预测：{cognitive_needs_result}

用户画像信息：{user_modeling_result}

用户历史信息：{user_profile}

历史对话样本：{conversation_history[-3:] if conversation_history else []}

请从以下维度提取和分析情境要素，并输出JSON格式结果：

## 分析维度

### 1. 时间情境 (Temporal Context)
分析时间相关的情境因素：
- **时间敏感性**: 任务的时间紧迫程度
- **时间范围**: 涉及的时间跨度（当前、历史、未来）
- **截止压力**: 时间约束带来的压力水平
- **时间参考**: 问题中提到的具体时间要素
- **时间地平线**: 预期的时间规划范围

### 2. 空间情境 (Spatial Context)
分析地理和文化空间因素：
- **物理位置**: 地理位置的相关性
- **文化背景**: 文化环境对问题的影响
- **地理范围**: 涉及的地理空间层次
- **位置特异性**: 特定位置的重要信息
- **环境因素**: 物理环境的影响要素

### 3. 领域情境 (Domain Context)
分析专业领域的情境特征：
- **主要领域**: 核心专业领域识别
- **相关领域**: 涉及的其他专业领域
- **领域边界**: 学科边界的清晰程度
- **专业要求**: 所需的专业知识水平
- **专业术语**: 领域特有的概念和词汇

### 4. 利益相关者情境 (Stakeholder Context)
分析涉及的人员和角色：
- **目标受众**: 主要的信息接收者
- **受众特征**: 专业水平、角色背景等
- **沟通要求**: 特殊的沟通需求
- **利益关切**: 各方关注的重点

### 5. 约束分析 (Constraint Analysis)
识别限制因素和约束条件：
- **主要约束**: 影响解决方案的限制因素
- **资源限制**: 时间、信息、计算等资源约束
- **规范约束**: 法规、政策等外部约束
- **伦理考量**: 道德和伦理方面的考虑

### 6. 信息环境 (Information Landscape)
分析信息的可得性和质量：
- **信息密度**: 可用信息的丰富程度
- **信息质量**: 信息的准确性和可靠性
- **信息来源**: 主要的信息获取渠道
- **知识缺口**: 关键信息的缺失
- **不确定性**: 各种不确定因素的水平

### 7. 复杂度评估 (Complexity Assessment)
评估情境的整体复杂度：
- **复杂度来源**: 概念、关系、动态、环境复杂度
- **复杂度驱动因素**: 导致复杂性的关键因素
- **简化机会**: 可能的复杂度降低策略

### 8. 情境优先级 (Contextual Priorities)
识别情境中的重要性排序：
- **核心优先级**: 最重要的关注点
- **优先级冲突**: 不同优先级间的矛盾
- **权衡考虑**: 需要平衡的因素

## 提取原则
1. **全面性**: 覆盖所有重要的情境维度
2. **准确性**: 基于明确的文本和上下文证据
3. **相关性**: 聚焦于影响认知处理的关键要素
4. **动态性**: 考虑情境的变化和发展趋势

请基于以上框架，深入分析当前情境的要素并生成结构化的JSON输出。
"""

        return prompt

    def _parse_json_output(self, json_output: str) -> dict[str, Any]:
        """解析JSON Schema约束的LLM输出"""
        try:
            # 直接解析JSON，因为通过Schema约束应该确保格式正确
            context_elements = json.loads(json_output)
            logger.info("成功解析JSON Schema约束的情境要素提取结果")
            return context_elements
        except json.JSONDecodeError as e:
            logger.error(f"JSON Schema输出解析失败: {e}")
            logger.warning("回退到默认情境要素")
            return self._create_default_context_elements(json_output)

    def _create_default_context_elements(self, analysis_text: str) -> dict[str, Any]:
        """创建默认情境要素提取结果"""
        return {
            "temporal_context": {
                "time_sensitivity": "flexible",
                "temporal_scope": "current",
                "deadline_pressure": "none",
                "temporal_references": [],
                "time_horizon": "hours",
            },
            "spatial_context": {
                "physical_location": "irrelevant",
                "cultural_context": "universal",
                "geographic_scope": "point",
                "location_specificity": [],
                "environmental_factors": [],
            },
            "domain_context": {
                "primary_domain": "general",
                "secondary_domains": [],
                "relevant_domains": ["general"],
                "domain_boundaries": {
                    "well_defined": False,
                    "interdisciplinary": False,
                    "emerging_field": False,
                    "boundary_clarity": "undefined",
                },
                "domain_expertise_requirements": "basic",
                "specialized_vocabulary": [],
            },
            "stakeholder_context": {
                "primary_audience": "general_user",
                "secondary_audiences": [],
                "audience_characteristics": {
                    "expertise_level": "intermediate",
                    "familiarity_with_domain": "basic",
                    "role_context": ["learner"],
                    "decision_authority": "none",
                },
                "communication_requirements": ["clear_explanation"],
                "stakeholder_interests": ["understanding"],
            },
            "constraint_analysis": {
                "active_constraints": [],
                "resource_limitations": {
                    "time_constraints": False,
                    "information_availability": "sufficient",
                    "computational_resources": "moderate",
                    "domain_expertise_access": "available",
                },
                "regulatory_constraints": [],
                "ethical_considerations": [],
            },
            "information_landscape": {
                "information_density": "moderate",
                "information_quality": "mixed",
                "information_sources": ["general_knowledge"],
                "knowledge_gaps": [],
                "uncertainty_levels": {
                    "factual_uncertainty": "moderate",
                    "methodological_uncertainty": "moderate",
                    "predictive_uncertainty": "moderate",
                },
            },
            "complexity_assessment": {
                "overall_complexity": "moderate",
                "complexity_sources": {
                    "conceptual_complexity": 0.5,
                    "relational_complexity": 0.4,
                    "dynamic_complexity": 0.3,
                    "contextual_complexity": 0.5,
                },
                "complexity_drivers": ["conceptual_ambiguity"],
                "simplification_opportunities": ["structured_breakdown"],
            },
            "contextual_priorities": {
                "primary_priorities": ["accuracy", "clarity"],
                "secondary_priorities": ["completeness"],
                "priority_conflicts": [],
                "trade_off_considerations": ["depth_vs_breadth"],
            },
            "confidence_score": 0.5,
            "extraction_notes": f"基于初始分析的情境要素提取: {analysis_text[:200]}...",
        }
