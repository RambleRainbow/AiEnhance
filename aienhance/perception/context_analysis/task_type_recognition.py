"""
任务类型识别子模块

基于设计文档第4.2.1节，识别用户任务的认知类型，为系统匹配合适的支持策略与资源提供任务导向基础。
"""

from typing import Dict, Any
import json
import logging
from aienhance.core.base_architecture import BaseSubModule, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class TaskTypeRecognitionSubModule(BaseSubModule):
    """任务类型识别子模块"""
    
    def __init__(self, llm_adapter=None, config: Dict[str, Any] = None):
        super().__init__("task_type_recognition", llm_adapter, config)
        
    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Task Type Recognition SubModule")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理任务类型识别"""
        try:
            # 构建任务类型识别提示词
            analysis_prompt = self._build_task_analysis_prompt(
                context.query,
                context.session_context
            )
            
            # 使用LLM识别任务类型
            analysis_result = await self.process_with_llm(analysis_prompt, context)
            
            # 解析LLM输出为结构化数据
            task_analysis = self._parse_llm_output(analysis_result)
            
            return ProcessingResult(
                success=True,
                data={
                    "task_analysis": task_analysis,
                    "primary_task_type": task_analysis.get("primary_task_type"),
                    "task_complexity": task_analysis.get("complexity_assessment", {}),
                    "recommended_strategies": task_analysis.get("support_strategies", [])
                },
                metadata={
                    "submodule": "task_type_recognition",
                    "confidence": task_analysis.get("confidence_score", 0.7),
                    "secondary_types": task_analysis.get("secondary_task_types", [])
                }
            )
            
        except Exception as e:
            logger.error(f"Task type recognition failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    def _build_task_analysis_prompt(self, query: str, session_context: Dict[str, Any]) -> str:
        """构建任务类型分析提示词"""
        
        conversation_context = session_context.get("conversation_history", [])
        user_context = session_context.get("user_context", {})
        
        prompt = f"""
你是任务类型识别专家，需要分析用户问题的认知任务类型。

用户问题：{query}

对话上下文：{conversation_context[-2:] if conversation_context else "无"}

用户背景：{user_context}

请根据以下任务类型特征进行分析：

## 任务类型定义

### 1. 探索型任务 (Exploratory)
特征：
- 开放性问题表述（"如何看待...""可能有哪些..."）
- 缺乏明确目标或评价标准
- 需要创造性思维和多角度分析
- 侧重探索过程而非最终结论

### 2. 分析型任务 (Analytical)
特征：
- 结构化问题表述（"分析...的原因""比较A与B"）
- 有明确的逻辑框架需求
- 需要系统性思维和严谨推理
- 强调结构合理和结论严密

### 3. 创新型任务 (Creative)
特征：
- 跨领域问题表述
- 寻求突破性解决方案
- 需要类比思维和概念重组
- 关注对"已知"的超越

### 4. 检索型任务 (Retrieval)
特征：
- 获得公共信息或知识
- 问题相对直接明确
- 主要需要信息查找和整理
- 可向其他任务类型迁移

## 输出格式（JSON）

```json
{{
    "primary_task_type": "exploratory|analytical|creative|retrieval",
    "secondary_task_types": ["可能的次要类型"],
    "task_characteristics": {{
        "openness": 0.0-1.0,
        "structure_requirement": 0.0-1.0,
        "creativity_need": 0.0-1.0,
        "knowledge_intensity": 0.0-1.0
    }},
    "complexity_assessment": {{
        "cognitive_complexity": "low|medium|high",
        "domain_complexity": "single|multi",
        "temporal_complexity": "immediate|extended",
        "social_complexity": "individual|collaborative"
    }},
    "question_patterns": {{
        "question_words": ["提取的疑问词"],
        "modal_verbs": ["情态动词"],
        "scope_indicators": ["范围指示词"],
        "certainty_markers": ["确定性标记"]
    }},
    "cognitive_demands": {{
        "required_thinking_modes": ["演绎", "归纳", "类比", "直觉"],
        "knowledge_synthesis_need": 0.0-1.0,
        "perspective_diversity_need": 0.0-1.0,
        "critical_thinking_need": 0.0-1.0
    }},
    "support_strategies": [
        "针对此任务类型的推荐支持策略"
    ],
    "interaction_recommendations": {{
        "optimal_response_style": "detailed|structured|creative|direct",
        "information_organization": "linear|hierarchical|network",
        "engagement_approach": "guided|collaborative|facilitative"
    }},
    "confidence_score": 0.0-1.0,
    "analysis_reasoning": "详细的任务类型识别推理过程"
}}
```

请基于问题内容进行深入的任务类型分析：
"""
        
        return prompt
    
    def _parse_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """解析LLM输出为结构化任务分析数据"""
        try:
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_output[json_start:json_end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                return self._create_default_task_analysis(llm_output)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse task analysis JSON: {e}")
            return self._create_default_task_analysis(llm_output)
    
    def _create_default_task_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """创建默认任务分析结果"""
        # 简单的规则基础判断
        query_lower = analysis_text.lower()
        
        # 基础任务类型判断
        primary_type = "retrieval"  # 默认
        if any(word in query_lower for word in ["如何看待", "分析", "评价", "比较"]):
            primary_type = "analytical"
        elif any(word in query_lower for word in ["创新", "设计", "想法", "可能性"]):
            primary_type = "creative"
        elif any(word in query_lower for word in ["探索", "了解", "研究", "发现"]):
            primary_type = "exploratory"
        
        return {
            "primary_task_type": primary_type,
            "secondary_task_types": [],
            "task_characteristics": {
                "openness": 0.5,
                "structure_requirement": 0.5,
                "creativity_need": 0.3 if primary_type == "creative" else 0.2,
                "knowledge_intensity": 0.6
            },
            "complexity_assessment": {
                "cognitive_complexity": "medium",
                "domain_complexity": "single",
                "temporal_complexity": "immediate",
                "social_complexity": "individual"
            },
            "question_patterns": {
                "question_words": [],
                "modal_verbs": [],
                "scope_indicators": [],
                "certainty_markers": []
            },
            "cognitive_demands": {
                "required_thinking_modes": ["归纳", "演绎"],
                "knowledge_synthesis_need": 0.5,
                "perspective_diversity_need": 0.4,
                "critical_thinking_need": 0.5
            },
            "support_strategies": [
                f"为{primary_type}任务提供相应支持"
            ],
            "interaction_recommendations": {
                "optimal_response_style": "structured",
                "information_organization": "hierarchical",
                "engagement_approach": "guided"
            },
            "confidence_score": 0.4,
            "analysis_reasoning": f"基于关键词的基础任务类型判断: {analysis_text[:100]}..."
        }