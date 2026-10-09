"""Score + sound design for the SILENCE ONE motion piece -> music.wav (48 kHz stereo, 34.5 s, 120 BPM).
Cuts: 3.0 drop · 8.0 teardown · 18.0 specs · 23.0 noise · 24.5 ANC (silence) · 27.5 hit · 31.0 LUMARC sting
"""
import subprocess, math
from itertools import accumulate
import numpy as np

SR, DUR = 48000, 34.5
N = int(SR * DUR); BEAT = .5
rng = np.random.default_rng(11)
def T(s): return int(round(s * SR))
def t_(n): return np.arange(n) / SR
def add(buf, x, at, g=1.):
    if x.ndim == 1: x = np.stack([x, x], 1)
    i = T(at); j = min(N, i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def lp(x, fc, passes=2):
    a = math.exp(-2 * math.pi * fc / SR); y = x
    for _ in range(passes): y = np.array(list(accumulate(y, lambda s, v: (1 - a) * v + a * s)), np.float32)
    return y
def hp(x, fc): return x - lp(x, fc, 1)
def noise(n): return rng.standard_normal(n).astype(np.float32)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

mus = np.zeros((N, 2), np.float32); sfx = np.zeros((N, 2), np.float32)

# --- instruments
n = T(.5); tt = t_(n)
KICK = np.tanh(2 * np.sin(2 * np.pi * (46 * tt + 80 * .03 * (1 - np.exp(-tt / .03)))) * np.exp(-tt / .17)) * .9
n = T(.06); HAT = hp(noise(n), 7000) * np.exp(-t_(n) / .02)
n = T(.25); tt = t_(n); CLAP = hp(noise(n), 1200) * (np.exp(-tt / .05) + .5 * np.exp(-np.maximum(tt - .012, 0) / .03) * (tt > .012))
def pluck(m, dur=.6, dec=.14):
    tt = t_(T(dur)); f = mtof(m)
    return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt) + .1 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt / dec)
def pad(notes, dur, att=.4, rel=.8, bright=1600):
    tt = t_(T(dur)); x = np.zeros(len(tt), np.float32)
    for m in notes:
        for det in (-.08, 0, .08):
            ph = mtof(m) * (1 + det / 100) * tt; x += (2 * (ph % 1) - 1) * .03
    x = lp(x, bright); env = np.minimum(1, tt / att) * np.minimum(1, (tt[-1] - tt) / rel + 1e-3)
    return x * env
def whoosh(at, dur=.5, g=.35, up=True):
    n = T(dur); tt = t_(n); w = noise(n); k = tt / tt[-1]
    x = hp(lp(w, 2500), 300) * (np.sin(np.pi * k) ** 2) * (k if up else 1 - k + .2)
    add(sfx, x, at - dur * .8, g)
def impact(at, g=1.):
    n = T(1.6); tt = t_(n)
    x = np.tanh(1.8 * np.sin(2 * np.pi * (50 * tt - 14 * tt ** 2)) * np.exp(-tt / .45)) + hp(noise(n), 1500) * np.exp(-tt / .06) * .4
    add(sfx, x, at, g)
def tick(at, f=2400, g=.18):
    n = T(.12); tt = t_(n); add(sfx, np.sin(2 * np.pi * f * tt) * np.exp(-tt / .02), at, g)

CH = [(38, [62, 65, 69, 72, 76]), (34, [58, 62, 65, 69, 74]), (41, [60, 65, 69, 72, 76]), (36, [60, 62, 64, 67, 69])]

# --- 0-3: intro — airy pad + riser into the drop
add(mus, pad([62, 69, 72, 76], 3.3, att=1.2, rel=.3, bright=1200), 0, 1.)
n = T(1.6); tt = t_(n); add(mus, lp(noise(n), 3000) * (tt / tt[-1]) ** 3 * .35, 1.4)
for i, at in enumerate((.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5)): tick(at, 1800 + 120 * i, .06)   # letters landing
impact(3.0, .9); whoosh(3.0, .6, .4)

# --- groove sections
def groove(a, b, g=1., clap_from=None, plucks=True, bass=True, half=False):
    k = 0
    while a + k * BEAT < b - 1e-6:
        at = a + k * BEAT
        if not half or k % 2 == 0: add(mus, KICK, at, .85 * g)
        add(mus, HAT, at + BEAT / 2, .2 * g)
        if k % 2 == 1 or half: add(mus, HAT, at + BEAT * .75, .08 * g)
        if not half and (clap_from is None or at >= clap_from) and k % 4 in (1, 3): add(mus, CLAP, at, .2 * g)
        k += 1
    bar = 4 * BEAT; c = 0; at = a
    while at < b - 1e-6:
        root, notes = CH[c % 4]; e = min(at + 2 * bar, b); tt = t_(T(e - at))
        if bass:
            bs = np.sin(2 * np.pi * mtof(root) * tt) + .25 * np.sin(4 * np.pi * mtof(root) * tt)
            pump = .35 + .65 * np.minimum(1, ((tt % BEAT) / .25)) ** .6
            add(mus, np.tanh(bs * 1.2) * pump * np.minimum(1, (tt[-1] - tt) / .02 + 1e-3) * .38 * g, at)
        add(mus, pad(notes[:4], e - at, att=.2, rel=.2), at, .8 * g)
        if plucks:
            for s in range(int((e - at) / (BEAT / 2))):
                if s % 8 in (3, 7): continue
                add(mus, pluck(notes[[0, 2, 4, 1, 3, 2, 4, 1][s % 8]] + 12) * .14 * g, at + s * BEAT / 2)
        at = e; c += 1
