#!/usr/bin/env python3
"""
AiEnhance Gradio界面
提供分层认知系统的可视化交互界面，展示各层处理过程和MIRIX记忆系统
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Any

import gradio as gr
import plotly.graph_objects as go

# 导入项目模块
from aienhance.core.layered_cognitive_system import LayeredCognitiveSystem
from aienhance.enhanced_system_factory import (
    create_creative_layered_system,
    create_educational_layered_system,
    create_layered_system,
    create_lightweight_layered_system,
    create_research_layered_system,
)
from aienhance.memory.interfaces import MemoryQuery, create_user_context

# MIRIX前端集成功能已简化，移除复杂依赖

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayeredSystemVisualizer:
    """分层认知系统可视化器"""

    def __init__(self):
        self.system: LayeredCognitiveSystem | None = None
        self.current_system_type = "educational"
        self.user_context = create_user_context("gradio_user", "gradio_session")

    async def initialize_system(self, system_type: str, llm_provider: str = "ollama",
                              llm_model: str = "qwen3:8b", temperature: float = 0.7) -> str:
        """初始化分层认知系统"""
        try:
            logger.info(f"初始化 {system_type} 系统...")

            # 创建系统配置
            config = {
                "system_type": system_type,
                "llm_provider": llm_provider,
                "llm_model_name": llm_model,
                "llm_temperature": temperature,
                "use_unified_llm": True,
                "memory_system_type": "mirix_unified"
            }

            # 根据系统类型创建对应的系统
            if system_type == "educational":
                self.system = create_educational_layered_system(**config)
            elif system_type == "research":
                self.system = create_research_layered_system(**config)
            elif system_type == "creative":
                self.system = create_creative_layered_system(**config)
            elif system_type == "lightweight":
                self.system = create_lightweight_layered_system(**config)
            else:
                self.system = create_layered_system(**config)

            # 初始化系统
            await self.system.initialize_layers()

            self.current_system_type = system_type

            return f"✅ {system_type} 系统初始化成功！\n系统信息：\n{json.dumps(self.system.get_system_info(), ensure_ascii=False, indent=2)}"

        except Exception as e:
            error_msg = f"❌ 系统初始化失败: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return error_msg

    async def process_query_with_layers(self, query: str) -> tuple[str, dict[str, Any]]:
        """处理查询并返回各层的详细输出"""
        if not self.system:
            return "❌ 系统未初始化，请先初始化系统", {}

        try:
            logger.info(f"处理查询: {query}")

            # 存储各层输出
            layer_outputs = {
                "perception": {},
                "cognition": {},
                "behavior": {},
                "collaboration": {}
            }

            # 1. 感知层处理
            logger.info("🔍 感知层处理中...")
            from aienhance.core.layer_interfaces import PerceptionInput

            perception_input = PerceptionInput(
                query=query,
                user_id=self.user_context.user_id,
                context={"session_id": self.user_context.session_id},
                historical_data=None
            )

            perception_result = await self.system.perception_layer.process(perception_input)

            layer_outputs["perception"] = {
                "输入查询": query,
                "处理状态": perception_result.status.value,
                "用户画像": {
                    "用户ID": perception_result.user_profile.user_id if perception_result.user_profile else "未知",
                    "认知特征": perception_result.user_profile.cognitive_characteristics if perception_result.user_profile else {},
                    "知识画像": perception_result.user_profile.knowledge_profile if perception_result.user_profile else {}
                } if perception_result.user_profile else {},
                "情境分析": {
                    "任务类型": perception_result.context_profile.task_type if perception_result.context_profile else "未知",
                    "复杂度": perception_result.context_profile.complexity_level if perception_result.context_profile else 0,
                    "领域特征": perception_result.context_profile.domain_characteristics if perception_result.context_profile else {}
                } if perception_result.context_profile else {},
                "感知洞察": perception_result.perception_insights,
                "处理时间": perception_result.processing_time
            }

            # 2. 认知层处理
            logger.info("🧠 认知层处理中...")
            from aienhance.core.layer_interfaces import CognitionInput

            cognition_input = CognitionInput(
                query=query,
                user_profile=perception_result.user_profile,
                context_profile=perception_result.context_profile,
                external_memories=[],
                perception_insights=perception_result.perception_insights
            )

            cognition_result = await self.system.cognition_layer.process(cognition_input)

            layer_outputs["cognition"] = {
                "处理状态": cognition_result.status.value,
                "记忆激活": {
                    "激活记忆数": len(cognition_result.memory_activation.activated_fragments) if cognition_result.memory_activation else 0,
                    "激活置信度": cognition_result.memory_activation.activation_confidence if cognition_result.memory_activation else 0,
                    "激活元数据": len(cognition_result.memory_activation.activation_metadata) if cognition_result.memory_activation else 0
                } if hasattr(cognition_result, 'memory_activation') and cognition_result.memory_activation else {},
                "语义增强": {
                    "增强内容数": len(cognition_result.semantic_enhancement.enhanced_content) if hasattr(cognition_result, 'semantic_enhancement') and cognition_result.semantic_enhancement else 0,
                    "语义补全数": len(cognition_result.semantic_enhancement.semantic_gaps_filled) if hasattr(cognition_result, 'semantic_enhancement') and cognition_result.semantic_enhancement else 0,
                    "增强置信度": cognition_result.semantic_enhancement.enhancement_confidence if hasattr(cognition_result, 'semantic_enhancement') and cognition_result.semantic_enhancement else 0
                } if hasattr(cognition_result, 'semantic_enhancement') and cognition_result.semantic_enhancement else {},
                "类比推理": {
                    "类比数量": len(cognition_result.analogy_reasoning.analogies) if hasattr(cognition_result, 'analogy_reasoning') and cognition_result.analogy_reasoning else 0,
                    "推理链数": len(cognition_result.analogy_reasoning.reasoning_chains) if hasattr(cognition_result, 'analogy_reasoning') and cognition_result.analogy_reasoning else 0,
                    "平均置信度": sum(cognition_result.analogy_reasoning.confidence_scores) / len(cognition_result.analogy_reasoning.confidence_scores) if hasattr(cognition_result, 'analogy_reasoning') and cognition_result.analogy_reasoning and cognition_result.analogy_reasoning.confidence_scores else 0
                } if hasattr(cognition_result, 'analogy_reasoning') and cognition_result.analogy_reasoning else {},
                "处理时间": cognition_result.processing_time
            }

            # 3. 行为层处理
            logger.info("🎯 行为层处理中...")
            from aienhance.core.layer_interfaces import BehaviorInput

            behavior_input = BehaviorInput(
                query=query,
                user_profile=perception_result.user_profile,
                context_profile=perception_result.context_profile,
                cognition_output=cognition_result,
                generation_requirements={"format": "text", "style": "informative"}
            )

            behavior_result = await self.system.behavior_layer.process(behavior_input)

            layer_outputs["behavior"] = {
                "处理状态": behavior_result.status.value,
                "响应生成": {
                    "生成内容": behavior_result.adapted_content.content[:200] + "..." if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content and len(behavior_result.adapted_content.content) > 200 else (behavior_result.adapted_content.content if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else ""),
                    "适配策略": behavior_result.adapted_content.adaptation_strategy if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else "默认",
                    "认知负荷": behavior_result.adapted_content.cognitive_load if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else 0,
                    "信息密度": behavior_result.adapted_content.information_density if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else "中等",
                    "个性化程度": behavior_result.adapted_content.personalization_level if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else 0
                } if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content else {},
                "生成元数据": behavior_result.generation_metadata if hasattr(behavior_result, 'generation_metadata') else {},
                "质量指标": behavior_result.quality_metrics if hasattr(behavior_result, 'quality_metrics') else {},
                "处理时间": behavior_result.processing_time
            }

            # 4. 协作层处理（如果启用）
            if hasattr(self.system, 'collaboration_layer') and self.system.collaboration_layer:
                logger.info("🤝 协作层处理中...")
                from aienhance.core.layer_interfaces import CollaborationInput

                collaboration_input = CollaborationInput(
                    query=query,
                    user_profile=perception_result.user_profile,
                    context_profile=perception_result.context_profile,
                    behavior_output=behavior_result,
                    collaboration_context={"mode": "enhancement", "perspectives": ["analytical", "creative"]}
                )

                collaboration_result = await self.system.collaboration_layer.process(collaboration_input)

                layer_outputs["collaboration"] = {
                    "处理状态": collaboration_result.status.value,
                    "多角度分析": {
                        "生成视角数": len(collaboration_result.perspective_generation.perspectives) if hasattr(collaboration_result, 'perspective_generation') and collaboration_result.perspective_generation else 0,
                        "视角多样性": collaboration_result.perspective_generation.perspective_diversity if hasattr(collaboration_result, 'perspective_generation') and collaboration_result.perspective_generation else 0,
                        "生成元数据": len(collaboration_result.perspective_generation.generation_metadata) if hasattr(collaboration_result, 'perspective_generation') and collaboration_result.perspective_generation else 0
                    } if hasattr(collaboration_result, 'perspective_generation') and collaboration_result.perspective_generation else {},
                    "认知挑战": {
                        "挑战数量": len(collaboration_result.cognitive_challenge.challenges) if hasattr(collaboration_result, 'cognitive_challenge') and collaboration_result.cognitive_challenge else 0,
                        "挑战强度": collaboration_result.cognitive_challenge.challenge_intensity if hasattr(collaboration_result, 'cognitive_challenge') and collaboration_result.cognitive_challenge else 0,
                        "教育价值": collaboration_result.cognitive_challenge.educational_value if hasattr(collaboration_result, 'cognitive_challenge') and collaboration_result.cognitive_challenge else 0
                    } if hasattr(collaboration_result, 'cognitive_challenge') and collaboration_result.cognitive_challenge else {},
                    "协作增强": collaboration_result.enhanced_content[:200] + "..." if hasattr(collaboration_result, 'enhanced_content') and collaboration_result.enhanced_content and len(collaboration_result.enhanced_content) > 200 else (collaboration_result.enhanced_content if hasattr(collaboration_result, 'enhanced_content') else ""),
                    "处理时间": collaboration_result.processing_time
                }
            else:
                layer_outputs["collaboration"] = {"状态": "协作层未启用或不可用"}

            # 获取最终响应
            if hasattr(behavior_result, 'adapted_content') and behavior_result.adapted_content:
                final_response = behavior_result.adapted_content.content
            else:
                final_response = "处理完成，但无法获取生成内容"

            return final_response, layer_outputs

        except Exception as e:
            error_msg = f"❌ 查询处理失败: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            return error_msg, {}

    async def get_memory_status(self) -> dict[str, Any]:
        """获取MIRIX记忆系统状态"""
        if not self.system or not self.system.memory_system:
            return {"状态": "记忆系统未初始化"}

        try:
            # 获取系统信息
            system_info = self.system.memory_system.get_system_info()

            # 获取用户记忆统计
            user_memories = await self.system.memory_system.get_user_memories(
                self.user_context, limit=100
            )

            # 按记忆类型分组统计
            memory_stats = {}
            for memory in user_memories.memories:
                mem_type = memory.memory_type.value
                if mem_type not in memory_stats:
                    memory_stats[mem_type] = 0
                memory_stats[mem_type] += 1

            return {
                "系统类型": system_info.get("system_type", "unknown"),
                "初始化状态": system_info.get("initialized", False),
                "LLM模式": system_info.get("mode", "unknown"),
                "LLM提供商": system_info.get("llm_provider", {}),
                "记忆总数": user_memories.total_count,
                "记忆类型统计": memory_stats,
                "查询时间": f"{user_memories.query_time:.3f}秒",
                "支持的功能": system_info.get("features", {})
            }

        except Exception as e:
            return {"错误": f"获取记忆状态失败: {str(e)}"}


# 全局可视化器实例
visualizer = LayeredSystemVisualizer()


def sync_initialize_system(system_type: str, llm_provider: str, llm_model: str, temperature: float) -> str:
    """同步包装器用于初始化系统"""
    return asyncio.run(visualizer.initialize_system(system_type, llm_provider, llm_model, temperature))


def sync_process_query_stream(query: str):
    """流式处理查询的生成器 - 新的默认处理方式"""
    if not query.strip():
        yield "❌ 请输入查询问题"
        return

    try:
        # 使用异步生成器进行流式处理
        async def _process():
            if not visualizer.system:
                yield "❌ 系统未初始化，请先初始化系统"
                return

            layer_info = {
                "perception": "",
                "cognition": "",
                "behavior": "",
                "collaboration": ""
            }

            content_parts = []
            current_layer = ""

            async for chunk in visualizer.system.process_stream(
                query=query,
                user_id="gradio_user",
                context={"source": "gradio", "timestamp": datetime.now().isoformat()}
            ):
                # 识别当前处理层
                if "感知层" in chunk:
                    current_layer = "perception"
                    layer_info[current_layer] += chunk
                elif "认知层" in chunk:
                    current_layer = "cognition"
                    layer_info[current_layer] += chunk
                elif "行为层" in chunk:
                    current_layer = "behavior"
                    layer_info[current_layer] += chunk
                elif "协作层" in chunk:
                    current_layer = "collaboration"
                    layer_info[current_layer] += chunk
                elif chunk.startswith(("🚀", "✅", "❌", "⚠️", "🎯")):
                    # 系统状态信息
                    if current_layer:
                        layer_info[current_layer] += chunk
                    yield chunk
                else:
                    # AI生成的内容
                    content_parts.append(chunk)
                    yield chunk

            # 处理完成后返回层级信息
            yield "\n\n📊 **处理层级信息:**\n"
            for layer, info in layer_info.items():
                if info:
                    yield f"\n**{layer.title()}层:** {info.strip()}\n"

            yield f"\n📈 **流式输出统计:** 总计{len(''.join(content_parts))}字符\n"

        # 运行异步生成器
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _process()
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    except Exception as e:
        yield f"❌ 流式处理异常: {str(e)}"


def sync_process_query(query: str) -> tuple[str, str, str, str, str, str]:
    """同步包装器用于处理查询 - 保持向后兼容"""
    if not query.strip():
        return "❌ 请输入查询问题", "", "", "", "", ""

    try:
        # 收集流式输出作为最终响应
        final_response = ""
        for chunk in sync_process_query_stream(query):
            final_response += chunk

        # 简化的层级输出（流式模式下层级信息已包含在响应中）
        layer_status = {
            "perception": {"状态": "✅ 已完成流式处理"},
            "cognition": {"状态": "✅ 已完成流式处理"},
            "behavior": {"状态": "✅ 已完成流式处理"},
            "collaboration": {"状态": "✅ 已完成流式处理"}
        }

        perception_output = json.dumps(layer_status["perception"], ensure_ascii=False, indent=2)
        cognition_output = json.dumps(layer_status["cognition"], ensure_ascii=False, indent=2)
        behavior_output = json.dumps(layer_status["behavior"], ensure_ascii=False, indent=2)
        collaboration_output = json.dumps(layer_status["collaboration"], ensure_ascii=False, indent=2)

        return final_response, perception_output, cognition_output, behavior_output, collaboration_output, "✅ 流式处理完成"

    except Exception as e:
        error_msg = f"❌ 查询处理异常: {str(e)}"
        return error_msg, "", "", "", "", error_msg


def sync_get_memory_status() -> str:
    """同步包装器用于获取记忆状态"""
    try:
        memory_status = asyncio.run(visualizer.get_memory_status())
        return json.dumps(memory_status, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ 获取记忆状态失败: {str(e)}"


def create_gradio_interface():
    """创建Gradio界面"""

    with gr.Blocks(
        title="AiEnhance - 分层认知系统可视化界面",
        theme=gr.themes.Soft(),
        css="""
        .layer-output {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            background-color: #f9f9f9;
        }
        .memory-panel {
            border: 1px solid #007acc;
            border-radius: 8px;
            padding: 12px;
            background-color: #f0f8ff;
        }
        """
    ) as interface:

        gr.Markdown("# 🧠 AiEnhance - 分层认知系统可视化界面")
        gr.Markdown("探索感知层→认知层→行为层→协作层的完整处理流程，并可视化MIRIX记忆系统")

        with gr.Tab("🎛️ 系统配置"):
            gr.Markdown("## 系统初始化配置")

            with gr.Row():
                with gr.Column(scale=1):
                    system_type = gr.Dropdown(
                        choices=["educational", "research", "creative", "lightweight"],
                        value="educational",
                        label="🎯 系统类型",
                        info="选择适合的认知系统类型"
                    )

                    llm_provider = gr.Dropdown(
                        choices=["ollama", "openai", "anthropic", "google_ai"],
                        value="ollama",
                        label="🤖 LLM提供商",
                        info="选择大语言模型提供商"
                    )

                with gr.Column(scale=1):
                    llm_model = gr.Textbox(
                        value="qwen3:8b",
                        label="📦 模型名称",
                        info="输入具体的模型名称"
                    )

                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.1,
                        label="🌡️ 温度参数",
                        info="控制输出的随机性"
                    )

            with gr.Row():
                init_btn = gr.Button("🚀 初始化系统", variant="primary", size="lg")

            init_status = gr.Textbox(
                label="📊 初始化状态",
                lines=10,
                max_lines=20,
                interactive=False
            )

        with gr.Tab("💬 分层处理可视化"):
            gr.Markdown("## 查询处理和分层输出展示")

            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="❓ 输入查询问题",
                        placeholder="例如：什么是人工智能？请解释深度学习的原理。",
                        lines=3
                    )

                    with gr.Row():
                        process_btn = gr.Button("🔄 开始处理", variant="primary", size="lg")
                        stream_toggle = gr.Checkbox(
                            label="⚡ 流式输出",
                            value=True,
                            info="默认启用流式输出以获得更好体验"
                        )

                    process_status = gr.Textbox(
                        label="⚡ 处理状态",
                        lines=2,
                        interactive=False
                    )

            with gr.Row():
                final_response = gr.Textbox(
                    label="💡 实时响应（流式输出）",
                    lines=8,
                    max_lines=15,
                    interactive=False,
                    info="AI回答将在此处实时显示"
                )

            with gr.Row():
                with gr.Column(scale=1):
                    perception_output = gr.Code(
                        label="🔍 感知层输出",
                        language="json",
                        lines=12
                    )

                with gr.Column(scale=1):
                    cognition_output = gr.Code(
                        label="🧠 认知层输出",
                        language="json",
                        lines=12
                    )

            with gr.Row():
                with gr.Column(scale=1):
                    behavior_output = gr.Code(
                        label="🎯 行为层输出",
                        language="json",
                        lines=12
                    )

                with gr.Column(scale=1):
                    collaboration_output = gr.Code(
                        label="🤝 协作层输出",
                        language="json",
                        lines=12
                    )

        with gr.Tab("🧠 MIRIX记忆系统"):
            gr.Markdown("## MIRIX记忆系统状态和可视化")

            with gr.Row():
                with gr.Column(scale=1):
                    refresh_memory_btn = gr.Button("🔄 刷新记忆状态", variant="secondary")
                    dashboard_btn = gr.Button("📊 生成记忆仪表板", variant="primary")

                with gr.Column(scale=1):
                    search_query = gr.Textbox(
                        label="🔍 搜索记忆",
                        placeholder="输入关键词搜索相关记忆..."
                    )
                    search_btn = gr.Button("🔎 搜索", variant="secondary")

            with gr.Row():
                with gr.Column(scale=1):
                    memory_status = gr.Code(
                        label="📊 记忆系统状态",
                        language="json",
                        lines=15
                    )

                with gr.Column(scale=1):
                    search_results = gr.Code(
                        label="🔍 搜索结果",
                        language="json",
                        lines=15
                    )

            with gr.Tab("📈 记忆分析图表"):
                gr.Markdown("### 记忆类型分布")
                memory_type_plot = gr.Plot(label="记忆类型分布图")

                gr.Markdown("### 记忆时间线")
                memory_timeline_plot = gr.Plot(label="记忆创建时间线")

                gr.Markdown("### 置信度分析")
                memory_confidence_plot = gr.Plot(label="记忆置信度分析")

                gr.Markdown("### 记忆关系网络")
                memory_network_plot = gr.Plot(label="记忆关系网络图")

            with gr.Tab("🌐 MIRIX Web界面"):
                gr.Markdown("### MIRIX原生Web界面集成")

                with gr.Row():
                    mirix_url = gr.Textbox(
                        value="http://localhost:3000",
                        label="🌐 MIRIX Web界面URL",
                        info="请确保MIRIX服务已启动"
                    )
                    load_iframe_btn = gr.Button("🚀 加载MIRIX界面", variant="primary")

                mirix_iframe = gr.HTML(
                    label="MIRIX Web界面",
                    value="<p>点击上方按钮加载MIRIX界面</p>"
                )

                gr.Markdown("### 💡 MIRIX前端集成说明")
                gr.Markdown("""
                **集成MIRIX项目前端的步骤:**
                
                1. **安装MIRIX SDK**: `pip install mirix`
                2. **启动MIRIX服务**: 根据MIRIX文档启动后端服务
                3. **启动Web界面**: 通常运行 `mirix serve` 或访问管理界面
                4. **配置URL**: 在上方输入框中设置正确的MIRIX Web界面地址
                
                **当前状态**: 使用MIRIX统一适配器，支持项目的LLM抽象层
                
                **支持的功能:**
                - ✅ 记忆类型可视化分析
                - ✅ 时间线图表
                - ✅ 置信度分析
                - ✅ 记忆搜索功能
                - ✅ 原生Web界面嵌入
                """)

        with gr.Tab("📊 系统监控"):
            gr.Markdown("## 系统性能和状态监控")

            with gr.Row():
                monitor_btn = gr.Button("📈 获取系统状态", variant="secondary")

            system_monitor = gr.Code(
                label="🔍 系统监控信息",
                language="json",
                lines=10
            )

        # 绑定事件处理器
        init_btn.click(
            fn=sync_initialize_system,
            inputs=[system_type, llm_provider, llm_model, temperature],
            outputs=init_status
        )

        # 定义处理函数选择器
        def process_query_handler(query: str, use_stream: bool):
            """根据用户选择使用流式或传统处理"""
            if use_stream:
                # 流式处理 - 返回生成器的完整结果
                full_response = ""
                for chunk in sync_process_query_stream(query):
                    full_response += chunk

                # 简化的层级状态
                simple_status = {"状态": "✅ 流式处理完成"}
                status_json = json.dumps(simple_status, ensure_ascii=False, indent=2)

                return (
                    full_response,
                    status_json,  # perception
                    status_json,  # cognition
                    status_json,  # behavior
                    status_json,  # collaboration
                    "✅ 流式处理完成"
                )
            else:
                # 传统处理
                return sync_process_query(query)

        process_btn.click(
            fn=process_query_handler,
            inputs=[query_input, stream_toggle],
            outputs=[final_response, perception_output, cognition_output,
                    behavior_output, collaboration_output, process_status]
        )

        refresh_memory_btn.click(
            fn=sync_get_memory_status,
            outputs=memory_status
        )

        # 记忆搜索功能
        def sync_search_memories(query: str) -> str:
            if not query.strip():
                return "请输入搜索关键词"

            try:
                if visualizer.system and visualizer.system.memory_system:
                    # 简化的记忆搜索实现
                    user_context = create_user_context("gradio_user", "search_session")
                    search_query = MemoryQuery(
                        query=query,
                        limit=10,
                        memory_types=None
                    )
                    results = asyncio.run(visualizer.system.memory_system.search_memories(
                        user_context, search_query
                    ))

                    if results.memories:
                        summary = f"找到 {len(results.memories)} 个相关记忆:\n\n"
                        for i, memory in enumerate(results.memories[:5], 1):
                            summary += f"{i}. {memory.content[:100]}...\n"
                        return summary
                    else:
                        return "未找到相关记忆"
                else:
                    return "记忆系统未初始化"
            except Exception as e:
                return f"搜索失败: {str(e)}"

        search_btn.click(
            fn=sync_search_memories,
            inputs=search_query,
            outputs=search_results
        )

        # 记忆仪表板生成
        def sync_generate_dashboard() -> tuple[go.Figure, go.Figure, go.Figure, go.Figure]:
            try:
                if visualizer.system and visualizer.system.memory_system:
                    # 简化的仪表板生成
                    user_context = create_user_context("gradio_user", "dashboard_session")
                    memories = asyncio.run(visualizer.system.memory_system.get_user_memories(
                        user_context, limit=100
                    ))

                    # 创建简单的统计图表
                    # 记忆类型分布图
                    type_counts = {}
                    for memory in memories.memories:
                        mem_type = memory.memory_type.value
                        type_counts[mem_type] = type_counts.get(mem_type, 0) + 1

                    type_fig = go.Figure(data=[go.Pie(
                        labels=list(type_counts.keys()),
                        values=list(type_counts.values()),
                        title="记忆类型分布"
                    )])

                    # 简单的时间线图
                    timeline_fig = go.Figure()
                    timeline_fig.add_trace(go.Scatter(
                        x=list(range(len(memories.memories))),
                        y=[1] * len(memories.memories),
                        mode='markers',
                        name='记忆创建时间线'
                    ))
                    timeline_fig.update_layout(title="记忆时间线")

                    # 置信度分析
                    confidences = [memory.confidence for memory in memories.memories if hasattr(memory, 'confidence')]
                    conf_fig = go.Figure(data=[go.Histogram(x=confidences, title="置信度分布")])

                    # 简单的网络图（占位）
                    network_fig = go.Figure()
                    network_fig.add_annotation(
                        text="记忆关系网络图（开发中）",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )

                    return type_fig, timeline_fig, conf_fig, network_fig
                else:
                    empty_fig = go.Figure()
                    empty_fig.add_annotation(
                        text="记忆系统未初始化",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                    return empty_fig, empty_fig, empty_fig, empty_fig

            except Exception as e:
                error_fig = go.Figure()
                error_fig.add_annotation(
                    text=f"生成图表失败: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return error_fig, error_fig, error_fig, error_fig

        dashboard_btn.click(
            fn=sync_generate_dashboard,
            outputs=[memory_type_plot, memory_timeline_plot, memory_confidence_plot, memory_network_plot]
        )

        # MIRIX Web界面加载
        def load_mirix_iframe(url: str) -> str:
            if not url.strip():
                return "<p>请输入有效的MIRIX Web界面URL</p>"

            iframe_html = f"""
            <iframe 
                src="{url}"
                width="100%" 
                height="600px"
                frameborder="0"
                style="border-radius: 8px; border: 1px solid #ddd;"
                sandbox="allow-scripts allow-same-origin allow-forms"
            >
                <p>无法加载MIRIX界面。请确保:</p>
                <ul>
                    <li>MIRIX服务正在运行</li>
                    <li>URL地址正确: <a href="{url}" target="_blank">{url}</a></li>
                    <li>网络连接正常</li>
                </ul>
            </iframe>
            """
            return iframe_html

        load_iframe_btn.click(
            fn=load_mirix_iframe,
            inputs=mirix_url,
            outputs=mirix_iframe
        )

        # 监控按钮处理
        def get_system_monitor():
            try:
                if visualizer.system:
                    info = visualizer.system.get_system_info()
                    return json.dumps(info, ensure_ascii=False, indent=2)
                else:
                    return "系统未初始化"
            except Exception as e:
                return f"获取系统信息失败: {str(e)}"

        monitor_btn.click(
            fn=get_system_monitor,
            outputs=system_monitor
        )

        # 示例查询按钮
        with gr.Row():
            example_queries = [
                "什么是人工智能？请给出详细解释。",
                "深度学习和机器学习有什么区别？",
                "如何设计一个推荐系统？",
                "请解释注意力机制的工作原理。"
            ]

            for i, example in enumerate(example_queries):
                btn = gr.Button(f"示例 {i+1}", variant="secondary", size="sm")
                btn.click(lambda x=example: x, outputs=query_input)

    return interface


def main():
    """主函数"""
    logger.info("启动 AiEnhance Gradio 界面...")

    # 创建界面
    interface = create_gradio_interface()

    # 启动服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
