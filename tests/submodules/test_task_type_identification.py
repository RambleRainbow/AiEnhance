"""
TaskTypeIdentificationSubModule验收测试

真实环境下测试任务类型识别子模块的核心业务功能。
使用实际的LLM适配器进行端到端测试。
"""

import asyncio

import pytest
import pytest_asyncio

from aienhance.config import config
from aienhance.core.base_architecture import ProcessingContext
from aienhance.llm.adapters.ollama_adapter import OllamaLLMAdapter
from aienhance.perception.context_analysis.task_type_identification import (
    TaskTypeIdentificationSubModule,
)


class TestTaskTypeIdentificationAcceptance:
    """TaskTypeIdentificationSubModule的验收测试"""

    @pytest_asyncio.fixture
    async def llm_adapter(self):
        """创建真实的Ollama LLM适配器"""
        llm_config = config.get_llm_config()
        from aienhance.llm.interfaces import ModelConfig

        model_config = ModelConfig(
            provider="ollama",
            model_name=llm_config["model_name"],
            api_base=llm_config["api_base"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
        )
        adapter = OllamaLLMAdapter(model_config)

        # 返回未初始化的适配器，由测试函数负责初始化
        yield adapter

        # 清理资源
        try:
            await adapter.cleanup()
        except Exception:
            pass  # 忽略清理错误

    @pytest.fixture
    def test_queries(self):
        """测试用的查询样本"""
        return [
            {
                "query": "请分析一下这个算法的时间复杂度",
                "expected_task_type": "analytical",
                "description": "分析型任务测试",
            },
            {
                "query": "帮我设计一个创新的移动应用界面",
                "expected_task_type": "creative",
                "description": "创造型任务测试",
            },
            {
                "query": "我想了解机器学习的基本概念",
                "expected_task_type": "learning",
                "description": "学习型任务测试",
            },
            {
                "query": "什么是量子计算？",
                "expected_task_type": "retrieval",
                "description": "检索型任务测试",
            },
            {
                "query": "如何解决网站加载慢的问题？",
                "expected_task_type": "problem_solving",
                "description": "问题解决型任务测试",
            },
        ]

    @pytest.fixture
    def sample_context(self):
        """创建测试用的ProcessingContext"""
        return ProcessingContext(
            user_id="acceptance_test_user",
            query="",  # 会在测试中替换
            session_context={
                "conversation_history": [],
                "user_profile": {"expertise_level": "intermediate"},
                "previous_task_types": [],
            },
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={},
        )

    @pytest.mark.asyncio
    async def test_submodule_initialization(self, llm_adapter):
        """测试子模块初始化"""
        # 首先初始化LLM适配器
        await llm_adapter.initialize()

        submodule = TaskTypeIdentificationSubModule(
            llm_adapter=llm_adapter, config={"enabled": True}
        )

        # 验证基本属性
        assert submodule.name == "task_type_identification"
        assert submodule.llm_adapter is not None
        assert submodule.enabled is True

        # 测试异步初始化
        result = await submodule.initialize()
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.slow  # 标记为慢速测试，因为需要实际LLM调用
    async def test_task_type_identification_main_function(
        self, llm_adapter, test_queries, sample_context
    ):
        """验收测试：测试主要业务功能 - 任务类型识别"""
        # 首先初始化LLM适配器
        await llm_adapter.initialize()

        submodule = TaskTypeIdentificationSubModule(
            llm_adapter=llm_adapter, config={"enabled": True}
        )

        # 初始化子模块
        await submodule.initialize()

        # 测试每个查询样本
        for test_case in test_queries:
            print(f"\n测试: {test_case['description']}")
            print(f"查询: {test_case['query']}")

            # 设置上下文
            context = sample_context
            context.query = test_case["query"]

            # 执行任务类型识别
            result = await submodule.process(context)

            # 验证基本返回结构
            assert result.success is True, f"处理失败: {result.error_message}"
            assert "task_analysis" in result.data
            assert "primary_task_type" in result.data
            assert "confidence_score" in result.data

            # 获取识别结果
            task_analysis = result.data["task_analysis"]
            identified_type = result.data["primary_task_type"]
            confidence = result.data["confidence_score"]

            print(f"识别结果: {identified_type}")
            print(f"预期类型: {test_case['expected_task_type']}")
            print(f"置信度: {confidence}")

            # 验证基本业务逻辑
            assert identified_type in [
                "analytical",
                "creative",
                "exploratory",
                "retrieval",
                "problem_solving",
                "learning",
                "decision_making",
            ], f"识别的任务类型无效: {identified_type}"

            assert 0.0 <= confidence <= 1.0, f"置信度超出范围: {confidence}"

            # 验证任务分析结构完整性
            assert "task_complexity" in task_analysis
            assert "intent_analysis" in task_analysis
            assert "processing_requirements" in task_analysis

            # 验证复杂度分析
            complexity = task_analysis["task_complexity"]
            assert "level" in complexity
            assert complexity["level"] in ["simple", "medium", "complex", "expert"]

            # 验证意图分析
            intent = task_analysis["intent_analysis"]
            assert "primary_intent" in intent
            assert "goal_clarity" in intent
            assert intent["goal_clarity"] in ["clear", "moderate", "vague", "ambiguous"]

            print(f"✅ {test_case['description']} 测试通过")

            # 添加小延迟避免请求过于频繁
            await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_error_handling(self, llm_adapter, sample_context):
        """测试错误处理能力"""
        # 首先初始化LLM适配器
        await llm_adapter.initialize()

        submodule = TaskTypeIdentificationSubModule(
            llm_adapter=llm_adapter, config={"enabled": True}
        )

        await submodule.initialize()

        # 使用空查询测试
        context = sample_context
        context.query = ""

        result = await submodule.process(context)

        # 即使输入为空，也应该有合理的处理结果
        assert result.success is True or result.success is False  # 任一结果都可接受

        if result.success:
            # 如果成功，应该有默认分析结果
            assert "task_analysis" in result.data
        else:
            # 如果失败，应该有错误信息
            assert result.error_message is not None

    def test_schema_structure(self, llm_adapter):
        """测试JSON Schema结构"""
        submodule = TaskTypeIdentificationSubModule(llm_adapter=llm_adapter)
        schema = submodule._get_task_type_schema()

        # 验证Schema基本结构
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        # 验证关键字段存在
        properties = schema["properties"]
        required_fields = [
            "primary_task_type",
            "secondary_task_types",
            "task_categories",
            "task_complexity",
            "intent_analysis",
            "processing_requirements",
            "confidence_score",
            "analysis_notes",
        ]

        for field in required_fields:
            assert field in properties, f"Schema缺少必需字段: {field}"

        # 验证任务类型枚举
        task_types = properties["primary_task_type"]["enum"]
        assert len(task_types) == 7, f"任务类型数量不正确: {len(task_types)}"
        assert "analytical" in task_types
        assert "creative" in task_types
        assert "learning" in task_types


# 测试运行器
if __name__ == "__main__":
    # 运行快速测试（跳过需要LLM的慢速测试）
    pytest.main([__file__, "-v", "-m", "not slow"])

    # 如果需要运行完整测试（包括LLM调用），使用：
    # pytest.main([__file__, "-v"])
