# CAPY Bug Hunter — Knowledge Base

*Auto-maintained by Prometheus (RnD). Follows Karpathy's LLM Wiki pattern: persistent, compounding, cross-referenced.*

## Structure
```
kb/
├── index.md                    # This file — top-level navigation
├── vulnerability-classes/      # Categorized vulnerability knowledge
│   ├── web2/                   # Web2 vulnerability patterns
│   │   ├── injection/          # SQLi, command injection, SSTI, etc.
│   │   ├── xss/                # Reflected, stored, DOM-based
│   │   ├── ssrf/               # Server-side request forgery
│   │   ├── auth/               # Authentication & authorization flaws
│   │   ├── misconfig/          # Security misconfigurations
│   │   └── business-logic/     # Business logic vulnerabilities
│   └── web3/                   # Web3/smart contract patterns
│       ├── reentrancy/
│       ├── access-control/
│       ├── arithmetic/
│       ├── oracle/             # Oracle manipulation
│       └── governance/
├── techniques/                 # Attack techniques & methodologies
│   ├── recon/                  # Reconnaissance techniques
│   ├── fuzzing/                # Fuzzing strategies
│   ├── bypass/                 # WAF & filter bypass techniques
│   └── chaining/               # Vulnerability chaining patterns
├── tools/                      # Tool knowledge & registry
│   ├── registry.md             # Complete tool inventory
│   ├── nuclei-templates/       # Custom Nuclei templates
│   └── custom-scripts/         # Our custom tools and scripts
├── targets/                    # Target-specific knowledge
│   └── *.md                    # Per-target KB entries
├── sessions/                   # Hunt session summaries (for learning)
│   └── HUNT-*.md               # Per-session learning artifacts
└── synthesis/                  # Cross-cutting synthesis pages
    ├── emerging-patterns.md    # Patterns we're tracking
    ├── blind-spots.md          # Areas we're weak in
    └── methodology-evolution.md # How our approach is evolving
```

## Wiki Conventions
1. **Every page has bidirectional links.** Use `[[page-name]]` syntax.
2. **Contradictions are flagged, not hidden.** Use `⚠️ CONTRADICTION:` markers.
3. **Version confidence.** Each claim has an implicit confidence based on evidence count.
4. **Synthesis pages tie it together.** Individual vulnerability pages are facts. Synthesis pages are understanding.

## How the KB Grows
```
New Information Source
    │
    ▼
┌─────────────────────────────┐
│ EXTRACT core insights       │
└─────────┬───────────────────┘
          ▼
┌─────────────────────────────┐
│ CATEGORIZE into KB tree     │
└─────────┬───────────────────┘
          ▼
┌─────────────────────────────┐
│ CROSS-REFERENCE             │
│ • Link to related pages     │
│ • Flag contradictions       │
│ • Update synthesis pages    │
└─────────┬───────────────────┘
          ▼
┌─────────────────────────────┐
│ PUBLISH                     │
│ • Write/update wiki pages   │
│ • Notify relevant agents    │
│ • Update index if needed    │
└─────────────────────────────┘
```

## Current State
*KB initialized — population begins with first hunt session.*
