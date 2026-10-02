# 04 Evidence data-flow testing

**Role priority:** test how the data gets to where it needs to go.

**Objective:** before relying on an automated control, prove that its input arrived complete, unaltered and on time at every hop between the source system and the control. Then show what each pipeline defect does to the control results that depend on it.

Auditors call this testing the completeness and accuracy of information produced by the entity. A control that passes on an incomplete or altered extract has not passed. SOC 2 CC2.1 asks for relevant, quality information to support internal control. This project makes that check executable.

## The model

A flow is an ordered list of hops, such as source API, evidence store and GRC platform. Each hop lists the records it holds and when each record arrived. Each flow names the key fields that must not change, a timeliness SLO and, where possible, a planted canary record.

| Check | Question | Typical defect it catches |
|---|---|---|
| Source count | Does the extract hold every record the source reports? | Pagination stopped after the first page |
| Completeness | Did every record from the previous hop arrive? | An ingestion filter dropped a class of events |
| Unexpected or duplicate | Did anything appear that was not upstream? | Retries without idempotency, injected records |
| Accuracy | Are the key fields unchanged? Timestamps compare as instants | A mapping dropped a UTC offset or truncated a value |
| Timeliness | Did each record arrive within the SLO from the source event? | A stalled queue or a batch job that skipped a run |
| Canary | Did a record planted at the source reach the final hop? | A broken path that produces no errors |

## The four flows

| Flow | Provider | Path | Planted defect | Verdict |
|---|---|---|---|---|
| DF-01 | AWS | CloudTrail, S3 log archive, SIEM index | The SIEM ingestion filter drops S3 control-plane events, including the `PutBucketPublicAccessBlock` call that changed `aws-records-01` | DEFECTIVE |
| DF-02 | Azure | Resource Graph query, evidence store, GRC platform | The export read the first page of Defender for Cloud assessments and ignored the continuation token: 10 of 12 records | DEFECTIVE |
| DF-03 | Google Cloud | Cloud Asset Inventory export, BigQuery, evaluator input | None. A labeled canary bucket arrives with every other record | RELIABLE |
| DF-04 | HR to identity | HR system report, integration platform, GRC evidence store | The integration appends Z to local times from the India HR instance without converting them | DEFECTIVE |

Resource Graph reports `totalRecords` and returns a `$skipToken` when more pages remain. An extract that holds fewer records than `totalRecords` is incomplete, even though every record it does hold is accurate.

## Expected results

| Result | Count |
|---|---:|
| Flows | 4 |
| Defective flows | 3 |
| Checks run | 37 |
| Checks passed | 34 |
| Checks failed | 3 |
| PASS results downgraded to UNKNOWN | 3 |
| Hidden failures revealed by recomputation | 1 |

## Effect on control results

| Flow | Use case | Entity | Project 01 result | Adjusted | Recomputed from source |
|---|---|---|---|---|---|
| DF-01 | UC-04 | aws-acct-prod | PASS | UNKNOWN | n/a |
| DF-02 | UC-07 | azure-vm-intake-01 | FAIL | FAIL | n/a |
| DF-02 | UC-07 | azure-vm-web-01 | PASS | UNKNOWN | n/a |
| DF-04 | UC-01 | W-1004 | PASS | UNKNOWN | FAIL |

- **A canary passed while real events were lost.** UC-04 passed `aws-acct-prod` because its canary arrived in 6 minutes. DF-01 shows the SIEM silently dropped an S3 control-plane change. A canary proves one path for one event type.
- **Truncation affects every entity in scope.** The two missing Defender records could belong to either Azure server, so the passing server is downgraded. The failing server stays FAIL, because a defective feed cannot turn a proven failure into a pass.
- **A pipeline defect hid a real failure.** W-1004's termination was 09:00 local time in India (+05:30), which is 03:30 UTC. The integration stored it as 09:00 UTC. On the stored value, the account was disabled 22 hours later and passed. Recomputed with the source value, the lag is 27.5 hours against a 24-hour SLA, and the control fails.
- **Format changes are not defects.** The other HR records arrive with a different offset format but the same instant. The accuracy check compares instants, so they pass.

## Designing these tests in production

1. Draw the path for each control input, from the system of record to the place the control reads it. Name the owner of each hop.
2. Choose key fields that the control logic depends on. Those are the fields to compare.
3. Get a count from the source that is independent of the extract, such as `totalRecords`, a report row count or an API count call.
4. Plant canaries that look like real records and are labeled synthetic. Route their removal through change control.
5. Run reconciliation on every collection, not once at onboarding. Store the results as evidence of the control's input quality.
6. Wire the result to the control. A defective input should change dependent PASS results to UNKNOWN automatically.

## Framework mapping

| Framework | Criteria | Coverage |
|---|---|---|
| SOC 2 | CC2.1 quality information. CC7.2 contextually | Partial |
| ISO 27001:2022 | 9.1, A.8.15 and A.8.16 | Contextual |
| HIPAA | 164.312(b) audit controls and 164.312(c)(1) integrity | Contextual |

## Exercises

1. In [flows.json](flows.json), add `evt-05` back to the DF-01 SIEM hop. DF-01 becomes RELIABLE, and UC-04 keeps its PASS.
2. Set DF-02's `declared_total` to 10. The source-count check passes, and `azure-vm-web-01` keeps its PASS. Then ask how you would know the real total.
3. In DF-04, change W-1004's value in both the integration hop and the GRC hop to `2026-09-20T03:30:00Z`. Accuracy passes and the impact list is empty. The Project 01 fixture still holds the wrong value, which shows that fixing the pipeline does not correct data that already landed.

## Limits

Each hop's record list is synthetic. In production, each hop needs its own collector identity, and the reconciliation job itself needs change control and monitoring. Accuracy compares declared key fields only. A field outside that list can change without detection.

Source: [flows.json](flows.json), [dataflow.py](../../src/assurance/dataflow.py).
