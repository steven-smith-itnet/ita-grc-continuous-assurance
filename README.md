# Continuous Assurance Engineering

A multi-cloud portfolio case study connecting data inventory, classification, automated control testing, evidence engineering, remediation and audit readiness.

Inspired by a user-supplied Compliance Product Consultant role description, with the employer anonymized as **Acme**. This independent project models Acme's Technology GRC group and its fictional **Atlas Records** service. It does not describe a real organization's internal environment, an engagement, a production deployment or a completed audit.

## Start here

- [Implementation handbook](docs/00-project-charter.md)
- [Phased delivery and prerequisite gates](docs/01-phases.md)
- [Runnable lab and expected results](docs/24-lab.md)
- [AWS](docs/06-aws.md), [Azure](docs/07-azure.md) and [Google Cloud](docs/08-gcp.md)
- [Framework workstreams](docs/26-frameworks.md)
- [Production implementation boundary](docs/28-production.md)
- [Primary sources and verification](docs/30-sources.md)

## What runs

The Python evaluator tests 14 versioned control definitions against nine declared synthetic workloads. It preserves missing assets, stale evidence, invalid values and explicit applicability. Accepted risk remains a failure with an annotation. Output includes JSON, CSV, a report, input snapshots and a SHA-256 integrity manifest.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance run --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/demo
```

Expected fixed-fixture results: **87 PASS, 9 FAIL, 12 UNKNOWN, 18 NOT_APPLICABLE** across 126 pairs. One failure has an approved synthetic exception. Evaluated coverage is 88.89%. Passing share of applicable pairs is 80.56%. Neither percentage is a certification score.

The engine and tests require Python 3.11+ and no third-party packages. Provider adapters cover one narrow storage-prevention baseline. Source observations are synthetic. See the handbook for live-collector requirements and process-evidence limitations.

## Presentation site

- [Live handbook and interactive demo](https://steven-smith-itnet.github.io/techgrc-continuous-assurance/)
- [Presentation](https://steven-smith-itnet.github.io/techgrc-continuous-assurance/presentation.html)
- [GitHub repository](https://github.com/steven-smith-itnet/techgrc-continuous-assurance)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/check_site.py site
python3 -m http.server 8765 --directory site
```

Open http://localhost:8765. The site contains a searchable handbook, interactive result filters, provider/maturity comparison, architecture and phase diagrams, a 20-slide presentation with speaker notes, templates and downloadable source/evidence packages. A [20-slide PDF](slides/presentation.pdf) is included, and the presentation can also be printed from the browser. Speaker notes remain available in the HTML presentation and slide JSON.

## Standalone GitHub Pages

This project is a standalone repository at `/home/ssmith/repos/techgrc-continuous-assurance`. Its `.github/workflows/check.yml` tests and builds it. GitHub Pages uses GitHub Actions, and the Pages workflow deploys on every push to `main` or a manual run. The workflow publishes only the generated static site. Internal links work under a repository project path.

The public source ZIP uses an explicit directory/suffix allowlist. Private evidence, arbitrary artifacts, credentials, local environments and Terraform state are excluded. Do not replace synthetic fixtures with real records in a public repository.

## Repository layout

| Directory | Purpose |
|---|---|
| `docs/` | Implementation handbook and provider runbooks |
| `src/assurance/` | Deterministic evaluation, adapters and bundle verification |
| `controls/` | Versioned executable control catalog |
| `fixtures/` | Declared scope, synthetic observations and exceptions |
| `tests/` | Predicate, provenance, population, exception and adapter regressions |
| `infra/` | AWS CloudFormation/Config, Azure Bicep/Policy, GCP Terraform pilot templates |
| `queries/` | Read-only CLI and analytical examples |
| `templates/` | Registers, workpapers, readiness, findings and recovery records |
| `slides/` | Presentation content and presenter notes |
| `assets/` | CSS, browser interactions and SVG diagrams |
| `scripts/` | Site build and validation |

## Implementation status

Locally executed: synthetic evaluator, automated tests, evidence verification, site build and checks.

Authored but not live deployed: cloud templates, cloud CLI examples and enterprise workflows. Native validation and sandbox integration are required before use. The project has not collected real organizational, customer, employee, payment or health data.

Formal assessment requires authoritative framework text, approved scope, actual operating evidence and appropriate independent review. The project demonstrates the engineering and operating method without claiming certification or an audit opinion.

## Optional validation tools

Install `requirements-dev.txt` for browser checks and CloudFormation linting, then run `python -m playwright install chromium`. With the site served, `scripts/check_browser.py` checks interactions and responsive layout. `scripts/export_pdf.py` regenerates the PDF from the served presentation. Bicep and Terraform validation use their native CLIs. See [the validation record](VALIDATION.md).
