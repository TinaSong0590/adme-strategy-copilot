"""
ADME Strategy Copilot MCP 服务器

基于 FastMCP 实现，为 Claude Desktop/Cursor 等 AI 工具提供临床前 ADME 策略分析能力。

使用方法:
1. 安装依赖: pip install -r requirements.txt
2. 启动 MCP 服务器: python -m mcp_server
3. 在 Claude Desktop/Cursor 中配置 MCP 工具
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

# 确保项目路径在 sys.path 中
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 尝试导入 FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("警告: fastmcp 未安装，MCP 服务器将不可用")
    print("请运行: pip install fastmcp")

from utils.models import ADMERequest, PipelineResult
from app.config import get_config
from agents.lead_agent import LeadAgent
from agents.chemistry_agent import ChemistryAgent
from agents.literature_agent import LiteratureAgent
from agents.metabolism_prediction_agent import MetabolismPredictionAgent
from agents.protocol_design_agent import ProtocolDesignAgent
from agents.synthesis_agent import SynthesisAgent
from services.chemistry_service import ChemistryService
from services.literature_service import LiteratureService
from services.report_generator import ReportGenerator
from services.skill_loader import SkillLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("adme_mcp")


# ========== MCP 服务器实例 ==========

if MCP_AVAILABLE:
    mcp = FastMCP("ADME Strategy Copilot")
else:
    mcp = None


# ========== 工具函数 ==========

def create_lead_agent() -> LeadAgent:
    """创建 LeadAgent 实例（与 main.py 相同逻辑）"""
    config = get_config()
    skill_loader = SkillLoader(
        primary_dir=config.openclaw_skills_dir,
        fallback_dir=config.project_skills_dir,
    )
    return LeadAgent(
        skill_loader=skill_loader,
        chemistry_agent=ChemistryAgent(chemistry_service=ChemistryService()),
        metabolism_agent=MetabolismPredictionAgent(),
        literature_agent=LiteratureAgent(
            literature_service=LiteratureService(
                enable_real_search=config.enable_real_literature_search,
                provider=config.literature_provider,
                europe_pmc_base_url=config.europe_pmc_base_url,
                pubmed_esearch_url=config.pubmed_esearch_url,
                pubmed_esummary_url=config.pubmed_esummary_url,
                pubmed_efetch_url=config.pubmed_efetch_url,
                enable_secondary_provider=config.enable_secondary_literature_provider,
                secondary_provider=config.secondary_literature_provider,
                timeout=config.literature_timeout,
                default_max_results=config.literature_max_results,
            )
        ),
        protocol_design_agent=ProtocolDesignAgent(),
        synthesis_agent=SynthesisAgent(),
        report_generator=ReportGenerator(reports_dir=config.reports_dir),
    )


# ========== MCP 工具定义 ==========

if MCP_AVAILABLE:
    
    @mcp.tool()
    def generate_adme_report(
        drug_name: str,
        smiles: str = "",
        species: str = "Rat",
        focus: str = "MetID",
        report_mode: str = "scientist"
    ) -> Dict[str, Any]:
        """
        生成完整的临床前 ADME 策略报告
        
        Args:
            drug_name: 化合物名称 (必需)
            smiles: SMILES 结构字符串 (可选，有则更准确)
            species: 实验物种 (Rat/Human/Dog/Mouse)
            focus: ADME 关注领域 (MetID/PK/BA/All)
            report_mode: 报告模式 (scientist/executive/cro_proposal/regulatory_prep)
        
        Returns:
            完整的 ADME 分析报告
        """
        logger.info(f"生成 ADME 报告: {drug_name}, Species: {species}, Focus: {focus}")
        
        try:
            request = ADMERequest(
                drug_name=drug_name,
                smiles=smiles,
                species=species,
                focus=focus,
                report_mode=report_mode
            )
            
            lead_agent = create_lead_agent()
            result = lead_agent.run(request)
            
            return {
                "success": True,
                "report_path": str(result.report_path),
                "drug_name": drug_name,
                "smiles_valid": result.chemistry.smiles_valid,
                "rdkit_used": result.chemistry.rdkit_used,
                "cyp_flags": result.metabolism.cyp_flags,
                "clearance_risk": result.metabolism.clearance_risk,
                "pathways": result.metabolism.pathways,
                "warnings": result.metabolism.warnings,
                "literature_provider": result.literature_search.provider_used,
                "literature_count": len(result.literature),
                "report_content": result.report.chemistry_intelligence[:500] if result.report.chemistry_intelligence else "",
                "report_summary": result.report.executive_priority_summary[:500] if result.report.executive_priority_summary else ""
            }
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def analyze_chemistry(
        drug_name: str,
        smiles: str = ""
    ) -> Dict[str, Any]:
        """
        分析化合物化学结构特征
        
        Args:
            drug_name: 化合物名称
            smiles: SMILES 结构字符串
        
        Returns:
            化学分析结果，包含结构特征、软点、CYP 预测等
        """
        logger.info(f"化学分析: {drug_name}")
        
        try:
            chemistry_service = ChemistryService()
            chemistry_agent = ChemistryAgent(chemistry_service=chemistry_service)
            
            request = ADMERequest(drug_name=drug_name, smiles=smiles)
            chemistry = chemistry_agent.run(request)
            
            return {
                "success": True,
                "smiles_valid": chemistry.smiles_valid,
                "rdkit_used": chemistry.rdkit_used,
                "molecular_weight": chemistry.molecular_weight,
                "molecular_formula": chemistry.molecular_formula,
                "feature_flags": chemistry.feature_flags or [],
                "structural_features": chemistry.structural_features or {},
                "soft_spot_hints": chemistry.soft_spot_hints or [],
                "phase1_liabilities": chemistry.phase1_liabilities or [],
                "phase2_liabilities": chemistry.phase2_liabilities or [],
                "cyp_preference_hints": chemistry.cyp_preference_hints or [],
                "transporter_hints": chemistry.transporter_hints or [],
                "permeability_hints": chemistry.permeability_hints or [],
                "clearance_route_hints": chemistry.clearance_route_hints or [],
                "chemistry_summary_text": chemistry.chemistry_summary_text
            }
        except Exception as e:
            logger.error(f"化学分析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def predict_metabolism(
        drug_name: str,
        smiles: str = "",
        species: str = "Rat",
        focus: str = "MetID"
    ) -> Dict[str, Any]:
        """
        预测化合物代谢特征
        
        Args:
            drug_name: 化合物名称
            smiles: SMILES 结构字符串
            species: 实验物种
            focus: ADME 关注领域
        
        Returns:
            代谢预测结果
        """
        logger.info(f"代谢预测: {drug_name}, Species: {species}")
        
        try:
            chemistry_service = ChemistryService()
            chemistry_agent = ChemistryAgent(chemistry_service=chemistry_service)
            metabolism_agent = MetabolismPredictionAgent()
            
            request = ADMERequest(drug_name=drug_name, smiles=smiles, species=species, focus=focus)
            chemistry = chemistry_agent.run(request)
            metabolism = metabolism_agent.run(request=request, chemistry=chemistry)
            
            return {
                "success": True,
                "pathways": metabolism.pathways,
                "warnings": metabolism.warnings,
                "cyp_flags": metabolism.cyp_flags,
                "clearance_risk": metabolism.clearance_risk,
                "reactive_metabolite_risk": metabolism.reactive_metabolite_risk,
                "detected_features": metabolism.detected_features,
                "rationale": metabolism.rationale
            }
        except Exception as e:
            logger.error(f"代谢预测失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def search_literature(
        drug_name: str,
        species: str = "Rat",
        focus: str = "MetID",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        搜索相关文献
        
        Args:
            drug_name: 化合物名称
            species: 实验物种
            focus: ADME 关注领域
            max_results: 最大结果数
        
        Returns:
            文献搜索结果
        """
        logger.info(f"文献搜索: {drug_name}, Species: {species}, Focus: {focus}")
        
        try:
            config = get_config()
            literature_service = LiteratureService(
                enable_real_search=config.enable_real_literature_search,
                provider=config.literature_provider,
                europe_pmc_base_url=config.europe_pmc_base_url,
                pubmed_esearch_url=config.pubmed_esearch_url,
                pubmed_esummary_url=config.pubmed_esummary_url,
                pubmed_efetch_url=config.pubmed_efetch_url,
                enable_secondary_provider=config.enable_secondary_literature_provider,
                secondary_provider=config.secondary_literature_provider,
                timeout=config.literature_timeout,
                default_max_results=max_results,
            )
            
            literature_agent = LiteratureAgent(literature_service=literature_service)
            metabolism_agent = MetabolismPredictionAgent()
            
            request = ADMERequest(drug_name=drug_name, species=species, focus=focus)
            placeholder_metabolism = metabolism_agent.run(request=request, chemistry=None)
            literature_search = literature_agent.run(request=request, metabolism=placeholder_metabolism)
            
            records = []
            for ref in literature_search.records[:max_results]:
                records.append({
                    "title": ref.title,
                    "source": ref.source,
                    "year": ref.year,
                    "authors": ref.authors,
                    "journal": ref.journal,
                    "summary": ref.summary[:200] if ref.summary else "",
                    "score": ref.final_score,
                    "evidence_bucket": ref.evidence_bucket
                })
            
            return {
                "success": True,
                "provider_used": literature_search.provider_used,
                "queries_used": literature_search.queries_used,
                "total_records": len(literature_search.records),
                "records": records
            }
        except Exception as e:
            logger.error(f"文献搜索失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def design_protocol(
        drug_name: str,
        smiles: str = "",
        species: str = "Rat",
        focus: str = "MetID"
    ) -> Dict[str, Any]:
        """
        设计预临床研究方案
        
        Args:
            drug_name: 化合物名称
            smiles: SMILES 结构字符串
            species: 实验物种
            focus: ADME 关注领域
        
        Returns:
            预临床研究方案
        """
        logger.info(f"方案设计: {drug_name}, Species: {species}")
        
        try:
            lead_agent = create_lead_agent()
            
            request = ADMERequest(drug_name=drug_name, smiles=smiles, species=species, focus=focus)
            chemistry = lead_agent.chemistry_agent.run(request)
            metabolism = lead_agent.metabolism_agent.run(request=request, chemistry=chemistry)
            protocol = lead_agent.protocol_design_agent.run(request=request, metabolism=metabolism, chemistry=chemistry)
            
            return {
                "success": True,
                "in_vitro": protocol.in_vitro,
                "in_vivo": protocol.in_vivo,
                "translation": protocol.translation,
                "risk_flags": protocol.risk_flags,
                "assay_work_package_summary": protocol.assay_work_package_summary,
                "proposed_first_pass_package": protocol.proposed_first_pass_package,
                "optional_followup_package": protocol.optional_followup_package
            }
        except Exception as e:
            logger.error(f"方案设计失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool()
    def get_supported_focus_areas() -> Dict[str, Any]:
        """
        获取支持的 ADME 关注领域
        
        Returns:
            所有支持的关注领域列表
        """
        focus_areas = {
            "MetID": "代谢物鉴定 - 代谢通路和代谢物结构分析",
            "PK": "药代动力学 - 吸收、分布、消除动力学",
            "BA": "生物利用度 - 生物利用度优化和预测",
            "All": "全面分析 - 综合所有 ADME 领域"
        }
        
        species_list = {
            "Rat": "大鼠 - 最常用的临床前模型",
            "Human": "人 - 人体翻译预测",
            "Dog": "犬 - 中等体型动物模型",
            "Mouse": "小鼠 - 基因工程模型"
        }
        
        report_modes = {
            "scientist": "科学家模式 - 完整技术视图",
            "executive": "高管模式 - 决策备忘录",
            "cro_proposal": "CRO提案模式 - 工作包导向",
            "regulatory_prep": "监管准备模式 - 保守不确定性导向"
        }
        
        return {
            "success": True,
            "focus_areas": focus_areas,
            "species": species_list,
            "report_modes": report_modes
        }


# ========== MCP 服务器启动 ==========

def start_mcp_server():
    """启动 MCP 服务器"""
    if not MCP_AVAILABLE:
        print("=" * 60)
        print("错误: FastMCP 未安装，无法启动服务器")
        print("请运行: pip install fastmcp")
        print("=" * 60)
        return
    
    print("=" * 60)
    print("ADME Strategy Copilot MCP 服务器")
    print("=" * 60)
    print("可用工具:")
    print("  - generate_adme_report: 生成完整 ADME 报告")
    print("  - analyze_chemistry: 分析化合物化学结构")
    print("  - predict_metabolism: 预测代谢特征")
    print("  - search_literature: 搜索相关文献")
    print("  - design_protocol: 设计预临床研究方案")
    print("  - get_supported_focus_areas: 获取支持的关注领域")
    print("=" * 60)
    print("启动 MCP 服务器...")
    print()
    
    mcp.run()


if __name__ == "__main__":
    start_mcp_server()
