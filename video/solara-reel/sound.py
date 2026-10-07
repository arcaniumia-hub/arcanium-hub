"""Soundtrack for the SOLARA before/after reel (30s, 48k stereo).
0-4s   "before": dull room tone + crickets
3-5s   riser into a big impact at 5.0s
5-30s  cinematic trap beat in F# minor, building at 10s, full at 15s, drop at 20s
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

# ---- "before": room tone + crickets (0-4s)
room = lowpass(rng.standard_normal(int(4.2 * SR)), 300) * .25
put(room * np.minimum(1, tt(4.2) / .3) * np.clip((4.2 - tt(4.2)) / .3, 0, 1), 0, .6)
for k, at in enumerate([0.5, 1.4, 2.2, 3.0]):
    for j in range(3):
        t = tt(.05)
        chirp = np.sin(2 * np.pi * 4300 * t) * np.sin(np.pi * t / .05) * .06
        put(chirp, at + j * .07, 1, pan=.4 if k % 2 else -.4)

# ---- transition
put(riser(1.6), 3.4, .9)
put(whoosh(.5), 4.0, 1.0)
put(boom(), 5.0, 1.0)

# ---- beat (BPM 100), F# minor: F#m - D - A - E
BPM = 100; beat = 60 / BPM; bar = beat * 4
roots = [42, 38, 45, 40]                       # F#2 D2 A2 E2
chords = [[54, 57, 61, 64], [50, 54, 57, 61], [57, 61, 64, 68], [52, 56, 59, 64]]
arp = [[66, 69, 73, 76], [62, 66, 69, 73], [69, 73, 76, 80], [64, 68, 71, 76]]
start = 5.0
t = start; b = 0
while t < 29.5:
    ci = b % 4
    sec = t
    full = sec >= 15.0
    build = sec >= 10.0
    put(pad(chords[ci], bar + .3, .14 if full else .11), t)
    put(sub(roots[ci], bar * .95), t, .9 if build else .55)
    for s in range(16):                         # 16th grid
        st = t + s * beat / 4
        if st >= 29.6: break
        if build and s in (0, 6, 10) or (not build and s == 0):
            put(kick(), st, .9)
        if full and s in (4, 12):
            put(clap(), st, .8)
        if full and s % 2 == 0:
            put(hat(), st, .8 if s % 4 else .5, pan=.25)
        if full and s in (14,):
            put(hat(True), st, .6, pan=-.25)
        if (build and s % 2 == 0) or (not build and s % 4 == 0):
            put(pluck(arp[ci][(s // 2) % 4] + (12 if sec >= 20 else 0), .4, .12), st, 1, pan=-.3 if s % 4 else .3)
    t += bar; b += 1

# section hits
put(boom(), 15.0, .7)
put(riser(1.4), 18.6, .6)
put(boom(), 20.0, .9)
put(riser(1.0), 24.0, .5)
put(boom(), 25.0, .8)
# word pops (whoosh ticks)
for at in [15.4, 16.5, 17.6, 18.7, 21.0, 25.3, 25.9, 27.0]:
    put(whoosh(.35), at - .12, .7)

mix = np.stack([L[:N], R[:N]], 1)
tt_ = np.arange(N) / SR
mix *= np.clip((DUR - tt_) / 1.8, 0, 1)[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.max(np.abs(mix)) / .89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok')
