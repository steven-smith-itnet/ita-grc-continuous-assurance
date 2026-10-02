"""Run the seven deeper projects and write a verifiable bundle for each one.

Every evidence fixture must be marked synthetic. Each bundle holds results.json,
results.csv, report.md and a SHA-256 manifest that the existing verify command checks.
"""
import csv
import hashlib
import json
from pathlib import Path

from . import audittest, controleval, coverage, dataflow, drift, remediation, usecases
from .engine import STATES, digest, timestamp

TITLES = {
    "01-control-automation": "Control automation use-case library",
    "02-configuration-drift": "Configuration baseline and drift",
    "03-control-evaluation": "Control evaluation with seeded faults",
    "04-evidence-data-flow": "Evidence data-flow testing",
    "05-remediation-testing": "Remediation verification",
    "06-audit-process-testing": "Audit process testing",
    "07-framework-coverage": "SOC 2-first framework coverage",
}


def _load(path):
    return json.loads(Path(path).read_text())


def _evidence(path):
    doc = _load(path)
    if doc.get("synthetic") is not True:
        raise ValueError(f"{path} is not marked synthetic; the public projects accept synthetic evidence only")
    return doc


def _fixtures(folder):
    return {p.stem: _evidence(p) for p in sorted((folder / "fixtures").glob("*.json"))}


def _inputs(root, *paths):
    return {Path(p).resolve().relative_to(Path(root).resolve()).as_posix(): hashlib.sha256(Path(p).read_bytes()).hexdigest()
            for p in paths}


def _non_pass(rows, label):
    lines = []
    for row in rows:
        if row.get("status") not in ("PASS", "NOT_APPLICABLE"):
            lines += [f"- **{label(row)}** {row['status']}: " + "; ".join(row["reasons"])]
    return lines or ["- None"]


def _counts_table(counts):
    return ["| State | Count |", "|---|---:|"] + [f"| {k} | {v} |" for k, v in counts.items()]


