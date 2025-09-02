"""
统一的层-模块-子模块抽象基类架构

基于设计文档的三层式结构：
- Layer（层）：系统的主要认知功能层
- Module（模块）：层内的功能模块
- SubModule（子模块）：模块内的具体功能实现

所有子模块的功能原则上都使用大模型实现。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingPhase(Enum):
    """处理阶段枚举"""
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProcessingContext:
    """处理上下文，在层-模块-子模块间传递"""
    user_id: str
    query: str
    session_context: Dict[str, Any]
    layer_outputs: Dict[str, Any]
    module_outputs: Dict[str, Any] 
    submodule_outputs: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.layer_outputs:
            self.layer_outputs = {}
        if not self.module_outputs:
            self.module_outputs = {}
        if not self.submodule_outputs:
            self.submodule_outputs = {}
        if not self.metadata:
            self.metadata = {
                "created_at": datetime.now(),
                "processing_history": []
            }


@dataclass
class ProcessingResult:
    """处理结果统一格式"""
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "processed_at": datetime.now(),
                "processing_time_ms": 0
            }


class BaseSubModule(ABC):
    """子模块抽象基类
    
    所有子模块都继承此基类，实现具体的认知功能。
    原则上所有功能都通过大模型实现。
    """
    
    def __init__(self, name: str, llm_adapter=None, config: Dict[str, Any] = None):
        self.name = name
        self.llm_adapter = llm_adapter
        self.config = config or {}
        self.enabled = config.get('enabled', True) if config else True
        self.phase = ProcessingPhase.INITIALIZING
        
    async def initialize(self) -> bool:
        """初始化子模块"""
        try:
            await self._initialize_impl()
            self.phase = ProcessingPhase.COMPLETED
            logger.info(f"SubModule {self.name} initialized successfully")
            return True
        except Exception as e:
            self.phase = ProcessingPhase.ERROR
            logger.error(f"SubModule {self.name} initialization failed: {e}")
            return False
    
    @abstractmethod
    async def _initialize_impl(self):
        """子模块具体初始化实现"""
        pass
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理核心逻辑"""
        pass
    
    async def process_with_llm(self, prompt: str, context: ProcessingContext) -> str:
        """使用LLM处理的通用方法"""
        if not self.llm_adapter:
            raise ValueError(f"SubModule {self.name} requires LLM adapter")
        
        try:
            response = await self.llm_adapter.generate_response(
                prompt=prompt,
                context=context.session_context
            )
            return response
        except Exception as e:
            logger.error(f"LLM processing failed in {self.name}: {e}")
            raise
    
    def is_enabled(self) -> bool:
        """检查子模块是否启用"""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """获取子模块配置"""
        return self.config.copy()


