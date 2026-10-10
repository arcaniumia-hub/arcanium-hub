"""Synth + sound-design toolkit for the SILENCE ONE hyper edit (numpy + scipy). 48 kHz, stereo float32.

Typical use in score.py:
    from lib import *
    mix = Mix(DUR)                       # stems: mix.bus('drums'), ...
    mix.add('drums', kick(), at=b(16))   # at = seconds; b(n) converts beats (150 BPM) to seconds
    ...
    mix.render('music.wav')              # sums stems, glue-compresses, limits, normalizes to -14 LUFS-ish (peak -1 dBFS)

Every generator returns a mono (n,) or stereo (n,2) float32 array; Mix.add() accepts either and pans mono.
"""
import math, subprocess
import numpy as np
from scipy import signal

SR = 48000
BPM = 150
BEAT = 60 / BPM          # 0.4 s
BAR = 4 * BEAT
rng = np.random.default_rng(1234)

def b(beats):            # beats -> seconds
    return beats * BEAT
def T(sec):              # seconds -> samples
    return int(round(sec * SR))
def tt(n):
    return np.arange(n, dtype=np.float32) / SR
def noise(n):
    return rng.standard_normal(n).astype(np.float32)
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)
NOTE = {n: i for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def note(name):          # 'A2', 'C#4' -> midi
    return NOTE[name[:-1]] + 12 * (int(name[-1]) + 1)

# ------------------------------------------------------------------ filters / utilities
def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * .45), 'low', fs=SR, output='sos'); return signal.sosfilt(sos, x, axis=0).astype(np.float32)
def hp(x, fc, order=2):
    sos = signal.butter(order, max(fc, 10), 'high', fs=SR, output='sos'); return signal.sosfilt(sos, x, axis=0).astype(np.float32)
def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [max(lo, 10), min(hi, SR * .45)], 'band', fs=SR, output='sos'); return signal.sosfilt(sos, x, axis=0).astype(np.float32)
def sweep_lp(x, f0, f1, curve=2.0):
    """time-varying one-pole-cascade lowpass from f0 to f1 (Hz) across the buffer (cheap 'filter sweep')."""
    n = len(x); k = (np.linspace(0, 1, n) ** curve); fc = f0 * (f1 / f0) ** k
    a = np.exp(-2 * np.pi * fc / SR).astype(np.float32)
    y = x.astype(np.float32).copy()
    for _ in range(2):
        out = np.empty_like(y); s = np.zeros(y.shape[1:], np.float32)
        for i in range(n):                       # python loop: keep sweeps short (< ~3 s)
            s = (1 - a[i]) * y[i] + a[i] * s; out[i] = s
        y = out
    return y
def env_adsr(n, a=.005, d=.1, s=.7, r=.2):
    e = np.ones(n, np.float32) * s; A, D, R = T(a), T(d), T(r)
    A = min(A, n); e[:A] = np.linspace(0, 1, A); D = min(D, n - A); e[A:A + D] = np.linspace(1, s, D)
    if R > 0 and n > R: e[n - R:] *= np.linspace(1, 0, R)
    return e
def exp_env(n, decay):
    return np.exp(-tt(n) / decay).astype(np.float32)
def fade(x, fin=.002, fout=.01):
    x = x.copy(); a, z = T(fin), T(fout)
    if a: x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if z: x[-z:] *= np.linspace(1, 0, z)[:, None] if x.ndim == 2 else np.linspace(1, 0, z)
    return x
def stereo(x, pan=0.0, width=0.0, delay_ms=0.0):
    """mono -> stereo with constant-power pan (-1..1) and optional Haas width."""
    if x.ndim == 2: return x
    l = x * math.cos((pan + 1) * math.pi / 4); r = x * math.sin((pan + 1) * math.pi / 4)
    if width > 0:
        d = T(delay_ms / 1000 if delay_ms else .012)
        r = np.concatenate([np.zeros(d, np.float32), r[:-d]]) * (1 - width * .3) + r * width * .3 if d else r
    return np.stack([l, r], 1).astype(np.float32)
def sat(x, drive=2.0):
    return (np.tanh(x * drive) / np.tanh(drive)).astype(np.float32)
def reverb(x, size=1.6, mix=.25, damp=6000, predelay=.015):
    """convolution with a decaying stereo noise impulse response."""
    n = T(size); t = tt(n); ir = np.stack([noise(n), noise(n)], 1) * np.exp(-t * 6.9 / size)[:, None]
    ir = lp(ir, damp); ir[:T(predelay)] = 0; ir /= np.sqrt((ir ** 2).sum(0, keepdims=True)) + 1e-9
    xs = stereo(x) if x.ndim == 1 else x
    wet = np.stack([signal.fftconvolve(xs[:, c], ir[:, c])[:len(xs)] for c in range(2)], 1).astype(np.float32)
    return xs * (1 - mix) + wet * mix * 2.5
