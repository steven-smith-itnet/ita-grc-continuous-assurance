# 01 Control automation use-case library

**Role priority:** most of the work is building control automation use cases.

**Objective:** build automated control tests that derive their result from the systems that produce the evidence, rather than from a supplied yes or no. Each use case states its objective, population, sources, logic, parameters, framework mapping, remediation path, retest method and limits in one versioned specification.

## What this project builds

- [usecases.json](usecases.json): eight use-case specifications. The code reads its parameters from this file, so a reviewer can see the exact SLA or threshold that produced a result.
- [usecases.py](../../src/assurance/usecases.py): one function per use case. Each joins two or more sources and returns PASS, FAIL, UNKNOWN or NOT_APPLICABLE with reasons and source references.
- [fixtures/](fixtures/hr_workers.json): synthetic exports shaped like an HR system, an identity provider, the AWS IAM credential report, GitHub and Azure Repos reviews, a CD deployment log, cloud logging configuration, KMS and Key Vault key metadata, backup exports, scanner findings and access-review campaigns.
- [tests/test_projects.py](../../tests/test_projects.py): regression tests for each scenario below.

## The eight use cases

| ID | Use case | Sources joined | Replaces base-lab fact | SOC 2 | ISO 27001:2022 | HIPAA |
|---|---|---|---|---|---|---|
| UC-01 | Leaver access removal | HR terminations, IdP accounts, AWS access keys, GCP service account keys | `access_removals_complete` | CC6.2 | A.5.18, A.5.16 | 164.308(a)(3)(ii)(C) |
| UC-02 | Privileged MFA enforcement | IdP groups, MFA policy assignment, registered methods, exclusion register | `privileged_mfa_verified` | CC6.1 | A.8.5, A.8.2 | 164.312(d) |
| UC-03 | Production change approval | CD deployment log, pull requests, reviews, emergency changes | `change_approved`, `change_separation_verified` | CC8.1 | A.8.32 | contextual |
| UC-04 | Audit log coverage and delivery | CloudTrail, Azure diagnostic settings, GCP sinks and auditConfigs, SIEM canary | `data_access_logging`, `log_canary_received` | CC7.2 | A.8.15, A.8.16 | 164.312(b) |
| UC-05 | ePHI encryption with customer-managed keys | Datastore inventory, classification tags, KMS, Key Vault and Cloud KMS metadata | `customer_managed_key` | CC6.1 | A.8.24 | 164.312(a)(2)(iv) |
| UC-06 | Backup coverage and restore evidence | Backup service exports, restore register | `recoverable_point_age_hours`, restore facts | A1.2, A1.3 | A.8.13 | 164.308(a)(7)(ii)(A), (D) |
| UC-07 | Vulnerability remediation within SLA | Compute inventory, Inspector, Defender for Cloud and SCC findings | `overdue_critical_vulnerabilities` | CC7.1 | A.8.8 | contextual |
| UC-08 | Privileged access review completeness | Review campaigns, membership snapshots, current group membership | `access_review_at` | CC6.2, CC6.3 | A.5.18, A.8.2 | 164.308(a)(4)(ii)(C) |

Mappings are candidates that a control steward and the assessor must review. The HIPAA column shows the closest Security Rule specification. "Contextual" means the use case informs the requirement without testing it.

## Rules every use case follows

1. **Derive, do not accept.** A result comes from joining records, not from a field that already says pass.
2. **Missing is not passing.** An absent field, a string where a boolean belongs, a timestamp without a UTC offset, or an uncorrelated identity produces UNKNOWN.
3. **A proven failure stands.** A FAIL is reported even when another input is missing.
4. **Keep the denominator visible.** Entities outside the population are listed as NOT_APPLICABLE with a reason.
5. **Parameters live in the specification.** SLAs, thresholds and group lists are reviewed configuration, not constants buried in code.
6. **Every result names its sources.** A reviewer can trace each row to the exports that produced it.

## Expected results

Run `PYTHONPATH=src python3 -m assurance projects --as-of 2026-09-30T12:00:00Z` and open `artifacts/projects/01-control-automation/report.md`.

| Use case | PASS | FAIL | UNKNOWN | NOT_APPLICABLE |
|---|---:|---:|---:|---:|
| UC-01 Leaver access removal | 2 | 3 | 1 | 1 |
| UC-02 Privileged MFA enforcement | 5 | 3 | 1 | 1 |
| UC-03 Production change approval | 4 | 3 | 1 | 1 |
| UC-04 Audit log coverage and delivery | 3 | 3 | 1 | 0 |
| UC-05 ePHI encryption with customer-managed keys | 2 | 2 | 1 | 3 |
| UC-06 Backup coverage and restore evidence | 1 | 3 | 1 | 3 |
| UC-07 Vulnerability remediation within SLA | 3 | 2 | 1 | 0 |
| UC-08 Privileged access review completeness | 1 | 2 | 1 | 0 |
| **Total** | **21** | **21** | **8** | **9** |

## What the results show

