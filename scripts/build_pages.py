#!/usr/bin/env python3
"""Generates the seven static pages of the redesign.

All original Greek copy is pulled verbatim from the ORIGINAL pages in git (commit ORIG),
so nothing is retyped; the few owner-approved wording changes are applied in code below.
Run from the project root:  python3 scripts/build_pages.py
"""
import os, re, subprocess

ORIG = 'd2c5358'   # last commit before the redesign (original pages + the owner's Feb 2026 title/subtitle edits). Do not change.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def orig(name):
    return subprocess.check_output(['git', 'show', f'{ORIG}:{name}.html'], text=True)


def main_of(name):
    s = orig(name)
    return s[s.index('<main'):s.index('</main>')]


def plain_paras(html):
    """<p> elements without a class, as inner HTML."""
    return [m.group(1).strip() for m in re.finditer(r'<p>(.*?)</p>', html, re.S)]


def clean(t):
    t = t.replace('</p></p>', '')
    return re.sub(r'\n\s*', ' ', t).strip()


# ---------------------------------------------------------------- images
def img(base, alt, sizes='(max-width:900px) 90vw, 480px', cls='', lazy=True, prio=False, pos=None):
    """<picture> with WebP + JPEG fallback, responsive srcset and intrinsic size."""
    from PIL import Image as _I
    d = 'assets/web'
    avail = sorted(int(m.group(1)) for f in os.listdir(d) for m in [re.fullmatch(re.escape(base) + r'-(\d+)\.jpg', f)] if m)
    jpg = ', '.join(f'{d}/{base}-{w}.jpg {w}w' for w in avail)
    mid = next((w for w in avail if w >= 1000), avail[-1])
    _w, _h = _I.open(f'{d}/{base}-{mid}.jpg').size
    attrs = f'src="{d}/{base}-{mid}.jpg" srcset="{jpg}" sizes="{sizes}" width="{_w}" height="{_h}" alt="{alt}"'
    if cls: attrs += f' class="{cls}"'
    if prio: attrs += ' fetchpriority="high"'
    elif lazy: attrs += ' loading="lazy"'
    if pos: attrs += f' style="object-position:{pos}"'
    attrs += ' decoding="async"'
    tag = f'<img {attrs}>'
    if all(os.path.exists(f'{d}/{base}-{w}.webp') for w in avail):
        webp = ', '.join(f'{d}/{base}-{w}.webp {w}w' for w in avail)
        tag = f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">{tag}</picture>'
    return tag


# ---------------------------------------------------------------- shell
NAV = [
    ('index.html', 'Αρχική'),
    ('viografiko.html', 'Βιογραφικό'),
    ('proseggisi.html', 'Η Προσέγγιση'),
    ('psychotherapeia.html', 'Ψυχοθεραπεία / Ψυχανάλυση'),
    ('epopteia.html', 'Εποπτεία'),
    ('dimosieuseis.html', 'Δημοσιεύσεις'),
    ('epikoinonia.html', 'Επικοινωνία'),
]


PRIVACY = ('politiki-aporritou.html', 'Πολιτική Απορρήτου')
SITE = 'https://www.tiliopoulou.com'   # assumed live domain (from README); change here if different
OG_IMAGE = SITE + '/assets/web/office-1-1200.jpg'

