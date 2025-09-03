"""
认知能力维度建模子模块

基于设计文档第4.1.1节，评估用户的抽象思维能力、逻辑推理偏好、概念联想习惯等认知特征。
"""

from typing import Dict, Any
import json
import logging
from aienhance.core.base_architecture import BaseSubModule, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class CognitiveAbilityModelingSubModule(BaseSubModule):
    """认知能力维度建模子模块"""
    
    def __init__(self, llm_adapter=None, config: Dict[str, Any] = None):
        super().__init__("cognitive_ability_modeling", llm_adapter, config)
        
    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Cognitive Ability Modeling SubModule")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理认知能力维度建模"""
        try:
            # 构建分析提示词
            analysis_prompt = self._build_analysis_prompt(
                context.query,
                context.session_context,
                context.user_id
            )
            
            # 获取JSON Schema
            cognitive_schema = self._get_cognitive_analysis_schema()
            
            # 使用LLM流式分析用户认知能力特征
            logger.info("开始流式认知能力建模分析...")
            analysis_result = ""
            chunk_count = 0
            async for chunk in self.process_with_llm_stream_json(
                analysis_prompt, 
                cognitive_schema, 
                context
            ):
                analysis_result += chunk
                chunk_count += 1
                if chunk_count % 10 == 0:
                    logger.debug(f"认知建模已接收 {chunk_count} 个片段，当前长度: {len(analysis_result)}")
            
            logger.info(f"流式认知建模完成，总共接收 {chunk_count} 个片段，总长度: {len(analysis_result)}")
            
            # 解析JSON结构化数据
            cognitive_profile = self._parse_json_output(analysis_result)
            
            return ProcessingResult(
                success=True,
                data={
                    "cognitive_profile": cognitive_profile,
                    "analysis_timestamp": context.metadata.get("created_at"),
                    "confidence_score": cognitive_profile.get("confidence_score", 0.7)
                },
                metadata={
                    "submodule": "cognitive_ability_modeling",
                    "prompt_tokens": len(analysis_prompt.split()),
                    "analysis_dimensions": list(cognitive_profile.keys())
                }
            )
            
        except Exception as e:
            logger.error(f"Cognitive ability modeling failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    def _get_cognitive_analysis_schema(self) -> dict:
        """获取认知分析的JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "thinking_style": {
                    "type": "object",
                    "properties": {
                        "abstract_vs_concrete": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "description": {"type": "string"},
                                "evidence": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["score", "description", "evidence"]
                        },
                        "deductive_vs_inductive": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "description": {"type": "string"},
                                "evidence": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["score", "description", "evidence"]
                        },
                        "analogy_usage": {
                            "type": "object",
                            "properties": {
                                "frequency": {"type": "string", "enum": ["low", "medium", "high"]},
                                "quality": {"type": "string", "enum": ["basic", "advanced"]},
                                "examples": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["frequency", "quality", "examples"]
                        }
                    },
                    "required": ["abstract_vs_concrete", "deductive_vs_inductive", "analogy_usage"]
                },
                "cognitive_complexity": {
                    "type": "object",
                    "properties": {
                        "concept_depth": {
                            "type": "object",
                            "properties": {
                                "level": {"type": "string", "enum": ["basic", "intermediate", "advanced"]},
                                "evidence": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["level", "evidence"]
                        },
                        "relation_understanding": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "types": {"type": "array", "items": {"type": "string"}},
                                "examples": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["score", "types", "examples"]
                        }
                    },
                    "required": ["concept_depth", "relation_understanding"]
                },
                "creativity_tendency": {
                    "type": "object",
                    "properties": {
                        "divergent_vs_convergent": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "description": {"type": "string"},
                                "evidence": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["score", "description", "evidence"]
                        },
                        "cross_domain_thinking": {
                            "type": "object",
                            "properties": {
                                "frequency": {"type": "string", "enum": ["rare", "occasional", "frequent"]},
                                "domains": {"type": "array", "items": {"type": "string"}},
                                "examples": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["frequency", "domains", "examples"]
                        }
                    },
                    "required": ["divergent_vs_convergent", "cross_domain_thinking"]
                },
                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "analysis_notes": {"type": "string"}
            },
            "required": ["thinking_style", "cognitive_complexity", "creativity_tendency", "confidence_score", "analysis_notes"]
        }
    
    def _build_analysis_prompt(self, query: str, session_context: Dict[str, Any], user_id: str) -> str:
        """构建认知能力分析提示词"""
        
        # 获取历史对话上下文
        conversation_history = session_context.get("conversation_history", [])
        previous_queries = [item.get("query", "") for item in conversation_history[-5:]]
        
        prompt = f"""
你是一位认知心理学专家，需要分析用户的认知能力特征。

当前用户问题：{query}

历史问题模式：{previous_queries}

请从以下维度分析用户的认知特征：

## 分析维度

### 1. 思维模式识别
- 抽象思维 vs 具体思维倾向（0.0=极具体，1.0=极抽象）
- 演绎推理 vs 归纳推理偏好（0.0=演绎，1.0=归纳）
- 类比使用频率和质量

### 2. 认知复杂度评估  
- 概念深度水平：basic/intermediate/advanced
- 关系理解能力和类型（因果、条件、类比等）
- 多层次概念处理能力

### 3. 创造性思维倾向
- 发散 vs 收敛思维倾向（0.0=收敛，1.0=发散）
- 跨领域思维频率和涉及领域
- 创新性问题处理方式

请基于用户问题的表述方式、概念使用、逻辑结构等特征进行深入分析，提供具体的行为证据和例子。
"""
        
        return prompt
    
    def _parse_json_output(self, json_output: str) -> Dict[str, Any]:
        """解析JSON Schema约束的LLM输出"""
        try:
            import json
            # 直接解析JSON，因为通过Schema约束应该确保格式正确
            cognitive_profile = json.loads(json_output)
            logger.info("成功解析JSON Schema约束的认知分析结果")
            return cognitive_profile
        except json.JSONDecodeError as e:
            logger.error(f"JSON Schema输出解析失败: {e}")
            logger.warning("回退到默认认知画像")
            return self._create_default_profile(json_output)
    
    def _parse_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """解析LLM输出为结构化认知画像数据"""
        try:
            # 尝试从输出中提取JSON
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_output[json_start:json_end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                # 如果没有找到JSON，返回基础结构
                return self._create_default_profile(llm_output)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON output: {e}")
            return self._create_default_profile(llm_output)
    
    def _create_default_profile(self, analysis_text: str) -> Dict[str, Any]:
        """创建默认认知画像结构"""
        return {
            "thinking_style": {
                "abstract_vs_concrete": {
                    "score": 0.5,
                    "description": "需要更多信息来判断",
                    "evidence": ["分析文本不完整"]
                },
                "deductive_vs_inductive": {
                    "score": 0.5,
                    "description": "需要更多交互来确定",
                    "evidence": ["初始判断"]
                },
                "analogy_usage": {
                    "frequency": "medium",
                    "quality": "basic",
                    "examples": []
                }
            },
            "cognitive_complexity": {
                "concept_depth": {
                    "level": "intermediate",
                    "evidence": ["基于初始问题判断"]
                },
                "relation_understanding": {
                    "score": 0.5,
                    "types": ["基础关系"],
                    "examples": []
                }
            },
            "creativity_tendency": {
                "divergent_vs_convergent": {
                    "score": 0.5,
                    "description": "待观察",
                    "evidence": ["需要更多样本"]
                },
                "cross_domain_thinking": {
                    "frequency": "occasional",
                    "domains": [],
                    "examples": []
                }
            },
            "confidence_score": 0.3,
            "analysis_notes": f"基于有限信息的初始分析: {analysis_text[:200]}..."
        }