def delay(x, time, fb=.35, mix=.3, pingpong=True):
    xs = stereo(x) if x.ndim == 1 else x.copy(); d = T(time); out = xs.copy(); tap = xs.copy()
    for k in range(1, 8):
        tap = np.concatenate([np.zeros((d, 2), np.float32), tap[:-d]]) * fb
        if pingpong: tap = tap[:, ::-1]
        out += tap * mix / fb
        if np.abs(tap).max() < 1e-4: break
    return out
def pitch_env(f0, f1, n, decay):
    """frequency trajectory f0 -> f1 with exponential decay; returns phase (radians)."""
    f = f1 + (f0 - f1) * np.exp(-tt(n) / decay); return 2 * np.pi * np.cumsum(f) / SR

# ------------------------------------------------------------------ oscillators
def osc(kind, freq, n, phase0=0.0):
    """freq can be scalar or array of length n. kinds: sine, saw, square, tri."""
    f = np.broadcast_to(np.asarray(freq, np.float32), (n,))
    ph = (phase0 + np.cumsum(f) / SR) % 1.0
    if kind == 'sine': return np.sin(2 * np.pi * ph).astype(np.float32)
    if kind == 'saw': return (2 * ph - 1).astype(np.float32)
    if kind == 'square': return np.where(ph < .5, 1.0, -1.0).astype(np.float32)
    if kind == 'tri': return (4 * np.abs(ph - .5) - 1).astype(np.float32)
    raise ValueError(kind)
def supersaw(freq, n, voices=7, detune=.25):
    out = np.zeros(n, np.float32)
    for v in range(voices):
        d = (v - (voices - 1) / 2) / ((voices - 1) / 2 or 1) * detune   # semitones
        out += osc('saw', freq * 2 ** (d / 12), n, rng.random())
    return out / voices

# ------------------------------------------------------------------ drums
def kick(dur=.55, punch=1.0, f0=150, f1=44, decay=.2, click=.15):
    n = T(dur); t = tt(n)
    body = np.sin(pitch_env(f0, f1, n, .035)) * np.exp(-t / decay)
    cl = hp(noise(n), 3000) * np.exp(-t / .003) * click
    return sat(body * punch + cl, 1.6) * .95
def sub808(midi, dur=.9, glide_from=None, drive=2.2):
    n = T(dur); t = tt(n); f = mtof(midi)
    fr = f if glide_from is None else mtof(midi) + (mtof(glide_from) - f) * np.exp(-t / .06)
    x = osc('sine', fr, n) * env_adsr(n, .002, .3, .65, .12)
    return sat(x, drive) * .9
def snare(dur=.3, tone=190, crack=1.0):
    n = T(dur); t = tt(n)
    body = np.sin(2 * np.pi * tone * t) * np.exp(-t / .07) * .6
    nz = bp(noise(n), 1500, 9000) * np.exp(-t / .09) * crack
    return sat(body + nz, 1.4) * .8
def clap(dur=.3):
    n = T(dur); t = tt(n); x = bp(noise(n), 900, 7000)
    e = np.zeros(n, np.float32)
    for k, off in enumerate((0, .011, .022)): e += np.exp(-np.maximum(t - off, 0) / (.008 if k < 2 else .07)) * (t >= off)
    return x * e * .7
def hat(dur=.06, open_=False):
    n = T(.35 if open_ else dur); t = tt(n)
    return hp(noise(n), 7500) * np.exp(-t / (.12 if open_ else .018)) * .5
def rim(dur=.08):
    n = T(dur); t = tt(n); return (np.sin(2 * np.pi * 1700 * t) * .6 + hp(noise(n), 4000) * .5) * np.exp(-t / .012)
def taiko(dur=1.2):
    n = T(dur); t = tt(n)
    x = np.sin(pitch_env(110, 52, n, .08)) * np.exp(-t / .35) + lp(noise(n), 900) * np.exp(-t / .05) * .6
    return reverb(sat(x, 1.5), 1.4, .3)

# ------------------------------------------------------------------ cinematic / sound design
def braam(midi=note('D2'), dur=2.4, bright=1.0):
    """detuned brass-ish saw stack with filter bloom (Inception horn)."""
    n = T(dur); t = tt(n)
    x = sum(supersaw(mtof(midi + o), n, 5, .18) * g for o, g in ((0, 1), (12, .5), (7, .35), (-12, .6)))
    x = sweep_lp(x, 220, 2200 * bright, 1.3) if dur <= 3.5 else lp(x, 1600 * bright)
    x = sat(x * env_adsr(n, .06, .5, .8, .6), 2.2)
    return reverb(x, 2.2, .3)
