"""
类比推理与跨域激活模块

基于设计文档第5.3节，类比推理是人类认知的核心机制之一，系统通过深度模拟这一机制实现创新性思维支持。
"""

from typing import Dict, Any, List
import logging
from aienhance.core.base_architecture import BaseModule, ProcessingContext, ProcessingResult

logger = logging.getLogger(__name__)


class AnalogyReasoningModule(BaseModule):
    """类比推理与跨域激活模块"""
    
    def __init__(self, llm_adapter=None, config: Dict[str, Any] = None):
        super().__init__("analogy_reasoning", [], config)
        self.llm_adapter = llm_adapter
        
    async def _initialize_impl(self):
        """模块初始化实现"""
        logger.info("Initializing Analogy Reasoning Module")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理类比推理"""
        try:
            # 获取语义增强结果
            semantic_output = context.module_outputs.get("semantic_enhancement_output", {})
            enhanced_content = semantic_output.get("enhanced_content", {})
            
            # 三个子功能
            
            # 1. 类比检索机制
            analogy_sources = await self._retrieve_analogies(context, enhanced_content)
            
            # 2. 思维框架匹配
            thinking_frameworks = await self._match_thinking_frameworks(context)
            
            # 3. 创新联想生成
            creative_associations = await self._generate_creative_associations(context, analogy_sources)
            
            analogy_results = {
                "analogy_sources": analogy_sources,
                "thinking_frameworks": thinking_frameworks,
                "creative_associations": creative_associations,
                "reasoning_synthesis": await self._synthesize_reasoning(analogy_sources, thinking_frameworks, creative_associations, context)
            }
            
            return ProcessingResult(
                success=True,
                data={
                    "analogy_results": analogy_results,
                    "reasoning_confidence": self._calculate_reasoning_confidence(analogy_results)
                },
                metadata={
                    "module": "analogy_reasoning",
                    "analogies_found": len(analogy_sources),
                    "frameworks_matched": len(thinking_frameworks)
                }
            )
            
        except Exception as e:
            logger.error(f"Analogy reasoning failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _retrieve_analogies(self, context: ProcessingContext, enhanced_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """类比检索机制"""
        
        analogies = []
        
        if self.llm_adapter:
            try:
                analogy_prompt = f"""
针对用户问题寻找合适的类比：

问题：{context.query}
增强内容：{enhanced_content.get('integrated_content', {}).get('integrated_narrative', '')[:200]}

请找出3个有助理解的类比，每个类比包括：
1. 类比源（熟悉的领域/概念）
2. 结构相似性
3. 启发价值

要求简洁明确。
"""
                
                response = await self.llm_adapter.generate_response(analogy_prompt, context.session_context)
                
                # 解析响应为结构化数据
                analogies = self._parse_analogy_response(response)
                
            except Exception as e:
                logger.warning(f"Analogy retrieval failed: {e}")
        
        # 如果没有获得类比，提供默认类比
        if not analogies:
            analogies = [{
                "analogy_source": "通用问题解决过程",
                "structural_similarity": "步骤化解决",
                "inspirational_value": 0.6,
                "analogy_content": "就像解决复杂问题需要分步骤一样"
            }]
            
        return analogies
    
    def _parse_analogy_response(self, response: str) -> List[Dict[str, Any]]:
        """解析类比响应"""
        analogies = []
        
        # 简化的解析逻辑
        lines = response.split('\n')
        current_analogy = {}
        
        for line in lines:
            line = line.strip()
            if '类比源' in line or '源：' in line:
                current_analogy['analogy_source'] = line.split('：')[-1] if '：' in line else line
            elif '相似' in line or '结构' in line:
                current_analogy['structural_similarity'] = line.split('：')[-1] if '：' in line else line
            elif current_analogy and len(current_analogy) >= 2:
                current_analogy['inspirational_value'] = 0.7
                current_analogy['analogy_content'] = line
                analogies.append(current_analogy)
                current_analogy = {}
                
        return analogies[:3]  # 最多3个类比
    
    async def _match_thinking_frameworks(self, context: ProcessingContext) -> List[Dict[str, Any]]:
        """思维框架匹配"""
        
        # 基于用户画像和问题类型匹配思维框架
        perception_output = context.layer_outputs.get("perception", {})
        context_analysis = perception_output.get("situation_analysis", {})
        task_type = context_analysis.get("task_analysis", {}).get("primary_task_type", "retrieval")
        
        frameworks_map = {
            "analytical": [
                {"name": "SWOT分析框架", "applicability": 0.8, "description": "优势劣势机会威胁分析"},
                {"name": "因果分析框架", "applicability": 0.7, "description": "原因结果链条分析"}
            ],
            "creative": [
                {"name": "SCAMPER技法", "applicability": 0.9, "description": "替代组合适应修改放大缩小重组逆向"},
                {"name": "发散收敛思维", "applicability": 0.8, "description": "先发散后收敛的创新过程"}
            ],
            "exploratory": [
                {"name": "5W1H分析法", "applicability": 0.8, "description": "谁什么时间地点为什么怎样"},
                {"name": "假设验证框架", "applicability": 0.7, "description": "提出假设并验证"}
            ]
        }
        
        return frameworks_map.get(task_type, frameworks_map["analytical"])
    
    async def _generate_creative_associations(self, context: ProcessingContext, analogies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创新联想生成"""
        
        associations = []
        
        for analogy in analogies:
            association = {
                "association_type": "远距离联想",
                "trigger_concept": analogy.get("analogy_source", ""),
                "novel_connection": f"从 '{analogy.get('analogy_source', '')}' 联想到问题解决的新角度",
                "creativity_score": 0.6,
                "feasibility": 0.7
            }
            associations.append(association)
            
        return associations
    
    async def _synthesize_reasoning(self, analogies: List[Dict[str, Any]], 
                                   frameworks: List[Dict[str, Any]], 
                                   associations: List[Dict[str, Any]], 
                                   context: ProcessingContext) -> Dict[str, Any]:
        """综合推理结果"""
        
        synthesis = {
            "key_analogies": [a.get("analogy_content", "") for a in analogies[:2]],
            "recommended_framework": frameworks[0].get("name", "") if frameworks else "通用分析框架",
            "creative_insights": [a.get("novel_connection", "") for a in associations[:2]],
            "reasoning_summary": f"基于 {len(analogies)} 个类比和 {len(frameworks)} 个思维框架的推理综合"
        }
        
        return synthesis
    
    def _calculate_reasoning_confidence(self, analogy_results: Dict[str, Any]) -> float:
        """计算推理置信度"""
        
        analogies = analogy_results.get("analogy_sources", [])
        frameworks = analogy_results.get("thinking_frameworks", [])
        associations = analogy_results.get("creative_associations", [])
        
        # 基于数量和质量计算
        analogy_factor = min(len(analogies) / 3.0, 1.0)
        framework_factor = min(len(frameworks) / 2.0, 1.0)
        association_factor = min(len(associations) / 3.0, 1.0)
        
        return (analogy_factor * 0.4 + framework_factor * 0.3 + association_factor * 0.3)