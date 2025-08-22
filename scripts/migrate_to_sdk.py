#!/usr/bin/env python3
"""
MIRIX SDK 迁移助手
帮助用户从Docker/HTTP模式迁移到SDK模式
"""

import os
import subprocess
import sys
from pathlib import Path


def check_requirement(name, check_func, install_hint=None):
    """检查依赖项"""
    try:
        result = check_func()
        if result:
            print(f"✅ {name}: 已满足")
            return True
        else:
            print(f"❌ {name}: 未满足")
            if install_hint:
                print(f"   💡 {install_hint}")
            return False
    except Exception as e:
        print(f"❌ {name}: 检查失败 ({e})")
        if install_hint:
            print(f"   💡 {install_hint}")
        return False


def check_python_version():
    """检查Python版本"""
    return sys.version_info >= (3, 8)


def check_mirix_package():
    """检查MIRIX包"""
    try:
        import mirix

        return True
    except ImportError:
        return False


def check_google_api_key():
    """检查Google API密钥"""
    return bool(os.getenv("GOOGLE_API_KEY"))


def install_mirix():
    """安装MIRIX包"""
    print("🔧 安装MIRIX SDK...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mirix"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ MIRIX SDK安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ MIRIX SDK安装失败: {e}")
        return False


def create_env_example():
    """创建.env示例文件"""
    env_example_content = """# MIRIX SDK配置
GOOGLE_API_KEY=your-google-api-key-here

# Ollama配置
OLLAMA_HOST=http://localhost:11434

# 日志配置
LOG_LEVEL=INFO
"""

    env_path = Path(".env.example")
    if not env_path.exists():
        env_path.write_text(env_example_content)
        print("✅ 创建了 .env.example 文件")
    else:
        print("ℹ️ .env.example 文件已存在")


def show_migration_steps():
    """显示迁移步骤"""
    print("\n🔄 迁移步骤总结:")
    print("=" * 50)
    print("1. 停止Docker服务:")
    print("   docker-compose down")
    print()
    print("2. 安装MIRIX SDK:")
    print("   pip install mirix")
    print()
    print("3. 设置Google API密钥:")
    print("   export GOOGLE_API_KEY='your-api-key'")
    print("   # 或在 .env 文件中设置")
    print()
    print("4. 测试新配置:")
    print("   python test_mirix_sdk.py")
    print()
    print("5. 使用新的CLI:")
    print("   python ai.py '测试MIRIX SDK集成'")


def main():
    """主函数"""
    print("🚀 MIRIX SDK 迁移助手")
    print("=" * 50)
    print("正在检查迁移准备情况...\n")

    # 检查依赖项
    checks = [
        ("Python版本 (>=3.8)", check_python_version, "请升级到Python 3.8+"),
        ("MIRIX包", check_mirix_package, "运行: pip install mirix"),
        (
            "Google API密钥",
            check_google_api_key,
            "设置环境变量: export GOOGLE_API_KEY='your-key'",
        ),
    ]

    all_passed = True
    for name, check_func, hint in checks:
        if not check_requirement(name, check_func, hint):
            all_passed = False

    print()

    # 如果MIRIX包未安装，尝试安装
    if not check_mirix_package():
        if input("是否现在安装MIRIX SDK? (y/N): ").lower() in ["y", "yes"]:
            if install_mirix():
                print("✅ MIRIX SDK安装完成")
            else:
                print("❌ 请手动安装: pip install mirix")
                all_passed = False

    # 创建配置文件示例
    create_env_example()

    print()

    if all_passed and check_mirix_package() and check_google_api_key():
        print("🎉 迁移准备完成！")
        print("你现在可以使用MIRIX SDK模式了。")

        if input("\n是否运行测试验证? (y/N): ").lower() in ["y", "yes"]:
            print("\n运行测试...")
            try:
                subprocess.run([sys.executable, "test_mirix_sdk.py"], check=True)
            except subprocess.CalledProcessError:
                print("❌ 测试失败，请检查配置")
            except FileNotFoundError:
                print("❌ 找不到测试文件，请确保在项目根目录")

    else:
        print("⚠️ 迁移准备未完成")
        print("请根据上述提示完成缺失的配置。")

    show_migration_steps()

    print("\n📚 更多信息请参考:")
    print("   - MIRIX_SDK_SETUP.md")
    print("   - 官方文档: https://docs.mirix.io")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 迁移助手已退出")
    except Exception as e:
        print(f"❌ 迁移助手运行失败: {e}")
