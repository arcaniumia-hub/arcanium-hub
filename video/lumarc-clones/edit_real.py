"""LUMARC Reel — "We're not real", v2: every clone lives in its own REAL location (photo plates in src/bg/), no group shots.

    python3 edit_real.py render [t0 t1]   # -> out/video.mp4   (needs work/track_*.mp4 from `edit.py tracks`)
    python3 edit_real.py stills t …       # -> out/still_<t>.jpg
    python3 edit.py mux                   # voice + music -> out/lumarc-clones.mp4 (same timeline as v1)

Clone #1 (blazer) talks from a home studio, #2 (hoodie) from a coffee shop, #3 (white tee) from a rooftop; the
conversation cuts between them. The "week" lines go to Paris / a boardroom / a dull training room, the punchline
to an empty beach chair. Compositing for a natural look: plates upscaled + depth-of-field blur, clone graded to the
plate's light, light-wrap on the key edge, handheld camera drift, jump-cut punch-ins, one grain/vignette pass on top.
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import edit as base
from edit import (W, H, FPS, TL, L, END, DUR, Reader, zoom, clamp, eout, back, put, popin, cached, pill, chip, key,
                  draw_captions, counters, views0, logo_pop, comment, endcard, glitch, NAME, HEAD, WORK, OUT, HY)

BG = {k: os.path.join(HERE, f'src/bg/bg{i}.png') for i, k in
      enumerate(['studio', 'cafe', 'rooftop', 'paris', 'board', 'taxes', 'beach'], 1)}
# location -> clone placement (cx, scale, y offset), plate blur (DOF), tint on the clone (r, g, b), desaturation
PLACE = {
    'studio':  dict(cx=600, s=.95, yo=40,  blur=5.0, tint=(1.03, .99, 1.02), desat=0),
    'cafe':    dict(cx=540, s=.88, yo=90,  blur=5.0, tint=(1.05, 1.00, .94), desat=0),
    'rooftop': dict(cx=430, s=.92, yo=30,  blur=4.0, tint=(1.08, 1.00, .88), desat=0),
    'paris':   dict(cx=360, s=.86, yo=120, blur=3.0, tint=(1.03, 1.00, .97), desat=0),
    'board':   dict(cx=560, s=.86, yo=230, blur=2.5, tint=(.97, 1.00, 1.04), desat=0),
    'taxes':   dict(cx=330, s=.84, yo=170, blur=1.6, tint=(1.00, 1.00, .98), desat=.3),
    'beach':   dict(blur=1.2),
}
LOC = ['studio', 'cafe', 'rooftop', 'studio', 'cafe', 'rooftop', 'paris', 'board', 'taxes', 'studio', 'cafe', 'rooftop', 'studio']
TIGHT = {3: 1.16, 4: 1.12, 5: 1.12, 9: 1.0, 10: 1.14, 11: 1.12, 12: 1.2}          # jump-cut punch-ins on repeat visits
S_BEACH = L[12]['t1'] + .28
SHOTS = []
for i in range(13):
    a = 0.0 if i == 0 else TL[i]['t0'] - .10
    z = TL[i + 1]['t0'] - .10 if i < 12 else S_BEACH
    SHOTS.append(dict(a=a, z=z, loc=LOC[i], k=TL[i]['k'], line=i, zoom=TIGHT.get(i, 1.0)))
SHOTS.append(dict(a=S_BEACH, z=END, loc='beach', k=None, line=13, zoom=1.0))
WHIP_IN = {6, 7, 8, 9, 13}                                                            # shots entered with a whip pan
FIRST = {}
for s in SHOTS:
    FIRST.setdefault(s['loc'], s['a'])

_plates = {}
def plate(loc):
    if loc not in _plates:
        im = Image.open(BG[loc]).convert('RGB')
        sc = max(W / im.width, H / im.height) * 1.06
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        x0, y0 = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((x0, y0, x0 + W, y0 + H))
        sharp = im.filter(ImageFilter.GaussianBlur(PLACE[loc]['blur']))
        wrap = im.filter(ImageFilter.GaussianBlur(40))
        mean = np.asarray(im.crop((200, 500, 880, 1500)), np.float32).reshape(-1, 3).mean(0)
        _plates[loc] = (sharp, wrap, mean)
    return _plates[loc]

def wobble(t, seed, amp):
    return amp * (math.sin(t * 1.3 + seed) * .6 + math.sin(t * 2.1 + seed * 1.7) * .3 + math.sin(t * 3.7 + seed * .3) * .1)

_grain = [np.random.default_rng(i).normal(0, 7, (H // 2, W // 2, 1)).astype(np.float32) for i in range(6)]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .30 * np.clip((((_xx - W / 2) / (W * .7)) ** 2 + ((_yy - H * .45) / (H * .7)) ** 2) - .2, 0, 1))[..., None]
del _yy, _xx

class Edit:
    def __init__(self, t0):
        self.t0 = t0; self.trk = {k: Reader(os.path.join(WORK, f'track_{k}.mp4'), t0, DUR - t0 + .5) for k in 'abc'}
        self.end = None
    def src(self, k, t): return self.trk[k].get(int(round((t - self.t0) * FPS)))

    def shot_at(self, t):
        for s in SHOTS:
            if s['a'] <= t < s['z']: return s
        return None

    def compose(self, s, t):
        loc = s['loc']; P = PLACE[loc]; sharp, wrap, mean = plate(loc); lt = t - s['a']
        img = sharp.copy()
        if s['k']:
            k = s['k']; sc = P['s']
            src = self.src(k, t)
            im = key(src.resize((int(W * sc), int(H * sc)), Image.BILINEAR))
            rgb = np.asarray(im.convert('RGB'), np.float32); al = np.asarray(im.getchannel('A'), np.float32) / 255
            # grade the clone to the plate: tint + pull its mean a little toward the plate's light
            rgb = rgb * np.array(P['tint'], np.float32)
            cm = rgb[al > .5].mean(0) if (al > .5).any() else rgb.reshape(-1, 3).mean(0)
            rgb = rgb * (1 + .18 * (mean / (cm + 1e-3) - 1))
            if P['desat']: g = rgb.mean(2, keepdims=True); rgb = g + (rgb - g) * (1 - P['desat'])
            x = int(P['cx'] - im.width / 2); y = int(H - im.height + P['yo'])
            # light wrap: plate light bleeding over the edge band
            a_img = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
            al = np.asarray(a_img, np.float32) / 255
            edge = np.clip(al - np.asarray(a_img.filter(ImageFilter.MinFilter(9)), np.float32) / 255, 0, 1)[..., None]
            wcrop = np.asarray(wrap.crop((x, y, x + im.width, y + im.height)).resize(im.size), np.float32)
            rgb = rgb * (1 - .45 * edge) + wcrop * .45 * edge
            out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); out.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
            img = img.convert('RGBA'); img.paste(out, (x, y), out)
            hx = P['cx']; hy = H - im.height + P['yo'] + sc * (HEAD[k] + 230)
            if s['line'] in (0, 1, 2) and t >= max(s['a'], TL[s['line']]['t0'] + (2.2 if s['line'] == 0 else 0)):
                first = TL[s['line']]['t0'] + (2.2 if s['line'] == 0 else 0)
                tx = hx + (300 if hx < 600 else -300)
                put(img, cached('tagr' + k, lambda k=k: pill(NAME[k], 40, 800, grad=True)), tx, hy - 60, popin(t - first))
            img = img.convert('RGB')
        else:
            hx, hy = 540, 900
        # camera: slow push, jump-cut punch, handheld drift
        z = s['zoom'] * (1.03 + .012 * lt)
        if s['line'] == 0:                       # punch-ins on "I'm not real" / "digital clone"
            for at, amt in ((TL[0]['t0'] + .9, .10), (TL[0]['t0'] + 2.25, .08)):
                if t >= at: z += amt * eout((t - at) / .12)
        dx = wobble(t, s['line'] * 3.1, 7); dy = wobble(t, s['line'] * 5.3 + 2, 6); rot = wobble(t, s['line'] + 9, .0035)
        ax, ay = (hx, hy) if s['k'] else (540, 1100)
        X = min(max(ax + dx, W - z * (W - ax)), z * ax); Y = min(max(ay + dy, H - z * (H - ay)), z * ay)
        return zoom(img, z, (ax, ay), dx=X - ax, dy=Y - ay, rot=rot)

    def endframe(self, t):
        if self.end is None:
            import subprocess
            b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '29.9', '-i', HY, '-frames:v', '1', '-vf', f'scale={W}:{H}',
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            self.end = Image.frombuffer('RGB', (W, H), b, 'raw', 'RGB', 0, 1).copy(); self.endr = Reader(HY, 28.3, 1.6)
        lt = t - END
        return zoom(self.endr.get(int(round(lt * FPS))) if lt < 1.55 else self.end, 1 + .02 * lt)

    def frame(self, t):
        for k in 'abc': self.src(k, t)
        if t >= END:
            img = self.endframe(t); s = None
        else:
            s = self.shot_at(t); i = SHOTS.index(s)
            if i in WHIP_IN and t < s['a'] + .12 or (i + 1 < len(SHOTS) and (i + 1) in WHIP_IN and t >= s['z'] - .12):
                w = s['a'] if t < s['a'] + .12 else s['z']; p = (t - (w - .12)) / .24
                A = self.compose(SHOTS[SHOTS.index(self.shot_at(w - .01))], min(t, w - .01)); B = self.compose(self.shot_at(w), max(t, w))
                c = Image.new('RGB', (W, H)); off = int(W * eout(p)); c.paste(A, (-off, 0)); c.paste(B, (W - off, 0))
                img = Image.blend(c, c.resize((W // 10, H), Image.BILINEAR).resize((W, H), Image.BILINEAR), .75 * (1 - abs(p - .5) * 2))
            else:
                img = self.compose(s, t)
            img = glitch(img, t)
            # unifying grade: vignette + grain
            a = np.asarray(img, np.float32) * VIG
            g = _grain[int(t * FPS) % len(_grain)]; a = a + np.repeat(np.repeat(g, 2, 0), 2, 1)
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        for at, amt in [(0.0, .6), (END, .6)]:
            if at <= t < at + .3:
                a = np.asarray(img).astype(np.float32); img = Image.fromarray(np.clip(a + (255 - a) * amt * math.exp(-(t - at) / .07), 0, 255).astype(np.uint8))
        fr = img.convert('RGBA')
        if s is not None:
            loc = s['loc']; ch = {'studio': 'HOME STUDIO', 'cafe': 'COFFEE SHOP', 'rooftop': 'ROOFTOP', 'paris': 'MONDAY · PARIS',
                                  'board': 'TUESDAY · INVESTORS', 'taxes': 'WEDNESDAY · TAXES', 'beach': 'OUT OF OFFICE'}[loc]
            first = FIRST[loc]; show = loc in ('paris', 'board', 'taxes', 'beach') or t < first + 1.6
            if show and t >= s['a'] and (loc in ('paris', 'board', 'taxes', 'beach') or s['a'] == first):
                a = 1 - clamp((t - first - 1.4) / .25) if loc in ('studio', 'cafe', 'rooftop') else 1
                put(fr, cached('chip' + loc, lambda ch=ch: chip(ch)), W / 2, 170, popin(t - s['a'] - .1), a)
            counters(fr, t); views0(fr, t); logo_pop(fr, t); comment(fr, t)
            draw_captions(fr, t, 700 if loc == 'beach' else 1310)
        endcard(fr, t)
        return fr.convert('RGB')

def render(t0=0., t1=None):
    import subprocess
    t1 = DUR if t1 is None else t1
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', os.path.join(OUT, 'video.mp4')], stdin=subprocess.PIPE)
    E = Edit(t0)
    for i in range(int(round((t1 - t0) * FPS))):
        enc.stdin.write(E.frame(t0 + i / FPS).tobytes())
        if i % 150 == 0: print(f'{t0 + i / FPS:.1f}', flush=True)
    enc.stdin.close(); enc.wait()

def stills(ts):
    for t in ts: Edit(t).frame(t).save(os.path.join(OUT, f'still_{t:05.2f}.jpg'), quality=88)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'render'
    if cmd == 'render': render(*[float(x) for x in sys.argv[2:4]])
    elif cmd == 'stills': stills([float(x) for x in sys.argv[2:]])
