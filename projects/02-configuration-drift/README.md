# 02 Configuration baseline and drift

**Role priority:** GRC engineering of automated controls and configuration, across AWS, Azure and GCP.

**Objective:** define one storage configuration baseline, evaluate it against provider-native API responses from all three clouds, and classify every change between two snapshots as authorized or unauthorized.

## What this project builds

- [baseline.json](baseline.json): four canonical settings with the native field for each provider and the native enforcement mechanism that should back it.
- [drift.py](../../src/assurance/drift.py): three provider adapters that turn native API responses into canonical values, a baseline evaluator and a drift classifier.
- [fixtures/](fixtures/resources.json): six of the base lab's storage workloads, two snapshots taken 24 hours apart in provider-native shapes, and the change register.

## The baseline

| Setting | AWS native evidence | Azure native evidence | Google Cloud native evidence | Applies to |
|---|---|---|---|---|
| Public access prevented | All four `PublicAccessBlockConfiguration` flags true | `allowBlobPublicAccess` false | `publicAccessPrevention` enforced | All |
| Identity-only access | `ObjectOwnership` BucketOwnerEnforced, which disables ACLs | `allowSharedKeyAccess` false | Uniform bucket-level access enabled | All |
| Versioning enabled | `GetBucketVersioning` Status Enabled | `isVersioningEnabled` true | `versioning.enabled` true | All |
| Customer-managed key | `aws:kms` with a key whose `KeyManager` is CUSTOMER | `encryption.keySource` Microsoft.Keyvault | `defaultKmsKeyName` set | Restricted only |

## Normalization decisions

Each adapter returns a value only when the native response establishes it. These decisions are where cross-cloud configuration testing usually goes wrong.

| Native response | Canonical value | Reason |
|---|---|---|
| AWS `GetBucketVersioning` returns no Status | Off | AWS documents an empty response for a bucket whose versioning was never enabled. |
| AWS versioning call missing from the snapshot | Unknown | Absence of the call is a collection gap, not a setting. |
| AWS `aws:kms` with no key ID | Not customer-managed | The bucket falls back to the AWS managed key. |
| Azure `allowSharedKeyAccess` null | Shared key allowed | Microsoft documents null as equivalent to true. |
| GCP `publicAccessPrevention` inherited | Unknown | The effective value depends on an organization policy that the bucket resource does not include. |
| GCP field absent from the bucket resource | Unknown | A partial-response projection also omits fields, so absence cannot prove a default. |

## Expected results

| Result | Count |
|---|---:|
| Setting checks | 24 |
| PASS | 17 |
| FAIL | 3 |
| UNKNOWN | 1 |
| NOT_APPLICABLE | 3 |
| Drift events | 3 |
| Unauthorized drift | 1 |

Baseline deviations:

- `aws-records-01`: public access prevention is off. `BlockPublicPolicy` and `RestrictPublicBuckets` changed to false.
- `aws-records-02`: versioning is suspended.
- `azure-records-01`: `allowSharedKeyAccess` is null, which allows shared key authorization on a restricted account.
- `gcp-records-02`: versioning is UNKNOWN because the field is absent from the snapshot.

Drift between the 2026-09-29 and 2026-09-30 snapshots:

| Resource | Setting | Change | Direction | Change record | Result |
|---|---|---|---|---|---|
| aws-records-01 | Public access prevented | true to false | Away from baseline | None | FAIL: unauthorized |
| aws-records-02 | Versioning enabled | true to false | Away from baseline | CHG-2041 | PASS for change control, but the baseline check still fails and needs an exception |
| gcp-records-01 | Identity-only access | false to true | Toward baseline | CHG-2044 | PASS |

Two separate questions are answered here. The baseline check asks whether the resource is configured correctly now. The drift check asks whether each change went through change control. An approved change can still leave a resource off baseline, and that needs a documented exception rather than a silent pass.

## Enforcement layers

A detective check is the last line. The baseline names the native mechanism that should prevent or correct each setting first.

| Setting | AWS | Azure | Google Cloud |
|---|---|---|---|
| Public access prevented | Config rule `s3-bucket-level-public-access-prohibited`, account-level Block Public Access | Built-in policy "Storage account public access should be disallowed" | Constraint `storage.publicAccessPrevention` |
| Identity-only access | Config rule `s3-bucket-acl-prohibited` | Built-in policy "Storage accounts should prevent shared key access" | Constraint `storage.uniformBucketLevelAccess` |
| Versioning enabled | Config rule `s3-bucket-versioning-enabled` | Custom policy or template default | Terraform module default with a plan-time check |
| Customer-managed key | Config rule `s3-default-encryption-kms` | Built-in policy requiring customer-managed keys for storage | Constraint `gcp.restrictNonCmekServices` |

Rule and constraint names were checked against provider documentation on 2026-10-02. Confirm them again before deployment.

## Framework mapping

| Framework | Criteria | Coverage |
|---|---|---|
| SOC 2 | CC7.1 detection of configuration changes, CC8.1 change management, CC6.1 logical access | Partial |
| ISO 27001:2022 | A.8.9 configuration management. A.8.32 and A.5.23 contextually | Partial |
| HIPAA | 164.312(a)(1) access control. 164.312(c)(1) integrity contextually | Partial |

## Exercises

1. In `fixtures/changes.json`, add an approved change for `aws-records-01` and `public_access_prevented` inside the snapshot window. The drift event becomes PASS, while the baseline check still fails.
2. In `fixtures/snapshot_t1.json`, delete the `GetBucketVersioning` object for `aws-records-01`. The versioning check becomes UNKNOWN and a drift event appears as undetermined.
3. Set `allowSharedKeyAccess` to false for `azure-records-01` in both snapshots. The Azure failure clears with no drift event, because nothing changed between snapshots.

## Limits

The adapters read one resource type. Effective exposure also depends on bucket policies, access points, account-level and organization-level settings, network rules and SAS tokens, which are outside this baseline. Two snapshots show the state at two times, not every change between them. Event-driven collection, such as CloudTrail, Activity Log or Cloud Audit Logs, closes that gap. [Project 04](../04-evidence-data-flow/README.md) shows why those events also need reconciliation.
