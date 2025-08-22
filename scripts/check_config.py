#!/usr/bin/env python3
"""
配置检查脚本
用于验证环境变量配置和系统状态
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from aienhance.config import config


def check_environment():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    print("=" * 50)

    # 打印配置摘要
    config.print_config_summary()

    print("\n🔧 详细配置:")
    print("=" * 50)

    # LLM配置
    llm_config = config.get_llm_config()
    print("📚 LLM配置:")
    for key, value in llm_config.items():
        print(f"   {key}: {value}")

    # 嵌入模型配置
    embedding_config = config.get_embedding_config()
    print("\n🔍 嵌入模型配置:")
    for key, value in embedding_config.items():
        print(f"   {key}: {value}")

    # 系统配置
    system_config = config.get_system_config()
    print("\n⚙️ 系统配置:")
    for key, value in system_config.items():
        print(f"   {key}: {value}")

    # Gradio配置
    gradio_config = config.get_gradio_config()
    print("\n🌐 Gradio配置:")
    for key, value in gradio_config.items():
        print(f"   {key}: {value}")

    # MIRIX配置
    mirix_config = config.get_mirix_config()
    print("\n🧠 MIRIX配置:")
    for key, value in mirix_config.items():
        print(f"   {key}: {value}")


def check_files():
    """检查重要文件存在性"""
    print("\n📁 检查配置文件:")
    print("=" * 50)

    files_to_check = [
        (".env", "环境变量文件"),
        (".env.example", "环境变量示例文件"),
        ("CLAUDE.md", "项目说明文档"),
        ("cli_example.py", "CLI入口文件"),
        ("gradio_interface.py", "Gradio界面文件"),
    ]

    for filename, description in files_to_check:
        file_path = Path(__file__).parent.parent / filename
        status = "✅ 存在" if file_path.exists() else "❌ 缺失"
        print(f"   {filename}: {status} ({description})")


def check_directories():
    """检查重要目录结构"""
    print("\n📂 检查目录结构:")
    print("=" * 50)

    directories_to_check = [
        ("aienhance", "主要包目录"),
        ("aienhance/core", "核心模块"),
        ("aienhance/llm", "LLM适配器"),
        ("aienhance/memory", "记忆系统"),
        ("scripts", "脚本目录"),
        ("tests", "测试目录"),
    ]

    base_path = Path(__file__).parent.parent
    for dirname, description in directories_to_check:
        dir_path = base_path / dirname
        status = "✅ 存在" if dir_path.exists() else "❌ 缺失"
        print(f"   {dirname}: {status} ({description})")


def main():
    """主函数"""
    print("🔧 AiEnhance配置检查工具")
    print("=" * 50)

    try:
        check_environment()
        check_files()
        check_directories()

        print("\n✅ 配置检查完成!")
        print("💡 如有问题，请检查 .env 文件或环境变量设置")

    except Exception as e:
        print(f"\n❌ 配置检查失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
