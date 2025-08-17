"""
辩证视角生成模块
实现对立观点生成、多学科视角切换、交替论证等功能
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
import logging

from .interfaces import (
    PerspectiveGenerator, PerspectiveRequest, PerspectiveResult, 
    Perspective, PerspectiveType, DisciplineCategory, CollaborationContext
)
from ..llm.interfaces import LLMProvider, ChatMessage, MessageRole
from ..memory.interfaces import MemorySystem, MemoryQuery, UserContext, MemoryType

logger = logging.getLogger(__name__)


class DialecticalPerspectiveGenerator(PerspectiveGenerator):
    """
    辩证视角生成器
    
    通过系统化地提供多元视角，培养用户的批判性思维和辩证分析能力
    """
    
    def __init__(self, llm_provider: LLMProvider, memory_system: Optional[MemorySystem] = None):
        self.llm_provider = llm_provider
        self.memory_system = memory_system
        
        # 学科视角库
        self.discipline_frameworks = {
            DisciplineCategory.MATHEMATICS: {
                "keywords": ["抽象", "形式化", "量化", "模型", "证明"],
                "approaches": ["数学建模", "逻辑推理", "量化分析", "形式验证"],
                "questions": ["如何量化这个问题？", "是否存在数学模型？", "逻辑关系是什么？"]
            },
            DisciplineCategory.PHYSICS: {
                "keywords": ["因果", "守恒", "对称", "能量", "系统"],
                "approaches": ["因果分析", "能量守恒", "系统动力学", "对称性分析"],
                "questions": ["遵循什么物理规律？", "能量如何转换？", "存在什么对称性？"]
            },
            DisciplineCategory.PSYCHOLOGY: {
                "keywords": ["认知", "情感", "行为", "动机", "偏见"],
                "approaches": ["认知分析", "情感理解", "行为预测", "动机探索"],
                "questions": ["心理机制是什么？", "存在认知偏见吗？", "情感因素如何影响？"]
            },
            DisciplineCategory.ECONOMICS: {
                "keywords": ["成本", "效益", "激励", "供需", "均衡"],
                "approaches": ["成本效益分析", "激励机制设计", "市场分析", "博弈论"],
                "questions": ["成本效益如何？", "激励机制是否合理？", "市场反应如何？"]
            },
            DisciplineCategory.SOCIOLOGY: {
                "keywords": ["群体", "文化", "制度", "权力", "社会"],
                "approaches": ["社会结构分析", "文化影响评估", "制度分析", "权力关系"],
                "questions": ["社会影响如何？", "文化因素是什么？", "权力结构如何？"]
            },
            DisciplineCategory.PHILOSOPHY: {
                "keywords": ["本质", "价值", "伦理", "意义", "真理"],
                "approaches": ["本质探询", "价值判断", "伦理分析", "意义阐释"],
                "questions": ["本质是什么？", "价值在哪里？", "伦理问题有哪些？"]
            }
        }
        
        # 对立观点生成策略
        self.opposition_strategies = [
            "direct_negation",      # 直接否定
            "premise_challenge",    # 前提挑战  
            "degree_adjustment",    # 程度调整
            "angle_shift",         # 角度转换
            "temporal_shift",      # 时间维度转换
            "context_expansion"    # 情境扩展
        ]
    
    async def generate_perspectives(self, request: PerspectiveRequest, 
                                  context: CollaborationContext) -> PerspectiveResult:
        """生成多元视角"""
        try:
            perspectives = []
            
            # 1. 分析用户内容和立场
            content_analysis = await self._analyze_content(request.content, request.user_position)
            
            # 2. 生成不同类型的视角
            for perspective_type in (request.perspective_types or [PerspectiveType.OPPOSING, PerspectiveType.MULTI_DISCIPLINARY]):
                if perspective_type == PerspectiveType.OPPOSING:
                    opposing_perspectives = await self._generate_opposing_views(request, content_analysis)
                    perspectives.extend(opposing_perspectives)
                    
                elif perspective_type == PerspectiveType.MULTI_DISCIPLINARY:
                    disciplinary_perspectives = await self._generate_disciplinary_views(request, content_analysis)
                    perspectives.extend(disciplinary_perspectives)
                    
                elif perspective_type == PerspectiveType.STAKEHOLDER:
                    stakeholder_perspectives = await self._generate_stakeholder_views(request, content_analysis)
                    perspectives.extend(stakeholder_perspectives)
            
            # 3. 限制视角数量
            if len(perspectives) > request.max_perspectives:
                perspectives = sorted(perspectives, key=lambda p: p.relevance_score, reverse=True)[:request.max_perspectives]
            
            # 4. 生成综合分析和辩证关系
            synthesis = await self._synthesize_perspectives(perspectives)
            dialectical_tensions = await self._identify_dialectical_tensions(perspectives)
            integration_suggestions = await self._generate_integration_suggestions(perspectives)
            
            return PerspectiveResult(
                perspectives=perspectives,
                synthesis=synthesis,
                dialectical_tensions=dialectical_tensions,
                integration_suggestions=integration_suggestions,
                generation_metadata={
                    "content_analysis": content_analysis,
                    "generation_strategies_used": [p.perspective_type.value for p in perspectives],
                    "total_generated": len(perspectives)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate perspectives: {e}")
            raise
    
    async def _analyze_content(self, content: str, user_position: Optional[str] = None) -> Dict[str, Any]:
        """分析内容和用户立场"""
        analysis_prompt = f"""