def impact(dur=2.0, sub=1.0, crack=.8, tail=.4):
    """trailer hit: sub drop + noise crack + metallic tail."""
    n = T(dur); t = tt(n)
    s = np.sin(pitch_env(90, 32, n, .25)) * np.exp(-t / .55) * sub
    c = hp(noise(n), 1200) * np.exp(-t / .045) * crack
    m = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) for f in (523, 787, 1131, 1666)) * np.exp(-t / .5) * .05 * tail
    return reverb(sat(s + c + m, 1.8), 2.5, .28)
def riser(dur=2.0, f0=200, f1=4000, noise_amt=1.0, tone_amt=.4):
    n = T(dur); t = tt(n); k = (t / t[-1]) ** 2
    nz = bp(noise(n), 300, 9000) * k * noise_amt
    tone = osc('saw', f0 * (f1 / f0) ** (t / t[-1]), n) * tone_amt * k
    return reverb(stereo(lp(nz + tone, 9000) * .5, 0, .6), 1.2, .2)
def downlifter(dur=1.5):
    n = T(dur); t = tt(n); k = 1 - t / t[-1]
    return reverb(stereo(bp(noise(n), 200, 6000) * k ** 2 * .6 + osc('sine', 900 * k + 60, n) * k * .2, 0, .5), 1.2, .25)
def whoosh(dur=.6, peak=.6, up=True):
    """noise swell; the loudest point is at `peak` fraction (place at = cut_time - dur*peak)."""
    n = T(dur); t = tt(n) / (dur); e = np.where(t < peak, (t / peak) ** 2, ((1 - t) / (1 - peak)) ** 1.5)
    x = bp(noise(n), 250, 5000) * e
    return stereo(x * .8, 0, .7)
def reverse_cymbal(dur=1.6):
    n = T(dur); t = tt(n); x = hp(noise(n), 4000) * np.exp(-(t[-1] - t) / .5)
    return stereo(x * .5, 0, .8)
def tape_stop(x, dur=None, curve=2.0):
    """slow a buffer down to a halt (pitch + speed drop). x: mono or stereo."""
    xs = stereo(x) if x.ndim == 1 else x; n = len(xs) if dur is None else min(len(xs), T(dur))
    rate = (1 - np.linspace(0, 1, n)) ** curve; pos = np.cumsum(rate); pos = pos[pos < len(xs) - 1]
    out = np.stack([np.interp(pos, np.arange(len(xs)), xs[:, c]) for c in range(2)], 1).astype(np.float32)
    return fade(out, 0, .05)
def stutter(x, slice_sec, repeats, decay=1.0):
    """repeat the first slice of x `repeats` times (glitch stutter)."""
    s = x[:T(slice_sec)]; out = np.concatenate([s * (decay ** i) for i in range(repeats)])
    return fade(out, .001, .003)
def bitcrush(x, bits=6, down=8):
    y = np.round(x * 2 ** bits) / 2 ** bits; return np.repeat(y[::down], down, axis=0)[:len(x)].astype(np.float32)
def scratch(dur=.45):
    """record scratch: noisy formant sweeping up and back."""
    n = T(dur); t = tt(n) / dur; f = 300 + 2200 * np.sin(np.pi * t) ** 1.5
    x = osc('saw', f, n) * .4 + bp(noise(n), 800, 5000) * .6
    return sat(bp(x, 300, 6000) * np.sin(np.pi * t) ** .5, 2.0) * .6
def vinyl(dur):
    n = T(dur); x = lp(noise(n), 3000) * .01
    pops = (rng.random(n) > .9996).astype(np.float32) * rng.standard_normal(n).astype(np.float32) * .4
    return x + lp(pops, 2500)
def glitch_burst(dur=.3, seed=0):
    r = np.random.default_rng(seed); n = T(dur); out = np.zeros(n, np.float32); i = 0
    while i < n:
        L = T(r.choice([.01, .02, .03, .045])); kind = r.integers(3)
        seg = (osc('square', r.uniform(200, 3000), L) if kind == 0 else bp(noise(L), 1000, 8000) if kind == 1 else osc('saw', r.uniform(60, 400), L)) * r.uniform(.2, .6)
        out[i:i + L] = seg[:n - i]; i += L
    return out
def tick(f=2600, dur=.08, g=.4):
    n = T(dur); return np.sin(2 * np.pi * f * tt(n)) * exp_env(n, .012) * g
