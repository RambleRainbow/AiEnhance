"""
集中式提示词管理模块
管理系统中所有LLM提示词模板，提供统一的访问接口和版本控制
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """提示词模板数据结构"""

    name: str  # 模板名称
    version: str  # 版本号
    template: str  # 模板内容
    description: str  # 描述
    variables: list[str]  # 模板变量列表
    category: str  # 分类（如：domain_inference, user_modeling等）
    language: str = "zh"  # 语言
    temperature: float = 0.7  # 推荐温度
    max_tokens: int = 800  # 推荐最大token数
    metadata: dict[str, Any] | None = None  # 扩展元数据


class PromptManager(ABC):
    """提示词管理器抽象接口"""

    @abstractmethod
    def get_prompt(self, name: str, version: str | None = None) -> PromptTemplate:
        """获取指定提示词模板"""
        pass

    @abstractmethod
    def render_prompt(
        self, name: str, variables: dict[str, Any], version: str | None = None
    ) -> str:
        """渲染提示词模板"""
        pass

    @abstractmethod
    def list_prompts(self, category: str | None = None) -> list[PromptTemplate]:
        """列出所有提示词模板"""
        pass


class FileSystemPromptManager(PromptManager):
    """文件系统提示词管理器 - 从文件加载提示词模板"""

    def __init__(self, prompts_dir: Path | None = None):
        if prompts_dir is None:
            # 默认使用项目中的prompts目录
            current_file = Path(__file__)
            prompts_dir = current_file.parent.parent / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self.templates: dict[str, dict[str, PromptTemplate]] = {}
        self.config_file = self.prompts_dir / "templates.yaml"

        self._load_templates_from_config()

    def _load_templates_from_config(self):
        """从配置文件加载模板定义"""
        try:
            if not self.config_file.exists():
                logger.error(f"Template config file not found: {self.config_file}")
                return

            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            for _category, templates in config.get("templates", {}).items():
                for _template_key, template_config in templates.items():
                    self._load_template_from_config(template_config)

            logger.info(f"Loaded {len(self.templates)} prompt templates from files")

        except Exception as e:
            logger.error(f"Failed to load template config: {e}")

    def _load_template_from_config(self, template_config: dict):
        """从配置加载单个模板"""
        try:
            template_file = self.prompts_dir / template_config["file"]

            if not template_file.exists():
                logger.error(f"Template file not found: {template_file}")
                return

            with open(template_file, encoding="utf-8") as f:
                template_content = f.read()

            template = PromptTemplate(
                name=template_config["name"],
                version=template_config["version"],
                template=template_content,
                description=template_config["description"],
                variables=template_config["variables"],
                category=template_config["category"],
                language=template_config.get("language", "zh"),
                temperature=template_config.get("temperature", 0.7),
                max_tokens=template_config.get("max_tokens", 800),
                metadata=template_config.get("metadata"),
            )

            self._register_template(template)

        except Exception as e:
            logger.error(
                f"Failed to load template {template_config.get('name', 'unknown')}: {e}"
            )

    def _register_template(self, template: PromptTemplate):
        """注册模板到内存"""
        if template.name not in self.templates:
            self.templates[template.name] = {}
        self.templates[template.name][template.version] = template

    def get_prompt(self, name: str, version: str | None = None) -> PromptTemplate:
        """获取指定提示词模板"""
        if name not in self.templates:
            raise ValueError(f"Prompt template '{name}' not found")

        if version is None:
            # 获取最新版本
            latest_version = max(self.templates[name].keys())
            return self.templates[name][latest_version]

        if version not in self.templates[name]:
            raise ValueError(f"Version '{version}' of prompt '{name}' not found")

        return self.templates[name][version]

    def render_prompt(
        self, name: str, variables: dict[str, Any], version: str | None = None
    ) -> str:
        """渲染提示词模板"""
        template = self.get_prompt(name, version)

        # 验证变量完整性
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            logger.warning(f"Missing variables for prompt '{name}': {missing_vars}")

        # 处理可选的context_section
        rendered_variables = variables.copy()
        if "context_section" in template.variables and "context" in variables:
            if variables["context"]:
                rendered_variables["context_section"] = (
                    f"\n额外上下文信息: {variables['context']}"
                )
            else:
                rendered_variables["context_section"] = ""

        try:
            return template.template.format(**rendered_variables)
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for prompt '{name}'") from e

    def list_prompts(self, category: str | None = None) -> list[PromptTemplate]:
        """列出所有提示词模板"""
        prompts = []
        for name_versions in self.templates.values():
            for template in name_versions.values():
                if category is None or template.category == category:
                    prompts.append(template)
        return prompts

    def add_template(self, template: PromptTemplate) -> bool:
        """添加新的提示词模板"""
        try:
            self._register_template(template)
            logger.info(f"Added prompt template: {template.name} v{template.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to add template: {e}")
            return False

    def get_template_info(self, name: str) -> dict[str, Any]:
        """获取模板信息"""
        if name not in self.templates:
            raise ValueError(f"Prompt template '{name}' not found")

        versions = list(self.templates[name].keys())
        latest = self.templates[name][max(versions)]

        return {
            "name": name,
            "versions": versions,
            "latest_version": max(versions),
            "category": latest.category,
            "description": latest.description,
            "variables": latest.variables,
            "recommended_settings": {
                "temperature": latest.temperature,
                "max_tokens": latest.max_tokens,
            },
        }


class StaticPromptManager(PromptManager):
    """静态提示词管理器 - 基于内存的实现（保留向后兼容）"""

    def __init__(self):
        self.templates: dict[str, dict[str, PromptTemplate]] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        """初始化默认提示词模板"""
        # 领域推断提示词
        self._register_domain_inference_prompts()

        # 用户建模提示词
        self._register_user_modeling_prompts()

        # 认知特征分析提示词
        self._register_cognitive_analysis_prompts()
        
        # 行为层输出适配提示词
        self._register_behavior_output_prompts()

        logger.info("Initialized default prompt templates")

    def _register_domain_inference_prompts(self):
        """注册领域推断相关提示词"""

        # 基础领域推断模板
        basic_template = PromptTemplate(
            name="domain_inference_basic",
            version="1.0",
            template="""你是一个专业的领域分析专家。请分析以下用户查询，确定它涉及的学术或专业领域。

