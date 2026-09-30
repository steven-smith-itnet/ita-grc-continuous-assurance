#!/usr/bin/env python3
"""Export the browser presentation as a 20-page PDF. Requires optional Playwright."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8765/presentation.html')
parser.add_argument('--output', type=Path, default=Path('slides/presentation.pdf'))
args = parser.parse_args()
args.output.parent.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1280, 'height':720})
    page.goto(args.url, wait_until='networkidle')
    page.add_style_tag(content='''@page { size: 13.333in 7.5in; margin: 0; }
      @media print { .deck {min-height:0;padding:0} .slide {height:7.5in; padding:.6in .8in; box-sizing:border-box; break-after:page; overflow:hidden} .slide:last-of-type {break-after:auto} .slide .speaker {display:none} .slide h1 {font-size:34pt} .slide .lead {font-size:20pt} .slide ul {font-size:18pt} .slide li {margin:.16in 0} .eyebrow {color:#086b60} }''')
    page.pdf(path=str(args.output), print_background=True, prefer_css_page_size=True)
    browser.close()
print(args.output)
