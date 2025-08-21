#!/usr/bin/env python3
"""
AiEnhance Gradio界面 UV环境专用启动脚本
专门为uv包管理环境设计的启动脚本
"""

import sys
import subprocess
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_uv_installation():
    """检查uv是否安装"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        logger.info(f"✅ UV已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ UV未安装，请先安装uv: pip install uv")
        return False


def install_dependencies_with_uv():
    """使用uv安装依赖"""
    dependencies = [
        "gradio",
        "plotly", 
        "pandas",
        "requests"
    ]
    
    logger.info("🔍 使用UV安装依赖包...")
    
    failed_packages = []
    
    for package in dependencies:
        logger.info(f"安装 {package}...")
        try:
            # 使用uv add安装
            subprocess.check_call(["uv", "add", package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            logger.info(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            # 如果uv add失败，尝试uv pip install
            try:
                subprocess.check_call(["uv", "pip", "install", package],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
                logger.info(f"✅ {package} 安装成功 (使用uv pip)")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ {package} 安装失败")
                failed_packages.append(package)
    
    return len(failed_packages) == 0, failed_packages


def check_existing_dependencies():
    """检查现有依赖"""
    try:
        import gradio
        import plotly
        import pandas
        logger.info("✅ 主要依赖已安装")
        return True
    except ImportError as e:
        logger.warning(f"⚠️ 缺少依赖: {e}")
        return False


def start_demo_interface():
    """启动演示界面"""
    logger.info("🚀 启动演示界面...")
    try:
        # 直接运行演示脚本
        subprocess.check_call([sys.executable, "demo_gradio.py"])
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 演示界面启动失败: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ 找不到demo_gradio.py文件")
        return False
    return True


def start_full_interface():
    """启动完整界面"""
    logger.info("🚀 尝试启动完整界面...")
    try:
        subprocess.check_call([sys.executable, "gradio_interface.py"])
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ 完整界面启动失败，回退到演示模式: {e}")
        return start_demo_interface()
    except FileNotFoundError:
        logger.warning("⚠️ 找不到gradio_interface.py，回退到演示模式")
        return start_demo_interface()
    return True


def main():
    """主启动函数"""
    print("🚀 启动 AiEnhance Gradio 可视化界面 (UV环境)")
    print("=" * 60)
    
    # 检查UV安装
    if not check_uv_installation():
        sys.exit(1)
    
    # 检查现有依赖
    if not check_existing_dependencies():
        logger.info("📦 需要安装依赖包...")
        
        success, failed = install_dependencies_with_uv()
        
        if not success:
            logger.error(f"❌ 以下包安装失败: {failed}")
            logger.info("💡 请手动安装：")
            for package in failed:
                logger.info(f"   uv add {package}")
            
            # 尝试启动演示版本
            logger.info("🎯 尝试启动演示版本（无需额外依赖）...")
            if not start_demo_interface():
                sys.exit(1)
        else:
            logger.info("✅ 所有依赖安装成功！")
    
    # 启动界面
    logger.info("🎬 启动Web界面...")
    
    # 优先尝试完整版本
    if not start_full_interface():
        logger.error("❌ 无法启动任何界面")
        sys.exit(1)


if __name__ == "__main__":
    main()