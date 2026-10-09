"""Trailer soundtrack for the ONYX X1 reel (30s, 48k stereo), synced to edit.py.
0-5s     cheesy slideshow muzak, tape-stop at 4.8s
5.75s    BRAAM on "THIS?"; 6.2-7.0 flip-book ticks into the ONYX logo hit (6.95s)
7.6-27.4 trailer: low string ostinato + taiko drums, braams on the title cards, hits on cuts,
         silence before the impact, final braam on the product title; LUMARC hit at 27.4s
Usage: python3 sound.py music.wav
"""
import sys, wave
import numpy as np

SR = 48000; DUR = 30.0; N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N + 4 * SR); R = np.zeros(N + 4 * SR)
def put(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), len(L) - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan)); R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))
def tt(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def onepole(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape); a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def saw(f, t): return 2 * ((f * t) % 1) - 1
def braam(m, d=2.6, g=1.0):
    t = tt(d); x = sum(saw(hz(m + o) * (1 + det), t) for o in (0, -12, 7) for det in (-.004, 0, .004)) / 9
    fc = 200 + 2600 * np.exp(-t * 1.6) * np.minimum(1, t / .05)
    env = np.minimum(1, t / .03) * np.exp(-t * .9)
    return onepole(x, fc) * env * g * 1.6
def boom(d=2.5):
    t = tt(d); f = 28 + 80 * np.exp(-t * 7)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5) + onepole(rng.standard_normal(len(t)), 600) * np.exp(-t * 6) * 1.5)
def taiko(g=1.0):
    t = tt(.9); f = 55 + 70 * np.exp(-t * 18)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) + onepole(rng.standard_normal(len(t)), 900) * np.exp(-t * 30) * .8) * g
def hit(): t = tt(1.2); return onepole(rng.standard_normal(len(t)), 3000) * np.exp(-t * 8) * .8 + boom(1.2) * .6
def riser(d):
    t = tt(d); n = rng.standard_normal(len(t)); hp = n - np.concatenate([[0], n[:-1]])
    return (hp * .25 + np.sin(2 * np.pi * np.cumsum(150 + 2400 * (t / d) ** 2) / SR) * .2) * (t / d) ** 2.4
def whoosh(d=.5):
    t = tt(d); n = rng.standard_normal(len(t)); hp = n - np.concatenate([[0], n[:-1]]); return hp * np.sin(np.pi * t / d) ** 2 * .35
def tick(): t = tt(.04); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * .3
def pad(ms, d, g):
    t = tt(d); x = sum(np.sin(2 * np.pi * hz(m) * t * (1 + .002 * np.sin(2 * np.pi * 5 * t + m))) for m in ms) / len(ms)
    return x * np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0) * g

# ---- 0-5s muzak (tinny square lead + soft chords), tape-stop at 4.8
bpm = 112; b = 60 / bpm
mel = [72, 74, 76, 79, 76, 74, 72, 67, 69, 72, 74, 72, 76, 74, 72, 71, 72]
for i, m in enumerate(mel):
    st = .15 + i * b / 2
    if st > 4.8: break
    t = tt(b / 2 * .9); sq = np.sign(np.sin(2 * np.pi * hz(m) * t)) * np.exp(-t * 4) * .07
    put(onepole(sq, 2500), st, 1, pan=.2)
for k, ch in enumerate([[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]):
    put(pad(ch, b * 4 + .3, .09), .15 + k * b * 4)
# tape stop: pitch-dropping tone + noise
t = tt(.35); put(np.sin(2 * np.pi * np.cumsum(400 * (1 - t / .35) ** 2 + 30) / SR) * (1 - t / .35) * .25, 4.8)
# ---- the turn
put(riser(.6), 5.15, .5); put(braam(33), 5.75, 1.0); put(boom(), 5.75, .9)
for i in range(11): put(tick(), 6.2 + i * .066 * (1 - i * .03), 1, pan=(-.3 if i % 2 else .3)); put(whoosh(.12), 6.2 + i * .066, .4)
put(riser(.75), 6.2, .6); put(hit(), 6.95, .9); put(braam(38, 2.0, .6), 6.95)
# ---- trailer bed 7.6-27.4: D minor ostinato + taiko
bpm = 120; b = 60 / bpm
roots = [38, 34, 41, 36]  # D, Bb, F, C (low)
def silent(st): return 23.4 <= st < 23.6 or 24.0 <= st < 24.62 or st >= 27.3
t0 = 7.6; i = 0
while t0 + i * b / 2 < 27.4:
    st = t0 + i * b / 2; bar = int((st - t0) / (b * 4)); root = roots[bar % 4]
    if not silent(st):
        tt_ = tt(b / 2 * .85); x = (saw(hz(root + 12), tt_) + saw(hz(root + 12) * 1.003, tt_)) / 2
        put(onepole(x, 900) * np.exp(-tt_ * 6) * .22, st, 1, pan=(.25 if i % 2 else -.25))
        intense = st >= 15.9
        if i % 4 == 0: put(taiko(1.0 if intense else .7), st)
        if intense and i % 4 == 2: put(taiko(.6), st)
        if st >= 20.6 and i % 2 == 1: put(taiko(.35), st, 1, pan=.3)
    i += 1
put(pad([50, 53, 57, 62], 19.8, .07), 7.6)
for at in [7.6, 12.9, 15.9, 20.6, 25.8]: put(hit(), at, .8)
put(boom(), 9.85, .6)
for at, m in [(12.1, 33), (19.9, 31)]: put(whoosh(.4), at - .3, .8); put(braam(m), at, 1.0); put(boom(), at, .7)
for at in [13.4, 16.5, 17.7, 18.9]: put(whoosh(.3), at - .1, .6); put(tick(), at, 2)
put(riser(1.2), 22.4, .6); put(boom(), 23.6, .8)
put(riser(.6), 24.0, .7); put(boom(3.5), 24.65, 1.4); put(braam(26, 2.4, .7), 24.65)
put(braam(33, 3.0, 1.0), 25.8); put(pad([62, 65, 69, 74], 2.6, .1), 25.8)
put(riser(.6), 26.8, .4); put(hit(), 27.4, .9)
put(pad([50, 57, 62, 65], 2.6, .07), 27.4)

mix = np.stack([L[:N], R[:N]], 1); tm = np.arange(N) / SR
mix *= np.clip((DUR - tm) / 1.2, 0, 1)[:, None]
mix = np.tanh(mix * 1.3) / np.tanh(1.3); mix /= np.max(np.abs(mix)) / .89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok')
