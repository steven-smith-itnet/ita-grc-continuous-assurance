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

DIRECTORIES = ('docs', 'src', 'tests', 'fixtures', 'controls', 'templates', 'infra', 'queries', 'scripts', 'assets', 'slides', '.github')
FILES = ('README.md', 'ROLE-SOURCE.md', 'VALIDATION.md', 'requirements.txt', 'requirements-dev.txt', '.gitignore')


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
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="A multi-cloud continuous assurance engineering case study with runnable synthetic evidence, phased implementation guides and audit workflows."><title>{html.escape(name)} · Continuous Assurance</title><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="topbar"><a class="brand" href="{prefix}index.html">CONTINUOUS / ASSURANCE</a><nav aria-label="Primary"><a href="{prefix}docs/00-project-charter.html">Handbook</a><a href="{prefix}dashboard.html">Evidence lab</a><a href="{prefix}presentation.html">Presentation</a><a href="{prefix}downloads.html">Downloads</a></nav></header>{('<div class="layout">' + sidebar) if sidebar else ''}{body}{'</div>' if sidebar else ''}<footer>Steven Smith · Portfolio engineering case study · Synthetic demonstration · Sources reviewed September 30, 2026</footer></body></html>'''


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
    (out / 'assets/search.json').write_text(json.dumps({p.stem: p.read_text().lower() for p in chapters}))
    for path in sources:
        if path.suffix != '.md':
            continue
        relative = path.relative_to(ROOT).with_suffix('.html')
        prefix = '../' * (len(relative.parts) - 1)
        nav = '<aside class="sidebar"><label for="chapter-search">Find a chapter</label><input id="chapter-search" type="search" placeholder="Inventory, identity, AWS…"><ol>'
        for chapter in chapters:
            label = title(chapter)
            active = ' class="active" aria-current="page"' if chapter == path else ''
            # Search includes chapter body, so technical terms beyond the title also match.
            haystack = html.escape(label.lower(), quote=True)
            nav += f'<li data-slug="{chapter.stem}" data-chapter="{haystack}"><a{active} href="{prefix}docs/{chapter.stem}.html">{html.escape(label)}</a></li>'
        nav += '</ol></aside>'
        footer = ''
        if path in chapters:
            i = chapters.index(path)
            footer = '<nav class="doc-nav" aria-label="Chapter navigation">'
            if i:
                footer += f'<a href="{chapters[i-1].stem}.html">← Previous chapter</a>'
            if i < len(chapters)-1:
                footer += f'<a href="{chapters[i+1].stem}.html">Next chapter →</a>'
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
    words = sum(len(p.read_text().split()) for p in chapters)
    sections = [
        ('01', 'Scope, data and controls', 'Establish the service boundary, discover assets, classify data and define testable objectives.', 'docs/00-project-charter.html'),
        ('02', 'Three cloud implementations', 'Follow provider-specific prerequisites, deployment patterns, collection paths and failure tests.', 'docs/06-aws.html'),
        ('03', 'Operating controls', 'Connect identity, SDLC, vulnerability, logging and recovery to verifiable process evidence.', 'docs/09-identity.html'),
        ('04', 'Evidence and remediation', 'Preserve provenance, test conservatively, investigate causes and independently verify correction.', 'docs/16-evidence.html'),
        ('05', 'Readiness and audit', 'Prepare service decisions, workpapers, management reports and coordinated regional operations.', 'docs/19-readiness.html'),
        ('06', 'Production and frameworks', 'Plan the live pilot and retain the differences among SOC 2, PCI DSS, ISO 27001, HIPAA and HITRUST.', 'docs/26-frameworks.html')]
    cards = ''.join(f'<article class="card"><span class="number">{n} / IMPLEMENTATION PATH</span><h3>{h}</h3><p>{d}</p><a href="{url}">Explore the path →</a></article>' for n,h,d,url in sections)
    landing = f'''<main id="main"><section class="hero"><div class="hero-inner"><div class="eyebrow">Multi-cloud GRC engineering / portfolio case study</div><h1>Build the controls.<br>Show the evidence.</h1><p>A complete implementation path from data inventory and classification to continuous control testing, remediation and an informed service-readiness decision.</p><div class="actions"><a class="button" href="docs/00-project-charter.html">Read the implementation handbook</a><a class="button secondary" href="dashboard.html">Explore the evidence lab →</a></div><p class="hero-note">Independent case study inspired by a supplied TechGRC role description. Fictional service, synthetic data and explicit implementation boundaries.</p><div class="stats"><div class="stat"><strong>{len(chapters)}</strong><span>handbook chapters</span></div><div class="stat"><strong>{words:,}</strong><span>words of implementation guidance</span></div><div class="stat"><strong>3</strong><span>cloud provider tracks</span></div><div class="stat"><strong>14</strong><span>runnable control definitions</span></div></div></div></section><div class="content"><div class="section-head"><h2>One evidence chain. Every stage explained.</h2><a href="presentation.html">Open the 20-slide presentation →</a></div><img class="diagram" src="assets/architecture.svg" alt="Source systems feed collectors, regional evidence storage, versioned tests, review and remediation."><div class="cards">{cards}</div><div class="section-head"><h2>Deliver through explicit gates</h2><a href="docs/01-phases.html">See prerequisites and exit evidence →</a></div><img class="diagram" src="assets/roadmap.svg" alt="Eight delivery phases from charter and inventory to automation, audit and ongoing operation."><div class="section-head"><h2>Choose the right level of engineering</h2></div><section class="card" aria-label="Cloud maturity comparison"><div class="tier-buttons" aria-label="Provider"><button data-cloud="aws" aria-pressed="true">AWS</button><button data-cloud="azure" aria-pressed="false">Azure</button><button data-cloud="gcp" aria-pressed="false">Google Cloud</button></div><div class="tier-buttons" aria-label="Maturity"><button data-tier="0" aria-pressed="true">Good</button><button data-tier="1" aria-pressed="false">Better</button><button data-tier="2" aria-pressed="false">Best when justified</button></div><p id="maturity-body" aria-live="polite">Reviewed account/region inventory, scoped API exports and manual evidence review.</p><a href="docs/25-maturity-cost.html">Compare cost, complexity and operating responsibility →</a></section><div class="notice"><strong>Inspect what is implemented.</strong> The Python evaluator, synthetic report and static site are runnable. Cloud templates and enterprise workflows are documented implementation work, with live validation still required.</div><div class="actions"><a class="button" href="docs/24-lab.html">Reproduce the lab</a> <a class="button secondary" href="downloads.html">Download source and templates</a></div></div></main>'''
    (out / 'index.html').write_text(shell('Build the controls. Show the evidence.', landing))
    counts = result['summary']['counts']
    metrics = ''.join(f'<div class="metric"><span class="badge {state}">{state.replace("_", " ")}</span><b>{count}</b></div>' for state,count in counts.items())
    bars = ''.join(f'<span class="{state}" style="width:{count/len(result["results"])*100:.4f}%" title="{state}: {count}"></span>' for state,count in counts.items())
    dashboard = f'''<main class="content" id="main"><div class="eyebrow" style="color:#08735b">REPRODUCIBLE / SYNTHETIC EVIDENCE</div><h1>Continuous control monitoring lab</h1><p>Nine declared workloads. Fourteen control definitions. One reproducible evaluation at <strong>2026-09-30 12:00 UTC</strong>.</p><div class="notice warning">This dashboard evaluates supplied synthetic observations. It is not connected to cloud accounts and does not establish framework compliance.</div><div class="metric-grid">{metrics}</div><div class="bar" role="img" aria-label="87 pass, 9 fail, 12 unknown and 18 not applicable">{bars}</div><p><strong>88.89% evaluated coverage</strong> · <strong>80.56% passing share</strong> of 108 applicable pairs · 1 accepted failure remains FAIL.</p><p><a href="docs/17-testing.html">Read the methodology</a> · <a href="data/results.csv">Download results CSV</a> · <a href="data/results.json">Inspect JSON</a> · <a href="data/manifest.json">Integrity manifest</a></p><div class="filters"><label>Provider<select id="provider"><option value="">All providers</option><option value="aws">AWS</option><option value="azure">Azure</option><option value="gcp">Google Cloud</option></select></label><label>Result state<select id="state"><option value="">All states</option>{''.join(f'<option value="{s}">{s}</option>' for s in counts)}</select></label><label>Resource or control<input type="search" id="result-search" placeholder="restore, IAM, records…"></label></div><p id="visible-count" aria-live="polite">Loading synthetic results…</p><div class="table-scroll"><table><thead><tr><th>Resource</th><th>Control</th><th>State</th><th>Exception</th><th>Reason</th></tr></thead><tbody id="result-rows"></tbody></table></div><noscript>Enable JavaScript for filtering, or download the CSV/JSON above to inspect every result.</noscript></main>'''
    (out / 'dashboard.html').write_text(shell('Evidence lab', dashboard))
    slides = json.loads((ROOT / 'slides/slides.json').read_text())
    deck = '<main class="deck" id="main">'
    for i, slide in enumerate(slides):
        hidden = ' hidden' if i else ''
        deck += f'<section class="slide"{hidden}><div class="eyebrow">CONTINUOUS ASSURANCE / {i+1:02}</div><h1>{html.escape(slide["title"])}</h1><p class="lead">{html.escape(slide["lead"])}</p><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in slide['points']) + f'</ul><details class="speaker"><summary>Presenter notes</summary><p>{html.escape(slide["notes"])}</p></details></section>'
    deck += '<div class="deck-controls"><button id="previous-slide" aria-label="Previous slide">← Previous</button><span id="slide-count" aria-live="polite">1 / 20</span><button id="next-slide" aria-label="Next slide">Next →</button><button id="print-slides">Print / save PDF</button></div></main>'
    (out / 'presentation.html').write_text(shell('Presentation', deck))
    with ZipFile(out / 'source.zip', 'w', ZIP_DEFLATED) as archive:
        for path in sources:
            archive.write(path, 'techgrc-continuous-assurance/' + str(path.relative_to(ROOT)))
    with ZipFile(out / 'synthetic-evidence.zip', 'w', ZIP_DEFLATED) as archive:
        for path in sorted((out / 'data').glob('*')):
            archive.write(path, path.name)
    pdf_link = '<p><a class="button secondary" href="slides/presentation.pdf">Download the 20-slide PDF</a></p>' if (out / 'slides/presentation.pdf').exists() else ''
    items = ''.join(f'<li><a href="templates/{p.name}">{html.escape(p.stem.replace("-", " "))}</a></li>' for p in sorted((ROOT / 'templates').glob('*')))
    downloads = f'''<main class="content" id="main"><h1>Inspectable source. Reusable artifacts.</h1><p>Download the complete project, reproduce the synthetic run, or adapt a focused template for an authorized implementation.</p><div class="cards"><article class="card"><h2>Source project</h2><p>Handbook, Python engine, tests, cloud templates, queries, slide content and site builder.</p><a class="button" href="source.zip">Download source ZIP</a></article><article class="card"><h2>Synthetic evidence</h2><p>Results, report, input snapshots and local integrity manifest from the fixed demonstration.</p><a class="button" href="synthetic-evidence.zip">Download evidence ZIP</a></article><article class="card"><h2>Run the demonstration</h2><p>Commands, expected results, mutation exercises and explicit implementation limits.</p><a class="button" href="docs/24-lab.html">Open the lab guide</a></article></div>{pdf_link}<h2>Working templates</h2><ul class="download-list">{items}</ul><h2>Cloud building blocks</h2><p><a href="infra/README.html">Read validation prerequisites</a> before using the AWS CloudFormation, Azure Bicep or GCP Terraform examples. No live deployment is claimed.</p><div class="notice">The public package is assembled from an allowlist. Live evidence, credentials, Terraform state, local environments and arbitrary artifacts are excluded.</div></main>'''
    (out / 'downloads.html').write_text(shell('Downloads', downloads))
    print(json.dumps({'output': str(out), 'chapters': len(chapters), 'handbook_words': words, 'source_files': len(sources), 'slides': len(slides)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'site')
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination == ROOT or ROOT in destination.parents and destination.parts[len(ROOT.parts)] in DIRECTORIES:
        parser.error('Output must not overwrite source directories')
    build(destination)