class BaseModule(ABC):
    """模块抽象基类
    
    模块管理多个子模块，协调它们的工作流程
    """
    
    def __init__(self, name: str, submodules: List[BaseSubModule] = None, config: Dict[str, Any] = None):
        self.name = name
        self.submodules = submodules or []
        self.config = config or {}
        self.enabled = config.get('enabled', True) if config else True
        self.phase = ProcessingPhase.INITIALIZING
        
    async def initialize(self) -> bool:
        """初始化模块和所有子模块"""
        try:
            # 初始化所有子模块
            init_results = await asyncio.gather(
                *[submodule.initialize() for submodule in self.submodules],
                return_exceptions=True
            )
            
            # 检查初始化结果
            failed_submodules = []
            for i, result in enumerate(init_results):
                if isinstance(result, Exception) or not result:
                    failed_submodules.append(self.submodules[i].name)
            
            if failed_submodules:
                logger.warning(f"Module {self.name}: Some submodules failed to initialize: {failed_submodules}")
            
            # 执行模块级初始化
            await self._initialize_impl()
            
            self.phase = ProcessingPhase.COMPLETED
            logger.info(f"Module {self.name} initialized successfully")
            return True
            
        except Exception as e:
            self.phase = ProcessingPhase.ERROR
            logger.error(f"Module {self.name} initialization failed: {e}")
            return False
    
    @abstractmethod
    async def _initialize_impl(self):
        """模块具体初始化实现"""
        pass
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理核心逻辑，协调子模块"""
        pass
    
    async def process_submodules(self, context: ProcessingContext, 
                                submodule_names: List[str] = None) -> Dict[str, ProcessingResult]:
        """处理指定的子模块"""
        if submodule_names is None:
            submodules_to_process = [sm for sm in self.submodules if sm.is_enabled()]
        else:
            submodules_to_process = [sm for sm in self.submodules 
                                   if sm.name in submodule_names and sm.is_enabled()]
        
        results = {}
        for submodule in submodules_to_process:
            try:
                result = await submodule.process(context)
                results[submodule.name] = result
                # 将子模块输出更新到上下文
                context.submodule_outputs[f"{self.name}.{submodule.name}"] = result.data
            except Exception as e:
                logger.error(f"SubModule {submodule.name} processing failed: {e}")
                results[submodule.name] = ProcessingResult(
                    success=False,
                    data={},
                    metadata={"error_time": datetime.now()},
                    error_message=str(e)
                )
        
        return results
    
    def add_submodule(self, submodule: BaseSubModule):
        """添加子模块"""
        self.submodules.append(submodule)
    
    def get_submodule(self, name: str) -> Optional[BaseSubModule]:
        """获取指定名称的子模块"""
        for submodule in self.submodules:
            if submodule.name == name:
                return submodule
        return None
    
    def is_enabled(self) -> bool:
        """检查模块是否启用"""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """获取模块配置"""
        return self.config.copy()


class BaseLayer(ABC):
    """层抽象基类
    
    层管理多个模块，代表系统的主要认知功能层
    """
    
    def __init__(self, name: str, modules: List[BaseModule] = None, config: Dict[str, Any] = None):
        self.name = name
        self.modules = modules or []
        self.config = config or {}
        self.enabled = config.get('enabled', True) if config else True
        self.phase = ProcessingPhase.INITIALIZING
        
    async def initialize(self) -> bool:
        """初始化层和所有模块"""
        try:
            # 初始化所有模块
            init_results = await asyncio.gather(
                *[module.initialize() for module in self.modules],
                return_exceptions=True
            )
            
            # 检查初始化结果
            failed_modules = []
            for i, result in enumerate(init_results):
                if isinstance(result, Exception) or not result:
                    failed_modules.append(self.modules[i].name)
            
            if failed_modules:
                logger.warning(f"Layer {self.name}: Some modules failed to initialize: {failed_modules}")
            
            # 执行层级初始化
            await self._initialize_impl()
            
            self.phase = ProcessingPhase.COMPLETED
            logger.info(f"Layer {self.name} initialized successfully")
            return True
            
        except Exception as e:
            self.phase = ProcessingPhase.ERROR
            logger.error(f"Layer {self.name} initialization failed: {e}")
            return False
    
    @abstractmethod
    async def _initialize_impl(self):
        """层具体初始化实现"""
        pass
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        """处理核心逻辑，协调模块"""
        pass
    
    async def process_modules(self, context: ProcessingContext, 
                             module_names: List[str] = None) -> Dict[str, ProcessingResult]:
        """处理指定的模块"""
        if module_names is None:
            modules_to_process = [m for m in self.modules if m.is_enabled()]
        else:
            modules_to_process = [m for m in self.modules 
                                if m.name in module_names and m.is_enabled()]
        
        results = {}
        for module in modules_to_process:
            try:
                result = await module.process(context)
                results[module.name] = result
                # 将模块输出更新到上下文
                context.module_outputs[f"{self.name}.{module.name}"] = result.data
            except Exception as e:
                logger.error(f"Module {module.name} processing failed: {e}")
                results[module.name] = ProcessingResult(
                    success=False,
                    data={},
                    metadata={"error_time": datetime.now()},
                    error_message=str(e)
                )
        
        return results
    
    def add_module(self, module: BaseModule):
        """添加模块"""
        self.modules.append(module)
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """获取指定名称的模块"""
        for module in self.modules:
            if module.name == name:
                return module
        return None
    
    def is_enabled(self) -> bool:
        """检查层是否启用"""
        return self.enabled
    
    def get_config(self) -> Dict[str, Any]:
        """获取层配置"""
        return self.config.copy()


class CognitiveSystem:
    """认知系统主类
    
    管理四个认知层的协同工作
    """
    
    def __init__(self, layers: List[BaseLayer], config: Dict[str, Any] = None):
        self.layers = layers
        self.config = config or {}
        self.phase = ProcessingPhase.INITIALIZING
        
    async def initialize(self) -> bool:
        """初始化所有层"""
        try:
            # 初始化所有层
            init_results = await asyncio.gather(
                *[layer.initialize() for layer in self.layers],
                return_exceptions=True
            )
            
            # 检查初始化结果
            failed_layers = []
            for i, result in enumerate(init_results):
                if isinstance(result, Exception) or not result:
                    failed_layers.append(self.layers[i].name)
            
            if failed_layers:
                logger.warning(f"System: Some layers failed to initialize: {failed_layers}")
                if len(failed_layers) >= len(self.layers):
                    raise Exception("All layers failed to initialize")
            
            self.phase = ProcessingPhase.COMPLETED
            logger.info("Cognitive system initialized successfully")
            return True
            
        except Exception as e:
            self.phase = ProcessingPhase.ERROR
            logger.error(f"System initialization failed: {e}")
            return False
    
    async def process(self, user_id: str, query: str, session_context: Dict[str, Any] = None) -> ProcessingResult:
        """系统处理主流程"""
        context = ProcessingContext(
            user_id=user_id,
            query=query,
            session_context=session_context or {},
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={}
        )
        
        try:
            # 按顺序处理各层
            for layer in self.layers:
                if layer.is_enabled():
                    result = await layer.process(context)
                    context.layer_outputs[layer.name] = result.data
                    context.metadata["processing_history"].append(
                        {"layer": layer.name, "status": "completed", "time": datetime.now()}
                    )
            
            return ProcessingResult(
                success=True,
                data={
                    "layer_outputs": context.layer_outputs,
                    "module_outputs": context.module_outputs,
                    "submodule_outputs": context.submodule_outputs
                },
                metadata=context.metadata
            )
            
        except Exception as e:
            logger.error(f"System processing failed: {e}")
            return ProcessingResult(
                success=False,
                data={},
                metadata=context.metadata,
                error_message=str(e)
            )
    
    def get_layer(self, name: str) -> Optional[BaseLayer]:
        """获取指定名称的层"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None