import json
def seo_head(fname, title, desc):
    url = SITE + '/' if fname == 'index.html' else f'{SITE}/{fname}'
    og_type = 'website'
    org = {
        '@type': ['ProfessionalService', 'LocalBusiness'],
        '@id': SITE + '/#practice',
        'name': 'Δρ Ηλιοπούλου Τριανταφυλλιά — Ψυχοθεραπεύτρια',
        'url': SITE + '/',
        'image': OG_IMAGE,
        'logo': SITE + '/assets/web/mark.png',
        'telephone': ['+302130475953', '+306978552358'],
        'email': 'felinahliop@gmail.com',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Ολυμπίων 10', 'addressLocality': 'Άνω Πατήσια, Αθήνα',
                    'postalCode': '11143', 'addressCountry': 'GR'},
        'areaServed': 'Αθήνα',
        'description': 'Ατομικές συνεδρίες ψυχοθεραπείας ή ψυχανάλυσης σε ενήλικες (Daseinsanalysis), δια ζώσης στην Αθήνα ή διαδικτυακά, και εποπτεία για επαγγελματίες.',
        'founder': {'@id': SITE + '/#person'},
        'knowsAbout': ['Ψυχοθεραπεία', 'Ψυχανάλυση', 'Daseinsanalysis', 'Φαινομενολογική – Υπαρξιακή Ανάλυση', 'Εποπτεία'],
    }
    person = {
        '@type': 'Person', '@id': SITE + '/#person',
        'name': 'Τριανταφυλλιά Ηλιοπούλου', 'honorificPrefix': 'Δρ.',
        'jobTitle': 'Ψυχολόγος/ Ψυχοθεραπεύτρια - Φαινομενολογικής & Υπαρξιακής Ανάλυσης',
        'image': SITE + '/assets/web/profile-800.jpg', 'url': SITE + '/viografiko.html',
        'worksFor': {'@id': SITE + '/#practice'},
    }
    graph = [org, person,
             {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Τριανταφυλλιά Ηλιοπούλου — Ψυχολόγος/ Ψυχοθεραπεύτρια', 'inLanguage': 'el'}]
    if fname != 'index.html':
        page_name = title.split(' — ')[0]
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Αρχική', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': page_name, 'item': url}]})
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1)
    t = title.replace('&amp;', '&')
    d = desc
    ROBOTS = 'noindex' if fname == '404.html' else 'index, follow, max-image-preview:large'
    return f'''  <link rel="canonical" href="{url}">
  <meta name="robots" content="{ROBOTS}">
  <meta name="author" content="Τριανταφυλλιά Ηλιοπούλου">
  <meta property="og:type" content="{og_type}">
  <meta property="og:locale" content="el_GR">
  <meta property="og:site_name" content="Τριανταφυλλιά Ηλιοπούλου — Ψυχολόγος/ Ψυχοθεραπεύτρια">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:image:alt" content="Το γραφείο: τιρκουάζ πολυθρόνες σε ξύλινο δάπεδο">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{t}">
  <meta name="twitter:description" content="{d}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <script type="application/ld+json">
{ld}
  </script>
'''


def shell(fname, title, body, desc):
    nav = '\n'.join(
        f'          <li><a href="{h}"' + (' class="nav-cta"' if h == 'epikoinonia.html' else '') + f'>{t}</a></li>'
        for h, t in NAV)
    footer_nav = '\n'.join(f'          <li><a href="{h}">{t}</a></li>' for h, t in NAV + [PRIVACY])
    return f'''<!doctype html>
<html lang="el">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#17474A">
{seo_head(fname, title, desc)}  <link rel="icon" href="assets/web/mark.png">
  <link rel="apple-touch-icon" href="assets/web/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300..700;1,300..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/styles.css">
</head>
<body>
  <a class="skip-link" href="#main">Μετάβαση στο περιεχόμενο</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="index.html">
        <img src="assets/web/mark.png" alt="Λογότυπο" width="46" height="42">
        <span class="brand-text">Δρ Ηλιοπούλου Τριανταφυλλιά</span>
      </a>
      <button id="navToggle" class="nav-toggle" aria-expanded="false" aria-controls="mainNav" aria-label="Μενού">☰</button>
      <nav class="main-nav" id="mainNav" aria-label="Primary navigation">
        <ul>
{nav}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main" tabindex="-1">
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div class="footer-brand">
          <img src="assets/web/mark-white.png" alt="" width="54" height="50">
          <div>
            <strong>Δρ Ηλιοπούλου Τριανταφυλλιά</strong>
            Ψυχολόγος/ Ψυχοθεραπεύτρια - Φαινομενολογικής &amp; Υπαρξιακής Ανάλυσης
          </div>
        </div>
        <nav aria-label="Footer navigation">
          <p class="footer-title">Πλοήγηση</p>
          <ul>
{footer_nav}
          </ul>
        </nav>
        <div>
          <p class="footer-title">Επικοινωνία</p>
          <address>
            Ολυμπίων 10, Άνω Πατήσια, Αθήνα 11143<br>
            <a href="tel:+302130475953">2130475953</a> · <a href="tel:+306978552358">6978552358</a><br>
            <a href="mailto:felinahliop@gmail.com">felinahliop@gmail.com</a><br>
            <a href="https://www.google.com/maps/search/?api=1&amp;query=%CE%9F%CE%BB%CF%85%CE%BC%CF%80%CE%AF%CF%89%CE%BD+10+%CE%86%CE%BD%CF%89+%CE%A0%CE%B1%CF%84%CE%AE%CF%83%CE%B9%CE%B1+11143" target="_blank" rel="noopener">Χάρτης</a>
          </address>
        </div>
      </div>
      <p class="copyright">© Τριανταφυλλιά Ηλιοπούλου — Όλα τα δικαιώματα διατηρούνται.</p>
    </div>
  </footer>

  <script src="js/main.js"></script>
</body>
</html>
'''


SHAPES = {'Βιογραφικό': 's-oval', 'Daseinsanalysis': 's-blob', 'Υπηρεσίες': 's-inv', 'Για επαγγελματίες': 's-tab', 'Έρευνα': 's-tabr'}


