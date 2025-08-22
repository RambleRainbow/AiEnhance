"""
认知挑战模块
实现假设质疑、盲点检测、复杂性扩展等认知挑战功能
"""

import logging
import re
from typing import Any

from ..llm.interfaces import ChatMessage, LLMProvider, MessageRole
from ..memory.interfaces import MemorySystem
from .interfaces import (
    Challenge,
    ChallengeRequest,
    ChallengeResult,
    ChallengeType,
    CognitiveChallenger,
    CollaborationContext,
)

logger = logging.getLogger(__name__)


class CognitiveChallenge(CognitiveChallenger):
    """
    认知挑战器

    通过系统化的质疑和挑战，帮助用户发现思维盲点，
    突破认知局限，培养更深层的批判性思维
    """

    def __init__(
        self, llm_provider: LLMProvider, memory_system: MemorySystem | None = None
    ):
        self.llm_provider = llm_provider
        self.memory_system = memory_system

        # 认知偏见库
        self.cognitive_biases = {
            "confirmation_bias": {
                "name": "确认偏误",
                "description": "倾向于寻找支持已有观点的信息",
                "challenge_questions": [
                    "是否只关注了支持观点的证据？",
                    "有没有主动寻找反对证据？",
                    "如果证据指向相反结论会怎样？",
                ],
            },
            "anchoring_bias": {
                "name": "锚定效应",
                "description": "过度依赖第一个获得的信息",
                "challenge_questions": [
                    "第一印象是否影响了后续判断？",
                    "如果从不同起点开始思考会如何？",
                    "是否存在未考虑的替代方案？",
                ],
            },
            "availability_heuristic": {
                "name": "可得性启发",
                "description": "基于容易想到的例子做判断",
                "challenge_questions": [
                    "这些例子是否真正代表性？",
                    "是否存在不容易想到但重要的情况？",
                    "统计数据是否支持这个判断？",
                ],
            },
            "overconfidence_bias": {
                "name": "过度自信",
                "description": "高估自己判断的准确性",
                "challenge_questions": [
                    "这个判断的确定性是多少？",
                    "还有哪些未知因素？",
                    "如果判断错误会有什么后果？",
                ],
            },
        }

        # 思维盲点类型
        self.blind_spot_types = [
            "temporal_blindness",  # 时间维度盲点
            "scale_blindness",  # 尺度盲点
            "perspective_blindness",  # 视角盲点
            "system_blindness",  # 系统性盲点
            "cultural_blindness",  # 文化盲点
            "emotional_blindness",  # 情感盲点
        ]

        # 复杂性扩展维度
        self.complexity_dimensions = [
            "stakeholder_complexity",  # 利益相关者复杂性
            "temporal_complexity",  # 时间复杂性
            "causal_complexity",  # 因果复杂性
            "value_complexity",  # 价值复杂性
            "uncertainty_complexity",  # 不确定性复杂性
        ]

    async def generate_challenges(
        self, request: ChallengeRequest, context: CollaborationContext
    ) -> ChallengeResult:
        """生成认知挑战"""
        try:
            challenges = []

            # 分析用户的推理过程
            reasoning_analysis = await self._analyze_reasoning(
                request.content, request.user_reasoning
            )

            # 生成不同类型的挑战
            challenge_types = request.challenge_types or [
                ChallengeType.ASSUMPTION_QUESTIONING,
                ChallengeType.BLIND_SPOT_DETECTION,
                ChallengeType.COMPLEXITY_EXPANSION,
            ]

            for challenge_type in challenge_types:
                try:
                    challenge = await self._generate_challenge_by_type(
                        request, reasoning_analysis, challenge_type
                    )
                    if challenge:
                        challenges.append(challenge)
                except Exception as e:
                    logger.warning(
                        f"Failed to generate {challenge_type.value} challenge: {e}"
                    )
                    continue

            # 生成元认知反思
            meta_reflection = await self._generate_meta_reflection(
                challenges, reasoning_analysis
            )

            # 识别成长机会
            growth_opportunities = await self._identify_growth_opportunities(challenges)

            # 提供下一步建议
            next_steps = await self._generate_next_steps(
                challenges, request.intensity_level
            )

            return ChallengeResult(
                challenges=challenges,
                meta_reflection=meta_reflection,
                growth_opportunities=growth_opportunities,
                next_steps=next_steps,
                challenge_metadata={
                    "reasoning_analysis": reasoning_analysis,
                    "intensity_level": request.intensity_level,
                    "challenge_types_generated": [
                        c.challenge_type.value for c in challenges
                    ],
                },
            )

        except Exception as e:
            logger.error(f"Failed to generate challenges: {e}")
            raise

    async def _analyze_reasoning(
        self, content: str, user_reasoning: str | None
    ) -> dict[str, Any]:
        """分析用户的推理过程"""
        prompt = f"""
请分析以下内容中的推理过程：

内容：{content}

{f"用户推理过程：{user_reasoning}" if user_reasoning else ""}

请识别：
1. 核心假设和前提
2. 推理链条和逻辑结构
3. 证据类型和质量
4. 可能的认知偏见
5. 推理的强点和弱点
6. 未充分考虑的因素

以结构化格式返回分析结果。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)

        # 解析响应为结构化数据
        return self._parse_reasoning_analysis(response.content)

    def _parse_reasoning_analysis(self, response: str) -> dict[str, Any]:
        """解析推理分析响应"""
        analysis = {
            "assumptions": [],
            "reasoning_chain": [],
            "evidence_types": [],
            "potential_biases": [],
            "strengths": [],
            "weaknesses": [],
            "unconsidered_factors": [],
        }

        current_section = None
        lines = [line.strip() for line in response.split("\n") if line.strip()]

        for line in lines:
            # 检测段落标题
            if any(keyword in line.lower() for keyword in ["假设", "assumption"]):
                current_section = "assumptions"
            elif any(
                keyword in line.lower() for keyword in ["推理", "reasoning", "逻辑"]
            ):
                current_section = "reasoning_chain"
            elif any(keyword in line.lower() for keyword in ["证据", "evidence"]):
                current_section = "evidence_types"
            elif any(keyword in line.lower() for keyword in ["偏见", "bias"]):
                current_section = "potential_biases"
            elif any(keyword in line.lower() for keyword in ["强点", "strength"]):
                current_section = "strengths"
            elif any(keyword in line.lower() for keyword in ["弱点", "weak"]):
                current_section = "weaknesses"
            elif any(keyword in line.lower() for keyword in ["未考虑", "unconsidered"]):
                current_section = "unconsidered_factors"
            elif re.match(r"^\d+\.", line) or line.startswith("- "):
                content = re.sub(r"^(\d+\.|[-*•])\s*", "", line)
                if current_section and current_section in analysis:
                    analysis[current_section].append(content)

        return analysis

    async def _generate_challenge_by_type(
        self,
        request: ChallengeRequest,
        reasoning_analysis: dict[str, Any],
        challenge_type: ChallengeType,
    ) -> Challenge | None:
        """根据类型生成特定挑战"""

        if challenge_type == ChallengeType.ASSUMPTION_QUESTIONING:
            return await self._generate_assumption_challenge(
                request, reasoning_analysis
            )
        elif challenge_type == ChallengeType.BLIND_SPOT_DETECTION:
            return await self._generate_blind_spot_challenge(
                request, reasoning_analysis
            )
        elif challenge_type == ChallengeType.COMPLEXITY_EXPANSION:
            return await self._generate_complexity_challenge(
                request, reasoning_analysis
            )
        elif challenge_type == ChallengeType.CREATIVE_PROVOCATION:
            return await self._generate_creative_challenge(request, reasoning_analysis)

        return None

    async def _generate_assumption_challenge(
        self, request: ChallengeRequest, reasoning_analysis: dict[str, Any]
    ) -> Challenge | None:
        """生成假设质疑挑战"""
        assumptions = reasoning_analysis.get("assumptions", [])

        prompt = f"""
