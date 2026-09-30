# Metrics that explain risk and uncertainty

**Objective:** help managers allocate attention and help engineers locate defects. A single green score should never conceal missing scope, weak evidence or overdue risk decisions.

## Define every metric

| Metric | Calculation | Decision supported | Main limitation |
|---|---|---|---|
| Inventory reconciliation | Discovered expected resources / expected resources | Where discovery access or ownership is missing | Expected population can itself be incomplete |
| Classification coverage | Reviewed classified datasets / discovered datasets | Where control selection is uncertain | Classification correctness still needs validation |
| Evaluated control coverage | Pass + fail / pass + fail + unknown | Reliability of the current result set | Counts pairs rather than unique risk scenarios |
| Passing share | Pass / pass + fail + unknown | Distribution of tested assertions | Not a certification or risk-weighted score |
| Evidence freshness | Fresh required observations / required observations | Collector maintenance and data quality | Fresh false data remains false |
| Remediation aging | Open findings by age and risk | Staffing and escalation | Severity and due-date changes can distort trends |
| Retest success | Findings passing independent retest / submitted for retest | Quality of corrective work | Depends on representative retest scope |
| Recurrence | Reopened or repeated cause / prior closed findings | Whether root causes are addressed | Needs stable identifiers and causal analysis |
| Exception aging | Active exceptions by expiry and risk | Management acceptance backlog | Acceptance does not remove technical failure |
| Recovery achievement | Exercises meeting approved RPO/RTO/integrity / exercises | Service resilience decisions | Small exercises may not represent full recovery |

Document source, owner, refresh interval, exclusions and known bias for each metric. Preserve historical definitions so trends remain interpretable.

## Dashboard design

Show the as-of time, evidence mode, scope, state counts and unknowns above the charts. Let readers filter by provider, control, severity and state. Provide a link from a finding to its reasons and evidence references. Use text labels in addition to color for accessibility.

The browser demo displays the generated synthetic result set. Filters change the visible rows and do not silently redefine the headline program denominator. The dashboard is a read-only presentation of test output, not a connection to cloud accounts.

## Management thresholds

Set response thresholds through management approval. Examples include an unowned restricted dataset, a missed collector run for a critical service, a restore exercise failing integrity, or an expired exception on an exposed resource. These may deserve attention even when the aggregate pass rate is high.

Separate target, observed value and decision. “Target 100% owner coverage” is a proposal. “Observed 100% owner coverage” requires a defined population and evidence. Do not claim realized cost savings or audit-time reduction from an offline demonstration.

## Trend analysis

Use stable service/resource/control IDs and retain rule versions. Explain score changes caused by scope expansion, new controls or better discovery. Adding previously unknown assets can worsen a score while improving the assurance program. A falling finding count can reflect lost scanning coverage rather than safer systems.

For operational outcomes, compare like periods and populations. Report median and tail latency where relevant, not only averages. Track time to detect separately from time to collect evidence and time to remediate.

## Good, better, best

Good: reviewed counts with clear denominators. Better: automated trends and drill-down to evidence. Best: decision-focused metrics tied to risk scenarios, service commitments and tested data quality. A sophisticated visualization does not repair an unreliable denominator.

Use the dashboard alongside [reporting methodology](20-audit-reporting.md) and [testing semantics](17-testing.md).
