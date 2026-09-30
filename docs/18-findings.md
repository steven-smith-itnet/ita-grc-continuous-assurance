# Findings, root cause, remediation and exceptions

**Objective:** turn a technical observation into a well-defined issue that an owner can fix and an independent reviewer can close.

## Write the finding before assigning the fix

A finding includes criteria, condition, population, evidence, cause, consequence and recommended action. The criteria identify the approved expectation. The condition states what was observed, when and how. Separate confirmed facts from hypotheses about cause or impact.

Example: “The restricted records bucket lacks the project's explicit anonymous-access prevention baseline in the 2026-09-30 synthetic observation.” This is supported by the fixture. “Customer records were exfiltrated” is not supported and must not appear in the finding. Missing prevention creates a risk condition that may require further exposure analysis.

## Triage and severity

Confirm the resource, service owner, data class, exposure, business criticality and evidence confidence. Identify whether there is an active incident. Preserve native scanner severity and record local severity with rationale. Combine related observations into a problem record when they share a cause, but retain affected-resource detail and separate closure evidence.

Proposed remediation targets should be approved by management and based on risk. Do not invent framework-wide deadlines from an internal severity label. Escalate overdue high-risk findings through the established management path.

## Root-cause method

1. Reproduce the condition with reliable evidence.
2. Establish a timeline of relevant deployments, approvals, policy changes and failed detections.
3. Ask why the control failed, then test each hypothesis against records.
4. Distinguish immediate cause, systemic cause and detection gap.
5. Identify the process or reusable artifact that must change to prevent recurrence.
6. Record contradictory evidence and unresolved questions rather than forcing a tidy story.

For the synthetic storage example, a plausible hypothesis is an old IaC module that omitted the setting. Validate that hypothesis by examining the module version and deployment record. If true, correcting only the bucket leaves the cause intact. Update the module, scan all resources created from it, and add a regression test.

## State machine

`New → Validated → Assigned → Planned → In progress → Ready for retest → Closed`

Alternative paths include rejected with rationale, duplicate linked to a parent, accepted risk with expiry, and reopened after failed retest or recurrence. Record every transition with actor, time, reason and evidence references. The remediation owner cannot independently approve their own closure.

## Retest criteria

Define success before work begins. Re-run the original test on the affected population, verify the corrected configuration through an independent collection identity, and validate any business impact. For operating controls, allow an appropriate observation period and verify repeated operation rather than a single corrected screenshot.

Close only when the criteria are met and the reviewer accepts evidence. Record residual risk and any follow-on preventive work. Keep the original finding and evidence intact.

## Exception record

An exception needs scope, requirement/control, rationale, requester, independent approver, compensating measures, start, expiry, review frequency and exit plan. The risk owner must have authority over the consequence. Exceptions should not self-renew without review.

The demo validates independent requester/approver names, approval time, expiry, rationale and compensation for a matching asset/control. It does not authenticate those identities. An accepted exception preserves `FAIL` and adds `accepted_risk: true`. Unknown evidence cannot be cured by accepting the risk of a different known failure.

## Good, better, best

Good: reviewed finding register with clear owners and retest evidence. Better: integrated ITSM workflow and due-date escalation. Best: recurrence analysis, reusable corrective controls and measured reduction in repeat causes. Measure closure quality as well as speed.

Artifacts: [finding](../templates/finding.md), [root cause](../templates/root-cause.md), [exception register](../fixtures/exceptions.json).
