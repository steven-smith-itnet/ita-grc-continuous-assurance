# 07 SOC 2-first framework coverage

**Role priority:** SOC 2 first. ISO 27001 preferred. HIPAA highly preferred. PCI DSS is owned by a separate team.

**Objective:** show which framework criteria the automated evidence in this repository supports, computed from mappings declared next to each use case and project. The output is also a backlog: criteria with high automation potential and no coverage are the next use cases to build.

## How coverage is computed

- Each use case in [Project 01's specification](../01-control-automation/usecases.json) declares its candidate mappings. Projects 02 to 06 declare theirs in [mappings.json](mappings.json).
- [frameworks.json](frameworks.json) lists the criteria in scope, a short topic label written for this project, and a planning judgment of automation potential.
- [coverage.py](../../src/assurance/coverage.py) joins the two. A mapping to a criterion that is not in the catalog stops the run, so a typo cannot inflate coverage. Any coverage value other than "partial" or "contextual" also stops the run.

| Coverage | Meaning |
|---|---|
| Partial | Automated evidence tests part of the criterion. Other parts still need people, documents or other systems |
| Contextual | The evidence informs the criterion without testing it |
| None | Nothing in this repository supports it |

There is no "full" level. No automated test satisfies a criterion on its own, and the assessor decides whether the overall evidence is sufficient.

## Results

| Framework | Priority | Criteria listed | Partial | Contextual only | None | High-potential gaps |
|---|---:|---:|---:|---:|---:|---|
| SOC 2 Trust Services Criteria | 1 | 38 | 11 | 2 | 25 | CC6.6, CC6.7, CC6.8 |
| ISO/IEC 27001:2022 | 2 | 24 | 14 | 4 | 6 | A.5.9, A.8.20 |
| HIPAA Security Rule | 3 | 20 | 9 | 3 | 8 | 164.308(a)(5)(ii)(C), 164.312(a)(2)(i), 164.312(e)(2)(ii) |
| PCI DSS v4.0.1 | 4 | 0 | 0 | 0 | 0 | Not mapped. Owned by a separate team |

The SOC 2 list covers the 33 common criteria plus Availability and Confidentiality, which the fictional engagement selects. The ISO list is a subset of clauses and Annex A controls relevant to technical evidence. A Statement of Applicability addresses all 93 Annex A controls. The HIPAA list covers Security Rule standards and implementation specifications relevant to cloud evidence, with R and A marking required and addressable specifications in the currently effective rule.

## SOC 2 detail

| Criterion | Topic | Potential | Coverage | Sources |
|---|---|---|---|---|
| CC1.1 to CC1.5 | Control environment | Low | None | Governance evidence, outside automation |
| CC2.1 | Relevant, quality information | Medium | Partial | P04 |
| CC2.2, CC2.3 | Internal and external communication | Low | None | |
| CC3.1 to CC3.4 | Risk assessment | Low to medium | None | |
| CC4.1 | Ongoing and separate evaluations | High | Partial | P03, P06 |
| CC4.2 | Deficiencies evaluated and communicated | Medium | Partial | P05 |
| CC5.1, CC5.3 | Control activities and policies | Low | None | |
| CC5.2 | General controls over technology | Medium | Contextual | P03 |
| CC6.1 | Logical access security | High | Partial | P02, UC-02, UC-05 |
| CC6.2 | User registration and removal | High | Partial | UC-01, UC-08 |
| CC6.3 | Role-based access, least privilege, segregation | High | Partial | UC-08, UC-01 contextually |
| CC6.4, CC6.5 | Physical access and disposal | Low to medium | None | |
| CC6.6 | Protection from threats outside the boundary | High | **None** | Backlog |
| CC6.7 | Restricted transmission and movement of information | High | **None** | Backlog |
| CC6.8 | Unauthorized or malicious software | High | **None** | Backlog |
| CC7.1 | Detection of configuration changes and vulnerabilities | High | Partial | P02, UC-07 |
| CC7.2 | Monitoring for anomalies | High | Partial | UC-04, P04 contextually |
| CC7.3 to CC7.5 | Event evaluation, incident response, recovery | Low to medium | None | |
| CC8.1 | Change management | High | Partial | P02, UC-03 |
| CC9.1, CC9.2 | Business disruption and vendor risk | Low | None | |
| A1.1 | Capacity | Medium | None | |
| A1.2 | Backup and recovery infrastructure | High | Partial | UC-06 |
| A1.3 | Recovery plan testing | Medium | Partial | UC-06 |
| C1.1 | Confidential information identified and protected | Medium | Contextual | UC-05 |
| C1.2 | Confidential information disposal | Medium | None | |

The full per-criterion tables for all three frameworks are in `artifacts/projects/07-framework-coverage/report.md` after a run.

## Backlog from the gaps

| Gap | Candidate use case | Sources |
|---|---|---|
| SOC 2 CC6.6, ISO A.8.20 | Network exposure baseline: no management ports open to the internet, private endpoints for restricted data | AWS security groups and VPC endpoints, Azure network security groups and private endpoints, GCP firewall rules and Private Service Connect |
| SOC 2 CC6.7, HIPAA 164.312(e)(2)(ii) | Encryption in transit: TLS minimums and HTTPS-only enforcement | S3 bucket policies with `aws:SecureTransport`, Azure `minimumTlsVersion` and HTTPS-only, GCP load balancer SSL policies |
| SOC 2 CC6.8 | Endpoint and workload protection coverage reconciled to inventory | EDR console export joined with the compute inventory |
| ISO A.5.9 | Inventory reconciliation across cloud, CMDB and billing | AWS Config, Resource Graph, Cloud Asset Inventory, CMDB export |
| HIPAA 164.312(a)(2)(i) | Unique user identification: no shared or generic accounts with ePHI access | IdP accounts joined with database and application user lists |
| HIPAA 164.308(a)(5)(ii)(C) | Log-in monitoring: failed sign-in alerting reaches the SOC | IdP sign-in logs and SIEM alert rules |

Each backlog item follows the lifecycle in [Project 01](../01-control-automation/README.md): specify, build, seed faults, reconcile the input, run in shadow mode, then operate.

## Limits

Topic labels are short descriptions written for this project, not the authoritative text. SOC 2 criteria and ISO 27001 are licensed, so obtain the current text before formal mapping. The HIPAA citations follow 45 CFR Part 164 Subpart C as currently effective. Check the status of proposed Security Rule changes before relying on the required and addressable designations. Coverage counts measure where automated evidence exists. They do not measure compliance.
