#!/usr/bin/env python3
"""Create web-sized images in assets/web/ from the originals in assets/ (originals are never touched).

Run from the project root:  python3 scripts/optimize_images.py
Needs Pillow:  python3 -m pip install pillow
Produces, for every photo: JPEG (600/1200/2000 px wide) + WebP twins, plus the logo variants,
the portrait and the home-screen icon.
"""
import os
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None

SRC, OUT = 'assets', 'assets/web'
os.makedirs(OUT, exist_ok=True)
PHOTOS = ['contact.jpg', 'home-hero.jpg', 'office-1.jpg', 'office-4.jpg', 'office-5.jpg', 'office-6.jpg',
          'office-7.jpg', 'office-8.jpg', 'office-9.jpg', 'office-10.jpg', 'office-11.jpg', 'office-12.jpg', 'office-14.jpg']


def save(im, base, w):
    h = round(im.height * w / im.width)
    r = im.resize((w, h), Image.LANCZOS)
    r.save(f'{OUT}/{base}-{w}.jpg', quality=78, optimize=True, progressive=True)
    r.save(f'{OUT}/{base}-{w}.webp', quality=76, method=6)


for n in PHOTOS:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, n))).convert('RGB')
    base = os.path.splitext(n)[0]
    for w in (600, 1200, 2000):
        if im.width >= w:
            save(im, base, w)

# portrait (800 px original)
pr = ImageOps.exif_transpose(Image.open(f'{SRC}/profile.jpeg')).convert('RGB')
for w in (600, 800):
    save(pr, 'profile', w)

# logo: white background -> transparent, then recoloured variants
lg = Image.open(f'{SRC}/newlogo.png').convert('RGBA')
px = lg.load()
for y in range(lg.height):
    for x in range(lg.width):
        r, g, b, a = px[x, y]
        m = min(r, g, b)
        if m > 235:
            px[x, y] = (r, g, b, 0)
        elif m > 200:
            px[x, y] = (r, g, b, int(255 * (235 - m) / 35))
lg = lg.crop(lg.getbbox()); lg.thumbnail((320, 320))
lg.save(f'{OUT}/mark.png', optimize=True)
for name, col in (('mark-mauve', (176, 58, 120)), ('mark-white', (255, 255, 255))):
    o = Image.new('RGBA', lg.size)
    sp, op = lg.load(), o.load()
    for y in range(lg.height):
        for x in range(lg.width):
            op[x, y] = col + (sp[x, y][3],)
    o.save(f'{OUT}/{name}.png', optimize=True)

# home-screen icon: blossom on cream
icon = Image.new('RGB', (180, 180), (247, 245, 241))
m = lg.copy(); m.thumbnail((124, 124))
icon.paste(m, ((180 - m.width) // 2, (180 - m.height) // 2), m)
icon.save(f'{OUT}/apple-touch-icon.png', optimize=True)
# social-sharing images (1200x630), one per page
OG = {'index': 'office-1', 'viografiko': 'office-5', 'proseggisi': 'office-10', 'psychotherapeia': 'office-9',
      'epopteia': 'office-12', 'dimosieuseis': 'office-4', 'epikoinonia': 'contact', 'politiki-aporritou': 'office-1'}
for page, src in OG.items():
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, src + '.jpg'))).convert('RGB')
    im = ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.5))
    im.save(f'{OUT}/og-{page}.jpg', quality=80, optimize=True, progressive=True)
print('done')