def page_hero(eyebrow, h1, subtitle, image_html, extra=''):
    sub = f'\n          <p class="subtitle">{subtitle}</p>' if subtitle else ''
    return f'''    <section class="page-hero">
      <div class="wrap split flip">
        <div class="split-text reveal">
          <span class="eyebrow">{eyebrow}</span>
          <h1>{h1}</h1>{sub}
{extra}
        </div>
        <div class="split-art reveal">
          <div class="arch-wrap {SHAPES.get(eyebrow, "")}"><div class="arch">{image_html}</div></div>
        </div>
      </div>
    </section>'''


# ---------------------------------------------------------------- session dials / formats / stats
def banner(rows):
    """Side banner: list of (label, value). Value may be empty."""
    items = '\n'.join(f'<li><span>{l}</span>' + (f'<strong>{v}</strong>' if v else '') + '</li>' for l, v in rows)
    return f'<div class="banner reveal"><ul>\n{items}\n</ul></div>'


_BAND = iter(['b-pill', 'b-leaf', 'b-arch', 'b-tab', 'b-ticket'])


def photo_band(html):
    return f'''    <section class="photo-band">
      <div class="wrap"><div class="wide reveal {next(_BAND)}">{html}</div></div>
    </section>'''


def write(fname, html):
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote', fname)


NAME = 'Δρ Ηλιοπούλου Τριανταφυλλιά'
SUBTITLE = 'Ψυχολόγος/ Ψυχοθεραπεύτρια - Φαινομενολογικής &amp; Υπαρξιακής Ανάλυσης'   # owner's wording (Feb 2026 edit)

# ================================================================ INDEX
idx = main_of('index')
intro = [clean(p).replace('βάση του Κώδικα', 'βάσει του Κώδικα') for p in plain_paras(idx.split('class="col text"')[1].split('</div>')[0])]
cards = re.findall(r'<article class="card">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', idx, re.S)
card = {h: p for h, p in cards}
psy_sentence = plain_paras(main_of('psychotherapeia'))[1 - 1].split('. ')[0] + '.'  # first sentence, verbatim

ICON_EYE = '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M3 24C9 14 16 9 24 9s15 5 21 15c-6 10-13 15-21 15S9 34 3 24Z"/><circle cx="24" cy="24" r="6.5"/></svg>'
ICON_TALK = '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 11h23a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H15l-7 6v-6H5a3 3 0 0 1-3-3V14a3 3 0 0 1 3-3Z"/><path d="M36 20h7a3 3 0 0 1 3 3v11a3 3 0 0 1-3 3h-1v6l-7-6H24"/></svg>'
ICON_PATH = '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="10" cy="36" r="4"/><circle cx="24" cy="14" r="4"/><circle cx="38" cy="30" r="4"/><path d="M13 33l8-15M28 16l8 11"/></svg>'

gallery = [
    ('office-4', 'Γραφείο και σκάλα, άποψη από ψηλά'),
    ('office-5', 'Αντίκα γραφείο με ανοιχτό βιβλίο'),
    ('office-7', 'Παλιό μπαούλο και πίνακας στον τοίχο'),
    ('office-9', 'Ο καναπές της ψυχανάλυσης και η βιβλιοθήκη'),
    ('office-11', 'Λεπτομέρεια τοίχου'),
    ('office-8', 'Πίνακας πάνω από καναπέ'),
    ('office-12', 'Δύο καρέκλες και λάμπα'),
    ('office-14', 'Πίνακας και βιβλιοθήκη'),
]
gal_html = '\n'.join(
    f'        <button class="gallery-item reveal" type="button" data-index="{i}" aria-label="Μεγέθυνση: {alt}">'
    f'{img(b, alt, sizes="(max-width:640px) 46vw, (max-width:1000px) 30vw, 280px")}<span class="caption">{alt}</span></button>'
    for i, (b, alt) in enumerate(gallery))

