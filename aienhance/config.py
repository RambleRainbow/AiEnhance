"""
AiEnhance配置管理模块
统一管理环境变量和默认配置
"""

import os
from typing import Any


class Config:
    """配置管理器"""

    # LLM配置
    LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")
    LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "qwen3:8b")
    LLM_TEMPERATURE = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "800"))

    # Ollama配置
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # 嵌入模型配置
    EMBEDDING_PROVIDER = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "ollama")
    EMBEDDING_MODEL = os.getenv("DEFAULT_EMBEDDING_MODEL", "bge-m3")

    # 系统配置
    SYSTEM_TYPE = os.getenv("DEFAULT_SYSTEM_TYPE", "educational")
    MEMORY_SYSTEM = os.getenv("DEFAULT_MEMORY_SYSTEM", "mirix_unified")
    ENVIRONMENT = os.getenv("AIENHANCE_ENV", "development")

    # 功能开关
    ENABLE_MEMORY_SYSTEM = os.getenv("ENABLE_MEMORY_SYSTEM", "true").lower() == "true"
    ENABLE_STREAMING_OUTPUT = (
        os.getenv("ENABLE_STREAMING_OUTPUT", "true").lower() == "true"
    )
    ENABLE_COLLABORATION_LAYER = (
        os.getenv("ENABLE_COLLABORATION_LAYER", "true").lower() == "true"
    )

    # Gradio配置
    GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    # MIRIX配置
    MIRIX_AGENT_NAME = os.getenv("MIRIX_AGENT_NAME", "aienhance_unified")
    MIRIX_AUTO_SAVE_INTERACTIONS = (
        os.getenv("MIRIX_AUTO_SAVE_INTERACTIONS", "true").lower() == "true"
    )

    # 调试配置
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

    # 会话管理
    SESSION_TIMEOUT = int(os.getenv("DEFAULT_SESSION_TIMEOUT", "3600"))

    @classmethod
    def get_llm_config(cls) -> dict[str, Any]:
        """获取LLM配置字典"""
        return {
            "provider": cls.LLM_PROVIDER,
            "model_name": cls.LLM_MODEL,
            "api_base": cls.OLLAMA_BASE_URL,
            "temperature": cls.LLM_TEMPERATURE,
            "max_tokens": cls.LLM_MAX_TOKENS,
        }

    @classmethod
    def get_embedding_config(cls) -> dict[str, Any]:
        """获取嵌入模型配置字典"""
        return {
            "provider": cls.EMBEDDING_PROVIDER,
            "model_name": f"{cls.EMBEDDING_MODEL}:latest",
        }

    @classmethod
    def get_system_config(cls) -> dict[str, Any]:
        """获取系统配置字典"""
        return {
            "system_type": cls.SYSTEM_TYPE,
            "memory_system_type": cls.MEMORY_SYSTEM,
            "environment": cls.ENVIRONMENT,
            "enable_memory": cls.ENABLE_MEMORY_SYSTEM,
            "enable_streaming": cls.ENABLE_STREAMING_OUTPUT,
            "enable_collaboration": cls.ENABLE_COLLABORATION_LAYER,
        }

    @classmethod
    def get_gradio_config(cls) -> dict[str, Any]:
        """获取Gradio配置字典"""
        return {
            "server_name": cls.GRADIO_SERVER_NAME,
            "server_port": cls.GRADIO_SERVER_PORT,
            "share": cls.GRADIO_SHARE,
            "debug": cls.DEBUG_MODE,
        }

    @classmethod
    def get_mirix_config(cls) -> dict[str, Any]:
        """获取MIRIX配置字典"""
        return {
            "agent_name": cls.MIRIX_AGENT_NAME,
            "auto_save_interactions": cls.MIRIX_AUTO_SAVE_INTERACTIONS,
        }

    @classmethod
    def print_config_summary(cls):
        """打印配置摘要"""
        print("🔧 AiEnhance配置摘要:")
        print(f"   LLM提供商: {cls.LLM_PROVIDER}")
        print(f"   LLM模型: {cls.LLM_MODEL}")
        print(f"   系统类型: {cls.SYSTEM_TYPE}")
        print(f"   记忆系统: {cls.MEMORY_SYSTEM}")
        print(f"   环境: {cls.ENVIRONMENT}")
        print(f"   Gradio端口: {cls.GRADIO_SERVER_PORT}")
        print(f"   记忆功能: {'启用' if cls.ENABLE_MEMORY_SYSTEM else '禁用'}")
        print(f"   协作层: {'启用' if cls.ENABLE_COLLABORATION_LAYER else '禁用'}")


# 全局配置实例
config = Config()
