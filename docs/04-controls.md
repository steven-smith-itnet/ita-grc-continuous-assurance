# Convert obligations into controls and evidence contracts

**Objective:** create a traceable path from a business requirement to an implementable control and a defensible conclusion.

The chain is `obligation → risk → control objective → implementation → test → evidence → finding → remediation → retest`. Every edge should have an identifier. A tool recommendation without this chain is difficult to defend or maintain.

## Write a control that can be tested

A useful implementation statement names who performs an action, on which population, at what frequency, using which system, and what record is retained. For example: “The platform team enforces explicit anonymous-access prevention on each in-scope storage resource. A daily collector obtains the provider setting, and the GRC team reviews exceptions within the assigned service level.” This is a local baseline, not a complete statement of cloud-storage security.

Avoid “all data is secure.” Replace it with specific objectives for exposure, encryption, keys, access, logging, retention and recoverability. An encrypted public dataset illustrates why those need separate tests.

## The control record

| Field | Required decision |
|---|---|
| Stable ID and version | Identify the exact rule used for the reporting period |
| Objective and risk | Explain the loss scenario being reduced |
| Accountable owner and operator | Separate responsibility from execution |
| Population and applicability | Explain inclusions, exclusions and dependencies |
| Preventive/detective/corrective type | State what the mechanism actually does |
| Frequency and evidence freshness | Distinguish performance frequency from collection timing |
| Predicate and expected result | Make automatic assertions unambiguous |
| Evidence method | Examination, interview, technical test, or combination |
| Failure and unknown treatment | Define finding versus collection defect |
| Mapping and limitations | Show which requirement aspect is addressed and what remains |
| Exception authority | Define approver, duration and compensation |
| Retest and closure | Identify independent reviewer and success criteria |

Assessment methods can combine examination, interviews and testing. The project uses NIST's assessment approach as a methodology reference, not as a claim of a completed NIST assessment. [NIST SP 800-53A](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final).

## Design, implementation and operating effectiveness

Design asks whether the intended mechanism could reduce the stated risk. Implementation asks whether that mechanism exists in the scoped environment. Operating effectiveness asks whether it worked throughout the relevant period. These are different propositions with different evidence.

For access reviews, a written quarterly procedure supports design. A configured campaign supports implementation. A complete population, dated reviewer decisions, timely removals and verification of those removals support operation. A screenshot of a completed campaign alone may omit excluded identities or unresolved revocations.

## Version mappings without overstating equivalence

Maintain framework version, requirement identifier, local control ID, mapping rationale, coverage type, residual requirements, reviewer and review date. Mark each mapping as candidate until the appropriate reviewer validates it. One technical control may support multiple frameworks, but the underlying requirement text, scope, evidence period and assessor judgment can differ.

The local catalog contains 14 runnable predicates. The broader program requires many more controls across organizational, personnel, supplier, physical and legal domains. Use [the framework workstreams](26-frameworks.md) and [organizational coverage](27-organizational-controls.md) to complete the program boundary.

## Evidence contracts

Define a contract before writing each collector. Include source API, credential scope, authoritative resource identifier, requested scope, observation and collection timestamps, result schema, page counts, errors, filter parameters, source version and source-object reference. Sensitive raw payloads remain protected. Normalized observations reference their provenance rather than duplicating confidential content everywhere.

A true boolean from an untrusted form is not evidence of an actual technical check. The demo intentionally accepts synthetic facts for reproducibility. Production must authenticate source systems, protect the normalization pipeline and independently validate control facts such as `change_separation_verified`.

## Change management for the control catalog

Submit predicate changes through a pull request. Attach positive, negative, boundary and missing-evidence tests. The control steward reviews the assurance consequence, while an engineer reviews correctness. Record whether the change is a bug fix or a policy change. Do not silently re-score a historical period under new logic. Preserve old catalog versions and present restated results separately when necessary.

Artifacts: [executable catalog](../controls/catalog.json), [control matrix template](../templates/control-matrix.csv), [evidence contract template](../templates/evidence-contract.json).