def run_all(root, as_of):
    """Return {slug: {"doc", "rows", "report"}} for every project."""
    now = timestamp(as_of)
    base = Path(root) / "projects"
    out = {}

    d1 = base / "01-control-automation"
    specs, data = _load(d1 / "usecases.json"), _fixtures(d1)
    rows1, by_uc = usecases.run(specs, data, now)
    summary1 = {"usecases": len(specs["usecases"]), "results": len(rows1), "counts": usecases.counts(rows1), "by_usecase": by_uc}
    report1 = ["| Use case | PASS | FAIL | UNKNOWN | NOT_APPLICABLE |", "|---|---:|---:|---:|---:|"]
    report1 += [f"| {s['id']} {s['name']} | " + " | ".join(str(by_uc[s['id']][k]) for k in STATES) + " |" for s in specs["usecases"]]
    report1 += ["", "## Failures and gaps", ""] + _non_pass(rows1, lambda r: f"{r['usecase_id']} {r['entity_id']}")
    out["01-control-automation"] = {"summary": summary1, "rows": rows1, "report": report1,
                                    "inputs": _inputs(root, d1 / "usecases.json", *sorted((d1 / "fixtures").glob("*.json")))}

    d2 = base / "02-configuration-drift"
    f2 = _fixtures(d2)
    baseline = _load(d2 / "baseline.json")
    rows2, events = drift.evaluate(baseline, f2["resources"], f2["snapshot_t0"], f2["snapshot_t1"], f2["changes"])
    summary2 = {"resources": len(f2["resources"]["resources"]), "settings": len(baseline["settings"]), "results": len(rows2),
                "counts": drift.counts(rows2), "drift_events": len(events), "drift_counts": drift.counts(events),
                "unauthorized_drift": sum(e["status"] == "FAIL" for e in events)}
    report2 = _counts_table(summary2["counts"]) + ["", "## Baseline deviations and gaps", ""]
    report2 += _non_pass(rows2, lambda r: f"{r['resource_id']} {r['setting']}")
    report2 += ["", "## Drift between snapshots", "", "| Resource | Setting | Before | After | Direction | Change | State |", "|---|---|---|---|---|---|---|"]
    report2 += [f"| {e['resource_id']} | {e['setting']} | {e['before']} | {e['after']} | {e['direction']} | {e['change_id'] or 'none'} | {e['status']} |" for e in events]
    out["02-configuration-drift"] = {"summary": summary2, "rows": rows2, "extra": {"drift_events": events}, "report": report2,
                                     "inputs": _inputs(root, d2 / "baseline.json", *sorted((d2 / "fixtures").glob("*.json")))}

    d3 = base / "03-control-evaluation"
    vectors = _evidence(d3 / "vectors.json")
    rows3, records = controleval.evaluate(specs, vectors, now)
    production = [r for r in records if r["role"] == "production"]
    candidates = [r for r in records if r["role"] == "candidate"]
    summary3 = {"vectors_run": len(rows3), "implementations": len(records),
                "production_implementations": len(production),
                "production_detected_all": sum(r["critical_misses"] == 0 and r["other_mismatches"] == 0 for r in production),
                "candidate_implementations": len(candidates),
                "candidate_design_deficiencies": sum(r["critical_misses"] > 0 for r in candidates),
                "counts": usecases.counts(rows3)}
    report3 = ["| Use case | Implementation | Role | Vectors | As expected | Critical misses | Other mismatches | Verdict |",
               "|---|---|---|---:|---:|---:|---:|---|"]
    report3 += [f"| {r['usecase_id']} | {r['implementation']} | {r['role']} | {r['vectors']} | {r['as_expected']} | {r['critical_misses']} | {r['other_mismatches']} | {r['verdict']} |" for r in records]
    report3 += ["", "## Mismatched vectors", ""]
    report3 += [f"- **{r['implementation']} / {r['vector']}**: expected {r['expected']}, observed {r['observed']} ({r['classification']}). {r['description']}."
                for r in rows3 if r["status"] != "PASS"] or ["- None"]
    out["03-control-evaluation"] = {"summary": summary3, "rows": rows3, "extra": {"evaluations": records}, "report": report3,
                                    "inputs": _inputs(root, d3 / "vectors.json", d1 / "usecases.json")}

    d4 = base / "04-evidence-data-flow"
    flows = _evidence(d4 / "flows.json")
    rows4, verdicts, impacts = dataflow.run(flows, rows1, specs, data, now)
    summary4 = {"flows": len(verdicts), "defective_flows": sum(v["verdict"] == "DEFECTIVE" for v in verdicts),
                "checks": len(rows4), "counts": dataflow.counts(rows4),
                "downgraded_results": sum(i["original_status"] == "PASS" and i["adjusted_status"] == "UNKNOWN" for i in impacts),
                "hidden_failures": sum(i.get("recomputed_from_source") == "FAIL" for i in impacts)}
    report4 = ["| Flow | Provider | Hops | Failed checks | Verdict |", "|---|---|---|---:|---|"]
    report4 += [f"| {v['flow_id']} {v['name']} | {v['provider']} | {' → '.join(v['hops'])} | {v['failed_checks']} of {v['checks']} | {v['verdict']} |" for v in verdicts]
    report4 += ["", "## Failed checks", ""] + _non_pass(rows4, lambda r: f"{r['flow_id']} {r['check']} ({r['hop']})")
    report4 += ["", "## Effect on control results", "", "| Flow | Use case | Entity | Original | Adjusted | Recomputed from source |", "|---|---|---|---|---|---|"]
    report4 += [f"| {i['flow_id']} | {i['usecase_id']} | {i['entity_id']} | {i['original_status']} | {i['adjusted_status']} | {i.get('recomputed_from_source', 'n/a')} |" for i in impacts]
    out["04-evidence-data-flow"] = {"summary": summary4, "rows": rows4, "extra": {"flows": verdicts, "impacts": impacts}, "report": report4,
                                    "inputs": _inputs(root, d4 / "flows.json", d1 / "usecases.json", *sorted((d1 / "fixtures").glob("*.json")))}

    d5 = base / "05-remediation-testing"
    f5 = _fixtures(d5)
    findings = remediation.evaluate_findings(f5["findings"], f5["runs"], now)
    actions = remediation.evaluate_actions(f5["actions"], f2["changes"], now)
    summary5 = remediation.summarize(findings, actions)
    report5 = ["| Finding | Control | Affected | Decision | Reasons |", "|---|---|---|---|---|"]
    report5 += [f"| {r['finding_id']} | {r['control']} | {', '.join(r['affected'])} | {r['decision']} | {'; '.join(r['reasons'])} |" for r in findings]
    report5 += ["", "## Automatic remediation actions", "", "| Action | Provider | Resource | State | Reasons |", "|---|---|---|---|---|"]
    report5 += [f"| {r['action_id']} | {r['provider']} | {r['resource_id']} | {r['status']} | {'; '.join(r['reasons'])} |" for r in actions]
    out["05-remediation-testing"] = {"summary": summary5, "rows": findings, "extra": {"actions": actions}, "report": report5,
                                     "inputs": _inputs(root, *sorted((d5 / "fixtures").glob("*.json")), d2 / "fixtures/changes.json")}

    d6 = base / "06-audit-process-testing"
    plan, f6 = _load(d6 / "plan.json"), _fixtures(d6)
    populations = {p["id"]: p for p in f6["populations"]["populations"]}
    samples = [audittest.test_population(populations[p["population_id"]],
                                         dict(p, sample_sizes=plan["sample_sizes"], authorized_approvers=plan["authorized_approvers"]),
                                         plan["period"]) for p in plan["populations"]]
    coverage_rows = audittest.test_period_coverage(f6["period_controls"], plan["period"])
    requests = audittest.test_requests(f6["pbc"], plan["period"])
    summary6 = {"period": plan["period"], "populations": len(samples),
                "populations_blocked": sum(s["status"] == "UNKNOWN" for s in samples),
                "sample_deviations": sum(len(s["sample_deviations"]) for s in samples),
                "full_population_deviations": sum(len(s["full_population_deviations"]) for s in samples),
                "periodic_controls": len(coverage_rows), "period_counts": audittest.counts(coverage_rows),
                "requests": len(requests), "request_counts": audittest.counts(requests),
                "delivered_requests": sum(bool(q.get("delivered_at")) for q in f6["pbc"]["requests"]),
                "accepted_first_pass": sum(bool(q.get("delivered_at")) and q.get("rework_count", 0) == 0 for q in f6["pbc"]["requests"])}
    report6 = ["## Populations and samples", ""]
    for s in samples:
        report6 += [f"### {s['population_id']}: {s['description']}", "",
                    f"Source count {s['declared_total']}, extracted {s['extracted']}. Seed `{s['seed']}`. Population hash `{s['population_sha256'][:16]}…`.", "",
                    s["conclusion"], ""]
        if s["sample"]:
            report6 += ["Selected items: " + ", ".join(s["sample"]), ""]
        report6 += [f"- Reconciliation issue: {x}" for x in s["reconciliation"]]
        report6 += [f"- Sample deviation {x['id']}: {'; '.join(x['failures'])}" for x in s["sample_deviations"]]
        report6 += [f"- Missed by the sample, found by full testing: {x}" for x in s.get("missed_by_sample", [])]
        report6 += [""]
    report6 += ["## Period coverage", "", "| Control | Provider | Frequency | Windows covered | State | Missed |", "|---|---|---|---:|---|---|"]
    report6 += [f"| {r['control_id']} {r['name']} | {r['provider']} | {r['frequency']} | {r['covered']} of {r['windows']} | {r['status']} | {', '.join(r['missed']) or 'none'} |" for r in coverage_rows]
    report6 += ["", "## Evidence requests", "",
                f"{summary6['accepted_first_pass']} of {summary6['delivered_requests']} delivered requests were accepted without rework.", "", "| Request | Control | Type | State | Reasons |", "|---|---|---|---|---|"]
    report6 += [f"| {r['request_id']} | {r['control']} | {r['evidence_type']} | {r['status']} | {'; '.join(r['reasons'])} |" for r in requests]
    out["06-audit-process-testing"] = {"summary": summary6, "rows": coverage_rows + requests,
                                       "extra": {"samples": samples, "period_coverage": coverage_rows, "requests": requests},
                                       "report": report6, "inputs": _inputs(root, d6 / "plan.json", *sorted((d6 / "fixtures").glob("*.json")))}

    d7 = base / "07-framework-coverage"
    rows7, summary7 = coverage.evaluate(_load(d7 / "frameworks.json"), specs, _load(d7 / "mappings.json"))
    report7 = ["| Framework | Priority | Criteria listed | Partial | Contextual only | None | High-potential gaps |", "|---|---:|---:|---:|---:|---:|---|"]
    report7 += [f"| {s['name']} | {s['priority']} | {s['criteria']} | {s['partial']} | {s['contextual']} | {s['none']} | {', '.join(s['backlog']) or 'none'} |" for s in summary7.values()]
    report7 += ["", "Coverage means automated evidence supports part of a criterion. It is not a compliance conclusion.", ""]
    for framework, s in summary7.items():
        report7 += [f"## {s['name']}", "", s["note"], ""]
        framework_rows = [r for r in rows7 if r["framework"] == framework]
        if framework_rows:
            report7 += ["| Criterion | Topic | Potential | Coverage | Sources |", "|---|---|---|---|---|"]
            report7 += [f"| {r['criterion']}{' (' + r['designation'] + ')' if 'designation' in r else ''} | {r['topic']} | {r['automation_potential']} | {r['coverage']} | {', '.join(r['sources']) or '—'} |" for r in framework_rows]
            report7 += [""]
    out["07-framework-coverage"] = {"summary": {"frameworks": summary7}, "rows": rows7, "report": report7,
                                    "inputs": _inputs(root, d7 / "frameworks.json", d7 / "mappings.json", d1 / "usecases.json")}
    return out