index_body = f'''    <section class="hero">
      <div class="wrap hero-grid">
        <div class="panel">
          <h1>{NAME}</h1>
          <p class="subtitle">{SUBTITLE}</p>
          <blockquote>“Full of merit, yet poetically, man Dwells on this earth” - Heidegger</blockquote>
          <a class="btn btn-mist" href="epikoinonia.html">Επικοινωνία</a>
        </div>
        <div class="hero-art">
          <div class="arch-wrap">
            <div class="arch">{img('office-1', 'Το γραφείο: τιρκουάζ πολυθρόνες σε ξύλινο δάπεδο', sizes='(max-width:900px) 80vw, 440px', lazy=False, prio=True, pos='72% 50%')}</div>
            <div class="hero-thumb">{img('office-12', 'Δύο καρέκλες και λάμπα', sizes='160px', lazy=False)}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section tint">
      <div class="wrap split">
        <div class="split-art reveal">
          <div class="arch-wrap s-leaf"><div class="arch">{img('profile', 'Προφίλ — Τριανταφυλλιά Ηλιοπούλου', sizes='(max-width:860px) 80vw, 420px', pos='42% 40%')}</div></div>
        </div>
        <div class="split-text reveal">
          <span class="eyebrow">Βιογραφικό</span>
          <p class="lead">{intro[0]}</p>
          <p>{intro[1]}</p>
          <a class="textlink" href="viografiko.html">Περισσότερα →</a>
        </div>
      </div>
    </section>

    <section class="band" aria-label="Υπηρεσίες">
      <div class="wrap services">
        <article class="service reveal">
          {ICON_EYE}
          <h3>Η Προσέγγιση</h3>
          <p>{card['Η Προσέγγιση']}</p>
          <a class="textlink" href="proseggisi.html">Περισσότερα →</a>
        </article>
        <article class="service reveal">
          {ICON_TALK}
          <h3>Ψυχοθεραπεία</h3>
          <p>{psy_sentence}</p>
          <a class="textlink" href="psychotherapeia.html">Περισσότερα →</a>
        </article>
        <article class="service reveal">
          {ICON_PATH}
          <h3>Εποπτεία</h3>
          <p>{card['Εποπτεία']}</p>
          <a class="textlink" href="epopteia.html">Περισσότερα →</a>
        </article>
      </div>
    </section>

    <section class="section warm">
      <div class="wrap">
        <div class="section-head reveal">
          <div class="divider"><img src="assets/web/mark-mauve.png" alt="" width="38" height="35"></div>
          <h2>Ο χώρος</h2>
        </div>
        <div class="gallery-grid">
{gal_html}
        </div>
      </div>
    </section>

    <section class="closing" style="background-image:url('assets/web/home-hero-1200.jpg')">
      <div class="wrap reveal">
        <img class="mark" src="assets/web/mark-white.png" alt="" width="44" height="40">
        <h2>Για ραντεβού ή πληροφορίες</h2>
        <a class="btn btn-mist" href="epikoinonia.html">Επικοινωνία</a>
      </div>
    </section>'''
write('index.html', shell('index.html', 'Ψυχολόγος/ Ψυχοθεραπεύτρια στην Αθήνα — Δρ Ηλιοπούλου Τριανταφυλλιά', index_body,
      'Δρ Ηλιοπούλου Τριανταφυλλιά, ψυχολόγος/ ψυχοθεραπεύτρια: ατομικές συνεδρίες ψυχοθεραπείας και ψυχανάλυσης (Daseinsanalysis) για ενήλικες στα Άνω Πατήσια της Αθήνας ή διαδικτυακά, και εποπτεία επαγγελματιών.'))

# ================================================================ VIOGRAFIKO
bio = [clean(p) for p in plain_paras(main_of('viografiko').split('<section class="page-bottom')[0]) if 'class' not in p]
bio_body = page_hero('Βιογραφικό', NAME, SUBTITLE, img('profile', 'Προφίλ — Τριανταφυλλιά Ηλιοπούλου', sizes='380px', lazy=False, pos='42% 40%')) + f'''

    <section class="prose-wrap">
      <div class="wrap">
        <div class="prose reveal">
          <p class="lead">{bio[0]}</p>
          {chr(10).join(f"<p>{p}</p>" for p in bio[1:])}
        </div>
      </div>
    </section>

''' + photo_band(img('office-5', 'Αντίκα γραφείο με ανοιχτό βιβλίο', sizes='1100px', pos='50% 55%'))
write('viografiko.html', shell('viografiko.html', 'Βιογραφικό — Δρ Ηλιοπούλου Τριανταφυλλιά, Ψυχολόγος/ Ψυχοθεραπεύτρια', bio_body, 'Σπουδές (BSc, MSc, PhD), έρευνα, διδασκαλία και κλινική εμπειρία της Δρ. Τριανταφυλλιάς Ηλιοπούλου, ψυχοθεραπεύτριας με πενταετή εκπαίδευση στη Daseinsanalysis.'))

