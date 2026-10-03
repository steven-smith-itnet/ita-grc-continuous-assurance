#!/usr/bin/env python3
"""Build a relative-link static site and synthetic-only public evidence bundle."""
import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from assurance.engine import evaluate
from assurance.__main__ import write_bundle
from assurance.projects import run_all as run_projects, write as write_projects

DIRECTORIES = ('docs', 'src', 'tests', 'fixtures', 'controls', 'projects', 'templates', 'infra', 'queries', 'scripts', 'assets', 'slides', '.github')
FILES = ('README.md', 'REQUEST-SOURCE.md', 'VALIDATION.md', 'requirements.txt', 'requirements-dev.txt', '.gitignore')


def safe_sources():
    allowed_suffixes = {'.md', '.py', '.json', '.yaml', '.yml', '.tf', '.bicep', '.csv', '.sh', '.sql', '.kql', '.css', '.js', '.svg', '.txt', '.hcl', '.pdf'}
    for directory in DIRECTORIES:
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file() and not path.is_symlink() and not any(part in path.parts for part in ('__pycache__', '.terraform', 'private-evidence', '.venv')) and path.suffix in allowed_suffixes:
                yield path
    for name in FILES:
        path = ROOT / name
        if path.exists():
            yield path


def title(path):
    return next(line[2:].strip() for line in path.read_text().splitlines() if line.startswith('# '))


