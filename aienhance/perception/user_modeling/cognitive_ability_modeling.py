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
            
            # 使用LLM分析用户认知能力特征
            analysis_result = await self.process_with_llm(analysis_prompt, context)
            
            # 解析LLM输出为结构化数据
            cognitive_profile = self._parse_llm_output(analysis_result)
            
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
    
    def _build_analysis_prompt(self, query: str, session_context: Dict[str, Any], user_id: str) -> str:
        """构建认知能力分析提示词"""
        
        # 获取历史对话上下文
        conversation_history = session_context.get("conversation_history", [])
        previous_queries = [item.get("query", "") for item in conversation_history[-5:]]
        
        prompt = f"""
你是一位认知心理学专家，需要分析用户的认知能力特征。

当前用户问题：{query}

历史问题模式：{previous_queries}

请从以下维度分析用户的认知特征，并输出JSON格式结果：

## 分析维度

### 1. 思维模式识别
- 形象思维倾向 vs 逻辑推理倾向
- 问题表述方式分析
- 论证结构偏好
- 概念使用习惯

### 2. 认知复杂度评估
- 多层次概念处理能力
- 抽象关系理解能力
- 认知处理深度

### 3. 创造性思维倾向
- 收敛性解决 vs 发散性探索
- 创新性问题处理方式
- 跨领域联想能力

## 输出格式（JSON）

```json
{{
    "thinking_style": {{
        "abstract_vs_concrete": {{
            "score": 0.0-1.0,
            "description": "抽象思维倾向程度",
            "evidence": ["具体证据"]
        }},
        "deductive_vs_inductive": {{
            "score": 0.0-1.0,
            "description": "演绎vs归纳推理偏好",
            "evidence": ["具体证据"]
        }},
        "analogy_usage": {{
            "frequency": "low|medium|high",
            "quality": "basic|advanced",
            "examples": ["类比使用例子"]
        }}
    }},
    "cognitive_complexity": {{
        "concept_depth": {{
            "level": "basic|intermediate|advanced",
            "evidence": ["层次概念使用证据"]
        }},
        "relation_understanding": {{
            "score": 0.0-1.0,
            "types": ["因果", "条件", "类比等"],
            "examples": ["关系理解例子"]
        }}
    }},
    "creativity_tendency": {{
        "divergent_vs_convergent": {{
            "score": 0.0-1.0,
            "description": "发散vs收敛思维倾向",
            "evidence": ["具体行为证据"]
        }},
        "cross_domain_thinking": {{
            "frequency": "rare|occasional|frequent",
            "domains": ["涉及的领域"],
            "examples": ["跨域思考例子"]
        }}
    }},
    "confidence_score": 0.0-1.0,
    "analysis_notes": "详细的分析说明"
}}
```

请基于提供的信息进行详细分析：
"""
        
        return prompt
    
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