基于以下内容和识别的假设，生成质疑性问题：

内容：{request.content}
识别的假设：{assumptions}

请：
1. 对核心假设提出深度质疑
2. 探索替代假设的可能性
3. 检查假设的合理性和局限性
4. 提供不同假设下的推理路径

生成3-5个具有挑战性的问题。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)

        questions = self._extract_questions(response.content)

        return Challenge(
            challenge_type=ChallengeType.ASSUMPTION_QUESTIONING,
            title="假设质疑挑战",
            description="深度质疑核心假设，探索替代可能性",
            questions=questions,
            alternative_frameworks=self._extract_frameworks(response.content),
            hidden_assumptions=assumptions,
            potential_biases=reasoning_analysis.get("potential_biases", []),
            expansion_directions=[
                "重新审视基础假设",
                "探索对立假设",
                "构建新的前提框架",
            ],
        )

    async def _generate_blind_spot_challenge(
        self, request: ChallengeRequest, reasoning_analysis: dict[str, Any]
    ) -> Challenge | None:
        """生成盲点检测挑战"""
        prompt = f"""
识别以下内容中可能存在的思维盲点：

内容：{request.content}
未考虑因素：{reasoning_analysis.get("unconsidered_factors", [])}

请从以下维度检测盲点：
1. 时间维度（短期vs长期影响）
2. 规模维度（个体vs群体vs系统）
3. 视角维度（不同利益相关者）
4. 文化维度（不同文化背景）
5. 情感维度（理性vs感性）

为每个维度提出挑战性问题。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)

        questions = self._extract_questions(response.content)

        return Challenge(
            challenge_type=ChallengeType.BLIND_SPOT_DETECTION,
            title="思维盲点检测",
            description="揭示被忽视的重要视角和考虑因素",
            questions=questions,
            alternative_frameworks=["多维度分析框架", "利益相关者分析", "系统思维模型"],
            hidden_assumptions=reasoning_analysis.get("assumptions", []),
            potential_biases=["视角局限", "经验偏见", "情境依赖"],
            expansion_directions=[
                "扩展时间视野",
                "多角度思考",
                "跨文化理解",
                "情感因素考虑",
            ],
        )

    async def _generate_complexity_challenge(
        self, request: ChallengeRequest, reasoning_analysis: dict[str, Any]
    ) -> Challenge | None:
        """生成复杂性扩展挑战"""
        prompt = f"""
