"""
ADME Strategy Copilot 交互式 CLI

提供对话式交互界面，支持多轮问答和实时反馈。
"""

from __future__ import annotations

import sys
import json
import cmd
import shlex
from pathlib import Path
from typing import Optional, Dict, Any, List

# 确保项目路径在 sys.path 中
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.models import ADMERequest
from utils.callbacks import ConsoleProgressCallback, create_console_callback
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
from app.config import get_config


class ADMEInteractiveCLI(cmd.Cmd):
    """ADME Strategy Copilot 交互式 CLI"""
    
    intro = """
╔══════════════════════════════════════════════════════════════════╗
║           ADME Strategy Copilot - 交互式模式                      ║
║                                                                      ║
║  输入命令或化合物名称开始分析。支持以下命令:                           ║
║    analyze <化合物名> [--smiles SMILES] [--species SPECIES]          ║
║    chemistry <化合物名> [--smiles SMILES]                            ║
║    metabolism <化合物名> [--smiles SMILES] [--species SPECIES]       ║
║    literature <化合物名> [--species SPECIES] [--max N]               ║
║    protocol <化合物名> [--smiles SMILES] [--species SPECIES]        ║
║    history                    - 显示分析历史                          ║
║    clear                      - 清屏                                 ║
║    help                       - 显示帮助                             ║
║    exit                       - 退出                                 ║
╚══════════════════════════════════════════════════════════════════╝
"""
    prompt = "(ADME) "
    file = None
    
    def __init__(self):
        super().__init__()
        self.history: List[Dict[str, Any]] = []
        self.current_drug: Optional[str] = None
        self.current_result: Optional[Dict[str, Any]] = None
        self.callback = create_console_callback(verbose=False)
        self._init_agents()
    
    def _init_agents(self):
        """初始化 Agent"""
        config = get_config()
        skill_loader = SkillLoader(
            primary_dir=config.openclaw_skills_dir,
            fallback_dir=config.project_skills_dir,
        )
        
        self.lead_agent = LeadAgent(
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
    
    def _create_request(self, drug_name: str, **kwargs) -> ADMERequest:
        """创建请求对象"""
        return ADMERequest(
            drug_name=drug_name,
            smiles=kwargs.get("smiles", ""),
            species=kwargs.get("species", "Rat"),
            focus=kwargs.get("focus", "MetID"),
            report_mode=kwargs.get("report_mode", "scientist")
        )
    
    def _add_to_history(self, command: str, result: Dict[str, Any]):
        """添加到历史"""
        self.history.append({
            "command": command,
            "result": result,
            "drug_name": self.current_drug
        })
        # 只保留最近 50 条
        if len(self.history) > 50:
            self.history = self.history[-50:]
    
    def _print_result(self, result: Dict[str, Any], title: str = "结果"):
        """打印结果"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print('='*60 + "\n")
    
    # ========== 命令处理 ==========
    
    def do_analyze(self, arg: str):
        """analyze <化合物名> [--smiles SMILES] [--species SPECIES] [--focus FOCUS] [--mode MODE]"""
        args = self._parse_args(arg)
        if not args:
            return
        
        drug_name = args.get("drug_name", "")
        if not drug_name:
            print("❌ 请提供化合物名称")
            return
        
        print(f"\n🔬 正在分析化合物: {drug_name}")
        
        try:
            request = self._create_request(
                drug_name=drug_name,
                smiles=args.get("smiles", ""),
                species=args.get("species", "Rat"),
                focus=args.get("focus", "MetID"),
                report_mode=args.get("mode", "scientist")
            )
            
            self.current_drug = drug_name
            result = self.lead_agent.run(request)
            
            self.current_result = {
                "drug_name": drug_name,
                "report_path": str(result.report_path),
                "smiles_valid": result.chemistry.smiles_valid,
                "rdkit_used": result.chemistry.rdkit_used,
                "cyp_flags": result.metabolism.cyp_flags,
                "clearance_risk": result.metabolism.clearance_risk,
                "pathways": result.metabolism.pathways,
                "literature_count": len(result.literature)
            }
            
            self._print_result(self.current_result, f"分析结果: {drug_name}")
            self._add_to_history(f"analyze {drug_name}", self.current_result)
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    def do_chemistry(self, arg: str):
        """chemistry <化合物名> [--smiles SMILES]"""
        args = self._parse_args(arg)
        if not args:
            return
        
        drug_name = args.get("drug_name", "")
        if not drug_name:
            print("❌ 请提供化合物名称")
            return
        
        print(f"\n🧪 正在分析化学结构: {drug_name}")
        
        try:
            chemistry_agent = ChemistryAgent(chemistry_service=ChemistryService())
            request = self._create_request(drug_name=drug_name, smiles=args.get("smiles", ""))
            chemistry = chemistry_agent.run(request)
            
            result = {
                "smiles_valid": chemistry.smiles_valid,
                "rdkit_used": chemistry.rdkit_used,
                "molecular_weight": chemistry.molecular_weight,
                "molecular_formula": chemistry.molecular_formula,
                "phase1_liabilities": chemistry.phase1_liabilities or [],
                "phase2_liabilities": chemistry.phase2_liabilities or [],
                "cyp_preference_hints": chemistry.cyp_preference_hints or []
            }
            
            self._print_result(result, f"化学分析: {drug_name}")
            self._add_to_history(f"chemistry {drug_name}", result)
            
        except Exception as e:
            print(f"❌ 化学分析失败: {e}")
    
    def do_metabolism(self, arg: str):
        """metabolism <化合物名> [--smiles SMILES] [--species SPECIES]"""
        args = self._parse_args(arg)
        if not args:
            return
        
        drug_name = args.get("drug_name", "")
        if not drug_name:
            print("❌ 请提供化合物名称")
            return
        
        print(f"\n⚗️ 正在预测代谢: {drug_name}")
        
        try:
            chemistry_agent = ChemistryAgent(chemistry_service=ChemistryService())
            metabolism_agent = MetabolismPredictionAgent()
            
            request = self._create_request(
                drug_name=drug_name,
                smiles=args.get("smiles", ""),
                species=args.get("species", "Rat")
            )
            
            chemistry = chemistry_agent.run(request)
            metabolism = metabolism_agent.run(request=request, chemistry=chemistry)
            
            result = {
                "pathways": metabolism.pathways,
                "warnings": metabolism.warnings,
                "cyp_flags": metabolism.cyp_flags,
                "clearance_risk": metabolism.clearance_risk,
                "reactive_metabolite_risk": metabolism.reactive_metabolite_risk
            }
            
            self._print_result(result, f"代谢预测: {drug_name}")
            self._add_to_history(f"metabolism {drug_name}", result)
            
        except Exception as e:
            print(f"❌ 代谢预测失败: {e}")
    
    def do_literature(self, arg: str):
        """literature <化合物名> [--species SPECIES] [--max N]"""
        args = self._parse_args(arg)
        if not args:
            return
        
        drug_name = args.get("drug_name", "")
        if not drug_name:
            print("❌ 请提供化合物名称")
            return
        
        print(f"\n📖 正在搜索文献: {drug_name}")
        
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
                default_max_results=int(args.get("max", 5)),
            )
            
            literature_agent = LiteratureAgent(literature_service=literature_service)
            metabolism_agent = MetabolismPredictionAgent()
            
            request = self._create_request(
                drug_name=drug_name,
                species=args.get("species", "Rat")
            )
            
            placeholder_metabolism = metabolism_agent.run(request=request, chemistry=None)
            literature_search = literature_agent.run(request=request, metabolism=placeholder_metabolism)
            
            records = [{
                "title": r.title,
                "year": r.year,
                "score": r.final_score,
                "evidence_bucket": r.evidence_bucket
            } for r in literature_search.records]
            
            result = {
                "provider": literature_search.provider_used,
                "count": len(records),
                "records": records
            }
            
            self._print_result(result, f"文献搜索: {drug_name}")
            self._add_to_history(f"literature {drug_name}", result)
            
        except Exception as e:
            print(f"❌ 文献搜索失败: {e}")
    
    def do_protocol(self, arg: str):
        """protocol <化合物名> [--smiles SMILES] [--species SPECIES]"""
        args = self._parse_args(arg)
        if not args:
            return
        
        drug_name = args.get("drug_name", "")
        if not drug_name:
            print("❌ 请提供化合物名称")
            return
        
        print(f"\n📋 正在设计方案: {drug_name}")
        
        try:
            chemistry_agent = ChemistryAgent(chemistry_service=ChemistryService())
            metabolism_agent = MetabolismPredictionAgent()
            protocol_agent = ProtocolDesignAgent()
            
            request = self._create_request(
                drug_name=drug_name,
                smiles=args.get("smiles", ""),
                species=args.get("species", "Rat")
            )
            
            chemistry = chemistry_agent.run(request)
            metabolism = metabolism_agent.run(request=request, chemistry=chemistry)
            protocol = protocol_agent.run(request=request, metabolism=metabolism, chemistry=chemistry)
            
            result = {
                "in_vitro": protocol.in_vitro,
                "in_vivo": protocol.in_vivo,
                "translation": protocol.translation,
                "risk_flags": protocol.risk_flags
            }
            
            self._print_result(result, f"研究方案: {drug_name}")
            self._add_to_history(f"protocol {drug_name}", result)
            
        except Exception as e:
            print(f"❌ 方案设计失败: {e}")
    
    def do_history(self, arg: str):
        """显示分析历史"""
        if not self.history:
            print("📭 暂无历史记录")
            return
        
        print("\n📜 分析历史:")
        print('-' * 40)
        for i, item in enumerate(reversed(self.history[-10:]), 1):
            drug = item.get("drug_name", "Unknown")
            cmd = item.get("command", "")[:30]
            print(f"  {i}. {drug}: {cmd}")
        print('-' * 40)
    
    def do_status(self, arg: str):
        """显示当前状态"""
        if self.current_drug:
            print(f"\n📌 当前化合物: {self.current_drug}")
            if self.current_result:
                print(f"   SMILES 有效: {self.current_result.get('smiles_valid', False)}")
                print(f"   代谢途径: {len(self.current_result.get('pathways', []))} 条")
                print(f"   CYP 标志: {self.current_result.get('cyp_flags', [])}")
        else:
            print("📌 当前化合物: 无")
    
    def do_clear(self, arg: str):
        """清屏"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_exit(self, arg: str):
        """退出"""
        print("\n👋 再见!")
        return True
    
    def do_quit(self, arg: str):
        """退出 (alias for exit)"""
        return self.do_exit(arg)
    
    # ========== 快捷方式 ==========
    
    def default(self, line: str):
        """处理非命令输入 - 当作化合物名分析"""
        if line.strip():
            # 尝试直接分析输入的化合物
            self.do_analyze(line)
    
    # ========== 辅助函数 ==========
    
    def _parse_args(self, arg: str) -> Dict[str, str]:
        """解析命令参数"""
        result = {"drug_name": ""}
        
        if not arg.strip():
            return result
        
        try:
            # 使用 shlex 正确处理引号
            parts = shlex.split(arg)
            
            for i, part in enumerate(parts):
                if part.startswith("--"):
                    key = part[2:]
                    if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                        result[key] = parts[i + 1]
                    else:
                        result[key] = "true"
                elif not result["drug_name"]:
                    result["drug_name"] = part
                    
        except ValueError:
            # 如果 shlex 失败，使用简单解析
            parts = arg.split()
            if parts:
                result["drug_name"] = parts[0]
                # 简单的 --key value 解析
                i = 1
                while i < len(parts):
                    if parts[i].startswith("--") and i + 1 < len(parts):
                        result[parts[i][2:]] = parts[i + 1]
                        i += 2
                    else:
                        i += 1
        
        return result
    
    def do_help(self, arg: str):
        """显示帮助"""
        help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                     ADME Strategy Copilot 帮助                    ║
╚══════════════════════════════════════════════════════════════════╝

命令格式: command [compound] [--option value]

┌─────────────────────────────────────────────────────────────────┐
│  分析命令                                                          │
├─────────────────────────────────────────────────────────────────┤
│  analyze <化合物> [--smiles SMILES] [--species Rat]             │
│    完整 ADME 分析，生成完整报告                                    │
│                                                                   │
│  chemistry <化合物> [--smiles SMILES]                             │
│    仅分析化学结构特征                                              │
│                                                                   │
│  metabolism <化合物> [--smiles SMILES] [--species Rat]           │
│    预测代谢途径和风险                                              │
│                                                                   │
│  literature <化合物> [--species Rat] [--max 5]                  │
│    搜索相关文献                                                    │
│                                                                   │
│  protocol <化合物> [--smiles SMILES] [--species Rat]             │
│    设计预临床研究方案                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  工具命令                                                          │
├─────────────────────────────────────────────────────────────────┤
│  history    - 显示最近 10 条分析历史                               │
│  status     - 显示当前化合物状态                                   │
│  clear      - 清屏                                                │
│  help       - 显示此帮助                                          │
│  exit/quit  - 退出                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  示例                                                              │
├─────────────────────────────────────────────────────────────────┤
│  analyze Ibrutinib --smiles "CC(C)(C)C1=C2C=C(C=C2C(=O)N1CC3..." │
│  chemistry Aspirin                                                  │
│  metabolism Warfarin --species Human                              │
│  literature Imatinib --max 10                                     │
└─────────────────────────────────────────────────────────────────┘
"""
        print(help_text)


def start_interactive_mode():
    """启动交互式模式"""
    print("启动交互式 CLI...")
    cli = ADMEInteractiveCLI()
    cli.cmdloop()


if __name__ == "__main__":
    start_interactive_mode()
