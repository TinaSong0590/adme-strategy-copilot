#!/bin/bash
# ADME Strategy Copilot 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ADME Strategy Copilot 启动器${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Python 版本
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
echo -e "${YELLOW}Python 版本:${NC} $python_version"

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"
if python3 -c "import rdkit" 2>/dev/null; then
    echo -e "  RDKit: ${GREEN}已安装${NC}"
else
    echo -e "  RDKit: ${YELLOW}未安装 (可选)${NC}"
fi

if python3 -c "import requests" 2>/dev/null; then
    echo -e "  requests: ${GREEN}已安装${NC}"
else
    echo -e "  requests: ${YELLOW}未安装${NC}"
    echo -e "${RED}请运行: pip install requests${NC}"
    exit 1
fi

# 检查 MCP
if python3 -c "import mcp" 2>/dev/null || python3 -c "import fastmcp" 2>/dev/null; then
    echo -e "  MCP: ${GREEN}已安装${NC}"
else
    echo -e "  MCP: ${YELLOW}未安装 (可选)${NC}"
fi

echo ""

# 显示使用选项
echo -e "${GREEN}使用选项:${NC}"
echo "  1. CLI 模式 - 单次分析"
echo "  2. 交互式模式 - 多轮对话"
echo "  3. MCP 服务器 - AI 工具集成"
echo "  4. 列出功能"
echo "  5. 帮助"
echo ""

read -p "请选择模式 (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}CLI 模式 - 请输入参数:${NC}"
        read -p "化合物名称 (默认: Ibrutinib): " drug_name
        read -p "SMILES (可选): " smiles
        read -p "物种 (Rat/Human/Dog/Mouse, 默认: Rat): " species
        read -p "关注领域 (MetID/PK/BA/All, 默认: MetID): " focus
        
        drug_name=${drug_name:-Ibrutinib}
        species=${species:-Rat}
        focus=${focus:-MetID}
        
        cmd="python3 main.py --drug-name \"$drug_name\" --species $species --focus $focus"
        if [ -n "$smiles" ]; then
            cmd="$cmd --smiles \"$smiles\""
        fi
        
        echo ""
        echo -e "${YELLOW}执行: $cmd${NC}"
        eval $cmd
        ;;
    2)
        echo ""
        echo -e "${YELLOW}启动交互式模式...${NC}"
        python3 interactive_cli.py
        ;;
    3)
        echo ""
        echo -e "${YELLOW}启动 MCP 服务器...${NC}"
        python3 mcp_server.py
        ;;
    4)
        echo ""
        python3 main.py --list-features
        ;;
    5)
        echo ""
        echo "========================================"
        echo "帮助信息"
        echo "========================================"
        echo ""
        echo "基本用法:"
        echo "  python3 main.py --drug-name COMPOUND [--options]"
        echo ""
        echo "示例:"
        echo "  python3 main.py -d Aspirin"
        echo "  python3 main.py -d 'My Drug' -s 'CCO' --species Human"
        echo "  python3 main.py -d Warfarin -m executive"
        echo ""
        echo "交互式模式:"
        echo "  python3 interactive_cli.py"
        echo ""
        echo "MCP 服务器:"
        echo "  python3 mcp_server.py"
        echo ""
        ;;
    *)
        echo -e "${RED}无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}再见!${NC}"