将以下问题的复杂性进行扩展：

内容：{request.content}

请从以下角度增加复杂性：
1. 利益相关者的多样性和冲突
2. 长期和短期效应的平衡
3. 因果关系的非线性和反馈循环
4. 价值观和目标的多元化
5. 不确定性和风险因素

为每个复杂性维度提出深入问题。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)

        questions = self._extract_questions(response.content)

        return Challenge(
            challenge_type=ChallengeType.COMPLEXITY_EXPANSION,
            title="复杂性扩展挑战",
            description="揭示问题的深层复杂性和相互关联",
            questions=questions,
            alternative_frameworks=["系统动力学", "复杂适应系统", "多目标优化"],
            hidden_assumptions=["简化假设", "线性思维", "单一目标"],
            potential_biases=["简化偏见", "控制错觉", "因果归因偏误"],
            expansion_directions=[
                "系统性思考",
                "动态分析",
                "多目标平衡",
                "不确定性管理",
            ],
        )

    async def _generate_creative_challenge(
        self, request: ChallengeRequest, reasoning_analysis: dict[str, Any]
    ) -> Challenge | None:
        """生成创意激发挑战"""
        prompt = f"""
为以下内容提供创意激发挑战：

内容：{request.content}

请：
1. 提出突破常规的问题
2. 鼓励跳出框架思考
3. 引入意外的联想和类比
4. 挑战传统解决方案
5. 激发创新思维

生成富有创意和启发性的问题。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)

        questions = self._extract_questions(response.content)

        return Challenge(
            challenge_type=ChallengeType.CREATIVE_PROVOCATION,
            title="创意激发挑战",
            description="突破常规思维，激发创新和创意",
            questions=questions,
            alternative_frameworks=["设计思维", "头脑风暴", "类比推理", "反向思考"],
            hidden_assumptions=["传统方法", "既有框架", "常规解决方案"],
            potential_biases=["功能固化", "经验依赖", "路径依赖"],
            expansion_directions=["跨界借鉴", "逆向思考", "极端场景", "未来导向"],
        )

    def _extract_questions(self, response: str) -> list[str]:
        """从响应中提取问题"""
        questions = []
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            # 查找以问号结尾的句子
            if line.endswith("？") or line.endswith("?"):
                # 清理格式符号
                clean_line = re.sub(r"^(\d+\.|[-*•])\s*", "", line)
                if clean_line:
                    questions.append(clean_line)

        # 如果没有找到问号结尾的句子，寻找包含疑问词的句子
        if not questions:
            for line in lines:
                line = line.strip()
                if any(
                    word in line
                    for word in [
                        "如何",
                        "为什么",
                        "什么",
                        "是否",
                        "会不会",
                        "how",
                        "why",
                        "what",
                        "whether",
                    ]
                ):
                    clean_line = re.sub(r"^(\d+\.|[-*•])\s*", "", line)
                    if clean_line:
                        questions.append(clean_line)

        return questions[:5]  # 最多5个问题

    def _extract_frameworks(self, response: str) -> list[str]:
        """从响应中提取框架"""
        frameworks = []
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in [
                    "框架",
                    "framework",
                    "模型",
                    "model",
                    "方法",
                    "approach",
                ]
            ):
                clean_line = re.sub(r"^(\d+\.|[-*•])\s*", "", line)
                if clean_line and len(clean_line) > 5:
                    frameworks.append(clean_line)

        return frameworks[:3]  # 最多3个框架

    async def _generate_meta_reflection(
        self, challenges: list[Challenge], reasoning_analysis: dict[str, Any]
    ) -> str:
        """生成元认知反思"""
        if not challenges:
            return "没有可用的挑战进行元认知反思。"

        challenge_summaries = [f"{c.title}: {c.description}" for c in challenges]

        prompt = f"""
