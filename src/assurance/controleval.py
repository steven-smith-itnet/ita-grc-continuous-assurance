"""Project 03: evaluate whether a control's test logic detects the failures it claims to detect.

Each suite starts from a known-good record set and applies seeded faults
("mutations"). Every mutation states the result a correct control must return.
Running the production logic and a weaker candidate side by side shows how a
design gap is found before anyone relies on the control.
"""
import copy
from collections import Counter

from .usecases import REGISTRY, _time


def apply_ops(data, ops):
    """Apply set, delete and append operations addressed by slash-separated paths."""
    data = copy.deepcopy(data)
    for op in ops:
        *parents, last = op["path"].split("/")
        target = data
        for key in parents:
            target = target[int(key)] if isinstance(target, list) else target[key]
        if isinstance(target, list):
            last = int(last)
        if op["op"] == "set":
            target[last] = op["value"]
        elif op["op"] == "delete":
            del target[last]
        elif op["op"] == "append":
            target[last].append(op["value"])
        else:
            raise ValueError("unsupported operation: " + op["op"])
    return data


# Candidate implementations that look reasonable but test a weaker assertion.

def naive_leaver_access(data, params, now, uc="UC-01"):
    """Checks only that an identity-provider account is disabled."""
    accounts = {a["worker_id"]: a for a in data["idp_accounts"]["accounts"] if a.get("worker_id")}
    rows = []
    for worker in data["hr_workers"]["workers"]:
        if worker.get("status") != "terminated":
            continue
        account = accounts.get(worker["worker_id"])
        status = "FAIL" if account and account.get("enabled") else "PASS"
        rows.append({"usecase_id": uc, "entity_id": worker["worker_id"], "status": status, "reasons": []})
    return rows


def naive_privileged_mfa(data, params, now, uc="UC-02"):
    """Checks only that at least one MFA method is registered."""
    rows = []
    for account in data["idp_accounts"]["accounts"]:
        if not set(account.get("groups", [])) & set(params["privileged_groups"]):
            continue
        methods = (account.get("mfa") or {}).get("methods") or []
        rows.append({"usecase_id": uc, "entity_id": account["account_id"],
                     "status": "PASS" if methods else "FAIL", "reasons": []})
    return rows


def naive_change_approval(data, params, now, uc="UC-03"):
    """Checks only that the deployed commit has a pull request with any approval."""
    pulls = {p["merge_commit_sha"]: p for p in data["pull_requests"]["pull_requests"]}
    rows = []
    for deploy in data["deployments"]["deployments"]:
        if deploy.get("environment") != "prod":
            continue
        pull = pulls.get(deploy.get("commit_sha"))
        approved = pull and any(r.get("state") == "APPROVED" for r in pull.get("reviews", []))
        rows.append({"usecase_id": uc, "entity_id": deploy["deployment_id"],
                     "status": "PASS" if approved else "FAIL", "reasons": []})
    return rows


def naive_vulnerability_sla(data, params, now, uc="UC-07"):
    """Counts overdue open findings without checking whether the asset was scanned."""
    rows = []
    for asset in data["compute_assets"]["assets"]:
        overdue = [f for f in data["vulnerabilities"]["findings"]
                   if f["asset_id"] == asset["asset_id"] and f.get("status") == "open"
                   and f.get("severity") in params["sla_days"] and _time(f.get("first_seen_at"))
                   and (now - _time(f["first_seen_at"])).days > params["sla_days"][f["severity"]]]
        rows.append({"usecase_id": uc, "entity_id": asset["asset_id"],
                     "status": "FAIL" if overdue else "PASS", "reasons": []})
    return rows


CANDIDATES = {
    "naive_leaver_access": naive_leaver_access,
    "naive_privileged_mfa": naive_privileged_mfa,
    "naive_change_approval": naive_change_approval,
    "naive_vulnerability_sla": naive_vulnerability_sla,
}

CRITICAL = {"missed failure", "unknown reported as pass", "entity dropped from population"}


def classify(expected, got):
    if expected == got:
        return "as expected"
    if got == "MISSING":
        return "entity dropped from population"
    return {("FAIL", "PASS"): "missed failure",
            ("UNKNOWN", "PASS"): "unknown reported as pass",
            ("PASS", "FAIL"): "false alarm",
            ("PASS", "UNKNOWN"): "false unknown",
            ("FAIL", "UNKNOWN"): "failure reported as unknown",
            ("UNKNOWN", "FAIL"): "unknown reported as failure"}.get((expected, got), "unexpected result")


def verdict(outcomes):
    tally = Counter(o["classification"] for o in outcomes)
    if any(tally[c] for c in CRITICAL):
        return "Design deficiency: misses seeded faults"
    if len(outcomes) != tally["as expected"]:
        return "Precision issue: review before reliance"
    return "Detected every seeded fault"


def evaluate(specs, vectors, now):
    """Run every implementation in every suite. Return per-vector rows and per-implementation records."""
    by_id = {s["id"]: s for s in specs["usecases"]}
    rows, records = [], []
    for suite in vectors["suites"]:
        spec = by_id[suite["usecase_id"]]
        cases = [{"id": "baseline", "description": "Known-good record set", "ops": [], "expect": suite["baseline_expect"]}]
        cases += suite["mutations"]
        for name in suite["implementations"]:
            function = REGISTRY.get(name) or CANDIDATES[name]
            role = "production" if name in REGISTRY else "candidate"
            outcomes = []
            for case in cases:
                data = apply_ops(suite["baseline"], case["ops"])
                result = function(data, spec["parameters"], now, spec["id"])
                got = next((r["status"] for r in result if r["entity_id"] == suite["entity_id"]), "MISSING")
                classification = classify(case["expect"], got)
                outcome = {"usecase_id": spec["id"], "implementation": name, "role": role, "vector": case["id"],
                           "description": case["description"], "expected": case["expect"], "observed": got,
                           "classification": classification,
                           "status": "PASS" if classification == "as expected" else "FAIL"}
                outcomes.append(outcome)
            rows += outcomes
            tally = Counter(o["classification"] for o in outcomes)
            records.append({"usecase_id": spec["id"], "name": spec["name"], "implementation": name, "role": role,
                            "vectors": len(outcomes), "as_expected": tally["as expected"],
                            "critical_misses": sum(tally[c] for c in CRITICAL),
                            "other_mismatches": len(outcomes) - tally["as expected"] - sum(tally[c] for c in CRITICAL),
                            "verdict": verdict(outcomes),
                            "data_flows": spec.get("data_flows", []),
                            "itgc_dependencies": spec.get("itgc_dependencies", [])})
    return rows, records
