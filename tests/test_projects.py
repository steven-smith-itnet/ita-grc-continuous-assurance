import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from assurance import audittest, controleval, coverage, dataflow, drift, remediation, usecases
from assurance.__main__ import verify
from assurance.engine import timestamp
from assurance.projects import headline, run_all, write

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "projects"
AS_OF = "2026-09-30T12:00:00Z"
NOW = timestamp(AS_OF)


def load(path):
    return json.loads(Path(path).read_text())


class ProjectBaselines(unittest.TestCase):
    """Fixed results that the documentation and site report. Update them together."""

    @classmethod
    def setUpClass(cls):
        cls.results = run_all(ROOT, AS_OF)

    def summary(self, slug):
        return self.results[slug]["summary"]

    def test_01_counts(self):
        s = self.summary("01-control-automation")
        self.assertEqual((s["usecases"], s["results"]), (8, 59))
        self.assertEqual(s["counts"], {"PASS": 21, "FAIL": 21, "UNKNOWN": 8, "NOT_APPLICABLE": 9})

    def test_02_counts(self):
        s = self.summary("02-configuration-drift")
        self.assertEqual(s["counts"], {"PASS": 17, "FAIL": 3, "UNKNOWN": 1, "NOT_APPLICABLE": 3})
        self.assertEqual((s["drift_events"], s["unauthorized_drift"]), (3, 1))

    def test_03_counts(self):
        s = self.summary("03-control-evaluation")
        self.assertEqual((s["vectors_run"], s["production_detected_all"], s["candidate_design_deficiencies"]), (109, 8, 4))

    def test_04_counts(self):
        s = self.summary("04-evidence-data-flow")
        self.assertEqual((s["flows"], s["defective_flows"], s["checks"], s["downgraded_results"], s["hidden_failures"]), (4, 3, 37, 3, 1))

    def test_05_counts(self):
        s = self.summary("05-remediation-testing")
        self.assertEqual(s["decisions"], {"CLOSE_ELIGIBLE": 1, "KEEP_OPEN": 4, "REOPEN": 1})
        self.assertEqual(s["action_counts"], {"PASS": 2, "FAIL": 4, "UNKNOWN": 1})

    def test_06_counts(self):
        s = self.summary("06-audit-process-testing")
        self.assertEqual((s["sample_deviations"], s["full_population_deviations"], s["populations_blocked"]), (1, 3, 1))
        self.assertEqual(s["period_counts"]["FAIL"], 3)
        self.assertEqual(s["request_counts"], {"PASS": 4, "FAIL": 4, "UNKNOWN": 2, "NOT_APPLICABLE": 0})

    def test_07_counts(self):
        f = self.summary("07-framework-coverage")["frameworks"]
        self.assertEqual((f["soc2"]["criteria"], f["soc2"]["partial"], f["soc2"]["backlog"]), (38, 11, ["CC6.6", "CC6.7", "CC6.8"]))
        self.assertEqual((f["iso27001_2022"]["partial"], f["hipaa"]["partial"]), (14, 9))

    def test_headlines_cover_every_project(self):
        for slug, result in self.results.items():
            self.assertTrue(headline(slug, result["summary"]))

    def test_deterministic(self):
        self.assertEqual(run_all(ROOT, AS_OF)["01-control-automation"]["rows"], self.results["01-control-automation"]["rows"])

    def test_bundles_verify_and_detect_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            write(self.results, d, AS_OF)
            for slug in self.results:
                self.assertTrue(verify(Path(d) / slug))
            (Path(d) / "02-configuration-drift" / "results.csv").write_text("tampered\n")
            with self.assertRaises(ValueError):
                verify(Path(d) / "02-configuration-drift")

    def test_non_synthetic_fixture_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(P, Path(d) / "projects")
            target = Path(d) / "projects/01-control-automation/fixtures/hr_workers.json"
            doc = load(target)
            doc["synthetic"] = False
            target.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                run_all(d, AS_OF)


class UseCaseTests(unittest.TestCase):
    def setUp(self):
        self.specs = load(P / "01-control-automation/usecases.json")
        self.data = {p.stem: load(p) for p in (P / "01-control-automation/fixtures").glob("*.json")}

    def row(self, uc, entity):
        rows, _ = usecases.run(self.specs, self.data, NOW)
        return next(r for r in rows if r["usecase_id"] == uc and r["entity_id"] == entity)

    def test_cloud_key_survives_idp_removal(self):
        row = self.row("UC-01", "W-1005")
        self.assertEqual(row["status"], "FAIL")
        self.assertIn("AKIA-SYNTH-0005", row["reasons"][0])

    def test_string_boolean_is_unknown(self):
        self.data["idp_accounts"]["accounts"][1]["enabled"] = "false"
        self.assertEqual(self.row("UC-01", "W-1002")["status"], "UNKNOWN")

    def test_future_termination_not_applicable(self):
        self.assertEqual(self.row("UC-01", "W-1008")["status"], "NOT_APPLICABLE")

    def test_self_approval_in_azure_repos(self):
        self.assertIn("approved only by its author", self.row("UC-03", "D-02")["reasons"][0])

    def test_ephi_project_requires_data_access_logs(self):
        self.assertEqual(self.row("UC-04", "gcp-proj-ehr")["status"], "FAIL")

    def test_unscanned_asset_is_unknown_not_clean(self):
        self.assertEqual(self.row("UC-07", "gcp-vm-extract-01")["status"], "UNKNOWN")

    def test_every_spec_has_an_implementation_and_mapping(self):
        for spec in self.specs["usecases"]:
            self.assertIn(spec["implementation"], usecases.REGISTRY)
            self.assertTrue(spec["frameworks"]["soc2"])


