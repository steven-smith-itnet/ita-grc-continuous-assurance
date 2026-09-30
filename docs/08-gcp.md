# Google Cloud implementation track

**Target:** use organization/project inventory, Cloud Storage policy, identity evidence and audit logs to evaluate a fictional service. Treat organization policies, IAM conditions, labels and data classification as separate mechanisms with explicit relationships.

## Prerequisites

Confirm organization/folder/project hierarchy, billing, service ownership, region requirements and enabled APIs. A standalone project lacks some organization-level governance capabilities. Establish a deployment principal and a separate collection principal. Prefer Workload Identity Federation for CI where appropriate, and avoid distributing service-account keys.

Document permissions for Cloud Asset Inventory, storage metadata, logging and any Security Command Center features. Reading a bucket's metadata does not require permission to download every object. Discovery tools with content access require separate approval and scope.

## Good, better, best GCP patterns

| Capability | Good | Better | Best |
|---|---|---|---|
| Scope | Reviewed project and resource list | Cloud Asset Inventory export and reconciliation | Organization/folder coverage with lifecycle events and regional stewardship |
| Classification | Dataset register and owner review | Sensitive Data Protection discovery for supported sources | Governed lineage and tested column/data-access controls |
| Storage baseline | Uniform bucket-level access and explicit public access prevention | Versioned IaC, policy constraints and CMEK where justified | Governed deployment patterns with effective-access tests and drift response |
| Control monitoring | Scheduled JSON exports and Python tests | SCC findings and native monitoring joined to process tests | Reviewed Compliance Manager adoption, evidence integration and collector SLOs |
| Evidence | Private regional Cloud Storage | Dedicated project, lifecycle controls and access logging | Approved retention lock, signing and regional recovery process |
| Analytics | Reviewed CSV | BigQuery result history and scheduled queries | Regional aggregation with confidence, coverage and exception analytics |

These levels are project maturity choices. They are not equivalent to Security Command Center service tiers.

## Build sequence

1. **Inventory the hierarchy.** Export approved project and folder scope. Use Cloud Asset Inventory for supported assets and policies. Compare results with billing, deployment records and the service catalog. Follow pagination and preserve asset timestamps. [Cloud Asset Inventory](https://docs.cloud.google.com/asset-inventory/docs/asset-inventory-overview).
2. **Deploy the pilot bucket.** The Terraform example sets uniform bucket-level access, explicit public access prevention, versioning and metadata. It optionally accepts a customer-managed key. Review the plan and key permissions before applying in a sandbox.
3. **Validate IAM separately.** Inspect project/folder/org grants and bucket bindings. Public access prevention addresses anonymous public access, while broad authenticated principals, excessive roles or compromised workloads require separate controls.
4. **Establish audit evidence.** Decide which Data Access audit logs are needed, route them to an approved sink and verify a synthetic canary event. Do not assume all required data access logging is present from default configuration.
5. **Discover sensitive data.** Review supported sources, scan scope, sampling, exclusions, residency and cost. Have the data owner approve classification and control changes.
6. **Normalize provider output.** The example adapter expects a Cloud Storage JSON API bucket resource. `iamConfiguration.publicAccessPrevention == enforced` proves the local explicit setting. `inherited` stays unknown until organization-policy evidence is collected. `gcloud` display formats may use different field names, so do not feed display output into an API-shaped adapter without a contract test. [Bucket API schema](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets).
7. **Run the finding lifecycle.** Evaluate a synthetic failure, review scope and severity, fix the approved configuration and retain independent retest evidence.
8. **Reconcile event and scheduled views.** Asset feeds improve timeliness. Scheduled full reconciliation identifies dropped events and unauthorized projects.

## Compliance tooling and current constraints

Google Cloud's Compliance Manager provides framework/control workflows within Security Command Center. Before adoption, review activation scope, permissions, regional processing and encryption requirements. Its documentation states that it uses a global endpoint and does not support customer-managed encryption keys. Those constraints can determine whether it fits a restricted evidence program. [Compliance Manager overview](https://docs.cloud.google.com/security-command-center/docs/compliance-manager-overview), [enablement requirements](https://docs.cloud.google.com/security-command-center/docs/compliance-manager-enable).

The current documentation also marks the SCC Enterprise tier deprecated with a planned May 21, 2027 shutdown. Verify the selected tier at implementation and avoid designing a new long-lived dependency around a retiring tier. This project remains usable without purchasing SCC because the offline demo consumes synthetic fixtures.

## Labels, tags and column controls

Use labels for resource organization and reporting. Use Resource Manager tags only with documented supported policy behavior. For BigQuery column restrictions, select the appropriate policy-tag or data-policy mechanism and test with representative identities. The presence of `classification=restricted` as a label does not itself restrict column access.

## Evidence retention and teardown

Cloud Storage Bucket Lock can lock a retention policy. A locked policy has important irreversibility constraints, so decide retention, legal obligations and cleanup before locking anything. Versioning alone is not an immutable archive. [Bucket Lock](https://docs.cloud.google.com/storage/docs/bucket-lock).

The Terraform example sets `force_destroy = false`. Review object versions and legal/retention controls before deleting lab resources. Confirm no test keys, service accounts, log sinks or query datasets remain unintentionally. Artifacts: [Terraform baseline](../infra/gcp/main.tf), [GCP queries](../queries/gcp.sh). Last verified: 2026-09-30 against linked Google documentation.

## Command-level sandbox walkthrough

Install an approved Terraform version and Google Cloud CLI. Authenticate to the intended project using the organization's approved method. Application Default Credentials and CLI credentials are related but distinct contexts, so validate the identity actually used by Terraform.

```bash
gcloud auth list
gcloud config get-value project
export ASSURANCE_PROJECT='REPLACE_WITH_LAB_PROJECT'
export ASSURANCE_BUCKET='REPLACE_WITH_GLOBALLY_UNIQUE_LAB_BUCKET'
gcloud projects describe "$ASSURANCE_PROJECT" --format=json
terraform -chdir=infra/gcp init -backend=false
terraform -chdir=infra/gcp validate
terraform -chdir=infra/gcp plan \
  -var="project_id=$ASSURANCE_PROJECT" \
  -var="bucket_name=$ASSURANCE_BUCKET" \
  -out=lab.tfplan
```

Review the account, project, region, versioning, public access prevention and the actual provider version selected in the lock file. The optional KMS key requires a compatible location and appropriate encryption/decryption permissions for the Cloud Storage service agent. Do not provide a key reference until those prerequisites are verified.

For the approved sandbox deployment:

```bash
terraform -chdir=infra/gcp apply lab.tfplan
bash queries/gcp.sh
```

The query captures a display export. The adapter's source contract is the JSON API bucket schema, which is not guaranteed to have the same field names as the CLI's transformed output. Compare them explicitly before writing a normalizer. A read-only bucket metadata role needs the relevant `storage.buckets.get` permission. Effective IAM review and data access testing require their own scoped permissions.

For organization inventory, use an approved Cloud Asset Inventory principal and explicit scope. For example, `gcloud asset search-all-resources --scope="projects/$ASSURANCE_PROJECT" --format=json` returns supported resources accessible to that identity. Record source errors, filters and page handling instead of treating an empty export as proof of no resources.

Use a separate approved identity to test access to a synthetic object and an unauthorized identity to confirm denial. A successful policy query is not a data-plane test. Preserve the result and check the intended audit event destination.

For cleanup, create and review a destroy plan using the same variables and state. The bucket refuses force deletion, so review versions and retention before removal. Keep Terraform state private because it can contain sensitive metadata. Record the final project resources and remaining log/backup destinations.