可选领域包括但不限于: {domains}

请以JSON格式输出结果，包含以下字段：
- primary_domains: 主要涉及的领域（最多3个）
- secondary_domains: 次要相关的领域（最多3个）  
- confidence_scores: 每个领域的置信度分数（0-1）
- interdisciplinary: 是否为跨学科查询（true/false）
- reasoning: 简要说明判断理由

用户查询: {query}

{context_section}

输出格式示例：
{{
    "primary_domains": ["technology", "education"], 
    "secondary_domains": ["psychology"],
    "confidence_scores": {{"technology": 0.9, "education": 0.8, "psychology": 0.6}},
    "interdisciplinary": true,
    "reasoning": "查询涉及技术教育，结合了技术和教育两个领域，并涉及学习心理学的相关概念。"
}}

请确保输出有效的JSON格式。""",
            description="基础领域推断模板，用于分析用户查询涉及的专业领域",
            variables=["domains", "query", "context_section"],
            category="domain_inference",
            temperature=0.1,
            max_tokens=300,
        )

        # 专业领域深度分析模板
        advanced_template = PromptTemplate(
            name="domain_inference_advanced",
            version="1.0",
            template="""作为资深的跨学科领域专家，请对用户查询进行深度领域分析。

分析维度：
1. 核心专业领域识别
2. 相关交叉学科分析
3. 知识深度层级评估
4. 应用场景定位

可选专业领域: {domains}

用户查询: {query}
上下文信息: {context}

请以JSON格式输出详细分析结果：
{{
    "primary_domains": [主要领域数组],
    "secondary_domains": [次要领域数组],
    "confidence_scores": {{领域: 置信度}},
    "interdisciplinary": 是否跨学科,
    "depth_level": "基础|中级|高级|专家",
    "application_scenarios": [应用场景数组],
    "knowledge_prerequisites": [前置知识数组],
    "reasoning": "详细推理过程",
    "complexity_score": 0.0-1.0
}}""",
            description="高级领域推断模板，提供更详细的跨学科分析",
            variables=["domains", "query", "context"],
            category="domain_inference",
            temperature=0.2,
            max_tokens=500,
        )

        self._register_template(basic_template)
        self._register_template(advanced_template)

    def _register_user_modeling_prompts(self):
        """注册用户建模相关提示词"""

        # 认知特征分析模板
        cognitive_template = PromptTemplate(
            name="cognitive_analysis",
            version="1.0",
            template="""请分析用户的认知特征，包括：
1. 思维模式 (analytical/intuitive/creative)
2. 认知复杂度 (0.0-1.0)
3. 抽象思维能力 (0.0-1.0)
4. 创造性思维倾向 (0.0-1.0)
5. 推理偏好描述

{domain_context}

用户当前问句：{current_query}

