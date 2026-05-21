# ARCHITECTURE.md — CAPY Bug Hunter

## System Overview

CAPY Bug Hunter is a self-learning multi-agent system for automated bug bounty hunting across web2 and web3 targets. It uses Nous Research's [Hermes Agent](https://github.com/NousResearch/hermes-agent) as the orchestrator layer, with a custom agent hierarchy, tool ecosystem, and learning pipeline built on top.

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  CLI (hermes) · Telegram · Discord · WebUI (Open WebUI)         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    HERMES ORCHESTRATOR                            │
│  Profile: athena (CEO)  ·  Gateway: port 8643                    │
│                                                                   │
│  Responsibilities:                                                │
│  • Task delegation & monitoring                                   │
│  • Scope enforcement oversight                                    │
│  • Kill-switch authority                                          │
│  • Quality gate for all findings                                  │
│  • Final report approval                                          │
└───┬───────────────────────┬──────────────────────┬───────────────┘
    │                       │                      │
    ▼                       ▼                      ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  PROMETHEUS   │  │    ODYSSEUS      │  │      ARES        │
│  RnD Lead     │  │  Strategy Lead   │  │  Execution Lead  │
│  Port: 8644   │  │  Port: 8645      │  │  Port: 8646      │
│               │  │                  │  │                  │
│ Sub-agents:   │  │ Sub-agents:      │  │ Sub-agents:      │
│ • Mnemosyne   │  │ • Themistocles   │  │ • Aegis (Recon)  │
│   (Researcher)│  │   (Strategist)   │  │ • Artemis (Hunt) │
│ • Logos       │  │ • Argus          │  │ • Hephaestus     │
│   (Analyst)   │  │   (Profiler)     │  │   (Exploit Dev)  │
│ • Cassandra   │  │ • Perseus        │  │ • Nemesis        │
│   (Intel)     │  │   (Planner)      │  │   (Validator)    │
└───────┬───────┘  └────────┬─────────┘  └────────┬─────────┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                    SHARED INFRASTRUCTURE                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Knowledge   │  │   Caveman    │  │     Scope-Guard       │  │
│  │  Base (KB)   │  │   Protocol   │  │  (Boundary Enforcer)  │  │
│  │              │  │              │  │                       │  │
│  │ LLM Wiki     │  │ Token: -65%  │  │ Pre-request checks    │  │
│  │ Persistent   │  │ Lite/Full/   │  │ Scope verification    │  │
│  │ Compounding  │  │ Ultra levels │  │ Rate limit enforcement│  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Audit Log   │  │  Kill-Switch │  │   Bug Report Corpus   │  │
│  │              │  │              │  │                       │  │
│  │ Immutable    │  │ Emergency    │  │ HackerOne + Immunefi  │  │
│  │ Full session │  │ halt system  │  │ CVE DB + Patterns     │  │
│  │ traceability │  │ Multi-trigger│  │ Methodology guides    │  │
│  └──────────────┘  └──────────────┘  └───────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Caveman Learning Engine                          │ │
│  │  • Post-session post-mortems                                  │ │
│  │  • Tool performance metrics                                   │ │
│  │  • Pattern evolution & clustering                             │ │
│  │  • Skill creation, adaptation, retirement                     │ │
│  │  • Methodology A/B testing & variation                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Agent Hierarchy

### Tier 1: Orchestrator
**Athena** — CEO and coordinator. Does not execute tools directly. Delegates to team leads, monitors progress, enforces scope, controls kill-switch, runs quality gate.

### Tier 2: Team Leads
**Prometheus** (RnD) — Knowledge engine. Researches vulnerability patterns, maintains KB, develops tools, runs learning loop.
**Odysseus** (Strategy) — Tactician. Profiles targets, designs attack paths, prioritizes by bounty, drafts reports.
**Ares** (Execution) — Weapon. Runs recon, vulnerability hunting, PoC development, and validation pipelines.

### Tier 3: Sub-Agents
Specialized agents spawned by team leads for parallel workstreams. Each has a distinct personality, tool set, and responsibility domain. Total: 11 sub-agents across 3 teams.

## Data Flow

