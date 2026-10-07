"""LUMARC end-card CTA, reusable at the end of every reel.
lumarc_cta(frame, lt) -> frame   (frame: RGBA 1080x1920 PIL image, lt: seconds since the CTA started)
Shows over ~2.6s: the last shot darkens/blurs, then the hook line, the LUMARC wordmark,
the tagline and a "DM us" button appear.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FB = '/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf'
ORANGE = (255, 140, 30)

def _clamp(x): return max(0., min(1., x))
def _eout(x): x = _clamp(x); return 1 - (1 - x) ** 3
def _eback(x):
    x = _clamp(x); c1 = 1.7; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def _spaced(text, size, fill, spacing):
    f = ImageFont.truetype(FB, size)
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    widths = [d0.textbbox((0, 0), ch, font=f)[2] for ch in text]
    w = sum(widths) + spacing * (len(text) - 1)
    im = Image.new('RGBA', (w + 80, int(size * 1.4) + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 40
    for ch, cw in zip(text, widths):
        d.text((x, 40), ch, font=f, fill=fill); x += cw + spacing
    return im

def _glow(im, color, radius, k):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(radius))
    g = Image.new('RGBA', im.size, color + (0,)); g.putalpha(a.point(lambda v: min(255, int(v * k))))
    return Image.alpha_composite(g, im)

def _button(text, size):
    f = ImageFont.truetype(FB, size)
    d0 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    b = d0.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0] + 96, b[3] - b[1] + 56
    im = Image.new('RGBA', (w + 60, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((30, 30, 30 + w, 30 + h), h // 2, fill=ORANGE)
    d.text((30 + 48 - b[0], 30 + 28 - b[1]), text, font=f, fill=(15, 10, 5))
    return _glow(im, ORANGE, 18, .9)

HOOK = _spaced('WANT YOUR PRODUCT', 44, (235, 235, 235), 4)
HOOK2 = _spaced('TO LOOK LIKE THIS?', 44, (235, 235, 235), 4)
MARK = _glow(_spaced('LUMARC', 150, (255, 255, 255), 24), (255, 150, 60), 26, .55)
TAG = _spaced('PRODUCT VIDEOS THAT STOP THE SCROLL', 30, (170, 170, 170), 5)
BTN = _button('DM us "VIDEO"', 46)

def _put(frame, spr, cx, cy, alpha=1., scale=1.):
    if alpha <= .01: return
    s = spr
    if abs(scale - 1) > .003: s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BICUBIC)
    if alpha < .999:
        s = s.copy(); s.putalpha(s.split()[3].point(lambda v: int(v * alpha)))
    frame.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

_BG = None
def _bg():
    global _BG
    if _BG is None:
        bg = Image.new('RGBA', (W, H), (10, 9, 9, 255))
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((W / 2 - 520, 980 - 520, W / 2 + 520, 980 + 520), fill=ORANGE + (60,))
        _BG = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(160)))
    return _BG

def lumarc_cta(frame, lt):
    k = _eout(lt / .45)
    if k < 1:  # previous shot blurs and darkens into the card
        prev = frame.filter(ImageFilter.GaussianBlur(18 * k))
        frame = Image.blend(prev, _bg(), k)
    else:
        frame = _bg().copy()
    _put(frame, HOOK, W / 2, 720, _eout((lt - .25) / .35), .94 + .06 * _eout((lt - .25) / .4))
    _put(frame, HOOK2, W / 2, 790, _eout((lt - .35) / .35), .94 + .06 * _eout((lt - .35) / .4))
    _put(frame, MARK, W / 2, 965, _eout((lt - .55) / .3), .8 + .2 * _eback((lt - .55) / .45))
    lw = int(300 * _eout((lt - .8) / .4))
    if lw > 2:
        ImageDraw.Draw(frame).rectangle((W / 2 - lw, 1078, W / 2 + lw, 1082), fill=ORANGE + (255,))
    _put(frame, TAG, W / 2, 1140, _eout((lt - .95) / .35))
    pulse = 1 + .035 * max(0., __import__('math').sin((lt - 1.6) * 6)) if lt > 1.6 else 1
    _put(frame, BTN, W / 2, 1330, _eout((lt - 1.15) / .3), (.85 + .15 * _eback((lt - 1.15) / .4)) * pulse)
    return frame