# ================================================================ PROSEGGISI
prs_main = main_of('proseggisi')
prs_sub = re.search(r'<p class="subtitle">(.*?)</p>', prs_main).group(1)
prs = [clean(p).replace('της ίδια της', 'της ίδιας της') for p in plain_paras(prs_main) if 'class' not in p]
prs_body = page_hero('Daseinsanalysis', 'Η Προσέγγιση', prs_sub, img('office-6', 'Αντίκα γραφείο με ανοιχτό βιβλίο', sizes='380px', lazy=False, pos='40% 50%')) + f'''

    <section class="prose-wrap">
      <div class="wrap">
        <div class="prose reveal">
          <p class="lead">{prs[0]}</p>
          <p>{prs[1]}</p>
        </div>
      </div>
    </section>

''' + photo_band(img('office-10', 'Τιρκουάζ πολυθρόνες και παραβάν', sizes='1100px', pos='50% 60%'))
write('proseggisi.html', shell('proseggisi.html', 'Η Προσέγγιση — Daseinsanalysis, Φαινομενολογική Ψυχοθεραπεία', prs_body, 'Η Φαινομενολογική – Υπαρξιακή Ανάλυση &amp; Ψυχοθεραπεία (Daseinsanalysis): μια προσέγγιση που στηρίζεται στη συνομιλία, τον αναστοχασμό και την ερμηνευτική φαινομενολογία.'))

# ================================================================ PSYCHOTHERAPEIA
psy_main = main_of('psychotherapeia')
psy_sub = re.search(r'<p class="subtitle">(.*?)</p>', psy_main).group(1)
pp = [clean(p) for p in plain_paras(psy_main) if 'class' not in p]
pp = [x.replace('μέσω Skype', 'μέσω online πλατφόρμας').replace('διαρκούν 60 λεπτά', 'διαρκούν 90 λεπτά') for x in pp]  # updated per owner
items = re.findall(r'<li>(.*?)</li>', psy_main)
psy_body = page_hero('Υπηρεσίες', 'Ψυχοθεραπεία / Ψυχανάλυση', psy_sub, img('office-9', 'Ο καναπές της ψυχανάλυσης και η βιβλιοθήκη', sizes='380px', lazy=False, pos='50% 60%')) + f'''

    <section class="prose-wrap">
      <div class="wrap">
        <div class="layout-2">
          <div class="prose reveal">
            <p class="lead">{pp[0]}</p>
            <p>{pp[1]}</p>
            <p>{pp[2]}</p>
          </div>
          <div class="side-stack">
          {banner([("Ψυχοθεραπεία", "45 λεπτά"), ("Ψυχανάλυση", "90 λεπτά"), ("Δια ζώσης και διαδικτυακά", "μέσω online πλατφόρμας")])}
          <aside class="pull reveal">
            <h3>Ενδεικτικά αιτήματα</h3>
            <ul class="checklist">
              {chr(10).join(f"<li>{i}</li>" for i in items)}
            </ul>
          </aside>
          </div>
        </div>
      </div>
    </section>

''' + photo_band(img('office-4', 'Γραφείο και σκάλα, άποψη από ψηλά', sizes='1100px', pos='50% 40%'))
write('psychotherapeia.html', shell('psychotherapeia.html', 'Ψυχοθεραπεία / Ψυχανάλυση στην Αθήνα — Δρ Ηλιοπούλου Τριανταφυλλιά', psy_body, 'Ατομικές συνεδρίες ψυχοθεραπείας (45 λεπτά) ή ψυχανάλυσης (90 λεπτά) για ενήλικες, δια ζώσης στα Άνω Πατήσια ή διαδικτυακά. Άγχος, κατάθλιψη, πένθος, σχέσεις.'))

# ================================================================ EPOPTEIA
ep = [clean(p).replace('μέσω Skype', 'μέσω online πλατφόρμας').replace('διάρκεια 1 ώρας', 'διάρκεια 60 λεπτών').replace('διάρκεια 1,5 ώρα', 'διάρκεια 90 λεπτών').replace('το πως να', 'το πώς να') for p in plain_paras(main_of('epopteia')) if 'class' not in p]
ep_body = page_hero('Για επαγγελματίες', 'Εποπτεία', '', img('office-12', 'Δύο καρέκλες και λάμπα', sizes='380px', lazy=False)) + f'''

    <section class="prose-wrap">
      <div class="wrap">
        <div class="layout-2">
          <div class="prose reveal">
            <p class="lead">{ep[0]}</p>
            <p>{ep[1]}</p>
          </div>
          {banner([("Ατομικά", "60 λεπτά"), ("Ομαδικά (3-4 άτομα)", "90 λεπτά, εβδομαδιαίως"), ("Δια ζώσης και διαδικτυακά", "μέσω online πλατφόρμας")])}
        </div>
      </div>
    </section>

''' + photo_band(img('office-7', 'Παλιό μπαούλο και πίνακας στον τοίχο', sizes='1100px', pos='50% 30%'))
write('epopteia.html', shell('epopteia.html', 'Εποπτεία για Ψυχοθεραπευτές — Δρ Ηλιοπούλου Τριανταφυλλιά', ep_body, 'Ατομική και ομαδική εποπτεία για επαγγελματίες ψυχοθεραπείας και ψυχανάλυσης, δια ζώσης ή διαδικτυακά, με στόχο τον αναστοχασμό και την επαγγελματική ανάπτυξη.'))

