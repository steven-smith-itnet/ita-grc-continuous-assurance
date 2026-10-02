# 03 Control evaluation with seeded faults

**Role priority:** know how to evaluate a control.

**Objective:** evaluate an automated control the way an assessor would, then add the step that automation makes possible: feed the control known faults and check that it catches each one.

## Evaluating an automated control

| Question | What it means for an automated control | Evidence |
|---|---|---|
| Design | Does the logic test the stated objective and risk, including failure modes and missing data? | Specification, walkthrough of the logic, seeded-fault results |
| Implementation | Does it run against the full population in production? | Population reconciliation, run logs, scope configuration |
| Operating effectiveness | Did it run as designed throughout the period, and were its exceptions handled? | Run history, exception follow-up, [Project 06](../06-audit-process-testing/README.md) period coverage |
| IT general controls | Could someone change the logic or parameters without review? Who can alter results? | Change management and access controls over the control code, parameters and evidence store |
| Information used | Are the inputs complete and accurate? | [Project 04](../04-evidence-data-flow/README.md) reconciliation of each input flow |

Assessors often test an automated control with a small number of examples, then rely on IT general controls to show the logic did not change during the period. That approach assumes the logic was right to begin with. Seeded faults test that assumption directly.

## What this project builds

- [vectors.json](vectors.json): eight suites, one per use case in Project 01. Each suite has a known-good record set and seeded faults. Each fault states the result a correct control must return.
- [controleval.py](../../src/assurance/controleval.py): a small path-based mutation tool, four weaker candidate implementations, and a classifier that grades each result.
- Each suite runs the production logic. Four suites also run a candidate that looks reasonable but tests a weaker assertion.

## How results are graded

| Expected | Observed | Classification | Severity |
|---|---|---|---|
| FAIL | PASS | Missed failure | Critical. The control hides a real exception |
| UNKNOWN | PASS | Unknown reported as pass | Critical. Missing evidence looks like compliance |
| Any | Entity missing | Entity dropped from population | Critical. The denominator shrinks silently |
| PASS | FAIL | False alarm | Precision issue. Owners learn to ignore the control |
| UNKNOWN | FAIL | Unknown reported as failure | Precision issue. Conservative, but misdirects remediation |

An implementation with any critical miss has a design deficiency. One with only precision issues needs review before anyone relies on it.

## Expected results

| Use case | Implementation | Vectors | As expected | Critical misses | Verdict |
|---|---|---:|---:|---:|---|
| UC-01 | Production | 8 | 8 | 0 | Detected every seeded fault |
| UC-01 | Candidate: checks only that the IdP account is disabled | 8 | 3 | 5 | Design deficiency |
| UC-02 | Production | 9 | 9 | 0 | Detected every seeded fault |
| UC-02 | Candidate: checks only that a method is registered | 9 | 2 | 5 | Design deficiency |
| UC-03 | Production | 10 | 10 | 0 | Detected every seeded fault |
| UC-03 | Candidate: checks only that some approval exists | 10 | 5 | 3 | Design deficiency |
| UC-04 | Production | 9 | 9 | 0 | Detected every seeded fault |
| UC-05 | Production | 11 | 11 | 0 | Detected every seeded fault |
| UC-06 | Production | 10 | 10 | 0 | Detected every seeded fault |
| UC-07 | Production | 8 | 8 | 0 | Detected every seeded fault |
| UC-07 | Candidate: ignores scan coverage | 8 | 5 | 3 | Design deficiency |
| UC-08 | Production | 9 | 9 | 0 | Detected every seeded fault |

That is 109 vector runs: 89 as expected and 20 mismatches, all from the candidates.

## What the candidates miss

- **Leaver check on the IdP alone** passes a 48-hour disable, an active AWS access key, an uncorrelated worker, a missing disable time and a timestamp without a UTC offset.
- **MFA check on registration alone** passes an account with no enforcing policy, an SMS-only account, a string `"true"` in place of a boolean, and break-glass accounts without a valid exclusion.
- **Change check on any approval** passes self-approval, an approval that predates the final commit, and a pull request that was never merged. It also raises a false alarm on a properly approved emergency change.
- **Vulnerability check without scan coverage** passes assets that were never scanned, assets scanned 20 days ago, and findings with no first-seen time.

Each candidate would look fine in a demo with clean data. The seeded faults show the gap before anyone relies on the result.

## Evaluation record

The project writes one record per implementation to `artifacts/projects/03-control-evaluation/results.json` under `evaluations`. Each record lists the vectors, the misses, the verdict, the data flows the control depends on and its IT general control dependencies from the use-case specification. A reviewer adds the walkthrough notes, the preparer and reviewer names, and the conclusion.

## Framework mapping

| Framework | Criteria | Coverage |
|---|---|---|
| SOC 2 | CC4.1 ongoing and separate evaluations. CC5.2 technology general controls contextually | Partial |
| ISO 27001:2022 | 9.1 monitoring, measurement, analysis and evaluation. A.5.35 contextually | Partial |
| HIPAA | 164.308(a)(8) evaluation | Partial |

## Exercises

1. In `src/assurance/usecases.py`, change the UC-03 comparison so stale approvals are accepted. Re-run. The `stale-approval` vector becomes a missed failure and the verdict changes to design deficiency.
2. Add a vector to the UC-05 suite that sets `rotation_period_days` to 0. The production logic returns UNKNOWN. Decide whether that is the right expectation and record why.
3. Remove the `break-glass-valid` vector from the UC-02 suite. The candidate's other mismatches drop from 2 to 1, but its verdict stays design deficiency, because its five critical misses remain.

## Limits

The same author wrote the vectors and the production logic, so the production results are weaker evidence than vectors written or reviewed independently. Seeded faults cover the failure modes someone thought of. They do not prove the absence of others. Passing every vector shows design is sound for those cases. It does not show the control operated through a period, which needs run history and IT general controls.
