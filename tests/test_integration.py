"""
CAPY Bug Hunter — Integration Test Suite (v2)

End-to-end tests for all core engines.
Uses ToolRegistry.execute() pattern to test tool calls properly.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestToolRegistry(unittest.TestCase):
    """Test the tool registry and all registered tools."""

    def setUp(self):
        if "hermes.bridge" in sys.modules:
            del sys.modules["hermes.bridge"]
        from hermes.bridge import _bridge
        from hermes.tools.registry import get_registry
        self.reg = get_registry()
        self.bridge = _bridge

    def test_tools_registered(self):
        self.assertGreater(len(self.reg), 0)

    def test_recon_tools_available(self):
        for tool_name in self.bridge.get_recon_pipeline():
            meta, func = self.reg.get(tool_name)
            self.assertIsNotNone(meta, f"Tool '{tool_name}' not registered")

    def test_enumerate_subdomains(self):
        r = self.reg.execute("enumerate_subdomains", domain="example.com", passive=True)
        self.assertTrue(r.success)
        self.assertIn("subdomains", r.data)

    def test_dns_resolve(self):
        r = self.reg.execute("resolve_dns", domains=["localhost"])
        self.assertTrue(r.success)
        self.assertIn("resolved_count", r.data)

    def test_js_analyzer(self):
        r = self.reg.execute("analyze_js", js_files=[{
            "url": "app.js",
            "content": "fetch('/api/users'); var app = new Vue({}); const API_KEY = 'sk_live_abcdefghijklmnop';"
        }])
        self.assertTrue(r.success)
        self.assertGreater(r.data["endpoint_count"], 0)
        self.assertGreater(len(r.data["libraries"]), 0)

    def test_tech_fingerprint(self):
        r = self.reg.execute("fingerprint_tech", hosts_data=[{
            "url": "https://ex.com",
            "headers": {"Server": "nginx", "X-Powered-By": "Express", "CF-Ray": "abc"},
            "body": "", "cookies": {},
        }])
        self.assertTrue(r.success)
        self.assertGreater(r.data["unique_technologies"], 0)

    def test_secret_scanner(self):
        r = self.reg.execute("scan_secrets", content_items=[{
            "source": "test.js", "content": "AKIA1234567890ABCDE sk_live_test12345", "type": "js"
        }])
        self.assertTrue(r.success)

    def test_waf_detector(self):
        r = self.reg.execute("detect_waf", response_data=[{
            "url": "https://ex.com", "headers": {"cf-ray": "abc"}, "body": "", "status": 200
        }])
        self.assertTrue(r.success)
        self.assertGreater(len(r.data["detected_wafs"]), 0)

    def test_jwt_analyzer(self):
        token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        r = self.reg.execute("analyze_jwt", tokens=[token])
        self.assertTrue(r.success)
        self.assertGreater(r.data["total_issues"], 0)

    def test_cvss_calculator(self):
        r = self.reg.execute("calculate_cvss",
            attack_vector="N", attack_complexity="L",
            privileges_required="N", user_interaction="N",
            scope="U", confidentiality="H", integrity="H", availability="H")
        self.assertTrue(r.success)
        self.assertEqual(r.data["severity"], "CRITICAL")

    def test_poc_design_non_destructive(self):
        r = self.reg.execute("design_poc", vulnerability_class="SQLI",
            endpoint="https://ex.com/api?id=1")
        self.assertTrue(r.success)
        self.assertFalse(r.data["destructive_required"])

    def test_deploy_poc_needs_approval(self):
        r = self.reg.execute("deploy_safe_poc", finding_id="t1",
            poc_design={"poc_suggestion": "test"}, target="https://ex.com", approved_by="")
        self.assertTrue(r.success)
        self.assertFalse(r.data["success"])

    def test_deploy_poc_with_approval(self):
        r = self.reg.execute("deploy_safe_poc", finding_id="t1",
            poc_design={"poc_suggestion": "test"}, target="https://ex.com",
            approved_by="human@capy.ai")
        self.assertTrue(r.success)

    def test_identify_chains(self):
        findings = [{"class": "SSRF", "endpoint": "/webhook", "confidence": 0.9},
                     {"class": "XSS", "endpoint": "/search", "confidence": 0.7}]
        r = self.reg.execute("identify_chains", findings=findings)
        self.assertTrue(r.success)

    def test_smart_contract_analyzer(self):
        code = "contract V { mapping(address=>uint) b; function w(uint a) external { require(b[msg.sender]>=a); (bool s,)=msg.sender.call{value:a}(\"\"); require(s); b[msg.sender]-=a; } }"
        r = self.reg.execute("analyze_smart_contract", contract_source=code)
        self.assertTrue(r.success)

    def test_check_scope_pass(self):
        scopes = [{"program": "t", "in_scope": {"domains": ["*.t.com"], "exclude": []},
                   "restricted": [], "approval_required": []}]
        r = self.reg.execute("check_scope", url="https://x.t.com", program_scopes=scopes,
            action_type="recon")
        self.assertTrue(r.success)
        self.assertTrue(r.data["pass"])

    def test_check_scope_block(self):
        scopes = [{"program": "t", "in_scope": {"domains": ["*.t.com"], "exclude": []},
                   "restricted": [], "approval_required": []}]
        r = self.reg.execute("check_scope", url="https://evil.com", program_scopes=scopes,
            action_type="recon")
        self.assertTrue(r.success)
        self.assertFalse(r.data["pass"])

    def test_check_scope_excluded(self):
        scopes = [{"program": "t", "in_scope": {"domains": ["*.t.com"], "exclude": ["docs.t.com"]},
                   "restricted": [], "approval_required": []}]
        r = self.reg.execute("check_scope", url="https://docs.t.com", program_scopes=scopes,
            action_type="recon")
        self.assertTrue(r.success)
        self.assertFalse(r.data["pass"])

    def test_rate_limiter(self):
        from hermes.tools.utility.rate_limiter import RateLimiter
        limiter = RateLimiter(default_rate=2.0)
        limiter.configure_host("test.com", 2.0)
        self.assertTrue(limiter.acquire("test.com"))
        self.assertTrue(limiter.acquire("test.com"))
        self.assertFalse(limiter.acquire("test.com"))

    def test_bridge_agent_tools(self):
        for agent in ["aegis", "artemis", "hephaestus", "odysseus"]:
            tools = self.bridge.get_agent_tools(agent)
            self.assertGreaterEqual(len(tools), 0)


class TestScopeGuardEngine(unittest.TestCase):
    """Scope-Guard enforcement engine."""

    def setUp(self):
        from scope_guard.engine import ScopeGuard
        self.guard = ScopeGuard()
        self.guard.load_program({
            "program": "hackerone/testco",
            "in_scope": {"domains": ["*.testco.com", "api.testco.io"],
                         "ips": ["10.0.0.1"], "exclude": ["docs.testco.com"]},
            "test_types": {"allowed": ["recon", "scanning"], "restricted": ["dos_testing"],
                          "approval_required": ["destructive_exploit"]},
            "rate_limits": {"requests_per_second": 10},
        })

    def test_in_scope_wildcard(self):
        self.assertTrue(self.guard.check("https://app.testco.com/api", "recon")["passed"])

    def test_in_scope_exact(self):
        self.assertTrue(self.guard.check("https://api.testco.io/v2", "scanning")["passed"])

    def test_in_scope_ip(self):
        self.assertTrue(self.guard.check("http://10.0.0.1/admin", "recon")["passed"])

    def test_excluded(self):
        r = self.guard.check("https://docs.testco.com", "recon")
        self.assertFalse(r["passed"])
        self.assertEqual(r["reason_code"], "excluded")

    def test_out_of_scope(self):
        r = self.guard.check("https://evil.com", "recon")
        self.assertFalse(r["passed"])
        self.assertEqual(r["reason_code"], "no_scope_match")

    def test_restricted_action(self):
        r = self.guard.check("https://app.testco.com", "dos_testing")
        self.assertFalse(r["passed"])

    def test_approval_required(self):
        r = self.guard.check("https://app.testco.com", "destructive_exploit")
        self.assertTrue(r["passed"])
        self.assertTrue(r["requires_approval"])

    def test_approval_granted(self):
        r = self.guard.check("https://app.testco.com", "destructive_exploit",
                             approved_actions=["destructive_exploit"])
        self.assertTrue(r["passed"])
        self.assertFalse(r["requires_approval"])

    def test_redirect_same_host(self):
        r = self.guard.check_redirect("https://app.testco.com/a", "https://app.testco.com/b",
                                      action_type="recon")
        self.assertTrue(r["passed"])

    def test_redirect_out_of_scope(self):
        r = self.guard.check_redirect("https://app.testco.com/a", "https://evil.com",
                                      action_type="recon")
        self.assertFalse(r["passed"])

    def test_violation_tracking(self):
        self.guard.check("https://evil.com", "recon")
        stats = self.guard.get_violation_stats()
        self.assertGreater(stats["total_violations"], 0)


class TestKillSwitchEngine(unittest.TestCase):
    """Kill-Switch emergency halt system."""

    def setUp(self):
        from kill_switch.engine import KillSwitch, TriggerSeverity
        self.ks = KillSwitch()
        self.Sev = TriggerSeverity

    def test_initial_state(self):
        from kill_switch.engine import KillSwitchState
        self.assertEqual(self.ks.state, KillSwitchState.ARMED)

    def test_trigger(self):
        events = []
        self.ks.register_listener(lambda e: events.append(e))
        ev = self.ks.trigger("scope_violation", self.Sev.CRITICAL, "aegis", "HUNT-1")
        self.assertEqual(len(events), 1)
        self.assertTrue(self.ks.is_active)

    def test_cooldown_enforced(self):
        self.ks.trigger("test", self.Sev.CRITICAL, "a", "s")
        self.assertGreater(self.ks.get_cooldown_remaining(), 250)

    def test_resume_blocked_during_cooldown(self):
        self.ks.trigger("test", self.Sev.CRITICAL, "a", "s")
        self.assertFalse(self.ks.request_resume("human"))

    def test_abort(self):
        from kill_switch.engine import KillSwitchState
        self.ks.trigger("test", self.Sev.CRITICAL, "a", "s")
        self.ks.abort_mission("user stop")
        self.assertEqual(self.ks.state, KillSwitchState.ABORTED)

    def test_shortcuts(self):
        self.ks.scope_violation("aegis", "H-1", "evil.com", "no_match")
        self.assertEqual(self.ks.trigger_count, 1)

    def test_status(self):
        self.ks.trigger("test", self.Sev.CRITICAL, "a", "s")
        st = self.ks.get_status()
        self.assertTrue(st["is_active"])
        self.assertIsNotNone(st["last_trigger"])


class TestAuditLogEngine(unittest.TestCase):
    """Audit-Log immutable logging."""

    def setUp(self):
        from audit_log.engine import AuditLogger
        self.tmp = tempfile.mkdtemp()
        self.log = AuditLogger(base_dir=self.tmp, retention_days=90)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_start_session(self):
        sid = self.log.start_session("ex.com")
        self.assertTrue(sid.startswith("HUNT-"))

    def test_log_action(self):
        sid = self.log.start_session("ex.com")
        aid = self.log.log_action("aegis", "recon", "ex.com", "cmd",
                                  {"passed": True}, {"status": "ok"}, sid)
        self.assertIsNotNone(aid)

    def test_log_finding(self):
        sid = self.log.start_session("ex.com")
        fid = self.log.log_finding("SQLI", "https://ex.com", 0.92, "artemis", sid, 7.5)
        self.assertIsNotNone(fid)

    def test_update_finding(self):
        sid = self.log.start_session("ex.com")
        fid = self.log.log_finding("XSS", "https://ex.com", 0.8, "test", sid)
        self.log.update_finding_status(fid, "validated", "nemesis", {"conf": 0.92})

    def test_log_kill_switch(self):
        class M: trigger_id="K1"; session_id="H"; condition="sc"; triggered_by="sg"; severity="c"; context={}
        self.log.log_kill_switch(M())

    def test_stats(self):
        self.log.start_session("ex.com")
        self.log.log_action("t", "t", "t", "c", {"passed": True}, {"s": "ok"})
        st = self.log.get_stats()
        self.assertGreater(st["size_bytes"], 0)


class TestCavemanProtocol(unittest.TestCase):
    """Caveman token compression."""

    def setUp(self):
        from caveman.engine import CavemanProtocol, CavemanLevel
        self.cp = CavemanProtocol()
        self.L = CavemanLevel.LITE
        self.F = CavemanLevel.FULL
        self.U = CavemanLevel.ULTRA

    def test_lite_drops_greetings(self):
        r = self.cp.compress("Hello, I think we should scan. Thank you.", self.L)
        self.assertNotIn("Hello", r)

    def test_full_drops_articles(self):
        r = self.cp.compress("The vulnerability is in the login page.", self.F)
        self.assertNotIn(" the ", r.lower())

    def test_ultra_alert(self):
        r = self.cp.compress("WAF detected", self.U, "alert")
        self.assertTrue(r.startswith("⚠️"))

    def test_validate_status(self):
        r = self.cp.validate_template("RECON done | 23 live | → HUNT", "status", self.U)
        self.assertTrue(r["valid"])

    def test_validate_finding(self):
        r = self.cp.validate_template("SQLI | POST /api | time-blind | conf=0.92", "finding", self.U)
        self.assertTrue(r["valid"])

    def test_compare(self):
        c = self.cp.compare("I completed scanning and found issues.", "SCAN done | 8 found")
        self.assertGreater(c["tokens_saved"], 0)

    def test_agent_levels(self):
        self.assertEqual(self.cp.for_agent("athena"), self.L)
        self.assertEqual(self.cp.for_agent("ares"), self.U)


class TestKbEngine(unittest.TestCase):
    """LLM Wiki KB engine."""

    def setUp(self):
        from hermes.kb.engine import KbEngine
        self.tmp = tempfile.mkdtemp()
        self.kb = KbEngine(base_dir=self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_write_read(self):
        self.kb.write("test/page", "Content [[link]].")
        c = self.kb.read("test/page")
        self.assertIn("Content", c)

    def test_append_section(self):
        self.kb.write("test/page", "Base.")
        self.kb.append_section("test/page", "New", "More.")
        c = self.kb.read("test/page")
        self.assertIn("New", c)

    def test_contradiction(self):
        self.kb.write("test/page", "Claim.")
        self.kb.flag_contradiction("test/page", "Disputed.")
        c = self.kb.read("test/page")
        self.assertIn("⚠️ CONTRADICTION:", c)

    def test_resolve_contradiction(self):
        self.kb.write("test/page", "Claim.")
        self.kb.flag_contradiction("test/page", "Disputed.")
        self.kb.resolve_contradiction("test/page", "Verified.")
        c = self.kb.read("test/page")
        self.assertIn("RESOLVED:", c)
        self.assertNotIn("⚠️ CONTRADICTION:", c)

    def test_backlinks(self):
        self.kb.write("a/page-a", "Ref [[page-b]].")
        self.kb.write("b/page-b", "Linked.")
        bl = self.kb.get_backlinks("b/page-b")
        self.assertIn("a/page-a.md", bl)

    def test_search(self):
        self.kb.write("sqli/time", "MySQL time-based blind SQL injection.")
        r = self.kb.search("SQL injection")
        self.assertGreater(len(r), 0)

    def test_index(self):
        self.kb.write("p1", "C1.")
        self.kb.write("p2", "C2 [[p1]].")
        idx = self.kb.get_index()
        self.assertGreaterEqual(idx["total_pages"], 2)


class TestLearningEngine(unittest.TestCase):
    """Caveman Learning Engine."""

    def setUp(self):
        from caveman.learning_engine import LearningEngine
        self.le = LearningEngine()

    def test_record_tool_call(self):
        self.le.record_tool_call("subfinder", True, 4500)
        m = self.le.get_tool_metrics("subfinder")
        self.assertEqual(m.total_calls, 1)

    def test_fp_tracking(self):
        self.le.record_tool_call("nuclei", True, 2000)
        for _ in range(6): self.le.record_finding_result("nuclei", True)
        for _ in range(4): self.le.record_finding_result("nuclei", False)
        m = self.le.get_tool_metrics("nuclei")
        self.assertGreater(m.fp_rate, 0.2)
        self.assertTrue(m.needs_review)

    def test_post_mortem(self):
        pm = self.le.create_post_mortem("HUNT-t", "ex.com", 3600, 10, 8, 2,
                                        ["subfinder", "nuclei"], "test_waf")
        pm.what_worked.append("Good subdomain coverage")
        pm.lessons.append("Need unicode WAF bypass")
        a = self.le.analyze_post_mortem(pm)
        self.assertEqual(a["fp_rate"], 0.2)

    def test_variation(self):
        r = self.le.record_variation("unicode_bypass", "waf_targets", 3, 7, 1800, 2100)
        self.assertEqual(r["verdict"], "BETTER")

    def test_adopt_variation(self):
        for _ in range(3):
            self.le.record_variation("fast_scan", "generic", 2, 4, 600, 500)
        self.assertTrue(self.le.should_adopt_variation("fast_scan"))

    def test_summary(self):
        self.le.record_tool_call("t1", True, 100)
        s = self.le.get_learning_summary()
        self.assertEqual(s["tools_tracked"], 1)


class TestEndToEnd(unittest.TestCase):
    """Full hunt flow simulation."""

    def test_full_flow(self):
        from scope_guard.engine import ScopeGuard
        from kill_switch.engine import KillSwitch
        from audit_log.engine import AuditLogger
        from caveman.engine import CavemanProtocol, CavemanLevel
        from caveman.learning_engine import LearningEngine

        tmp = tempfile.mkdtemp()
        cp = CavemanProtocol()
        le = LearningEngine()

        try:
            guard = ScopeGuard()
            guard.load_program({
                "program": "hackerone/t",
                "in_scope": {"domains": ["*.t.com"], "exclude": []},
                "test_types": {"allowed": ["recon"], "restricted": [], "approval_required": []},
                "rate_limits": {"requests_per_second": 10},
            })

            log = AuditLogger(base_dir=os.path.join(tmp, "audit"))
            sid = log.start_session("t.com")

            ks = KillSwitch()
            self.assertEqual(str(ks.state), "KillSwitchState.ARMED")

            sc = guard.check("https://app.t.com", "recon", sid)
            self.assertTrue(sc["passed"])

            log.log_scope_check("https://app.t.com", sc, "aegis", sid)

            msg = cp.compress("Recon done. 23 live hosts.", CavemanLevel.ULTRA, "status")
            self.assertIn("|", msg)

            fid = log.log_finding("SQLI", "https://app.t.com/api", 0.92, "artemis", sid, 7.5)
            le.record_tool_call("sqlmap", True, 12000)
            le.record_finding_result("sqlmap", True)

            log.update_finding_status(fid, "validated", "nemesis", {"conf": 0.92})

            pm = le.create_post_mortem(sid, "t.com", 4200, 8, 6, 2, ["subfinder", "sqlmap"])
            pm.lessons.append("SQL injection in API search param")
            a = le.analyze_post_mortem(pm)
            self.assertEqual(a["fp_rate"], 0.25)

            log.end_session(sid, "completed", {"findings": 8, "validated": 6})

            self.assertGreater(log.get_stats()["size_bytes"], 0)
            self.assertGreaterEqual(le.get_learning_summary()["tools_tracked"], 1)

        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