- **IdP removal is not enough.** Worker W-1005's identity-provider account was disabled 9 hours after termination. An AWS IAM access key tagged to that worker stayed active and was last used two days later. UC-01 fails the worker. A check of the identity provider alone would pass.
- **A late removal is a failure, not a pass.** W-1003 was disabled 40 hours after termination against a 24-hour SLA.
- **A pass can rest on bad data.** W-1004 passes here at 22 hours. [Project 04](../04-evidence-data-flow/README.md) shows the HR integration dropped a +05:30 offset, and the real lag was 27.5 hours.
- **Self-approval depends on the platform.** Deployment D-02 came from Azure Repos, where a branch policy can allow requestors to approve their own changes. The only approval is the author's.
- **Approval must cover the deployed commit.** D-03's approval was on commit `c2c2c2c`. The merged and deployed head was `c3c3c3c`, so the deployed code was never reviewed. GitHub records the reviewed commit in each review's `commit_id`.
- **Emergency changes need a separate path.** D-05 has no pull request but passes, because emergency change EC-0917 was approved by someone other than the deployer within 72 hours.
- **A canary is necessary but not sufficient.** GCP project `gcp-proj-ehr` delivered its canary in 3 minutes, but it hosts ePHI and Data Access audit logs are not enabled for Cloud Storage. Google Cloud writes Admin Activity audit logs automatically. Data Access audit logs are off by default except for BigQuery.
- **Break-glass accounts need an approved exception.** `bg-azure-01` has a valid, independently approved exclusion and is NOT_APPLICABLE. `bg-aws-01` has none and fails.
- **An unscanned asset is not a clean asset.** `gcp-vm-extract-01` was last scanned 12 days ago. It is UNKNOWN, not PASS.
- **A completed review can still be incomplete.** AR-GCP-Q3 left out `u-1015`, and `u-1010` reviewed their own access. AR-AZ-Q3 decided to revoke `u-1014`, but the membership is still present.

## Cloud-specific sources

| Use case | AWS | Azure | Google Cloud |
|---|---|---|---|
| UC-01 | `aws iam get-credential-report` access key fields | Microsoft Graph users and app credentials | `gcloud iam service-accounts keys list --managed-by=user` |
| UC-02 | IAM Identity Center account assignments | Conditional Access policies and `userRegistrationDetails` | Organization IAM policy bindings |
| UC-04 | `describe-trails` IsMultiRegionTrail, `get-trail-status` IsLogging | Subscription diagnostic settings with the Administrative category | Log sinks and IAM policy `auditConfigs` |
| UC-05 | `get-bucket-encryption`, `kms describe-key` KeyManager, `get-key-rotation-status` RotationPeriodInDays | Storage `encryption.keySource`, Key Vault rotation policy | Bucket `defaultKmsKeyName`, CryptoKey `rotationPeriod` |
| UC-06 | AWS Backup protected resources, recovery points and restore jobs | Azure Backup items and recovery points | Backup and DR or Cloud SQL backups |
| UC-07 | Amazon Inspector findings | Defender for Cloud assessments through Resource Graph | Security Command Center findings |

Change approval (UC-03) and access reviews (UC-08) are cloud-neutral. They read source control, CD, ITSM and identity governance systems.

## How a new use case moves to production

1. **Intake.** Start from a requirement and a risk, not a tool. Name the control owner and the population.
2. **Specify.** Add an entry to `usecases.json` with sources, logic, parameters, mapping, remediation, retest and limits.
3. **Build.** Add a function to `usecases.py` and register it. Keep provider differences in small adapters.
4. **Validate the logic.** Add a seeded-fault suite in [Project 03](../03-control-evaluation/README.md). The use case does not ship until it detects every fault, and an independent reviewer approves the vectors.
5. **Validate the data path.** Add or reuse a flow in [Project 04](../04-evidence-data-flow/README.md) so the input is reconciled to its source.
6. **Shadow mode.** Run it beside the existing manual control for at least one cycle. Investigate every disagreement before anyone relies on it.
7. **Operate.** Route FAIL and UNKNOWN to owners, and verify closure with [Project 05](../05-remediation-testing/README.md). Review parameters and mappings when frameworks or policies change.

## Exercises

1. In `fixtures/cloud_credentials.json`, set the status of `AKIA-SYNTH-0005` to `inactive`. Re-run. W-1005 becomes PASS, and the counts change to 22 PASS and 20 FAIL.
2. In `fixtures/idp_accounts.json`, change `u-1012`'s `policy_enforced` to the string `"true"`. Re-run. The result becomes UNKNOWN, not PASS.
3. Raise `sla_hours` for UC-01 in `usecases.json` to 48. W-1003 passes. A parameter change is a control change, so it needs the same review as code.

## Limits

These functions run on synthetic records. They do not authenticate to any system, and they do not prove that a real export contains what its documentation says. Owner correlation depends on worker IDs and tags that a separate control must keep accurate. Customer-managed keys, SLAs and rotation periods are fictional Acme policy values. HIPAA encryption at rest is an addressable specification, so the policy choice to require it belongs to the organization.
