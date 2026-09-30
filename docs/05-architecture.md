# Architecture and trust boundaries

**Objective:** make evidence collection reproducible, protect sensitive artifacts and preserve the distinction between measurements and decisions.

## Logical architecture

<div class="flow"><span>Cloud + IT systems</span><span>Read-only collectors</span><span>Regional raw vault</span><span>Normalize + validate</span><span>Versioned tests</span><span>Findings + review</span><span>Assurance report</span></div>

The service catalog and data catalog supply scope and classification to the evaluator. The requirements register supplies control applicability. An exception register supplies approved risk decisions. These inputs join at evaluation time but remain independently versioned.

## Trust boundary 1: production to collection

Collectors obtain configuration and process metadata through scoped identities. Prefer workload federation and short-lived credentials to stored access keys. A collector should not have the same permissions as a remediation function. Partition identity by provider and sensitive boundary so a compromised collector does not read every evidence source.

Record authentication context, requested scope, start/end time, source versions and errors. Do not grant broad data-content access merely because metadata collection was approved. A classification scanner may need content access, while a storage policy collector usually does not. Treat these as separate roles.

## Trust boundary 2: raw evidence to normalized facts

Raw evidence is encrypted, access logged and stored under an approved retention policy. Normalization converts provider-specific fields into a documented canonical vocabulary. Preserve null, absent, denied, unsupported and not-applicable states separately. A default `false` or `true` that hides a missing field can corrupt the entire program.

Only normalized data with valid schema and provenance enters the evaluator. Failed normalization creates a collection issue. Validation should include tenant/resource identity checks, schema version, plausible timestamps, duplicate detection and scope reconciliation. The local engine demonstrates several of these checks, while authenticating provider identities remains a production integration.

## Trust boundary 3: results to management decisions

An evaluator produces a result for a stated predicate and population. Findings add risk context, ownership and remediation plans. Management decides whether a residual risk is acceptable. The same person should not implement a correction, approve an exception and independently close the finding.

Keep dashboards read-only relative to the evidence store. Ticket integrations use idempotent keys such as service/resource/control/version/episode. Group duplicate symptoms without erasing affected-resource detail. A reopened failure creates a recurrence record rather than overwriting the prior closure.

## Data stores and processing options

Good: daily exports, versioned files and a reviewed issue register. Better: event-driven collection, durable queue, object storage and a queryable results database. Best: governed regional evidence stores, policy-controlled aggregation, signed releases and measured collector SLOs. Choose the least complex design that meets evidence and operations requirements.

For AWS, combine Config and service APIs with EventBridge, Lambda or Step Functions, S3 and Athena. For Azure, use Resource Graph and service APIs with Functions or Automation, Storage and Log Analytics. For GCP, use Cloud Asset Inventory and APIs with Cloud Run jobs, Pub/Sub, Cloud Storage and BigQuery. These are proposed compositions, not services that inherently establish compliance.

## Reliability and failure handling

Set timeouts on every network call. Retry only safe read operations with bounded exponential backoff and jitter. Preserve continuation tokens and checkpoint progress. Send persistent failures to a dead-letter queue with an owner. Reconcile periodically even when event processing is enabled. Treat provider maintenance or an expired credential as an availability issue for the assurance service.

Run collectors in approved regions. Track data residency for metadata and findings as well as raw documents. A central dashboard can aggregate counts without replicating restricted evidence. Cross-region redundancy must respect retention and contractual constraints.

## Threat model

| Threat | Consequence | Countermeasure | Validation |
|---|---|---|---|
| Collector credential theft | Unauthorized metadata access | Least privilege, federation, scoped roles | Denied write and cross-scope read tests |
| Tampered control logic | False assurance | Protected branch, review, immutable release identifier | Negative regression fixtures |
| Deleted or replaced evidence | Inability to substantiate a result | Versioning, access separation, approved retention and signed manifest | Tamper and recovery exercise |
| Forged timestamps | Misleading operating-period claim | Authenticated sources, server timestamps, clock monitoring | Future/stale evidence rejection |
| Metadata downgrade | Weaker controls on sensitive data | Governed classification writes and approval | Unauthorized relabeling test |
| Public-site data leakage | Exposure of customer or employee information | Synthetic-only build allowlist | Package-content inspection |
| Queue backlog | Stale results appear current | Freshness checks, backlog SLO and report banner | Stop collector and observe unknown state |

The prototype writes local hashes to detect changes against a manifest. That is not a digital signature or an independent timestamp. A production design needs trusted identity, protected signing keys and storage controls in addition to hashing. See [evidence engineering](16-evidence.md).
