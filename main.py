"""
ADME Strategy Copilot - 主入口

支持 CLI 和交互式两种模式。
"""

from __future__ import annotations

import argparse
import json
import sys
import logging
from pathlib import Path

from agents.chemistry_agent import ChemistryAgent
from agents.lead_agent import LeadAgent
from agents.literature_agent import LiteratureAgent
from agents.metabolism_prediction_agent import MetabolismPredictionAgent
from agents.protocol_design_agent import ProtocolDesignAgent
from agents.synthesis_agent import SynthesisAgent
from app.config import get_config
from services.chemistry_service import ChemistryService
from services.literature_service import LiteratureService
from services.report_generator import ReportGenerator
from services.skill_loader import SkillLoader
from utils.models import ADMERequest
from utils.callbacks import create_console_callback, CallbackManager, PipelineEvent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("adme_main")


def parse_args() -> tuple[argparse.Namespace, str]:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="ADME Strategy Copilot - 临床前 ADME 策略分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整分析
  python main.py --drug-name Ibrutinib --species Rat --focus MetID
  
  # 指定 SMILES
  python main.py --drug-name "My Drug" --smiles "CCO" --species Rat
  
  # 不同报告模式
  python main.py --drug-name Aspirin --report-mode executive
  
  # 交互式模式
  python main.py --interactive
  
  # 查看支持的功能
  python main.py --list-features
