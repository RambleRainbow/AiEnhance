"""
多LLM配置管理模块
为多模型协同调度提供配置抽象和管理功能
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMModelConfig:
    """单个LLM模型配置"""
    provider: str  # 提供商名称，如 "ollama", "openai", "anthropic"
    model_name: str  # 模型名称
    base_url: Optional[str] = None  # API基础URL
    api_key: Optional[str] = None  # API密钥
    temperature: float = 0.7  # 温度参数
    max_tokens: int = 800  # 最大输出token数
    timeout: int = 30  # 请求超时时间
    custom_params: Dict[str, Any] = field(default_factory=dict)  # 自定义参数


@dataclass 
class BusinessFunctionLLMConfig:
    """业务功能LLM配置"""
    function_name: str  # 业务功能名称
    primary_model: LLMModelConfig  # 主要模型
    fallback_model: Optional[LLMModelConfig] = None  # 备选模型
    enabled: bool = True  # 是否启用
    custom_config: Dict[str, Any] = field(default_factory=dict)  # 自定义配置


class MultiLLMConfigManager:
    """多LLM配置管理器"""
    
    def __init__(self):
        self.business_configs: Dict[str, BusinessFunctionLLMConfig] = {}
        self.default_config: Optional[LLMModelConfig] = None
        
    def set_default_config(self, config: LLMModelConfig):
        """设置默认LLM配置"""
        self.default_config = config
        logger.info(f"Set default LLM config: {config.provider}/{config.model_name}")
    
    def register_business_function(self, config: BusinessFunctionLLMConfig):
        """注册业务功能的LLM配置"""
        self.business_configs[config.function_name] = config
        logger.info(f"Registered LLM config for business function: {config.function_name}")
    
    def get_config_for_function(self, function_name: str) -> Optional[LLMModelConfig]:
        """获取指定业务功能的LLM配置"""
        if function_name in self.business_configs:
            config = self.business_configs[function_name]
            if config.enabled:
                return config.primary_model
        
        # 如果没有专门配置，返回默认配置
        return self.default_config
    
    def get_fallback_config_for_function(self, function_name: str) -> Optional[LLMModelConfig]:
        """获取指定业务功能的备选LLM配置"""
        if function_name in self.business_configs:
            config = self.business_configs[function_name]
            if config.enabled and config.fallback_model:
                return config.fallback_model
        
        return None
    
    def list_configured_functions(self) -> list[str]:
        """列出已配置的业务功能"""
        return [name for name, config in self.business_configs.items() if config.enabled]
    
    def disable_function(self, function_name: str) -> bool:
        """禁用指定业务功能的LLM"""
        if function_name in self.business_configs:
            self.business_configs[function_name].enabled = False
            logger.info(f"Disabled LLM for function: {function_name}")
            return True
        return False
    
    def enable_function(self, function_name: str) -> bool:
        """启用指定业务功能的LLM"""
        if function_name in self.business_configs:
            self.business_configs[function_name].enabled = True
            logger.info(f"Enabled LLM for function: {function_name}")
            return True
        return False


def create_config_from_dict(config_dict: Dict[str, Any]) -> MultiLLMConfigManager:
    """从字典创建多LLM配置管理器"""
    manager = MultiLLMConfigManager()
    
    # 设置默认配置
    if 'default' in config_dict:
        default_dict = config_dict['default']
        default_config = LLMModelConfig(
            provider=default_dict['provider'],
            model_name=default_dict['model_name'],
            base_url=default_dict.get('base_url'),
            api_key=default_dict.get('api_key'),
            temperature=default_dict.get('temperature', 0.7),
            max_tokens=default_dict.get('max_tokens', 800),
            timeout=default_dict.get('timeout', 30),
            custom_params=default_dict.get('custom_params', {})
        )
        manager.set_default_config(default_config)
    
    # 配置业务功能
    if 'business_functions' in config_dict:
        for func_name, func_config in config_dict['business_functions'].items():
            primary_config = LLMModelConfig(
                provider=func_config['primary']['provider'],
                model_name=func_config['primary']['model_name'],
                base_url=func_config['primary'].get('base_url'),
                api_key=func_config['primary'].get('api_key'),
                temperature=func_config['primary'].get('temperature', 0.7),
                max_tokens=func_config['primary'].get('max_tokens', 800),
                timeout=func_config['primary'].get('timeout', 30),
                custom_params=func_config['primary'].get('custom_params', {})
            )
            
            fallback_config = None
            if 'fallback' in func_config:
                fallback_config = LLMModelConfig(
                    provider=func_config['fallback']['provider'],
                    model_name=func_config['fallback']['model_name'],
                    base_url=func_config['fallback'].get('base_url'),
                    api_key=func_config['fallback'].get('api_key'),
                    temperature=func_config['fallback'].get('temperature', 0.7),
                    max_tokens=func_config['fallback'].get('max_tokens', 800),
                    timeout=func_config['fallback'].get('timeout', 30),
                    custom_params=func_config['fallback'].get('custom_params', {})
                )
            
            business_config = BusinessFunctionLLMConfig(
                function_name=func_name,
                primary_model=primary_config,
                fallback_model=fallback_config,
                enabled=func_config.get('enabled', True),
                custom_config=func_config.get('custom_config', {})
            )
            
            manager.register_business_function(business_config)
    
    return manager


# 预定义的常用配置模板
DOMAIN_INFERENCE_OPTIMIZED_CONFIG = {
    "provider": "ollama",
    "model_name": "qwen3:8b",  # 或其他适合分类任务的模型
    "temperature": 0.1,  # 低温度确保一致性
    "max_tokens": 300,   # 较少的token用于分类任务
    "timeout": 10        # 较短超时
}

CREATIVE_TASK_CONFIG = {
    "provider": "ollama", 
    "model_name": "qwen3:32b",  # 更大模型用于创意任务
    "temperature": 0.8,         # 高温度增加创造性
    "max_tokens": 1200,         # 更多token用于创意输出
    "timeout": 30
}

ANALYTICAL_TASK_CONFIG = {
    "provider": "ollama",
    "model_name": "qwen3:14b",  # 中等大小模型
    "temperature": 0.3,         # 中等温度平衡准确性和灵活性
    "max_tokens": 1000,         # 适中的token限制
    "timeout": 25
}