#!/usr/bin/env python3
"""测试Gradio界面属性修复"""

from datetime import datetime

# 导入接口定义
from aienhance.core.layer_interfaces import (
    AdaptedContent,
    AnalogyReasoning,
    BehaviorOutput,
    CognitionOutput,
    CognitiveChallenge,
    CollaborationOutput,
    MemoryActivation,
    PerspectiveGeneration,
    ProcessingStatus,
    SemanticEnhancement,
)


def test_gradio_attribute_access():
    """测试Gradio界面中的属性访问是否正确"""
    print("🔍 测试Gradio界面属性访问修复...")

    try:
        # 1. 测试MemoryActivation属性
        memory_activation = MemoryActivation(
            activated_fragments=["fragment1", "fragment2", "fragment3"],
            activation_confidence=0.85,
            activation_metadata={"source": "test", "timestamp": "2024-01-01"},
        )

        # 模拟Gradio界面代码中的属性访问
        activated_count = len(memory_activation.activated_fragments)
        confidence = memory_activation.activation_confidence
        metadata_count = len(memory_activation.activation_metadata)

        print("✅ MemoryActivation属性访问正确:")
        print(f"   - 激活记忆数: {activated_count}")
        print(f"   - 激活置信度: {confidence}")
        print(f"   - 激活元数据项: {metadata_count}")

        # 2. 测试SemanticEnhancement属性
        semantic_enhancement = SemanticEnhancement(
            enhanced_content=["enhanced1", "enhanced2"],
            semantic_gaps_filled=["gap1", "gap2", "gap3"],
            enhancement_confidence=0.75,
        )

        enhanced_count = len(semantic_enhancement.enhanced_content)
        gaps_filled = len(semantic_enhancement.semantic_gaps_filled)
        enhancement_conf = semantic_enhancement.enhancement_confidence

        print("✅ SemanticEnhancement属性访问正确:")
        print(f"   - 增强内容数: {enhanced_count}")
        print(f"   - 语义补全数: {gaps_filled}")
        print(f"   - 增强置信度: {enhancement_conf}")

        # 3. 测试AnalogyReasoning属性
        analogy_reasoning = AnalogyReasoning(
            analogies=[{"source": "A", "target": "B"}, {"source": "C", "target": "D"}],
            reasoning_chains=[["step1", "step2"], ["step3", "step4", "step5"]],
            confidence_scores=[0.8, 0.9],
        )

        analogy_count = len(analogy_reasoning.analogies)
        chain_count = len(analogy_reasoning.reasoning_chains)
        avg_confidence = sum(analogy_reasoning.confidence_scores) / len(
            analogy_reasoning.confidence_scores
        )

        print("✅ AnalogyReasoning属性访问正确:")
        print(f"   - 类比数量: {analogy_count}")
        print(f"   - 推理链数: {chain_count}")
        print(f"   - 平均置信度: {avg_confidence}")

        # 4. 测试AdaptedContent属性
        adapted_content = AdaptedContent(
            content="这是适配后的内容，经过了认知负荷和个性化调整。",
            adaptation_strategy="cognitive_load_reduction",
            cognitive_load=0.6,
            information_density="medium",
            structure_type="hierarchical",
            personalization_level=0.7,
        )

        content_preview = (
            adapted_content.content[:50] + "..."
            if len(adapted_content.content) > 50
            else adapted_content.content
        )
        strategy = adapted_content.adaptation_strategy
        cog_load = adapted_content.cognitive_load
        info_density = adapted_content.information_density
        personalization = adapted_content.personalization_level

        print("✅ AdaptedContent属性访问正确:")
        print(f"   - 生成内容: {content_preview}")
        print(f"   - 适配策略: {strategy}")
        print(f"   - 认知负荷: {cog_load}")
        print(f"   - 信息密度: {info_density}")
        print(f"   - 个性化程度: {personalization}")

        # 5. 测试PerspectiveGeneration属性
        perspective_generation = PerspectiveGeneration(
            perspectives=[
                {"type": "analytical", "content": "分析视角"},
                {"type": "creative", "content": "创意视角"},
                {"type": "critical", "content": "批判视角"},
            ],
            perspective_diversity=0.8,
            generation_metadata={"method": "dialectical", "time": "2024-01-01"},
        )

        perspective_count = len(perspective_generation.perspectives)
        diversity = perspective_generation.perspective_diversity
        metadata_count = len(perspective_generation.generation_metadata)

        print("✅ PerspectiveGeneration属性访问正确:")
        print(f"   - 生成视角数: {perspective_count}")
        print(f"   - 视角多样性: {diversity}")
        print(f"   - 生成元数据项: {metadata_count}")

        # 6. 测试CognitiveChallenge属性
        cognitive_challenge = CognitiveChallenge(
            challenges=[
                {"type": "assumption", "content": "质疑假设"},
                {"type": "alternative", "content": "替代方案"},
            ],
            challenge_intensity=0.7,
            educational_value=0.9,
        )

        challenge_count = len(cognitive_challenge.challenges)
        intensity = cognitive_challenge.challenge_intensity
        edu_value = cognitive_challenge.educational_value

        print("✅ CognitiveChallenge属性访问正确:")
        print(f"   - 挑战数量: {challenge_count}")
        print(f"   - 挑战强度: {intensity}")
        print(f"   - 教育价值: {edu_value}")

        print("\n🎉 所有Gradio界面属性访问测试通过！")
        print("修复后的属性名称与layer_interfaces.py中的定义完全匹配。")

        return True

    except Exception as e:
        print(f"❌ 属性访问测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_layer_output_construction():
    """测试层输出对象的构造"""
    print("\n🔧 测试层输出对象构造...")

    try:
        # 构造CognitionOutput
        cognition_output = CognitionOutput(
            layer_name="cognition",
            status=ProcessingStatus.COMPLETED,
            data={"test": "data"},
            metadata={"processing_time": 1.5},
            timestamp=datetime.now().isoformat(),
            processing_time=1.5,
            memory_activation=MemoryActivation(
                activated_fragments=["frag1", "frag2"],
                activation_confidence=0.8,
                activation_metadata={"test": "meta"},
            ),
            semantic_enhancement=SemanticEnhancement(
                enhanced_content=["enhanced1"],
                semantic_gaps_filled=["gap1"],
                enhancement_confidence=0.7,
            ),
            analogy_reasoning=AnalogyReasoning(
                analogies=[{"source": "A", "target": "B"}],
                reasoning_chains=[["step1", "step2"]],
                confidence_scores=[0.85],
            ),
        )

        print("✅ CognitionOutput构造成功")

        # 构造BehaviorOutput
        behavior_output = BehaviorOutput(
            layer_name="behavior",
            status=ProcessingStatus.COMPLETED,
            data={"test": "data"},
            adapted_content=AdaptedContent(
                content="测试内容",
                adaptation_strategy="test_strategy",
                cognitive_load=0.5,
                information_density="medium",
                structure_type="linear",
                personalization_level=0.6,
            ),
            generation_metadata={"method": "llm"},
            quality_metrics={"fluency": 0.9, "relevance": 0.8},
        )

        print("✅ BehaviorOutput构造成功")

        # 构造CollaborationOutput
        collaboration_output = CollaborationOutput(
            layer_name="collaboration",
            status=ProcessingStatus.COMPLETED,
            data={"test": "data"},
            perspective_generation=PerspectiveGeneration(
                perspectives=[{"type": "test", "content": "test"}],
                perspective_diversity=0.5,
                generation_metadata={"test": "meta"},
            ),
            cognitive_challenge=CognitiveChallenge(
                challenges=[{"type": "test", "content": "challenge"}],
                challenge_intensity=0.6,
                educational_value=0.8,
            ),
            enhanced_content="协作增强内容",
        )

        print("✅ CollaborationOutput构造成功")
        print("✅ 所有层输出对象构造测试通过！")

        return True

    except Exception as e:
        print(f"❌ 层输出构造测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 开始测试Gradio界面属性修复...")

    success1 = test_gradio_attribute_access()
    success2 = test_layer_output_construction()

    if success1 and success2:
        print("\n🎉 所有测试通过！Gradio界面属性修复成功。")
        print("现在Gradio界面应该能够正确访问各层输出的属性了。")
    else:
        print("\n❌ 部分测试失败，需要进一步调试。")
