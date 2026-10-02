# Reproduce the lab from a clean checkout

**Objective:** execute real control-testing code against clearly identified synthetic evidence and inspect the resulting proof artifacts. No cloud account, paid service or API key is required.

## Prerequisites

Use Python 3.11 or later, a terminal and a checkout of this project. The control engine and tests use only the standard library. The website builder additionally uses the pinned Markdown dependency in `requirements.txt`. The implementation was exercised locally on Python 3.14. The standalone CI workflow also runs on Python 3.11.

From the project directory:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance run --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/demo
```

The fixed as-of date makes the fixture reproducible. Using today's date against an old fixture should eventually produce unknown results because its observations are stale. For real collection, use the actual reporting timestamp and authenticated observations rather than refreshing fixture dates to manufacture freshness.

## Inspect inputs before results

Open `fixtures/scope.json` to see nine declared assets. Open `fixtures/evidence.json` to see observations for only eight. The missing GCP resource deliberately tests whether the engine retains population gaps. Read the control catalog to see exact predicates and applicability.

The sample includes false storage prevention, a missing customer-managed-key predicate, missing ownership, an overdue access review, a change-separation failure, a slow restore, stale log evidence, missing MFA evidence, discovery gaps, an unverified private path and overdue vulnerabilities. Several observations combine into a single control result, so count results rather than field defects.

## Expected baseline

| Item | Expected value |
|---|---:|
| Declared assets | 9 |
| Control definitions | 14 |
| Asset/control pairs | 126 |
| Applicable pairs | 108 |
| PASS | 87 |
| FAIL | 9 |
| UNKNOWN | 12 |
| NOT_APPLICABLE | 18 |
| Accepted failures | 1 |
| Evaluated coverage | 88.89% |
| Passing share of applicable pairs | 80.56% |

The bundle contains `results.json`, `results.csv`, `report.md`, input snapshots and `manifest.json`. Inspect the reasons for each result and the evidence hashes. The manifest is local integrity checking, not a cryptographic signature by a trusted collector.

## Exercise 1: demonstrate a failure and repair

Copy the synthetic evidence to `artifacts/repaired-evidence.json`. Change only the `public_access_prevention` value for `aws-records-01` from false to true. Keep the source explicitly synthetic. Run the evaluator with `--evidence artifacts/repaired-evidence.json --out artifacts/repaired`. The STO-01 pair changes from FAIL to PASS, while the separate key failure remains.

This is a fixture mutation that demonstrates predicate behavior. A live remediation would require an actual approved cloud change, independent recollection and a retest. Do not describe editing JSON as fixing a cloud environment.

## Exercise 2: remove evidence

Delete a required observation or make its collection time older than 24 hours relative to the fixed as-of time. Run again. The result becomes UNKNOWN unless another fresh predicate already demonstrates failure. The applicable denominator remains stable.

## Exercise 3: test exceptions

Move EX-001's expiry to the as-of time. Re-run and confirm accepted risk becomes false. Make requester and approver identical and confirm the same behavior. The underlying KEY-01 failure remains present regardless of acceptance.

## Exercise 4: verify integrity

Copy the demo directory to another temporary directory, change a byte in its `results.json`, and run the verify command on the copy. Verification fails. Explain why replacing both data and manifest is outside this mechanism's protection.

## Exercise 5: inspect provider adapters

The unit suite feeds synthetic AWS, Azure and GCP API-shaped fixtures to a narrow public-prevention adapter. It tests missing fields and GCP inheritance. The adapters are not automatically wired into live collectors and do not establish effective access across all provider policies. Use the cloud guides to plan those integration tests.

## Strict pipeline mode

```bash
PYTHONPATH=src python3 -m assurance run --as-of 2026-09-30T12:00:00Z --strict
```

Exit code 2 means at least one FAIL or UNKNOWN. Exit code 1 indicates invalid input or integrity errors. Exit code 0 in ordinary demo mode means the evaluation completed, not that all controls passed. CI should use strict mode only with the expected gating policy and should separately test deliberately failing fixtures.

## Run the deeper projects

```bash
PYTHONPATH=src python3 -m assurance projects --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/projects/03-control-evaluation
```

The command writes one verifiable bundle per project under `artifacts/projects/` and prints a headline for each. The [projects overview](../projects/README.md) lists the expected results. Project 01 should report 59 results: 21 PASS, 21 FAIL, 8 UNKNOWN and 9 NOT_APPLICABLE.

## Build and serve the presentation site

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build_site.py
python3 -m http.server 8765 --directory site
```

Open `http://localhost:8765`. Use the dashboard filters, search the handbook and open the presentation. The source ZIP is built from an allowlist. The site works at a GitHub Pages project subpath because internal links are relative.

## What this proves

The code demonstrates repeatable predicate evaluation, explicit unknown handling, scope reconciliation, exception annotation and reproducible report generation. It does not prove live cloud deployment, actual business process operation, an external audit result or compliance certification. Those are subsequent execution stages described in the handbook.