def shell(name, body, prefix='', sidebar=''):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="A multi-cloud continuous assurance engineering case study with runnable synthetic evidence, phased implementation guides and audit workflows."><title>{html.escape(name)} · Continuous Assurance</title><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="topbar"><a class="brand" href="{prefix}index.html">CONTINUOUS / ASSURANCE</a><nav aria-label="Primary"><a href="{prefix}docs/00-project-charter.html">Handbook</a><a href="{prefix}dashboard.html">Evidence lab</a><a href="{prefix}projects.html">Projects</a><a href="{prefix}presentation.html">Presentation</a><a href="{prefix}downloads.html">Downloads</a></nav></header>{('<div class="layout">' + sidebar) if sidebar else ''}{body}{'</div>' if sidebar else ''}<footer>Steven Smith · Portfolio engineering case study · Synthetic demonstration · Sources last reviewed October 2, 2026</footer></body></html>'''


def render_md(text):
    rendered = markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc'])
    rendered = re.sub(r'href="([^"#?]+)\.md(#[^"]*)?"', lambda m: f'href="{m[1]}.html{m[2] or ""}"', rendered)
    return rendered.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')


def build(out):
    out.mkdir(parents=True, exist_ok=True)
    chapters = sorted((ROOT / 'docs').glob('*.md'))
    sources = list(safe_sources())
    for path in sources:
        relative = path.relative_to(ROOT)
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    (out / '.nojekyll').write_text('')
    project_pages = [ROOT / 'projects/README.md'] + sorted((ROOT / 'projects').glob('*/README.md'))
    def slug(page):
        return page.stem if page in chapters else 'p-' + (page.parent.name if page.parent.name != 'projects' else 'overview')
    (out / 'assets/search.json').write_text(json.dumps({slug(p): p.read_text().lower() for p in chapters + project_pages}))
    for path in sources:
        if path.suffix != '.md':
            continue
        relative = path.relative_to(ROOT).with_suffix('.html')
        prefix = '../' * (len(relative.parts) - 1)
        group, noun = (project_pages, 'project') if path in project_pages else (chapters, 'chapter')
        placeholder = 'Sampling, drift, canary, SOC 2…' if noun == 'project' else 'Inventory, identity, AWS…'
        nav = f'<aside class="sidebar"><label for="chapter-search">Find a {noun}</label><input id="chapter-search" type="search" placeholder="{placeholder}"><ol>'
        for page in group:
            label = title(page)
            active = ' class="active" aria-current="page"' if page == path else ''
            # Search includes the page body, so technical terms beyond the title also match.
            haystack = html.escape(label.lower(), quote=True)
            href = prefix + page.relative_to(ROOT).with_suffix('.html').as_posix()
            nav += f'<li data-slug="{slug(page)}" data-chapter="{haystack}"><a{active} href="{href}">{html.escape(label)}</a></li>'
        nav += '</ol></aside>'
        footer = ''
        if path in group:
            i = group.index(path)
            link = lambda page: prefix + page.relative_to(ROOT).with_suffix('.html').as_posix()
            footer = f'<nav class="doc-nav" aria-label="{noun.title()} navigation">'
            if i:
                footer += f'<a href="{link(group[i-1])}">← Previous {noun}</a>'
            if i < len(group)-1:
                footer += f'<a href="{link(group[i+1])}">Next {noun} →</a>'
            footer += '</nav>'
        body = '<main class="doc" id="main">' + render_md(path.read_text()) + footer + '</main>'
        (out / relative).write_text(shell(title(path), body, prefix, nav))
    scope = json.loads((ROOT / 'fixtures/scope.json').read_text())
    evidence = json.loads((ROOT / 'fixtures/evidence.json').read_text())
    if evidence.get('synthetic') is not True:
        raise ValueError('Public build requires explicitly synthetic fixture evidence')
    catalog = json.loads((ROOT / 'controls/catalog.json').read_text())
    exceptions = json.loads((ROOT / 'fixtures/exceptions.json').read_text())
    result = evaluate(scope, evidence, catalog, '2026-09-30T12:00:00Z', exceptions)
    write_bundle(result, out / 'data', {'scope.json': scope, 'evidence.json': evidence, 'catalog.json': catalog, 'exceptions.json': exceptions})
    slides = json.loads((ROOT / 'slides/slides.json').read_text())
    project_summary = write_projects(run_projects(ROOT, '2026-09-30T12:00:00Z'), out / 'data/projects', '2026-09-30T12:00:00Z')
    words = sum(len(p.read_text().split()) for p in chapters)
    project_words = sum(len(p.read_text().split()) for p in project_pages)
    sections = [
        ('01', 'Scope, data and controls', 'Establish the service boundary, discover assets, classify data and define testable objectives.', 'docs/00-project-charter.html'),
        ('02', 'Three cloud implementations', 'Follow provider-specific prerequisites, deployment patterns, collection paths and failure tests.', 'docs/06-aws.html'),
        ('03', 'Operating controls', 'Connect identity, SDLC, vulnerability, logging and recovery to verifiable process evidence.', 'docs/09-identity.html'),
        ('04', 'Evidence and remediation', 'Preserve provenance, test conservatively, investigate causes and independently verify correction.', 'docs/16-evidence.html'),
        ('05', 'Readiness and audit', 'Prepare service decisions, workpapers, management reports and coordinated regional operations.', 'docs/19-readiness.html'),
        ('06', 'Production and frameworks', 'Plan the live pilot and retain the differences among SOC 2, PCI DSS, ISO 27001, HIPAA and HITRUST.', 'docs/26-frameworks.html')]
    cards = ''.join(f'<article class="card"><span class="number">{n} / IMPLEMENTATION PATH</span><h3>{h}</h3><p>{d}</p><a href="{url}">Explore the path →</a></article>' for n,h,d,url in sections)
    blurbs = {
        '01-control-automation': 'Eight use cases that join HR, identity, CI/CD, backup, scanner and cloud API records into control results.',
        '02-configuration-drift': 'One storage baseline normalized across AWS, Azure and GCP, with every change classified as authorized or not.',
        '03-control-evaluation': 'Seeded faults that separate sound control logic from plausible logic that hides exceptions.',
        '04-evidence-data-flow': 'Hop-by-hop reconciliation of evidence pipelines, and what each defect does to control results.',
        '05-remediation-testing': 'Closure criteria that a fix must meet, and tests of automatic remediation that can loop or overreach.',
        '06-audit-process-testing': 'Population reconciliation, reproducible sampling, period coverage and evidence-request quality.',
        '07-framework-coverage': 'SOC 2 first, then ISO 27001 and HIPAA: coverage from declared mappings and the next use cases to build.'}
    project_links = ''.join(f'<article class="card"><span class="number">{folder[:2]} / PROJECT</span><h3>{html.escape(project_summary["projects"][folder]["title"])}</h3><p>{blurbs[folder]}</p><a href="projects/{folder}/README.html">Open the project →</a></article>' for folder in project_summary['projects'])
    landing = f'''<main id="main"><section class="hero"><div class="hero-inner"><div class="eyebrow">Multi-cloud GRC engineering / portfolio case study</div><h1>Build the controls.<br>Show the evidence.</h1><p>A complete implementation path from data inventory and classification to continuous control testing, remediation and an informed service-readiness decision.</p><div class="actions"><a class="button" href="docs/00-project-charter.html">Read the implementation handbook</a><a class="button secondary" href="dashboard.html">Explore the evidence lab →</a></div><p class="hero-note">Independent case study inspired by a client compliance request. Fictional service, synthetic data and explicit implementation boundaries.</p><div class="stats"><div class="stat"><strong>{len(chapters)}</strong><span>handbook chapters</span></div><div class="stat"><strong>{words:,}</strong><span>words of implementation guidance</span></div><div class="stat"><strong>7</strong><span>deeper runnable projects</span></div><div class="stat"><strong>{14 + len(project_summary['projects']['01-control-automation']['summary']['by_usecase'])}</strong><span>automated control tests</span></div></div></div></section><div class="content"><div class="section-head"><h2>One evidence chain. Every stage explained.</h2><a href="presentation.html">Open the {len(slides)}-slide presentation →</a></div><img class="diagram" src="assets/architecture.svg" alt="Source systems feed collectors, regional evidence storage, versioned tests, review and remediation."><div class="cards">{cards}</div><div class="section-head"><h2>Seven deeper projects from the request's priorities</h2><a href="projects.html">Open the projects lab →</a></div><div class="cards">{project_links}</div><div class="section-head"><h2>Deliver through explicit gates</h2><a href="docs/01-phases.html">See prerequisites and exit evidence →</a></div><img class="diagram" src="assets/roadmap.svg" alt="Eight delivery phases from charter and inventory to automation, audit and ongoing operation."><div class="section-head"><h2>Choose the right level of engineering</h2></div><section class="card" aria-label="Cloud maturity comparison"><div class="tier-buttons" aria-label="Provider"><button data-cloud="aws" aria-pressed="true">AWS</button><button data-cloud="azure" aria-pressed="false">Azure</button><button data-cloud="gcp" aria-pressed="false">Google Cloud</button></div><div class="tier-buttons" aria-label="Maturity"><button data-tier="0" aria-pressed="true">Good</button><button data-tier="1" aria-pressed="false">Better</button><button data-tier="2" aria-pressed="false">Best when justified</button></div><p id="maturity-body" aria-live="polite">Reviewed account/region inventory, scoped API exports and manual evidence review.</p><a href="docs/25-maturity-cost.html">Compare cost, complexity and operating responsibility →</a></section><div class="notice"><strong>Inspect what is implemented.</strong> The Python evaluator, synthetic report and static site are runnable. Cloud templates and enterprise workflows are documented implementation work, with live validation still required.</div><div class="actions"><a class="button" href="docs/24-lab.html">Reproduce the lab</a> <a class="button secondary" href="downloads.html">Download source and templates</a></div></div></main>'''
    (out / 'index.html').write_text(shell('Build the controls. Show the evidence.', landing))
    def priority(page):
        line = next((l for l in page.read_text().splitlines() if l.startswith('**Role priority:**')), '')
        text = line.replace('**Role priority:**', '').strip()
        return text[:1].upper() + text[1:]
    project_cards = ''
    for page in project_pages[1:]:
        folder = page.parent.name
        info = project_summary['projects'][folder]
        facts = ''.join(f'<li><b>{html.escape(str(v))}</b> {html.escape(k)}</li>' for k, v in info['headline'].items())
        files = ' · '.join(f'<a href="data/projects/{folder}/{name}">{label}</a>' for name, label in (('report.md', 'Report'), ('results.csv', 'CSV'), ('results.json', 'JSON'), ('manifest.json', 'Manifest')))
        project_cards += f'''<article class="card project-card"><span class="number">{folder[:2]} / PROJECT</span><h2>{html.escape(info['title'])}</h2><p class="priority">{html.escape(priority(page))}</p><ul class="headline">{facts}</ul><p><a href="projects/{folder}/README.html">Read the project →</a></p><p class="files">{files}</p></article>'''
    projects_page = f'''<main class="content" id="main"><div class="eyebrow" style="color:#08735b">SEVEN DEEPER PROJECTS / SYNTHETIC EVIDENCE</div><h1>Deeper projects</h1><p>Each project answers one priority from the <a href="REQUEST-SOURCE.html#supplementary-priorities">supplementary request priorities</a>: building control automation use cases, testing configuration, evaluating a control, testing how evidence reaches the control, verifying remediation, testing the audit process and prioritizing SOC 2, ISO 27001 and HIPAA. All seven run from the same fixed as-of time, <strong>2026-09-30 12:00 UTC</strong>.</p><div class="notice warning">Every record is synthetic. The cloud API shapes follow provider documentation, but nothing here ran against a cloud account or establishes compliance.</div><div class="cards projects-grid">{project_cards}</div><h2>How the projects connect</h2><ol><li>Project 01 passes worker W-1004 on the HR data in the evidence store.</li><li>Project 04 finds the HR integration dropped a UTC offset for that record. Recomputed from the source, W-1004 fails.</li><li>Project 03 shows a simpler leaver check would also miss an active AWS access key for another worker.</li><li>Project 02 detects an unauthorized change to aws-records-01, and Project 04 shows the SIEM never received the CloudTrail event for it.</li><li>Project 05 keeps that finding open until three independent runs pass, and blocks a vulnerability closure while a sibling server still fails.</li><li>Project 07 turns the uncovered SOC 2 criteria into the next use cases to build.</li></ol><h2>Reproduce every result</h2><pre><code>PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m assurance projects --as-of 2026-09-30T12:00:00Z
PYTHONPATH=src python3 -m assurance verify artifacts/projects/01-control-automation</code></pre><p><a href="projects/README.html">Read the projects overview</a> · <a href="data/projects/summary.json">Download the summary JSON</a></p></main>'''
    (out / 'projects.html').write_text(shell('Deeper projects', projects_page))
    counts = result['summary']['counts']
    metrics = ''.join(f'<div class="metric"><span class="badge {state}">{state.replace("_", " ")}</span><b>{count}</b></div>' for state,count in counts.items())
    bars = ''.join(f'<span class="{state}" style="width:{count/len(result["results"])*100:.4f}%" title="{state}: {count}"></span>' for state,count in counts.items())
    dashboard = f'''<main class="content" id="main"><div class="eyebrow" style="color:#08735b">REPRODUCIBLE / SYNTHETIC EVIDENCE</div><h1>Continuous control monitoring lab</h1><p>Nine declared workloads. Fourteen control definitions. One reproducible evaluation at <strong>2026-09-30 12:00 UTC</strong>.</p><div class="notice warning">This dashboard evaluates supplied synthetic observations. It is not connected to cloud accounts and does not establish framework compliance.</div><div class="metric-grid">{metrics}</div><div class="bar" role="img" aria-label="87 pass, 9 fail, 12 unknown and 18 not applicable">{bars}</div><p><strong>88.89% evaluated coverage</strong> · <strong>80.56% passing share</strong> of 108 applicable pairs · 1 accepted failure remains FAIL.</p><p><a href="docs/17-testing.html">Read the methodology</a> · <a href="data/results.csv">Download results CSV</a> · <a href="data/results.json">Inspect JSON</a> · <a href="data/manifest.json">Integrity manifest</a></p><div class="filters"><label>Provider<select id="provider"><option value="">All providers</option><option value="aws">AWS</option><option value="azure">Azure</option><option value="gcp">Google Cloud</option></select></label><label>Result state<select id="state"><option value="">All states</option>{''.join(f'<option value="{s}">{s}</option>' for s in counts)}</select></label><label>Resource or control<input type="search" id="result-search" placeholder="restore, IAM, records…"></label></div><p id="visible-count" aria-live="polite">Loading synthetic results…</p><div class="table-scroll"><table><thead><tr><th>Resource</th><th>Control</th><th>State</th><th>Exception</th><th>Reason</th></tr></thead><tbody id="result-rows"></tbody></table></div><noscript>Enable JavaScript for filtering, or download the CSV/JSON above to inspect every result.</noscript></main>'''
    (out / 'dashboard.html').write_text(shell('Evidence lab', dashboard))
    deck = '<main class="deck" id="main">'
    for i, slide in enumerate(slides):
        hidden = ' hidden' if i else ''
        deck += f'<section class="slide"{hidden}><div class="eyebrow">CONTINUOUS ASSURANCE / {i+1:02}</div><h1>{html.escape(slide["title"])}</h1><p class="lead">{html.escape(slide["lead"])}</p><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in slide['points']) + f'</ul><details class="speaker"><summary>Presenter notes</summary><p>{html.escape(slide["notes"])}</p></details></section>'
    deck += f'<div class="deck-controls"><button id="previous-slide" aria-label="Previous slide">← Previous</button><span id="slide-count" aria-live="polite">1 / {len(slides)}</span><button id="next-slide" aria-label="Next slide">Next →</button><button id="print-slides">Print / save PDF</button></div></main>'
    (out / 'presentation.html').write_text(shell('Presentation', deck))
    with ZipFile(out / 'source.zip', 'w', ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, 'ita-grc-continuous-assurance/' + str(path.relative_to(ROOT)))
    with ZipFile(out / 'synthetic-evidence.zip', 'w', ZIP_DEFLATED) as archive:
        for path in sorted((out / 'data').rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(out / 'data').as_posix())
    pdf_link = f'<p><a class="button secondary" href="slides/presentation.pdf">Download the {len(slides)}-slide PDF</a></p>' if (out / 'slides/presentation.pdf').exists() else ''
    items = ''.join(f'<li><a href="templates/{p.name}">{html.escape(p.stem.replace("-", " "))}</a></li>' for p in sorted((ROOT / 'templates').glob('*')))
    downloads = f'''<main class="content" id="main"><h1>Inspectable source. Reusable artifacts.</h1><p>Download the complete project, reproduce the synthetic run, or adapt a focused template for an authorized implementation.</p><div class="cards"><article class="card"><h2>Source project</h2><p>Handbook, Python engine, tests, cloud templates, queries, slide content and site builder.</p><a class="button" href="source.zip">Download source ZIP</a></article><article class="card"><h2>Synthetic evidence</h2><p>Results, reports, input snapshots and local integrity manifests from the base lab and all seven deeper projects.</p><a class="button" href="synthetic-evidence.zip">Download evidence ZIP</a></article><article class="card"><h2>Run the demonstration</h2><p>Commands, expected results, mutation exercises and explicit implementation limits.</p><a class="button" href="docs/24-lab.html">Open the lab guide</a></article></div>{pdf_link}<h2>Working templates</h2><ul class="download-list">{items}</ul><h2>Cloud building blocks</h2><p><a href="infra/README.html">Read validation prerequisites</a> before using the AWS CloudFormation, Azure Bicep or GCP Terraform examples. No live deployment is claimed.</p><div class="notice">The public package is assembled from an allowlist. Live evidence, credentials, Terraform state, local environments and arbitrary artifacts are excluded.</div></main>'''
    (out / 'downloads.html').write_text(shell('Downloads', downloads))
    print(json.dumps({'output': str(out), 'chapters': len(chapters), 'handbook_words': words, 'project_pages': len(project_pages), 'project_words': project_words, 'source_files': len(sources), 'slides': len(slides)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination == ROOT or ROOT in destination.parents and destination.parts[len(ROOT.parts)] in DIRECTORIES:
        parser.error('Output must not overwrite source directories')
    build(destination)
