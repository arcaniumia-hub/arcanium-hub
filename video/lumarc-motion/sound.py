"""Soundtrack for the LUMARC motion graphics reel (30s, 48k stereo), synced to the cuts in anim.js.
0-4s   "before": room tone + crickets; 4-5s glitch + riser, "ASSIM?" hit
5-30s  120 BPM electronic beat in F minor; stop-hit at 9.5s (the scroll stops), whooshes on each service, final hit at 26.5s
Usage: python3 sound.py music.wav
"""
import sys, wave
import numpy as np

SR = 48000; DUR = 30.0; N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N + SR); R = np.zeros(N + SR)

def put(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), len(L) - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan))
    R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))

def tt(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    # simple IIR via cumulative trick in blocks
    b = 1 - a
    for i in range(len(x)):
        s = b * x[i] + a * s; y[i] = s
    return y

def kick(g=1.0):
    t = tt(.5); f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return g * np.sin(ph) * np.exp(-t * 7) + g * .25 * rng.standard_normal(len(t)) * np.exp(-t * 120)

def clap():
    t = tt(.3); n = rng.standard_normal(len(t))
    env = np.exp(-t * 22) + .5 * np.exp(-((t - .012) * 300) ** 2) + .4 * np.exp(-((t - .024) * 300) ** 2)
    hp = n - np.concatenate([[0], n[:-1]])
    return hp * env * .5

def hat(open_=False):
    t = tt(.25 if open_ else .06); n = rng.standard_normal(len(t))
    hp = n - np.concatenate([[0], n[:-1]])
    return hp * np.exp(-t * (14 if open_ else 70)) * .22

def sub(m, d):
    t = tt(d); env = np.minimum(1, t / .01) * np.minimum(1, (d - t) / .05)
    return (np.sin(2 * np.pi * hz(m) * t) + .3 * np.sin(4 * np.pi * hz(m) * t)) * env * .55

def pad(ms, d, g=.12):
    t = tt(d); out = np.zeros(len(t))
    for m in ms:
        for det in (-.08, 0, .08):
            f = hz(m) * 2 ** (det / 12)
            out += np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t + 1) + .15 * np.sin(6 * np.pi * f * t)
    env = np.minimum(1, t / .4) * np.minimum(1, (d - t) / .4)
    return out * env * g / len(ms)

def pluck(m, d=.35, g=.18):
    t = tt(d); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) + .25 * np.sin(6 * np.pi * f * t)
    return s * np.exp(-t * 9) * g

def boom():
    t = tt(2.5); f = 30 + 70 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    n = rng.standard_normal(len(t)) * np.exp(-t * 5) * .4
    return s + lowpass(n, 900) * 2

def riser(d):
    t = tt(d); n = rng.standard_normal(len(t))
    hp = n - np.concatenate([[0], n[:-1]])
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / d) ** 2) / SR)
    return (hp * .25 + sweep * .2) * (t / d) ** 2.2

def whoosh(d=.6):
    t = tt(d); n = rng.standard_normal(len(t))
    hp = n - np.concatenate([[0], n[:-1]])
    env = np.sin(np.pi * t / d) ** 2
    return hp * env * .3


def glitch(d):
    t = tt(d); n = rng.standard_normal(len(t))
    gate = (np.floor(t * 38) % 3 != 0).astype(float)
    crushed = np.round(n * 3) / 3
    return crushed * gate * .25 * np.sin(np.pi * t / d)

# ---- before (0-4s): room tone + crickets
room = lowpass(rng.standard_normal(int(4.5 * SR)), 300) * .25
put(room * np.minimum(1, tt(4.5) / .3) * np.clip((4.5 - tt(4.5)) / .2, 0, 1), 0, .6)
for k, at in enumerate([0.4, 1.3, 2.1, 2.9, 3.6]):
    for j in range(3):
        t = tt(.05)
        put(np.sin(2 * np.pi * 4300 * t) * np.sin(np.pi * t / .05) * .06, at + j * .07, 1, pan=.4 if k % 2 else -.4)
# ---- transition
put(glitch(.45), 4.0, 1.0)
put(riser(.75), 4.0, .7)
put(whoosh(.3), 4.45, .9)
put(boom(), 4.72, .55)
put(riser(.25), 4.75, .4)
put(boom(), 5.0, 1.0)

# ---- beat (120 BPM) in F minor: Fm - Db - Ab - Eb
BPM = 120; beat = 60 / BPM; bar = beat * 4
roots = [41, 37, 44, 39]
chords = [[53, 56, 60, 63], [49, 53, 56, 60], [56, 60, 63, 67], [51, 55, 58, 63]]
arp = [[65, 68, 72, 75], [61, 65, 68, 72], [68, 72, 75, 79], [63, 67, 70, 75]]
def silent(st): return 9.5 <= st < 9.75 or st >= 28.5
t = 5.0; b = 0
while t < 29.0:
    ci = b % 4
    put(pad(chords[ci], bar + .3, .12), t)
    for s in range(16):
        st = t + s * beat / 4
        if silent(st): continue
        intro = st < 8.0; drop = 11.0 <= st < 23.0 or st >= 26.5
        if s % 4 == 0 and (not intro or s == 0): put(kick(), st, .95)
        if not intro and s in (4, 12): put(clap(), st, .75)
        if not intro and s % 2 == 0: put(hat(), st, .7 if s % 4 else .45, pan=.25)
        if drop and s % 2 == 1: put(hat(), st, .35, pan=-.25)
        if s % 4 == 0: put(sub(roots[ci], beat * .9), st, .8)
        if drop or s % 2 == 0:
            put(pluck(arp[ci][s % 4] + (12 if drop else 0), .3, .1), st, 1, pan=-.3 if s % 2 else .3)
    t += bar; b += 1
# section hits
put(boom(), 9.5, .9); put(whoosh(.4), 9.35, .8)        # the scroll stops
for at in [8.0, 23.0]: put(whoosh(.5), at - .25, .8); put(boom(), at, .5)
put(riser(1.5), 9.5, .45); put(boom(), 11.0, .8)
for k in range(6): put(whoosh(.35), 11.0 + k * 1.5 - .15, .85)
put(riser(1.4), 21.6, .5)
put(riser(1.0), 25.5, .5); put(boom(), 26.5, 1.0)
for at in [20.3, 20.55, 20.8, 21.05, 21.3, 21.55]: put(whoosh(.2), at, .5)

mix = np.stack([L[:N], R[:N]], 1)
tt_ = np.arange(N) / SR
mix *= np.clip((DUR - tt_) / 1.5, 0, 1)[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.max(np.abs(mix)) / .89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok')
