# Δρ Ηλιοπούλου Τριανταφυλλιά — website

A static website (plain HTML, CSS, JS). No framework, no build tools beyond two small Python scripts.

## Folder map

| Path | What it is |
|---|---|
| `*.html` | The pages. **Generated** by `scripts/build_pages.py` — don't edit by hand, edit the script. |
| `css/styles.css` | All styling. Colours, fonts and spacing are variables at the top (`:root`). |
| `js/main.js` | Menu, scroll effects, photo viewer, contact form. |
| `assets/` | Original photos (huge — **never upload these**). |
| `assets/web/` | Web-sized images made by `scripts/optimize_images.py`. |
| `scripts/` | The build tools. |
| `dist/` | The clean folder to upload (created by `build_dist.py`; ignored by git). |

## Rebuild after a change

Needs Python 3 and Pillow (`python3 -m pip install pillow`). From this folder:

```bash
python3 scripts/optimize_images.py   # only when photos change
python3 scripts/build_pages.py       # regenerates every page + sitemap.xml + robots.txt
python3 scripts/build_dist.py        # copies only what's needed into dist/
```

Preview locally: `python3 -m http.server 8000` and open http://localhost:8000

**Publishing:** upload the *contents of `dist/`* — nothing else.

## Where things are set

- **Greek text:** the original copy is read from git commit `d2c5358` (the last pre-redesign commit, including the Feb 2026 title/subtitle edits) by `build_pages.py`; the few approved wording changes (online platform, 90 minutes, typo fixes, ψυχανάλυση) are applied in that script. New text (banners, privacy page, headings) is written in the script too.
- **Live domain** (canonical links, sitemap, social preview): `SITE` near the top of `scripts/build_pages.py`. Currently assumed to be `https://www.tiliopoulou.com`.
- **Fonts:** Roboto, set in `:root` of `css/styles.css` (`--serif`, `--sans`) and in the Google Fonts link inside `shell()` in `build_pages.py`.
- **Colours:** `:root` of `css/styles.css`.
- **Contact form:** posts to Formspree (`action` URL in `build_pages.py`).
- **Privacy page:** `politiki-aporritou.html` — a *draft* that the practice owner should review before publishing.

## Before going live

1. Confirm the domain in `SITE`, rebuild.
2. Review the privacy notice text.
3. Check the pages on a real phone (including the uppercase Greek labels on iPhone).
4. Upload `dist/`.
