#!/usr/bin/env python3
"""
MIRIX前端集成模块
提供MIRIX记忆系统的Web界面集成和可视化组件
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from aienhance.memory.interfaces import MemoryType, MemoryQuery, create_user_context

logger = logging.getLogger(__name__)


class MirixFrontendIntegrator:
    """MIRIX前端集成器"""
    
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.user_context = create_user_context("frontend_user", "frontend_session")
    
    async def get_memory_analytics(self) -> Dict[str, Any]:
        """获取记忆系统分析数据"""
        if not self.memory_system:
            return {"error": "记忆系统未初始化"}
        
        try:
            # 获取所有记忆
            all_memories = await self.memory_system.get_user_memories(
                self.user_context, limit=1000
            )
            
            # 按类型统计
            type_stats = {}
            time_stats = {}
            confidence_stats = []
            
            for memory in all_memories.memories:
                # 记忆类型统计
                mem_type = memory.memory_type.value
                type_stats[mem_type] = type_stats.get(mem_type, 0) + 1
                
                # 时间统计（按天）
                day_key = memory.timestamp.strftime("%Y-%m-%d") if memory.timestamp else "Unknown"
                time_stats[day_key] = time_stats.get(day_key, 0) + 1
                
                # 置信度统计
                confidence_stats.append({
                    "type": mem_type,
                    "confidence": memory.confidence,
                    "timestamp": memory.timestamp.isoformat() if memory.timestamp else None
                })
            
            return {
                "total_memories": all_memories.total_count,
                "type_distribution": type_stats,
                "time_distribution": time_stats,
                "confidence_data": confidence_stats,
                "query_time": all_memories.query_time
            }
            
        except Exception as e:
            logger.error(f"获取记忆分析失败: {e}")
            return {"error": f"获取分析失败: {str(e)}"}
    
    def create_memory_type_chart(self, analytics_data: Dict[str, Any]) -> go.Figure:
        """创建记忆类型分布图"""
        type_dist = analytics_data.get("type_distribution", {})
        
        if not type_dist:
            fig = go.Figure()
            fig.add_annotation(
                text="暂无记忆数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=list(type_dist.keys()),
            values=list(type_dist.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='auto',
            marker_colors=px.colors.qualitative.Set3
        )])
        
        fig.update_layout(
            title={
                'text': '记忆类型分布',
                'x': 0.5,
                'xanchor': 'center'
            },
            font=dict(size=12),
            showlegend=True
        )
        
        return fig
    
    def create_memory_timeline_chart(self, analytics_data: Dict[str, Any]) -> go.Figure:
        """创建记忆时间线图"""
        time_dist = analytics_data.get("time_distribution", {})
        
        if not time_dist:
            fig = go.Figure()
            fig.add_annotation(
                text="暂无时间数据",
                xref="paper", yref="paper", 
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # 排序日期
        sorted_dates = sorted(time_dist.keys())
        counts = [time_dist[date] for date in sorted_dates]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=sorted_dates,
                y=counts,
                mode='lines+markers',
                name='记忆数量',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            )
        ])
        
        fig.update_layout(
            title={
                'text': '记忆创建时间线',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='日期',
            yaxis_title='记忆数量',
            font=dict(size=12),
            hovermode='x unified'
        )
        
        return fig
    
    def create_confidence_analysis_chart(self, analytics_data: Dict[str, Any]) -> go.Figure:
        """创建置信度分析图"""
        confidence_data = analytics_data.get("confidence_data", [])
        
        if not confidence_data:
            fig = go.Figure()
            fig.add_annotation(
                text="暂无置信度数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('各类型记忆置信度分布', '置信度直方图'),
            vertical_spacing=0.12
        )
        
        # 按类型分组置信度
        type_confidence = {}
        all_confidences = []
        
        for item in confidence_data:
            mem_type = item["type"]
            confidence = item["confidence"]
            
            if mem_type not in type_confidence:
                type_confidence[mem_type] = []
            type_confidence[mem_type].append(confidence)
            all_confidences.append(confidence)
        
        # 箱线图
        for mem_type, confidences in type_confidence.items():
            fig.add_trace(
                go.Box(
                    y=confidences,
                    name=mem_type,
                    boxpoints='outliers'
                ),
                row=1, col=1
            )
        
        # 直方图
        fig.add_trace(
            go.Histogram(
                x=all_confidences,
                nbinsx=20,
                name='置信度分布',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title={
                'text': '记忆置信度分析',
                'x': 0.5,
                'xanchor': 'center'
            },
            font=dict(size=12),
            height=600
        )
        
        return fig
    
    async def search_memories_with_visualization(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """搜索记忆并返回可视化数据"""
        if not self.memory_system:
            return {"error": "记忆系统未初始化"}
        
        try:
            # 创建搜索查询
            memory_query = MemoryQuery(
                query=query,
                user_context=self.user_context,
                limit=limit,
                similarity_threshold=0.3
            )
            
            # 执行搜索
            search_result = await self.memory_system.search_memories(memory_query)
            
            # 格式化结果
            memories_data = []
            for memory in search_result.memories:
                memories_data.append({
                    "内容": memory.content[:200] + "..." if len(memory.content) > 200 else memory.content,
                    "类型": memory.memory_type.value,
                    "置信度": f"{memory.confidence:.3f}",
                    "时间": memory.timestamp.strftime("%Y-%m-%d %H:%M:%S") if memory.timestamp else "未知",
                    "元数据": json.dumps(memory.metadata or {}, ensure_ascii=False)[:100]
                })
            
            return {
                "search_query": query,
                "total_found": search_result.total_count,
                "query_time": search_result.query_time,
                "memories": memories_data,
                "metadata": search_result.metadata
            }
            
        except Exception as e:
            logger.error(f"搜索记忆失败: {e}")
            return {"error": f"搜索失败: {str(e)}"}
    
    def generate_mirix_iframe_config(self, mirix_base_url: str = "http://localhost:3000") -> str:
        """生成MIRIX前端iframe配置"""
        iframe_html = f"""
        <iframe 
            src="{mirix_base_url}"
            width="100%" 
            height="600px"
            frameborder="0"
            style="border-radius: 8px; border: 1px solid #ddd;"
            sandbox="allow-scripts allow-same-origin allow-forms"
        >
            <p>您的浏览器不支持iframe。请直接访问 <a href="{mirix_base_url}">MIRIX界面</a></p>
        </iframe>
        """
        return iframe_html
    
    def create_memory_network_graph(self, analytics_data: Dict[str, Any]) -> go.Figure:
        """创建记忆关系网络图"""
        # 这是一个概念性实现，实际需要根据MIRIX的关系数据调整
        fig = go.Figure()
        
        # 示例节点和边数据
        node_trace = go.Scatter(
            x=[1, 2, 3, 4, 2.5],
            y=[1, 2, 1, 2, 1.5],
            mode='markers+text',
            marker=dict(
                size=[30, 40, 25, 35, 20],
                color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                line=dict(width=2, color='white')
            ),
            text=['核心记忆', '情节记忆', '语义记忆', '程序记忆', '资源记忆'],
            textposition="middle center",
            hovertemplate='<b>%{text}</b><extra></extra>'
        )
        
        # 添加连接线
        edge_trace = []
        edges = [(0, 4), (1, 4), (2, 4), (3, 4)]  # 连接到中心节点
        
        for edge in edges:
            x0, y0 = node_trace.x[edge[0]], node_trace.y[edge[0]]
            x1, y1 = node_trace.x[edge[1]], node_trace.y[edge[1]]
            
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=1, color='rgba(125, 125, 125, 0.5)'),
                    hoverinfo='none',
                    showlegend=False
                )
            )
        
        fig.add_traces(edge_trace)
        fig.add_trace(node_trace)
        
        fig.update_layout(
            title={
                'text': '记忆关系网络图',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            font=dict(size=12),
            height=400,
            plot_bgcolor='white'
        )
        
        return fig


def create_memory_dashboard_data(memory_system) -> Dict[str, Any]:
    """创建记忆仪表板数据"""
    integrator = MirixFrontendIntegrator(memory_system)
    
    try:
        # 获取分析数据
        analytics = asyncio.run(integrator.get_memory_analytics())
        
        if "error" in analytics:
            return analytics
        
        # 生成图表
        charts = {
            "type_chart": integrator.create_memory_type_chart(analytics),
            "timeline_chart": integrator.create_memory_timeline_chart(analytics),
            "confidence_chart": integrator.create_confidence_analysis_chart(analytics),
            "network_chart": integrator.create_memory_network_graph(analytics)
        }
        
        return {
            "analytics": analytics,
            "charts": charts,
            "iframe_config": integrator.generate_mirix_iframe_config()
        }
        
    except Exception as e:
        logger.error(f"创建仪表板数据失败: {e}")
        return {"error": f"创建仪表板失败: {str(e)}"}


# 用于Gradio集成的辅助函数
def search_memories_for_gradio(memory_system, query: str, limit: int = 20) -> tuple:
    """为Gradio界面搜索记忆"""
    if not memory_system:
        return "记忆系统未初始化", ""
    
    integrator = MirixFrontendIntegrator(memory_system)
    
    try:
        result = asyncio.run(integrator.search_memories_with_visualization(query, limit))
        
        if "error" in result:
            return result["error"], ""
        
        # 创建表格数据
        if result["memories"]:
            import pandas as pd
            df = pd.DataFrame(result["memories"])
            table_html = df.to_html(classes="memory-table", escape=False, index=False)
        else:
            table_html = "<p>未找到相关记忆</p>"
        
        summary = f"""
搜索查询: {result['search_query']}
找到记忆数: {result['total_found']}
查询时间: {result['query_time']:.3f}秒
        """
        
        return summary, table_html
        
    except Exception as e:
        return f"搜索失败: {str(e)}", ""