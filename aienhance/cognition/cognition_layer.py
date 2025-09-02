"""
认知层主类

基于设计文档第五章，认知层是整个系统的核心，负责依据感知层提供的用户模型和情境信息，
从记忆库中动态激活相关记忆并对其进行语义层面的加工补充。
这一层的设计突破了传统RAG系统的局限，实现了从"信息匹配"到"认知协同"的飞跃。
"""

from typing import Dict, Any
import logging
from aienhance.core.base_architecture import BaseLayer, ProcessingContext, ProcessingResult
from .memory_activation.memory_activation_module import MemoryActivationModule
from .semantic_enhancement.semantic_enhancement_module import SemanticEnhancementModule
from .analogy_reasoning.analogy_reasoning_module import AnalogyReasoningModule
from .knowledge_graph.adaptive_knowledge_graph_platform import AdaptiveKnowledgeGraphPlatform

logger = logging.getLogger(__name__)


class CognitionLayer(BaseLayer):
    """认知层"""
    
    def __init__(self, llm_adapter=None, memory_adapter=None, config: Dict[str, Any] = None):
        # 创建四个核心模块
        modules = [
            MemoryActivationModule(llm_adapter, memory_adapter, config),
            SemanticEnhancementModule(llm_adapter, config),
            AnalogyReasoningModule(llm_adapter, config),
            AdaptiveKnowledgeGraphPlatform(llm_adapter, memory_adapter, config)
        ]
        
        super().__init__("cognition", modules, config)
        self.llm_adapter = llm_adapter
        self.memory_adapter = memory_adapter
        
    async def _initialize_impl(self):
        """层初始化实现"""
        logger.info("Initializing Cognition Layer")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理认知层逻辑"""
        try:
            # 从感知层获取用户画像和情境分析
            perception_output = context.layer_outputs.get("perception", {})
            user_profile = perception_output.get("user_cognitive_profile", {})
            situation_analysis = perception_output.get("situation_analysis", {})
            
            # 串行处理模块，每个模块的输出作为下个模块的输入
            
            # 1. 记忆激活模块
            memory_activation_result = await self._process_memory_activation(context, user_profile)
            
            # 2. 语义补充模块
            semantic_enhancement_result = await self._process_semantic_enhancement(
                context, memory_activation_result
            )
            
            # 3. 类比推理模块
            analogy_reasoning_result = await self._process_analogy_reasoning(
                context, semantic_enhancement_result
            )
            
            # 4. 知识图谱平台（用于优化和学习）
            knowledge_graph_result = await self._process_knowledge_graph_update(
                context, analogy_reasoning_result
            )
            
            # 整合认知层输出
            integrated_cognition = {
                "activated_memories": memory_activation_result.get("activated_memories", []),
                "enhanced_semantics": semantic_enhancement_result.get("enhanced_content", {}),
                "analogy_insights": analogy_reasoning_result.get("analogy_results", []),
                "knowledge_connections": knowledge_graph_result.get("updated_connections", []),
                "cognitive_synthesis": await self._synthesize_cognitive_output(
                    memory_activation_result, semantic_enhancement_result, 
                    analogy_reasoning_result, context
                )
            }
            
            return ProcessingResult(
                success=True,
                data={
                    "cognition_output": integrated_cognition,
                    "cognitive_insights": integrated_cognition["cognitive_synthesis"],
                    "memory_context": integrated_cognition["activated_memories"],
                    "reasoning_paths": integrated_cognition["analogy_insights"]
                },
                metadata={
                    "layer": "cognition",
                    "processing_modules": ["memory_activation", "semantic_enhancement", "analogy_reasoning", "knowledge_graph"],
                    "synthesis_confidence": integrated_cognition["cognitive_synthesis"].get("confidence", 0.7)
                }
            )
            
        except Exception as e:
            logger.error(f"Cognition layer processing failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _process_memory_activation(self, context: ProcessingContext, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """处理记忆激活模块"""
        memory_activation_module = self.get_module("memory_activation")
        if memory_activation_module and memory_activation_module.is_enabled():
            result = await memory_activation_module.process(context)
            if result.success:
                return result.data
        
        return {"activated_memories": [], "activation_confidence": 0.5}
    
    async def _process_semantic_enhancement(self, context: ProcessingContext, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理语义补充模块"""
        # 将记忆激活结果加入上下文
        context.module_outputs["memory_activation_output"] = memory_data
        
        semantic_enhancement_module = self.get_module("semantic_enhancement")
        if semantic_enhancement_module and semantic_enhancement_module.is_enabled():
            result = await semantic_enhancement_module.process(context)
            if result.success:
                return result.data
                
        return {"enhanced_content": {}, "enhancement_confidence": 0.5}
    
    async def _process_analogy_reasoning(self, context: ProcessingContext, semantic_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理类比推理模块"""
        # 将语义补充结果加入上下文
        context.module_outputs["semantic_enhancement_output"] = semantic_data
        
        analogy_reasoning_module = self.get_module("analogy_reasoning")
        if analogy_reasoning_module and analogy_reasoning_module.is_enabled():
            result = await analogy_reasoning_module.process(context)
            if result.success:
                return result.data
                
        return {"analogy_results": [], "reasoning_confidence": 0.5}
    
    async def _process_knowledge_graph_update(self, context: ProcessingContext, analogy_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理知识图谱平台更新"""
        context.module_outputs["analogy_reasoning_output"] = analogy_data
        
        knowledge_graph_platform = self.get_module("adaptive_knowledge_graph_platform")
        if knowledge_graph_platform and knowledge_graph_platform.is_enabled():
            result = await knowledge_graph_platform.process(context)
            if result.success:
                return result.data
                
        return {"updated_connections": [], "graph_confidence": 0.5}
    
    async def _synthesize_cognitive_output(self, memory_result: Dict[str, Any], 
                                          semantic_result: Dict[str, Any],
                                          analogy_result: Dict[str, Any],
                                          context: ProcessingContext) -> Dict[str, Any]:
        """综合认知层各模块输出"""
        
        synthesis = {
            "integrated_knowledge": {},
            "cognitive_insights": [],
            "reasoning_chains": [],
            "confidence": 0.7,
            "synthesis_notes": "认知层各模块协同处理结果"
        }
        
        # 整合激活的记忆
        activated_memories = memory_result.get("activated_memories", [])
        if activated_memories:
            synthesis["integrated_knowledge"]["memory_base"] = activated_memories
            synthesis["cognitive_insights"].append("成功激活相关记忆内容")
        
        # 整合语义增强结果
        enhanced_content = semantic_result.get("enhanced_content", {})
        if enhanced_content:
            synthesis["integrated_knowledge"]["enhanced_semantics"] = enhanced_content
            synthesis["cognitive_insights"].append("完成语义层面的补充和加工")
        
        # 整合类比推理结果
        analogy_results = analogy_result.get("analogy_results", [])
        if analogy_results:
            synthesis["reasoning_chains"] = analogy_results
            synthesis["cognitive_insights"].append("生成类比推理和跨域联想")
        
        # 如果有LLM适配器，生成更详细的综合分析
        if self.llm_adapter:
            try:
                synthesis_prompt = f"""
基于以下认知处理结果，生成简洁的认知综合分析：

记忆激活结果：{memory_result}
语义增强结果：{semantic_result}  
类比推理结果：{analogy_result}

用户问题：{context.query}

请生成认知综合分析，包括：
1. 主要认知发现
2. 知识整合要点
3. 推理路径总结
4. 对后续处理的建议

要求简洁明确，不超过200字。
"""
                
                synthesis_response = await self.llm_adapter.generate_response(
                    prompt=synthesis_prompt,
                    context=context.session_context
                )
                
                synthesis["synthesis_notes"] = synthesis_response
                
            except Exception as e:
                logger.warning(f"Cognitive synthesis generation failed: {e}")
        
        return synthesis