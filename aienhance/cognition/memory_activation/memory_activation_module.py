"""
多层次记忆激活模块

基于设计文档第5.1节，系统采用表层-深层-元层三层记忆激活机制，模拟人类记忆的层次性组织和激活过程。
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from aienhance.core.base_architecture import BaseModule, ProcessingContext, ProcessingResult
from aienhance.memory.interfaces import MemoryQuery, UserContext

logger = logging.getLogger(__name__)


@dataclass
class MemoryFragment:
    """记忆片段数据类"""
    content: str
    fragment_id: str
    source: str
    relevance_score: float
    activation_strength: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryActivationModule(BaseModule):
    """多层次记忆激活模块"""
    
    def __init__(self, llm_adapter=None, memory_adapter=None, config: Dict[str, Any] = None):
        super().__init__("memory_activation", [], config)
        self.llm_adapter = llm_adapter
        self.memory_adapter = memory_adapter
        
    async def _initialize_impl(self):
        """模块初始化实现"""
        logger.info("Initializing Memory Activation Module")
        
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理记忆激活"""
        try:
            # 三层记忆激活机制
            
            # 1. 表层激活：显性语义匹配
            surface_memories = await self._surface_activation(context)
            
            # 2. 深层激活：概念网络扩散  
            deep_memories = await self._deep_activation(context, surface_memories)
            
            # 3. 元层激活：认知模式匹配
            meta_memories = await self._meta_activation(context, deep_memories)
            
            # 整合三层激活结果
            integrated_memories = await self._integrate_memory_activation(
                surface_memories, deep_memories, meta_memories, context
            )
            
            return ProcessingResult(
                success=True,
                data={
                    "activated_memories": integrated_memories,
                    "surface_layer": surface_memories,
                    "deep_layer": deep_memories, 
                    "meta_layer": meta_memories,
                    "activation_confidence": self._calculate_activation_confidence(integrated_memories)
                },
                metadata={
                    "module": "memory_activation",
                    "total_memories": len(integrated_memories),
                    "activation_layers": ["surface", "deep", "meta"]
                }
            )
            
        except Exception as e:
            logger.error(f"Memory activation failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata={"error": str(e)},
                error_message=str(e)
            )
    
    async def _surface_activation(self, context: ProcessingContext) -> List[Dict[str, Any]]:
        """表层激活：显性语义匹配"""
        surface_memories = []
        
        if self.memory_adapter:
            try:
                # 创建用户上下文
                user_context = UserContext(user_id=context.user_id)
                
                # 创建记忆查询
                memory_query = MemoryQuery(
                    query=context.query,
                    user_context=user_context,
                    limit=10
                )
                
                # 使用记忆适配器进行语义搜索
                search_result = await self.memory_adapter.search_memories(memory_query)
                
                for memory_entry in search_result.memories:
                    surface_memories.append({
                        "content": memory_entry.content,
                        "relevance_score": memory_entry.confidence,
                        "source": "surface_activation",
                        "memory_type": memory_entry.memory_type.value,
                        "activation_layer": "surface"
                    })
                    
            except Exception as e:
                logger.warning(f"Surface activation with memory adapter failed: {e}")
        
        # 如果没有记忆适配器或搜索失败，返回基础结果
        if not surface_memories:
            surface_memories = [{
                "content": f"基于问题 '{context.query}' 的基础语义匹配",
                "relevance_score": 0.6,
                "source": "surface_activation_default",
                "memory_type": "semantic_match",
                "activation_layer": "surface"
            }]
            
        return surface_memories
    
    async def _deep_activation(self, context: ProcessingContext, surface_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """深层激活：概念网络扩散"""
        deep_memories = []
        
        # 从表层记忆中提取关键概念
        key_concepts = await self._extract_key_concepts(surface_memories, context)
        
        # 基于概念进行扩散激活
        for concept in key_concepts:
            if self.memory_adapter:
                try:
                    # 创建用户上下文
                    user_context = UserContext(user_id=context.user_id)
                    
                    # 创建概念相关的记忆查询
                    concept_query = MemoryQuery(
                        query=concept,
                        user_context=user_context,
                        limit=5
                    )
                    
                    # 概念相关记忆搜索
                    concept_result = await self.memory_adapter.search_memories(concept_query)
                    
                    for memory_entry in concept_result.memories:
                        deep_memories.append({
                            "content": memory_entry.content,
                            "relevance_score": memory_entry.confidence * 0.8,  # 降权
                            "source": "deep_activation",
                            "related_concept": concept,
                            "activation_layer": "deep"
                        })
                        
                except Exception as e:
                    logger.warning(f"Deep activation for concept '{concept}' failed: {e}")
        
        # 如果没有深层记忆，创建概念扩展记忆
        if not deep_memories:
            for concept in key_concepts[:3]:  # 限制前3个概念
                deep_memories.append({
                    "content": f"与概念 '{concept}' 相关的扩展知识和联想",
                    "relevance_score": 0.5,
                    "source": "deep_activation_default", 
                    "related_concept": concept,
                    "activation_layer": "deep"
                })
                
        return deep_memories
    
    async def _meta_activation(self, context: ProcessingContext, deep_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """元层激活：认知模式匹配"""
        meta_memories = []
        
        # 从用户画像中获取认知模式信息
        perception_output = context.layer_outputs.get("perception", {})
        user_profile = perception_output.get("user_cognitive_profile", {})
        
        # 基于用户认知模式激活相关记忆
        cognitive_patterns = self._extract_cognitive_patterns(user_profile)
        
        for pattern in cognitive_patterns:
            meta_memories.append({
                "content": f"基于认知模式 '{pattern}' 的相关知识和经验",
                "relevance_score": 0.6,
                "source": "meta_activation",
                "cognitive_pattern": pattern,
                "activation_layer": "meta"
            })
        
        return meta_memories
    
    async def _extract_key_concepts(self, surface_memories: List[Dict[str, Any]], context: ProcessingContext) -> List[str]:
        """从表层记忆和查询中提取关键概念"""
        concepts = []
        
        # 简单的关键词提取
        query_words = context.query.split()
        concepts.extend([word for word in query_words if len(word) > 3])
        
        # 从记忆内容中提取概念
        for memory in surface_memories:
            content = memory.get("content", "")
            # 简化的概念提取
            memory_words = content.split()
            concepts.extend([word for word in memory_words if len(word) > 4])
        
        # 去重并限制数量
        unique_concepts = list(set(concepts))[:5]
        
        return unique_concepts
    
    def _extract_cognitive_patterns(self, user_profile: Dict[str, Any]) -> List[str]:
        """从用户画像中提取认知模式"""
        patterns = []
        
        # 从认知能力中提取模式
        cognitive_abilities = user_profile.get("cognitive_abilities", {})
        if cognitive_abilities:
            thinking_style = cognitive_abilities.get("thinking_style", {})
            if thinking_style.get("abstract_vs_concrete", {}).get("score", 0.5) > 0.6:
                patterns.append("抽象思维")
            if thinking_style.get("deductive_vs_inductive", {}).get("score", 0.5) > 0.6:
                patterns.append("演绎推理")
            else:
                patterns.append("归纳推理")
        
        # 从交互模式中提取模式
        interaction_patterns = user_profile.get("interaction_patterns", {})
        if interaction_patterns:
            focus_style = interaction_patterns.get("attention_patterns", {}).get("focus_style", {})
            if focus_style.get("type") == "deep_focus":
                patterns.append("深度聚焦")
            elif focus_style.get("type") == "broad_scan":
                patterns.append("广度扫描")
        
        return patterns if patterns else ["通用认知模式"]
    
    async def _integrate_memory_activation(self, surface_memories: List[Dict[str, Any]],
                                          deep_memories: List[Dict[str, Any]],
                                          meta_memories: List[Dict[str, Any]],
                                          context: ProcessingContext) -> List[Dict[str, Any]]:
        """整合三层记忆激活结果"""
        
        all_memories = surface_memories + deep_memories + meta_memories
        
        # 按相关性排序
        all_memories.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # 限制总数量并添加整合信息
        integrated_memories = all_memories[:15]  # 最多15个记忆
        
        for memory in integrated_memories:
            memory["integration_timestamp"] = context.metadata.get("created_at")
            memory["query_context"] = context.query
        
        return integrated_memories
    
    def _calculate_activation_confidence(self, memories: List[Dict[str, Any]]) -> float:
        """计算激活置信度"""
        if not memories:
            return 0.0
        
        scores = [memory.get("relevance_score", 0) for memory in memories]
        avg_score = sum(scores) / len(scores)
        
        # 基于记忆数量和平均得分计算置信度
        quantity_factor = min(len(memories) / 10.0, 1.0)  # 10个记忆为满分
        
        return (avg_score * 0.7 + quantity_factor * 0.3)