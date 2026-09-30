# Data protection, keys, retention and privacy

**Objective:** protect data throughout creation, use, movement, storage, recovery and disposal. Inventory and classification determine which measures apply, while technical tests establish whether those measures actually work.

## Select controls from the data contract

For each dataset, identify purpose, sensitivity, authorized consumers, locations, retention schedule, deletion conditions, legal holds, recovery objectives and key-custody requirements. A restricted class may trigger customer-managed keys in this project's policy, but customer-managed encryption is not a universal requirement for every framework or every workload.

Separate encryption at rest, transport protection, access authorization, masking/tokenization, data loss prevention, minimization and deletion. Each reduces a different risk. Encryption at rest does not prevent an authorized but overprivileged application from returning plaintext.

## Implement the storage and transport baseline

1. Restrict anonymous access and review authenticated sharing separately.
2. Select approved transport protocols and validate client behavior, endpoint configuration and certificate lifecycle.
3. Configure provider-managed or customer-managed encryption based on the risk decision.
4. Restrict key usage and key administration separately. Validate service-agent permissions and recovery paths.
5. Restrict data paths with approved network controls without assuming private networking replaces identity controls.
6. Configure required data access logs and verify receipt through a canary action.
7. Test denied access with a representative unauthorized principal and approved access with the application identity.
8. Apply the retention schedule and verify deletion on a disposable synthetic dataset.

## Keys and separation of duties

| Design choice | When to consider it | Additional operating responsibility |
|---|---|---|
| Provider-managed encryption | Baseline workload where contractual/risk needs allow it | Validate service configuration and access controls |
| Customer-managed key | Separate custody, policy or audit requirement | Key policy, service permissions, rotation, backup/recovery and deletion controls |
| Managed HSM / hardware protection | Required assurance boundary or key isolation | Availability, quotas, operational ceremonies and cost |
| External key management | Explicit external custody requirement | External dependency, latency, availability and failure recovery |

AWS KMS/CloudHSM, Azure Key Vault/Managed HSM and Google Cloud KMS/Cloud HSM/Cloud EKM are not interchangeable product tiers. Choose by custody, supported integration, throughput, availability, operational competence and contractual requirements. Link to the existing key-management portfolio guides for specialized deployment depth after confirming current provider support.

Perform a key-disable exercise only in a sandbox. Observe affected reads/writes, alerts and recovery. A backup encrypted under an unavailable key can be unrecoverable even if the backup job succeeded. Record who can schedule deletion and how that action is reviewed.

## Retention, legal holds and deletion

Translate records policy into lifecycle rules by data class and purpose. Document where retention starts, whether versions and replicas are included, who can place/release a legal hold, and what happens when privacy deletion requests conflict with legal obligations. Obtain the appropriate legal decision rather than hard-coding a blanket deletion period.

Test deletion across primary storage, derived copies, caches, search indexes and analytics exports. Backup deletion may follow a controlled expiry policy rather than immediate per-record deletion. Record the actual behavior and customer commitments. Cryptographic erasure requires a defensible key/data relationship and treatment of other copies, not simply deleting an arbitrary key.

## Masking, tokenization and nonproduction

Use synthetic data by default in the portfolio lab. For enterprise test environments, define approved de-identification or tokenization, control the re-identification service, and test whether combined attributes can still identify a person. A masked display field does not prove that exports, logs or APIs are masked.

Scan developer exports, support bundles and telemetry for inappropriate sensitive content. Limit diagnostic logging, redact before egress where possible, and test with synthetic identifiers. Evidence itself may contain sensitive data and needs its own classification.

## Good, better, best

Good: approved inventory, baseline encryption, access restrictions and retention procedure. Better: enforced policy, governed keys, tested masking and continuous discovery. Best: lineage-aware data controls, verified deletion workflows and recoverable key architecture with measured exposure and exception handling. Complexity should follow a documented requirement, not the desire to use the most expensive key service.

## Proof packet

Include the dataset contract, classification approval, effective policy, key-role separation test, successful and denied access, transport test, data-event log, retention configuration and deletion/restore exercise. Link every artifact to the scoped dataset and test date. See [recovery](15-recovery.md) for the availability side of data protection.
