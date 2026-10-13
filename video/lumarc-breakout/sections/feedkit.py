"""feedkit — the full-screen, dark-mode, Instagram-style feed the film opens in (owned by the integrator; sections import
it, never edit it — wrap/extend inside your own file if you need a variant).

The viewer must believe for ~1 s that they are looking at their own feed. Generic app chrome only (no official logos or
wordmarks), fictional handles. Everything is in SCREEN pixels (1080x1920); the feed scrolls under fixed chrome.

    import sections.feedkit as FK
    img = FK.screen(scroll, special=media_rgb, t=t)     # RGBA 1080x1920: chrome + posts at `scroll`
    FK.media_rect(i, scroll)                            # (x, y, w, h) of post i's media on screen
    FK.center_scroll(i)                                 # scroll value that centres post i's media on screen
    FK.SPECIAL                                          # index of the @lumarc_studio Reel post (his world goes in it)
    FK.special_media(ctx, cam=None)                     # his studio world (avatar included) cropped to the 4:5 media box

`scroll` is in content pixels (0 = top of the stories row sits right under the top bar). Posts are cached cards, so a
frame costs only a few pastes. `special` is any RGB image; it is cover-fitted into the 1080x1350 media box.
"""
import math, os, zlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

W, H = E.W, E.H
BG = (0, 0, 0)                     # IG dark mode is pure black
FG = (245, 245, 245)
SUB = (168, 168, 168)
LINE = (38, 38, 38)
STATUS_H, TOP_H, NAV_H = 70, 120, 150
TOP_Y = STATUS_H + TOP_H           # 190: feed content starts here at scroll 0
NAV_Y = H - NAV_H                  # 1770
STORIES_H = 250
HEAD_H, MEDIA_H, ACT_H, META_H, GAP = 118, 1350, 104, 150, 24
CARD_H = HEAD_H + MEDIA_H + ACT_H + META_H + GAP

POSTS = [
    dict(user='brightside.cafe', sub='Brooklyn, New York', img='loc2', likes='212', cap='New spot, same coffee ☕ come say hi'),
    dict(user='tonys.pizza.nyc', sub='Sponsored', img='bad_flyer', likes='9', cap='BIG SALE!!! 50% OFF call now!!!'),
    dict(user='lumarc_studio', sub='Original audio', img=None, likes='48.2K', cap='Your content shouldn\'t stay on the screen.', reel=True, verified=True),
    dict(user='jess.travels', sub='Paris, France', img='loc4', likes='1,031', cap='paris in the morning hits different'),
    dict(user='burgerhouse_', sub='', img='bad_blurry_photo', likes='14', cap='lunch special today'),
    dict(user='northroast.coffee', sub='Sponsored', img='carousel_1', likes='3,880', cap='The art of the perfect cup.', carousel=True),
    dict(user='salon.glow.studio', sub='', img='bad_shaky_video', likes='6', cap='book now link in bio', reel=True),
    dict(user='sunset.rooftop', sub='Manhattan', img='loc3', likes='842', cap='golden hour, every day at 7'),
    dict(user='maisoncrumb', sub='', img='design_post', likes='5,402', cap='Baked at 5am. Gone by 10.'),
    dict(user='smash.burger.co', sub='', img='close_food', likes='2,291', cap='the double. that\'s it. that\'s the post.'),
    dict(user='beach.days', sub='Tulum, Mexico', img='loc7', likes='388', cap='out of office 🌴'),
    dict(user='oliva.restaurant', sub='Sponsored', img='website', likes='1,207', cap='A table worth remembering.'),
    dict(user='the.craft.bench', sub='', img='close_skill', likes='976', cap='8 hours on this one ring'),
    dict(user='corner.latte', sub='', img='close_service', likes='451', cap='made with love, every cup'),
]
SPECIAL = 2
AV_IMG = {'brightside.cafe': 'loc2', 'brightside': 'loc2', 'tonys.pizza.nyc': 'bad_flyer', 'tonys': 'bad_flyer', 'jess.travels': 'loc4',
          'burgerhouse_': 'bad_blurry_photo', 'northroast.coffee': 'close_service', 'salon.glow.studio': 'bad_shaky_video',
          'sunset.rooftop': 'loc3', 'maisoncrumb': 'design_post', 'smash.burger.co': 'close_food', 'beach.days': 'loc7',
          'oliva.restaurant': 'website', 'oliva': 'website', 'the.craft.bench': 'close_skill', 'corner.latte': 'close_service'}
