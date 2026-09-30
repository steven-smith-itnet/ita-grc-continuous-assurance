# Validation record

Date: 2026-09-30. All results below concern the local reference project and synthetic data.

| Check | Result | Scope and limitation |
|---|---|---|
| Python unit and provider-contract suite | 29 tests passed | Deterministic engine, malformed/missing/stale facts, scope, exceptions, integrity and narrow adapters |
| Fixed synthetic run | 87 PASS, 9 FAIL, 12 UNKNOWN, 18 NOT_APPLICABLE | 126 pairs, 108 applicable, one accepted failure |
| Bundle verification | Passed | Hashes match the local manifest. No trusted signature or timestamp is provided |
| Static site checks | Passed | Local targets/anchors, document landmarks, source allowlist and fixed result counts |
| Rendered browser checks | Passed | Chromium, 1440px desktop and 390px mobile, filters, full-text search, maturity selector, slides and print visibility |
| Existing portfolio build | Passed | Vite production build. Existing large-chunk advisory remains |
| AWS templates | cfn-lint 1.57.1 passed | CloudFormation storage template and Config pack. No AWS deployment or API collection |
| Azure template | Bicep 0.47.16 compiled | ARM output generated locally. No Azure what-if/deployment or collection |
| GCP template | Terraform 1.13.3 fmt and validate passed | Google provider 7.46.1 initialized, provider lock included. No cloud plan/apply or collection |
| Presentation | 20-slide browser deck and PDF | Speaker notes in HTML/JSON, printable deck in PDF |

## Reproduction

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance run --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/demo
python3 scripts/build_site.py
python3 scripts/check_site.py site
```

The engine has no third-party runtime dependencies. Site rendering requires the pinned Markdown dependency. Browser and CloudFormation checks require optional development dependencies. Native infrastructure validation requires Bicep/Terraform CLIs.

The workflows are configured for future GitHub execution. No remote workflow run, public-site deployment, customer environment or external assessment result is claimed.
