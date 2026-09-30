# Azure implementation track

**Target:** build a governed storage workload and an evidence path across resource configuration, Entra identity and application process records. Keep Azure management-plane state distinct from data-plane authorization and Microsoft Purview classification.

## Prerequisites

Confirm Entra tenant, management-group hierarchy, subscription owner, approved region, resource-group naming, budget, workforce access and deployment identity. Register required resource providers. Determine whether existing landing-zone policies apply and whether the lab can create custom policy definitions or assignments. Establish a Log Analytics workspace or other approved log destination with documented residency and retention.

Grant the collector scoped resource read access and the specific log or identity permissions required by each evidence contract. A subscription Reader assignment does not automatically provide Microsoft Graph access to privileged identity or access-review data. Keep tenant-wide directory permissions separate and reviewed.

## Good, better, best Azure patterns

| Capability | Good | Better | Best |
|---|---|---|---|
| Resource scope | Explicit subscription/resource list | Resource Graph exports and service-catalog reconciliation | Management-group governance with orphan-subscription detection |
| Data catalog | Reviewed dataset register | Purview scans of supported sources with steward approval | Governed lineage and tested policy/label propagation |
| Enforcement | Bicep defaults and scoped RBAC | Azure Policy initiatives, diagnostic settings and private endpoints | Tested landing-zone policies, exemption expiry and deployment gates |
| Identity | MFA and reviewed privileged groups | Entra PIM, access reviews and workload managed identities where licensed | Continuous lifecycle reconciliation and independent privileged-session review |
| Evidence | Private Blob container with versioning | Regional archive, access logs and retention decisions | Approved immutable-storage policy plus recovery and signing process |
| Monitoring | Resource exports and manual review | Policy Insights, Defender for Cloud and KQL | Joined configuration/process evidence with coverage and freshness SLOs |

Licensing and feature availability are explicit design inputs. Product availability alone does not establish that the tenant is entitled to use the selected feature.

## Build sequence

1. **Reconcile subscription scope.** Query Resource Graph across authorized subscriptions, retain subscription identifiers and paging state, then compare with the approved service inventory. Resource Graph describes supported resource metadata, not every row in a database. [Resource Graph overview](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview).
2. **Build the storage baseline.** Review the Bicep example, generate a deployment what-if result and examine the intended changes. The template disables anonymous blob access, requires HTTPS, disables shared-key authorization and defaults public network access to disabled.
3. **Plan connectivity before use.** With public networking disabled, a valid private endpoint and private DNS path are required for ordinary data access. The small template does not provision that network. Validate resolution from the actual client network before troubleshooting authorization.
4. **Assign policy in audit mode.** Confirm effect, scope, exclusions, managed identity and remediation requirements. Validate on a canary resource before moving a supported policy to deny. Existing resources may require remediation rather than merely assigning a policy.
5. **Configure diagnostics.** Route resource and data-plane logs needed for the control. Generate a synthetic read/write event and verify arrival at the expected workspace/table. Log configuration alone does not prove delivery.
6. **Integrate identity evidence.** Export privileged assignments, approval records, access reviews and revocation outcomes. Join them to the service and resource population using stable object IDs.
7. **Normalize and evaluate.** The adapter treats `allowBlobPublicAccess: false` as evidence for a narrow anonymous-access prevention baseline. It does not establish that SAS tokens, shared keys, RBAC or network paths are safe.
8. **Open and close a finding.** Introduce a synthetic failing fact, assign ownership, implement an approved correction and independently retest.

## Compliance states need interpretation

Azure Policy distinguishes states including compliant, non-compliant, exempt, unknown, conflicting and error. Its rolled-up percentage can include states that this project's strict pass rate excludes. Preserve the native state and map it explicitly. Never import a portal percentage into a management report without documenting its denominator and treatment of exemptions. [Azure Policy compliance states](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/compliance-states).

## Classification is a separate control path