STORIES = ['Your story', 'brightside', 'jess.travels', 'maisoncrumb', 'oliva', 'beach.days', 'tonys']

def post_top(i):
    """content-y of the top of post i's card."""
    return STORIES_H + i * CARD_H
def media_rect(i, scroll):
    """screen (x, y, w, h) of post i's media box at `scroll`."""
    return 0, int(round(TOP_Y + post_top(i) + HEAD_H - scroll)), W, MEDIA_H
def center_scroll(i, screen_cy=(TOP_Y + NAV_Y) / 2):
    """scroll that puts the centre of post i's media at screen_cy (default: centre of the visible feed area)."""
    return TOP_Y + post_top(i) + HEAD_H + MEDIA_H / 2 - screen_cy
CONTENT_H = STORIES_H + len(POSTS) * CARD_H

# ---------------------------------------------------------------- drawing helpers (2x supersampled icons)
SS = 3
def _icon(w, h, fn, col=FG):
    def mk():
        im = Image.new('L', (w * SS, h * SS)); fn(ImageDraw.Draw(im), SS * w / 56)
        a = im.resize((w, h), Image.LANCZOS); out = Image.new('RGBA', (w, h), col + (0,)); out.putalpha(a); return out
    return mk
def icon(name, size=56, col=FG):
    return E.cached(('fk_icon', name, size, col), _icon(size, size, ICONS[name], col))

def _heart(d, s, fill=False):
    k = s
    pts = []
    for j in range(64):
        a = 2 * math.pi * j / 64; x = 16 * math.sin(a) ** 3; y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((28 * k + x * 1.45 * k, 29 * k + y * 1.45 * k))
    if fill: d.polygon(pts, fill=255)
    else: d.line(pts + [pts[0]], fill=255, width=int(3.6 * k), joint='curve')
def _comment(d, s):
    d.ellipse((7 * s, 6 * s, 49 * s, 48 * s), outline=255, width=int(3.6 * s)); d.polygon([(10 * s, 38 * s), (4 * s, 52 * s), (20 * s, 46 * s)], fill=255)
def _share(d, s):
    d.line([(6 * s, 10 * s), (50 * s, 10 * s), (24 * s, 50 * s), (20 * s, 26 * s), (6 * s, 10 * s)], fill=255, width=int(3.6 * s), joint='curve')
    d.line([(20 * s, 26 * s), (50 * s, 10 * s)], fill=255, width=int(3.6 * s))
def _save(d, s):
    d.line([(12 * s, 6 * s), (44 * s, 6 * s), (44 * s, 50 * s), (28 * s, 36 * s), (12 * s, 50 * s), (12 * s, 6 * s)], fill=255, width=int(3.6 * s), joint='curve')
def _home(d, s):
    d.polygon([(28 * s, 6 * s), (50 * s, 24 * s), (50 * s, 50 * s), (6 * s, 50 * s), (6 * s, 24 * s)], fill=255)
    d.rectangle((22 * s, 34 * s, 34 * s, 50 * s), fill=0)
def _search(d, s):
    d.ellipse((6 * s, 6 * s, 42 * s, 42 * s), outline=255, width=int(3.8 * s)); d.line([(36 * s, 36 * s), (50 * s, 50 * s)], fill=255, width=int(4.2 * s))
def _plus(d, s):
    d.rounded_rectangle((6 * s, 6 * s, 50 * s, 50 * s), 12 * s, outline=255, width=int(3.6 * s))
    d.line([(28 * s, 16 * s), (28 * s, 40 * s)], fill=255, width=int(3.6 * s)); d.line([(16 * s, 28 * s), (40 * s, 28 * s)], fill=255, width=int(3.6 * s))
