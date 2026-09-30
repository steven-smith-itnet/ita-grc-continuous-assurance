import copy
import json
from pathlib import Path
import tempfile
import unittest
from assurance.engine import evaluate, timestamp
from assurance.adapters import explicit_public_prevention
from assurance.__main__ import write_bundle, verify

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-09-30T12:00:00Z"


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.scope = json.loads((ROOT / "fixtures/scope.json").read_text())
        self.evidence = json.loads((ROOT / "fixtures/evidence.json").read_text())
        self.catalog = json.loads((ROOT / "controls/catalog.json").read_text())
        self.exceptions = json.loads((ROOT / "fixtures/exceptions.json").read_text())

    def run_case(self):
        return evaluate(self.scope, self.evidence, self.catalog, NOW, self.exceptions)

    def row(self, cid="STO-01", aid="aws-records-01"):
        return next(r for r in self.run_case()["results"] if r["asset_id"] == aid and r["control_id"] == cid)

    def test_expected_population(self):
        self.assertEqual(len(self.run_case()["results"]), 9 * 14)

    def test_missing_asset_does_not_disappear(self):
        self.assertEqual(self.row(aid="gcp-records-03")["status"], "UNKNOWN")

    def test_missing_fact_unknown(self):
        del self.evidence["assets"][0]["facts"]["public_access_prevention"]
        self.assertEqual(self.row()["status"], "UNKNOWN")

    def test_false_is_failure(self):
        self.assertEqual(self.row()["status"], "FAIL")

    def test_stale_unknown(self):
        self.evidence["assets"][0]["facts"]["public_access_prevention"]["collected_at"] = "2026-01-01T00:00:00Z"
        self.assertEqual(self.row()["status"], "UNKNOWN")

    def test_future_unknown(self):
        self.evidence["assets"][0]["facts"]["public_access_prevention"]["collected_at"] = "2027-01-01T00:00:00Z"
        self.assertEqual(self.row()["status"], "UNKNOWN")

    def test_string_true_not_boolean(self):
        self.evidence["assets"][0]["facts"]["public_access_prevention"]["value"] = "true"
        self.assertEqual(self.row()["status"], "UNKNOWN")

    def test_missing_source_unknown(self):
        self.evidence["assets"][0]["facts"]["public_access_prevention"]["source"] = ""
        self.assertEqual(self.row()["status"], "UNKNOWN")

    def test_valid_exception_keeps_failure(self):
        row = self.row("KEY-01")
        self.assertEqual(row["status"], "FAIL")
        self.assertTrue(row["accepted_risk"])

    def test_expired_exception_invalid(self):
        self.exceptions[0]["expires_at"] = NOW
        self.assertFalse(self.row("KEY-01")["accepted_risk"])

    def test_self_approval_invalid(self):
        self.exceptions[0]["approver"] = self.exceptions[0]["requester"]
        self.assertFalse(self.row("KEY-01")["accepted_risk"])

    def test_missing_compensation_invalid(self):
        del self.exceptions[0]["compensating_control"]
        self.assertFalse(self.row("KEY-01")["accepted_risk"])

    def test_out_of_scope_control_explicit(self):
        self.assertEqual(self.row("KEY-01", "aws-records-02")["status"], "NOT_APPLICABLE")

    def test_missing_scope_classification_unknown(self):
        del self.scope["assets"][0]["classification"]
        self.assertEqual(self.row("KEY-01")["status"], "UNKNOWN")

    def test_duplicate_population_rejected(self):
        self.scope["assets"].append(copy.deepcopy(self.scope["assets"][0]))
        with self.assertRaises(ValueError): self.run_case()

    def test_unscoped_evidence_rejected(self):
        self.evidence["assets"][0]["id"] = "unscoped"
        with self.assertRaises(ValueError): self.run_case()

    def test_empty_population_rejected(self):
        self.scope["assets"] = []
        with self.assertRaises(ValueError): self.run_case()

    def test_unknown_remains_in_denominator(self):
        summary = self.run_case()["summary"]
        c = summary["counts"]
        self.assertEqual(summary["pass_percent_of_applicable"], round(c["PASS"] / (c["PASS"] + c["FAIL"] + c["UNKNOWN"]) * 100, 2))

    def test_deterministic(self):
        self.assertEqual(self.run_case(), self.run_case())

    def test_hash_changes_with_evidence(self):
        first = self.run_case()["evidence_sha256"]
        self.evidence["assets"][0]["facts"]["owner"]["value"] = "new-owner"
        self.assertNotEqual(first, self.run_case()["evidence_sha256"])

    def test_bundle_tamper_detected(self):
        with tempfile.TemporaryDirectory() as d:
            write_bundle(self.run_case(), d, {"scope.json": self.scope})
            self.assertTrue(verify(d))
            (Path(d) / "results.json").write_text("{}")
            with self.assertRaises(ValueError): verify(d)

    def test_naive_time_rejected(self):
        with self.assertRaises(ValueError): timestamp("2026-09-30T12:00:00")

    def test_negative_rpo_unknown(self):
        self.evidence["assets"][0]["facts"]["recoverable_point_age_hours"]["value"] = -1
        self.assertEqual(self.row("BCP-01")["status"], "UNKNOWN")

    def test_failed_predicate_not_hidden_by_missing_fact(self):
        del self.evidence["assets"][3]["facts"]["restore_integrity_verified"]
        self.assertEqual(self.row("BCP-02", "azure-records-01")["status"], "FAIL")


class AdapterTests(unittest.TestCase):
    def test_provider_fixtures(self):
        for provider in ("aws", "azure", "gcp"):
            with self.subTest(provider=provider):
                raw = json.loads((ROOT / f"fixtures/raw/{provider}.json").read_text())
                self.assertTrue(explicit_public_prevention(provider, raw))

    def test_empty_exports_unknown(self):
        for provider in ("aws", "azure", "gcp"):
            self.assertIsNone(explicit_public_prevention(provider, {}))

    def test_gcp_inheritance_unknown(self):
        self.assertIsNone(explicit_public_prevention("gcp", {"iamConfiguration": {"publicAccessPrevention": "inherited"}}))

    def test_azure_null_unknown(self):
        self.assertIsNone(explicit_public_prevention("azure", {"allowBlobPublicAccess": None}))

    def test_aws_partial_unknown(self):
        self.assertIsNone(explicit_public_prevention("aws", {"PublicAccessBlockConfiguration": {"BlockPublicAcls": True}}))


if __name__ == "__main__":
    unittest.main()