### Hunt Session Flow
```
1. Signal In (user request / cron / intel alert)
       │
2. Athena: Verify scope, determine priority
       │
3. [PARALLEL] Odysseus: Profile target + design attack paths
   [PARALLEL] Prometheus: Research tech stack + known vulns
       │
4. Athena: Select & prioritize attack paths
       │
5. Odysseus (Perseus): Generate executable playbooks
       │
6. Ares (Aegis): Run recon pipeline → live hosts, endpoints, tech
       │
7. Ares (Artemis): Hunt for vulnerabilities → raw findings
       │
8. Ares (Hephaestus): Develop non-destructive PoCs
       │
9. Ares (Nemesis): Validate findings, eliminate FPs
       │
10. Athena: Quality review → approve/reject
       │
11. Odysseus: Draft submission-ready reports
       │
12. Prometheus: Extract lessons → update KB → evolve tools
```

### Knowledge Flow
```
Bug Reports (corpus) ──► Prometheus ──► KB (wiki) ──► All agents
Session Logs ──────────► Prometheus ──► KB + Tools update
Threat Intel ──────────► Cassandra ──► Prometheus ──► All agents
Findings ──────────────► Prometheus ──► Pattern extraction ──► Tools
```

### Communication Flow
```
Inter-agent: Caveman protocol (lite/full/ultra)
  Athena ↔ Team leads: lite
  Team leads ↔ Sub-agents: full
  Ares ↔ Sub-agents: ultra
  Sub-agents ↔ Sub-agents: ultra

User-facing: Natural language (Athena)
Report output: Professional prose (Odysseus)
```

## Technology Stack

### Core
- **Hermes Agent** (Nous Research) — Multi-agent orchestrator, gateway, messaging
- **LLM Providers** — Anthropic (Claude), OpenAI, DeepSeek, OpenRouter (configurable)

### Agent Runtime
- Each agent = isolated Hermes profile with independent memory, skills, sessions
- Sub-agents = Hermes sub-agent spawning (isolated, parallel VMs)
- Gateway = OpenAI-compatible API per agent (Open WebUI compatible)

### Security Tools (mapped via MCP / subprocess)
- **Recon**: subfinder, amass, dnsx, httpx, naabu, ffuf, katana, gau, waybackurls
- **Vuln Scanning**: nuclei, sqlmap, dalfox, tplmap, commix, graphql-scanner
- **Web3**: slither, mythril, foundry, echidna, crytic-compile
- **Validation**: custom Python/JS scripts, curl, Burp headless

### Storage
- SQLite (Hermes native: memory, sessions, skills)
- Filesystem (KB wiki, corpus, audit logs, configs)
- JSONL (audit log entries, findings)

## Deployment

### Docker Compose (Primary)
```
docker-compose.yml:
  ├── hermes (multi-profile gateway w/ fleet entrypoint)
  └── open-webui (optional visual interface)
```

### Profiles
Each agent = separate Hermes profile with isolated:
- Memory (SQLite)
- Skills (filesystem)
- Sessions (SQLite)
- Personality (SOUL.md injected as context)
- API endpoint (unique port + API key)

## Security Model

### Scope Enforcement
- Pre-execution hook: Scope-Guard validates every request
- Synchronous check: no request proceeds without explicit PASS
- Redirect following: re-check after redirect
- JS/external resources: check before fetch

### Kill-Switch
- Multi-trigger: scope violation, destructive action, data exfiltration, anomalies
- Athena holds authority, human required for resume
- Cooldown: 5 min after first trigger, 24h after third
- Immutable logging: every trigger permanently recorded

### Audit Trail
- Every action logged: agent, target, command, result, scope check
- Append-only: no log modification
- Retention: 90 days (sessions/actions), permanent (findings, kill-switch)
- JSONL format for machine processing + human readability

### Non-Destructive Policy
- All exploits: read-only by default
- Destructive testing: requires explicit human approval
- No data exfiltration beyond PoC
- No artifacts left on target systems

## Scalability

### Horizontal
- Additional Hermes instances for more parallel hunts
- Each agent profile can be scaled independently
- Sub-agents spawn on-demand (no idle costs)

