# Discover resources, datasets and dependencies

**Objective:** construct a defensible population before testing controls. A control report can only speak about the assets it knows about. Inventory completeness is itself a control, not administrative preparation to be skipped.

## Four linked inventories

| Inventory | Minimum record | Why it matters |
|---|---|---|
| Service catalog | Service ID, business owner, technical owner, criticality, customer commitments, support hours | Establishes who approves scope and remediation |
| Resource inventory | Provider, tenant/account/project, region, native ID, resource type, state, first/last observed | Defines technical population and detects unmanaged assets |
| Data asset inventory | Dataset ID, purpose, subjects, data types, steward, location, copies, retention and lineage | Determines sensitivity and applicable controls |
| Identity and dependency inventory | Human/workload principal, authority, privileges, service dependencies, supplier and repository links | Exposes access and inherited-control dependencies |

Use native immutable resource identifiers where available. Names alone collide across accounts. Model resource deletion as a tombstone with a deletion timestamp so an audit-period population does not lose assets that existed earlier.

## Step 1: enumerate the cloud hierarchy

AWS: obtain Organizations account and organizational-unit inventory, enabled regions and account lifecycle state. Azure: establish Entra tenant, management groups, subscriptions and resource groups, including subscriptions outside the intended management-group inheritance. GCP: enumerate organization, folders, projects, project numbers, billing linkage and lifecycle state.

Reconcile cloud hierarchy with finance and identity records. A resource discovery identity that cannot see an account cannot establish that the account contains no assets. Record denied scopes in a collection ledger and include them in the report.

## Step 2: collect metadata through more than one lens

AWS Config records supported resource configuration when configured to record it. Supplement with Resource Explorer, service APIs, IaC state and billing exports where appropriate. Azure Resource Graph queries resource metadata across authorized scopes, while separate APIs are needed for some data-plane details. GCP Cloud Asset Inventory provides resource and policy inventory for supported asset types. None of these is a universal scan of every record stored inside each resource. [Azure Resource Graph](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview), [Cloud Asset Inventory](https://docs.cloud.google.com/asset-inventory/docs/asset-inventory-overview).

Start with `queries/` examples. A production collector must follow every continuation token, preserve the requested scope and record the count from each page. Store a run status per account/region/service rather than only a single global success flag. Retry transient throttling with bounded backoff. Permission denial is a collection defect, not an empty result.

## Step 3: find actual data locations

Interview application owners and trace ingestion to primary databases, object stores, queues, exports, search indexes, analytics, backups, observability systems, caches and support attachments. Include datasets copied by developers and vendors. Sample discovery scans to identify unsupported formats, encrypted files, oversized objects and excluded prefixes.

Reconcile observed stores with application configuration and connection strings without copying secrets into inventory. Maintain the relationship `service → dataset → resource → region → key → authorized principal → supplier`. A data-flow record includes source, destination, purpose, protocol, transformation, retention and cross-border movement.

## Step 4: assign ownership and measure uncertainty

Assign a business data owner who can approve purpose, sensitivity and retention, a steward who maintains the catalog, and a technical custodian who operates the service. Team identifiers are preferable to personal email addresses in provider tags. Escalate orphaned assets to the service owner rather than guessing from the last deployment principal.

Track four separate ratios: discovered/expected resources, owner-assigned/discovered resources, classified/discovered datasets, and successfully evaluated/applicable control pairs. Report numerator, denominator and collection window. Never multiply these into a single opaque score.

## Step 5: reconcile continually

Use creation/deletion events for speed and periodic full reconciliation for completeness. Events can be dropped, delayed, duplicated or reordered. Persist an idempotency key and reprocess safely. Compare each inventory snapshot with the last approved scope. A newly found production store opens classification and ownership tasks immediately.

## Acceptance exercise

1. Declare nine resources in scope and return eight from collection.
2. Ensure the ninth remains visible as missing evidence.
3. Add a tenth evidence record without a scope entry. The demo rejects the unscoped record so scope must be reviewed.
4. Remove a required classification field. Restricted-data control applicability must become unknown rather than not applicable.
5. For a real collector, remove permission to one region and demonstrate an explicit collection error.

The first four cases are represented in the local implementation and tests. Live inventory reconciliation is a production extension. Use [the asset register template](../templates/asset-register.csv) to plan it and [classification](03-classification.md) to turn discovered data into control requirements.
