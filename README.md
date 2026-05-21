# ⛏️ CAPY BUG HUNTER — Multi-Agent Bug Bounty System

A self-learning, autonomous multi-agent system for web2/web3 bug hunting, orchestrated by [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research. Combines LLM-powered reasoning with real security tooling to discover, validate, and report vulnerabilities on public bug bounty platforms.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    HERMES ORCHESTRATOR (CEO)                  │
│  "Athena" — Task delegation, monitoring, kill-switch control │
└──────┬───────────────────────┬───────────────────────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐   ┌──────────────────────┐   ┌──────────────────┐
│  TIM RnD     │   │  TIM PLAN & STRATEGY │   │  TIM EXECUTION   │
│  "Prometheus"│   │  "Odysseus"          │   │  "Ares"          │
│              │   │                      │   │                  │
│ • Researcher │   │ • Strategist          │   │ • Recon Spec.   │
│ • Analyst    │   │ • Target Profiler     │   │ • Vuln Hunter   │
│ • Threat     │   │ • Attack Planner      │   │ • Exploit Dev   │
│   Intel      │   │                      │   │ • Validator      │
└──────┬───────┘   └──────────┬───────────┘   └────────┬─────────┘
       │                      │                        │
       └──────────────────────┼────────────────────────┘
                              ▼
              ┌───────────────────────────────┐
              │       SHARED INFRASTRUCTURE    │
              │  KB • Caveman • Scope-Guard    │
              │  Audit-Log • Kill-Switch       │
              │  Corpus • Learning Engine      │
              └───────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/fourteeners/capy-ai.git
cd capy-ai

# 2. Install Hermes Agent
pip install hermes-agent

# 3. Configure LLM provider
cp hermes/config/.env.example hermes/config/.env
# Edit .env with your API keys

# 4. Launch the multi-agent fleet
./scripts/launch-fleet.sh

# 5. Run first recon
hermes -p athena "Scan hackerone program: example.com"
```

## Agent Fleet

| Agent | Role | Character |
|-------|------|-----------|
| **Athena** | Orchestrator / CEO | Strategic mastermind, calm under pressure |
| **Prometheus** | RnD Lead | Eternal knowledge-seeker, methodical |
| **Odysseus** | Strategy Lead | Cunning tactician, sees patterns others miss |
| **Ares** | Execution Lead | Relentless hunter, precision executor |
| + 11 sub-agents | Specialized roles | See `agents/` directory |

## Key Features

- **Self-learning**: Learns from every bug report, adapts methodologies
- **Caveman protocol**: Token-optimized inter-agent communication (~65% fewer tokens)
- **LLM Wiki KB**: Persistent, compounding knowledge base from Karpathy's pattern
- **Dual Web2/Web3**: Parallel pipelines with specialized toolchains
- **Semi-auto mode**: Auto until exploit, manual approval for live execution
- **Scope-Guard**: Enforces target boundaries, never touch out-of-scope
- **Audit-Log**: Full session traceability for compliance
- **Kill-Switch**: Emergency halt with multiple trigger conditions

## Directory Structure

```
capy-ai/
├── agents/           # Agent personalities (SOUL.md, AGENT.md, SKILL.md)
├── hermes/           # Hermes orchestrator config, tools, skills, memory
├── caveman/          # Token compression profiles & rules
├── scope-guard/      # Scope enforcement policies
├── audit-log/        # Session & finding logs
├── kill-switch/      # Emergency shutdown triggers
├── corpus/           # Bug reports, methodologies, CVE database
├── docs/             # Architecture, workflow, and design docs
├── scripts/          # Launch, setup, and utility scripts
├── tests/            # Agent test suites
└── docker/           # Docker Compose for Hermes fleet
```

## References

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — Multi-agent orchestrator
- [HexStrike AI](https://github.com/0x4m4/hexstrike-ai) — MCP security tools reference
- [Caveman](https://github.com/JuliusBrussee/caveman) — Token compression
- [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — Knowledge base pattern
- [HackerOne Reports](https://www.ddosi.org/hackerone-report.html) — Bug report corpus
- [Immunefi Audits](https://github.com/immunefi-team/Past-Audit-Competitions) — Web3 audit corpus

## License

MIT — use responsibly. Only test targets you own or have explicit permission to test.