def clack(at, g=.3, f=3200):  # metallic latch release
    n = T(.18); tt = t_(n)
    x = hp(noise(n), 2500) * np.exp(-tt / .008) + np.sin(2 * np.pi * f * tt) * np.exp(-tt / .03) * .5 + np.sin(2 * np.pi * f * 1.47 * tt) * np.exp(-tt / .02) * .3
    add(sfx, x, at, g)

# --- 3-8: hero
groove(3.0, 8.0, 1., clap_from=5.0, plucks=False)

# --- 8-18: teardown — half-time groove, scanner, latches, layer clicks, snap back
whoosh(8.0, .5, .3)
n = T(1.1); tt = t_(n); scan = np.sin(2 * np.pi * (400 * tt + 360 * tt ** 2)) * (.5 + .5 * np.sin(2 * np.pi * 14 * tt)) * np.sin(np.pi * tt / tt[-1])
add(sfx, scan, 8.2, .07)
groove(8.0, 15.9, .75, plucks=True, half=True)
whoosh(9.4, .7, .32)
for at in (9.45, 9.65, 9.85): clack(at, .22)
for at in (9.9, 10.3, 10.7, 11.0): tick(at, 2600, .1)
whoosh(11.5, .6, .3); whoosh(12.3, .5, .25)
for i in range(9): clack(12.35 + i * .2, .14, 2400 + 180 * i)
for i in range(9): tick(12.9 + i * .3, 2800, .08)
n = T(.95); tt = t_(n); add(mus, lp(noise(n), 3500) * (tt / tt[-1]) ** 3 * .4, 15.9)   # rewind riser
whoosh(16.85, .9, .45); impact(16.85, .8); clack(16.85, .45, 2000)
add(mus, pad([62, 65, 69, 72, 76], 1.3, att=.05, rel=.6, bright=1500), 16.85, .9)
for i in range(5): add(mus, pluck(86 + [0, 3, 7, 10, 12][i], .8, .25) * .07, 17.0 + i * .08)

# --- 18-23: turntable + specs
whoosh(18.0, .5, .3)
groove(18.0, 23.0, 1., plucks=True)
for at in (18.5, 19.1, 19.7, 20.3): tick(at, 2600, .12); tick(at + .45, 3200, .07)

# --- 23-24.5: the world is loud (music muffled, noise floods in) / 24.5 ANC click -> silence
i0, i1 = T(23.0), T(24.5)
groove(23.0, 24.5, .6, plucks=False)
mus[i0:i1] = np.stack([lp(mus[i0:i1, 0], 450), lp(mus[i0:i1, 1], 450)], 1)
n = i1 - i0; tt = t_(n)
city = lp(noise(n), 1800) * .5 + lp(noise(n), 200) * 1.6 + hp(noise(n), 3000) * .08 * (np.sin(2 * np.pi * 9 * tt) > .6)
for at, f in ((.2, 415), (.8, 370), (1.15, 440)):
    m = T(.35); t2 = t_(m); h = np.tanh(3 * (np.sin(2 * np.pi * f * t2) + .7 * np.sin(2 * np.pi * f * 1.26 * t2))) * np.minimum(1, (t2[-1] - t2) / .05)
    city[T(at):T(at) + m] += lp(h, 2500) * .35
add(sfx, city * np.minimum(1, tt / .15), 23.0, 1.3)
whoosh(23.0, .4, .3)
mus[T(24.5):T(27.5)] = 0; sfx[T(24.5):T(24.55)] *= np.linspace(1, 0, T(.05))[:, None]; sfx[T(24.55):T(27.1)] = 0
n = T(.05); tt = t_(n); add(sfx, np.sin(2 * np.pi * 1900 * tt) * np.exp(-tt / .005) * .7 + np.sin(2 * np.pi * 150 * tt) * np.exp(-tt / .012), 24.5, .5)
add(mus, pad([62, 65, 69, 72], 2.6, att=1.0, rel=.4, bright=1100), 25.0, .9)
for s in range(5): add(mus, pluck([74, 77, 81, 79, 76][s], 1.2, .3) * .12, 25.2 + s * .5)
n = T(.7); tt = t_(n); add(mus, lp(noise(n), 4000) * (tt / tt[-1]) ** 3 * .35, 26.8)

# --- 27.5-31: final hero, full groove
impact(27.5, 1.0)
groove(27.5, 31.0, 1.)
whoosh(31.0, .5, .35)

# --- 31: LUMARC sting — hit + shimmering chord that rings out
impact(31.0, .7)
n = T(3.5); tt = t_(n); sh = np.zeros(n, np.float32)
for m in (50, 57, 62, 66, 69, 74, 78):
    for det in (-.1, .1): sh += np.sin(2 * np.pi * mtof(m) * (1 + det / 100) * tt) * (.12 if m < 60 else .06)
sh *= np.minimum(1, tt / .03) * np.exp(-tt / 1.4)
add(mus, sh, 31.0, .9)
for i in range(6): add(mus, pluck(86 + [0, 3, 7, 10, 12, 15][i], .8, .2) * .08, 31.1 + i * .09)

mix = mus * .8 + sfx
mix[T(24.55):T(25.0)] = 0
mix[-T(.4):] *= np.linspace(1, 0, T(.4))[:, None]
mix = np.tanh(mix * 1.1) / 1.1; mix = mix / (np.abs(mix).max() + 1e-6) * .89
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', 'music.wav'],
               input=(mix * 32767).astype('<i2').tobytes())
print('ok')
