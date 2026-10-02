"""Project 07: SOC 2-first framework coverage from the automated evidence in this repository.

Coverage is computed from mappings declared next to each use case and project. A
mapping to an unknown criterion is an error, so typos cannot inflate coverage.
"partial" means the evidence supports part of the criterion. "contextual" means it
informs the criterion without testing it. Nothing here is marked "full", because
no automated test satisfies a criterion on its own.
"""
from collections import Counter

LEVELS = ("partial", "contextual", "none")


def collect(specs, mappings):
    """Return (framework, criterion) -> list of supporting sources."""
    found = {}
    for spec in specs["usecases"]:
        for framework, entries in spec["frameworks"].items():
            for entry in entries:
                found.setdefault((framework, entry["id"]), []).append(
                    {"source": spec["id"], "name": spec["name"], "project": "01", "coverage": entry["coverage"]})
    for item in mappings["mappings"]:
        for framework, entries in item["frameworks"].items():
            for entry in entries:
                found.setdefault((framework, entry["id"]), []).append(
                    {"source": item["id"], "name": item["name"], "project": item["project"], "coverage": entry["coverage"]})
    return found


def evaluate(catalog, specs, mappings):
    found = collect(specs, mappings)
    known = {(f, c["id"]) for f, body in catalog["frameworks"].items() for c in body.get("criteria", [])}
    unknown = sorted(f"{f} {c}" for f, c in found if (f, c) not in known)
    if unknown:
        raise ValueError("mapping to a criterion missing from the catalog: " + ", ".join(unknown))
    bad = sorted({s["coverage"] for v in found.values() for s in v} - {"partial", "contextual"})
    if bad:
        raise ValueError("unsupported coverage value: " + ", ".join(bad))
    rows, summary = [], {}
    for framework, body in sorted(catalog["frameworks"].items(), key=lambda kv: kv[1]["priority"]):
        criteria = body.get("criteria", [])
        framework_rows = []
        for criterion in criteria:
            sources = found.get((framework, criterion["id"]), [])
            levels = {s["coverage"] for s in sources}
            level = "partial" if "partial" in levels else "contextual" if levels else "none"
            row = {"framework": framework, "criterion": criterion["id"], "topic": criterion["topic"],
                   "automation_potential": criterion["automation_potential"], "coverage": level,
                   "sources": sorted(f"{s['source']} ({s['coverage']})" for s in sources)}
            if "designation" in criterion:
                row["designation"] = criterion["designation"]
            framework_rows.append(row)
        rows += framework_rows
        tally = Counter(r["coverage"] for r in framework_rows)
        summary[framework] = {"name": body["name"], "priority": body["priority"], "criteria": len(criteria),
                              **{level: tally[level] for level in LEVELS},
                              "backlog": [r["criterion"] for r in framework_rows
                                          if r["coverage"] == "none" and r["automation_potential"] == "high"],
                              "note": body.get("note", "")}
    return rows, summary
