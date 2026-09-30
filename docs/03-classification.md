# Classify data and bind metadata to controls

**Objective:** make data sensitivity, purpose, residency and lifecycle actionable. A tag is useful only when its value is trustworthy and something consumes it.

## Define the taxonomy before scanning

Adopt four fictional lab classes: public, internal, confidential and restricted. Define examples, prohibited uses, sharing rules, retention authority and required reviewers. These are project choices, not universal categories imposed by any framework. Treat classification as multidimensional: sensitivity alone does not encode legal purpose, geographic restrictions, recovery criticality or records retention.

| Attribute | Example | Authority | Control use |
|---|---|---|---|
| `classification` | restricted | Data owner | Private access, approved key custody, enhanced logging |
| `data_domain` | customer-records | Data steward | Discovery rules and purpose validation |
| `regulatory_scope` | hipaa-candidate | Legal/privacy with business owner | Applicability assessment, not automatic legal determination |
| `residency_policy` | approved-us-regions | Legal/contracts | Deployment and replication constraints |
| `retention_policy_id` | records-policy-07 | Records management | Lifecycle rules, archive and deletion |
| `legal_hold_id` | opaque reference or none | Legal | Suspend authorized deletion where required |
| `service_id` / `owner` | atlas-records / records-platform | Service catalog | Routing and escalation |
| `criticality` | tier1 | Business continuity owner | Recovery objectives and exercise frequency |
| `classification_status` | reviewed / provisional / unknown | Steward | Evidence confidence and workflow gating |

Do not place personal information, customer names, secrets or actual record contents in broadly readable cloud metadata. Store restricted details in the catalog and use opaque references in tags.

## Discover, validate, label, enforce

1. Register the data source and approve the discovery identity. Determine whether the scan reads content and where findings are processed.
2. Select detectors for the relevant data types. Use synthetic positive and negative samples to test precision, recall and unsupported-content handling.
3. Preserve scan scope, excluded paths, timestamps, sampling method and error counts. A scan that examined one object cannot classify a million-object bucket as harmless.
4. Send uncertain results to the data steward. The data owner approves the classification or documents why a detector result is incorrect.
5. Write a versioned catalog decision and synchronize supported metadata to provider resources. Record failed synchronization separately.
6. Evaluate the binding: does the chosen tag actually trigger a deny, policy assignment, column restriction, lifecycle decision or review task?
7. Run an access test as an unauthorized principal. A visible label alone is not proof that access is restricted.
8. On data movement, re-evaluate destination metadata and effective controls. Do not assume every format or export carries the label.

## Provider terminology matters

**AWS:** resource tags annotate resources and can participate in authorization where the service and IAM condition keys support it. Lake Formation tags apply to governed data access. Glue Data Catalog holds metadata. Amazon Macie analyzes supported S3 content and its automated discovery uses sampling. Preserve coverage limitations instead of reporting every S3 object as scanned. [Macie discovery configuration](https://docs.aws.amazon.com/macie/latest/APIReference/automated-discovery-configuration.html).

**Azure:** Azure resource tags are management metadata. Microsoft Purview classifications and sensitivity labels are separate concepts. Data Map scans can discover classifications and label supported assets, but feature support and protection behavior vary by workload. The cited Data Map sensitivity-label feature is documented as preview, so do not make it a required production control without reviewing release status and support. [Purview Data Map labels](https://learn.microsoft.com/en-us/purview/data-map-sensitivity-labels).

**GCP:** labels are queryable metadata. Resource Manager tags can support conditional policy enforcement. BigQuery policy tags support column-level controls and are distinct from ordinary resource labels. Newer data-governance-tag functionality has its own availability constraints. [Tags overview](https://docs.cloud.google.com/resource-manager/docs/tags/tags-overview), [BigQuery policy tags](https://docs.cloud.google.com/bigquery/docs/best-practices-policy-tags).

## Protect the classification decision

A workload administrator must not reduce controls simply by relabeling restricted data as public. Limit write permissions on authoritative classification fields, require approval for downgrades, record old/new values and trigger re-evaluation. Classification inherited from a parent is a starting point, not proof that every child dataset has identical sensitivity. Conflicting classifications should resolve through a documented precedence rule and owner review.

## Good, better, best

Good: a controlled register with owner-approved classification and explicit resource links. Better: scheduled discovery and metadata synchronization with exception queues. Best: tested enforcement tied to governed attributes, lineage-aware propagation and drift detection. The strongest option still needs human decisions about purpose, legal basis and acceptable exposure.

## Proof exercise

Create a synthetic restricted dataset. Remove its classification label and confirm a governance finding. Attempt a public-access change and confirm the preventive control rejects it in an authorized sandbox. Attempt an unauthorized downgrade and capture the denied event. Change the schema to add a sensitive column, rerun discovery and verify that downstream consumers receive the appropriate restrictions.

In the runnable fixture, `unresolved_discovery_gaps` means the number of **unresolved discovery gaps**, so zero satisfies the demo predicate. It is not a percentage. A production implementation should also record scanned objects, total supported objects, excluded objects and scan errors separately. See [data protection](10-data-protection.md) for enforcement and [the testing contract](17-testing.md) for evidence limitations.