请分析以下内容的核心观点、关键论据和潜在假设：

内容：{content}

{f"用户立场：{user_position}" if user_position else ""}

请识别：
1. 核心观点和主要立场
2. 支撑论据和证据类型
3. 隐含前提和假设
4. 论证的强度和弱点
5. 涉及的领域和学科

以JSON格式返回分析结果。
"""
        
        messages = [ChatMessage(role=MessageRole.USER, content=analysis_prompt)]
        response = await self.llm_provider.chat(messages)
        
        try:
            # 尝试解析JSON，如果失败则返回基本结构
            import json
            return json.loads(response.content)
        except:
            return {
                "core_viewpoint": content[:200],
                "key_arguments": [content],
                "assumptions": [],
                "domains": ["general"],
                "argument_strength": "moderate"
            }
    
    async def _generate_opposing_views(self, request: PerspectiveRequest, 
                                     content_analysis: Dict[str, Any]) -> List[Perspective]:
        """生成对立观点"""
        opposing_perspectives = []
        
        for strategy in self.opposition_strategies[:2]:  # 限制策略数量
            try:
                perspective = await self._generate_opposing_view_by_strategy(
                    request.content, content_analysis, strategy
                )
                if perspective:
                    opposing_perspectives.append(perspective)
            except Exception as e:
                logger.warning(f"Failed to generate opposing view with strategy {strategy}: {e}")
                continue
        
        return opposing_perspectives
    
    async def _generate_opposing_view_by_strategy(self, content: str, 
                                                content_analysis: Dict[str, Any], 
                                                strategy: str) -> Optional[Perspective]:
        """使用特定策略生成对立观点"""
        strategy_prompts = {
            "direct_negation": f"""
基于以下内容，构建一个直接对立的观点：

原始内容：{content}

请提供：
1. 对立观点的核心立场
2. 支持这个对立立场的3个关键论据  
3. 相关的证据或例子
4. 为什么这个对立观点同样有效

以清晰的结构化格式回答。
""",
            "premise_challenge": f"""
基于以下内容，挑战其核心前提和假设：

原始内容：{content}
核心假设：{content_analysis.get('assumptions', [])}

请：
1. 识别并质疑关键前提
2. 提出替代假设
3. 基于新假设构建不同结论
4. 说明为什么替代假设更合理

以清晰的结构化格式回答。
""",
            "angle_shift": f"""
从完全不同的角度重新审视以下内容：

原始内容：{content}

请从以下角度之一重新分析：
- 长期 vs 短期影响
- 个体 vs 集体利益  
- 理论 vs 实践
- 理想 vs 现实

