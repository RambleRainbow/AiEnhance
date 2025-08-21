#!/usr/bin/env python3
"""
UV环境依赖安装脚本
为uv环境安装Gradio界面所需的依赖包
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """安装UV环境依赖"""
    print("📦 为UV环境安装Gradio界面依赖...")
    print("=" * 50)
    
    # 需要安装的包
    dependencies = [
        "gradio",
        "plotly", 
        "pandas",
        "requests"
    ]
    
    failed_packages = []
    
    for package in dependencies:
        print(f"安装 {package}...")
        try:
            # 使用uv add命令
            result = subprocess.run(
                ["uv", "add", package], 
                capture_output=True, 
                text=True,
                check=True
            )
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 使用uv add失败，尝试uv pip install...")
            try:
                result = subprocess.run(
                    ["uv", "pip", "install", package],
                    capture_output=True,
                    text=True, 
                    check=True
                )
                print(f"✅ {package} 安装成功 (uv pip)")
            except subprocess.CalledProcessError as e2:
                print(f"❌ {package} 安装失败: {e2}")
                failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if failed_packages:
        print(f"❌ 以下包安装失败: {', '.join(failed_packages)}")
        print("\n💡 手动安装命令:")
        for package in failed_packages:
            print(f"  uv add {package}")
        sys.exit(1)
    else:
        print("✅ 所有依赖安装成功！")
        print("\n🚀 现在可以运行:")
        print("  uv run demo_gradio.py        # 演示版本")
        print("  uv run gradio_interface.py   # 完整版本")

if __name__ == "__main__":
    main()