def shimmer(midis, dur=3.0, decay=1.2):
    n = T(dur); t = tt(n); x = np.zeros(n, np.float32)
    for m in midis:
        for d in (-.08, .08): x += np.sin(2 * np.pi * mtof(m) * (1 + d / 100) * t) * (1 / len(midis))
    return reverb(x * np.minimum(1, t / .02) * np.exp(-t / decay), 3.0, .4)

# ------------------------------------------------------------------ instruments
def pluck(midi, dur=.5, decay=.15, bright=1.0):
    n = T(dur); t = tt(n); f = mtof(midi)
    x = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) * bright + .12 * np.sin(6 * np.pi * f * t) * bright
    return x * exp_env(n, decay) * .5
def ukulele(midi, dur=.6):
    """Karplus-Strong string — the cheesy stock-music BEFORE."""
    f = mtof(midi); N = int(SR / f); buf = (rng.random(N) * 2 - 1).astype(np.float32); n = T(dur); out = np.zeros(n, np.float32)
    for i in range(n):
        out[i] = buf[i % N]; buf[i % N] = .5 * (buf[i % N] + buf[(i + 1) % N]) * .996
    return lp(out, 5000) * .6
def glock(midi, dur=.8):
    n = T(dur); t = tt(n); f = mtof(midi)
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .1)) * np.exp(-t / .35) * .35
def pad(midis, dur, att=.4, rel=.6, bright=1800, detune=.15):
    n = T(dur); x = sum(supersaw(mtof(m), n, 5, detune) for m in midis) / max(1, len(midis))
    return stereo(lp(x, bright) * env_adsr(n, att, .2, 1, rel) * .6, 0, .6)
def lead(midi, dur, bright=3500, vib=.15):
    n = T(dur); t = tt(n); f = mtof(midi) * (1 + vib / 100 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / .3))
    x = supersaw(f, n, 5, .12) * .7 + osc('square', f / 2, n) * .2
    return lp(x, bright) * env_adsr(n, .01, .15, .75, .12) * .5
def reese(midi, dur, bright=900):
    n = T(dur); x = osc('saw', mtof(midi) * 1.004, n) + osc('saw', mtof(midi) * .996, n)
    return sat(lp(x, bright), 2.5) * env_adsr(n, .005, .1, .9, .06) * .5

# ------------------------------------------------------------------ mixing
class Mix:
    def __init__(self, dur):
        self.dur = dur; self.n = T(dur); self.stems = {}; self.ducks = []
    def bus(self, name):
        if name not in self.stems: self.stems[name] = np.zeros((self.n, 2), np.float32)
        return self.stems[name]
    def add(self, stem, x, at, gain=1.0, pan=0.0):
        buf = self.bus(stem); xs = stereo(np.asarray(x, np.float32), pan); i = T(at)
        if i >= self.n or i + len(xs) <= 0: return
        if i < 0: xs = xs[-i:]; i = 0
        j = min(self.n, i + len(xs)); buf[i:j] += xs[:j - i] * gain
    def silence(self, start, end, stems=None, fade_ms=4):
        """hard digital silence on the given stems (all if None) between start and end seconds."""
        i, j, f = T(start), T(end), T(fade_ms / 1000)
        for k, buf in self.stems.items():
            if stems and k not in stems: continue
            if f: buf[max(0, i - f):i] *= np.linspace(1, 0, min(f, i))[:, None]
            buf[i:j] = 0
    def sidechain(self, target, times, depth=.6, release=.18):
        """duck a stem at each time (kick pump)."""
        g = np.ones(self.n, np.float32)
        for at in times:
            i = T(at); m = min(self.n - i, T(release * 3))
            if m > 0: g[i:i + m] = np.minimum(g[i:i + m], 1 - depth * np.exp(-tt(m) / release))
        self.bus(target)[:] *= g[:, None]
    def filter_range(self, stem, start, end, kind='lp', fc=500):
        i, j = T(start), T(end); buf = self.bus(stem)
        buf[i:j] = (lp if kind == 'lp' else hp)(buf[i:j], fc)
    def render(self, path, gains=None, target_peak=.89, keep_silence=()):
        gains = gains or {}
        mix = sum(buf * gains.get(k, 1.0) for k, buf in self.stems.items())
        # glue: gentle soft clip + peak normalize
        mix = np.tanh(mix * 1.2) / 1.2
        mix = mix / (np.abs(mix).max() + 1e-9) * target_peak
        for a, z in keep_silence: mix[T(a):T(z)] = 0
        mix[-T(.3):] *= np.linspace(1, 0, T(.3))[:, None]
        pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2').tobytes()
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm, check=True)
        return mix