class DriftTests(unittest.TestCase):
    def test_aws_unset_versioning_is_off(self):
        self.assertFalse(drift.normalize("aws", {"GetBucketVersioning": {}})["versioning_enabled"])

    def test_aws_missing_call_is_unknown(self):
        self.assertIsNone(drift.normalize("aws", {})["versioning_enabled"])

    def test_azure_null_shared_key_means_allowed(self):
        self.assertFalse(drift.normalize("azure", {"storageAccount": {"allowSharedKeyAccess": None}})["identity_only_access"])

    def test_gcp_inherited_prevention_is_unknown(self):
        self.assertIsNone(drift.normalize("gcp", {"iamConfiguration": {"publicAccessPrevention": "inherited"}})["public_access_prevented"])

    def test_aws_default_kms_key_is_not_customer_managed(self):
        raw = {"GetBucketEncryption": {"ServerSideEncryptionConfiguration": {"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}]}}}
        self.assertFalse(drift.normalize("aws", raw)["customer_managed_key"])

    def test_missing_resource_is_unknown(self):
        d = P / "02-configuration-drift"
        after = load(d / "fixtures/snapshot_t1.json")
        del after["resources"]["azure-records-02"]
        rows, _ = drift.evaluate(load(d / "baseline.json"), load(d / "fixtures/resources.json"),
                                 load(d / "fixtures/snapshot_t0.json"), after, load(d / "fixtures/changes.json"))
        self.assertTrue(all(r["status"] in ("UNKNOWN", "NOT_APPLICABLE") for r in rows if r["resource_id"] == "azure-records-02"))

    def test_authorized_change_still_fails_baseline(self):
        d = P / "02-configuration-drift"
        rows, events = drift.evaluate(load(d / "baseline.json"), load(d / "fixtures/resources.json"),
                                      load(d / "fixtures/snapshot_t0.json"), load(d / "fixtures/snapshot_t1.json"),
                                      load(d / "fixtures/changes.json"))
        event = next(e for e in events if e["resource_id"] == "aws-records-02")
        self.assertEqual((event["status"], event["change_id"]), ("PASS", "CHG-2041"))
        self.assertEqual(next(r for r in rows if r["resource_id"] == "aws-records-02" and r["setting"] == "versioning_enabled")["status"], "FAIL")


class ControlEvaluationTests(unittest.TestCase):
    def test_naive_change_approval_misses_self_approval(self):
        rows, _ = controleval.evaluate(load(P / "01-control-automation/usecases.json"), load(P / "03-control-evaluation/vectors.json"), NOW)
        row = next(r for r in rows if r["implementation"] == "naive_change_approval" and r["vector"] == "self-approval")
        self.assertEqual(row["classification"], "missed failure")

    def test_unsupported_operation_rejected(self):
        with self.assertRaises(ValueError):
            controleval.apply_ops({"a": 1}, [{"op": "move", "path": "a"}])

    def test_baseline_not_mutated(self):
        base = {"a": {"b": [1, 2]}}
        controleval.apply_ops(base, [{"op": "append", "path": "a/b", "value": 3}])
        self.assertEqual(base, {"a": {"b": [1, 2]}})


class DataFlowTests(unittest.TestCase):
    def setUp(self):
        self.flows = load(P / "04-evidence-data-flow/flows.json")

    def flow(self, fid):
        return copy.deepcopy(next(f for f in self.flows["flows"] if f["id"] == fid))

    def test_offset_change_is_not_a_defect(self):
        rows, defects = dataflow.reconcile(self.flow("DF-04"))
        self.assertEqual(list(defects["altered"]), ["term-W-1004"])

    def test_lost_canary_fails(self):
        flow = self.flow("DF-03")
        flow["hops"][-1]["records"] = [r for r in flow["hops"][-1]["records"] if r["id"] != "canary-gcp-asset-01"]
        rows, _ = dataflow.reconcile(flow)
        self.assertEqual(next(r for r in rows if r["check"] == "canary")["status"], "FAIL")

    def test_duplicate_detected(self):
        flow = self.flow("DF-03")
        flow["hops"][1]["records"].append(copy.deepcopy(flow["hops"][1]["records"][0]))
        rows, _ = dataflow.reconcile(flow)
        self.assertIn("FAIL", [r["status"] for r in rows if r["check"] == "no unexpected or duplicate records"])

    def test_hidden_failure_recomputed(self):
        specs = load(P / "01-control-automation/usecases.json")
        data = {p.stem: load(p) for p in (P / "01-control-automation/fixtures").glob("*.json")}
        rows, _ = usecases.run(specs, data, NOW)
        _, _, impacts = dataflow.run(self.flows, rows, specs, data, NOW)
        w1004 = next(i for i in impacts if i["entity_id"] == "W-1004")
        self.assertEqual((w1004["original_status"], w1004["adjusted_status"], w1004["recomputed_from_source"]), ("PASS", "UNKNOWN", "FAIL"))


class RemediationTests(unittest.TestCase):
    def setUp(self):
        d = P / "05-remediation-testing/fixtures"
        self.findings, self.runs, self.actions = load(d / "findings.json"), load(d / "runs.json"), load(d / "actions.json")
        self.changes = load(P / "02-configuration-drift/fixtures/changes.json")

    def decision(self, fid):
        return next(r for r in remediation.evaluate_findings(self.findings, self.runs, NOW) if r["finding_id"] == fid)

    def test_remediator_identity_does_not_count(self):
        self.assertIn("remediator's own identity", self.decision("F-202")["reasons"][0])

    def test_recurrence_reopens(self):
        self.assertEqual(self.decision("F-204")["decision"], "REOPEN")

    def test_sibling_failure_blocks_closure(self):
        self.assertTrue(any("root cause not addressed" in r for r in self.decision("F-205")["reasons"]))

    def test_runs_after_as_of_ignored(self):
        self.runs["runs"].append({"run_id": "R-future", "at": "2026-10-05T00:00:00Z", "collector_identity": "assurance-collector",
                                  "results": [{"control": "UC-05", "entity": "aws-claims-docs", "status": "PASS"}]})
        self.assertIn("no retest run", self.decision("F-206")["reasons"][0])

    def test_loop_and_conflict_detected(self):
        row = next(r for r in remediation.evaluate_actions(self.actions, self.changes, NOW) if r["action_id"] == "AR-04")
        self.assertEqual(row["status"], "FAIL")
        self.assertTrue(any("CHG-2041" in r for r in row["reasons"]))


class AuditProcessTests(unittest.TestCase):
    def test_sample_independent_of_order(self):
        ids = [f"X-{n:03d}" for n in range(100)]
        self.assertEqual(audittest.select_sample(ids, 10, "seed"), audittest.select_sample(list(reversed(ids)), 10, "seed"))

    def test_sample_changes_with_seed(self):
        ids = [f"X-{n:03d}" for n in range(100)]
        self.assertNotEqual(audittest.select_sample(ids, 10, "a"), audittest.select_sample(ids, 10, "b"))

    def test_item_outside_period_blocks_sampling(self):
        d = P / "06-audit-process-testing"
        plan = load(d / "plan.json")
        population = load(d / "fixtures/populations.json")["populations"][0]
        population["items"][0]["provisioned_at"] = "2025-12-30T00:00:00Z"
        record = audittest.test_population(population, dict(plan["populations"][0], sample_sizes=plan["sample_sizes"],
                                                            authorized_approvers=plan["authorized_approvers"]), plan["period"])
        self.assertEqual(record["status"], "UNKNOWN")

    def test_weekly_windows_roll_from_period_start(self):
        rows = audittest.test_period_coverage({"controls": [{"id": "W", "name": "w", "provider": "aws", "frequency": "weekly",
                                                              "occurrences": ["2026-01-01", "2026-01-08"]}]},
                                              {"start": "2026-01-01T00:00:00Z", "end": "2026-01-14T00:00:00Z"})
        self.assertEqual((rows[0]["windows"], rows[0]["status"]), (2, "PASS"))


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load(P / "07-framework-coverage/frameworks.json")
        self.specs = load(P / "01-control-automation/usecases.json")
        self.mappings = load(P / "07-framework-coverage/mappings.json")

    def test_unknown_criterion_rejected(self):
        self.mappings["mappings"][0]["frameworks"]["soc2"].append({"id": "CC9.9", "coverage": "partial"})
        with self.assertRaises(ValueError):
            coverage.evaluate(self.catalog, self.specs, self.mappings)

    def test_full_coverage_value_rejected(self):
        self.mappings["mappings"][0]["frameworks"]["soc2"][0]["coverage"] = "full"
        with self.assertRaises(ValueError):
            coverage.evaluate(self.catalog, self.specs, self.mappings)


if __name__ == "__main__":
    unittest.main()
