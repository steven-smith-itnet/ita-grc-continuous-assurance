# AWS implementation track

**Target:** support one fictional product service in a dedicated AWS sandbox, then extend collection to an organization. Implement the controls as infrastructure and operating procedures, collect evidence independently, and verify both successful and denied behavior.

## Prerequisites and authority

Obtain an account owner, billing contact, approved regions, budget alert, root-account protection, workforce federation, service inventory and data classification. Document whether the account belongs to AWS Organizations and whether Control Tower governs it. Organization-level setup requires authority beyond a workload account. Establish a security tooling account and log archive design before broad rollout.

Use a dedicated read-only collection role. Inventory collection may require Organizations, Config and individual service metadata permissions. Reading configuration does not require downloading all object contents. A separate discovery role may need tightly scoped S3 read and KMS decrypt access. Prove that collection cannot put a bucket policy, alter a key or delete evidence.

## Good, better, best AWS patterns

| Capability | Good: bounded pilot | Better: repeatable service | Best: organization operation |
|---|---|---|---|
| Inventory | Reviewed resource exports plus account/region manifest | Config recorder and scheduled reconciliation | Organization inventory reconciliation, lifecycle events and owner enforcement |
| Data discovery | Owner-approved dataset register and targeted scan | Macie discovery for supported S3 objects plus other datastore scanners | Governed discovery coverage, lineage and classification approval across services |
| Preventive controls | Hardened IaC defaults and peer review | IAM policies, bucket controls and Config detection | SCP/RCP where appropriate, approved landing-zone patterns and drift response |
| Testing | Python over dated snapshots | Config rules and conformance packs plus custom process tests | Versioned central catalog with independently reviewed test releases |
| Evidence | Private S3 with encryption and versioning | Separate archive account, scoped access and retention | Approved Object Lock design, signing, regional custody and recovery exercise |
| Reporting | Reviewed CSV and finding register | Athena queries and scheduled management reports | Cross-service trends with freshness/coverage SLOs and regional aggregation |

These are maturity patterns, not AWS product tiers. A small service may meet its objectives with the middle column.

## Build sequence

1. **Declare scope.** List account IDs, regions, services, resource types, service IDs and expected owners. Exclude no region simply because it is rarely used.
2. **Establish logs.** Configure CloudTrail management events and explicitly decide which data events are required. Route logs to a protected destination and test ingestion with a known API action. Review cost before enabling broad data-event collection.
3. **Enable configuration recording.** Select supported resource types, IAM role, delivery destination and recorder scope. Confirm that a deliberately changed resource appears in configuration history. A recorder that exists but is stopped does not provide current evidence.
4. **Deploy a narrow baseline.** The included CloudFormation template creates a private, encrypted, versioned S3 bucket with metadata and a transport-security policy. Review the change set in a sandbox before creating it. It is not a complete landing zone or evidence archive.
5. **Assign detective tests.** The Config conformance-pack example checks storage exposure and encryption. Conformance packs group Config rules and remediation definitions for deployment. Confirm recorder prerequisites and rule applicability in the target region. [AWS Config conformance packs](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html).
6. **Collect independently.** Use the read-only commands in `queries/aws.sh`, preserve raw JSON privately, and run the narrow adapter test. Add account-level settings, policies, access points and effective-access tests before claiming broad exposure analysis.
7. **Exercise the failure path.** Supply a synthetic disabled prevention flag to the evaluator. Open a finding, repair the sandbox configuration through IaC, recollect and independently retest.
8. **Measure operation.** Run daily plus on relevant change events. Alert when a scheduled run is missing, not only when a control fails.

## IAM and shared responsibility

IAM Identity Center supports workforce access, while workload roles and temporary credentials support service identities. IAM policy evaluation and organization policies need separate attention from identity lifecycle. An SCP constrains permissions in its scope and does not grant permissions. Keep permission boundaries, resource policies and key policies in the effective-access review.

Collect privileged assignments, role trust policies, approval records and revocation evidence. Verify break-glass access separately. A federated session's MFA evidence may live in the identity provider, so the absence or presence of a local IAM-user MFA device is not a universal workforce-MFA test.