用户历史交互：{historical_data}

请以JSON格式返回分析结果：
{{
    "thinking_mode": "analytical|intuitive|creative",
    "cognitive_complexity": 0.0-1.0,
    "abstraction_level": 0.0-1.0,
    "creativity_tendency": 0.0-1.0,
    "reasoning_preference": "推理偏好描述",
    "confidence": 0.0-1.0,
    "analysis_basis": "分析依据说明"
}}""",
            description="用户认知特征分析模板",
            variables=["domain_context", "current_query", "historical_data"],
            category="user_modeling",
            temperature=0.3,
            max_tokens=400,
        )

        # 学习风格识别模板
        learning_style_template = PromptTemplate(
            name="learning_style_analysis",
            version="1.0",
            template="""基于用户的查询和交互模式，分析其学习风格特征：

查询内容: {query}
领域背景: {domain}
交互历史: {interaction_history}

分析维度：
1. 信息处理偏好（视觉/听觉/动手）
2. 学习节奏偏好（快速/渐进/深入）
3. 反馈接收方式（直接/引导/探索）
4. 知识建构方式（线性/网络/循环）

JSON输出格式：
{{
    "processing_preference": "visual|auditory|kinesthetic",
    "learning_pace": "fast|gradual|deep",
    "feedback_style": "direct|guided|exploratory", 
    "knowledge_construction": "linear|network|iterative",
    "interaction_density": 0.0-1.0,
    "detail_preference": 0.0-1.0,
    "example_preference": 0.0-1.0,
    "explanation": "学习风格分析说明"
}}""",
            description="学习风格识别和分析模板",
            variables=["query", "domain", "interaction_history"],
            category="user_modeling",
            temperature=0.4,
            max_tokens=450,
        )

        self._register_template(cognitive_template)
        self._register_template(learning_style_template)

    def _register_cognitive_analysis_prompts(self):
        """注册认知分析相关提示词"""

        # 情境分析模板
        context_analysis_template = PromptTemplate(
            name="context_analysis",
            version="1.0",
            template="""作为情境分析专家，请分析用户当前的情境特征：

用户查询: {query}
背景信息: {background}
时间情境: {temporal_context}

分析要点：
1. 任务紧急程度 (0.0-1.0)
2. 复杂度评估 (0.0-1.0)  
3. 资源约束情况
4. 社交协作需求
5. 环境影响因素

请以JSON格式输出情境分析：
{{
    "urgency_level": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "resource_constraints": {{
        "time_pressure": 0.0-1.0,
        "knowledge_gap": 0.0-1.0,
        "tool_availability": 0.0-1.0
    }},
    "social_context": {{
        "collaboration_needed": true/false,
        "audience_type": "self|team|public|expert",
        "communication_formality": 0.0-1.0
    }},
    "environmental_factors": [影响因素数组],
    "recommended_approach": "具体建议",
    "context_summary": "情境总结"
}}""",
            description="用户情境分析模板，评估任务环境和约束条件",
            variables=["query", "background", "temporal_context"],
            category="cognitive_analysis",
            temperature=0.3,
            max_tokens=500,
        )

        # 问题复杂度评估模板
        complexity_assessment_template = PromptTemplate(
            name="complexity_assessment",
            version="1.0",
            template="""请评估以下问题的认知复杂度：

问题描述: {problem_description}
领域范围: {domain_scope}
用户背景: {user_background}

评估维度：
1. 概念抽象程度
2. 多步骤推理需求
3. 跨领域知识整合
4. 创新思维要求
5. 不确定性处理

输出JSON格式：
{{
    "overall_complexity": 0.0-1.0,
    "dimensions": {{
        "abstraction_level": 0.0-1.0,
        "reasoning_steps": 1-10,
        "domain_integration": 0.0-1.0,
        "creativity_requirement": 0.0-1.0,
        "uncertainty_level": 0.0-1.0
    }},
    "cognitive_load": "low|medium|high",
    "recommended_approach": "解决方案建议",
    "breakdown_suggestion": "问题分解建议",
    "complexity_explanation": "复杂度分析说明"
}}""",
            description="问题认知复杂度评估模板",
            variables=["problem_description", "domain_scope", "user_background"],
            category="cognitive_analysis",
            temperature=0.2,
            max_tokens=400,
        )

        self._register_template(context_analysis_template)
        self._register_template(complexity_assessment_template)

    def _register_behavior_output_prompts(self):
        """注册行为层输出适配相关提示词"""

        # 自适应输出生成模板
        adaptive_output_template = PromptTemplate(
            name="adaptive_output",
            version="1.0",
            template="""基于用户认知特征和学习风格，请调整和优化以下内容的表达方式：

