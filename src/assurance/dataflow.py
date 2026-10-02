"""Project 04: test how control evidence gets from the source system to the control.

A flow is an ordered list of hops, such as source API, evidence store and GRC
platform. Each hop lists the records it holds. Reconciliation checks every hop
against the one before it for completeness, unexpected or duplicate records,
field-level accuracy and timeliness. Planted canary records must reach the final
hop. A defective flow then downgrades the control results that depend on it.
"""
import copy
from collections import Counter

from .engine import STATES, timestamp
from .usecases import REGISTRY


def _same(field, left, right):
    """Compare a key field. Timestamps compare as instants, so a format change is not a defect."""
    if field.get("type") == "timestamp":
        try:
            return timestamp(left) == timestamp(right)
        except (ValueError, TypeError, AttributeError):
            return False
    return left == right


def _check(flow, check, hop, status, reasons, records=()):
    return {"flow_id": flow["id"], "provider": flow["provider"], "check": check, "hop": hop, "status": status,
            "reasons": reasons, "records": sorted(records)}


def reconcile(flow):
    """Return check rows plus the record IDs that failed completeness or accuracy."""
    rows, missing_ids, altered = [], set(), {}
    fields, slo = flow["key_fields"], flow["slo_minutes"]
    source = flow["hops"][0]
    declared = source.get("declared_total")
    truncated = False
    if declared is not None:
        if declared != len(source["records"]):
            truncated = True
            rows.append(_check(flow, "source count", source["name"], "FAIL",
                               [f"extract holds {len(source['records'])} of {declared} records reported by the source; "
                                "the remaining records were never retrieved"]))
        else:
            rows.append(_check(flow, "source count", source["name"], "PASS",
                               [f"extract holds all {declared} records reported by the source"]))
    origin = {r["id"]: r for r in source["records"]}
    for upstream, downstream in zip(flow["hops"], flow["hops"][1:]):
        label = f"{upstream['name']} -> {downstream['name']}"
        up = {r["id"]: r for r in upstream["records"]}
        ids = [r["id"] for r in downstream["records"]]
        down = {r["id"]: r for r in downstream["records"]}
        missing = sorted(set(up) - set(down))
        missing_ids |= set(missing)
        rows.append(_check(flow, "completeness", label, "FAIL" if missing else "PASS",
                           [f"{len(missing)} of {len(up)} records did not arrive"] if missing else
                           [f"all {len(up)} records arrived"], missing))
        extra = sorted(set(down) - set(up))
        duplicates = sorted(i for i, n in Counter(ids).items() if n > 1)
        rows.append(_check(flow, "no unexpected or duplicate records", label,
                           "FAIL" if extra or duplicates else "PASS",
                           ([f"records not present upstream: {', '.join(extra)}"] if extra else []) +
                           ([f"duplicated records: {', '.join(duplicates)}"] if duplicates else []) or
                           ["no unexpected or duplicate records"], extra + duplicates))
        mismatches = []
        for rid in sorted(set(up) & set(down)):
            changed = [f["name"] for f in fields
                       if not _same(f, up[rid]["fields"].get(f["name"]), down[rid]["fields"].get(f["name"]))]
            if changed:
                mismatches.append(rid)
                altered.setdefault(rid, set()).update(changed)
        rows.append(_check(flow, "accuracy", label, "FAIL" if mismatches else "PASS",
                           [f"{rid}: {', '.join(sorted(altered[rid]))} changed"
                            for rid in mismatches] or ["key fields unchanged for every matched record"], mismatches))
        late, unknown = [], []
        for rid in sorted(set(origin) & set(down)):
            try:
                lag = (timestamp(down[rid]["at"]) - timestamp(origin[rid]["at"])).total_seconds() / 60
            except (KeyError, TypeError, ValueError):
                unknown.append(rid)
                continue
            if lag < 0 or lag > slo:
                late.append(f"{rid} ({lag:.0f} min)")
        status = "FAIL" if late else "UNKNOWN" if unknown else "PASS"
        rows.append(_check(flow, "timeliness from source", label, status,
                           ([f"exceeds the {slo} min SLO: " + ", ".join(late)] if late else []) +
                           ([f"arrival time missing: {', '.join(unknown)}"] if unknown else []) or
                           [f"every record arrived within {slo} min of the source event"]))
    final = {r["id"] for r in flow["hops"][-1]["records"]}
    for canary in flow.get("canaries", []):
        arrived = canary in final
        rows.append(_check(flow, "canary", flow["hops"][-1]["name"], "PASS" if arrived else "FAIL",
                           [f"planted record {canary} " + ("reached the final hop" if arrived else "did not reach the final hop")],
                           [canary]))
    return rows, {"missing": sorted(missing_ids), "altered": {rid: sorted(names) for rid, names in altered.items()},
                  "truncated": truncated}


