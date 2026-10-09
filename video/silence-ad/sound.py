"""Sound design + score for the SILENCE ad -> mix.wav (48 kHz stereo, 30 s).
Inputs (cwd): clips/A1.mp4 A2.mp4 A3.mp4 (native audio), vo/0..4.mp3 (narration L1..L5)
"""
import subprocess, math
import numpy as np

SR, DUR = 48000, 30.0
N = int(SR * DUR)
BEAT = 60 / 118
C1 = 13.0; D = C1 + 16 * BEAT
rng = np.random.default_rng(3)
def T(s): return int(round(s * SR))
def t_(n): return np.arange(n) / SR
def load(path, ss=0., dur=None, tempo=1.):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(dur)] if dur else []) + ['-i', path, '-vn']
    if tempo != 1: cmd += ['-af', f'atempo={tempo}']
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
    return a.reshape(-1, 2).copy() if a.size else np.zeros((1, 2), np.float32)
def add(buf, x, at, g=1.):
    if x.ndim == 1: x = np.stack([x, x], 1)
    i = T(at); j = min(N, i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def lp(x, fc):  # one-pole lowpass (fc may be an array)
    a = np.exp(-2 * np.pi * np.broadcast_to(fc, x.shape[:1]) / SR); y = np.zeros_like(x); s = np.zeros(x.shape[1:], x.dtype)
    for n in range(len(x)): s = (1 - a[n]) * x[n] + a[n] * s; y[n] = s
    return y
def lp_fast(x, fc, passes=2):
    a = math.exp(-2 * math.pi * fc / SR)
    from itertools import accumulate
    y = x
    for _ in range(passes):
        y = np.array(list(accumulate(y, lambda s, v: (1 - a) * v + a * s)), np.float32)
    return y
def hp_fast(x, fc): return x - lp_fast(x, fc, 1)
def env(n, a, r): e = np.ones(n, np.float32); na = max(1, T(a)); e[:na] = np.linspace(0, 1, na); return e * np.exp(-t_(n) / r)
def noise(n): return rng.standard_normal(n).astype(np.float32)
def pink(n):
    w = np.fft.rfft(noise(n)); f = np.arange(len(w)) + 1; return np.fft.irfft(w / np.sqrt(f), n).astype(np.float32) * 8

sfx = np.zeros((N, 2), np.float32); mus = np.zeros((N, 2), np.float32); vo = np.zeros((N, 2), np.float32); amb = np.zeros((N, 2), np.float32)

# --- PART 1: flat room tone, nothing else
rt = lp_fast(pink(T(4.5)), 900) * .02
rt[-T(.05):] *= np.linspace(1, 0, T(.05))
add(sfx, rt, 0)
for k, at in enumerate((3.82, 3.92, 4.02)):  # stickers peeling off
    n = T(.16); x = hp_fast(noise(n), 1800) * env(n, .01, .05) * (1 + .8 * np.sign(np.sin(2 * np.pi * 90 * t_(n))))
    add(sfx, x, at, .08)

# --- THE BREAK: deep bass hit + soft whoosh + glass, then total silence
n = T(.8); tt = t_(n)
boom = np.sin(2 * np.pi * (52 * tt - 20 * tt ** 2)) * np.exp(-tt / .28) + .5 * np.sin(2 * np.pi * 34 * tt) * np.exp(-tt / .4)
boom = np.tanh(boom * 1.6) * .9; add(sfx, boom, 4.5)
n = T(.75); tt = t_(n); w = noise(n); fc = 400 + 3500 * (tt / tt[-1]) ** 2
wh = lp(w[:, None], fc)[:, 0] - lp(w[:, None], fc * .35)[:, 0]
wh *= np.sin(np.pi * tt / tt[-1]) ** 2; add(sfx, wh, 4.05, .5)
gl = np.zeros(T(.7), np.float32)
for k in range(70):
    at = rng.uniform(0, .35) ** 1.5; f = rng.uniform(2500, 9000); m = T(.12); tt = t_(m)
    s = np.sin(2 * np.pi * f * tt) * np.exp(-tt / rng.uniform(.01, .05)) * rng.uniform(.2, 1)
    i = T(at); gl[i:i + m] += s[:len(gl) - i]
gl += hp_fast(noise(len(gl)), 3000) * env(len(gl), .002, .06) * .6
add(sfx, gl, 4.5, .18)
sfx[T(5.3):T(6.0)] *= np.linspace(1, 0, T(6.0) - T(5.3))[:, None] ** 6  # sudden silence

# --- SCENE A: the noise (clip audio, escalating) + horns, rumble
CUTS = [(6.0, 7.2, 'A1', 1.0, .55), (7.2, 8.0, 'A3', .4, .7), (8.0, 8.6, 'A2', 1.2, .8),
        (8.6, 9.2, 'A1', 3.2, .9), (9.2, 9.6, 'A3', 2.4, 1.), (9.6, 10.0, 'A2', 3.2, 1.)]
for a, b, c, ss, g in CUTS:
    x = load(f'clips/{c}.mp4', ss, b - a + .03)
    if np.abs(x).max() > 0: x = x / (np.abs(x).max() + 1e-6) * .6
    m = min(len(x), T(b - a + .03)); x = x[:m]; x[:T(.006)] *= np.linspace(0, 1, T(.006))[:, None]
    add(amb, x, a, g)
n = T(4.85); tt = t_(n)
rumble = lp_fast(noise(n), 160) * 3 * (tt / tt[-1]) ** 1.5 + lp_fast(pink(n), 2500) * .12 * (tt / tt[-1]) ** 2
add(amb, rumble, 6.0, .5)
for at, f1 in ((7.22, 415), (8.62, 370), (9.25, 440), (9.62, 392)):  # car horns
    n = T(.45); tt = t_(n); h = np.tanh(3 * (np.sin(2 * np.pi * f1 * tt) + .7 * np.sin(2 * np.pi * f1 * 1.26 * tt))) * env(n, .01, .9)
    add(amb, lp_fast(h, 3000), at, .12)
for a, b in ((7.2, 8.0), (9.2, 9.6)):  # jackhammer
    n = T(b - a); tt = t_(n); jh = lp_fast(noise(n), 1500) * (np.sin(2 * np.pi * 24 * tt) > 0) * 1.4
    add(amb, jh, a, .35)
# B1: the world muffles as the headphones settle, then a click, then absolute digital silence
i0, i1 = T(10.0), T(10.86)
seg = amb[i0:i1].copy() + .25 * np.stack([lp_fast(noise(i1 - i0), 300)] * 2, 1)
fc = np.geomspace(6000, 120, i1 - i0)
seg = lp(seg, fc) * np.linspace(1, .15, i1 - i0)[:, None]
amb[i0:i1] = seg; amb[i1:] = 0
n = T(.06); tt = t_(n)
click = (np.sin(2 * np.pi * 2100 * tt) * np.exp(-tt / .004) * .5 + np.sin(2 * np.pi * 140 * tt) * np.exp(-tt / .012)
         + hp_fast(noise(n), 4000) * np.exp(-tt / .002) * .6)
add(sfx, click, 10.86, .45)
sfx[T(10.93):T(12.45)] = 0

# --- SCORE: minimal premium electronic, 118 BPM, drops exactly at 13.0
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
CH = [(38, [62, 65, 69, 72, 76]), (34, [58, 62, 65, 69, 74]), (41, [60, 65, 69, 72, 76]), (36, [60, 62, 64, 67, 69])]
BAR = 4 * BEAT
def chord_at(t): return CH[int((t - C1) // (2 * BAR)) % 4]
end_drums = 25.8
# kick
n = T(.45); tt = t_(n)
KICK = np.sin(2 * np.pi * (48 * tt + 70 * .035 * (1 - np.exp(-tt / .035)))) * np.exp(-tt / .16)
KICK = np.tanh(KICK * 1.8) * .85 + hp_fast(noise(n), 2000) * np.exp(-tt / .003) * .1
n = T(.06); HAT = hp_fast(noise(n), 7000) * np.exp(-t_(n) / .018)
n = T(.25); tt = t_(n); CLAP = hp_fast(noise(n), 1200) * (np.exp(-tt / .05) + .5 * np.exp(-np.maximum(tt - .012, 0) / .03) * (tt > .012))
side = np.ones(N, np.float32)
b = 0
while C1 + b * BEAT < end_drums - .01:
    at = C1 + b * BEAT; g = 1. if at < D else .62
    add(mus, KICK, at, .9 * g)
    i = T(at); m = min(N - i, T(.3)); side[i:i + m] = np.minimum(side[i:i + m], .35 + .65 * (t_(m) / .3) ** .6)
    add(mus, HAT, at + BEAT / 2, .22 * g, ) if True else None
    if b % 4 in (1, 3): add(mus, CLAP, at, .2 * g)
    if b % 2 == 1: add(mus, HAT, at + BEAT * .75, .09 * g)
    b += 1
# sub bass (sidechained), plucks, pad
tt_all = t_(N)
bass = np.zeros(N, np.float32); pad = np.zeros(N, np.float32); pl = np.zeros(N, np.float32)
k = 0
for c in range(4):
    a = C1 + c * 2 * BAR; e = min(a + 2 * BAR, end_drums)
    if a >= end_drums: break
    root, notes = CH[c % 4]; i, j = T(a), T(e); tt = t_(j - i)
    f = mtof(root); bs = np.sin(2 * np.pi * f * tt) + .25 * np.sin(4 * np.pi * f * tt)
    bs *= np.minimum(1, tt / .02) * np.minimum(1, (tt[-1] - tt) / .03 + .001)
    bass[i:j] += bs * .42
    for nn in notes[:4]:
        for det in (-.07, .0, .07):
            ph = 2 * np.pi * mtof(nn - 12) * (1 + det / 100) * tt
            pad[i:j] += (2 * ((ph / (2 * np.pi)) % 1) - 1) * .02
    for s in range(16):  # 8th-note plucks walking the chord
        at = a + s * BEAT / 2
        if at >= e or (s % 8) in (3, 7): continue
        nn = notes[[0, 2, 4, 1, 3, 2, 4, 1][s % 8]] + 12; m = T(.5); t2 = t_(m)
        x = (np.sin(2 * np.pi * mtof(nn) * t2) + .3 * np.sin(4 * np.pi * mtof(nn) * t2)) * np.exp(-t2 / .12) * .16
        ii = T(at); pl[ii:ii + m] += x[:N - ii]
bass = np.tanh(bass * 1.3) * side; pad = lp_fast(pad, 1400) * (.6 + .4 * side)
dl = T(BEAT * .75); plL = pl.copy(); plR = pl.copy(); plL[dl:] += pl[:-dl] * .35; plR[2 * dl:] += pl[:-2 * dl] * .25
mus[:, 0] += bass + pad + plL; mus[:, 1] += bass + pad + plR
# riser into the drop (12.45 -> 13.0) and the final sustained note
n = T(.55); tt = t_(n); rs = lp_fast(noise(n), 2500) * (tt / tt[-1]) ** 3 * .25 + np.sin(2 * np.pi * mtof(50) * tt) * (tt / tt[-1]) ** 4 * .15
add(mus, rs, 12.45)
mus[T(D):T(end_drums)] *= .8                        # music sits lower under the hero
i = T(end_drums); n = T(3.0); tt = t_(n)
sus = np.zeros(n, np.float32)
for nn in (41, 53, 60, 65, 69, 76):
    for det in (-.06, .06):
        sus += np.sin(2 * np.pi * mtof(nn) * (1 + det / 100) * tt) * (.08 if nn > 45 else .18)
sus *= np.minimum(1, tt / .05) * np.clip(1 - tt / 2.8, 0, 1) ** 1.6
add(mus, sus, end_drums, .9)
mus[:T(12.45)] = 0

# --- NARRATION (never over the 1.5 s silence)
def vo_line(i, at, tempo=1., squeeze=None):
    x = load(f'vo/{i}.mp3', tempo=tempo)
    if squeeze:  # shorten long pauses between phrases
        e = np.abs(x).max(1); win = T(.03); sm = np.convolve(e, np.ones(win) / win, 'same'); quiet = sm < .01
        keep = np.ones(len(x), bool); run = 0
        for n in range(len(x)):
            run = run + 1 if quiet[n] else 0
            if run > T(squeeze): keep[n] = False
        x = x[keep]
    s = np.argmax(np.abs(x).max(1) > .01); x = x[max(0, s - T(.02)):]
    add(vo, x, at); return len(x) / SR
spans = [(0.3, vo_line(0, 0.3)), (4.55, vo_line(1, 4.55)), (16.0, vo_line(2, 16.0)),
         (24.3, vo_line(3, 24.3, 1.1, .26)), (27.15, vo_line(4, 27.15, 1.08, .24))]
print('vo spans', [(a, round(a + d, 2)) for a, d in spans])
duck = np.ones(N, np.float32)
for a, d in spans[2:]:
    duck[T(a - .1):T(a + d + .2)] = .55
duck = np.convolve(duck, np.ones(T(.08)) / T(.08), 'same').astype(np.float32)

mix = sfx + amb * 1.8 + mus * duck[:, None] * .8 + vo * 1.15
mix[T(10.93):T(12.45)] = 0  # absolute digital silence
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-6) * .89
pcm = (mix * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', 'mix_raw.wav'], input=pcm)
print('ok')
