#!/usr/bin/env python3
"""
集中式提示词管理系统演示
展示如何使用新的提示词管理系统进行模板管理和渲染
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from aienhance.core.prompts import (
    get_prompt_manager,
    render_prompt,
    get_prompt_template,
    list_available_prompts,
    PromptTemplate,
)


def demonstrate_prompt_listing():
    """演示提示词列表功能"""
    print("🔧 提示词管理系统演示")
    print("=" * 50)

    print("\n1️⃣ 所有可用提示词:")
    all_prompts = list_available_prompts()
    for prompt in all_prompts:
        print(f"   • {prompt}")

    print("\n2️⃣ 按类别分组的提示词:")
    categories = ["domain_inference", "user_modeling", "cognitive_analysis"]

    for category in categories:
        print(f"\n   📌 {category}:")
        category_prompts = list_available_prompts(category)
        for prompt in category_prompts:
            print(f"      - {prompt}")


def demonstrate_template_info():
    """演示模板信息查看"""
    print("\n" + "=" * 50)
    print("📋 模板详细信息")
    print("=" * 50)

    manager = get_prompt_manager()
    template_names = [
        "domain_inference_basic",
        "cognitive_analysis",
        "context_analysis",
    ]

    for name in template_names:
        try:
            info = manager.get_template_info(name)
            print(f"\n🔍 模板: {name}")
            print(f"   描述: {info['description']}")
            print(f"   类别: {info['category']}")
            print(f"   变量: {info['variables']}")
            print(
                f"   推荐设置: T={info['recommended_settings']['temperature']}, "
                f"Max={info['recommended_settings']['max_tokens']}"
            )
            print(f"   版本: {info['versions']} (最新: {info['latest_version']})")
        except ValueError as e:
            print(f"   ❌ {name}: {e}")


def demonstrate_prompt_rendering():
    """演示提示词渲染"""
    print("\n" + "=" * 50)
    print("🎨 提示词渲染演示")
    print("=" * 50)

    # 领域推断示例
    print("\n1️⃣ 领域推断提示词渲染:")
    domain_prompt = render_prompt(
        name="domain_inference_basic",
        variables={
            "domains": "technology, science, education, business, art",
            "query": "如何使用Python开发机器学习应用？",
            "context": {"level": "intermediate", "background": "software_developer"},
        },
    )
    print("渲染结果:")
    print("─" * 40)
    print(domain_prompt[:300] + "..." if len(domain_prompt) > 300 else domain_prompt)

    # 认知分析示例
    print("\n2️⃣ 认知分析提示词渲染:")
    cognitive_prompt = render_prompt(
        name="cognitive_analysis",
        variables={
            "domain_context": "技术领域：平衡分析各项认知能力",
            "current_query": "我想深入学习算法设计和优化",
            "historical_data": "用户之前询问过基础编程问题",
        },
    )
    print("渲染结果:")
    print("─" * 40)
    print(
        cognitive_prompt[:300] + "..."
        if len(cognitive_prompt) > 300
        else cognitive_prompt
    )


def demonstrate_advanced_features():
    """演示高级功能"""
    print("\n" + "=" * 50)
    print("⚙️ 高级功能演示")
    print("=" * 50)

    manager = get_prompt_manager()

    # 1. 添加自定义模板
    print("\n1️⃣ 添加自定义提示词模板:")
    custom_template = PromptTemplate(
        name="custom_example",
        version="1.0",
        template="这是一个自定义模板示例：{content}\n参数：{param1}, {param2}",
        description="自定义示例模板",
        variables=["content", "param1", "param2"],
        category="examples",
        temperature=0.5,
        max_tokens=200,
    )

    success = manager.add_template(custom_template)
    print(f"   添加结果: {'✅ 成功' if success else '❌ 失败'}")

    if success:
        # 使用自定义模板
        custom_rendered = render_prompt(
            name="custom_example",
            variables={"content": "测试内容", "param1": "参数1", "param2": "参数2"},
        )
        print(f"   渲染结果: {custom_rendered}")

    # 2. 版本管理演示
    print("\n2️⃣ 版本管理:")
    try:
        # 获取特定版本
        template_v1 = get_prompt_template("domain_inference_basic", "1.0")
        print(f"   获取v1.0版本: ✅ {template_v1.name}")

        # 获取最新版本（默认）
        template_latest = get_prompt_template("domain_inference_basic")
        print(f"   获取最新版本: ✅ {template_latest.name} v{template_latest.version}")

    except ValueError as e:
        print(f"   版本获取失败: ❌ {e}")


def demonstrate_best_practices():
    """演示最佳实践"""
    print("\n" + "=" * 50)
    print("💡 最佳实践演示")
    print("=" * 50)

    print("\n1️⃣ 提示词设计原则:")
    print("   • 明确的指令和期望输出格式")
    print("   • 合理的变量占位符设计")
    print("   • 恰当的温度和token设置")
    print("   • 清晰的版本管理策略")

    print("\n2️⃣ 模板组织建议:")
    print("   • 按业务功能分类 (domain_inference, user_modeling等)")
    print("   • 使用语义化的版本号")
    print("   • 提供详细的描述和使用说明")
    print("   • 记录推荐的模型参数设置")

    print("\n3️⃣ 变更管理流程:")
    print("   • 新增模板时进行充分测试")
    print("   • 版本升级时保持向后兼容")
    print("   • 废弃旧版本时提供迁移指南")
    print("   • 维护模板使用文档和示例")

    print("\n4️⃣ 性能优化建议:")
    print("   • 合理控制提示词长度")
    print("   • 避免过度复杂的模板嵌套")
    print("   • 缓存常用的渲染结果")
    print("   • 监控不同模板的效果和性能")


def main():
    """主演示函数"""
    print("🚀 集中式提示词管理系统完整演示")
    print("=" * 70)

    # 基础功能演示
    demonstrate_prompt_listing()
    demonstrate_template_info()
    demonstrate_prompt_rendering()

    # 高级功能演示
    demonstrate_advanced_features()

    # 最佳实践
    demonstrate_best_practices()

    print("\n" + "=" * 70)
    print("✨ 演示完成!")
    print("💡 这个系统支持:")
    print("   • 集中式提示词模板管理")
    print("   • 版本控制和向后兼容")
    print("   • 灵活的变量替换和渲染")
    print("   • 按类别组织和检索模板")
    print("   • 推荐参数设置和元数据")
    print("   • 易于扩展的插件架构")
    print("=" * 70)


if __name__ == "__main__":
    main()
