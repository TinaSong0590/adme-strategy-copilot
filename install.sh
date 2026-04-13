#!/bin/bash
# Install script for ADME Strategy Copilot
# This script handles RDKit installation which varies by Python version

set -e

echo "========================================"
echo "ADME Strategy Copilot - Installation"
echo "========================================"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Detected Python version: $PYTHON_VERSION"

# Install core dependencies
echo ""
echo "[1/3] Installing core dependencies..."
pip install -q python-dotenv>=1.0 requests>=2.31

# Install optional dependencies
echo ""
echo "[2/3] Installing optional dependencies..."
pip install -q fastmcp>=0.1.0 rich>=13.7.0 typer>=0.9.0

# Try to install LLM integration (optional)
pip install -q langchain>=0.3.0 langchain-core>=0.3.0 langchain-openai>=0.2.0 2>/dev/null || true

# RDKit installation
echo ""
echo "[3/3] Checking RDKit installation..."

if python3 -c "from rdkit import Chem" 2>/dev/null; then
    echo "  ✓ RDKit is already installed"
else
    echo "  ✗ RDKit is not installed"
    echo ""
    echo "  RDKit requires conda for Python 3.12+. Options:"
    echo ""
    echo "  Option 1: Use conda (recommended for Python 3.12+)"
    echo "    conda install -c conda-forge rdkit -y"
    echo ""
    echo "  Option 2: For Python 3.8-3.11 only"
    echo "    pip install rdkit-pypi>=2022.9.5"
    echo ""
    echo "  Without RDKit, the system will use fallback heuristics."
    echo "  All core functionality will still work."
fi

echo ""
echo "========================================"
echo "Installation complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  python main.py --drug-name Ibrutinib --species Rat"
echo ""
echo "For interactive mode:"
echo "  python interactive_cli.py"
