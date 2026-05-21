#!/bin/bash
# ============================================================
# CAPY BUG HUNTER — Fleet Launch Script
# ============================================================
# Launches the full multi-agent fleet via Docker Compose.
# Prerequisites: Docker, Docker Compose v2, LLM API keys in .env
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_DIR/docker"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  ⛏️  CAPY BUG HUNTER — Multi-Agent Bug Bounty Fleet     ║"
    echo "║  Hermes Orchestrator · Athena · Prometheus · Odysseus · Ares ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_prerequisites() {
    echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

    if ! command -v docker &>/dev/null; then
        echo -e "${RED}ERROR: Docker not found. Please install Docker.${NC}"
        exit 1
    fi

    if ! docker compose version &>/dev/null; then
        echo -e "${RED}ERROR: Docker Compose v2 not found.${NC}"
        exit 1
    fi

    if [ ! -f "$PROJECT_DIR/hermes/config/.env" ]; then
        echo -e "${YELLOW}WARNING: .env not found. Creating from .env.example...${NC}"
        cp "$PROJECT_DIR/hermes/config/.env.example" "$PROJECT_DIR/hermes/config/.env"
        echo -e "${RED}Please edit hermes/config/.env with your API keys before continuing.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Prerequisites met${NC}"
}

setup_directories() {
    echo -e "${YELLOW}[2/5] Setting up directories...${NC}"

    mkdir -p "$PROJECT_DIR/hermes/profiles"
    mkdir -p "$PROJECT_DIR/hermes/memory"
    mkdir -p "$PROJECT_DIR/hermes/kb"
    mkdir -p "$PROJECT_DIR/audit-log/sessions"
    mkdir -p "$PROJECT_DIR/audit-log/findings"
    mkdir -p "$PROJECT_DIR/audit-log/actions"

    echo -e "${GREEN}✓ Directories ready${NC}"
}

copy_configs() {
    echo -e "${YELLOW}[3/5] Copying configurations...${NC}"

    # Ensure run_agents.sh is executable
    chmod +x "$PROJECT_DIR/hermes/config/run_agents.sh"

    echo -e "${GREEN}✓ Configurations ready${NC}"
}

start_fleet() {
    echo -e "${YELLOW}[4/5] Starting fleet...${NC}"

    cd "$DOCKER_DIR"

    # Source .env for Docker Compose
    set -a
    source "$PROJECT_DIR/hermes/config/.env" 2>/dev/null || true
    set +a

    docker compose up -d

    echo -e "${GREEN}✓ Fleet containers started${NC}"
}

wait_for_ready() {
    echo -e "${YELLOW}[5/5] Waiting for agents to be ready...${NC}"

    local agents=(
        "8643:Athena (Orchestrator)"
        "8644:Prometheus (RnD)"
        "8645:Odysseus (Strategy)"
        "8646:Ares (Execution)"
    )

    local max_wait=60
    local waited=0

    for agent in "${agents[@]}"; do
        local port="${agent%%:*}"
        local name="${agent##*:}"

        while ! curl -s "http://localhost:$port/v1/models" >/dev/null 2>&1; do
            if [ $waited -ge $max_wait ]; then
                echo -e "${RED}  ✗ $name timed out after ${max_wait}s${NC}"
                break
            fi
            sleep 2
            waited=$((waited + 2))
        done

        if [ $waited -lt $max_wait ]; then
            echo -e "${GREEN}  ✓ $name ready on port $port${NC}"
        fi
    done
}

show_status() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  🛡️  FLEET OPERATIONAL${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${BLUE}Agent Endpoints:${NC}"
    echo -e "    Athena (CEO):         http://localhost:8643/v1"
    echo -e "    Prometheus (RnD):     http://localhost:8644/v1"
    echo -e "    Odysseus (Strategy):  http://localhost:8645/v1"
    echo -e "    Ares (Execution):     http://localhost:8646/v1"
    echo ""
    echo -e "  ${BLUE}Web UI:${NC}  http://localhost:3000"
    echo ""
    echo -e "  ${BLUE}Quick commands:${NC}"
    echo -e "    hermes -p athena \"Scan hackerone program: example.com\""
    echo -e "    hermes -p athena \"Research: JWT algorithm confusion\""
    echo -e "    hermes -p athena \"Status report\""
    echo ""
    echo -e "  ${YELLOW}Stop fleet:${NC} cd docker && docker compose down"
    echo -e "  ${YELLOW}View logs:${NC}  cd docker && docker compose logs -f hermes"
    echo ""
}

# --- Main ---
banner
check_prerequisites
setup_directories
copy_configs
start_fleet
wait_for_ready
show_status
