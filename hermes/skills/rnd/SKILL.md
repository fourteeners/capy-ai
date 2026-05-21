# SKILL: Vulnerability Research & Intelligence

## Metadata
- **Skill ID**: `rnd-001`
- **Version**: 1.0.0
- **Author**: CAPY Bug Hunter System
- **Category**: Research
- **Caveman Level**: full

## Purpose
Research vulnerability patterns, maintain the knowledge base, develop tools, and ensure the system learns from every engagement.

## Core Capabilities

### 1. Knowledge Base Management (LLM Wiki Pattern)
```
KB_UPDATE cycle:
  1. RECEIVE: new information (finding, report, research brief, intel)
  2. EXTRACT: core insight, patterns, metadata
  3. CATEGORIZE: vulnerability class, tech stack, web2/web3
  4. CROSS-REFERENCE: related entries, contradictions, synthesis
  5. WRITE: update/create wiki page with structured content
  6. LINK: bidirectional links to related pages
  7. NOTIFY: alert relevant agents to the update
```

KB structure follows Karpathy's LLM Wiki pattern:
- Persistent, compounding markdown files
- Cross-referenced with bidirectional links
- Synthesis maintained across entries
- Contradictions flagged, not hidden

### 2. Vulnerability Pattern Extraction
```
EXTRACT from bug report:
  1. Parse: vulnerability class, affected component, root cause
  2. Generalize: what makes this exploitable in general?
  3. Detection: how would we find this automatically?
  4. Tool mapping: which existing tool finds this? Need new tool?
  5. Confidence: how reliable is this pattern?
```

### 3. False Positive Analysis
```
FP_CHECK on finding:
  1. Response deduplication: is response identical to known-good?
  2. Soft 404: word count < 20% of average? Line count anomaly?
  3. WAF block: does response match known WAF patterns?
  4. Environment: does finding persist across different conditions?
  5. Scanner bias: known FP pattern from this tool?
```

### 4. Tool Evolution
```
TOOL_REVIEW cycle (every 30 days):
  1. Check: tool still maintained upstream?
  2. Test: tool accuracy on known-benchmark targets
  3. Identify: gaps, false positives, false negatives
  4. Adapt: modify detection rules, add bypasses, update signatures
  5. Retire: if tool is obsolete or superseded
```

## Skills Used
- `search_corpus` — Search bug report corpus
- `query_cve` — CVE database lookup
- `analyze_finding` — Enrich with pattern matching + CVSS
- `detect_false_positive` — FP heuristics
- `synthesize_pattern` — Generalize from specific findings
- `update_kb` — Write/update wiki page
- `create_skill` — Register new SKILL
- `update_tool` — Modify existing tool
- `search_web` — External research

## Integration
- Hermes profile: `prometheus`
- Personality: `agents/rnd/soul/SOUL.md`
- Sub-agents: researcher (Mnemosyne), analyst (Logos), threat-intel (Cassandra)
