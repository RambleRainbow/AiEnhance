"""
MIRIX LLM桥接适配器
将项目的LLM抽象层桥接到MIRIX系统中，实现非侵入式集成
"""

import logging
import os
import tempfile
from typing import Any

import yaml

from ...llm.interfaces import LLMProvider, ModelConfig

logger = logging.getLogger(__name__)


class MirixLLMBridge:
    """
    MIRIX LLM桥接器

    将项目的LLM提供商适配到MIRIX使用的配置格式
    实现非侵入式集成，让MIRIX使用项目统一的LLM抽象
    """

    def __init__(self, llm_provider: LLMProvider):
        """
        初始化LLM桥接器

        Args:
            llm_provider: 项目中的LLM提供商实例
        """
        self.llm_provider = llm_provider
        self.temp_config_path = None

    def create_mirix_config(self, agent_name: str = "aienhance_mirix") -> str:
        """
        为MIRIX创建兼容的配置文件

        Args:
            agent_name: MIRIX智能体名称

        Returns:
            str: 临时配置文件路径
        """
        config = self._generate_mirix_config(agent_name)

        # 创建临时配置文件
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        )

        yaml.dump(config, temp_file, default_flow_style=False, allow_unicode=True)
        temp_file.flush()

        self.temp_config_path = temp_file.name
        temp_file.close()

        logger.info(f"为MIRIX创建配置文件: {self.temp_config_path}")
        return self.temp_config_path

    def _generate_mirix_config(self, agent_name: str) -> dict[str, Any]:
        """
        生成MIRIX兼容的配置

        Args:
            agent_name: 智能体名称

        Returns:
            Dict: MIRIX配置字典
        """
        llm_config = self.llm_provider.config
        provider = llm_config.provider.lower()

        # 基础配置
        config = {"agent_name": agent_name, "model_name": llm_config.model_name}

        # 根据提供商类型适配配置
        if provider == "ollama":
            config.update(self._adapt_ollama_config(llm_config))
        elif provider == "openai":
            config.update(self._adapt_openai_config(llm_config))
        elif provider == "anthropic":
            config.update(self._adapt_anthropic_config(llm_config))
        else:
            # 通用配置
            config.update(self._adapt_generic_config(llm_config))

        # 生成配置
        if llm_config.temperature is not None:
            config.setdefault("generation_config", {})["temperature"] = (
                llm_config.temperature
            )
        if llm_config.max_tokens is not None:
            config.setdefault("generation_config", {})["max_tokens"] = (
                llm_config.max_tokens
            )

        return config

    def _adapt_ollama_config(self, llm_config: ModelConfig) -> dict[str, Any]:
        """适配Ollama配置"""
        config = {}

        if llm_config.api_base:
            config["model_endpoint"] = llm_config.api_base

        # Ollama通常不需要API密钥，但如果有自定义配置则添加
        if llm_config.custom_config:
            config.update(llm_config.custom_config)

        return config

    def _adapt_openai_config(self, llm_config: ModelConfig) -> dict[str, Any]:
        """适配OpenAI配置"""
        config = {}

        # 设置API密钥环境变量
        if llm_config.api_key:
            os.environ["OPENAI_API_KEY"] = llm_config.api_key

        if llm_config.api_base and llm_config.api_base != "https://api.openai.com/v1":
            config["model_endpoint"] = llm_config.api_base

        if llm_config.organization:
            os.environ["OPENAI_ORG_ID"] = llm_config.organization

        return config

    def _adapt_anthropic_config(self, llm_config: ModelConfig) -> dict[str, Any]:
        """适配Anthropic配置"""
        config = {}

        # 设置API密钥环境变量
        if llm_config.api_key:
            os.environ["ANTHROPIC_API_KEY"] = llm_config.api_key

        if llm_config.api_base:
            config["model_endpoint"] = llm_config.api_base

        return config

    def _adapt_generic_config(self, llm_config: ModelConfig) -> dict[str, Any]:
        """适配通用配置"""
        config = {}

        # 通用API密钥设置
        if llm_config.api_key:
            provider_upper = llm_config.provider.upper()
            os.environ[f"{provider_upper}_API_KEY"] = llm_config.api_key

        if llm_config.api_base:
            config["model_endpoint"] = llm_config.api_base

        if llm_config.custom_config:
            config.update(llm_config.custom_config)

        return config

    def setup_environment_variables(self):
        """设置MIRIX需要的环境变量"""
        llm_config = self.llm_provider.config
        provider = llm_config.provider.lower()

        # 为MIRIX设置对应的环境变量
        if provider == "openai" and llm_config.api_key:
            os.environ["OPENAI_API_KEY"] = llm_config.api_key
        elif provider == "anthropic" and llm_config.api_key:
            os.environ["ANTHROPIC_API_KEY"] = llm_config.api_key
        elif provider == "google_ai" and llm_config.api_key:
            os.environ["GEMINI_API_KEY"] = llm_config.api_key

        logger.debug(f"为MIRIX设置环境变量: {provider}")

    def get_mirix_model_provider(self) -> str:
        """
        获取MIRIX兼容的模型提供商名称

        Returns:
            str: MIRIX格式的提供商名称
        """
        provider_mapping = {
            "ollama": "ollama",
            "openai": "openai",
            "anthropic": "anthropic",
            "google_ai": "google_ai",
            "azure": "azure_openai",
        }

        provider = self.llm_provider.config.provider.lower()
        return provider_mapping.get(provider, provider)

    def get_initialization_params(self) -> dict[str, Any]:
        """
        获取MIRIX SDK初始化参数

        Returns:
            Dict: 初始化参数字典
        """
        llm_config = self.llm_provider.config
        provider = llm_config.provider.lower()

        params = {
            "model_provider": self.get_mirix_model_provider(),
            "model": llm_config.model_name,
        }

        # 根据提供商类型决定是否需要API密钥
        if provider == "ollama":
            # Ollama通常不需要API密钥，使用占位符或空字符串
            params["api_key"] = "ollama_local_placeholder"
        elif llm_config.api_key:
            # 其他提供商使用实际API密钥
            params["api_key"] = llm_config.api_key
        else:
            # 对于需要API密钥但未提供的情况，使用占位符
            params["api_key"] = "not_required_for_local_llm"

        # 添加配置文件路径
        if self.temp_config_path:
            params["config_path"] = self.temp_config_path

        return params

    def cleanup(self):
        """清理临时文件"""
        if self.temp_config_path and os.path.exists(self.temp_config_path):
            try:
                os.unlink(self.temp_config_path)
                logger.debug(f"清理临时配置文件: {self.temp_config_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")
            finally:
                self.temp_config_path = None

    def __del__(self):
        """析构时自动清理"""
        self.cleanup()


def create_mirix_bridge(llm_provider: LLMProvider) -> MirixLLMBridge:
    """
    创建MIRIX LLM桥接器的便捷函数

    Args:
        llm_provider: LLM提供商实例

    Returns:
        MirixLLMBridge: 桥接器实例
    """
    return MirixLLMBridge(llm_provider)
