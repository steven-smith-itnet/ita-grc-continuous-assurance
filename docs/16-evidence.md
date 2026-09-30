# Evidence engineering and chain of custody

**Objective:** make each reported result traceable to an identified source, population, time and test version while minimizing unnecessary exposure of sensitive information.

## Evidence lifecycle

Define request, collection, validation, normalization, evaluation, review, retention, export and disposal. Assign an owner to every stage. Separate the people who administer the evidence store from those who approve assurance reports when feasible.

An evidence item needs a stable ID, source system, native resource ID, collection scope, observed time, collected time, collector version, control/test version, content hash, classification, storage reference, retention policy and access rules. Preserve source request parameters, pagination totals and errors. For human evidence, retain the identity and authority of the person making the statement and the supporting records.

## Integrity is more than hashing

The local bundle includes a SHA-256 manifest. It detects content changes relative to the included manifest. An attacker who can replace both the files and manifest can recompute the hashes. A production chain can add signed manifests, protected signing keys, trusted time, restricted storage writes, versioning, appropriate retention and independent verification.

Do not label a local hash as proof of source authenticity or nonrepudiation. Likewise, immutable storage preserves what was written but cannot make false or incomplete input accurate.

## Raw and normalized evidence

Retain raw exports in a protected location when permitted. Create normalized facts for tests, each linked to its source. Avoid repeatedly copying sensitive payloads into every result or ticket. Normalize provider fields only when their semantics are understood. Keep native states alongside canonical states so a reviewer can reconstruct the interpretation.

For example, an Azure Policy exemption, an AWS rule's insufficient-data state and an unavailable GCP observation must not all become “pass.” The normalized schema should explicitly preserve evidence quality and applicability decisions.

## Period and population

Define the reporting period before collecting the audit packet. Identify resources and identities that existed at any relevant point during that period, including deleted assets. Preserve time-of-event, time-of-observation and time-of-collection separately. A current screenshot cannot prove what was true six months ago.

For sample-based tests, preserve the full population, sampling method, exclusions, chosen items and rationale. Let the assessor determine or agree the appropriate sample strategy. Automation can collect broadly, but it does not eliminate judgment about the reliability and relevance of evidence.

## Minimize and segregate

Classify raw evidence and reports. Redact secrets, customer identifiers and unnecessary personnel information before approved export. Maintain the original privately when needed for traceability, and record what was redacted. Keep regional evidence in approved locations and aggregate only permitted summaries across borders.

The public site in this repository is built from synthetic fixtures and an explicit source allowlist. `private-evidence/`, live credentials, Terraform state and arbitrary artifacts are excluded from the downloadable package. Adding a new source path to the publisher is a reviewable security change.

## Evidence request workflow

1. Create the request with requirement, period, population, owner and due date.
2. Confirm expected evidence with the requester so teams do not collect irrelevant screenshots.
3. Collect through approved access and record failures.
4. Validate completeness, timestamp, source identity and schema.
5. Attach normalized results and retained source references.
6. Have an independent reviewer assess sufficiency and resolve questions.
7. Export a versioned packet through approved channels and log delivery/access.
8. Retain or dispose according to the approved schedule and holds.

## Good, better, best

Good: controlled repository of dated exports and an evidence index. Better: automated source collection, schema validation and protected versioned storage. Best: authenticated collection, signed releases, tested retention and regional custody with measurable quality SLOs.

## Demonstration

Run the lab, verify the manifest, copy the bundle to a temporary directory and alter one result file. Verification must fail. Then explain why an attacker who replaces the manifest remains outside this local check's protection. This demonstrates both a useful mechanism and a correct understanding of its limits.

Artifacts: [evidence contract](../templates/evidence-contract.json), [PBC register](../templates/pbc-register.csv), [local run](24-lab.md).
