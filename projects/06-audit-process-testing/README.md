# 06 Audit process testing

**Role priority:** evaluate and test auditing processes.

**Objective:** test the audit process itself before relying on its conclusions. Four questions come first. Is the population complete? Can anyone reproduce the sample? Did the control operate in every window of the period? Is each piece of evidence fit for the period it claims to cover?

The fictional period runs from January 1 to June 30, 2026, in the style of a SOC 2 Type 2 examination, with fieldwork in the third quarter.

## What this project builds

- [plan.json](plan.json): the period, the sampling plan, the authorized approvers and the attributes to test for each population.
- [audittest.py](../../src/assurance/audittest.py): population reconciliation, reproducible sample selection, attribute testing, period-window coverage and evidence-request checks.
- [fixtures/](fixtures/populations.json): two populations, six periodic controls with their run history, and a register of ten evidence requests.

## 1. Reconcile the population before sampling

| Population | Source count | Extracted | Result |
|---|---:|---:|---|
| Privileged access grants across AWS, Azure and GCP | 60 | 60 | Reconciled. Sample drawn |
| Production changes from the ITSM change report | 41 | 40 | Not reconciled. No sample drawn |

The change extract filtered on change type "standard" and dropped one emergency change. Emergency changes carry the most risk, so a sample drawn from this extract would be drawn from the wrong population. The tool also blocks sampling when an item is dated outside the period or appears twice.

## 2. Draw a sample anyone can reproduce

Items are ranked by the SHA-256 hash of a recorded seed and the item ID, and the lowest ranks are selected. The same seed and population always give the same sample, on any machine and any Python version, and the order of the extract does not matter. The bundle records the seed and a hash of the population, so a reviewer can confirm the sample was not chosen after seeing the results.

Sample sizes in the plan are illustrative planning values: 1 for annual controls, 2 for quarterly or monthly, 5 for weekly, and 25 for daily or event-driven populations. The assessor's methodology sets the real sizes.

## 3. Compare the sample with testing every item

Three deviations are planted in the 60 access grants. Each grant is tested for approval before provisioning, an approver other than the grantee, an approver on the authorized list for that cloud, and a request ticket.

| Method | Items tested | Deviations found |
|---|---:|---:|
| Sample of 25 | 25 | 1: AG-021, approved 20 hours after access was provisioned |
| Every item, automated | 60 | 3: AG-021, plus AG-008 approved by the grantee, and AG-038 approved by an unauthorized approver |

The sample found a deviation, which is enough to report an exception. It missed the self-approval and the unauthorized approver. That is sampling risk, and it is the strongest argument for automated full-population testing where the data allows it.

## 4. Check every window of the period

| Control | Provider | Frequency | Windows covered | Result |
|---|---|---|---|---|
| PC-01 Weekly vulnerability scan | AWS | Weekly | 26 of 26 | PASS |
| PC-02 Weekly vulnerability scan | Azure | Weekly | 25 of 26 | FAIL: week of 2026-04-16 |
| PC-03 Weekly vulnerability scan | Google Cloud | Weekly | 26 of 26 | PASS |
| PC-04 Daily backup job for aws-claims-db | AWS | Daily | 179 of 181 | FAIL: 2026-03-14 and 2026-03-15 |
| PC-05 Quarterly privileged access review | All | Quarterly | 2 of 2 | PASS |
| PC-06 Monthly cloud security posture review | All | Monthly | 5 of 6 | FAIL: April 2026 |

Weekly windows roll in seven-day steps from the period start, so a partial calendar week at either edge does not create a false gap. Monthly and quarterly windows follow the calendar.

## 5. Check each evidence request

| Request | Evidence | Result | Reason |
|---|---|---|---|
| PBC-01 | Change population export | PASS | On time, covers the period, system source |
| PBC-02 | Access grant population | PASS | On time, covers the period, system source |
| PBC-03 | MFA policy screenshot | FAIL | No visible source system or timestamp |
| PBC-04 | Backup job history | FAIL | Starts March 1, so it cannot show operation from January 1 |
| PBC-05 | Quarterly access review | FAIL | Delivered 3 days late |
| PBC-06 | Incident response tabletop | UNKNOWN | Management attestation alone. Corroborate with system evidence |
| PBC-07 | Vulnerability scan history | PASS | On time, covers the period. Needed two rounds of rework |
| PBC-08 | Encryption configuration export | PASS | Point-in-time configuration, on time |
| PBC-09 | Training completion report | UNKNOWN | Does not state the dates it covers |
| PBC-10 | Restore exercise records | FAIL | Not delivered |

Seven of the nine delivered requests were accepted without rework. Rework rate and late delivery are measures of the audit process, not of the controls, and they belong in the readiness report.

## Framework mapping

| Framework | Criteria | Coverage |
|---|---|---|
| SOC 2 | CC4.1 ongoing and separate evaluations | Contextual |
| ISO 27001:2022 | 9.2 internal audit. A.5.35 and A.5.36 contextually | Partial |
| HIPAA | 164.308(a)(8) evaluation | Contextual |

## Exercises

1. Change the access-grant seed in `plan.json`. A different sample is drawn, and it may find zero, one or more of the three deviations. The full-population result does not change.
2. Add the missing emergency change to the change population. Reconciliation passes and a sample is drawn.
3. Add `2026-04-17` to PC-02's occurrences. The Azure scan control passes.

## Limits

Attribute tests here are simple field checks on synthetic records. Real attribute testing often needs judgment, such as whether an approver understood what they approved. Sample sizes and the three-deviation design are illustrative. The evidence register checks timing and type, not content. A reviewer still reads each item.