def assess_impact(flow, defects, usecase_rows, specs, data, now):
    """Downgrade dependent PASS results. Where a field was altered and the source value is known,
    recompute the control with the source value to show what the defect concealed."""
    feed = flow.get("feeds")
    if not feed:
        return []
    affected = set()
    if defects["truncated"]:
        affected |= set(feed.get("entity_scope", []))
    source = {r["id"]: r for r in flow["hops"][0]["records"]}
    for rid in defects["missing"] + list(defects["altered"]):
        entity = feed.get("entity_map", {}).get(source[rid]["fields"].get(feed["entity_field"])) \
            or source[rid]["fields"].get(feed["entity_field"])
        if entity:
            affected.add(entity)
    spec = next(s for s in specs["usecases"] if s["id"] == feed["usecase_id"])
    impacts = []
    for row in usecase_rows:
        if row["usecase_id"] != feed["usecase_id"] or row["entity_id"] not in affected:
            continue
        impact = {"flow_id": flow["id"], "usecase_id": row["usecase_id"], "entity_id": row["entity_id"],
                  "original_status": row["status"]}
        if row["status"] != "PASS":
            impact.update(adjusted_status=row["status"],
                          reasons=["result already reports a failure or gap; a defective feed cannot make it pass"])
            impacts.append(impact)
            continue
        impact.update(adjusted_status="UNKNOWN",
                      reasons=[f"input evidence failed {flow['id']} reconciliation; this PASS cannot be relied on"])
        patch = feed.get("recompute")
        if patch:
            corrected = copy.deepcopy(data)
            records = corrected[patch["dataset"]][patch["collection"]]
            for rid, names in defects["altered"].items():
                key = source[rid]["fields"].get(feed["entity_field"])
                for record in records:
                    if record.get(patch["key"]) == key:
                        for name in names:
                            record[name] = source[rid]["fields"][name]
            recomputed = REGISTRY[spec["implementation"]](corrected, spec["parameters"], now, spec["id"])
            again = next((r for r in recomputed if r["entity_id"] == row["entity_id"]), None)
            if again:
                impact["recomputed_from_source"] = again["status"]
                impact["reasons"].append("recomputed with source values: " + "; ".join(again["reasons"]))
        impacts.append(impact)
    return impacts


def run(flows, usecase_rows, specs, data, now):
    checks, verdicts, impacts = [], [], []
    for flow in flows["flows"]:
        rows, defects = reconcile(flow)
        checks += rows
        failed = [r for r in rows if r["status"] != "PASS"]
        verdicts.append({"flow_id": flow["id"], "name": flow["name"], "provider": flow["provider"],
                         "hops": [h["name"] for h in flow["hops"]], "checks": len(rows),
                         "failed_checks": len(failed),
                         "verdict": "DEFECTIVE" if failed else "RELIABLE",
                         "feeds": (flow.get("feeds") or {}).get("usecase_id")})
        impacts += assess_impact(flow, defects, usecase_rows, specs, data, now)
    return checks, verdicts, impacts


def counts(rows):
    tally = Counter(r["status"] for r in rows)
    return {s: tally[s] for s in STATES}
