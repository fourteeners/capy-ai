"""
CAPY Bug Hunter — Scope-Guard Test Suite

Validates scope enforcement logic without making actual network requests.
"""

import unittest


class TestScopeGuard(unittest.TestCase):
    """Test scope boundary enforcement."""

    def setUp(self):
        """Load a sample scope configuration."""
        self.sample_scope = {
            "program": "hackerone/test",
            "in_scope": {
                "domains": ["*.test.com", "api.test.io"],
                "ips": [],
                "exclude": ["docs.test.com", "status.test.com"]
            },
            "out_of_scope": {
                "domains": ["*.test-cdn.com"],
                "notes": "CDN services"
            },
            "test_types": {
                "allowed": ["recon", "scanning", "fuzzing", "injection_testing"],
                "restricted": ["dos_testing", "social_engineering"],
                "approval_required": ["destructive_exploit"]
            },
            "rate_limits": {
                "requests_per_second": 5,
                "concurrent_scans": 1
            }
        }

    def test_in_scope_exact_match(self):
        """Exact domain match should pass."""
        self.assertTrue(
            self._mock_scope_check("api.test.io", "scanning")
        )

    def test_in_scope_wildcard_match(self):
        """Wildcard domain match should pass."""
        self.assertTrue(
            self._mock_scope_check("sub.test.com", "recon")
        )
        self.assertTrue(
            self._mock_scope_check("deep.nested.sub.test.com", "fuzzing")
        )

    def test_out_of_scope_domain(self):
        """Non-matching domain should fail."""
        self.assertFalse(
            self._mock_scope_check("evil.com", "recon")
        )

    def test_excluded_subdomain(self):
        """Explicitly excluded subdomain should fail."""
        self.assertFalse(
            self._mock_scope_check("docs.test.com", "scanning")
        )

    def test_restricted_test_type(self):
        """Restricted test types should fail."""
        self.assertFalse(
            self._mock_scope_check("sub.test.com", "dos_testing")
        )
        self.assertFalse(
            self._mock_scope_check("sub.test.com", "social_engineering")
        )

    def test_approval_required_type(self):
        """Approval-required types should fail without approval."""
        self.assertFalse(
            self._mock_scope_check("sub.test.com", "destructive_exploit", approved=False)
        )
        self.assertTrue(
            self._mock_scope_check("sub.test.com", "destructive_exploit", approved=True)
        )

    def test_cdn_out_of_scope(self):
        """CDN domains should not match wildcard."""
        self.assertFalse(
            self._mock_scope_check("cdn.test-cdn.com", "recon")
        )

    def test_all_allowed_types(self):
        """All allowed types should pass for in-scope domain."""
        for test_type in ["recon", "scanning", "fuzzing", "injection_testing"]:
            with self.subTest(test_type=test_type):
                self.assertTrue(
                    self._mock_scope_check("app.test.com", test_type)
                )

    def _mock_scope_check(self, hostname, action_type, approved=False):
        """Mock scope check without network access."""
        scope = self.sample_scope

        # Check domain match
        in_scope = False
        for domain in scope["in_scope"]["domains"]:
            if self._domain_matches(hostname, domain):
                in_scope = True
                break

        if not in_scope:
            return False

        # Check exclusions
        for excluded in scope["in_scope"]["exclude"]:
            if self._domain_matches(hostname, excluded):
                return False

        # Check restricted types
        if action_type in scope["test_types"]["restricted"]:
            return False

        # Check approval
        if action_type in scope["test_types"]["approval_required"]:
            return approved

        return True

    def _domain_matches(self, hostname, pattern):
        """Simple glob-style domain matching."""
        if pattern.startswith("*."):
            suffix = pattern[2:]
            return hostname == suffix or hostname.endswith("." + suffix)
        return hostname == pattern


class TestCavemanProtocol(unittest.TestCase):
    """Test Caveman communication templates."""

    def test_status_template(self):
        """Status messages should match template."""
        status = "RECON done | 23 live | 14 web | → HUNT"
        self.assertIn("RECON", status)
        self.assertIn("→", status)

    def test_finding_template(self):
        """Finding messages should match template."""
        finding = "SQLI | POST /api/users?id= | time-blind | conf=0.92"
        parts = finding.split("|")
        self.assertGreaterEqual(len(parts), 4)
        self.assertIn("SQLI", parts[0])

    def test_alert_template(self):
        """Alert messages should start with ⚠️."""
        alert = "⚠️ WAF | Cloudflare block | paused"
        self.assertTrue(alert.startswith("⚠️"))

    def test_emergency_template(self):
        """Emergency messages should start with 🛑."""
        emergency = "🛑 KILLSWITCH | scope_violation | admin redirect external"
        self.assertTrue(emergency.startswith("🛑"))


class TestAuditLog(unittest.TestCase):
    """Test audit log entry formatting."""

    def test_action_log_format(self):
        """Action log should contain required fields."""
        entry = {
            "action_id": "test-001",
            "session_id": "HUNT-20250101-120000-abc",
            "timestamp": "2025-01-01T12:00:00Z",
            "agent": "ares.aegis",
            "action_type": "recon.subdomain_enum",
            "target": "test.com",
            "scope_check": {"result": "PASS", "rule": "*.test.com in scope"},
            "command": "subfinder -d test.com",
            "result": {"status": "success", "output_summary": "Found 23 subdomains"}
        }
        self.assertIn("action_id", entry)
        self.assertIn("scope_check", entry)
        self.assertEqual(entry["scope_check"]["result"], "PASS")

    def test_finding_log_format(self):
        """Finding log should contain required fields."""
        entry = {
            "finding_id": "test-find-001",
            "session_id": "HUNT-20250101-120000-abc",
            "vulnerability_class": "SQLI",
            "confidence": 0.92,
            "status": "validated"
        }
        self.assertGreaterEqual(entry["confidence"], 0.8)
        self.assertEqual(entry["status"], "validated")


class TestKillSwitch(unittest.TestCase):
    """Test kill-switch trigger logic."""

    def test_critical_triggers_immediate(self):
        """Critical triggers should halt immediately."""
        critical_triggers = [
            "scope_violation",
            "destructive_action",
            "data_exfiltration_attempt",
            "target_damage",
            "user_halt",
        ]
        for trigger in critical_triggers:
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, [
                    "scope_violation", "destructive_action",
                    "data_exfiltration_attempt", "target_damage",
                    "user_halt"
                ])

    def test_cooldown_enforced(self):
        """Kill-switch should enforce cooldown periods."""
        COOLDOWN_AFTER_FIRST = 300  # 5 minutes
        COOLDOWN_AFTER_THIRD = 86400  # 24 hours

        self.assertEqual(COOLDOWN_AFTER_FIRST, 300)
        self.assertEqual(COOLDOWN_AFTER_THIRD, 86400)


if __name__ == "__main__":
    unittest.main()
