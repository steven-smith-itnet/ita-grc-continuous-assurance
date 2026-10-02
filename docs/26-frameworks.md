# Framework workstreams and mapping discipline

**Objective:** support the frameworks named in the role while preserving their different purposes, scopes and assessment methods. This chapter is an implementation planning guide. It does not reproduce licensed standards or provide a complete requirement-by-requirement certification workbook.

## Priority for this role

The supplementary role notes set the order: SOC 2 first, ISO standards next, HIPAA highly preferred, and PCI DSS owned by a separate team. [Project 07](../projects/07-framework-coverage/README.md) computes automated evidence coverage in that order and turns the gaps into a backlog. The PCI DSS section below stays for completeness.

## SOC 2

SOC 2 addresses controls relevant to the selected Trust Services Criteria categories. Security is central, and availability, processing integrity, confidentiality and privacy depend on the engagement scope. A Type I report addresses a point in time, while a Type II engagement includes operation over a specified period. Confirm engagement details with the CPA firm. [AICPA SOC resources](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services), [Trust Services Criteria](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022).

Implementation workstream: define system boundary and commitments, describe infrastructure/software/people/procedures/data, identify service organizations and customer responsibilities, map controls, preserve period evidence, test exceptions and prepare management responses. The lab supports technical evidence patterns. Management oversight, risk assessment, communication and other organization-level evidence remain necessary.

Candidate mappings include access controls to CC6 topics, monitoring to CC7 topics and change management to CC8 topics. These are thematic candidates requiring exact requirement and assessor review, not assertions that a single predicate satisfies a criterion.

## PCI DSS

Start by determining whether and how the service stores, processes, transmits or can affect payment-account data security. Draw the cardholder-data environment and connected/security-impacting dependencies. Do not assume outsourced payment processing removes every obligation. Use the current PCI SSC documents and the appropriate validation route. The document library identifies PCI DSS v4.0.1. [PCI SSC library](https://www.pcisecuritystandards.org/document_library/).

Implementation workstream: minimize payment data, validate segmentation, secure configurations, protect stored/transmitted data, manage vulnerabilities, control access, log activity, test security, maintain policies and assign responsibilities. The twelve requirement groups need their own applicability and testing workpapers. The sample cloud checks support only portions of that work.

Payment-page and e-commerce requirements depend on implementation and validation scope. Obtain the relevant assessor/acquirer guidance rather than using a generic cloud baseline as an SAQ determination. Validate segmentation and data flows with technical evidence, not only diagrams.

## ISO/IEC 27001

ISO/IEC 27001:2022 specifies an information security management system. Scope, risk assessment, risk treatment, leadership, objectives, operational management, performance evaluation and continual improvement are fundamental alongside selected controls. [ISO standard overview](https://www.iso.org/standard/27001).

Implementation workstream: establish organizational context and ISMS scope, identify interested parties, assess/treat risk, maintain a Statement of Applicability with justified inclusions/exclusions, implement controls, measure performance, conduct internal audit, hold management review and address nonconformities. Obtain the licensed standard and applicable amendments for formal work.

The project catalog is not a complete Statement of Applicability. Control evidence can support it, but selecting tools alone does not establish an operating management system.

## HIPAA

Assess whether the service and organization are covered entities, business associates or otherwise in a relevant relationship, and whether electronic protected health information is involved. The Security Rule includes administrative, physical and technical safeguards, and risk analysis informs the safeguards. Addressable specifications require a documented assessment and appropriate response rather than casual omission. HHS distinguishes the currently effective rule from proposed modifications. [HHS Security Rule summary](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html).

Implementation workstream: map ePHI flows and business associates, perform risk analysis, assign security responsibility, manage workforce access, train personnel, establish incident/contingency procedures, protect facilities/workstations/media and implement technical safeguards. Review business associate agreements and eligible cloud-service use with authorized specialists. Privacy and breach-notification obligations extend beyond cloud posture.

The lab uses synthetic records and makes no claim to process actual ePHI. Its recovery and logging examples illustrate technical evidence patterns, not HIPAA certification.

## HITRUST

The posting's “HITRSUT” is interpreted as HITRUST. HITRUST offers different assessment paths, including e1, i1 and r2, with different assurance scope and depth. Select the required path with the customer/assessor and use current licensed materials. [HITRUST assessment overview](https://hitrustalliance.net/assessments-and-certifications).

Implementation workstream: define scope and factors, determine the applicable assessment, assign requirement owners, gather evidence, assess implementation and maturity where relevant, remediate gaps and coordinate validated assessment activities. Do not copy proprietary requirement sets into a public portfolio or infer certification from another framework's control mapping.

## Cross-framework reuse

Reuse reliable evidence where the population, period and assertion align. Keep framework-specific applicability and residual requirements separate. The matrix should identify whether a local control provides full, partial, inherited or contextual support, with a reviewed rationale. Different frameworks can require distinct report forms, independent assessors, operating periods and management assertions.

## Assessment packet per framework

Create a scope statement, authoritative requirement/version list, applicability decisions, local control mapping, owners, evidence plan, test workpapers, findings and management response. Add framework-specific deliverables such as system description, Statement of Applicability, payment scope/validation documentation, ePHI risk analysis or the selected HITRUST assessment records.

All formal interpretations require the authoritative text and appropriate professional review. The portfolio demonstrates how to engineer and organize evidence without claiming a completed certification. Last verified: 2026-09-30 against the linked primary sources.
