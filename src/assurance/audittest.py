"""Project 06: test the audit process itself.

Covers four questions an assessor asks before relying on a control test:
1. Is the population complete? Reconcile the extract to the source system count.
2. Can anyone reproduce the sample? Selection uses a recorded seed and SHA-256
   ranking, so it is stable across Python versions and machines.
3. Did the control operate in every period it should have? Check each window.
4. Is the evidence fit for the period? Check each evidence request's timing,
   source and type.
"""
import hashlib
from collections import Counter
from datetime import date, timedelta

from .engine import STATES, digest, timestamp


def select_sample(ids, size, seed):
    """Rank items by SHA-256 of seed and ID, then take the lowest. Anyone with the seed can reproduce it."""
    ranked = sorted(ids, key=lambda i: hashlib.sha256(f"{seed}|{i}".encode()).hexdigest())
    return sorted(ranked[:min(size, len(ranked))])


def _attribute_failures(item, attributes, approvers):
    failures = []
    for attribute in attributes:
        if attribute == "approved_before_provisioned":
            try:
                if timestamp(item["approved_at"]) > timestamp(item["provisioned_at"]):
                    failures.append("approved after access was provisioned")
            except (KeyError, TypeError, ValueError):
                failures.append("approval or provisioning time missing")
        elif attribute == "approver_not_grantee":
            if item.get("approver") == item.get("grantee"):
                failures.append("grantee approved their own access")
        elif attribute == "approver_authorized":
            if item.get("approver") not in approvers.get(item.get("system"), []):
                failures.append(f"{item.get('approver')} is not an authorized approver for {item.get('system')}")
        elif attribute == "ticket_present":
            if not item.get("ticket"):
                failures.append("no request ticket")
        else:
            raise ValueError("unknown attribute " + attribute)
    return failures


def test_population(population, plan, period):
    """Reconcile, sample and attribute-test one population. Also test every item, to show what sampling can miss."""
    start, end = timestamp(period["start"]), timestamp(period["end"])
    items = population["items"]
    ids = [i["id"] for i in items]
    outside = sorted(i["id"] for i in items if not start <= timestamp(i[population["date_field"]]) <= end)
    duplicates = sorted(i for i, n in Counter(ids).items() if n > 1)
    declared = population.get("declared_total")
    record = {"population_id": population["id"], "description": population["description"], "provider": population["provider"],
              "declared_total": declared, "extracted": len(items), "population_sha256": digest(sorted(ids)),
              "reconciliation": [], "seed": plan["seed"], "frequency": plan["frequency"]}
    if declared != len(items):
        record["reconciliation"].append(f"extract holds {len(items)} items; the source reports {declared}")
    if outside:
        record["reconciliation"].append("items dated outside the period: " + ", ".join(outside))
    if duplicates:
        record["reconciliation"].append("duplicate items: " + ", ".join(duplicates))
    if record["reconciliation"]:
        record.update(status="UNKNOWN", sample=[], sample_size=0, sample_deviations=[], full_population_deviations=[],
                      conclusion="Population not reconciled. No sample drawn; reconcile the extract with the source first.")
        return record
    size = plan["sample_sizes"][plan["frequency"]]
    sample = select_sample(ids, size, plan["seed"])
    by_id = {i["id"]: i for i in items}
    def deviations(selection):
        out = []
        for item_id in selection:
            failures = _attribute_failures(by_id[item_id], plan["attributes"], plan["authorized_approvers"])
            if failures:
                out.append({"id": item_id, "failures": failures})
        return out
    found = deviations(sample)
    everything = deviations(sorted(ids))
    missed = sorted({d["id"] for d in everything} - {d["id"] for d in found})
    record.update(status="FAIL" if found else "PASS", sample=sample, sample_size=len(sample),
                  sample_deviations=found, full_population_deviations=everything, missed_by_sample=missed,
                  conclusion=(f"{len(found)} deviation(s) in a sample of {len(sample)}; the assessor evaluates the effect. "
                              if found else f"No deviations in a sample of {len(sample)}. ")
                  + f"Testing all {len(ids)} items found {len(everything)} deviation(s).")
    return record


