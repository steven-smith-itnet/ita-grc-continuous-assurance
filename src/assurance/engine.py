"""Deterministic, conservative tests over a declared population and dated observations."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

STATES = ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def check_value(value, test, now):
    op = test["op"]
    if op == "true":
        if type(value) is not bool:
            raise ValueError("expected boolean")
        return value
    if op == "nonempty":
        if not isinstance(value, str):
            raise ValueError("expected text")
        return bool(value.strip())
    if op == "one_of":
        if not isinstance(value, str):
            raise ValueError("expected text")
        return value in test["values"]
    if op == "lte":
        if type(value) not in (int, float) or not 0 <= value < float("inf"):
            raise ValueError("expected nonnegative finite number")
        return value <= test["value"]
    if op == "within_days":
        age = (now - timestamp(value)).total_seconds() / 86400
        if age < 0:
            raise ValueError("future event timestamp")
        return age <= test["value"]
    raise ValueError("unsupported operator")


def validate(scope, evidence, catalog):
    if scope.get("schema_version") != 1 or evidence.get("schema_version") != 1:
        raise ValueError("unsupported schema version")
    assets = scope.get("assets", [])
    if not assets:
        raise ValueError("empty population cannot be assessed")
    ids = [a["id"] for a in assets]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scope asset")
    if any(a.get("provider") not in ("aws", "azure", "gcp") for a in assets):
        raise ValueError("unknown provider")
    control_ids = [c["id"] for c in catalog]
    if len(control_ids) != len(set(control_ids)) or not catalog:
        raise ValueError("empty or duplicate control catalog")
    seen = set()
    for item in evidence.get("assets", []):
        if item["id"] in seen:
            raise ValueError("duplicate evidence asset")
        seen.add(item["id"])
        if item["id"] not in ids:
            raise ValueError("evidence asset missing from declared scope")
    for c in catalog:
        if not c.get("tests") or c.get("max_age_hours", 0) <= 0:
            raise ValueError("invalid control definition")


def exception_valid(exception, asset, control, now):
    try:
        return (exception["asset_id"] == asset and exception["control_id"] == control
                and exception["status"] == "approved"
                and bool(exception["approver"].strip())
                and exception["approver"] != exception["requester"]
                and bool(exception["rationale"].strip())
                and bool(exception["compensating_control"].strip())
                and timestamp(exception["approved_at"]) <= now < timestamp(exception["expires_at"]))
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def evaluate(scope, evidence, catalog, as_of, exceptions=None):
    validate(scope, evidence, catalog)
    now = timestamp(as_of)
    observed = {a["id"]: a for a in evidence.get("assets", [])}
    rows = []
    for asset in sorted(scope["assets"], key=lambda x: x["id"]):
        record = observed.get(asset["id"], {})
        facts = record.get("facts", {})
        for control in catalog:
            row = {"asset_id": asset["id"], "provider": asset["provider"],
                   "control_id": control["id"], "title": control["title"],
                   "severity": control["severity"], "status": "UNKNOWN",
                   "accepted_risk": False, "evidence_ids": [], "reasons": []}
            applies = control.get("applies", {})
            missing_scope = [key for key in applies if key not in asset]
            if missing_scope:
                row["reasons"] = ["scope metadata missing: " + ", ".join(missing_scope)]
            elif any(asset[k] not in values for k, values in applies.items()):
                row["status"] = "NOT_APPLICABLE"
                row["reasons"] = ["outside documented control population"]
            else:
                failures, unknown = [], []
                for test in control["tests"]:
                    field = test["field"]
                    fact = facts.get(field)
                    if not isinstance(fact, dict) or fact.get("value") is None:
                        unknown.append(field + ": missing observation")
                        continue
                    try:
                        if not isinstance(fact.get("source"), str) or not fact["source"].strip():
                            raise ValueError("missing evidence source")
                        age = (now - timestamp(fact["collected_at"])).total_seconds() / 3600
                        if age < 0 or age > control["max_age_hours"]:
                            raise ValueError("stale or future observation")
                        row["evidence_ids"].append(digest(fact))
                        if not check_value(fact["value"], test, now):
                            failures.append(field + ": expected " + json.dumps(test, sort_keys=True))
                    except (ValueError, TypeError, KeyError, AttributeError) as exc:
                        unknown.append(field + ": " + str(exc))
                # A proven failure remains a failure even when other facts are unavailable.
                row["status"] = "FAIL" if failures else "UNKNOWN" if unknown else "PASS"
                row["reasons"] = failures + unknown or ["all defined predicates satisfied"]
                if row["status"] == "FAIL":
                    row["accepted_risk"] = any(exception_valid(e, asset["id"], control["id"], now)
                                               for e in exceptions or [])
            rows.append(row)
    counts = Counter(r["status"] for r in rows)
    applicable = len(rows) - counts["NOT_APPLICABLE"]
    assessed = counts["PASS"] + counts["FAIL"]
    return {"schema_version": 1, "as_of": as_of, "synthetic": evidence.get("synthetic") is True,
            "scope_sha256": digest(scope), "evidence_sha256": digest(evidence),
            "catalog_sha256": digest(catalog), "exceptions_sha256": digest(exceptions or []),
            "summary": {"assets": len(scope["assets"]), "controls": len(catalog),
                        "counts": {s: counts[s] for s in STATES},
                        "coverage_percent": round(100 * assessed / applicable, 2) if applicable else None,
                        "pass_percent_of_applicable": round(100 * counts["PASS"] / applicable, 2) if applicable else None,
                        "accepted_failures": sum(r["accepted_risk"] for r in rows)},
            "results": rows}