提供：
1. 新角度的核心洞察
2. 从这个角度看到的不同问题
3. 相应的解决方案或建议

以清晰的结构化格式回答。
"""
        }
        
        prompt = strategy_prompts.get(strategy, strategy_prompts["direct_negation"])
        
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        
        return self._parse_perspective_response(response.content, PerspectiveType.OPPOSING, strategy)
    
    async def _generate_disciplinary_views(self, request: PerspectiveRequest,
                                         content_analysis: Dict[str, Any]) -> List[Perspective]:
        """生成多学科视角"""
        disciplinary_perspectives = []
        
        # 选择相关学科
        disciplines = request.disciplines or [
            DisciplineCategory.PSYCHOLOGY, 
            DisciplineCategory.ECONOMICS,
            DisciplineCategory.PHILOSOPHY
        ]
        
        for discipline in disciplines[:2]:  # 限制学科数量
            try:
                perspective = await self._generate_disciplinary_view(
                    request.content, content_analysis, discipline
                )
                if perspective:
                    disciplinary_perspectives.append(perspective)
            except Exception as e:
                logger.warning(f"Failed to generate {discipline.value} perspective: {e}")
                continue
        
        return disciplinary_perspectives
    
    async def _generate_disciplinary_view(self, content: str,
                                        content_analysis: Dict[str, Any],
                                        discipline: DisciplineCategory) -> Optional[Perspective]:
        """生成特定学科视角"""
        framework = self.discipline_frameworks.get(discipline, {})
        
        prompt = f"""
请从{discipline.value}学科的角度分析以下内容：

内容：{content}

{discipline.value}学科的关键概念：{framework.get('keywords', [])}
分析方法：{framework.get('approaches', [])}
关键问题：{framework.get('questions', [])}

请提供：
1. 从这个学科角度的核心洞察
2. 运用该学科理论的分析
3. 这个学科特有的解决方案
4. 该学科视角揭示的新问题

以清晰的结构化格式回答。
"""
        
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        
        perspective = self._parse_perspective_response(
            response.content, 
            PerspectiveType.MULTI_DISCIPLINARY,
            discipline.value
        )
        
        if perspective:
            perspective.discipline = discipline
            
        return perspective
    
    async def _generate_stakeholder_views(self, request: PerspectiveRequest,
                                        content_analysis: Dict[str, Any]) -> List[Perspective]:
        """生成利益相关者视角"""
        # 识别潜在利益相关者
        stakeholders = await self._identify_stakeholders(request.content)
        
        stakeholder_perspectives = []
        for stakeholder in stakeholders[:2]:  # 限制数量
            try:
                perspective = await self._generate_stakeholder_view(
                    request.content, stakeholder
                )
                if perspective:
                    stakeholder_perspectives.append(perspective)
            except Exception as e:
                logger.warning(f"Failed to generate stakeholder view for {stakeholder}: {e}")
                continue
        
        return stakeholder_perspectives
    
    async def _identify_stakeholders(self, content: str) -> List[str]:
        """识别利益相关者"""
        prompt = f"""
识别以下内容中涉及的主要利益相关者：

内容：{content}

请列出3-5个主要利益相关者群体，如：
- 直接受影响的人群
- 决策制定者
- 实施者
- 监管者
- 其他相关群体

简洁列出即可。
"""
        
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        
        # 简单解析利益相关者列表
        stakeholders = []
        for line in response.content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 2:
                # 清理格式符号
                clean_line = re.sub(r'^[-*•]\s*', '', line)
                if clean_line:
                    stakeholders.append(clean_line)
        
        return stakeholders[:5]  # 最多5个
    
    async def _generate_stakeholder_view(self, content: str, stakeholder: str) -> Optional[Perspective]:
        """生成特定利益相关者视角"""
        prompt = f"""
从{stakeholder}的角度分析以下内容：

内容：{content}

请提供：
1. 这个群体的核心关切和利益
2. 从他们角度看的主要问题
3. 他们可能的反应和立场
4. 对他们的影响和后果

