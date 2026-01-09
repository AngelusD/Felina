#!/usr/bin/env python3
"""Simple accessibility scanner for the local static site.

Checks (quick):
- presence of skip link
- nav elements have role/aria-label
- main landmark has id="main" and role="main"
- img tags have non-empty alt
- form inputs have ids and matching labels

Run from project root: python3 scripts/a11y_audit.py
"""
import os
import sys
from html.parser import HTMLParser


class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def check_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    p = MyParser()
    p.feed(src)

    report = []
    tags = p.tags

    # Skip link
    if 'class="skip-link"' not in src and 'href="#main"' not in src:
        report.append('Missing skip link to #main')

    # Nav check
    navs = [t for t in tags if t[0]=='nav']
    for nav in navs:
        attrs = nav[1]
        if 'role' not in attrs or attrs.get('role')!='navigation':
            report.append('Nav without role="navigation"')
        if 'aria-label' not in attrs:
            report.append('Nav missing aria-label')

    # Main check
    mains = [t for t in tags if t[0]=='main']
    if not mains:
        report.append('No <main> landmark found')
    else:
        mattrs = mains[0][1]
        if mattrs.get('id') != 'main':
            report.append('<main> missing id="main"')
        if mattrs.get('role') != 'main':
            report.append('<main> missing role="main"')

    # Images
    imgs = [t for t in tags if t[0]=='img']
    for i, img in enumerate(imgs, start=1):
        alt = img[1].get('alt')
        srcattr = img[1].get('src','')
        if alt is None or alt.strip()=='' :
            report.append(f'Image {srcattr} missing alt text')

    # Forms and inputs
    forms = [t for t in tags if t[0]=='form']
    if forms:
        inputs = [t for t in tags if t[0] in ('input','textarea','select')]
        # build map of labels
        labels = [t for t in tags if t[0]=='label']
        label_for = set()
        for lab in labels:
            if 'for' in lab[1]:
                label_for.add(lab[1]['for'])

        for inp in inputs:
            attrs = inp[1]
            if inp[0]=='input' and attrs.get('type') in ('hidden','submit','button'):
                continue
            idv = attrs.get('id')
            name = attrs.get('name','')
            if not idv:
                report.append(f'Form control name="{name}" missing id (labels may not be associated)')
            else:
                if idv not in label_for:
                    report.append(f'Form control id="{idv}" has no label with for="{idv}"')

    return report


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    html_files = [os.path.join(root, f) for f in os.listdir(root) if f.endswith('.html')]
    overall = {}
    for f in sorted(html_files):
        issues = check_file(f)
        overall[f] = issues

    any_issues = False
    for f, issues in overall.items():
        print('\n' + '='*60)
        print(f'File: {os.path.relpath(f, root)}')
        if not issues:
            print('  OK — no quick issues found')
        else:
            any_issues = True
            for it in issues:
                print('  -', it)

    print('\n' + '='*60)
    if any_issues:
        print('Accessibility quick-scan finished: issues found.')
        sys.exit(2)
    else:
        print('Accessibility quick-scan finished: no issues found.')


if __name__=='__main__':
    main()
