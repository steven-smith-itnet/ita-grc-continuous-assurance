# Build a continuous assurance program

A portfolio engineering case study inspired by the supplied Compliance Product Consultant role description, with the employer anonymized as **Acme**. This project models Acme's Technology GRC group using a fictional service called **Atlas Records**, synthetic evidence, and proposed operating procedures. The source employer's actual architecture, policies, findings, control implementations, and audit scope were not provided. Nothing here represents a real client engagement or an assurance opinion.

The [anonymized role excerpt](../ROLE-SOURCE.md) is retained for traceability.

The business problem is straightforward: a product team must explain which obligations apply to its service, demonstrate that controls operate, find exceptions early, and close findings with evidence that survives scrutiny. Adding a dashboard does not solve unclear scope, unreliable inventories, missing ownership, or poor evidence quality. This project builds those foundations first.

## Objectives translated from the role

| Role requirement | Problem to solve | Implementation | Concrete proof | Accountable decision |
|---|---|---|---|---|
| Drive compliance under the TechGRC manager | Teams interpret obligations differently | Approved charter, requirements register, control catalog and escalation matrix | Versioned scope and control records | Manager approves program scope and priorities |
| Continuous auditing and monitoring | Annual collection misses configuration drift and operating gaps | Scheduled inventory, event triggers, deterministic tests and human review | Dated runs, complete population and collection-gap reports | Control owner owns correction, assurance reviewer evaluates sufficiency |
| External audit | Evidence requests arrive late and cannot be reproduced | Period-based evidence index, PBC queue, walkthroughs and independently reviewed workpapers | Frozen export with provenance and sample rationale | External assessor determines conclusions |
| Service readiness | A launch inherits untested controls and dependencies | Gate review spanning design, implementation and operation | Readiness record with blockers, owners and expiry | Authorized service risk owner accepts residual risk |
| Compliance reports | Scores hide unknowns and provide no management action | Executive risk brief plus engineering detail and methodology | Machine-generated results joined to reviewed findings | TechGRC manager approves distribution |
| Identify and define issues | Scanner output lacks business context | Condition, criteria, cause, consequence and corrective action | Finding record with reproduction and affected population | Triage lead confirms severity |
| Root cause and remediation | Symptoms are fixed while defects repeat | Causal analysis, corrective/preventive work and independent retest | Before/after evidence, recurrence tests and closure approval | Owner implements, reviewer closes |
| Global collaboration | Handoffs, time zones and local obligations create gaps | Regional evidence custody, UTC records and explicit handoff receipts | RACI, runbooks, regional matrix and meeting decisions | Regional owners resolve jurisdiction and access decisions |
| AWS, Azure and GCP experience | Similar objectives have different enforcement mechanisms | Separate implementation tracks and native terminology | CLI examples, provider adapters and policy templates | Platform teams validate service-specific behavior |
| Framework knowledge | Teams mistake a configuration check for compliance | Scoped requirement mapping with human verification | Applicability decisions and residual evidence requirements | GRC/legal and assessor review mappings |
| Core IT processes | Cloud posture omits identities, deployments and recoverability | Join IAM, SDLC, vulnerability, logging and recovery evidence | Control walkthroughs with positive and negative tests | Service owners maintain process operation |
| GRC engineering | Evidence gathering cannot scale or be trusted | Versioned schema, policy tests, conservative evaluation and integrity manifest | Runnable Python lab with deliberate failure cases | Code reviewer approves changes to test logic |

## Fictional service and boundary

Atlas Records accepts documents, extracts metadata, stores originals, exposes an API, and sends operational telemetry to a monitoring service. Each cloud track is an alternative implementation of the same service. Running all three simultaneously is an advanced comparison exercise, not a requirement to replicate production data across clouds.

The sample population consists of nine storage workloads. The program design also covers application services, identities, repositories, pipelines, suppliers, endpoints and physical dependencies. The executable demo does not discover or verify all those systems. Its 14 control definitions evaluate 126 declared asset/control pairs using synthetic observations. Its limits are part of the evidence story.

Proposed sensitive-data variants include ordinary business confidential records, payment-adjacent records, and a healthcare workload. They are separate applicability exercises. Merely naming PCI DSS, HIPAA or HITRUST does not make each framework applicable to every asset.

## Deliverable boundaries

**Implemented locally:** conservative control evaluator, provider-schema adapters for one narrow storage baseline, regression tests, synthetic evidence bundle, searchable documentation site, presentation and downloadable source package.

**Implementation designs and lab templates:** cloud discovery, event collection, policy deployment, evidence storage, IAM federation, integrations, restore runbooks, audit workpapers and release gates. These require a funded sandbox, approved credentials and provider-specific validation before live use.

**Organizational procedures:** governance, legal interpretation, independent assessment, personnel controls and acceptance of residual risk. The project provides the operating artifacts and walkthroughs. Software does not execute management accountability.

## Acceptance criteria

1. Every supplied job requirement maps to a chapter, workflow and artifact.
2. Scope precedes measurement. Missing resources never silently disappear from the denominator.
3. Classification drives documented control selection and an explicit owner decision.
4. Each cloud track identifies permissions, collection points, enforcement, failure modes and cleanup.
5. Results retain collection time, control version, source references and uncertainty.
6. A reviewer can reproduce the synthetic run from a clean checkout without cloud credentials.
7. A reader can distinguish tested code, unexecuted templates, and future architecture.
8. The site can be served under a GitHub Pages project path or the existing portfolio site without a backend.

Start with [the delivery phases](01-phases.md), then [inventory](02-inventory.md). Use [the lab](24-lab.md) for a short demonstration before reading the full implementation sequence.
