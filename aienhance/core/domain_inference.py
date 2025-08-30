"""
领域推断模块
使用大模型进行查询领域推断的抽象接口和实现
支持多模型协同调度的可配置架构
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DomainInferenceResult:
    """领域推断结果"""
    primary_domains: List[str]  # 主要领域
    secondary_domains: List[str]  # 次要领域  
    confidence_scores: Dict[str, float]  # 每个领域的置信度
    interdisciplinary: bool  # 是否跨学科
    reasoning: Optional[str] = None  # 推理过程（可选）
    metadata: Optional[Dict[str, Any]] = None  # 额外元数据


@dataclass
class DomainInferenceConfig:
    """领域推断配置"""
    llm_provider: Any  # LLM提供商实例
    model_name: Optional[str] = None  # 特定模型名称
    temperature: float = 0.1  # 低温度确保一致性
    max_tokens: int = 300  # 限制输出长度
    timeout: int = 10  # 超时设置
    fallback_to_keywords: bool = True  # 是否回退到关键词匹配
    custom_domains: Optional[List[str]] = None  # 自定义领域列表


class DomainInferenceProvider(ABC):
    """领域推断提供商抽象接口"""
    
    def __init__(self, config: DomainInferenceConfig):
        self.config = config
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化提供商"""
        pass
    
    @abstractmethod
    async def infer_domains(self, query: str, context: Optional[Dict[str, Any]] = None) -> DomainInferenceResult:
        """推断查询涉及的领域"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """清理资源"""
        pass


class LLMDomainInferenceProvider(DomainInferenceProvider):
    """基于大模型的领域推断提供商"""
    
    def __init__(self, config: DomainInferenceConfig):
        super().__init__(config)
        self.llm_provider = config.llm_provider
        self.prompt_template = self._create_prompt_template()
        
    def _create_prompt_template(self) -> str:
        """创建领域推断的提示模板"""
        base_domains = [
            "technology", "science", "education", "business", "art", 
            "health", "finance", "legal", "engineering", "mathematics",
            "language", "history", "philosophy", "psychology", "social_science"
        ]
        
        if self.config.custom_domains:
            domains_list = self.config.custom_domains
        else:
            domains_list = base_domains
        
        domains_str = ", ".join(domains_list)
        
        return f"""你是一个专业的领域分析专家。请分析以下用户查询，确定它涉及的学术或专业领域。

可选领域包括但不限于: {domains_str}

请以JSON格式输出结果，包含以下字段：
- primary_domains: 主要涉及的领域（最多3个）
- secondary_domains: 次要相关的领域（最多3个）  
- confidence_scores: 每个领域的置信度分数（0-1）
- interdisciplinary: 是否为跨学科查询（true/false）
- reasoning: 简要说明判断理由

用户查询: {{query}}

输出格式示例：
{{
    "primary_domains": ["technology", "education"], 
    "secondary_domains": ["psychology"],
    "confidence_scores": {{"technology": 0.9, "education": 0.8, "psychology": 0.6}},
    "interdisciplinary": true,
    "reasoning": "查询涉及技术教育，结合了技术和教育两个领域，并涉及学习心理学的相关概念。"
}}