Resource tags support organization and policy selection. Purview classifications describe discovered data, and sensitivity-label support depends on the source and feature. A label visible in Data Map is not sufficient proof of encryption, DLP or access enforcement for every underlying data store. Maintain an enforcement matrix for each supported workload, and test access using approved identities.

## Immutable evidence and recovery

Azure immutable Blob storage supports time-based retention and legal holds. Choose container-level or version-level policy based on requirements and supported account features. Validate lifecycle, restore and legal-hold interactions before locking a policy. The lab baseline is intentionally a workload template, not a claim of a configured immutable evidence vault. [Immutable Blob storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview).

## Acceptance and cleanup

Use a authorized identity to test legitimate access and another identity to test denial. Verify private DNS, log canary receipt and collector scope. Attempt collection without the required Graph permission and preserve the error. Confirm that policy exemptions have an owner and expiration. A private endpoint alone does not establish that public access is disabled.

Delete only the lab resource group after reviewing retained data, locks, soft-delete policies and recovery obligations. Record resources that remain due to retention. Artifacts: [Bicep baseline](../infra/azure/storage.bicep), [policy example](../infra/azure/policy.json), [KQL and CLI queries](../queries/azure.sh). Last verified: 2026-09-30 against linked Microsoft documentation.

## Command-level sandbox walkthrough

Use an approved Azure CLI session and a dedicated lab subscription/resource group. First compile locally, then inspect a what-if plan. Resource-group creation and deployment are state-changing operations for the authorized lab operator, not steps executed by this portfolio build.

```bash
az account show --output table
az bicep build --file infra/azure/storage.bicep
export ASSURANCE_SUBSCRIPTION='REPLACE_WITH_SUBSCRIPTION_ID'
export ASSURANCE_RESOURCE_GROUP='rg-atlas-assurance-lab'
export ASSURANCE_STORAGE='REPLACE_WITH_GLOBALLY_UNIQUE_LOWERCASE_NAME'
az group create --subscription "$ASSURANCE_SUBSCRIPTION" \
  --name "$ASSURANCE_RESOURCE_GROUP" --location eastus2
az deployment group what-if --subscription "$ASSURANCE_SUBSCRIPTION" \
  --resource-group "$ASSURANCE_RESOURCE_GROUP" \
  --template-file infra/azure/storage.bicep \
  --parameters storageName="$ASSURANCE_STORAGE"
```

Review disabled public networking and the absence of private endpoint/DNS resources. Deploy only after those constraints and the budget are understood:

```bash
az deployment group create --subscription "$ASSURANCE_SUBSCRIPTION" \
  --resource-group "$ASSURANCE_RESOURCE_GROUP" \
  --name atlas-storage-baseline \
  --template-file infra/azure/storage.bicep \
  --parameters storageName="$ASSURANCE_STORAGE"
bash queries/azure.sh
```

A collection identity can use an appropriately scoped Reader role for management-plane storage properties. Data-plane tests need a suitable data role and reachable endpoint. Entra/Graph evidence requires separate tenant permissions. Demonstrate those boundaries by confirming a permitted metadata read and a denied unauthorized data read.

For Resource Graph, install or enable the approved CLI extension if needed and run the query against explicit subscriptions. The query below is a limited pilot page, not a complete inventory collector:

```bash
az graph query --subscriptions "$ASSURANCE_SUBSCRIPTION" \
  --graph-query "Resources | where type =~ 'microsoft.storage/storageaccounts' | project id, name, location, tags" \
  --first 1000 --output json
```

Inspect the returned count and continuation token. A production collector must follow additional pages. For policy deployment, split the supplied policy object's `properties.policyRule` into the CLI's expected rule input or deploy the complete definition through the resource API/IaC. Validate the alias and assignment scope before promoting audit to enforcement.

After verifying only lab resources exist in the group, review `az group delete --name "$ASSURANCE_RESOURCE_GROUP" --subscription "$ASSURANCE_SUBSCRIPTION"`. Retention, locks and soft-delete behavior may leave recoverable data or prevent deletion. Preserve the agreed evidence and record the final resource state.
