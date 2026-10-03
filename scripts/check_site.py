#!/usr/bin/env python3
"""Check generated local references, document structure and downloadable content."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from zipfile import ZipFile
import hashlib
import json
import sys

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.title = False
        self.lang = False
        self.main = False
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.title |= tag == 'title'
        self.lang |= tag == 'html' and values.get('lang') == 'en'
        self.main |= tag == 'main'
        if 'id' in values: self.ids.add(values['id'])
        for key in ('href', 'src'):
            if key in values: self.links.append(values[key])

def check(root):
    root = root.resolve()
    pages = {}
    errors = []
    for file in root.rglob('*.html'):
        parser = Page()
        parser.feed(file.read_text())
        pages[file] = parser
        if not (parser.title and parser.lang and parser.main):
            errors.append(f'Missing document landmark: {file}')
    for file, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc: continue
            target = (file.parent / unquote(url.path)).resolve() if url.path else file
            if root != target and root not in target.parents:
                errors.append(f'Link escapes site: {file}: {link}')
                continue
            if not target.exists(): errors.append(f'Missing target: {file}: {link}')
            if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'Missing anchor: {file}: {link}')
    with ZipFile(root / 'source.zip') as archive:
        for name in archive.namelist():
            if any(part in name.split('/') for part in ('.venv', 'private-evidence', 'artifacts', '.terraform', '__pycache__')) or '.tfstate' in name:
                errors.append('Forbidden source package member: ' + name)
    result = json.loads((root / 'data/results.json').read_text())
    if result['synthetic'] is not True: errors.append('Public report is not synthetic')
    if result['summary']['counts'] != {'PASS':87, 'FAIL':9, 'UNKNOWN':12, 'NOT_APPLICABLE':18}:
        errors.append('Fixture counts changed: update and review presentation claims')
    summary = json.loads((root / 'data/projects/summary.json').read_text())
    if summary.get('synthetic') is not True or len(summary['projects']) != 7:
        errors.append('Project summary missing, incomplete or not synthetic')
    expected = {'01-control-automation': {'PASS': 21, 'FAIL': 21, 'UNKNOWN': 8, 'NOT_APPLICABLE': 9},
                '02-configuration-drift': {'PASS': 17, 'FAIL': 3, 'UNKNOWN': 1, 'NOT_APPLICABLE': 3}}
    for slug, counts in expected.items():
        if summary['projects'].get(slug, {}).get('summary', {}).get('counts') != counts:
            errors.append(f'Project {slug} counts changed: update and review the project write-up and slides')
    for slug in summary['projects']:
        folder = root / 'data/projects' / slug
        manifest = json.loads((folder / 'manifest.json').read_text())
        for name, digest in manifest['sha256'].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
                errors.append(f'Project bundle hash mismatch: {slug}/{name}')
    with ZipFile(root / 'source.zip') as archive:
        if 'ita-grc-continuous-assurance/projects/README.md' not in archive.namelist():
            errors.append('Projects missing from the source package')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Validated {len(pages)} HTML pages, local links/anchors, source package, project bundles and synthetic result counts.')

if __name__ == '__main__':
    check(Path(sys.argv[1] if len(sys.argv)>1 else 'site'))