请确保输出有效的JSON格式。"""

    async def initialize(self) -> bool:
        """初始化LLM提供商"""
        try:
            if not self.llm_provider:
                logger.error("LLM provider not configured")
                return False
                
            # 这里可以添加LLM连接测试
            self.is_initialized = True
            logger.info("LLM domain inference provider initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM domain inference provider: {e}")
            return False
    
    async def infer_domains(self, query: str, context: Optional[Dict[str, Any]] = None) -> DomainInferenceResult:
        """使用大模型推断领域"""
        if not self.is_initialized:
            raise RuntimeError("Domain inference provider not initialized")
        
        try:
            # 构建完整提示
            prompt = self.prompt_template.replace("{query}", query)
            if context:
                prompt += f"\n\n额外上下文信息: {json.dumps(context, ensure_ascii=False)}"
            
            # 调用LLM
            response = await asyncio.wait_for(
                self._call_llm(prompt),
                timeout=self.config.timeout
            )
            
            # 解析响应
            return self._parse_llm_response(response, query)
            
        except asyncio.TimeoutError:
            logger.warning(f"LLM domain inference timeout for query: {query[:50]}...")
            return self._fallback_inference(query)
            
        except Exception as e:
            logger.error(f"LLM domain inference failed: {e}")
            return self._fallback_inference(query)
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM生成响应"""
        try:
            # 构建消息格式
            messages = [{"role": "user", "content": prompt}]
            
            # 调用LLM (需要适配不同的LLM接口)
            if hasattr(self.llm_provider, 'generate_async'):
                # 异步接口
                response = await self.llm_provider.generate_async(
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name
                )
            elif hasattr(self.llm_provider, 'chat'):
                # 同步聊天接口
                response = await asyncio.to_thread(
                    self.llm_provider.chat,
                    messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    model=self.config.model_name or "default"
                )
            else:
                raise ValueError("Unsupported LLM provider interface")
            
            # 提取文本内容
            if isinstance(response, dict):
                return response.get('content', response.get('message', str(response)))
            elif hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str, original_query: str) -> DomainInferenceResult:
        """解析LLM响应"""
        try:
            # 尝试提取JSON部分
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            # 解析JSON
            parsed = json.loads(response)
            
            # 验证必需字段
            primary_domains = parsed.get('primary_domains', [])
            secondary_domains = parsed.get('secondary_domains', [])
            confidence_scores = parsed.get('confidence_scores', {})
            interdisciplinary = parsed.get('interdisciplinary', False)
            reasoning = parsed.get('reasoning', '')
            
            return DomainInferenceResult(
                primary_domains=primary_domains,
                secondary_domains=secondary_domains,
                confidence_scores=confidence_scores,
                interdisciplinary=interdisciplinary,
                reasoning=reasoning,
                metadata={
                    "provider": "llm",
                    "model": self.config.model_name,
                    "original_query": original_query
                }
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            return self._fallback_inference(original_query)
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._fallback_inference(original_query)
    
    def _fallback_inference(self, query: str) -> DomainInferenceResult:
        """回退到关键词匹配的领域推断"""
        if not self.config.fallback_to_keywords:
            return DomainInferenceResult(
                primary_domains=["general"],
                secondary_domains=[],
                confidence_scores={"general": 0.5},
                interdisciplinary=False,
                reasoning="LLM推断失败，未启用关键词回退",
                metadata={"provider": "fallback", "method": "none"}
            )
        
        logger.info("Falling back to keyword-based domain inference")
        
        # 使用原有的关键词匹配逻辑
        domain_keywords = {
            "technology": ["技术", "科技", "编程", "AI", "人工智能", "软件", "algorithm", "programming", "AI", "software"],
            "education": ["教育", "学习", "教学", "培训", "education", "learning", "teaching", "training"],
            "science": ["科学", "研究", "实验", "理论", "science", "research", "experiment", "theory"],
            "business": ["商业", "管理", "营销", "经济", "business", "management", "marketing", "economics"],
            "art": ["艺术", "设计", "创作", "美学", "art", "design", "creative", "aesthetic"],
            "health": ["健康", "医疗", "医学", "health", "medical", "medicine"],
            "finance": ["金融", "财务", "投资", "finance", "financial", "investment"],
            "legal": ["法律", "法规", "合规", "legal", "law", "regulation"],
        }
        
        detected_domains = []
        confidence_scores = {}
        query_lower = query.lower()
        
        for domain, keywords in domain_keywords.items():
            matches = sum(1 for keyword in keywords if keyword.lower() in query_lower)
            if matches > 0:
                confidence = min(0.9, 0.3 + matches * 0.2)  # 基于匹配数量计算置信度
                detected_domains.append((domain, confidence))
                confidence_scores[domain] = confidence
        
        # 按置信度排序
        detected_domains.sort(key=lambda x: x[1], reverse=True)
        
        if not detected_domains:
            return DomainInferenceResult(
                primary_domains=["general"],
                secondary_domains=[],
                confidence_scores={"general": 0.5},
                interdisciplinary=False,
                reasoning="未检测到特定领域关键词，归类为通用领域",
                metadata={"provider": "fallback", "method": "keywords"}
            )
        
        # 分配主要和次要领域
        primary_domains = [domain for domain, _ in detected_domains[:2]]
        secondary_domains = [domain for domain, _ in detected_domains[2:4]]
        interdisciplinary = len(detected_domains) > 1
        
        return DomainInferenceResult(
            primary_domains=primary_domains,
            secondary_domains=secondary_domains,
            confidence_scores=confidence_scores,
            interdisciplinary=interdisciplinary,
            reasoning=f"基于关键词匹配检测到{len(detected_domains)}个相关领域",
            metadata={"provider": "fallback", "method": "keywords"}
        )
    
    async def cleanup(self) -> None:
        """清理资源"""
        try:
            # 这里可以添加特定的清理逻辑
            self.is_initialized = False
            logger.info("LLM domain inference provider cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


class DomainInferenceManager:
    """领域推断管理器
    
    支持多提供商配置和切换，为多模型协同调度做准备
    """
    
    def __init__(self):
        self.providers: Dict[str, DomainInferenceProvider] = {}
        self.default_provider_name: Optional[str] = None
        
    async def register_provider(self, name: str, provider: DomainInferenceProvider) -> bool:
        """注册领域推断提供商"""
        try:
            success = await provider.initialize()
            if success:
                self.providers[name] = provider
                if self.default_provider_name is None:
                    self.default_provider_name = name
                logger.info(f"Registered domain inference provider: {name}")
                return True
            else:
                logger.error(f"Failed to initialize provider: {name}")
                return False
        except Exception as e:
            logger.error(f"Error registering provider {name}: {e}")
            return False
    
    async def infer_domains(
        self, 
        query: str, 
        provider_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DomainInferenceResult:
        """推断领域"""
        provider_name = provider_name or self.default_provider_name
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not found: {provider_name}")
        
        provider = self.providers[provider_name]
        return await provider.infer_domains(query, context)
    
    async def cleanup(self) -> None:
        """清理所有提供商"""
        for name, provider in self.providers.items():
            try:
                await provider.cleanup()
                logger.info(f"Cleaned up provider: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up provider {name}: {e}")
        
        self.providers.clear()
        self.default_provider_name = None
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return list(self.providers.keys())
    
    def set_default_provider(self, name: str) -> bool:
        """设置默认提供商"""
        if name in self.providers:
            self.default_provider_name = name
            return True
        return False