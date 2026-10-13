"""s03 — "Your last post was Christmas. [beat] Twenty twenty-one." / Kevin: "I've been busy!"   (lines 4-5)

Beats (timeline s, frame grid 30 fps; onsets measured on src/voice16k.raw, see _B_kit.MEASURED):
  10.46  Instagram, deadpan. A slow sitcom push into his face (+3 %/s) that leans in harder from "Christmas" (11.55)
         through the beat — the audience waits with him.
  12.567 SMASH CUT on "Twenty" (12.56) to a screen recording of @kevinsbakery's last post: iOS recording pill, the
         "Posts" nav bar, grey no-photo avatar, the sad flash-glare Christmas tree, "3 likes", kevins_mom: "so proud of
         you sweetie", December 24, 2021. The feed is still settling from a scroll (content slides under the fixed nav
         bar); the next, older post peeks in below — a flyer (sets up s04).
  13.000 "twenty-one" (13.00) — documentary punch-in, ON the word: z 1 -> 1.66 in 5 frames about the date line, then
         a creep; rendered from a 2x screen so the type stays crisp. The mom comment still fits on screen.
         Captions: our own one-line kinetic type of the same words in the black gap under the date (engine captions
         would wrap onto the UI).
  13.867 cut to Kevin (between "twenty-one" and "I've" 13.95): defensive. CRASH ZOOM on "busy!" (14.37), held on his
         sheepish closed-mouth half-smile (the take's own tail) until Instagram fires back at 15.04.
B_review: measured captions (no stale page over the Kevin cut, CHRISTMAS pops on the word, not 0.35 s late), clean
matte on both takes, nav bar + 2x punch-in, the push now starts ON "twenty-one".
"""
import math
from PIL import Image
import engine as E
from sections import _B_kit as K

START, END = E.span(4, 5)                     # 10.46 – 15.04

WORDS = {(4, w): t for w, t in K.MEASURED[4]}
WORDS.update({(5, w): t for w, t in K.MEASURED[5]})
T_XMAS, T_TW, T_21, T_BUSY = WORDS[(4, 'CHRISTMAS.')], WORDS[(4, 'TWENTY')], WORDS[(4, 'TWENTY-ONE.')], WORDS[(5, 'BUSY!')]
FR = lambda j: j / E.FPS
CUT_POST = FR(377)          # 12.5667 — first frame at/after "Twenty" (12.56)
PUSH_21 = FR(390)           # 13.0000 — "twenty-one" (13.00): first zoomed frame is ON the word
CUT_KEVIN = FR(416)         # 13.8667 — after "twenty-one" ends (13.80), before "I've" (13.95)
SNAP = FR(431)              # 14.3667 — "busy!" /b/ release 14.37

CUES = [
    (T_XMAS, 'riser', {'to': CUT_POST, 'gain': -9}),   # the lean-in from "Christmas" through the beat
    (CUT_POST, 'swipe', {'gain': -4}),                 # into the screen recording
    (PUSH_21, 'zoom', {'gain': -9}),                   # documentary punch-in on the date
    (SNAP, 'zoom', {}),                                # crash zoom on "busy!"
]

IG_FACE = (452, 410)        # Instagram's face on his angle (screen px at z=1)
K_FACE = (548, 440)         # Kevin's face on his angle

def _smooth(x):
    x = E.clamp(x); return x * x * (3 - 2 * x)

def _post_screen(t):
    """the 2021 post screen recording at t (RGB 1080x1920) and its punch-in zoom."""
    scroll = -56 * (1 - E.eout((t - CUT_POST) / .34))             # he just scrolled up to it: still settling
    k = E.eout(E.clamp((t - PUSH_21 + 1 / E.FPS) / (5 / E.FPS)))
    z = 1 + .66 * k + .045 * _smooth((t - PUSH_21 - 5 / E.FPS) / .7)
    return K.ig2021_screen(scroll if scroll < -.5 else 0.0, z, (16, 1565)), z

CAP_Y = 1662
def _caption(ctx, t):
    """one-line kinetic caption of the same words (engine word-pop maths, Instagram's colours), in the black gap
    between the date and the next post — before and after the punch-in."""
    words = [('TWENTY', T_TW), ('TWENTY-ONE.', T_21)]
    size = 78; gap = int(size * .30)
    ims = [E.cap_word(w, size, 'I') for w, _ in words]
    pads = [E.word_img(w, size, 'white')[1] for w, _ in words]
    widths = [im.width - 2 * p for im, p in zip(ims, pads)]
    x = E.W / 2 - (sum(widths) + gap) / 2
    for (w, t0), im, p, wd in zip(words, ims, pads, widths):
        if t >= t0 - .02:
            lt = t - t0 + .02; s = .72 + .28 * E.back(lt / .16, 1.4)
            if t0 - .02 <= t < t0 + .40: s *= 1.03
            img = im if lt >= .05 else E.fade(im, lt / .05)
            if abs(s - 1) > .01: img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
            ctx.add('screen', img, x + wd / 2, CAP_Y)
        x += wd + gap

def draw(ctx, lt, t):
    if t < CUT_POST:
        # Instagram: slow push, leaning in harder from "Christmas" through the beat
        K.show(ctx, 'I', ctx.shot['src'], 'I')
        z = 1 + .03 * (t - START) + .075 * _smooth((t - T_XMAS) / (CUT_POST - T_XMAS))
        ctx.cam.update(z=z, x=IG_FACE[0], y=IG_FACE[1])
    elif t < CUT_KEVIN:
        scr, z = _post_screen(t)
        ctx.full = scr
        _caption(ctx, t)
        ctx.post.update(vignette=.10, grain=.55)
    else:
        # Kevin: "I've been busy!" — crash zoom on "busy!"
        K.show(ctx, 'K', 7.36 + (t - 13.92), 'K')
        k = E.eout((t - SNAP + 1 / E.FPS) / (2.4 / E.FPS))
        z = 1 + .012 * (t - CUT_KEVIN) + .40 * k + .025 * E.clamp((t - SNAP) / .7)
        ctx.cam.update(z=z, x=K_FACE[0], y=K_FACE[1], dy=40 * k)
        if SNAP - .5 / E.FPS <= t < SNAP + 1.5 / E.FPS:       # smooth crash-zoom blur on the picture only
            amt = .07 if t < SNAP + .5 / E.FPS else .025
            ctx.wrap = lambda fr, a=amt: K.zoom_blur(fr, a, (540, 520))
    K.captions(ctx, t, (4, 5), cuts=(CUT_POST, CUT_KEVIN), hide=((CUT_POST, CUT_KEVIN),))
