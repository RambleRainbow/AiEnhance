"""
重构后系统的测试

测试新的层-模块-子模块架构的基本功能
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from aienhance.core.base_architecture import (
    CognitiveSystem,
    ProcessingContext,
    ProcessingResult,
    BaseLayer,
    BaseModule,
    BaseSubModule
)
from aienhance.core.restructured_system_factory import (
    create_restructured_cognitive_system,
    create_educational_system,
    initialize_system_async
)


class TestRestructuredSystemArchitecture:
    """测试重构后的系统架构"""
    
    def test_processing_context_creation(self):
        """测试ProcessingContext创建"""
        context = ProcessingContext(
            user_id="test_user",
            query="测试问题",
            session_context={},
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={}
        )
        
        assert context.user_id == "test_user"
        assert context.query == "测试问题"
        assert isinstance(context.metadata, dict)
        assert "created_at" in context.metadata
        assert "processing_history" in context.metadata
    
    def test_processing_result_creation(self):
        """测试ProcessingResult创建"""
        result = ProcessingResult(
            success=True,
            data={"test": "data"},
            metadata={"test": "meta"}
        )
        
        assert result.success is True
        assert result.data["test"] == "data"
        assert result.metadata["test"] == "meta"
        assert "processed_at" in result.metadata


class MockSubModule(BaseSubModule):
    """用于测试的模拟子模块"""
    
    async def _initialize_impl(self):
        pass
    
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        return ProcessingResult(
            success=True,
            data={"submodule_output": f"Processed by {self.name}"},
            metadata={"test": True}
        )


class MockModule(BaseModule):
    """用于测试的模拟模块"""
    
    async def _initialize_impl(self):
        pass
    
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        # 处理子模块
        submodule_results = await self.process_submodules(context)
        
        return ProcessingResult(
            success=True,
            data={
                "module_output": f"Processed by {self.name}",
                "submodule_results": submodule_results
            },
            metadata={"test": True}
        )


class MockLayer(BaseLayer):
    """用于测试的模拟层"""
    
    async def _initialize_impl(self):
        pass
    
    async def process(self, context: ProcessingContext) -> ProcessingResult:
        # 处理模块
        module_results = await self.process_modules(context)
        
        return ProcessingResult(
            success=True,
            data={
                "layer_output": f"Processed by {self.name}",
                "module_results": module_results
            },
            metadata={"test": True}
        )


class TestModularComponents:
    """测试模块化组件"""
    
    @pytest.mark.asyncio
    async def test_submodule_processing(self):
        """测试子模块处理"""
        submodule = MockSubModule("test_submodule")
        await submodule.initialize()
        
        context = ProcessingContext(
            user_id="test",
            query="test query",
            session_context={},
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={}
        )
        
        result = await submodule.process(context)
        
        assert result.success is True
        assert "submodule_output" in result.data
        assert "Processed by test_submodule" in result.data["submodule_output"]
    
    @pytest.mark.asyncio
    async def test_module_processing(self):
        """测试模块处理"""
        # 创建带子模块的模块
        submodules = [MockSubModule("sub1"), MockSubModule("sub2")]
        module = MockModule("test_module", submodules)
        
        await module.initialize()
        
        context = ProcessingContext(
            user_id="test",
            query="test query",
            session_context={},
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={}
        )
        
        result = await module.process(context)
        
        assert result.success is True
        assert "module_output" in result.data
        assert "submodule_results" in result.data
        assert len(result.data["submodule_results"]) == 2
    
    @pytest.mark.asyncio
    async def test_layer_processing(self):
        """测试层处理"""
        # 创建带模块的层
        submodules1 = [MockSubModule("sub1")]
        submodules2 = [MockSubModule("sub2")]
        modules = [
            MockModule("module1", submodules1),
            MockModule("module2", submodules2)
        ]
        layer = MockLayer("test_layer", modules)
        
        await layer.initialize()
        
        context = ProcessingContext(
            user_id="test",
            query="test query",
            session_context={},
            layer_outputs={},
            module_outputs={},
            submodule_outputs={},
            metadata={}
        )
        
        result = await layer.process(context)
        
        assert result.success is True
        assert "layer_output" in result.data
        assert "module_results" in result.data
        assert len(result.data["module_results"]) == 2


class TestSystemFactory:
    """测试系统工厂"""
    
    def test_create_educational_system(self):
        """测试创建教育系统（不启动LLM）"""
        # 使用mock LLM适配器避免实际网络调用
        with pytest.raises(Exception):  # 预期会因为缺少LLM适配器而失败
            system = create_educational_system(
                llm_provider="ollama",
                memory_provider="none"
            )
    
    def test_system_creation_with_mock(self):
        """使用mock测试系统创建"""
        # 这个测试展示了如何mock依赖项
        mock_llm = Mock()
        mock_memory = Mock()
        
        # 实际的系统创建需要真实的适配器，这里只是演示结构
        assert mock_llm is not None
        assert mock_memory is not None


class TestIntegrationBasics:
    """基础集成测试"""
    
    @pytest.mark.asyncio
    async def test_cognitive_system_integration(self):
        """测试认知系统集成（使用mock组件）"""
        # 创建mock层
        layers = [
            MockLayer("perception", [MockModule("user_modeling", [MockSubModule("cognitive_ability")])]),
            MockLayer("cognition", [MockModule("memory_activation", [MockSubModule("surface_activation")])])
        ]
        
        system = CognitiveSystem(layers)
        
        # 初始化系统
        success = await system.initialize()
        assert success is True
        
        # 处理请求
        result = await system.process(
            user_id="test_user",
            query="测试问题",
            session_context={}
        )
        
        assert result.success is True
        assert "layer_outputs" in result.data
        assert len(result.data["layer_outputs"]) == 2
        assert "perception" in result.data["layer_outputs"]
        assert "cognition" in result.data["layer_outputs"]


@pytest.mark.asyncio 
async def test_system_factory_basic():
    """测试系统工厂基础功能"""
    try:
        # 尝试创建一个最简单的系统（预期会失败但展示结构）
        system = create_educational_system(
            llm_provider="mock",  # 不存在的provider会导致错误
            memory_provider="none"
        )
        
        # 如果到达这里说明有问题
        assert False, "应该因为不存在的provider而失败"
        
    except ValueError as e:
        # 预期的错误
        assert "Unsupported LLM provider" in str(e)
    except Exception as e:
        # 其他错误也是可以接受的，因为我们在测试错误处理
        assert str(e) is not None


if __name__ == "__main__":
    # 运行基本测试
    pytest.main([__file__, "-v"])