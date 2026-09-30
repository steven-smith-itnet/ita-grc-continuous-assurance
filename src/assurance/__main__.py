import argparse
import csv
import hashlib
import json
from pathlib import Path
from .engine import evaluate


def read(path):
    return json.loads(Path(path).read_text())


def verify(directory):
    root = Path(directory).resolve()
    manifest = read(root / "manifest.json")
    for name, expected in manifest["sha256"].items():
        file = (root / name).resolve()
        if file.parent != root or not file.is_file():
            raise ValueError("invalid manifest path")
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError("integrity mismatch: " + name)
    return True


def write_bundle(result, out, inputs):
    root = Path(out)
    root.mkdir(parents=True, exist_ok=True)
    (root / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    for name, value in inputs.items():
        (root / name).write_text(json.dumps(value, indent=2) + "\n")
    fields = ["asset_id", "provider", "control_id", "title", "severity", "status", "accepted_risk", "reasons"]
    with (root / "results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in result["results"]:
            writer.writerow({**row, "reasons": " | ".join(row["reasons"])})
    summary = result["summary"]
    report = ["# Continuous control monitoring report", "",
              "Evidence: " + ("SYNTHETIC LAB DATA" if result["synthetic"] else "USER-SUPPLIED DATA, independently validate provenance"),
              "", "As of: " + result["as_of"], "",
              "This report evaluates declared predicates. It is not an audit opinion or framework certification.", "",
              f"Population: {summary['assets']} assets. Control definitions: {summary['controls']}.", "",
              "| State | Count |", "|---|---:|"]
    report += [f"| {key} | {value} |" for key, value in summary["counts"].items()]
    report += ["", f"Evaluated coverage: {summary['coverage_percent']}%. Passing share of applicable pairs: {summary['pass_percent_of_applicable']}%.",
               "", "Unknown evidence stays in the denominator. Accepted risk does not convert a failure to a pass.",
               "", "## Findings and collection gaps", ""]
    for row in result["results"]:
        if row["status"] in ("FAIL", "UNKNOWN"):
            report += [f"### {row['asset_id']} / {row['control_id']} — {row['status']}", "",
                       "Risk accepted: " + str(row["accepted_risk"]), "",
                       *["- " + reason for reason in row["reasons"]], ""]
    (root / "report.md").write_text("\n".join(report) + "\n")
    names = ["results.json", "results.csv", "report.md", *inputs]
    manifest = {"warning": "Hashes detect modification against this manifest. No signature or trusted timestamp is provided.",
                "sha256": {n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in names}}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--scope", default="fixtures/scope.json")
    run.add_argument("--evidence", default="fixtures/evidence.json")
    run.add_argument("--catalog", default="controls/catalog.json")
    run.add_argument("--exceptions", default="fixtures/exceptions.json")
    run.add_argument("--as-of", required=True)
    run.add_argument("--out", default="artifacts/demo")
    run.add_argument("--strict", action="store_true", help="exit 2 for FAIL or UNKNOWN, including accepted risk")
    check = sub.add_parser("verify")
    check.add_argument("directory")
    args = parser.parse_args()
    try:
        if args.command == "verify":
            verify(args.directory)
            print("Bundle hashes verified against local manifest (not proof of authenticity).")
            return 0
        scope, evidence, catalog, exceptions = map(read, (args.scope, args.evidence, args.catalog, args.exceptions))
        result = evaluate(scope, evidence, catalog, args.as_of, exceptions)
        write_bundle(result, args.out, {"scope.json": scope, "evidence.json": evidence,
                                     "catalog.json": catalog, "exceptions.json": exceptions})
        print(json.dumps(result["summary"], indent=2))
        return 2 if args.strict and any(r["status"] in ("FAIL", "UNKNOWN") for r in result["results"]) else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"Input or integrity error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
