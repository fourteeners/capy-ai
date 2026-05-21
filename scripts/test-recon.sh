#!/bin/bash
# ============================================================
# CAPY BUG HUNTER — Recon Sub-Agent Test
# ============================================================
# Tests the recon sub-agent (Aegis) end-to-end.
# Requires: Hermes fleet running, target specified or defaults to test target.
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo -e "${YELLOW}Usage: $0 <target-domain>${NC}"
    echo -e "Example: $0 example.com"
    echo ""
    echo -e "${RED}WARNING: Only test targets you own or have explicit permission to test.${NC}"
    exit 1
fi

echo -e "${BLUE}⛏️  CAPY Recon Test — Target: $TARGET${NC}"
echo -e "${YELLOW}This will run a non-intrusive reconnaissance against $TARGET${NC}"
echo ""

# Check fleet is running
echo -e "${YELLOW}[1/3] Checking fleet status...${NC}"
if ! curl -s "http://localhost:8646/v1/models" >/dev/null 2>&1; then
    echo -e "${RED}✗ Ares (Execution) agent not reachable on port 8646.${NC}"
    echo -e "${YELLOW}  Make sure the fleet is running: ./launch-fleet.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ares agent online${NC}"

# Run recon via Athena → Ares delegation
echo -e "${YELLOW}[2/3] Delegating recon to Ares (Aegis)...${NC}"

RESPONSE=$(curl -s -X POST "http://localhost:8643/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer sk-athena-bughunter-ceo-2025" \
    -d '{
        "model": "athena",
        "messages": [
            {
                "role": "system",
                "content": "You are Athena, CEO orchestrator of CAPY Bug Hunter. Communicate in caveman lite mode. Delegate recon tasks to Ares."
            },
            {
                "role": "user",
                "content": "Run quick recon on target: '"$TARGET"'. Passive + active (rate limit: 5 req/s). Subdomain enum, HTTP probing, tech fingerprint, JS analysis. Export results."
            }
        ],
        "max_tokens": 2000
    }' 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to communicate with Athena${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Recon delegation sent${NC}"
echo ""

# Display response
echo -e "${BLUE}══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Athena Response:${NC}"
echo -e "${BLUE}══════════════════════════════════════════════${NC}"
echo "$RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    content = data.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
    print(content)
except:
    print(sys.stdin.read())
" 2>/dev/null || echo "$RESPONSE"

echo ""
echo -e "${YELLOW}[3/3] Check audit log for results:${NC}"
echo -e "  cat audit-log/sessions/HUNT-*.jsonl | tail -20"
echo ""
echo -e "${GREEN}Recon test complete. Check Ares gateway logs for detailed output:${NC}"
echo -e "  docker compose -f docker/docker-compose.yml logs hermes | grep ares"
