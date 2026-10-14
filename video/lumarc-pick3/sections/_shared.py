"""Shared bits used by more than one section (read-only for section authors).

    from sections import _shared as SH
    SH.PHONE                       # '(854) 295-2249' — the CTA number (shown on screen, never spoken)
    SH.generic_stamp(w=760)        # the red "GENÉRICO" rubber stamp (RGBA, already rotated): s01 slams it, s08 brings it back
    SH.STAMP_RED                   # its ink colour
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E

PHONE = '(854) 295-2249'
STAMP_RED = (226, 44, 58)

def generic_stamp(w=760, angle=-9.0, word='GENÉRICO', seed=7):
    """distressed red rubber stamp: double-ruled rounded box + heavy caps, uneven ink (seeded = deterministic)."""
    def mk():
        h = int(w * .30); S = 2; W2, H2 = w * S, h * S
        m = Image.new('L', (W2, H2), 0); d = ImageDraw.Draw(m)
        lw = int(H2 * .055); r = int(H2 * .12)
        d.rounded_rectangle((lw, lw, W2 - lw, H2 - lw), r, outline=255, width=lw)
        g = int(lw * 2.1); d.rounded_rectangle((g + lw, g + lw, W2 - g - lw, H2 - g - lw), int(r * .7), outline=255, width=max(2, lw // 2))
        f = E.font(int(H2 * .52), 900); l, t, rr, b = f.getbbox(word); tw, th = rr - l, b - t
        sx = min(1.0, (W2 - 2 * g - 6 * lw) / tw)
        txt = Image.new('L', (tw + 4, th + 4), 0); ImageDraw.Draw(txt).text((2 - l, 2 - t), word, font=f, fill=255)
        txt = txt.resize((max(1, int(txt.width * sx)), txt.height), Image.LANCZOS)
        m.paste(txt, ((W2 - txt.width) // 2, (H2 - txt.height) // 2), txt)
        rng = np.random.default_rng(seed)
        n = rng.random((H2 // 6 + 1, W2 // 6 + 1)).astype(np.float32)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W2, H2), Image.BICUBIC), np.float32) / 255
        speck = (rng.random((H2, W2)) > .985).astype(np.float32)
        a = np.asarray(m, np.float32) / 255 * np.clip(.55 + .75 * n, 0, 1) * (1 - speck * .9)
        a = np.clip(a * 1.15, 0, 1)
        img = Image.new('RGBA', (W2, H2), STAMP_RED + (0,)); img.putalpha(Image.fromarray((a * 235).astype(np.uint8)))
        img = img.resize((w, h), Image.LANCZOS).rotate(angle, Image.BICUBIC, expand=True)
        return img
    return E.cached(('generic_stamp', w, angle, word, seed), mk)

if __name__ == '__main__':
    import os; os.makedirs(os.path.join(E.HERE, 'out', 'shared'), exist_ok=True)
    bg = Image.new('RGBA', (900, 400), (240, 240, 240, 255)); s = generic_stamp(760); bg.alpha_composite(s, ((900 - s.width) // 2, (400 - s.height) // 2))
    bg.convert('RGB').save(os.path.join(E.HERE, 'out', 'shared', 'stamp.jpg')); print('ok')
