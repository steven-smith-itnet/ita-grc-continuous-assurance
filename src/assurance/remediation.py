"""Project 05: decide whether a remediated finding can close, and test automatic remediation.

Closure criteria are defined before the fix: retest after the fix, from a collector
identity independent of the remediator, sustained across consecutive runs, applied
at the source of truth, and with sibling resources built from the same root cause
also passing. A closed finding that fails again is reopened.
"""
from collections import Counter

from .engine import timestamp

DECISIONS = ("CLOSE_ELIGIBLE", "KEEP_OPEN", "REOPEN")


def _status_in(run, control, entity):
    return next((r["status"] for r in run["results"] if r["control"] == control and r["entity"] == entity), None)


def _covers(run, control, entities):
    return all(_status_in(run, control, e) is not None for e in entities)


def decide(finding, runs, now):
    """Apply the closure criteria to one finding. Return the decision and reasons."""
    control, affected = finding["control"], finding["affected"]
    ordered = sorted((r for r in runs if timestamp(r["at"]) <= now), key=lambda r: timestamp(r["at"]))
    if finding["state"] == "closed":
        closed = timestamp(finding["closed_at"])
        recurred = [(r["run_id"], e) for r in ordered if timestamp(r["at"]) > closed
                    for e in affected if _status_in(r, control, e) == "FAIL"]
        if recurred:
            return "REOPEN", [f"closed {finding['closed_at']}, then failed again in {run} for {entity}" for run, entity in recurred]
        return "CLOSE_ELIGIBLE", ["remains closed; no recurrence in later runs"]
    declared = finding["remediation"].get("declared_fixed_at")
    if not declared:
        return "KEEP_OPEN", ["no remediation date declared"]
    fixed = timestamp(declared)
    criteria = finding["closure_criteria"]
    remediator = finding["remediation"]["remediator"]
    reasons = []
    after = [r for r in ordered if timestamp(r["at"]) > fixed and _covers(r, control, affected)]
    if not after:
        reasons.append("no retest run after the declared fix covers the affected resources")
    else:
        independent = [r for r in after if r["collector_identity"] != remediator]
        if len(independent) < len(after):
            reasons.append(f"{len(after) - len(independent)} retest run(s) used the remediator's own identity and do not count")
        streak = 0
        for run in reversed(independent):
            if all(_status_in(run, control, e) == "PASS" for e in affected):
                streak += 1
            else:
                break
        if streak < criteria["consecutive_passing_runs"]:
            reasons.append(f"{streak} of {criteria['consecutive_passing_runs']} required consecutive independent passing runs")
    if criteria.get("fix_at_source") and finding["remediation"]["method"] not in criteria["accepted_methods"]:
        reasons.append(f"fixed by {finding['remediation']['method']}; the root cause lives in "
                       f"{finding['root_cause']['artifact']}, so the next deployment can reintroduce the defect")
    sibling_control = finding["root_cause"].get("sibling_control", control)
    for sibling in finding["root_cause"].get("siblings", []):
        last = next((r for r in reversed(ordered) if _status_in(r, sibling_control, sibling) is not None), None)
        status = _status_in(last, sibling_control, sibling) if last else None
        if status is None:
            reasons.append(f"no run covers {sibling}, which shares the root cause")
        elif status == "FAIL":
            reasons.append(f"root cause not addressed: {sibling}, built from {finding['root_cause']['artifact']}, still fails")
        elif status != "PASS":
            reasons.append(f"{sibling}, built from {finding['root_cause']['artifact']}, could not be verified ({status})")
    return ("KEEP_OPEN", reasons) if reasons else ("CLOSE_ELIGIBLE", ["all closure criteria met; an independent reviewer may close"])


def evaluate_findings(register, runs, now):
    rows = []
    for finding in sorted(register["findings"], key=lambda f: f["id"]):
        decision, reasons = decide(finding, runs["runs"], now)
        rows.append({"finding_id": finding["id"], "control": finding["control"], "provider": finding["provider"],
                     "affected": finding["affected"], "state": finding["state"], "decision": decision, "reasons": reasons})
    return rows


def evaluate_actions(log, changes, now):
    """Test automatic remediation actions as controls in their own right."""
    rows = []
    actions = sorted(log["actions"], key=lambda a: a["action_id"])
    for action in actions:
        fail, unknown = [], []
        if action.get("runbook") not in log["approved_runbooks"]:
            fail.append(f"runbook {action.get('runbook')} is not on the approved list")
        if action.get("resource_tags", {}).get("remediation") == "exempt":
            fail.append("acted on a resource tagged remediation=exempt")
        window = timestamp(action["at"])
        repeats = [a for a in actions if a["resource_id"] == action["resource_id"] and a["runbook"] == action["runbook"]
                   and abs((timestamp(a["at"]) - window).total_seconds()) <= 86400]
        if len(repeats) > log["max_repeats_per_day"]:
            fail.append(f"{len(repeats)} runs on the same resource within 24 h; the source configuration keeps "
                        "reapplying the drift, so the remediation is looping")
        for change in changes["changes"]:
            if (change.get("status") == "approved" and change["resource_id"] == action["resource_id"]
                    and change["setting"] == action.get("setting") and timestamp(change["window_start"]) <= window):
                fail.append(f"reverses approved change {change['change_id']} on {change['setting']}")
        post = action.get("post_check")
        if post is None:
            unknown.append("no independent post-action check recorded")
        elif post != "PASS":
            fail.append(f"post-action check returned {post}")
        status = "FAIL" if fail else "UNKNOWN" if unknown else "PASS"
        rows.append({"action_id": action["action_id"], "provider": action["provider"], "resource_id": action["resource_id"],
                     "runbook": action["runbook"], "status": status,
                     "reasons": fail + unknown or ["approved runbook, in scope, verified by an independent post-check"]})
    return rows


def summarize(finding_rows, action_rows):
    decisions = Counter(r["decision"] for r in finding_rows)
    actions = Counter(r["status"] for r in action_rows)
    return {"findings": len(finding_rows), "decisions": {d: decisions[d] for d in DECISIONS},
            "actions": len(action_rows), "action_counts": {s: actions[s] for s in ("PASS", "FAIL", "UNKNOWN")}}
