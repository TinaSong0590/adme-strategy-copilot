"""
LLM 集成模块 - 为 ADME Strategy Copilot 提供大模型能力

可选扩展，支持自然语言增强的 ADME 分析和报告生成。
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("adme_llm")

# LangChain 组件
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain 未安装，LLM 增强功能将不可用")


@dataclass
class ADMELLMConfig:
    """LLM 配置"""
    provider: str = "qwen"  # qwen 或 openai
    model: str = "qwen-max-latest"
    api_key: Optional[str] = None
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    temperature: float = 0.7
    max_tokens: int = 4096


class ADMELLM:
    """ADME 专用 LLM 集成"""
    
    def __init__(self, config: Optional[ADMELLMConfig] = None):
        self.config = config or self._load_config()
        self.llm = None
        self.available = False
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain 不可用，LLM 功能将被禁用")
            return
        
        self._initialize_llm()
    
    def _load_config(self) -> ADMELLMConfig:
        """从环境变量加载配置"""
        provider = os.getenv("ADME_LLM_PROVIDER", "qwen")
        
        if provider == "openai":
            return ADMELLMConfig(
                provider="openai",
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            )
        else:
            return ADMELLMConfig(
                provider="qwen",
                model=os.getenv("QWEN_MODEL", "qwen-max-latest"),
                api_key=os.getenv("QWEN_API_KEY"),
                base_url=os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            )
    
    def _initialize_llm(self):
        """初始化 LLM"""
        if not self.config.api_key:
            logger.warning(f"未找到 {self.config.provider.upper()} API Key，LLM 功能将被禁用")
            return
        
        try:
            self.llm = ChatOpenAI(
                model=self.config.model,
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            self.available = True
            logger.info(f"✅ {self.config.provider.upper()} LLM 初始化成功: {self.config.model}")
        except Exception as e:
            logger.error(f"❌ LLM 初始化失败: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """检查 LLM 是否可用"""
        return self.available and self.llm is not None
    
    async def enhance_chemistry_analysis(
        self,
        drug_name: str,
        chemistry_summary: Dict[str, Any]
    ) -> str:
        """
        使用 LLM 增强化学分析的自然语言描述
        
        Args:
            drug_name: 化合物名称
            chemistry_summary: 化学分析结果
        
        Returns:
            增强的自然语言分析
        """
        if not self.is_available():
            return chemistry_summary.get("chemistry_summary_text", "LLM 不可用")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的药物化学家，擅长将化学分析数据转化为清晰的自然语言解释。
            
请基于以下化学分析数据，为药物研发科学家撰写一段专业的化学特征描述。

要求：
1. 解释关键结构特征及其对 ADME 的影响
2. 指出潜在的安全问题（如反应性代谢物风险）
3. 提供临床前研究建议
4. 使用专业但易于理解的语言"""),
            ("user", """化合物: {drug_name}

化学分析数据:
- 分子式: {formula}
- 分子量: {mw} Da
- 结构特征: {features}
- Phase I 代谢位点: {phase1}
- Phase II 代谢位点: {phase2}
- CYP 代谢酶: {cyp}
- 渗透性提示: {permeability}
- 清除途径: {clearance}

请撰写一段专业的化学特征描述。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = await chain.ainvoke({
                "drug_name": drug_name,
                "formula": chemistry_summary.get("molecular_formula", "未知"),
                "mw": chemistry_summary.get("molecular_weight", "未知"),
                "features": str(chemistry_summary.get("structural_features", {})),
                "phase1": str(chemistry_summary.get("phase1_liabilities", [])),
                "phase2": str(chemistry_summary.get("phase2_liabilities", [])),
                "cyp": str(chemistry_summary.get("cyp_preference_hints", [])),
                "permeability": str(chemistry_summary.get("permeability_hints", [])),
                "clearance": str(chemistry_summary.get("clearance_route_hints", []))
            })
            return result
        except Exception as e:
            logger.error(f"LLM 化学分析增强失败: {e}")
            return chemistry_summary.get("chemistry_summary_text", "LLM 调用失败")
    
    async def summarize_literature_findings(
        self,
        drug_name: str,
        literature_records: list[Dict[str, Any]]
    ) -> str:
        """
        使用 LLM 总结文献发现
        
        Args:
            drug_name: 化合物名称
            literature_records: 文献记录列表
        
        Returns:
            文献总结
        """
        if not self.is_available():
            return f"找到 {len(literature_records)} 篇相关文献"
        
        # 构建文献摘要文本
        papers_text = "\n".join([
            f"{i+1}. {r.get('title', 'N/A')} ({r.get('year', 'N/A')})"
            for i, r in enumerate(literature_records[:10])
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的临床药理学家，擅长总结和解读药物文献。

请基于以下文献列表，撰写一段简洁但全面的文献综述总结。

要求：
1. 识别主要研究发现
2. 指出文献中的一致性和分歧
3. 强调对临床前研究设计的影响
4. 控制在 300 字以内"""),
            ("user", """化合物: {drug_name}

相关文献:
{papers}

请撰写文献综述总结。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = await chain.ainvoke({
                "drug_name": drug_name,
                "papers": papers_text or "未找到相关文献"
            })
            return result
        except Exception as e:
            logger.error(f"LLM 文献总结失败: {e}")
            return f"找到 {len(literature_records)} 篇相关文献"
    
    async def generate_executive_summary(
        self,
        drug_name: str,
        chemistry: Dict[str, Any],
        metabolism: Dict[str, Any],
        protocol: Dict[str, Any]
    ) -> str:
        """
        生成高管级别执行摘要
        
        Args:
            drug_name: 化合物名称
            chemistry: 化学分析结果
            metabolism: 代谢预测结果
            protocol: 研究方案
        
        Returns:
            执行摘要
        """
        if not self.is_available():
            return "LLM 不可用，请使用标准报告模式"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位生物技术公司的高管，擅长撰写简洁、有影响力的决策支持文档。

请为以下临床前 ADME 数据撰写一段执行摘要，供投资人和高层决策者阅读。

格式要求：
- 标题: 化合物执行摘要
- 关键发现: 3-4 个要点
- 风险评估: 高/中/低
- 下一步建议: 1-2 句话
- 总字数控制在 200 字以内
- 使用 bullet points"""),
            ("user", """化合物: {drug_name}

化学分析:
- 分子量: {mw} Da
- CYP 代谢酶: {cyp}
- 渗透性: {permeability}
- 关键风险: {chemistry_risks}

代谢预测:
- 主要途径: {pathways}
- 清除风险: {clearance_risk}
- 反应性代谢物风险: {reactive_risk}

研究方案:
- 建议: {protocol_summary}
- 风险标志: {risk_flags}

请撰写执行摘要。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = await chain.ainvoke({
                "drug_name": drug_name,
                "mw": chemistry.get("molecular_weight", "未知"),
                "cyp": str(chemistry.get("cyp_preference_hints", [])),
                "permeability": str(chemistry.get("permeability_hints", [])),
                "chemistry_risks": str(chemistry.get("reactive_metabolite_risks", [])),
                "pathways": str(metabolism.get("pathways", [])),
                "clearance_risk": metabolism.get("clearance_risk", "未知"),
                "reactive_risk": metabolism.get("reactive_metabolite_risk", "未知"),
                "protocol_summary": protocol.get("assay_work_package_summary", ""),
                "risk_flags": str(protocol.get("risk_flags", []))
            })
            return result
        except Exception as e:
            logger.error(f"LLM 执行摘要生成失败: {e}")
            return "LLM 调用失败"


# 全局实例
_llm_instance: Optional[ADMELLM] = None


def get_llm() -> Optional[ADMELLM]:
    """获取 LLM 实例（单例模式）"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ADMELLM()
    return _llm_instance


def is_llm_available() -> bool:
    """检查 LLM 是否可用"""
    llm = get_llm()
    return llm is not None and llm.is_available()
