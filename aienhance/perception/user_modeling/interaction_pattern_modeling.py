"""
交互模式维度建模子模块

基于设计文档第4.1.3节，了解用户的思维节奏、信息接受偏好、认知负荷阈值。
"""

from typing import Dict, Any
import json
import logging
from datetime import datetime, timedelta
from aienhance.core.base_architecture import BaseSubModule, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class InteractionPatternModelingSubModule(BaseSubModule):
    """交互模式维度建模子模块"""
    
    def __init__(self, llm_adapter=None, config: Dict[str, Any] = None):
        super().__init__("interaction_pattern_modeling", llm_adapter, config)
        
    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Interaction Pattern Modeling SubModule")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理交互模式维度建模"""
        try:
            # 构建交互模式分析提示词
            analysis_prompt = self._build_interaction_analysis_prompt(
                context.query,
                context.session_context,
                context.user_id
            )
            
            # 使用LLM流式分析用户交互模式
            logger.info("开始流式分析用户交互模式...")
            analysis_result = ""
            chunk_count = 0
            async for chunk in self.process_with_llm_stream(analysis_prompt, context):
                analysis_result += chunk
                chunk_count += 1
                if chunk_count % 10 == 0:  # 每10个chunk记录一次进度
                    logger.debug(f"已接收 {chunk_count} 个响应片段，当前长度: {len(analysis_result)}")
            logger.info(f"流式分析完成，总共接收 {chunk_count} 个片段，总长度: {len(analysis_result)}")
            
            # 解析LLM输出为结构化数据
            interaction_profile = self._parse_llm_output(analysis_result)
            
            # 添加实时交互数据
            interaction_profile = self._enhance_with_realtime_data(
                interaction_profile,
                context.session_context
            )
            
            return ProcessingResult(
                success=True,
                data={
                    "interaction_profile": interaction_profile,
                    "analysis_timestamp": context.metadata.get("created_at"),
                    "interaction_preferences": interaction_profile.get("preferences_summary", {}),
                    "cognitive_load_profile": interaction_profile.get("cognitive_load", {})
                },
                metadata={
                    "submodule": "interaction_pattern_modeling",
                    "response_pattern": interaction_profile.get("response_timing", {}),
                    "preferred_complexity": interaction_profile.get("information_processing", {}).get("complexity_preference")
                }
            )
            
        except Exception as e:
            logger.error(f"Interaction pattern modeling failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    def _build_interaction_analysis_prompt(self, query: str, session_context: Dict[str, Any], user_id: str) -> str:
        """构建交互模式分析提示词"""
        
        conversation_history = session_context.get("conversation_history", [])
        response_times = session_context.get("response_times", [])
        user_feedback = session_context.get("user_feedback", [])
        
        # 计算交互统计信息
        interaction_stats = self._calculate_interaction_stats(conversation_history, response_times)
        
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

## 输出格式（JSON）

```json
{{
    "information_processing": {{
        "speed_preference": {{
            "type": "fast_response|deep_thinking|balanced",
            "score": 0.0-1.0,
            "evidence": ["具体行为证据"],
            "patterns": ["观察到的模式"]
        }},
        "complexity_preference": {{
            "level": "simple|moderate|complex",
            "tolerance": 0.0-1.0,
            "examples": ["复杂度处理例子"],
            "breakdown_needs": true|false
        }},
        "information_density": {{
            "preferred_density": "low|medium|high",
            "adaptation_ability": 0.0-1.0,
            "overload_indicators": ["过载信号"]
        }}
    }},
    "attention_patterns": {{
        "focus_style": {{
            "type": "deep_focus|broad_scan|mixed",
            "sustainability": 0.0-1.0,
            "context_switching": "frequent|moderate|rare",
            "evidence": ["注意力模式证据"]
        }},
        "engagement_rhythm": {{
            "session_length": "short|medium|long",
            "intensity_pattern": "consistent|variable|peaks",
            "break_needs": 0.0-1.0,
            "optimal_timing": ["最佳交互时间模式"]
        }}
    }},
    "cognitive_load": {{
        "multitasking_ability": {{
            "score": 0.0-1.0,
            "concurrent_concepts": 1-10,
            "performance_degradation": 0.0-1.0,
            "examples": ["多任务处理例子"]
        }},
        "threshold_management": {{
            "overload_threshold": "low|medium|high",
            "recovery_speed": 0.0-1.0,
            "warning_signs": ["负荷过载的早期信号"],
            "mitigation_strategies": ["用户的应对策略"]
        }}
    }},
    "interaction_preferences": {{
        "communication_style": {{
            "formality": "formal|semi_formal|casual",
            "detail_level": "brief|moderate|detailed",
            "structure_preference": "linear|hierarchical|network",
            "examples": ["交流风格例子"]
        }},
        "feedback_needs": {{
            "frequency": "high|medium|low",
            "type": ["confirmation", "progress", "clarification"],
            "timing": "immediate|delayed|batch",
            "evidence": ["反馈需求证据"]
        }},
        "personalization_level": {{
            "desired_level": "minimal|moderate|high",
            "adaptation_areas": ["个性化需求领域"],
            "flexibility": 0.0-1.0
        }}
    }},
    "response_timing": {{
        "average_response_time": "快速|正常|慢速",
        "variability": "consistent|variable",
        "context_dependency": ["影响响应时间的因素"],
        "patterns": ["时间模式分析"]
    }},
    "preferences_summary": {{
        "optimal_interaction_mode": "简洁描述最佳交互方式",
        "key_adaptations": ["主要适应性调整建议"],
        "avoid_patterns": ["应该避免的交互模式"]
    }},
    "confidence_score": 0.0-1.0,
    "analysis_notes": "详细的交互模式分析说明"
}}
```

请基于提供的交互数据进行深入分析：
"""
        
        return prompt
    
    def _calculate_interaction_stats(self, conversation_history: list, response_times: list) -> Dict[str, Any]:
        """计算交互统计信息"""
        if not conversation_history:
            return {"message": "无足够历史数据"}
        
        stats = {
            "total_interactions": len(conversation_history),
            "average_query_length": sum(len(item.get("query", "")) for item in conversation_history) / len(conversation_history),
            "session_duration": "未知",
            "interaction_frequency": "未知"
        }
        
        if response_times:
            stats["average_response_time"] = sum(response_times) / len(response_times)
            stats["response_time_variance"] = "计算方差" if len(response_times) > 1 else "单次响应"
        
        # 分析对话复杂度
        complex_queries = sum(1 for item in conversation_history 
                             if len(item.get("query", "")) > 100 or "?" in item.get("query", ""))
        stats["complex_query_ratio"] = complex_queries / len(conversation_history) if conversation_history else 0
        
        return stats
    
    def _enhance_with_realtime_data(self, profile: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """用实时交互数据增强画像"""
        current_session = session_context.get("current_session", {})
        
        # 添加当前会话的实时指标
        if "session_start_time" in current_session:
            session_duration = datetime.now() - current_session["session_start_time"]
            profile["current_session"] = {
                "duration_minutes": session_duration.total_seconds() / 60,
                "interaction_count": current_session.get("interaction_count", 0),
                "complexity_trend": current_session.get("complexity_trend", "stable")
            }
        
        return profile
    
    def _parse_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """解析LLM输出为结构化交互模式数据"""
        try:
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_output[json_start:json_end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                return self._create_default_interaction_profile(llm_output)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse interaction pattern JSON: {e}")
            return self._create_default_interaction_profile(llm_output)
    
    def _create_default_interaction_profile(self, analysis_text: str) -> Dict[str, Any]:
        """创建默认交互模式画像"""
        return {
            "information_processing": {
                "speed_preference": {
                    "type": "balanced",
                    "score": 0.5,
                    "evidence": ["初始观察"],
                    "patterns": ["待观察"]
                },
                "complexity_preference": {
                    "level": "moderate",
                    "tolerance": 0.5,
                    "examples": [],
                    "breakdown_needs": True
                },
                "information_density": {
                    "preferred_density": "medium",
                    "adaptation_ability": 0.5,
                    "overload_indicators": []
                }
            },
            "attention_patterns": {
                "focus_style": {
                    "type": "mixed",
                    "sustainability": 0.5,
                    "context_switching": "moderate",
                    "evidence": ["需要更多观察"]
                },
                "engagement_rhythm": {
                    "session_length": "medium",
                    "intensity_pattern": "consistent",
                    "break_needs": 0.3,
                    "optimal_timing": []
                }
            },
            "cognitive_load": {
                "multitasking_ability": {
                    "score": 0.5,
                    "concurrent_concepts": 3,
                    "performance_degradation": 0.3,
                    "examples": []
                },
                "threshold_management": {
                    "overload_threshold": "medium",
                    "recovery_speed": 0.5,
                    "warning_signs": [],
                    "mitigation_strategies": []
                }
            },
            "interaction_preferences": {
                "communication_style": {
                    "formality": "semi_formal",
                    "detail_level": "moderate",
                    "structure_preference": "hierarchical",
                    "examples": []
                },
                "feedback_needs": {
                    "frequency": "medium",
                    "type": ["confirmation", "progress"],
                    "timing": "immediate",
                    "evidence": []
                },
                "personalization_level": {
                    "desired_level": "moderate",
                    "adaptation_areas": [],
                    "flexibility": 0.7
                }
            },
            "response_timing": {
                "average_response_time": "正常",
                "variability": "consistent",
                "context_dependency": [],
                "patterns": []
            },
            "preferences_summary": {
                "optimal_interaction_mode": "平衡的交互方式，中等复杂度",
                "key_adaptations": ["观察用户反馈", "逐步调整复杂度"],
                "avoid_patterns": ["信息过载", "过于简化"]
            },
            "confidence_score": 0.3,
            "analysis_notes": f"基于初始交互的交互模式分析: {analysis_text[:200]}..."
        }