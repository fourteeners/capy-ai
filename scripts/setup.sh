#!/bin/bash
# ============================================================
# CAPY BUG HUNTER — Initial Setup Script
# ============================================================
# Installs Hermes Agent, security tools, and configures the
# multi-agent system for first use.
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}⛏️  CAPY Bug Hunter — Initial Setup${NC}\n"

# --- Step 1: Install Hermes Agent ---
echo -e "${YELLOW}[1/4] Installing Hermes Agent...${NC}"
if command -v hermes &>/dev/null; then
    echo -e "${GREEN}  ✓ Hermes already installed: $(hermes --version 2>/dev/null || echo 'unknown')${NC}"
else
    pip install hermes-agent
    echo -e "${GREEN}  ✓ Hermes Agent installed${NC}"
fi

# --- Step 2: Install Security Tools ---
echo -e "${YELLOW}[2/4] Installing security tools...${NC}"

# Go-based tools
if command -v go &>/dev/null; then
    echo "  Installing Go tools..."
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || echo "  ⚠ subfinder skipped (already installed or Go not configured)"
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || echo "  ⚠ httpx skipped"
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null || echo "  ⚠ nuclei skipped"
    go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest 2>/dev/null || echo "  ⚠ dnsx skipped"
    go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest 2>/dev/null || echo "  ⚠ naabu skipped"
    go install github.com/projectdiscovery/katana/cmd/katana@latest 2>/dev/null || echo "  ⚠ katana skipped"
    go install github.com/ffuf/ffuf/v2@latest 2>/dev/null || echo "  ⚠ ffuf skipped"
    go install github.com/hahwul/dalfox/v2@latest 2>/dev/null || echo "  ⚠ dalfox skipped"
    go install github.com/OWASP/Amass/v4/...@latest 2>/dev/null || echo "  ⚠ amass skipped"
    echo -e "${GREEN}  ✓ Go tools installed${NC}"
else
    echo -e "${YELLOW}  ⚠ Go not found — skipping Go-based tools. Install Go 1.21+ for full tool suite.${NC}"
fi

# Python-based tools
echo "  Installing Python tools..."
pip install sqlmap 2>/dev/null || echo "  ⚠ sqlmap skipped"
pip install arjun 2>/dev/null || echo "  ⚠ arjun skipped"
pip install tplmap 2>/dev/null || echo "  ⚠ tplmap skipped"

# Web3 tools
if command -v pip &>/dev/null; then
    pip install slither-analyzer 2>/dev/null || echo "  ⚠ slither skipped (needs solc)"
    pip install mythril 2>/dev/null || echo "  ⚠ mythril skipped"
fi

if command -v foundryup &>/dev/null || command -v forge &>/dev/null; then
    echo "  ✓ Foundry detected"
else
    echo -e "${YELLOW}  ⚠ Foundry not found — install for Web3 testing: curl -L https://foundry.paradigm.xyz | bash${NC}"
fi

echo -e "${GREEN}  ✓ Python tools installed${NC}"

# --- Step 3: Configure Environment ---
echo -e "${YELLOW}[3/4] Configuring environment...${NC}"

if [ ! -f ../hermes/config/.env ]; then
    cp ../hermes/config/.env.example ../hermes/config/.env
    echo -e "${YELLOW}  ⚠ Created .env from example. Edit ../hermes/config/.env with your API keys.${NC}"
else
    echo -e "${GREEN}  ✓ .env already exists${NC}"
fi

# --- Step 4: Verify ---
echo -e "${YELLOW}[4/4] Verifying setup...${NC}"

echo "  Hermes Agent: $(command -v hermes && echo '✓' || echo '✗ not found')"
echo "  Go tools: $(command -v subfinder && echo '✓' || echo '⚠ some missing')"
echo "  SQLMap: $(command -v sqlmap && echo '✓' || echo '⚠ not found')"
echo "  Nuclei: $(command -v nuclei && echo '✓' || echo '⚠ not found')"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""
echo "  Next steps:"
echo "  1. Edit hermes/config/.env with your LLM API keys"
echo "  2. Run: ./launch-fleet.sh"
echo "  3. Start hunting: hermes -p athena 'Scan example.com'"
echo ""