# ================================================================ DIMOSIEUSEIS
dm_main = main_of('dimosieuseis')
lis = re.findall(r'<li><strong>(.*?)</strong><br>(.*?)</li>', dm_main, re.S)
dm_intro = [clean(p) for p in plain_paras(dm_main)]
pubs = [(y, t) for y, t in lis if re.fullmatch(r'\d{4}', y)]
projs = [(y, t) for y, t in lis if not re.fullmatch(r'\d{4}', y)]


def pub_list(rows):
    return '<ul class="pubs">\n' + '\n'.join(
        f'          <li class="pub"><span class="pub-year">{y}</span><p>{clean(t)}</p></li>' for y, t in rows) + '\n        </ul>'


dm_body = page_hero('Έρευνα', 'Δημοσιεύσεις', '', img('office-4', 'Γραφείο και σκάλα, άποψη από ψηλά', sizes='380px', lazy=False, pos='50% 40%')) + f'''

    <section class="prose-wrap">
      <div class="wrap">
        <div class="reveal">
          <p class="lead">{dm_intro[0]}</p>
          {pub_list(pubs)}
          <h2 class="pubs-title">{dm_intro[1].replace('<strong>', '').replace('</strong>', '')}</h2>
          {pub_list(projs)}
        </div>
      </div>
    </section>

''' + photo_band(img('office-11', 'Λεπτομέρεια τοίχου', sizes='1100px', pos='50% 35%'))
write('dimosieuseis.html', shell('dimosieuseis.html', 'Δημοσιεύσεις και Έρευνα — Δρ Ηλιοπούλου Τριανταφυλλιά', dm_body, 'Επιλεγμένες επιστημονικές δημοσιεύσεις και συμμετοχή σε ερευνητικά προγράμματα της Δρ. Τριανταφυλλιάς Ηλιοπούλου (2018–2022).'))

# ================================================================ EPIKOINONIA
MAPQ = '%CE%9F%CE%BB%CF%85%CE%BC%CF%80%CE%AF%CF%89%CE%BD+10+%CE%86%CE%BD%CF%89+%CE%A0%CE%B1%CF%84%CE%AE%CF%83%CE%B9%CE%B1+11143'
ct_body = f"""    <section class="contact-head">
      <div class="wrap">
        <span class="eyebrow">Ραντεβού</span>
        <h1>Επικοινωνία</h1>
        <p class="lead">Για ραντεβού ή πληροφορίες</p>
      </div>
    </section>

    <section class="contact-actions">
      <div class="wrap actions">
        <div class="action reveal">
          <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M12 6h8l4 11-5 3a24 24 0 0 0 9 9l3-5 11 4v8a4 4 0 0 1-4 4C21 40 8 27 8 10a4 4 0 0 1 4-4Z"/></svg>
          <span class="eyebrow">Τηλέφωνα</span>
          <a class="big-link" href="tel:+302130475953">2130475953</a>
          <a class="big-link" href="tel:+306978552358">6978552358</a>
        </div>
        <div class="action reveal">
          <svg viewBox="0 0 48 48" aria-hidden="true"><rect x="5" y="10" width="38" height="28" rx="4"/><path d="m6 13 18 14 18-14"/></svg>
          <span class="eyebrow">Email</span>
          <a class="big-link small" href="mailto:felinahliop@gmail.com">felinahliop@gmail.com</a>
          <a class="chip" href="mailto:felinahliop@gmail.com">Αποστολή email</a>
        </div>
        <div class="action reveal">
          <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 43S9 30 9 19a15 15 0 0 1 30 0c0 11-15 24-15 24Z"/><circle cx="24" cy="19" r="5"/></svg>
          <span class="eyebrow">Διεύθυνση</span>
          <address class="big-link plain">Ολυμπίων 10, Άνω Πατήσια<br>Αθήνα 11143</address>
          <a class="chip" href="https://www.google.com/maps/search/?api=1&amp;query={MAPQ}" target="_blank" rel="noopener">Οδηγίες</a>
        </div>
      </div>
    </section>

    <section class="prose-wrap">
      <div class="wrap contact-grid">
        <div class="form-card reveal">
          <h2>Στείλτε μήνυμα</h2>
          <form id="contactForm" action="https://formspree.io/f/mbdjkeja" method="post">
            <input type="hidden" name="_subject" value="Νέο μήνυμα από την ιστοσελίδα">
            <input type="hidden" id="_gotcha" name="_gotcha">
            <div class="form-row">
              <div><label for="fname">Όνομα *</label><input id="fname" name="fname" required aria-required="true" autocomplete="given-name"></div>
              <div><label for="lname">Επώνυμο</label><input id="lname" name="lname" autocomplete="family-name"></div>
            </div>
            <label for="email">Email *</label>
            <input id="email" name="email" type="email" required aria-required="true" autocomplete="email">
            <label for="message">Μήνυμα</label>
            <textarea id="message" name="message" rows="6"></textarea>
            <p class="form-note">Τα στοιχεία σας χρησιμοποιούνται μόνο για να απαντήσουμε στο μήνυμά σας. Παρακαλούμε μην αναφέρετε ευαίσθητα προσωπικά δεδομένα υγείας. <a href="politiki-aporritou.html">Πολιτική Απορρήτου</a></p>
            <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
            <button type="submit" class="btn btn-petrol">Αποστολή</button>
          </form>
        </div>
        <div class="side-stack">
          {banner([("Ψυχοθεραπεία", "45 λεπτά"), ("Ψυχανάλυση", "90 λεπτά"), ("Δια ζώσης και διαδικτυακά", "μέσω online πλατφόρμας")])}
          <div class="map-box reveal" id="mapBox">
            <iframe src="https://www.google.com/maps?q={MAPQ}&amp;output=embed" title="Χάρτης: Ολυμπίων 10, Άνω Πατήσια, Αθήνα" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
          </div>
        </div>
      </div>
    </section>"""
