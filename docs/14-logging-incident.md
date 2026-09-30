# Logging, monitoring and incident response

**Objective:** detect relevant events, retain usable evidence and coordinate a response. Logging configuration, event delivery, detection logic and responder action are separate controls.

## Define the event contract

For each control and threat scenario, identify required events, source identity, timestamps, actor/resource identifiers, sensitive fields, destination, retention, parser and detection owner. Include administrative changes, privileged access, data access where required, key operations, authentication failures, deployment events, backup failures and evidence-pipeline activity.

Avoid “log everything” as an architecture. It can create cost, privacy and signal-quality problems while still missing the events needed for a specific control. Define event requirements from actual detection and assurance use cases.

## Provider path

AWS: CloudTrail for API activity, CloudWatch and service logs for operations, and approved centralized storage/query systems. Azure: Activity Log, resource diagnostics, Entra logs and Log Analytics or another approved destination. GCP: Cloud Audit Logs, Cloud Logging sinks and approved storage/BigQuery destinations. Required data-plane events often need explicit service-specific configuration.

Preserve native event schema and normalized fields. Record processing delay and dropped events. Centralized metadata may itself be sensitive and subject to residency restrictions.

## Implement and validate

1. Select the source event and a harmless synthetic canary action.
2. Configure the source and destination with scoped permissions and approved retention.
3. Generate the canary and record the expected event identifier and timestamp.
4. Verify source creation, transport, destination storage, parsing and query visibility.
5. Run detection logic and confirm a case or alert reaches the assigned responder.
6. Confirm acknowledgement and required response within the approved target.
7. Disable one stage in a sandbox and verify a pipeline-health alert.
8. Restore the stage, reconcile missing data where possible and document any irrecoverable gap.

The local `LOG-01` test requires both configured data-access logging and a received canary fact. This illustrates why checking a configuration flag alone is inadequate. Its values are synthetic and do not prove a live log pipeline exists.

## Incident operating model

Define incident severity, declaration authority, response commander, technical leads, legal/privacy involvement, customer communication, evidence custodian and regional coverage. Prepare playbooks for credential compromise, public data exposure, ransomware/recovery, malicious deployment and evidence-pipeline compromise.

A security finding can become an incident when there is suspected or confirmed adverse activity. Do not treat every policy violation as an incident, and do not wait for a compliance reporting cycle when active compromise is suspected. Legal notification decisions depend on the facts and applicable requirements and belong to authorized specialists.

## Evidence preservation

Record investigator actions and custody transfers. Preserve source identifiers, timestamps and access logs. Avoid copying production personal data into general-purpose tickets or the public project. Restrict incident evidence more tightly than ordinary dashboard summaries when needed. Verify that clocks and time zones can be reconciled.

Hashes help detect changes to a captured artifact, but they do not establish that the source was truthful or that collection was complete. Signed manifests and protected evidence stores improve provenance when tied to trusted identities and procedures.

## Good, better, best

Good: defined logging requirements, reviewed alerts and exercised response procedures. Better: automated canaries, monitored ingestion and linked incident/finding records. Best: tested detection coverage, regional response continuity and verified evidence preservation with periodic adversarial exercises.

## Tabletop scenario

A restricted storage resource becomes publicly reachable after an emergency change. The scanner detects it, but the log sink has been failing for six hours. The team must contain exposure, preserve available evidence, establish the gap, assess potential access, involve the correct decision makers and restore monitoring. The management report should show both the configuration failure and the uncertainty created by missing logs.
