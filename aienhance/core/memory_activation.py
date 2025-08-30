"""
记忆激活模块 - 基于LLM的重构版本
使用大模型进行智能记忆激活和语义增强
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .llm_module_base import LLMModuleConfig, LLMModuleManager, LLMModuleProvider

logger = logging.getLogger(__name__)


class ActivationLevel(Enum):
    """激活层次"""
    
    SURFACE = "surface"  # 表层激活
    DEEP = "deep"        # 深层激活
    META = "meta"        # 元层激活


class RelationType(Enum):
    """关联类型"""
    
    SEMANTIC = "semantic"         # 语义关联
    FUNCTIONAL = "functional"     # 功能关联
    TEMPORAL = "temporal"         # 时空关联
    EXPERIENTIAL = "experiential" # 经验关联


@dataclass
class MemoryFragment:
    """记忆片段"""
    
    content: str
    fragment_id: str
    source: str
    relevance_score: float
    activation_strength: float
    metadata: Dict[str, Any]


@dataclass
class ActivationResult:
    """激活结果"""
    
    fragments: List[MemoryFragment]
    activation_level: ActivationLevel
    total_score: float
    activation_path: List[str]  # 激活路径
    semantic_clusters: List[Dict[str, Any]]  # 语义聚类
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SemanticEnhancementResult:
    """语义增强结果"""
    
    enhanced_content: str
    enhancement_type: str  # "conceptual", "contextual", "associative"
    relevance_score: float
    semantic_links: List[Dict[str, Any]]  # 语义链接
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MemoryActivationConfig(LLMModuleConfig):
    """记忆激活配置"""
    
    activation_type: str = "memory_activation"  # "memory_activation" 或 "semantic_enhancement"
    max_fragments: int = 10  # 最大记忆片段数
    min_relevance: float = 0.3  # 最小相关性阈值
    
    def __post_init__(self):
        if not self.prompt_template_name:
            if self.activation_type == "semantic_enhancement":
                self.prompt_template_name = "semantic_enhancement"
            else:
                self.prompt_template_name = "memory_activation"
        if self.temperature is None:
            self.temperature = 0.4  # 中等温度，平衡创造性和准确性
        if self.max_tokens is None:
            self.max_tokens = 600


class LLMMemoryActivationProvider(
    LLMModuleProvider[ActivationResult, MemoryActivationConfig]
):
    """基于大模型的记忆激活提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for memory activation")
                return False

            self.is_initialized = True
            logger.info("LLM memory activation provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize memory activation provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> ActivationResult:
        """处理记忆激活业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Memory activation provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Memory activation failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备记忆激活提示词变量"""
        user_query = input_data
        available_memory = ""
        context_info = ""
        
        if context:
            available_memory = context.get("available_memory", "")
            context_info = context.get("context_info", "")
            
            # 处理记忆片段列表
            memory_fragments = context.get("memory_fragments", [])
            if memory_fragments:
                memory_strs = []
                for fragment in memory_fragments[:self.config.max_fragments]:
                    if isinstance(fragment, dict):
                        content = fragment.get("content", "")
                        source = fragment.get("source", "unknown")
                        memory_strs.append(f"[{source}] {content}")
                    else:
                        memory_strs.append(str(fragment))
                available_memory = "\\n".join(memory_strs)
            
        return {
            "query": user_query,
            "available_memory": available_memory or "当前无可用记忆内容",
            "context_info": context_info or "标准记忆激活情境",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> ActivationResult:
        """解析记忆激活LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析激活层次
            activation_level_str = parsed.get("activation_level", "surface").lower()
            activation_level = ActivationLevel.SURFACE
            for level_enum in ActivationLevel:
                if level_enum.value in activation_level_str:
                    activation_level = level_enum
                    break

            # 解析记忆片段
            fragments = []
            fragments_data = parsed.get("activated_fragments", [])
            if isinstance(fragments_data, list):
                for i, frag_data in enumerate(fragments_data):
                    if isinstance(frag_data, dict):
                        fragment = MemoryFragment(
                            content=frag_data.get("content", ""),
                            fragment_id=frag_data.get("id", f"frag_{i}"),
                            source=frag_data.get("source", "llm_generated"),
                            relevance_score=min(1.0, max(0.0, frag_data.get("relevance", 0.5))),
                            activation_strength=min(1.0, max(0.0, frag_data.get("strength", 0.5))),
                            metadata=frag_data.get("metadata", {})
                        )
                        fragments.append(fragment)

            # 解析激活路径
            activation_path = parsed.get("activation_path", [])
            if not isinstance(activation_path, list):
                activation_path = []

            # 解析语义聚类
            semantic_clusters = parsed.get("semantic_clusters", [])
            if not isinstance(semantic_clusters, list):
                semantic_clusters = []

            return ActivationResult(
                fragments=fragments,
                activation_level=activation_level,
                total_score=min(1.0, max(0.0, parsed.get("total_score", 0.5))),
                activation_path=activation_path,
                semantic_clusters=semantic_clusters,
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_input,
                    "fragment_count": len(fragments),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse memory activation response: {e}")
            return ActivationResult(
                fragments=[],
                activation_level=ActivationLevel.SURFACE,
                total_score=0.0,
                activation_path=[],
                semantic_clusters=[],
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_query": original_input,
                    "error": str(e),
                },
            )


class LLMSemanticEnhancementProvider(
    LLMModuleProvider[SemanticEnhancementResult, MemoryActivationConfig]
):
    """基于大模型的语义增强提供商"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured for semantic enhancement")
                return False

            self.is_initialized = True
            logger.info("LLM semantic enhancement provider initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize semantic enhancement provider: {e}")
            return False

    async def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> SemanticEnhancementResult:
        """处理语义增强业务逻辑"""
        if not self.is_initialized:
            raise RuntimeError("Semantic enhancement provider not initialized")

        try:
            variables = self._prepare_prompt_variables(input_data, context)
            response = await self._call_llm_with_prompt(
                self.config.prompt_template_name, variables
            )
            return self._parse_llm_response(response, input_data)

        except Exception as e:
            logger.error(f"Semantic enhancement failed: {e}")
            raise

    def _prepare_prompt_variables(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """准备语义增强提示词变量"""
        original_content = input_data
        memory_context = ""
        domain_knowledge = ""
        
        if context:
            memory_context = context.get("memory_context", "")
            domain_knowledge = context.get("domain_knowledge", "")
            
        return {
            "original_content": original_content,
            "memory_context": memory_context or "无相关记忆上下文",
            "domain_knowledge": domain_knowledge or "通用知识领域",
        }

    def _parse_llm_response(
        self, response: str, original_input: str
    ) -> SemanticEnhancementResult:
        """解析语义增强LLM响应"""
        try:
            parsed = self._extract_json_from_response(response)

            # 解析语义链接
            semantic_links = parsed.get("semantic_links", [])
            if not isinstance(semantic_links, list):
                semantic_links = []

            return SemanticEnhancementResult(
                enhanced_content=parsed.get("enhanced_content", original_input),
                enhancement_type=parsed.get("enhancement_type", "contextual"),
                relevance_score=min(1.0, max(0.0, parsed.get("relevance_score", 0.6))),
                semantic_links=semantic_links,
                confidence=min(1.0, max(0.0, parsed.get("confidence", 0.7))),
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "links_count": len(semantic_links),
                },
            )

        except Exception as e:
            logger.error(f"Failed to parse semantic enhancement response: {e}")
            return SemanticEnhancementResult(
                enhanced_content=original_input,
                enhancement_type="fallback",
                relevance_score=0.3,
                semantic_links=[],
                confidence=0.3,
                metadata={
                    "provider": "llm_fallback",
                    "model": self.config.model_name,
                    "original_content": original_input,
                    "error": str(e),
                },
            )


class MemoryActivationManager(LLMModuleManager[ActivationResult, MemoryActivationConfig]):
    """记忆激活管理器"""

    def __init__(self):
        super().__init__("memory_activation")

    async def activate_memory_async(
        self,
        query: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ActivationResult:
        """激活记忆 - 提供向后兼容的方法名"""
        return await self.process(query, provider_name, context)


class SemanticEnhancementManager(LLMModuleManager[SemanticEnhancementResult, MemoryActivationConfig]):
    """语义增强管理器"""

    def __init__(self):
        super().__init__("semantic_enhancement")

    async def enhance_semantic_async(
        self,
        content: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SemanticEnhancementResult:
        """语义增强 - 提供向后兼容的方法名"""
        return await self.process(content, provider_name, context)