write('epikoinonia.html', shell('epikoinonia.html', 'Επικοινωνία — Ραντεβού Ψυχοθεραπείας, Άνω Πατήσια Αθήνα', ct_body, 'Ολυμπίων 10, Άνω Πατήσια, Αθήνα 11143. Τηλέφωνα 2130475953 και 6978552358, email και φόρμα επικοινωνίας για ραντεβού ψυχοθεραπείας ή πληροφορίες.'))


# ================================================================ PRIVACY
MONTHS = ['Ιανουάριος', 'Φεβρουάριος', 'Μάρτιος', 'Απρίλιος', 'Μάιος', 'Ιούνιος', 'Ιούλιος', 'Αύγουστος', 'Σεπτέμβριος', 'Οκτώβριος', 'Νοέμβριος', 'Δεκέμβριος']
import datetime as _dt
_t = _dt.date.today()
privacy_body = f"""    <!-- DRAFT privacy notice: to be reviewed and approved by the practice owner (and a legal adviser if possible) before publishing. -->
    <section class="contact-head">
      <div class="wrap">
        <span class="eyebrow">Νομικά</span>
        <h1>Πολιτική Απορρήτου</h1>
        <p class="lead">Πώς χρησιμοποιούνται τα στοιχεία σας όταν επικοινωνείτε μέσω αυτού του ιστότοπου.</p>
      </div>
    </section>

    <section class="prose-wrap">
      <div class="wrap">
        <div class="prose">
          <h2>Υπεύθυνη επεξεργασίας</h2>
          <p>Τριανταφυλλιά Ηλιοπούλου, Ψυχοθεραπεύτρια · Ολυμπίων 10, Άνω Πατήσια, Αθήνα 11143 · <a href="mailto:felinahliop@gmail.com">felinahliop@gmail.com</a> · <a href="tel:+302130475953">2130475953</a>.</p>

          <h2>Ποια στοιχεία συλλέγονται και γιατί</h2>
          <p>Όταν στέλνετε μήνυμα από τη φόρμα επικοινωνίας, συλλέγονται το όνομά σας, το επώνυμό σας (προαιρετικά), η διεύθυνση email σας και το περιεχόμενο του μηνύματος. Χρησιμοποιούνται αποκλειστικά για να απαντήσουμε στο αίτημά σας, να κανονίσουμε ραντεβού ή να σας δώσουμε πληροφορίες. Δεν χρησιμοποιούνται για διαφήμιση ή προώθηση και δεν πωλούνται ούτε διατίθενται σε τρίτους.</p>
          <p>Νομική βάση της επεξεργασίας είναι η συγκατάθεσή σας (άρθρο 6 παρ. 1 α΄ του Γενικού Κανονισμού Προστασίας Δεδομένων – ΓΚΠΔ), την οποία παρέχετε στέλνοντας το μήνυμα, και, όταν το αίτημά σας αφορά τη σύναψη συνεργασίας, η λήψη μέτρων κατόπιν αιτήματός σας (άρθρο 6 παρ. 1 β΄).</p>
          <p>Παρακαλούμε να μην αναφέρετε στο μήνυμα ευαίσθητα δεδομένα υγείας ή λεπτομέρειες του προβλήματός σας. Αυτά μπορούν να συζητηθούν με ασφάλεια στη συνεδρία.</p>

          <h2>Πώς αποστέλλεται η φόρμα</h2>
          <p>Το μήνυμα διαβιβάζεται μέσω της υπηρεσίας Formspree (Formspree, Inc., ΗΠΑ), η οποία το προωθεί στο email μας και ενεργεί ως εκτελούσα την επεξεργασία. Η διαβίβαση προς χώρα εκτός Ευρωπαϊκού Οικονομικού Χώρου γίνεται με τις εγγυήσεις που προβλέπει ο ΓΚΠΔ. Περισσότερα στην <a href="https://formspree.io/legal/privacy-policy/" target="_blank" rel="noopener">πολιτική απορρήτου της Formspree</a>.</p>

          <h2>Υπηρεσίες Google</h2>
          <p>Ο ιστότοπος φορτώνει γραμματοσειρές από το Google Fonts και ενσωματωμένο χάρτη Google Maps στη σελίδα «Επικοινωνία». Κατά τη φόρτωσή τους η Google μπορεί να λαμβάνει τη διεύθυνση IP και τεχνικά στοιχεία της συσκευής σας και να τοποθετεί cookies. Δείτε την <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">πολιτική απορρήτου της Google</a>.</p>

          <h2>Cookies</h2>
          <p>Ο ιστότοπος δεν χρησιμοποιεί cookies για στατιστικά, παρακολούθηση ή διαφήμιση. Τα μόνα cookies που ενδέχεται να οριστούν προέρχονται από τον ενσωματωμένο χάρτη της Google.</p>

          <h2>Διατήρηση</h2>
          <p>Τα μηνύματα διατηρούνται μόνο για όσο χρόνο χρειάζεται για την εξυπηρέτηση του αιτήματός σας και στη συνέχεια διαγράφονται, εκτός αν υπάρχει νομική υποχρέωση διατήρησης.</p>

          <h2>Τα δικαιώματά σας</h2>
          <p>Έχετε δικαίωμα πρόσβασης, διόρθωσης, διαγραφής, περιορισμού της επεξεργασίας, φορητότητας και εναντίωσης, καθώς και δικαίωμα να ανακαλέσετε τη συγκατάθεσή σας οποιαδήποτε στιγμή. Για να τα ασκήσετε, επικοινωνήστε μαζί μας στο <a href="mailto:felinahliop@gmail.com">felinahliop@gmail.com</a>. Έχετε επίσης δικαίωμα καταγγελίας στην <a href="https://www.dpa.gr" target="_blank" rel="noopener">Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα</a>.</p>

          <h2>Εμπιστευτικότητα</h2>
          <p>Το θεραπευτικό πλαίσιο διέπεται από ασφάλεια, σεβασμό και εχεμύθεια και τηρείται το απόρρητο βάσει του Κώδικα Δεοντολογίας.</p>

          <p><small>Τελευταία ενημέρωση: {MONTHS[_t.month - 1]} {_t.year}</small></p>
        </div>
      </div>
    </section>"""