基于以下认知挑战，提供元认知反思：

挑战列表：
{chr(10).join(challenge_summaries)}

推理分析：{reasoning_analysis}

请提供：
1. 对当前思维模式的反思
2. 发现的认知局限性
3. 思维能力的成长空间
4. 改进思维质量的建议

保持建设性和启发性。
"""

        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        response = await self.llm_provider.chat(messages)
        return response.content

    async def _identify_growth_opportunities(
        self, challenges: list[Challenge]
    ) -> list[str]:
        """识别成长机会"""
        opportunities = []

        for challenge in challenges:
            if challenge.challenge_type == ChallengeType.ASSUMPTION_QUESTIONING:
                opportunities.append("培养质疑精神，不轻易接受表面观点")
            elif challenge.challenge_type == ChallengeType.BLIND_SPOT_DETECTION:
                opportunities.append("发展多角度思维，识别认知盲点")
            elif challenge.challenge_type == ChallengeType.COMPLEXITY_EXPANSION:
                opportunities.append("提升系统思维能力，理解复杂性")
            elif challenge.challenge_type == ChallengeType.CREATIVE_PROVOCATION:
                opportunities.append("激发创新思维，突破思维定势")

        # 添加通用成长机会
        opportunities.extend(
            [
                "增强批判性思维能力",
                "培养开放和包容的思维态度",
                "发展元认知意识和反思能力",
            ]
        )

        return list(set(opportunities))  # 去重

    async def _generate_next_steps(
        self, challenges: list[Challenge], intensity_level: str
    ) -> list[str]:
        """生成下一步建议"""
        next_steps = []

        if intensity_level == "gentle":
            next_steps.extend(
                [
                    "从最感兴趣的挑战问题开始思考",
                    "尝试用不同角度重新审视问题",
                    "与他人讨论，获得外部视角",
                ]
            )
        elif intensity_level == "moderate":
            next_steps.extend(
                [
                    "深入探索每个挑战问题",
                    "寻找具体证据支持或反驳观点",
                    "构建更完整的思维框架",
                ]
            )
        elif intensity_level == "strong":
            next_steps.extend(
                [
                    "系统性地重新构建整个论证",
                    "主动寻找最强的反对观点",
                    "挑战最根本的假设和前提",
                ]
            )

        # 添加通用建议
        next_steps.extend(["记录思考过程，追踪思维变化", "将挑战性思维应用到其他问题"])

        return next_steps

    async def adapt_challenge_intensity(
        self, base_challenge: Challenge, user_response: str
    ) -> Challenge:
        """适应挑战强度"""
        # 分析用户响应的深度和开放性
        response_analysis = await self._analyze_user_response(user_response)

        # 基于分析调整挑战强度
        if response_analysis.get("depth", "moderate") == "shallow":
            # 增加引导性问题
            adapted_questions = base_challenge.questions + [
                "让我们从一个具体例子开始思考",
                "如果情况发生轻微变化会怎样？",
            ]
        elif response_analysis.get("openness", "moderate") == "resistant":
            # 使用更温和的挑战方式
            adapted_questions = [
                q.replace("为什么", "是否考虑过").replace("错误", "不同")
                for q in base_challenge.questions
            ]
        else:
            # 保持原有强度或增强
            adapted_questions = base_challenge.questions

        # 创建适应后的挑战
        adapted_challenge = Challenge(
            challenge_type=base_challenge.challenge_type,
            title=base_challenge.title,
            description=base_challenge.description,
            questions=adapted_questions,
            alternative_frameworks=base_challenge.alternative_frameworks,
            hidden_assumptions=base_challenge.hidden_assumptions,
            potential_biases=base_challenge.potential_biases,
            expansion_directions=base_challenge.expansion_directions,
        )

        return adapted_challenge

    async def _analyze_user_response(self, user_response: str) -> dict[str, str]:
        """分析用户响应"""
        # 简单的启发式分析
        analysis = {"depth": "moderate", "openness": "moderate"}

        # 深度分析
        if len(user_response.split()) < 20:
            analysis["depth"] = "shallow"
        elif len(user_response.split()) > 100:
            analysis["depth"] = "deep"

        # 开放性分析
        resistant_keywords = ["不对", "错误", "不同意", "反对"]
        if any(keyword in user_response for keyword in resistant_keywords):
            analysis["openness"] = "resistant"

        open_keywords = ["有趣", "确实", "思考", "可能"]
        if any(keyword in user_response for keyword in open_keywords):
            analysis["openness"] = "open"

        return analysis
