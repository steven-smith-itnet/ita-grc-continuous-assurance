# Good, better, best and the cost of operation

**Objective:** choose an implementation level based on risk, service complexity and operating capacity. “Best” means strongest fit for the stated requirement, not the greatest number of services.

## End-to-end maturity options

| Dimension | Good | Better | Best when justified |
|---|---|---|---|
| Scope | Reviewed service/resource register | Scheduled reconciled discovery | Event plus full reconciliation with ownership enforcement |
| Classification | Owner-reviewed register | Supported automated scans and steward workflow | Governed lineage, metadata protection and tested enforcement |
| Controls | Documented objectives and manual tests | Versioned executable catalog plus process reviews | Independently validated releases and continuous operating evidence |
| Evidence | Dated protected exports | Automated contracts, schema checks and versioned storage | Authenticated collection, signed packets and tested regional custody |
| Remediation | Owner/due-date register | ITSM integration and retest workflow | Recurrence analysis and preventive platform changes |
| Readiness | Reviewed checklist and sign-off | Automated evidence prechecks | Change-triggered reassessment of approved operating conditions |
| Reporting | Clear findings and coverage | Interactive drill-down and trends | Decision-oriented risk scenarios and evidence-quality SLOs |
| Recovery | Documented backup/restore process | Representative measured restore exercises | Isolated recovery under compromise and regional failure scenarios |

A regulated service may need selected “best” capabilities immediately while remaining simpler elsewhere. Conversely, a pilot should not deploy complex cross-cloud orchestration before its first control is trustworthy.

## Cost model

Estimate costs from measured volumes and current provider calculators. This project does not quote live prices or promise a fixed cloud bill.

`monthly operating cost = collection API/service charges + scan volume + log ingestion + retention storage + query compute + automation runtime + licensing + engineering/review labor`

Include data transfer, key-management operations, private endpoints, backup copies, minimum service commitments and regional variations. Labor includes maintaining adapters, investigating false positives, reviewing exceptions and preparing evidence. Free-tier assumptions should never be the only cost control.

## Measurement worksheet

1. Count accounts/subscriptions/projects, regions, resources and datasets.
2. Estimate change events and full-scan frequency.
3. Measure bytes per raw export, log-event volume and required retention.
4. Estimate classification scan bytes and supported/unsupported content.
5. Estimate query frequency and data scanned per query.
6. Identify licensed features and who needs access.
7. Add engineering and review hours per control and source integration.
8. Model a low, expected and high-volume scenario.
9. Set budget alerts and owner escalation before enabling broad collection.
10. Reconcile actual usage after the first pilot week and revise assumptions.

The local demo runs without cloud charges. Hosting cost depends on the selected GitHub/portfolio plan and deployment configuration.

## Build versus buy

Native provider tooling offers close integration but leaves cross-provider normalization and business-process evidence to solve. A commercial GRC or compliance platform can supply workflow, integrations and reporting but still depends on correct scope, configuration, data quality and owner review. A custom pipeline offers control over semantics but requires engineering maintenance and assurance of its own.

Evaluate each option with a proof of concept: exportability, source coverage, handling of unknowns, custom-control support, evidence retention, residency, identity integration, audit trail, licensing and exit plan. Do not select only on the appearance of a compliance dashboard.

## Staffing and sustainability

At minimum, name a program owner, source-system owners, an engineer for integrations, a control reviewer and an operations contact. One person may hold multiple roles in a small team, but independent approval boundaries still need a workable design. Document backup coverage for critical individuals.

Prefer a reliable narrow control set to a broad unmaintained catalog. Expand after the collection SLO, evidence quality and remediation ownership remain stable through real changes.

## Decision record

Record the chosen level for every major capability, the requirement driving it, alternatives considered, cost/complexity, residual risk and review trigger. Use [the architecture decision template](../templates/architecture-decision.md). Revisit when scope, customer commitments, service volume or provider availability changes.