原始内容：{original_content}

用户特征：
- 认知复杂度：{cognitive_complexity}
- 思维模式：{thinking_mode}
- 学习风格：{learning_style}
- 处理偏好：{processing_preference}
- 详细程度偏好：{detail_preference}

优化要求：
1. 根据用户认知水平调整内容难度和深度
2. 根据学习风格调整表达方式和结构
3. 根据处理偏好选择最佳呈现格式
4. 保持内容的准确性和完整性

请以JSON格式输出优化后的内容：
{{
    "adapted_content": "适配后的内容文本",
    "adaptation_strategy": "适配策略说明",
    "content_structure": "内容结构类型（linear|modular|layered）",
    "difficulty_level": "难度等级（basic|intermediate|advanced）",
    "presentation_format": "呈现格式建议",
    "engagement_elements": ["参与要素数组"],
    "adaptation_confidence": 0.0-1.0,
    "additional_resources": ["补充资源建议数组"]
}}""",
            description="基于用户特征的自适应内容输出生成模板",
            variables=["original_content", "cognitive_complexity", "thinking_mode", "learning_style", "processing_preference", "detail_preference"],
            category="behavior_output",
            temperature=0.4,
            max_tokens=800,
        )

        self._register_template(adaptive_output_template)

    def _register_template(self, template: PromptTemplate):
        """注册模板到内存"""
        if template.name not in self.templates:
            self.templates[template.name] = {}
        self.templates[template.name][template.version] = template

    def get_prompt(self, name: str, version: str | None = None) -> PromptTemplate:
        """获取指定提示词模板"""
        if name not in self.templates:
            raise ValueError(f"Prompt template '{name}' not found")

        if version is None:
            # 获取最新版本
            latest_version = max(self.templates[name].keys())
            return self.templates[name][latest_version]

        if version not in self.templates[name]:
            raise ValueError(f"Version '{version}' of prompt '{name}' not found")

        return self.templates[name][version]

    def render_prompt(
        self, name: str, variables: dict[str, Any], version: str | None = None
    ) -> str:
        """渲染提示词模板"""
        template = self.get_prompt(name, version)

        # 验证变量完整性
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            logger.warning(f"Missing variables for prompt '{name}': {missing_vars}")

        # 处理可选的context_section
        rendered_variables = variables.copy()
        if "context_section" in template.variables and "context" in variables:
            if variables["context"]:
                rendered_variables["context_section"] = (
                    f"\n额外上下文信息: {variables['context']}"
                )
            else:
                rendered_variables["context_section"] = ""

        try:
            return template.template.format(**rendered_variables)
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for prompt '{name}'") from e

    def list_prompts(self, category: str | None = None) -> list[PromptTemplate]:
        """列出所有提示词模板"""
        prompts = []
        for name_versions in self.templates.values():
            for template in name_versions.values():
                if category is None or template.category == category:
                    prompts.append(template)
        return prompts

    def add_template(self, template: PromptTemplate) -> bool:
        """添加新的提示词模板"""
        try:
            self._register_template(template)
            logger.info(f"Added prompt template: {template.name} v{template.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to add template: {e}")
            return False

    def get_template_info(self, name: str) -> dict[str, Any]:
        """获取模板信息"""
        if name not in self.templates:
            raise ValueError(f"Prompt template '{name}' not found")

        versions = list(self.templates[name].keys())
        latest = self.templates[name][max(versions)]

        return {
            "name": name,
            "versions": versions,
            "latest_version": max(versions),
            "category": latest.category,
            "description": latest.description,
            "variables": latest.variables,
            "recommended_settings": {
                "temperature": latest.temperature,
                "max_tokens": latest.max_tokens,
            },
        }


# 全局提示词管理器实例
_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """获取全局提示词管理器实例"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = FileSystemPromptManager()
    return _prompt_manager


def render_prompt(
    name: str, variables: dict[str, Any], version: str | None = None
) -> str:
    """便捷函数：渲染提示词"""
    return get_prompt_manager().render_prompt(name, variables, version)


def get_prompt_template(name: str, version: str | None = None) -> PromptTemplate:
    """便捷函数：获取提示词模板"""
    return get_prompt_manager().get_prompt(name, version)


def list_available_prompts(category: str | None = None) -> list[str]:
    """便捷函数：列出可用提示词名称"""
    manager = get_prompt_manager()
    templates = manager.list_prompts(category)
    return [f"{t.name} (v{t.version})" for t in templates]
