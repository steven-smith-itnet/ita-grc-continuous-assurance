# Service readiness and launch decisions

**Objective:** determine whether a service can enter the intended operating state with known controls, reliable support and explicitly owned residual risk. Readiness is a decision process supported by evidence.

## Trigger the review early

Run readiness review for a new service, significant architecture change, new sensitive data class, new region, major supplier change or new customer assurance commitment. The service owner supplies scope, dependencies and intended launch date. The GRC team coordinates evidence requirements and escalates unresolved issues under the manager's authority.

Do not wait until the release is built to discover that data residency, identity integration or recovery cannot meet the requirement. Phase-zero scope and classification are readiness inputs.

## Gate matrix

| Gate | Required evidence | Example blocker | Decision owner |
|---|---|---|---|
| Scope and data | Approved boundary, inventory, flows and classification | Unknown restricted-data destination | Service/data owner |
| Identity | Privileged access, workload identity and lifecycle test | Uncontrolled production admin access | Identity/platform owner |
| Protection | Access, encryption, keys, network and retention tests | Unsupported key recovery dependency | Security/data owner |
| SDLC | Approved deployment and rollback evidence | Untraceable production artifact | Engineering owner |
| Detection | Required logs, canary and response ownership | No alert route for critical event | Security operations |
| Recovery | BIA, RPO/RTO and representative restore exercise | Failed integrity validation | Continuity/service owner |
| Suppliers | Dependency assessment and required agreements | Unapproved subprocessor or missing obligation | Procurement/legal/security |
| Operations | Runbooks, support, regional handoff and capacity | No owner outside one time zone | Operations owner |
| Assurance | Control evidence, known findings and report limitations | Material coverage gap hidden from decision | GRC manager |

## Decision options

Ready: required criteria met with evidence. Conditionally ready: explicitly authorized limited operation with bounded scope, compensating measures, expiry and follow-up. Not ready: blocking criteria unmet. Define what kinds of risk cannot be accepted by the proposed approver and how to escalate them.

A conditional decision should name the exact service version, region, data classes, allowed users and expiration. It should not become a blanket approval for future changes.

## Conduct the review

1. Distribute a concise pre-read with the scope, architecture and evidence index.
2. Identify unresolved findings and unknowns before the meeting.
3. Have technical owners demonstrate the highest-risk controls and recovery path.
4. Challenge assumptions about inherited controls, provider responsibility and process evidence.
5. Record decisions, dissent, action owners and deadlines.
6. Obtain approval from the authorized decision maker.
7. Monitor conditions after launch and automatically flag expiring acceptance.
8. Reopen review when the approved boundary changes materially.

## Scenario walkthrough

The Azure synthetic workload restores in seven hours against the project's four-hour target. Engineering proposes a launch because backups are successful. The readiness reviewer asks for the measured exercise, affected customer commitments and a recovery improvement plan. The decision cannot rely on backup job success alone. A conditional launch, if authorized, might limit critical workloads until a representative restore meets the agreed objective.

## Good, better, best

Good: repeatable checklist with named approvals and linked evidence. Better: reusable service patterns and automated evidence prechecks. Best: change-triggered reassessment, measured readiness lead time and continuous monitoring of approved conditions. Automate evidence gathering and gate consistency while retaining accountable human decisions.

Artifact: [readiness review template](../templates/readiness-review.md). The local project does not issue an actual service launch approval.