## Evidence custody and service availability

S3 Object Lock provides retention and legal-hold mechanisms for object versions. Choose retention only after records-management and legal review, and test the operating model in a disposable design before applying irreversible restrictions. The included pilot template enables versioning but does not claim WORM protection. [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html).

AWS Audit Manager is in maintenance mode and is not open to new customers after April 30, 2026. Existing deployments have account/region expansion limitations. This project therefore uses Config, logs and a separate evidence pipeline as its new-account baseline. [AWS availability notice](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html).

## Acceptance and teardown

Verify tags, private-access baseline, encryption configuration, CloudTrail event receipt and Config resource coverage. Capture one denied anonymous-access attempt and one authorized read using synthetic content. Remove a collector permission and confirm an explicit unknown state. Review findings with the service owner.

Before cleanup, export approved synthetic results. Delete only the resources created for the sandbox. Empty versioned buckets by reviewing object versions and delete markers. Retention locks, snapshots and log destinations can intentionally survive a workload teardown and continue to incur charges. Document retained resources instead of bypassing protection casually.

Artifacts: [CloudFormation](../infra/aws/storage.yaml), [Config pack](../infra/aws/conformance-pack.yaml), [AWS queries](../queries/aws.sh). Templates are authored examples, not live deployment evidence. Last verified: 2026-09-30 against linked AWS documentation.

## Command-level sandbox walkthrough

Install AWS CLI v2 and authenticate through the approved workforce/session mechanism. Run from the project root. These commands are a walkthrough for an authorized sandbox and were not executed against a cloud account while building this project.

```bash
aws sts get-caller-identity
aws configure get region
aws cloudformation validate-template --template-body file://infra/aws/storage.yaml
aws cloudformation deploy \
  --template-file infra/aws/storage.yaml \
  --stack-name atlas-assurance-storage-lab \
  --parameter-overrides Owner=records-platform \
  --no-execute-changeset
aws cloudformation describe-change-set \
  --stack-name atlas-assurance-storage-lab \
  --change-set-name REVIEW_THE_NAME_RETURNED_BY_DEPLOY
```

Review the change set, account, region, names, encryption choice and retained-resource behavior. For an approved execution, use `aws cloudformation execute-change-set` with that exact stack and change-set name, then wait for stack creation and inspect its outputs. The generated bucket name is the resource to collect. Do not substitute an existing production bucket.

```bash
aws cloudformation describe-stacks \
  --stack-name atlas-assurance-storage-lab \
  --query 'Stacks[0].Outputs' --output json
export ASSURANCE_BUCKET='REPLACE_WITH_LAB_BUCKET'
export ASSURANCE_ACCOUNT='REPLACE_WITH_EXPECTED_ACCOUNT'
bash queries/aws.sh
```

The required read permissions for these bucket checks are `s3:GetBucketPublicAccessBlock`, `s3:GetEncryptionConfiguration` and `s3:GetBucketVersioning` scoped to the lab bucket. Additional effective-access checks need separate permissions and evidence. The deployment principal and collection principal should be different roles in a production design.

Inspect the four prevention booleans, encryption rules and versioning status. Compare the output to the adapter contract. Capture collection timestamps and source command references when normalizing observations. Do not simply copy a provider export into the richer process-evidence fixture and label every missing process fact true.

To add the Config pack, first confirm the recorder and delivery channel are configured and active, then use:

```bash
aws configservice describe-configuration-recorder-status
aws configservice describe-delivery-channels
aws configservice put-conformance-pack \
  --conformance-pack-name atlas-storage-baseline \
  --template-body file://infra/aws/conformance-pack.yaml
aws configservice describe-conformance-pack-status \
  --conformance-pack-names atlas-storage-baseline
```

Wait for evaluation and inspect resource-level findings. A deployed pack is not proof every expected bucket was evaluated. Reconcile with scope and preserve insufficient-data or missing-resource states. For teardown, remove the lab pack when no longer required, review the stack deletion, and handle the intentionally retained versioned bucket under the lab cleanup plan.
