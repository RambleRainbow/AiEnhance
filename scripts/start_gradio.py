#!/usr/bin/env python3
"""
AiEnhance Gradio界面启动脚本
自动检查依赖并启动可视化界面
"""

import importlib
import logging
import os
import subprocess
import sys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_and_install_package(package_name: str, import_name: str = None):
    """检查并安装缺失的包"""
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        logger.info(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        logger.warning(f"⚠️ {package_name} 未安装，正在安装...")

        # 检测是否在uv环境中
        if is_uv_environment():
            return install_with_uv(package_name)
        else:
            return install_with_pip(package_name)


def is_uv_environment():
    """检测是否在uv环境中"""
    # 检查是否存在uv命令
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        # 检查是否在.venv目录中
        venv_path = os.path.join(os.getcwd(), ".venv")
        return os.path.exists(venv_path) and sys.executable.startswith(venv_path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_with_uv(package_name: str):
    """使用uv安装包"""
    try:
        subprocess.check_call(["uv", "add", package_name])
        logger.info(f"✅ {package_name} 安装成功 (uv)")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {package_name} uv安装失败: {e}")
        # 尝试使用uv pip作为后备
        try:
            subprocess.check_call(["uv", "pip", "install", package_name])
            logger.info(f"✅ {package_name} 安装成功 (uv pip)")
            return True
        except subprocess.CalledProcessError as e2:
            logger.error(f"❌ {package_name} uv pip安装也失败: {e2}")
            return False


def install_with_pip(package_name: str):
    """使用pip安装包"""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ])
        logger.info(f"✅ {package_name} 安装成功 (pip)")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {package_name} pip安装失败: {e}")
        return False


def install_required_dependencies():
    """安装必需的依赖包"""
    dependencies = [
        ("gradio", "gradio"),
        ("plotly", "plotly"),
        ("pandas", "pandas"),
        ("asyncio", None),  # 内置模块
        ("json", None),     # 内置模块
    ]

    logger.info("🔍 检查依赖包...")

    all_installed = True
    for package, import_name in dependencies:
        if import_name is None:  # 内置模块
            continue

        if not check_and_install_package(package, import_name):
            all_installed = False

    return all_installed


def check_ollama_service():
    """检查Ollama服务状态"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=3)
        if response.status_code == 200:
            logger.info("✅ Ollama服务运行正常")
            return True
        else:
            logger.warning("⚠️ Ollama服务可能有问题")
            return False
    except Exception as e:
        logger.warning(f"⚠️ 无法连接到Ollama服务: {e}")
        logger.info("💡 提示: 如果需要使用本地LLM，请启动Ollama服务: ollama serve")
        return False


def main():
    """主启动函数"""
    print("🚀 启动 AiEnhance Gradio 可视化界面...")
    print("=" * 60)

    # 检查依赖
    logger.info("1️⃣ 检查Python依赖...")
    if not install_required_dependencies():
        logger.error("❌ 依赖安装失败，请手动安装缺失的包")
        sys.exit(1)

    # 检查Ollama服务（可选）
    logger.info("2️⃣ 检查Ollama服务状态...")
    check_ollama_service()

    # 启动Gradio界面
    logger.info("3️⃣ 启动Gradio界面...")
    try:
        from gradio_interface import main as start_gradio
        start_gradio()
    except ImportError as e:
        logger.error(f"❌ 无法导入Gradio界面: {e}")
        logger.info("请确保 gradio_interface.py 文件存在且无语法错误")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