def headline(slug, summary):
    """A few numbers that describe each project's outcome, for the CLI and the site."""
    if slug == "01-control-automation":
        return {"use cases": summary["usecases"], "results": summary["results"], **summary["counts"]}
    if slug == "02-configuration-drift":
        return {"setting checks": summary["results"], **summary["counts"], "unauthorized drift": summary["unauthorized_drift"]}
    if slug == "03-control-evaluation":
        return {"vectors run": summary["vectors_run"],
                "production logic detecting every fault": f"{summary['production_detected_all']} of {summary['production_implementations']}",
                "weaker candidates with design gaps": f"{summary['candidate_design_deficiencies']} of {summary['candidate_implementations']}"}
    if slug == "04-evidence-data-flow":
        return {"flows": summary["flows"], "defective flows": summary["defective_flows"], "checks": summary["checks"],
                "PASS results downgraded": summary["downgraded_results"], "hidden failures revealed": summary["hidden_failures"]}
    if slug == "05-remediation-testing":
        return {**summary["decisions"], "automatic actions": summary["actions"], **{f"actions {k}": v for k, v in summary["action_counts"].items()}}
    if slug == "06-audit-process-testing":
        return {"deviations in sample": summary["sample_deviations"], "deviations in full population": summary["full_population_deviations"],
                "populations blocked": summary["populations_blocked"],
                "periodic controls with gaps": f"{summary['period_counts']['FAIL']} of {summary['periodic_controls']}",
                "evidence requests failing": f"{summary['request_counts']['FAIL']} of {summary['requests']}"}
    if slug == "07-framework-coverage":
        return {s["name"].split(" (")[0].split(",")[0]: f"{s['partial']} partial of {s['criteria']}"
                for s in summary["frameworks"].values() if s["criteria"]}
    raise ValueError("unknown project " + slug)


