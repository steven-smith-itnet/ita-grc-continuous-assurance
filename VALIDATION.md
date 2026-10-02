# Validation record

Latest run: 2026-10-02. First recorded: 2026-09-30. All results below concern the local reference project and synthetic data.

| Check | Result | Scope and limitation |
|---|---|---|
| Python unit, provider-contract and project suite | 72 tests passed on Python 3.14.4 and 3.11.16 | 29 base-lab tests plus 43 project tests: derived use cases, normalization, seeded faults, flow reconciliation, closure decisions, sampling, period windows and coverage validation |
| Fixed base-lab run | 87 PASS, 9 FAIL, 12 UNKNOWN, 18 NOT_APPLICABLE | 126 pairs, 108 applicable, one accepted failure. Unchanged by the projects |
| Deeper projects run | Seven bundles, results identical on Python 3.11 and 3.14 | Headline results are listed in [the projects overview](projects/README.md) |
| Bundle verification | Passed for the base lab and all seven project bundles | Hashes match each local manifest. No trusted signature or timestamp is provided |
| Documented exercises | Each project's exercises produced the described result | Run as scripted fixture changes, not against cloud accounts |
| Static site checks | Passed: 56 HTML pages | Local targets and anchors, document landmarks, source allowlist, project bundle hashes and fixed result counts |
| Rendered browser checks | Passed | Chromium at 1440px and 390px: dashboard filters, projects page, project search, maturity selector, slides, print visibility and no horizontal overflow |
| External references | Checked 2026-10-02 | HIPAA designations, GitHub review fields, S3 versioning, AWS Config rule names, KMS rotation fields, Azure Shared Key and Resource Graph paging, Google Cloud constraints and audit-log defaults. See [the source register](docs/30-sources.md) |
| AWS templates | cfn-lint 1.57.1 passed on 2026-09-30 | CloudFormation storage template and Config pack. Not changed since. No AWS deployment or API collection |
| Azure template | Bicep 0.47.16 compiled on 2026-09-30 | Not changed since. No Azure what-if, deployment or collection |
| GCP template | Terraform 1.13.3 fmt and validate passed on 2026-09-30 | Not changed since. No cloud plan, apply or collection |
| Presentation | 24-slide browser deck and PDF | Four slides added for the projects. Speaker notes in HTML and JSON |

## Reproduction

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance run --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/demo
PYTHONPATH=src python3 -m assurance projects --as-of 2026-09-30T12:00:00Z
for d in artifacts/projects/*/; do PYTHONPATH=src python3 -m assurance verify "$d"; done
python3 scripts/build_site.py
python3 scripts/check_site.py site
```

The engine and projects have no third-party runtime dependencies. Site rendering requires the pinned Markdown dependency. Browser and CloudFormation checks require optional development dependencies. Native infrastructure validation requires the Bicep and Terraform CLIs.

The workflows are configured for GitHub execution. This record does not claim a remote workflow run, a customer environment or an external assessment result.
