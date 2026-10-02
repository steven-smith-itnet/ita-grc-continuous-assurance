# Delivery phases and entry gates

This is a proposed delivery sequence, not a claim that an organization completed the work. The time ranges are planning assumptions for a small service and a dedicated working group. Procurement, licensing, legal review, missing source access and discovery complexity may dominate elapsed time.

| Phase | Planning range | Inputs and prerequisites | Work products | Exit evidence |
|---|---|---|---|---|
| 0. Charter and authority | Week 1 | Sponsor, service description, business commitments | Charter, RACI, scope candidates, assumptions and risk register | Manager approves scope and decision rights |
| 1. Discover and classify | Weeks 2–3 | Cloud hierarchy and read-only access | Resource and data inventories, data flows, classification and ownership | Reconciled population, unresolved gaps assigned |
| 2. Design controls | Weeks 3–4 | Applicability and risk assessment | Control catalog, framework mapping, evidence contracts | Owners accept test methods and evidence expectations |
| 3. Establish foundations | Weeks 4–6 | Accounts/projects, budget, identity baseline | Logging, evidence storage, keys, collection identities and pipeline | Positive/negative tests and access review |
| 4. Automate a vertical slice | Weeks 6–8 | Reliable inventory and source APIs | Tested collectors, normalizers, evaluator, findings queue | Known-failure detection and collection-failure handling |
| 5. Extend process coverage | Weeks 8–10 | IAM, SDLC, backup and ITSM access | Joiner/mover/leaver tests, change evidence, recovery exercise | Process operation demonstrated across a defined period |
| 6. Remediate and prepare audit | Weeks 10–12 | Evaluated results and owner capacity | Findings, root causes, PBC index, management report | Independent retests and unresolved risk disclosure |
| 7. Operate and improve | Ongoing | Approved runbooks and service ownership | SLOs, drift response, periodic reassessment, control-version reviews | Sustained coverage and reviewed trend data |

## Phase 0: establish who can decide

Interview the service owner, GRC manager, cloud leads, identity owner, data steward, legal/privacy contact and recovery owner. Obtain a product data-flow description and existing contractual commitments. Record customer-facing claims separately from internally proposed targets. Identify the person authorized to accept service risk and the people prohibited from approving their own exceptions.

Write a one-page charter that names the service boundary, exclusions, intended audience, delivery budget, first audit period and dependency owners. Mark unknowns with owners and due dates. A missing answer is a discovery task, not a reason to claim the service is ready.

## Phase 1: establish the denominator

Export cloud hierarchy, reconcile discovered resources with billing and deployment records, and discover data stores. Include suspended accounts, ephemeral resources, replicas, log archives and unmanaged projects. Assign a stable service ID to each asset. Then map datasets and data flows onto resources. Do not confuse a resource list with a data inventory.

Select pilot assets representing a restricted dataset, a routine internal workload and an intentional collection failure. The phase succeeds when the team can explain the differences between expected, discovered, classified and evaluated populations.

## Phase 2: make requirements testable

For each obligation, write a control objective, owner, implementation statement, population, frequency, expected evidence, exact failure condition, exception route and retest method. Decide which portions are automatic, manual or hybrid. Agree evidence expectations with the intended assessor before building a large collection system.

A useful first control is anonymous-access prevention on storage. It crosses inventory, classification, cloud APIs, preventive policy, test code, a finding and a verified repair. Complete that chain before automating fifty disconnected checks.

## Phase 3: secure the assurance platform

Create dedicated collection identities with only the read permissions required. Keep collection, evaluation, storage administration and report approval separate. Establish secrets handling, log retention, key ownership, clock synchronization and a protected code repository. Validate that a collector can read required metadata but cannot modify a workload or delete evidence.

Store sensitive raw evidence in approved regional locations. Export only synthetic or explicitly approved sanitized artifacts to the portfolio. The public-site builder in this project copies an allowlist and regenerates its report from the synthetic fixture.

## Phases 4–5: prove behavior before expanding scope

Use unit tests for rule logic, contract tests for provider exports and integration tests in a sandbox. Exercise timeouts, permission denial, partial pages, stale timestamps, new accounts and provider schema changes. Build a collector health dashboard before interpreting control pass rates.

Expand from posture into operating controls: actual access removals, changes with independent approval, restore exercises, incident escalation and vulnerability closure. A configuration snapshot cannot establish sustained operation throughout a reporting period.

## Phases 6–7: make the program repeatable

Freeze the period, preserve the population, generate the evidence index and conduct a mock walkthrough. Every exception receives an owner and deadline. The GRC manager reviews the management report, including coverage gaps. After launch, refresh applicability when a service adds data types, regions, suppliers or major architecture changes.

## Stop and re-plan triggers

A newly discovered regulated dataset changes scope. A collector missing a region invalidates that region's coverage claim. A key-custody restriction changes the evidence architecture. A restore exercise exceeding recovery objectives changes launch readiness. Treat these as planned decision gates with documented responses, not late surprises.

Artifacts: [scope](../fixtures/scope.json), [requirements and controls](04-controls.md), [operating model](22-operating-model.md), [production rollout](28-production.md).
