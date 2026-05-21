# Emerging Patterns — What We're Tracking

*Last updated: 2025-01-01 | Author: logos (Analyst)*

## Pattern 1: GraphQL as Attack Surface Multiplier
**Evidence**: 8 related reports in 6 months
**Signal**: GraphQL endpoints with introspection enabled appear in 40% of recent targets
**Impact**: Full schema disclosure → targeted attacks on every mutation and query
**Trend**: Increasing as more teams adopt GraphQL without understanding security implications
**Action**: Priority scan for GraphQL + introspection on ALL recon passes

## Pattern 2: JWT Algorithm Confusion Resurgence
**Evidence**: 5 reports in 3 months, all affecting Python/Node.js backends
**Signal**: RS256→HS256 confusion still works on many production systems
**Impact**: Full authentication bypass
**Trend**: Resurgence as teams migrate to microservices with JWT-based auth
**Action**: Add JWT analysis to STANDARD recon (not optional)

## Pattern 3: Webhook SSRF
**Evidence**: 12 reports across all platforms
**Signal**: Webhook/notification URLs are the #1 SSRF entry point
**Impact**: Cloud metadata access, internal network scanning
**Trend**: Steady — every app with webhooks is potentially vulnerable
**Action**: Test webhook URL fields for SSRF on EVERY target with webhooks

## Pattern 4: Blockchain Oracle Manipulation
**Evidence**: 6 Immunefi reports in 6 months
**Signal**: Protocols using spot price from DEX pairs without TWAP
**Impact**: Protocol insolvency, unfair liquidations
**Trend**: Increasing with DeFi TVL growth
**Action**: Add TWAP/Chainlink check to all Web3 contract analyses

## Pattern 5: Go/Node.js SSTI
**Evidence**: 4 reports — increasing
**Signal**: Template injection in Go `html/template` and Node.js template engines
**Impact**: RCE in some template engines
**Trend**: New — previously considered Java/Python-only vulnerability
**Action**: Add SSTI testing for Go and Node.js targets

## Confidence Levels
| Pattern | Confidence | Data Points |
|---------|-----------|-------------|
| GraphQL Attack Surface | 0.92 | 8 reports |
| JWT Confusion | 0.85 | 5 reports |
| Webhook SSRF | 0.95 | 12 reports |
| Oracle Manipulation | 0.88 | 6 reports |
| Go/Node SSTI | 0.65 | 4 reports |

## KB Updates Required
- [[vulnerability-classes/web2/graphql]] — Update with introspection findings
- [[vulnerability-classes/web2/jwt-confusion]] — Add recent bypass variants
- [[vulnerability-classes/web2/ssrf]] — Add webhook-specific section
- [[vulnerability-classes/web3/oracle-manipulation]] — Create new page
- [[vulnerability-classes/web2/ssti-go-node]] — Create new page