def _windows(kind, start, end):
    """Yield (label, first day, last day) for every window overlapping the period."""
    if kind == "daily":
        day = start
        while day <= end:
            yield day.isoformat(), day, day
            day += timedelta(days=1)
    elif kind == "weekly":
        # Rolling seven-day windows from the period start, so partial calendar weeks at the edges
        # do not create false gaps.
        day = start
        while day <= end:
            yield f"week of {day.isoformat()}", day, min(day + timedelta(days=6), end)
            day += timedelta(days=7)
    elif kind == "monthly":
        day = start.replace(day=1)
        while day <= end:
            following = (day.replace(day=28) + timedelta(days=4)).replace(day=1)
            yield day.strftime("%Y-%m"), max(day, start), min(following - timedelta(days=1), end)
            day = following
    elif kind == "quarterly":
        day = start.replace(month=3 * ((start.month - 1) // 3) + 1, day=1)
        while day <= end:
            month = day.month + 3
            following = date(day.year + (month > 12), (month - 1) % 12 + 1, 1)
            yield f"{day.year}-Q{(day.month - 1) // 3 + 1}", max(day, start), min(following - timedelta(days=1), end)
            day = following
    else:
        raise ValueError("unsupported frequency " + kind)


def test_period_coverage(controls, period):
    """Each periodic control must have at least one successful occurrence in every window of the period."""
    start, end = date.fromisoformat(period["start"][:10]), date.fromisoformat(period["end"][:10])
    rows = []
    for control in sorted(controls["controls"], key=lambda c: c["id"]):
        occurred = {date.fromisoformat(d) for d in control["occurrences"]}
        windows = list(_windows(control["frequency"], start, end))
        missed = [label for label, first, last in windows
                  if not any(first <= d <= last for d in occurred)]
        rows.append({"control_id": control["id"], "name": control["name"], "provider": control["provider"],
                     "frequency": control["frequency"], "windows": len(windows), "covered": len(windows) - len(missed),
                     "missed": missed, "status": "FAIL" if missed else "PASS",
                     "reasons": [f"no occurrence in {len(missed)} window(s): " + ", ".join(missed)] if missed
                     else [f"occurred in all {len(windows)} windows"]})
    return rows


def test_requests(register, period):
    """Check each evidence request for timeliness, period fit and evidence reliability."""
    start, end = timestamp(period["start"]), timestamp(period["end"])
    reliable = set(register["reliable_types"])
    rows = []
    for request in sorted(register["requests"], key=lambda r: r["id"]):
        fail, unknown = [], []
        delivered = request.get("delivered_at")
        if delivered is None:
            rows.append({"request_id": request["id"], "control": request["control"], "owner": request["owner"],
                         "evidence_type": request.get("evidence_type"), "rework": request.get("rework_count", 0),
                         "status": "FAIL", "reasons": ["not delivered"]})
            continue
        if timestamp(delivered) > timestamp(request["due_at"]):
            days = (timestamp(delivered) - timestamp(request["due_at"])).days
            fail.append(f"delivered {days} day(s) after the due date")
        covers_from, covers_to = request.get("covers_from"), request.get("covers_to")
        if not covers_from or not covers_to:
            unknown.append("evidence does not state the dates it covers")
        elif timestamp(covers_to) < start or timestamp(covers_from) > end:
            fail.append("evidence covers dates outside the audit period")
        elif request.get("period_control") and timestamp(covers_from) > start:
            fail.append(f"evidence starts {covers_from[:10]}; it does not show operation from the start of the period")
        kind = request.get("evidence_type")
        if kind == "screenshot" and not request.get("shows_source_and_timestamp"):
            fail.append("screenshot without visible source system and timestamp")
        elif kind == "attestation":
            unknown.append("management attestation alone; corroborate with system evidence")
        elif kind not in reliable | {"screenshot", "attestation"}:
            unknown.append(f"evidence type {kind} not recognized")
        status = "FAIL" if fail else "UNKNOWN" if unknown else "PASS"
        rows.append({"request_id": request["id"], "control": request["control"], "owner": request["owner"],
                     "evidence_type": kind, "rework": request.get("rework_count", 0), "status": status,
                     "reasons": fail + unknown or ["on time, covers the period, reliable source"]})
    return rows


def counts(rows):
    tally = Counter(r["status"] for r in rows)
    return {s: tally[s] for s in STATES}
