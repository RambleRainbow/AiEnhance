"""
通用LLM模块基础抽象
为所有业务模块提供统一的LLM集成模式
基于domain_inference模式的抽象和泛化
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .prompts import get_prompt_manager

logger = logging.getLogger(__name__)

# 泛型类型定义
T = TypeVar('T')  # 模块特定的结果类型
C = TypeVar('C')  # 模块特定的配置类型


@dataclass
class LLMModuleConfig:
    """通用LLM模块配置基类"""
    
    llm_provider: Any  # LLM提供商实例
    model_name: Optional[str] = None  # 特定模型名称
    temperature: float = 0.7  # 温度参数
    max_tokens: int = 800  # 最大token数
    timeout: int = 10  # 超时设置
    prompt_template_name: str = ""  # 提示词模板名称
    custom_params: Optional[Dict[str, Any]] = None  # 自定义参数


class LLMModuleProvider(ABC, Generic[T, C]):
    """通用LLM模块提供商抽象基类
    
    所有业务模块都应继承此类，实现统一的LLM集成模式
    """
    
    def __init__(self, config: C):
        self.config = config
        self.is_initialized = False
        self.llm_provider = getattr(config, 'llm_provider', None)
        self.prompt_manager = get_prompt_manager()
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化提供商"""
        pass
    
    @abstractmethod
    async def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> T:
        """处理业务逻辑 - 每个模块实现自己的业务处理"""
        pass
    
    @abstractmethod
    def _parse_llm_response(self, response: str, original_input: str) -> T:
        """解析LLM响应 - 每个模块实现自己的响应解析逻辑"""
        pass
    
    @abstractmethod
    def _prepare_prompt_variables(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """准备提示词变量 - 每个模块实现自己的变量准备逻辑"""
        pass
    
    async def _call_llm_with_prompt(self, prompt_template_name: str, variables: Dict[str, Any]) -> str:
        """通用LLM调用方法"""
        try:
            # 渲染提示词
            prompt = self.prompt_manager.render_prompt(
                name=prompt_template_name,
                variables=variables
            )
            
            # 调用LLM
            response = await asyncio.wait_for(
                self._call_llm(prompt),
                timeout=self.config.timeout
            )
            
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"LLM call timeout for template: {prompt_template_name}")
            raise TimeoutError(f"LLM call timeout after {self.config.timeout} seconds")
        except Exception as e:
            logger.error(f"LLM call failed for template {prompt_template_name}: {e}")
            raise
    
    async def _call_llm(self, prompt: str) -> str:
        """底层LLM调用 - 通用实现"""
        try:
            # 构建消息格式
            messages = [{"role": "user", "content": prompt}]
            
            # 适配不同LLM提供商接口
            if hasattr(self.llm_provider, "generate_async"):
                # 异步接口
                response = await self.llm_provider.generate_async(
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name,
                )
            elif hasattr(self.llm_provider, "chat"):
                # 同步聊天接口
                response = await asyncio.to_thread(
                    self.llm_provider.chat,
                    messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name or "default",
                )
            else:
                raise ValueError("Unsupported LLM provider interface")
            
            # 提取文本内容
            if isinstance(response, dict):
                return response.get("content", response.get("message", str(response)))
            elif hasattr(response, "content"):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """通用JSON提取方法"""
        try:
            # 清理响应格式
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # 解析JSON
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    async def cleanup(self) -> None:
        """清理资源 - 通用实现"""
        try:
            self.is_initialized = False
            logger.info(f"{self.__class__.__name__} cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class LLMModuleManager(Generic[T, C]):
    """通用LLM模块管理器基类
    
    支持多提供商配置和切换，为多模型协同调度做准备
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.providers: Dict[str, LLMModuleProvider[T, C]] = {}
        self.default_provider_name: Optional[str] = None
    
    async def register_provider(self, name: str, provider: LLMModuleProvider[T, C]) -> bool:
        """注册模块提供商"""
        try:
            success = await provider.initialize()
            if success:
                self.providers[name] = provider
                if self.default_provider_name is None:
                    self.default_provider_name = name
                logger.info(f"Registered {self.module_name} provider: {name}")
                return True
            else:
                logger.error(f"Failed to initialize {self.module_name} provider: {name}")
                return False
        except Exception as e:
            logger.error(f"Error registering {self.module_name} provider {name}: {e}")
            return False
    
    async def process(
        self,
        input_data: str,
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> T:
        """处理业务逻辑"""
        provider_name = provider_name or self.default_provider_name
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"{self.module_name} provider not found: {provider_name}")
        
        provider = self.providers[provider_name]
        return await provider.process(input_data, context)
    
    async def cleanup(self) -> None:
        """清理所有提供商"""
        for name, provider in self.providers.items():
            try:
                await provider.cleanup()
                logger.info(f"Cleaned up {self.module_name} provider: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up {self.module_name} provider {name}: {e}")
        
        self.providers.clear()
        self.default_provider_name = None
    
    def get_available_providers(self) -> List[str]:
        """获取可用提供商列表"""
        return list(self.providers.keys())
    
    def set_default_provider(self, name: str) -> bool:
        """设置默认提供商"""
        if name in self.providers:
            self.default_provider_name = name
            return True
        return False


@dataclass
class ModuleProcessingResult:
    """通用模块处理结果基类"""
    
    success: bool
    data: Any
    confidence: float
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None


def create_llm_module_config(
    llm_provider: Any,
    prompt_template_name: str,
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 800,
    timeout: int = 10,
    **custom_params
) -> LLMModuleConfig:
    """便捷的配置创建函数"""
    return LLMModuleConfig(
        llm_provider=llm_provider,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        prompt_template_name=prompt_template_name,
        custom_params=custom_params
    )