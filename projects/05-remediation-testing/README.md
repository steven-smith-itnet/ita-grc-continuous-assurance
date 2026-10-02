# 05 Remediation verification

**Role priority:** evaluate and test remediation.

**Objective:** decide whether a fixed finding can close, using criteria agreed before the fix. Then test automatic remediation as a control in its own right, because a remediation job can fail, loop, or undo an approved change.

## Closure criteria

Each finding in [findings.json](fixtures/findings.json) carries its criteria. The decision logic in [remediation.py](../../src/assurance/remediation.py) applies them to a history of control runs in [runs.json](fixtures/runs.json).

| Criterion | Why it matters |
|---|---|
| A retest ran after the declared fix and covered the affected resources | A screenshot from before the fix is not a retest |
| The retest used a collector identity independent of the remediator | The person who made the fix should not produce the evidence that it worked |
| A set number of consecutive independent runs passed, three by default | One passing run can catch a resource between drift cycles |
| The fix was made at the source of truth, such as infrastructure as code, an image rebuild or a policy | A console fix leaves the module or template that caused the defect unchanged |
| Siblings built from the same root cause also pass | Fixing one server built from a vulnerable image leaves the others exposed |
| A closed finding has not failed again since closure | Recurrence reopens the finding and its root cause |

Runs dated after the as-of time are ignored, so a later result cannot close a finding early.

## Expected results: findings

| Finding | Provider | Decision | Reason |
|---|---|---|---|
| F-201 Public access prevention removed on aws-records-01 | AWS | KEEP_OPEN | 1 of 3 required consecutive independent passing runs |
| F-202 Shared key allowed on azure-records-01 | Azure | KEEP_OPEN | The only retest ran under the remediator's own identity |
| F-203 Uniform bucket-level access disabled on gcp-records-01 | Google Cloud | CLOSE_ELIGIBLE | 4 independent passing runs, fixed in the module, sibling bucket passes |
| F-204 Self-approval allowed in atlas-web | Azure Repos | REOPEN | Closed 2026-09-05, then failed again in run R-03 |
| F-205 Critical vulnerability in the GKE node pool | Google Cloud | KEEP_OPEN | The node pool passes, but `aws-vm-worker-01` from the same base image still fails, and `gcp-vm-extract-01` is unverified |
| F-206 ePHI bucket with a provider-managed key | AWS | KEEP_OPEN | No retest since the fix, and the fix was made in the console rather than the module |

CLOSE_ELIGIBLE is a recommendation. An independent reviewer still closes the finding and records residual risk.

## Testing automatic remediation

Automatic remediation is a control. It needs its own tests. [actions.json](fixtures/actions.json) holds seven actions from AWS Config remediation, Azure Policy remediation tasks and a GCP event-driven function.

| Test | Failure it catches |
|---|---|
| Runbook is on the approved list | An unreviewed script changing production |
| Resource is not tagged as exempt | Remediation acting on a resource under legal hold or a documented exception |
| No more than two runs on the same resource within 24 hours | A loop where infrastructure as code or a job keeps reapplying the drift |
| Does not reverse an approved change in [the Project 02 change register](../02-configuration-drift/fixtures/changes.json) | Automation overriding a decision made through change control |
| An independent post-action check passed | An action that reported success without changing the setting |

| Action | Provider | Result | Reason |
|---|---|---|---|
| AR-01 | AWS | PASS | Approved runbook, verified afterward |
| AR-02 | Azure | PASS | Approved runbook, verified afterward |
| AR-03, AR-04, AR-05 | AWS | FAIL | Three runs in 24 hours on `aws-records-02`, each reversing approved change CHG-2041 |
| AR-06 | Google Cloud | FAIL | Acted on a bucket tagged `remediation=exempt` during a legal-hold export |
| AR-07 | Azure | UNKNOWN | No independent post-action check recorded |

The AWS loop is the useful lesson. Versioning on `aws-records-02` was suspended under an approved change. The remediation rule kept turning it back on, and the re-ingest job kept suspending it. Either the change needs an exception that the rule honors, or the change should not have been approved.

## Native remediation mechanisms

| Provider | Mechanism | What to test |
|---|---|---|
| AWS | AWS Config remediation actions that run Systems Manager Automation documents | Approved document, retry limits, exclusion tags, post-check by a different identity |
| Azure | Azure Policy `modify` and `deployIfNotExists` effects with remediation tasks | Assignment scope and exemptions, the managed identity's permissions, task results |
| Google Cloud | Organization policy constraints for prevention, and event-driven functions for correction | Constraint scope and exceptions, function identity, idempotency |

## Framework mapping

| Framework | Criteria | Coverage |
|---|---|---|
| SOC 2 | CC4.2 deficiencies evaluated and communicated for corrective action | Partial |
| ISO 27001:2022 | 10.2 nonconformity and corrective action | Partial |
| HIPAA | 164.308(a)(1)(ii)(B) risk management | Contextual |

## Exercises

1. Add two more independent passing runs for `aws-records-01` after 11:30 but before the as-of time. F-201 becomes CLOSE_ELIGIBLE.
2. Change F-206's method from `console` to `iac`. The finding stays open, because no retest has run yet.
3. Raise `max_repeats_per_day` to 3. AR-03 to AR-05 still fail, because each reverses CHG-2041.

## Limits

The run history is synthetic and already normalized. In production, retest evidence comes from the same collectors as Projects 01 and 02, and the finding register lives in an ITSM or GRC tool with its own access controls. Three consecutive runs is a fictional Acme criterion. A periodic control, such as a quarterly review, needs the next occurrence rather than repeated daily runs.
