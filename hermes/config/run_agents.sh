#!/bin/bash
# ============================================================
# CAPY BUG HUNTER — Multi-Agent Fleet Entrypoint
# ============================================================
# Runs BEFORE Hermes built-in entrypoint.
# Creates profiles from agents.yml, sets up shared infrastructure,
# then launches all active agent gateways with auto-restart.
# ============================================================

set -euo pipefail

AGENTS_YML="${HERMES_CONFIG_DIR:-/home/hermes/.hermes/config}/agents.yml"
AGENTS_DIR="/home/hermes/agents"
SKILLS_DIR="/home/hermes/.hermes/skills"
MEMORY_DIR="/home/hermes/.hermes/memory"
KB_DIR="/home/hermes/.hermes/kb"
LOG_DIR="/home/hermes/audit-log"

log() { echo "[CAPY-FLEET] $(date '+%Y-%m-%d %H:%M:%S') $*" >&2; }
warn() { echo "[CAPY-FLEET] ⚠️  $(date '+%Y-%m-%d %H:%M:%S') $*" >&2; }

# --- Pre-flight: verify minimal config ---
if [ ! -f "$AGENTS_YML" ]; then
    warn "agents.yml not found at $AGENTS_YML — fleet cannot start"
    exit 1
fi

# --- Ensure shared directories exist ---
mkdir -p "$MEMORY_DIR" "$KB_DIR" "$LOG_DIR/sessions" "$LOG_DIR/findings" "$LOG_DIR/actions"

# --- Initialize Knowledge Base if empty ---
if [ ! -f "$KB_DIR/index.md" ]; then
    log "Initializing Knowledge Base index..."
    cat > "$KB_DIR/index.md" << 'KBEOF'
# CAPY Bug Hunter — Knowledge Base

## Active Targets

*No targets yet — assign via Athena.*

## Vulnerability Patterns

### Web2
- See: /home/hermes/corpus/vulnerability-patterns/web2/

### Web3
- See: /home/hermes/corpus/vulnerability-patterns/web3/

## Learning Journal

*Auto-populated by Prometheus (RnD) after each hunt session.*

## Tool Registry

*Auto-populated as agents create/adapt tools.*

KBEOF
fi

# --- Parse agents.yml and create profiles ---
log "Parsing agent fleet from $AGENTS_YML..."

# Simple YAML parse — extract profile names and clone-from relationships
# In production this uses python/yq; here we parse the structure
PROFILES=$(grep -E '^[a-z]+:' "$AGENTS_YML" | grep -v '^#' | cut -d: -f1)

for profile in $PROFILES; do
    log "Setting up profile: $profile"

    # Check if profile already exists
    if hermes profile list 2>/dev/null | grep -q "^$profile$"; then
        log "  Profile '$profile' already exists — skipping creation"
    else
        CLONE_FROM=$(grep -A5 "^${profile}:" "$AGENTS_YML" | grep "clone-from:" | awk '{print $2}' || echo "false")

        if [ "$CLONE_FROM" = "false" ] || [ -z "$CLONE_FROM" ]; then
            hermes profile create "$profile" 2>/dev/null || log "  Created fresh profile: $profile"
        else
            hermes profile create "$profile" --clone-from "$CLONE_FROM" 2>/dev/null || \
                log "  Created profile: $profile (cloned from $CLONE_FROM)"
        fi
    fi

    # Inject personality file if specified
    PERSONALITY_FILE=$(grep -A20 "^${profile}:" "$AGENTS_YML" | grep "HERMES_PERSONALITY_FILE:" | awk '{print $2}' | tr -d '"' || echo "")
    if [ -n "$PERSONALITY_FILE" ] && [ -f "$PERSONALITY_FILE" ]; then
        log "  Personality file: $PERSONALITY_FILE"
    fi
done

# --- Launch all active agent gateways ---
log "Starting agent gateways..."

for profile in $PROFILES; do
    ACTIVE=$(grep -A3 "^${profile}:" "$AGENTS_YML" | grep "active:" | awk '{print $2}')
    PORT=$(grep -A10 "^${profile}:" "$AGENTS_YML" | grep "API_SERVER_PORT:" | awk '{print $2}')

    if [ "$ACTIVE" = "true" ] && [ -n "$PORT" ]; then
        log "  Launching $profile on port $PORT..."

        # Auto-restart loop: if a gateway dies, restart after 5s
        (
            while true; do
                log "  [$profile] Gateway starting on :$PORT"
                hermes -p "$profile" gateway 2>&1 | sed "s/^/[$profile] /" || true
                log "  [$profile] Gateway exited — restarting in 5s..."
                sleep 5
            done
        ) &
    fi
done

log "All agents launched. Handing off to Hermes default gateway..."
log "Fleet ready:"
for profile in $PROFILES; do
    PORT=$(grep -A10 "^${profile}:" "$AGENTS_YML" | grep "API_SERVER_PORT:" | awk '{print $2}')
    [ -n "$PORT" ] && log "  $profile → http://localhost:$PORT/v1"
done

# Hand off to built-in entrypoint
exec /opt/hermes/docker/entrypoint.sh "$@"