write('politiki-aporritou.html', shell('politiki-aporritou.html', 'Πολιτική Απορρήτου — Δρ Ηλιοπούλου Τριανταφυλλιά', privacy_body, 'Πώς χρησιμοποιούνται τα στοιχεία που στέλνετε μέσω της φόρμας επικοινωνίας και ποια είναι τα δικαιώματά σας.'))

# ================================================================ 404
nf_body = """    <section class="contact-head">
      <div class="wrap">
        <span class="eyebrow">404</span>
        <h1>Η σελίδα δεν βρέθηκε</h1>
        <p class="lead">Η σελίδα που ψάχνετε δεν υπάρχει ή έχει μετακινηθεί.</p>
        <p style="margin-top:1.6rem"><a class="btn btn-petrol" href="index.html">Επιστροφή στην αρχική</a></p>
      </div>
    </section>
    <div style="height:clamp(48px,10vw,140px)"></div>"""
nf = shell('404.html', 'Η σελίδα δεν βρέθηκε — Δρ Ηλιοπούλου Τριανταφυλλιά', nf_body, 'Η σελίδα δεν βρέθηκε.')
# the 404 page is served from any URL depth, so make local links root-relative
nf = re.sub(r'((?:href|src)=")(?!https?:|mailto:|tel:|#|/)', r'\1/', nf)
write('404.html', nf)


# ================================================================ SITEMAP / ROBOTS
import datetime
today = datetime.date.today().isoformat()
urls = [(SITE + '/', '1.0')] + [(f'{SITE}/{h}', '0.8') for h, _ in NAV[1:]] + [(f'{SITE}/{PRIVACY[0]}', '0.3')]
with open('sitemap.xml', 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u, pr in urls:
        f.write(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>\n')
    f.write('</urlset>\n')
with open('robots.txt', 'w', encoding='utf-8') as f:
    f.write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
print('wrote sitemap.xml, robots.txt')
