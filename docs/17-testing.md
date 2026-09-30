# Automated testing, evidence quality and confidence

**Objective:** turn defined control assertions into repeatable results without hiding missing data or implying broader assurance than the test supports.

## Test architecture

The prototype uses Python's standard library. `scope.json` declares the population, `evidence.json` contains dated observations, `catalog.json` defines predicates, and `exceptions.json` supplies risk decisions. The CLI writes JSON, CSV, a Markdown report and a hash manifest.

The engine evaluates each declared asset against each control. Applicability uses scope metadata. Missing applicability metadata becomes unknown. A resource absent from evidence remains in the population. Evidence for an undeclared asset is rejected so the operator must reconcile scope instead of silently expanding it.

## Result semantics

| State | Meaning | Management treatment |
|---|---|---|
| PASS | All defined predicates satisfied by fresh, structurally valid observations | Limited to the specified assertion and evidence source |
| FAIL | At least one tested predicate demonstrably false | Finding/triage, owner and remediation |
| UNKNOWN | Required evidence unavailable, stale, malformed or future-dated | Collection or assessment gap, never a pass |
| NOT_APPLICABLE | Scope metadata places the asset outside the defined control population | Retain rationale and review applicability |

A proven failure remains a failure even when another predicate is unknown. This preserves known risk. An accepted exception is an annotation on a failure, not an alternative passing status.

## Evidence predicates and boundaries

Booleans must be real JSON booleans. The string `"true"` is not accepted. Numeric metrics must be finite and nonnegative. Timestamps require a timezone, and future observations do not satisfy freshness checks. A missing source reference invalidates a fact for evaluation.

The default controls require observations collected within 24 hours. That is a lab freshness policy. The underlying business events have separate windows, such as an access review within 90 days. Recollecting an old review today does not make the review recent.

The executable field checks do not authenticate a source or independently calculate supplied process booleans. They provide a deterministic testing contract. Production adapters must derive facts from reliable source systems and preserve provenance.

## Test pyramid

1. **Unit tests:** predicate boundaries, missing fields, dates, state precedence, exception expiry and denominator math.
2. **Contract tests:** provider response shape, null handling, required fields and semantic assumptions.
3. **Sandbox integration tests:** read permissions, pagination, API errors, actual configuration changes and source timestamps.
4. **Control validation:** independent reviewer verifies that the predicate actually tests the intended objective.
5. **Operating-period assessment:** preserve repeated results and review whether the control operated over the relevant period.

The repository implements the first two levels and the synthetic pipeline. The other levels are documented execution tasks requiring appropriate access and review.

## Catalog change safety

A new rule needs a positive case, a known failure, missing evidence, boundary values and applicability tests. Include tests for unsupported provider behavior. Version the predicate and mapping. Retain historical rule versions rather than silently rewriting conclusions.

Test collector failures separately from control failures. A denied API query should return a collection error with the affected scope. It should not produce an empty successful list. For large populations, test rate limits, pagination, duplicates and eventual consistency.

## Score interpretation

Coverage is `(PASS + FAIL) / (PASS + FAIL + UNKNOWN)`. Passing share is `PASS / (PASS + FAIL + UNKNOWN)`. Not-applicable pairs are excluded with an explicit count. Accepted failures remain failures in both metrics. A low unknown count improves coverage but does not necessarily reduce risk.

Pair-level scores give equal weight to every applicable asset/control pair. They are not risk-weighted, and several pairs can share the same underlying process evidence. Present that limitation rather than calling the number a “compliance score.”

## Good, better, best

Good: reviewed deterministic scripts and reproducible fixtures. Better: validated source adapters, CI checks and collector-health monitoring. Best: independently reviewed control releases, historical evidence lineage and mutation/chaos testing of the assurance pipeline.

Run [the lab](24-lab.md) and inspect [the tests](../tests/test_assurance.py). Use the browser dashboard to explore results, then reproduce them from source.