def _reels(d, s):
    d.rounded_rectangle((6 * s, 6 * s, 50 * s, 50 * s), 12 * s, outline=255, width=int(3.6 * s)); d.line([(6 * s, 18 * s), (50 * s, 18 * s)], fill=255, width=int(3.4 * s))
    d.line([(18 * s, 6 * s), (24 * s, 18 * s)], fill=255, width=int(3 * s)); d.line([(32 * s, 6 * s), (38 * s, 18 * s)], fill=255, width=int(3 * s))
    d.polygon([(23 * s, 26 * s), (23 * s, 42 * s), (36 * s, 34 * s)], fill=255)
def _dots(d, s):
    for x in (12, 28, 44): d.ellipse(((x - 3.5) * s, 24.5 * s, (x + 3.5) * s, 31.5 * s), fill=255)
def _messenger(d, s):
    d.ellipse((5 * s, 5 * s, 51 * s, 49 * s), outline=255, width=int(3.6 * s)); d.polygon([(10 * s, 40 * s), (6 * s, 54 * s), (20 * s, 47 * s)], fill=255)
    d.line([(15 * s, 33 * s), (24 * s, 22 * s), (31 * s, 29 * s), (41 * s, 20 * s)], fill=255, width=int(3.4 * s), joint='curve')
def _mute(d, s):
    d.polygon([(8 * s, 22 * s), (18 * s, 22 * s), (30 * s, 12 * s), (30 * s, 44 * s), (18 * s, 34 * s), (8 * s, 34 * s)], fill=255)
    d.line([(36 * s, 20 * s), (50 * s, 36 * s)], fill=255, width=int(3.4 * s)); d.line([(50 * s, 20 * s), (36 * s, 36 * s)], fill=255, width=int(3.4 * s))
def _verified(d, s):
    pts = []
    for j in range(24):
        a = 2 * math.pi * j / 24; r = (25 if j % 2 == 0 else 21) * s; pts.append((28 * s + r * math.cos(a), 28 * s + r * math.sin(a)))
    d.polygon(pts, fill=255)
    d.line([(18 * s, 28 * s), (25 * s, 35 * s), (38 * s, 21 * s)], fill=0, width=int(4 * s), joint='curve')
def _chev(d, s):
    d.line([(14 * s, 20 * s), (28 * s, 34 * s), (42 * s, 20 * s)], fill=255, width=int(4 * s), joint='curve')
ICONS = dict(heart=lambda d, s: _heart(d, s), heart_fill=lambda d, s: _heart(d, s, True), comment=_comment, share=_share, save=_save,
             home=_home, search=_search, plus=_plus, reels=_reels, dots=_dots, messenger=_messenger, mute=_mute, verified=_verified, chev=_chev)

