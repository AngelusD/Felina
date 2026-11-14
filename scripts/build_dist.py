#!/usr/bin/env python3
"""Copy ONLY what the website needs into dist/ — this is the folder to upload.

Leaves out: the huge original photos, scripts/, docs, git, and any image the pages don't use.
Run from the project root (after build_pages.py):  python3 scripts/build_dist.py
"""
import glob, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DIST = 'dist'
shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(DIST)

files = glob.glob('*.html') + ['css/styles.css', 'js/main.js', 'sitemap.xml', 'robots.txt', 'CNAME']
used = set()
for f in glob.glob('*.html') + ['css/styles.css', 'js/main.js']:
    txt = open(f, encoding='utf-8').read()
    used |= set(re.findall(r'assets/web/[A-Za-z0-9_.-]+\.(?:jpg|webp|png)', txt))
files += sorted(used)

for f in files:
    dst = os.path.join(DIST, f)
    os.makedirs(os.path.dirname(dst) or DIST, exist_ok=True)
    shutil.copy2(f, dst)

size = sum(os.path.getsize(os.path.join(d, x)) for d, _, fs in os.walk(DIST) for x in fs)
print(f'dist/: {len(files)} files, {size / 1e6:.1f} MB')
