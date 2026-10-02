# Deeper projects

Seven runnable sub-projects extend the base lab toward the priorities in a second, more specific description of the same role. Each project has its own code, synthetic fixtures for AWS, Azure and Google Cloud, regression tests, expected results and a write-up. The employer remains anonymized as **Acme**. See [the role source](../ROLE-SOURCE.md) for the anonymized priorities.

The base lab evaluates 14 controls over supplied facts, such as `privileged_mfa_verified: true`. These projects go one layer down. They derive those facts from the records that produce them, test the test logic, test the evidence pipeline, decide when a fix is really fixed, and test the audit process itself.

## Role priorities and the project that answers each

| Role priority | Project | What it demonstrates |
|---|---|---|
| Most of the work is building control automation use cases | [01 Control automation use-case library](01-control-automation/README.md) | Eight use cases that join HR, identity, CI/CD, backup, scanner and cloud API records into control results |
| GRC engineering: automated controls and configuration | [02 Configuration baseline and drift](02-configuration-drift/README.md) | One storage baseline normalized across three providers, with drift classified as authorized or unauthorized |
| Know how to evaluate a control | [03 Control evaluation with seeded faults](03-control-evaluation/README.md) | 109 seeded-fault vectors that separate sound control logic from plausible but weak logic |
| Test how the data gets to where it needs to go | [04 Evidence data-flow testing](04-evidence-data-flow/README.md) | Hop-by-hop reconciliation of four evidence pipelines, and the effect of each defect on control results |
| Evaluate and test remediation | [05 Remediation verification](05-remediation-testing/README.md) | Closure criteria applied to six findings, plus tests of automatic remediation actions |
| Evaluate and test auditing processes | [06 Audit process testing](06-audit-process-testing/README.md) | Population reconciliation, reproducible sampling, period coverage and evidence-request quality |
| SOC 2 first, then ISO 27001, then HIPAA. PCI DSS is owned by another team | [07 SOC 2-first framework coverage](07-framework-coverage/README.md) | Coverage computed from declared mappings, with the next use cases to build |
| AWS, Azure and GCP, at least one in depth | All projects | Every project carries provider-native fixtures for all three clouds |

## Run every project

From the repository root, with Python 3.11 or later and no third-party packages:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance projects --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/projects/01-control-automation
```

The `projects` command writes one bundle per project under `artifacts/projects/`. Each bundle holds `results.json`, `results.csv`, `report.md` and a SHA-256 `manifest.json` that the existing `verify` command checks. A `summary.json` collects the headline results. The command refuses any evidence fixture that is not marked synthetic.

## Expected headline results

All results use the fixed as-of time 2026-09-30 12:00 UTC.

| Project | Headline |
|---|---|
| 01 | 59 results from 8 use cases: 21 PASS, 21 FAIL, 8 UNKNOWN, 9 NOT_APPLICABLE |
| 02 | 24 setting checks: 17 PASS, 3 FAIL, 1 UNKNOWN, 3 NOT_APPLICABLE. 3 drift events, 1 unauthorized |
| 03 | 109 vectors. All 8 production implementations detect every seeded fault. All 4 weaker candidates miss faults |
| 04 | 4 flows, 3 defective. 3 PASS results downgraded to UNKNOWN, and 1 of them is a hidden failure |
| 05 | 6 findings: 1 eligible to close, 4 kept open, 1 reopened. 7 automatic actions: 2 PASS, 4 FAIL, 1 UNKNOWN |
| 06 | Sample found 1 of 3 planted deviations. 1 population blocked. 3 of 6 periodic controls missed a window. 4 of 10 evidence requests failed |
| 07 | SOC 2: 11 of 38 listed criteria have partial automated evidence. ISO 27001: 14 of 24. HIPAA: 9 of 20 |

## How the projects connect

The projects share one fictional story, so a defect found in one shows up in the others.

1. Project 01 passes worker W-1004 on the HR data in the evidence store.
2. Project 04 finds that the HR integration dropped a UTC offset for that record. Recomputed from the HR source, W-1004 fails.
3. Project 03 shows that a simpler leaver check would also have missed an active AWS access key for another worker.
4. Project 02 detects an unauthorized change to `aws-records-01`. Project 04 shows the SIEM never received the CloudTrail event for that change.
5. Project 05 keeps that finding open, because only one of three required passing runs has happened since the fix.
6. Project 05 also blocks closure of a base-image vulnerability, because a sibling server built from the same image still fails in Project 01.
7. Project 07 turns the remaining uncovered SOC 2 criteria into the next use cases to build.

## Boundaries

Every record is synthetic. The cloud API shapes follow provider documentation, but no command ran against a cloud account. Framework mappings are candidates for review, not compliance conclusions. Policy values such as SLAs and rotation limits are fictional Acme choices, not framework requirements.
