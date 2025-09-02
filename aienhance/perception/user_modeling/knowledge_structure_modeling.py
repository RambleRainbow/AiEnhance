"""
知识结构维度建模子模块

基于设计文档第4.1.2节，获取用户的专业背景、身份、能力等信息，分析经验深度、知识框架，构建个性化知识图谱。
"""

from typing import Dict, Any, List
import json
import logging
from aienhance.core.base_architecture import BaseSubModule, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class KnowledgeStructureModelingSubModule(BaseSubModule):
    """知识结构维度建模子模块"""
    
    def __init__(self, llm_adapter=None, config: Dict[str, Any] = None):
        super().__init__("knowledge_structure_modeling", llm_adapter, config)
        
    async def _initialize_impl(self):
        """子模块初始化"""
        logger.info("Initializing Knowledge Structure Modeling SubModule")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理知识结构维度建模"""
        try:
            # 构建知识结构分析提示词
            analysis_prompt = self._build_knowledge_analysis_prompt(
                context.query,
                context.session_context,
                context.user_id
            )
            
            # 使用LLM分析用户知识结构
            analysis_result = await self.process_with_llm(analysis_prompt, context)
            
            # 解析LLM输出为结构化数据
            knowledge_profile = self._parse_llm_output(analysis_result)
            
            return ProcessingResult(
                success=True,
                data={
                    "knowledge_profile": knowledge_profile,
                    "analysis_timestamp": context.metadata.get("created_at"),
                    "domains_identified": len(knowledge_profile.get("domain_expertise", {})),
                    "knowledge_graph": knowledge_profile.get("personal_knowledge_graph", {})
                },
                metadata={
                    "submodule": "knowledge_structure_modeling",
                    "expertise_domains": list(knowledge_profile.get("domain_expertise", {}).keys()),
                    "knowledge_depth_score": knowledge_profile.get("overall_knowledge_depth", 0.5)
                }
            )
            
        except Exception as e:
            logger.error(f"Knowledge structure modeling failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    def _build_knowledge_analysis_prompt(self, query: str, session_context: Dict[str, Any], user_id: str) -> str:
        """构建知识结构分析提示词"""
        
        # 获取历史对话上下文
        conversation_history = session_context.get("conversation_history", [])
        user_profile = session_context.get("user_profile", {})
        mentioned_domains = session_context.get("mentioned_domains", [])
        
        prompt = f"""
你是一位知识结构分析专家，需要分析用户的知识背景和专业能力。

当前用户问题：{query}

用户历史信息：{user_profile}

提及的专业领域：{mentioned_domains}

历史对话样本：{conversation_history[-3:] if conversation_history else []}

请从以下维度分析用户的知识结构，并输出JSON格式结果：

## 分析维度

### 1. 领域知识映射
- 专业领域识别
- 各领域的专业程度评估
- 知识深度与广度分析

### 2. 知识边界识别
- 用户熟悉的知识区域
- 知识边界和盲点
- 学习需求识别

### 3. 跨域知识连接
- 不同领域间的知识整合能力
- 跨学科思维表现
- 知识迁移能力

### 4. 个性化知识图谱构建
- 核心概念节点
- 边缘概念节点
- 潜在扩展区域

## 输出格式（JSON）

```json
{{
    "domain_expertise": {{
        "技术领域": {{
            "expertise_level": "beginner|intermediate|advanced|expert",
            "confidence": 0.0-1.0,
            "key_concepts": ["核心概念1", "核心概念2"],
            "evidence": ["从对话中提取的证据"],
            "knowledge_gaps": ["识别的知识缺口"]
        }},
        "其他领域": {{
            "expertise_level": "beginner|intermediate|advanced|expert",
            "confidence": 0.0-1.0,
            "key_concepts": ["核心概念"],
            "evidence": ["证据"],
            "knowledge_gaps": ["缺口"]
        }}
    }},
    "knowledge_boundaries": {{
        "strong_areas": ["用户擅长的知识领域"],
        "weak_areas": ["知识薄弱的领域"],
        "learning_interests": ["显示出学习兴趣的领域"],
        "boundary_concepts": ["边界概念，用户部分了解但不深入"]
    }},
    "cross_domain_ability": {{
        "integration_skill": {{
            "score": 0.0-1.0,
            "description": "跨域知识整合能力",
            "examples": ["具体例子"]
        }},
        "transfer_capability": {{
            "score": 0.0-1.0,
            "successful_transfers": ["成功的知识迁移例子"],
            "transfer_patterns": ["迁移模式"]
        }}
    }},
    "personal_knowledge_graph": {{
        "core_concepts": [
            {{
                "concept": "概念名称",
                "domain": "所属领域",
                "importance": 0.0-1.0,
                "connections": ["相关概念"]
            }}
        ],
        "edge_concepts": [
            {{
                "concept": "边缘概念",
                "domain": "所属领域",
                "understanding_level": "basic|partial|unclear",
                "potential": 0.0-1.0
            }}
        ],
        "expansion_areas": [
            {{
                "area": "潜在扩展领域",
                "readiness": 0.0-1.0,
                "prerequisites": ["前置知识"],
                "learning_path": ["建议的学习路径"]
            }}
        ]
    }},
    "overall_knowledge_depth": 0.0-1.0,
    "knowledge_breadth": 0.0-1.0,
    "learning_style_indicators": ["指标1", "指标2"],
    "confidence_score": 0.0-1.0,
    "analysis_notes": "详细的知识结构分析说明"
}}
```

请基于提供的信息进行深入的知识结构分析：
"""
        
        return prompt
    
    def _parse_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """解析LLM输出为结构化知识画像数据"""
        try:
            # 尝试从输出中提取JSON
            json_start = llm_output.find('{')
            json_end = llm_output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_output[json_start:json_end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                return self._create_default_knowledge_profile(llm_output)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse knowledge structure JSON: {e}")
            return self._create_default_knowledge_profile(llm_output)
    
    def _create_default_knowledge_profile(self, analysis_text: str) -> Dict[str, Any]:
        """创建默认知识结构画像"""
        return {
            "domain_expertise": {
                "general": {
                    "expertise_level": "intermediate",
                    "confidence": 0.5,
                    "key_concepts": [],
                    "evidence": ["初始交互"],
                    "knowledge_gaps": ["待识别"]
                }
            },
            "knowledge_boundaries": {
                "strong_areas": [],
                "weak_areas": [],
                "learning_interests": [],
                "boundary_concepts": []
            },
            "cross_domain_ability": {
                "integration_skill": {
                    "score": 0.5,
                    "description": "需要更多观察",
                    "examples": []
                },
                "transfer_capability": {
                    "score": 0.5,
                    "successful_transfers": [],
                    "transfer_patterns": []
                }
            },
            "personal_knowledge_graph": {
                "core_concepts": [],
                "edge_concepts": [],
                "expansion_areas": []
            },
            "overall_knowledge_depth": 0.5,
            "knowledge_breadth": 0.5,
            "learning_style_indicators": ["待观察"],
            "confidence_score": 0.3,
            "analysis_notes": f"基于初始信息的知识结构分析: {analysis_text[:200]}..."
        }