以清晰的结构化格式回答。
"""
        
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        
        perspective = self._parse_perspective_response(
            response.content,
            PerspectiveType.STAKEHOLDER, 
            stakeholder
        )
        
        if perspective:
            perspective.stakeholder = stakeholder
            
        return perspective
    
    def _parse_perspective_response(self, response: str, perspective_type: PerspectiveType, 
                                  identifier: str) -> Optional[Perspective]:
        """解析视角生成响应"""
        try:
            # 简单的响应解析
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            title = f"{perspective_type.value.replace('_', ' ').title()} - {identifier}"
            description = lines[0] if lines else "No description available"
            
            # 提取关键论据（寻找编号列表）
            key_arguments = []
            supporting_evidence = []
            
            current_section = None
            for line in lines:
                if any(keyword in line.lower() for keyword in ['论据', 'argument', '观点', 'view']):
                    current_section = 'arguments'
                elif any(keyword in line.lower() for keyword in ['证据', 'evidence', '例子', 'example']):
                    current_section = 'evidence'
                elif re.match(r'^\d+\.', line) or line.startswith('- '):
                    content = re.sub(r'^(\d+\.|[-*•])\s*', '', line)
                    if current_section == 'arguments':
                        key_arguments.append(content)
                    elif current_section == 'evidence':
                        supporting_evidence.append(content)
                    else:
                        key_arguments.append(content)  # 默认作为论据
            
            # 如果没有找到结构化内容，使用整个响应
            if not key_arguments:
                key_arguments = [description]
            
            return Perspective(
                perspective_type=perspective_type,
                title=title,
                description=description,
                key_arguments=key_arguments[:3],  # 最多3个论据
                supporting_evidence=supporting_evidence[:3],  # 最多3个证据
                confidence=0.8,
                relevance_score=0.8
            )
            
        except Exception as e:
            logger.error(f"Failed to parse perspective response: {e}")
            return None
    
    async def synthesize_perspectives(self, perspectives: List[Perspective]) -> str:
        """综合多个视角"""
        if not perspectives:
            return "没有可用的视角进行综合。"
        
        perspective_summaries = []
        for i, p in enumerate(perspectives, 1):
            summary = f"{i}. {p.title}：{p.description}"
            perspective_summaries.append(summary)
        
        prompt = f"""
请综合以下多个视角，提供一个平衡且深入的分析：

视角列表：
{chr(10).join(perspective_summaries)}

请提供：
1. 各视角的共同点和分歧
2. 更全面的理解框架
3. 平衡考虑各方观点的建议
4. 进一步思考的方向

保持客观和建设性。
"""
        
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        return response.content
    
    async def _synthesize_perspectives(self, perspectives: List[Perspective]) -> str:
        """内部综合方法"""
        return await self.synthesize_perspectives(perspectives)
    
    async def _identify_dialectical_tensions(self, perspectives: List[Perspective]) -> List[str]:
        """识别辩证冲突点"""
        if len(perspectives) < 2:
            return []
        
        tensions = []
        for i, p1 in enumerate(perspectives):
            for p2 in perspectives[i+1:]:
                if p1.perspective_type != p2.perspective_type:
                    tension = f"{p1.title} vs {p2.title}: 在核心假设和价值取向上存在根本分歧"
                    tensions.append(tension)
        
        return tensions[:3]  # 最多3个冲突点
    
    async def _generate_integration_suggestions(self, perspectives: List[Perspective]) -> List[str]:
        """生成整合建议"""
        if not perspectives:
            return []
        
        suggestions = [
            "寻找各视角的互补性，而非对立性",
            "在不同情境下采用不同视角的洞察",
            "构建包含多元观点的综合框架"
        ]
        
        # 基于具体视角类型添加建议
        has_opposing = any(p.perspective_type == PerspectiveType.OPPOSING for p in perspectives)
        has_disciplinary = any(p.perspective_type == PerspectiveType.MULTI_DISCIPLINARY for p in perspectives)
        
        if has_opposing:
            suggestions.append("将对立观点视为思考的起点，而非终点")
        
        if has_disciplinary:
            suggestions.append("利用跨学科视角发现创新解决方案")
        
        return suggestions