# Source register and verification boundaries

Last source review: **2026-09-30**. The supplied role description is the requirements source. The architecture, phases, thresholds, fictional service and example procedures are this project's design choices. Provider behavior and framework descriptions use the primary references below. Recheck availability, supported resource types, regional behavior, licensing and authoritative framework text before implementation.

## Framework and assessment references

- [AICPA SOC suite](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services): engagement and reporting context.
- [AICPA Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022): authoritative criteria resource.
- [PCI SSC document library](https://www.pcisecuritystandards.org/document_library/): current PCI DSS and validation documents.
- [ISO/IEC 27001](https://www.iso.org/standard/27001): management-system standard context. Licensed requirements are not reproduced.
- [HHS Security Rule summary](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html): effective-rule overview and safeguards.
- [HHS risk-analysis guidance](https://www.hhs.gov/hipaa/for-professionals/security/guidance/final-guidance-risk-analysis/index.html): risk-analysis starting point.
- [HITRUST assessments](https://hitrustalliance.net/assessments-and-certifications): assessment-path overview. Proprietary requirements are not reproduced.
- [NIST SP 800-53A](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final): assessment-methodology reference.

## AWS

- [Audit Manager availability](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html): new-customer and expansion limitations.
- [Config conformance packs](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html): grouped rule deployment.
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html): retention and legal-hold mechanisms.
- [S3 public-access-block CLI](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-public-access-block.html): API response and bucket/account scope.
- [Macie automated discovery](https://docs.aws.amazon.com/macie/latest/APIReference/automated-discovery-configuration.html): S3 scope and sampling.

## Microsoft

- [Resource Graph](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview): resource-query scope.
- [Azure Policy states](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/compliance-states): native states and percentage semantics.
- [Immutable Blob storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview): retention architecture.
- [Purview Data Map labels](https://learn.microsoft.com/en-us/purview/data-map-sensitivity-labels): labeling workflow and preview status.
- [Storage account CLI](https://learn.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest): collection commands.

## Google Cloud

- [Cloud Asset Inventory](https://docs.cloud.google.com/asset-inventory/docs/asset-inventory-overview): supported inventory model.
- [Compliance Manager overview](https://docs.cloud.google.com/security-command-center/docs/compliance-manager-overview): control workflows and processing constraints.
- [Compliance Manager enablement](https://docs.cloud.google.com/security-command-center/docs/compliance-manager-enable): activation, permissions and encryption constraints.
- [Resource Manager tags](https://docs.cloud.google.com/resource-manager/docs/tags/tags-overview): tags versus labels.
- [BigQuery policy tags](https://docs.cloud.google.com/bigquery/docs/best-practices-policy-tags): column-control concepts.
- [Cloud Storage bucket API](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets): provider adapter schema.
- [Bucket Lock](https://docs.cloud.google.com/storage/docs/bucket-lock): retention-lock behavior.

## Publishing

- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages): build/deploy workflow structure.
- [GitHub Pages publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site): repository setup.

## Verification ledger

| Claim class | Verification performed | Remaining work |
|---|---|---|
| Local evaluator | Unit/contract tests and reproducible synthetic run | Production source integrations and independent control validation |
| Static site | Build and local-link checks | Public deployment to selected host |
| Cloud templates | CloudFormation lint, Bicep compilation and Terraform validation | Cloud plans/change review, sandbox deployment and live tests |
| Framework mappings | Primary-source thematic review | Licensed requirement-level mapping and assessor review |
| Program outcomes | Proposed objectives and metrics | Actual operational measurements over an agreed period |

Do not infer cost savings, audit success, production coverage or Adobe adoption from the portfolio demonstration. The project's value is the inspectable implementation, explicit methodology and practical execution plan.

See [the local validation record](../VALIDATION.md) for tool versions and actual checks.
