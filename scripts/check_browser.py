#!/usr/bin/env python3
"""Optional rendered checks. Requires playwright and its Chromium browser."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8765/')
parser.add_argument('--artifacts', type=Path, default=Path('artifacts/browser'))
args = parser.parse_args()
args.artifacts.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1440, 'height':1000}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.goto(args.url, wait_until='networkidle')
    assert page.get_by_role('heading', name='Build the controls. Show the evidence.').count() == 1
    page.screenshot(path=str(args.artifacts / 'desktop.png'), full_page=True)
    page.get_by_role('button', name='Azure', exact=True).click()
    page.get_by_role('button', name='Better', exact=True).click()
    assert 'Purview' in page.locator('#maturity-body').inner_text()
    page.goto(args.url + 'dashboard.html', wait_until='networkidle')
    assert page.locator('#result-rows tr').count() == 126
    page.select_option('#provider', 'aws')
    assert page.locator('#result-rows tr').count() == 42
    page.select_option('#state', 'FAIL')
    assert page.locator('#result-rows tr').count() == 4
    page.fill('#result-search', 'KEY-01')
    assert page.locator('#result-rows tr').count() == 1
    assert 'Accepted risk' in page.locator('#result-rows').inner_text()
    page.goto(args.url + 'docs/03-classification.html', wait_until='networkidle')
    page.fill('#chapter-search', 'Macie')
    assert page.locator('[data-chapter]:visible').count() > 1
    assert page.locator('[data-chapter]:visible').count() < 31
    page.goto(args.url + 'projects.html', wait_until='networkidle')
    assert page.locator('.project-card').count() == 7
    page.goto(args.url + 'projects/04-evidence-data-flow/README.html', wait_until='networkidle')
    page.fill('#chapter-search', 'sampling')
    assert 0 < page.locator('[data-chapter]:visible').count() < 8
    page.goto(args.url + 'presentation.html', wait_until='networkidle')
    total = page.locator('.slide').count()
    assert page.locator('.slide:visible').count() == 1
    page.keyboard.press('ArrowRight')
    assert page.locator('#slide-count').inner_text() == f'2 / {total}'
    page.emulate_media(media='print')
    assert page.locator('.slide:visible').count() == total
    page.emulate_media(media='screen')
    for path in ['', 'dashboard.html', 'projects.html', 'projects/01-control-automation/README.html', 'docs/06-aws.html', 'presentation.html', 'downloads.html']:
        page.set_viewport_size({'width':390, 'height':844})
        page.goto(args.url + path, wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow: ' + path
    page.goto(args.url, wait_until='networkidle')
    page.screenshot(path=str(args.artifacts / 'mobile.png'), full_page=True)
    browser.close()
    assert not errors, errors
print('Browser checks passed: dashboard, projects, maturity controls, full-text search, slides, print layout and mobile overflow.')