def _avatar_circle(size, seed, ring=True, img=None):
    def mk():
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        if ring:
            g = E.gradient(size, size, [(255, 196, 0), (255, 48, 108), (200, 40, 200)]).convert('RGBA')
            m = Image.new('L', (size * SS, size * SS)); ImageDraw.Draw(m).ellipse((0, 0, size * SS - 1, size * SS - 1), fill=255)
            g.putalpha(m.resize((size, size), Image.LANCZOS)); im.alpha_composite(g)
            m2 = Image.new('L', (size * SS, size * SS)); o = int(size * .06 * SS); ImageDraw.Draw(m2).ellipse((o, o, size * SS - 1 - o, size * SS - 1 - o), fill=255)
            blk = Image.new('RGBA', (size, size), BG + (255,)); blk.putalpha(m2.resize((size, size), Image.LANCZOS)); im.alpha_composite(blk)
        inset = int(size * (.12 if ring else 0)); s2 = size - 2 * inset
        if img is not None: face = img
        elif seed == 'lumarc':
            face = Image.new('RGB', (s2, s2), (14, 14, 20)); lg = E.logo(int(s2 * .82)); face = face.convert('RGBA')
            face.alpha_composite(lg, ((s2 - lg.width) // 2, (s2 - lg.height) // 2)); face = face.convert('RGB')
        else:
            src = AV_IMG.get(seed)
            if src:
                a = E.asset(src); s_ = min(a.width, a.height); face = a.crop(((a.width - s_) // 2, (a.height - s_) // 2, (a.width + s_) // 2, (a.height + s_) // 2))
            else:
                r = np.random.default_rng(zlib.crc32(seed.encode()))
                cs = [tuple(int(v) for v in r.integers(40, 230, 3)) for _ in range(3)]
                face = E.gradient(s2, s2, cs)
        face = face.convert('RGB').resize((s2, s2), Image.LANCZOS)
        m3 = Image.new('L', (s2 * SS, s2 * SS)); ImageDraw.Draw(m3).ellipse((0, 0, s2 * SS - 1, s2 * SS - 1), fill=255)
        f = face.convert('RGBA'); f.putalpha(m3.resize((s2, s2), Image.LANCZOS)); im.alpha_composite(f, (inset, inset))
        return im
    return E.cached(('fk_av', size, seed, ring), mk)

def _cover(img, w, h):
    sc = max(w / img.width, h / img.height); im = img.resize((int(img.width * sc + .999), int(img.height * sc + .999)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2; return im.crop((x, y, x + w, y + h))

def _media(i):
    p = POSTS[i]
    def mk():
        im = _cover(E.asset(p['img']), W, MEDIA_H).convert('RGBA')
        d = ImageDraw.Draw(im)
        if p.get('carousel'):
            pill_ = Image.new('RGBA', (96, 52), (0, 0, 0, 0)); ImageDraw.Draw(pill_).rounded_rectangle((0, 0, 95, 51), 26, fill=(20, 20, 20, 170))
            ImageDraw.Draw(pill_).text((48, 26), '1/6', font=E.font(28, 600), fill=FG, anchor='mm'); im.alpha_composite(pill_, (W - 126, 30))
        if p.get('reel'):
            im.alpha_composite(icon('reels', 52), (W - 82, 30))
            m = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); ImageDraw.Draw(m).ellipse((0, 0, 63, 63), fill=(20, 20, 20, 170))
            m.alpha_composite(icon('mute', 34), (15, 15)); im.alpha_composite(m, (W - 94, MEDIA_H - 94))
        return im
    return E.cached(('fk_media', i), mk)

def _reel_overlay():
    """the badges drawn over the special Reel's media (reels glyph top-right, mute bottom-right)."""
    def mk():
        im = Image.new('RGBA', (W, MEDIA_H), (0, 0, 0, 0))
        im.alpha_composite(icon('reels', 52), (W - 82, 30))
        m = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); ImageDraw.Draw(m).ellipse((0, 0, 63, 63), fill=(20, 20, 20, 170))
        m.alpha_composite(icon('mute', 34), (15, 15)); im.alpha_composite(m, (W - 94, MEDIA_H - 94))
        return im
    return E.cached('fk_reel_ov', mk)

def _head(i):
    p = POSTS[i]
    def mk():
        im = Image.new('RGBA', (W, HEAD_H), BG + (255,)); d = ImageDraw.Draw(im)
        im.alpha_composite(_avatar_circle(84, 'lumarc' if p['user'] == 'lumarc_studio' else p['user']), (26, (HEAD_H - 84) // 2))
        f = E.font(32, 700); d.text((130, 30 if p['sub'] else 42), p['user'], font=f, fill=FG)
        x = 130 + int(f.getlength(p['user'])) + 10
        if p.get('verified'): im.alpha_composite(icon('verified', 30, (61, 133, 250)), (x, 33 if p['sub'] else 45))
        if p['sub']: d.text((130, 70), p['sub'], font=E.font(25, 400), fill=FG if p['sub'] != 'Sponsored' else SUB)
        im.alpha_composite(icon('dots', 44), (W - 74, (HEAD_H - 44) // 2))
        return im
    return E.cached(('fk_head', i), mk)

def _foot(i, liked=False):
    p = POSTS[i]
    def mk():
        im = Image.new('RGBA', (W, ACT_H + META_H + GAP), BG + (255,)); d = ImageDraw.Draw(im)
        hy = (ACT_H - 56) // 2 + 4
        im.alpha_composite(icon('heart_fill', 56, (255, 48, 64)) if liked else icon('heart', 56), (30, hy))
        im.alpha_composite(icon('comment', 56), (122, hy)); im.alpha_composite(icon('share', 56), (214, hy)); im.alpha_composite(icon('save', 56), (W - 86, hy))
        if p.get('carousel'):
            for k in range(6): d.ellipse((W / 2 - 50 + k * 18, ACT_H / 2 - 5, W / 2 - 40 + k * 18, ACT_H / 2 + 5), fill=(61, 133, 250) if k == 0 else (90, 90, 90))
        d.text((30, ACT_H + 4), f"{p['likes']} likes", font=E.font(30, 700), fill=FG)
        fb = E.font(30, 700); d.text((30, ACT_H + 50), p['user'], font=fb, fill=FG)
        d.text((30 + fb.getlength(p['user']) + 12, ACT_H + 50), p['cap'], font=E.font(30, 400), fill=FG)
        d.text((30, ACT_H + 98), 'View all comments' if p['likes'] not in ('9', '6', '14') else 'Add a comment…', font=E.font(27, 400), fill=SUB)
        return im
    return E.cached(('fk_foot', i, liked), mk)

def _stories():
    def mk():
        im = Image.new('RGBA', (W, STORIES_H), BG + (255,)); d = ImageDraw.Draw(im)
        for k, name in enumerate(STORIES):
            x = 22 + k * 176
            im.alpha_composite(_avatar_circle(150, name, ring=k > 0), (x, 10))
            if k == 0:
                d.ellipse((x + 104, 112, x + 148, 156), fill=(61, 133, 250), outline=BG, width=5)
                d.text((x + 126, 133), '+', font=E.font(40, 700), fill=FG, anchor='mm')
            d.text((x + 75, 196), name[:11], font=E.font(24, 400), fill=FG if k else SUB, anchor='mm')
        d.line([(0, STORIES_H - 1), (W, STORIES_H - 1)], fill=LINE, width=1)
        return im
    return E.cached('fk_stories', mk)

def chrome_top(clock='9:41'):
    """status bar + app top bar (RGBA, 1080 x TOP_Y)."""
    def mk():
        im = Image.new('RGBA', (W, TOP_Y), BG + (255,)); d = ImageDraw.Draw(im)
        d.text((86, 40), clock, font=E.font(34, 700), fill=FG, anchor='mm')
        # signal / wifi / battery
        for k in range(4): d.rounded_rectangle((W - 238 + k * 13, 46 - 6 - k * 5, W - 229 + k * 13, 48), 2, fill=FG)
        for r, w_ in ((26, 4), (17, 4), (8, 0)):
            if w_: d.arc((W - 168 - r, 50 - r, W - 168 + r, 50 + r), 225, 315, fill=FG, width=w_)
            else: d.pieslice((W - 168 - 9, 50 - 9, W - 168 + 9, 50 + 9), 225, 315, fill=FG)
        d.rounded_rectangle((W - 126, 28, W - 66, 54), 8, outline=(150, 150, 150), width=3); d.rounded_rectangle((W - 121, 33, W - 86, 49), 4, fill=FG)
        d.rounded_rectangle((W - 63, 36, W - 58, 46), 2, fill=(150, 150, 150))
        f = E.font(52, 800); d.text((34, STATUS_H + TOP_H / 2), 'For you', font=f, fill=FG, anchor='lm')
        im.alpha_composite(icon('chev', 40), (34 + int(f.getlength('For you')) + 8, int(STATUS_H + TOP_H / 2 - 16)))
        im.alpha_composite(icon('heart', 58), (W - 182, int(STATUS_H + TOP_H / 2 - 29)))
        im.alpha_composite(icon('messenger', 58), (W - 92, int(STATUS_H + TOP_H / 2 - 29)))
        rd = Image.new('RGBA', (34, 34), (0, 0, 0, 0)); ImageDraw.Draw(rd).ellipse((0, 0, 33, 33), fill=(255, 48, 64), outline=BG, width=3)
        ImageDraw.Draw(rd).text((17, 17), '3', font=E.font(20, 700), fill=FG, anchor='mm'); im.alpha_composite(rd, (W - 54, STATUS_H + 18))
        return im
    return E.cached(('fk_top', clock), mk)

def chrome_nav():
    """bottom tab bar (RGBA, 1080 x NAV_H)."""
    def mk():
        im = Image.new('RGBA', (W, NAV_H), BG + (255,)); d = ImageDraw.Draw(im)
        d.line([(0, 0), (W, 0)], fill=LINE, width=2)
        for k, name in enumerate(['home', 'search', 'plus', 'reels']):
            im.alpha_composite(icon(name, 60), (int(W * (k + .5) / 5 - 30), 30))
        im.alpha_composite(_avatar_circle(64, 'me', ring=False), (int(W * 4.5 / 5 - 32), 28))
        d.rounded_rectangle((W / 2 - 140, NAV_H - 20, W / 2 + 140, NAV_H - 10), 5, fill=(230, 230, 230))     # home indicator
        return im
    return E.cached('fk_nav', mk)

def special_media(ctx, cam=None, avatar=None):
    """his live studio world (avatar talking) as the 1080x1350 media of the special Reel post. Default framing: the
    engine world through a camera that frames head + chest in 4:5 (crop y 285..1635 of the composed frame)."""
    c = dict(z=1.0, x=540., y=960., dx=0., dy=0., rot=0.); c.update(cam or {})
    fr = ctx.compose(cam=c, avatar=avatar)
    y0 = 300; return fr.convert('RGB').crop((0, y0, W, y0 + MEDIA_H))

def screen(scroll, special=None, t=0.0, chrome=True, liked=None, clock='9:41', special_overlay=True):
    """the whole phone screen (RGBA 1080x1920) at `scroll` content-px. `special`: RGB image for the Reel media (None =
    black). `liked`: set of post indices drawn with a red heart."""
    im = Image.new('RGBA', (W, H), BG + (255,))
    y0 = TOP_Y - scroll                                # screen y of content 0
    if y0 + STORIES_H > 0 and y0 < H: im.alpha_composite(_stories(), (0, int(round(y0)))) if y0 >= 0 else _paste_clip(im, _stories(), 0, y0)
    for i in range(len(POSTS)):
        top = y0 + post_top(i)
        if top > H or top + CARD_H < 0: continue
        _paste_clip(im, _head(i), 0, top)
        if i == SPECIAL:
            m = special if special is not None else Image.new('RGB', (W, MEDIA_H), (10, 10, 14))
            if m.size != (W, MEDIA_H): m = _cover(m, W, MEDIA_H)
            m = m.convert('RGBA')
            if special_overlay: m = m.copy(); m.alpha_composite(_reel_overlay())
        else: m = _media(i)
        _paste_clip(im, m, 0, top + HEAD_H)
        _paste_clip(im, _foot(i, liked is not None and i in liked), 0, top + HEAD_H + MEDIA_H)
    if chrome:
        im.alpha_composite(chrome_top(clock), (0, 0)); im.alpha_composite(chrome_nav(), (0, NAV_Y))
    return im

def _paste_clip(base, img, x, y):
    x, y = int(round(x)), int(round(y))
    if y >= 0 and y + img.height <= base.height: base.alpha_composite(img, (x, y)); return
    a0, a1 = max(0, -y), min(img.height, base.height - y)
    if a1 > a0: base.alpha_composite(img.crop((0, a0, img.width, a1)), (x, y + a0))