"""
    )
    
    # 位置参数
    parser.add_argument("--drug-name", "-d", default="Ibrutinib", help="化合物名称")
    
    # 可选参数
    parser.add_argument("--smiles", "-s", default="", help="SMILES 结构字符串")
    parser.add_argument("--species", default="Rat", 
                        choices=["Rat", "Human", "Dog", "Mouse"],
                        help="实验物种 (默认: Rat)")
    parser.add_argument("--focus", "-f", default="MetID",
                        choices=["MetID", "PK", "BA", "All"],
                        help="ADME 关注领域 (默认: MetID)")
    parser.add_argument("--report-mode", "-m", default="scientist",
                        choices=["scientist", "executive", "cro_proposal", "regulatory_prep"],
                        help="报告模式 (默认: scientist)")
    
    # 模式选择
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="启动交互式 CLI 模式")
    parser.add_argument("--list-features", action="store_true",
                        help="列出所有支持的功能")
    
    # 输出选项
    parser.add_argument("--output-json", "-o", action="store_true",
                        help="以 JSON 格式输出结果")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="安静模式，减少输出")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    
    args = parser.parse_args()
    
    # 确定运行模式
    if args.interactive:
        mode = "interactive"
    elif args.list_features:
        mode = "list"
    else:
        mode = "cli"
    
    return args, mode


def build_lead_agent(verbose: bool = True) -> LeadAgent:
    """构建 LeadAgent 实例"""
    config = get_config()
    skill_loader = SkillLoader(
        primary_dir=config.openclaw_skills_dir,
        fallback_dir=config.project_skills_dir,
    )
    
    agent = LeadAgent(
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
    
    return agent


def run_analysis(request: ADMERequest, verbose: bool = True) -> dict:
    """运行分析并返回结果"""
    callback_manager = CallbackManager()
    
    if verbose:
        callback = create_console_callback(verbose=True)
        callback_manager.add_callback(callback)
    
    # 触发开始事件
    callback_manager.emit(PipelineEvent.START, {"request": str(request)})
    
    try:
        # 构建并运行 Agent
        lead_agent = build_lead_agent(verbose=verbose)
        
        # 触发各阶段事件
        callback_manager.emit(PipelineEvent.SKILL_LOADED, {
            "skills": list(lead_agent.skill_loader._loaded_documents.keys()) if hasattr(lead_agent.skill_loader, '_loaded_documents') else []
        })
        
        callback_manager.emit(PipelineEvent.CHEMISTRY_START)
        chemistry = lead_agent.chemistry_agent.run(request)
        callback_manager.emit(PipelineEvent.CHEMISTRY_COMPLETE, {
            "rdkit_used": chemistry.rdkit_used,
            "smiles_valid": chemistry.smiles_valid
        })
        
        callback_manager.emit(PipelineEvent.METABOLISM_START)
        metabolism = lead_agent.metabolism_agent.run(request=request, chemistry=chemistry)
        callback_manager.emit(PipelineEvent.METABOLISM_COMPLETE, {
            "pathways": metabolism.pathways
        })
        
        callback_manager.emit(PipelineEvent.LITERATURE_START)
        placeholder_metabolism = metabolism
        literature_search = lead_agent.literature_agent.run(
            request=request, 
            metabolism=placeholder_metabolism
        )
        callback_manager.emit(PipelineEvent.LITERATURE_COMPLETE, {
            "count": len(literature_search.records),
            "provider": literature_search.provider_used
        })
        
        callback_manager.emit(PipelineEvent.LINKING_START)
        lead_agent._apply_linking(
            request=request,
            chemistry=chemistry,
            literature_search=literature_search
        )
        callback_manager.emit(PipelineEvent.LINKING_COMPLETE, {
            "linked_hotspots": len(chemistry.hotspot_priorities) if chemistry.hotspot_priorities else 0
        })
        
        # 重新运行代谢（带链接信息）
        metabolism = lead_agent.metabolism_agent.run(request=request, chemistry=chemistry)
        
        callback_manager.emit(PipelineEvent.PROTOCOL_START)
        protocol = lead_agent.protocol_design_agent.run(
            request=request, 
            metabolism=metabolism, 
            chemistry=chemistry
        )
        callback_manager.emit(PipelineEvent.PROTOCOL_COMPLETE, {
            "in_vitro_count": len(protocol.in_vitro)
        })
        
        callback_manager.emit(PipelineEvent.SYNTHESIS_START)
        report = lead_agent.synthesis_agent.run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature_search,
            skill_sources={}
        )
        callback_manager.emit(PipelineEvent.SYNTHESIS_COMPLETE, {
            "mode": request.report_mode
        })
        
        callback_manager.emit(PipelineEvent.REPORT_WRITE, {
            "path": str(lead_agent.report_generator.reports_dir)
        })
        
        report_path = lead_agent.report_generator.write_report(request=request, report=report)
        
        callback_manager.emit(PipelineEvent.COMPLETE)
        
        return {
            "report_path": str(report_path),
            "report_mode": request.report_mode,
            "rdkit_used": chemistry.rdkit_used,
            "smiles_valid": chemistry.smiles_valid,
            "cyp_flags": metabolism.cyp_flags,
            "clearance_risk": metabolism.clearance_risk,
            "primary_provider": literature_search.primary_provider,
            "provider_used": literature_search.provider_used,
            "literature_count": len(literature_search.records),
            "hotspots": len(chemistry.hotspot_priorities) if chemistry.hotspot_priorities else 0
        }
        
    except Exception as e:
        callback_manager.emit(PipelineEvent.ERROR, {"error": str(e)})
        raise


def list_features():
    """列出所有支持的功能"""
    features = {
        "species": {
            "Rat": "大鼠 - 最常用的临床前模型",
            "Human": "人 - 人体翻译预测",
            "Dog": "犬 - 中等体型动物模型",
            "Mouse": "小鼠 - 基因工程模型"
        },
        "focus_areas": {
            "MetID": "代谢物鉴定 - 代谢通路和代谢物结构分析",
            "PK": "药代动力学 - 吸收、分布、消除动力学",
            "BA": "生物利用度 - 生物利用度优化和预测",
            "All": "全面分析 - 综合所有 ADME 领域"
        },
        "report_modes": {
            "scientist": "科学家模式 - 完整技术视图",
            "executive": "高管模式 - 决策备忘录",
            "cro_proposal": "CRO提案模式 - 工作包导向",
            "regulatory_prep": "监管准备模式 - 保守不确定性导向"
        },
        "commands": {
            "analyze": "完整 ADME 分析",
            "chemistry": "化学结构分析",
            "metabolism": "代谢预测",
            "literature": "文献检索",
            "protocol": "方案设计"
        }
    }
    
    print("\n" + "="*60)
    print("  ADME Strategy Copilot - 支持的功能")
    print("="*60 + "\n")
    
    print("📊 实验物种:")
    for key, desc in features["species"].items():
        print(f"  {key:10} - {desc}")
    
    print("\n🔬 ADME 关注领域:")
    for key, desc in features["focus_areas"].items():
        print(f"  {key:10} - {desc}")
    
    print("\n📋 报告模式:")
    for key, desc in features["report_modes"].items():
        print(f"  {key:18} - {desc}")
    
    print("\n🛠️ 交互式命令:")
    for key, desc in features["commands"].items():
        print(f"  {key:15} - {desc}")
    
    print("\n" + "="*60)


def main() -> None:
    """主入口"""
    args, mode = parse_args()
    
    if mode == "interactive":
        # 启动交互式模式
        from interactive_cli import start_interactive_mode
        start_interactive_mode()
        return
    
    if mode == "list":
        list_features()
        return
    
    # CLI 模式
    verbose = not args.quiet
    
    if verbose:
        print("\n" + "="*60)
        print("  ADME Strategy Copilot")
        print("="*60)
        print(f"  化合物: {args.drug_name}")
        print(f"  物种:   {args.species}")
        print(f"  关注:   {args.focus}")
        print(f"  模式:   {args.report_mode}")
        print("="*60 + "\n")
    
    request = ADMERequest(
        drug_name=args.drug_name,
        smiles=args.smiles,
        species=args.species,
        focus=args.focus,
        report_mode=args.report_mode,
    )
    
    try:
        result = run_analysis(request, verbose=verbose)
        
        if verbose:
            print("\n" + "="*60)
            print("  ✅ 分析完成")
            print("="*60)
        
        if args.output_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"📄 报告路径: {result['report_path']}")
            print(f"📊 文献来源: {result['provider_used']}")
            print(f"🔬 CYP 标志: {', '.join(result['cyp_flags']) if result['cyp_flags'] else '无'}")
            print(f"⚠️  清除风险: {result['clearance_risk']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
