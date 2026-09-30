# Terminology and translation guide

| Term | Meaning in this project | Common confusion |
|---|---|---|
| Assurance | Evidence-supported confidence about defined objectives | A dashboard score or an unsupported promise |
| Continuous monitoring | Repeated observation and evaluation with a stated cadence | Literal uninterrupted proof of every activity |
| Continuous auditing | An audit approach using frequent/automated procedures with appropriate oversight | Replacing independent judgment with scanner output |
| Control objective | Desired risk-reducing outcome | A specific product name |
| Control implementation | Mechanism and process used to achieve the objective | Merely documenting a policy |
| Design effectiveness | Whether the control could address the risk | Evidence it actually operated |
| Operating effectiveness | Whether it worked over the relevant period | One current configuration snapshot |
| Evidence freshness | Age of the observation/collection according to policy | Age of the underlying business event |
| Population | Complete set relevant to the test | Only the records successfully returned by a query |
| PBC | Evidence/request register provided by the client for an engagement | A guarantee the evidence is sufficient |
| Shared responsibility | Allocation of provider/customer obligations | Provider certification automatically covering customer configuration |
| RPO | Acceptable recovery-point/data-loss objective | Backup job frequency alone |
| RTO | Approved restoration-time objective | Only file-copy time |
| CMK/CMEK | Customer-managed encryption key terminology | Universal proof of stronger overall data security |
| WORM | Storage behavior limiting modification/deletion under defined retention | Authenticity of the data written |
| Root cause | Validated reason the issue arose or recurred | The first plausible explanation |
| Exception | Approved, scoped, time-limited risk decision | A technical pass |
| Policy as code | Versioned machine-evaluable rules | Complete legal or framework interpretation |
| Evidence as code | Structured, reproducible evidence generation and handling | Self-attested facts becoming inherently trustworthy |

## Cloud hierarchy

AWS organization → organizational unit → account → region/service resource. Azure Entra tenant and management groups → subscription → resource group → resource. GCP organization → folder → project → service resource. These hierarchies are not one-to-one equivalents, and authorization inheritance depends on the specific service and policy mechanism.

## Cloud control vocabulary

| Objective | AWS examples | Azure examples | GCP examples |
|---|---|---|---|
| Inventory | Config, Resource Explorer, service APIs | Resource Graph, service APIs | Cloud Asset Inventory, service APIs |
| Policy constraints | SCP/RCP, IAM and resource policies | Azure Policy, Azure RBAC | Organization Policy, IAM allow/deny/conditions |
| Posture findings | Security Hub, Config | Defender for Cloud, Policy Insights | Security Command Center |
| Data discovery | Macie for supported S3 content | Microsoft Purview supported scans | Sensitive Data Protection |
| Audit events | CloudTrail | Activity Log, resource/Entra logs | Cloud Audit Logs |
| Evidence objects | S3 | Blob Storage | Cloud Storage |
| Event processing | EventBridge, Lambda, Step Functions | Event Grid, Functions, Automation | Pub/Sub, Cloud Run jobs/workflows |
| Query | Athena | KQL/Log Analytics | BigQuery/Logging queries |

This table identifies candidate technologies, not a claim of identical semantics or full feature parity. Follow each cloud chapter's validation steps.

## Assumptions to challenge during an interview

Can the team prove inventory completeness? Does classification actually change enforcement? Who can alter the control logic? What happens when a collector fails? How are deleted resources represented in a reporting period? Can a finding be traced to original evidence? Does acceptance leave technical failure visible? When was the last representative restore? Who makes the readiness decision? These questions connect engineering mechanisms to assurance outcomes.