def write(results, out_dir, as_of):
    """Write one bundle per project plus a summary.json across projects."""
    root = Path(out_dir)
    summary = {"as_of": as_of, "synthetic": True, "projects": {}}
    for slug, result in results.items():
        folder = root / slug
        folder.mkdir(parents=True, exist_ok=True)
        doc = {"schema_version": 1, "project": slug, "title": TITLES[slug], "as_of": as_of, "synthetic": True,
               "inputs_sha256": result["inputs"], "summary": result["summary"], "results": result["rows"],
               **result.get("extra", {})}
        (folder / "results.json").write_text(json.dumps(doc, indent=2) + "\n")
        fields = []
        for row in result["rows"]:
            fields += [k for k in row if k not in fields]
        with (folder / "results.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in result["rows"]:
                writer.writerow({k: " | ".join(map(str, v)) if isinstance(v, list) else v for k, v in row.items()})
        report = [f"# {TITLES[slug]}", "", "Evidence: SYNTHETIC LAB DATA", "", "As of: " + as_of, "",
                  "These results test declared synthetic records. They are not an audit opinion or a compliance conclusion.", ""]
        (folder / "report.md").write_text("\n".join(report + result["report"]) + "\n")
        names = ["results.json", "results.csv", "report.md"]
        manifest = {"warning": "Hashes detect modification against this manifest. No signature or trusted timestamp is provided.",
                    "sha256": {n: hashlib.sha256((folder / n).read_bytes()).hexdigest() for n in names}}
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        summary["projects"][slug] = {"title": TITLES[slug], "headline": headline(slug, result["summary"]), "summary": result["summary"],
                                     "results_sha256": digest(result["rows"])}
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
