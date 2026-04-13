"""
ADME Strategy Copilot

临床前 ADME 策略分析工具，支持多源文献检索、化学智能和智能方案设计。

主要模块:
- agents: Agent 实现 (LeadAgent, ChemistryAgent, LiteratureAgent 等)
- services: 服务层 (ChemistryService, LiteratureService, ReportGenerator 等)
- utils: 工具函数 (models, callbacks, cache)
- app: 应用配置

使用方式:
    # CLI 模式
    python main.py --drug-name Ibrutinib --species Rat
    
    # 交互式模式
    python interactive_cli.py
    
    # MCP 服务器
    python mcp_server.py
"""

__version__ = "1.0.0"
__author__ = "ADME Strategy Team"

from utils.models import ADMERequest, PipelineResult