### Vertical
- LLM model tiering: Opus for CEO, Sonnet for strategy, Haiku for execution
- Caveman compression: 65-75% token reduction for execution agents
- Cache: scope rules, KB lookups, tool results

## Learning System

The Caveman Learning Engine is embedded in Prometheus's core loop:

1. **Continuous**: Every session, finding, and report feeds the KB
2. **Pattern-driven**: Logos clusters reports, identifies blind spots
3. **Tool-evolving**: Tools reviewed every 30 days, adapted or retired
4. **Methodology-varying**: Odysseus varies at least one parameter per hunt
5. **A/B testing**: Data-driven methodology optimization
6. **Compounding**: KB grows richer with every engagement (LLM Wiki pattern)

## File Map

```
capy-ai/
├── README.md                         # Project overview
├── docs/
│   ├── ARCHITECTURE.md               # This file
│   └── WORKFLOW.md                   # Operational workflows
├── agents/
│   ├── orchestrator/                 # Athena (CEO)
│   │   ├── SOUL.md                   # Personality definition
│   │   └── AGENT.md                  # Role, tools, protocols
│   ├── rnd/                          # Prometheus (RnD)
│   │   ├── SOUL.md
│   │   ├── AGENT.md
│   │   └── sub-agents/
│   │       ├── researcher/           # Mnemosyne
│   │       ├── analyst/              # Logos
│   │       └── threat-intel/         # Cassandra
│   ├── plan-strategy/                # Odysseus (Strategy)
│   │   ├── SOUL.md
│   │   ├── AGENT.md
│   │   └── sub-agents/
│   │       ├── strategist/           # Themistocles
│   │       ├── target-profiler/      # Argus
│   │       └── attack-planner/       # Perseus
│   └── execution/                    # Ares (Execution)
│       ├── SOUL.md
│       ├── AGENT.md
│       └── sub-agents/
│           ├── recon-specialist/     # Aegis
│           ├── vuln-hunter/          # Artemis
│           ├── exploit-dev/          # Hephaestus
│           └── validator/            # Nemesis
├── hermes/
│   ├── config/
│   │   ├── agents.yml                # Fleet declaration
│   │   ├── .env.example              # Environment template
│   │   └── run_agents.sh             # Fleet entrypoint
│   ├── profiles/                     # Hermes profile data (runtime)
│   ├── skills/                       # Agent skills (SKILL.md per team)
│   │   ├── orchestrator/
│   │   ├── rnd/
│   │   ├── plan-strategy/
│   │   ├── execution/
│   │   └── shared/
│   ├── tools/                        # Tool definitions & manifest
│   ├── memory/                       # Hermes persistent memory
│   ├── kb/                           # LLM Wiki knowledge base
│   └── experiences/                  # Learned experiences
├── caveman/
│   ├── profiles/                     # Compression profiles (lite/full/ultra)
│   ├── rules/                        # Communication protocol
│   └── LEARNING_ENGINE.md            # Experience-based learning system
├── scope-guard/
│   ├── rules/                        # Scope enforcement rules
│   ├── scopes/                       # Per-program scope definitions
│   └── policies/                     # Rate limits, test restrictions
├── audit-log/
│   ├── sessions/                     # Session logs (JSONL)
│   ├── findings/                     # Finding logs (JSONL)
│   └── actions/                      # Action logs (JSONL)
├── kill-switch/
│   ├── triggers/                     # Trigger definitions
│   ├── conditions/                   # Trigger conditions
│   └── recovery/                     # Recovery procedures
├── corpus/
│   ├── bug-reports/                  # HackerOne, Immunefi, other
│   ├── methodologies/                # Bug bounty methodology guides
│   ├── techniques/                   # Attack techniques & bypasses
│   ├── cve-db/                       # Curated CVE database
│   ├── vulnerability-patterns/       # web2 + web3 patterns
│   └── target-profiles/              # Historical target dossiers
├── scripts/
│   ├── launch-fleet.sh               # One-command fleet launch
│   ├── setup.sh                      # Initial system setup
│   └── test-recon.sh                 # Recon sub-agent test
├── tests/                            # Agent test suites
└── docker/
    └── docker-compose.yml            # Docker deployment
```
