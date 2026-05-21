"""
CAPY Bug Hunter CLI — command-line interface for standalone operations.

Usage:
    capy-hunt recon example.com
    capy-hunt validate agents.yml
    capy-hunt health
    capy-hunt stats
"""

import argparse
import json
import sys
from pathlib import Path


def cmd_recon(args):
    """Run standalone reconnaissance on a target."""
    from hermes.tools.registry import get_registry
    from scope_guard.engine import ScopeGuard

    target = args.target
    if not target:
        print("Error: target domain required")
        sys.exit(1)

    print(f"⛏️  CAPY Recon — {target}")
    print("=" * 50)

    reg = get_registry()

    # Step 1: Subdomain enum
    print("[1/5] Enumerating subdomains...")
    r = reg.execute("enumerate_subdomains", domain=target, passive=True)
    if r.success:
        subs = r.data.get("subdomains", [])
        print(f"  ✓ Found {len(subs)} subdomains")
        for sub in subs[:10]:
            print(f"    - {sub}")
        if len(subs) > 10:
            print(f"    ... and {len(subs) - 10} more")
    else:
        print(f"  ✗ Failed: {r.error}")

    # Step 2: DNS resolve
    print("\n[2/5] Resolving DNS...")
    domains = [target] + subs[:20] if subs else [target]
    r = reg.execute("resolve_dns", domains=domains)
    if r.success:
        resolved = r.data.get("resolved_count", 0)
        print(f"  ✓ Resolved {resolved}/{len(domains)} domains")

    # Step 3: HTTP probe
    print("\n[3/5] Probing HTTP services...")
    r = reg.execute("probe_http", hosts=domains[:20])
    if r.success:
        live = r.data.get("live_count", 0)
        print(f"  ✓ {live} live hosts")
        tech_dist = r.data.get("technology_distribution", {})
        if tech_dist:
            print("  Technologies detected:")
            for tech, count in sorted(tech_dist.items(), key=lambda x: -x[1])[:5]:
                print(f"    - {tech}: {count} host(s)")

    # Step 4: Tech fingerprint
    print("\n[4/5] Fingerprinting technology...")
    r = reg.execute("fingerprint_tech", hosts_data=r.data.get("live_hosts", []) if r.success else [])
    if r.success:
        print(f"  ✓ Fingerprinted {r.data.get('unique_technologies', 0)} unique technologies")

    # Step 5: JS analysis
    print("\n[5/5] Analyzing JavaScript...")
    r = reg.execute("analyze_js", js_files=[])
    print(f"  ✓ JS analysis framework ready")

    print("\n" + "=" * 50)
    print("Recon complete.")


def cmd_validate(args):
    """Validate system configuration."""
    from hermes.config.validator import validate_all

    print("⛏️  CAPY Config Validation")
    print("=" * 50)

    result = validate_all()

    if result["valid"]:
        print("✓ All configurations valid")
    else:
        print("✗ Configuration errors found:")
        for section, section_result in result.get("results", {}).items():
            if not section_result["valid"]:
                print(f"\n  [{section}]")
                for error in section_result.get("errors", []):
                    print(f"    ✗ {error}")

    if not result["valid"]:
        sys.exit(1)


def cmd_health(args):
    """Check system health."""
    from hermes.observability import health_check, get_metrics
    import time

    print("⛏️  CAPY Health Check")
    print("=" * 50)

    health = health_check()
    print(f"Status: {health['status']}")
    print(f"Timestamp: {health['timestamp']}")
    print(f"Agents: {json.dumps(health.get('agents', {}), indent=2)}")

    metrics = get_metrics()
    print(f"\nUptime: {metrics.get_system_health()['uptime_seconds']:.0f}s")


def cmd_stats(args):
    """Show system statistics."""
    from hermes.tools.registry import get_registry
    from hermes.observability import get_metrics

    print("⛏️  CAPY Statistics")
    print("=" * 50)

    reg = get_registry()
    tools = reg.list_all()
    print(f"Tools registered: {len(tools)}")
    print(f"Tool categories:")
    cats = {}
    for t in tools:
        cats[t.category.value] = cats.get(t.category.value, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    metrics = get_metrics()
    counters = metrics.get_system_health().get("counters", {})
    if counters:
        print(f"\nMetrics counters: {json.dumps(counters, indent=2)}")


def cmd_test(args):
    """Run test suite."""
    import unittest
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def main():
    parser = argparse.ArgumentParser(description="CAPY Bug Hunter CLI")
    sub = parser.add_subparsers(dest="command")

    # recon
    p_recon = sub.add_parser("recon", help="Run reconnaissance on a target")
    p_recon.add_argument("target", help="Target domain")
    p_recon.add_argument("--passive", action="store_true", help="Passive recon only")

    # validate
    sub.add_parser("validate", help="Validate system configuration")

    # health
    sub.add_parser("health", help="Check system health")

    # stats
    sub.add_parser("stats", help="Show system statistics")

    # test
    sub.add_parser("test", help="Run test suite")

    args = parser.parse_args()

    if args.command == "recon":
        cmd_recon(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "test":
        cmd_test(args)
    else:
        # If run directly without arguments
        parser.print_help()


if __name__ == "__main__":
    main()
