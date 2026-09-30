# Backup, disaster recovery and recoverability evidence

**Objective:** demonstrate that the service can recover usable data and resume required operations within approved limits. A successful backup job does not prove recovery.

## Prerequisites from the business impact analysis

Identify critical business functions, maximum tolerable disruption, dependencies, minimum operating capacity and customer commitments. Obtain approved recovery time objectives (RTO) and recovery point objectives (RPO) for each service and dataset. Record the authority and date of approval.

The demo uses a four-hour RPO, four-hour measured restore target and a restore exercise within 90 days for tier-one workloads. Those are fictional project policies, not universal SOC 2, PCI, ISO, HIPAA or HITRUST requirements.

## Design for actual failure scenarios

Include accidental deletion, malicious encryption, compromised administration, region loss, corrupted application data, unavailable keys and failed dependencies. Replication can rapidly copy corruption or deletion and is not automatically an independent backup. A recovery design must address integrity and administrative separation as well as availability.

| Pattern | Good | Better | Best when justified |
|---|---|---|---|
| Data recovery | Versioned backups with documented restore | Automated backups, separated custody and scheduled restores | Isolated or immutable recovery copies with adversarial recovery tests |
| Service recovery | Manual runbook and known dependencies | Infrastructure rebuild automation and tested failover | Rehearsed regional recovery with capacity and dependency validation |
| Key recovery | Documented key access and recovery owner | Tested access during recovery and deletion safeguards | Independent custody/recovery design aligned to threat model |
| Evidence | Backup job logs | Measured restore and integrity results | Sustained exercises with recurrence tracking and executive review |

## Provider implementation paths

AWS can combine AWS Backup and service-native backup/versioning with cross-account or cross-region designs where supported. Azure can use Azure Backup, service-native backups and Azure Site Recovery where appropriate. Google Cloud can use Backup and DR plus service-native backups, snapshots and replication. Select service support, recovery granularity, region and threat model before choosing a product.

For each protected resource, record policy, schedule, recovery points, retention, encryption/key dependency, destination, administrator and restore procedure. Verify coverage against the resource inventory. An unprotected new database is a scope gap even when every scheduled backup job succeeded.

## Step-by-step restore exercise

1. Select a representative service and an approved recovery point. Record the target RPO and RTO.
2. Prepare an isolated recovery environment with approved networking and identities.
3. Start the clock at the defined recovery initiation point, not after infrastructure preparation has already consumed time.
4. Recover infrastructure, keys, secrets and data in dependency order.
5. Validate record counts, checksums or application-level invariants appropriate to the dataset.
6. Run functional and security checks, including restricted access and logging.
7. Determine the actual age of the latest usable recovery point and elapsed recovery time.
8. Document manual steps, missing dependencies, capacity limits and failed assumptions.
9. Have the business/service owner accept the exercise result and assign corrective work.
10. Remove the temporary environment under the approved cleanup process and preserve the exercise evidence.

## RPO and RTO measurement

RPO concerns recoverable data loss, not merely the scheduled backup interval. Use the timestamp of the latest usable recovery point relative to the failure scenario. RTO includes the agreed recovery boundary: technical restoration alone may not include customer verification, DNS convergence or downstream reconciliation. State exactly what was timed.

The demo's `recoverable_point_age_hours`, `restore_elapsed_hours` and `restore_integrity_verified` facts are supplied observations. They illustrate the predicates but do not perform recovery. Live proof requires an actual exercise log and validation output.

## Failure scenario

Restore completes in seven hours against a four-hour target. Determine whether the bottleneck was data volume, serial dependencies, missing permissions, unavailable key access, undocumented DNS steps or insufficient capacity. Correct the design and rerun a comparable exercise. Do not close the finding merely because the next small test dataset restores quickly.

Artifacts: [restore record](../templates/restore-exercise.md), [readiness gate](19-readiness.md), [findings lifecycle](18-findings.md).
