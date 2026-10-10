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
def _polyblep(ph, dt):
    """band-limited step correction (PolyBLEP) -> far less aliasing on saw/square leads."""
    y = np.zeros_like(ph)
    m = ph < dt; x = ph[m] / dt[m]; y[m] = 2 * x - x * x - 1
    m = ph > 1 - dt; x = (ph[m] - 1) / dt[m]; y[m] = x * x + 2 * x + 1
    return y
def osc(kind, freq, n, phase0=0.0):
    """freq can be scalar or array of length n. kinds: sine, saw, square, tri."""
    f = np.broadcast_to(np.asarray(freq, np.float32), (n,))
    ph = (phase0 + np.cumsum(f) / SR) % 1.0
    if kind == 'sine': return np.sin(2 * np.pi * ph).astype(np.float32)
    dt = np.clip(np.abs(f) / SR, 1e-6, .5)
    if kind == 'saw': return (2 * ph - 1 - _polyblep(ph, dt)).astype(np.float32)
    if kind == 'square': return (np.where(ph < .5, 1.0, -1.0) + _polyblep(ph, dt) - _polyblep((ph + .5) % 1.0, dt)).astype(np.float32)
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


# ====================================================================== additions for score.py (hyper edit)
from scipy.ndimage import minimum_filter1d, uniform_filter1d

def db(x):                  # dB -> linear gain
    return 10 ** (x / 20)
def to_db(x):
    return 20 * np.log10(np.maximum(x, 1e-12))
def as_st(x):
    return stereo(np.asarray(x, np.float32)) if np.ndim(x) == 1 else np.asarray(x, np.float32)
def pad_to(x, n):
    if len(x) >= n: return x[:n]
    z = np.zeros((n - len(x),) + x.shape[1:], np.float32); return np.concatenate([x, z])
def rev(x):
    return np.ascontiguousarray(x[::-1])
def pink(n):
    """pink noise (Paul Kellet-style 1/f approximation via IIR)."""
    w = noise(n)
    bz = [0.049922035, -0.095993537, 0.050612699, -0.004408786]; az = [1, -2.494956002, 2.017265875, -0.522189400]
    y = signal.lfilter(bz, az, w).astype(np.float32); return y / (np.std(y) + 1e-9) * .3

def tv_lp(x, fc, block=96, order=2, kind='low'):
    """time-varying Butterworth filter: fc is a scalar or a per-sample array (Hz). State carried block to block."""
    xs = np.asarray(x, np.float32); n = len(xs); fc = np.broadcast_to(np.asarray(fc, np.float64), (n,))
    out = np.empty_like(xs); zi = None
    for i in range(0, n, block):
        f = float(np.clip(fc[min(n - 1, i + block // 2)], 12, SR * .45))
        sos = signal.butter(order, f, kind, fs=SR, output='sos')
        if zi is None: zi = np.zeros((sos.shape[0], 2) + xs.shape[1:], np.float64)
        seg = xs[i:i + block]
        y, zi = signal.sosfilt(sos, seg, axis=0, zi=zi); out[i:i + block] = y
    return out
def tv_bp(x, fc, q=4.0, block=96):
    """time-varying resonant band-pass (RBJ biquad, constant peak gain) with per-sample centre fc."""
    xs = np.asarray(x, np.float32); n = len(xs); fc = np.broadcast_to(np.asarray(fc, np.float64), (n,))
    out = np.empty_like(xs); zi = np.zeros((1, 2) + xs.shape[1:], np.float64)
    for i in range(0, n, block):
        f = float(np.clip(fc[min(n - 1, i + block // 2)], 20, SR * .45)); w0 = 2 * np.pi * f / SR; al = np.sin(w0) / (2 * q)
        bq = np.array([al, 0, -al]); aq = np.array([1 + al, -2 * np.cos(w0), 1 - al])
        sos = np.concatenate([bq / aq[0], aq / aq[0]])[None]
        y, zi = signal.sosfilt(sos, xs[i:i + block], axis=0, zi=zi); out[i:i + block] = y
    return out

def varispeed(x, rate, n_out=None):
    """read x at a time-varying playback rate (array per output sample, or scalar). pitch+speed change (tape)."""
    xs = np.asarray(x, np.float32); n_out = n_out or (len(rate) if np.ndim(rate) else len(xs))
    r = np.broadcast_to(np.asarray(rate, np.float64), (n_out,)); pos = np.concatenate([[0], np.cumsum(r)[:-1]])
    pos = np.clip(pos, 0, len(xs) - 1)
    if xs.ndim == 1: return np.interp(pos, np.arange(len(xs)), xs).astype(np.float32)
    return np.stack([np.interp(pos, np.arange(len(xs)), xs[:, c]) for c in range(xs.shape[1])], 1).astype(np.float32)

def pan_curve(x, pan):
    """mono -> stereo with a per-sample constant-power pan (-1..1)."""
    x = np.asarray(x, np.float32); p = np.broadcast_to(np.asarray(pan, np.float32), x.shape)
    a = (p + 1) * np.pi / 4; return np.stack([x * np.cos(a), x * np.sin(a)], 1).astype(np.float32)
def width(x, w):
    """mid/side width scale (0 = mono, 1 = unchanged)."""
    x = as_st(x); m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1).astype(np.float32)

def ks(midi, dur=.8, bright=.6, decay=.996, pluck_pos=.3):
    """vectorised Karplus-Strong string (IIR comb via lfilter) -> fast ukulele / guitar / pluck."""
    f = mtof(midi); N = max(2, int(round(SR / f - .5))); n = T(dur)
    exc = (rng.random(N) * 2 - 1).astype(np.float32)
    exc = lp(exc, 800 + 9000 * bright, 1)
    k = int(N * pluck_pos); exc = exc - np.roll(exc, k) * .6              # pluck position comb
    x = np.zeros(n, np.float32); x[:N] = exc[:n]
    a = np.zeros(N + 2); a[0] = 1; a[N] = -.5 * decay; a[N + 1] = -.5 * decay
    y = signal.lfilter([1.0], a, x).astype(np.float32)
    return fade(y / (np.abs(y).max() + 1e-9) * .5, .0005, .02)
def strum(midis, dur=.4, spread=.012, down=True, vel=1.0, bright=.6):
    order = midis if down else midis[::-1]; n = T(dur + spread * len(midis)); out = np.zeros(n, np.float32)
    for i, m in enumerate(order):
        s = ks(m, dur, bright) * vel * (1 - .08 * i); j = T(spread * i); out[j:j + len(s)] += s[:n - j]
    return out / max(1, len(midis)) * 1.6

def bell(midi, dur=3.0, decay=1.4, bright=1.0):
    """struck bell / ring 'TING': inharmonic partials with individual decays."""
    n = T(dur); t = tt(n); f = mtof(midi); x = np.zeros(n, np.float32)
    for r, g, d in ((.5, .35, 1.6), (1, 1, 1), (1.19, .45, .7), (1.5, .3, .5), (2.0, .5 * bright, .45), (2.74, .3 * bright, .25), (3.76, .2 * bright, .15), (5.4, .12 * bright, .08)):
        if f * r < SR * .4: x += np.sin(2 * np.pi * f * r * t + rng.random() * 6) * g * np.exp(-t / (decay * d))
    x *= np.minimum(1, t / .002); return x * .25
def metal(f0=900, dur=.9, decay=.35, ratios=(1, 1.47, 2.09, 2.56, 3.39, 4.17)):
    """metallic 'shing' / clank partial cluster."""
    n = T(dur); t = tt(n); x = sum(np.sin(2 * np.pi * f0 * r * t + rng.random() * 6) * np.exp(-t / (decay / (1 + .4 * i))) / (1 + .5 * i) for i, r in enumerate(ratios))
    return (x * np.minimum(1, t / .001) * .3).astype(np.float32)
def shing(f0=1400, dur=.9):
    n = T(dur); t = tt(n); sw = hp(noise(n), 3000) * np.exp(-t / .05) * .35
    return lp(metal(f0, dur, .4) + sw, 11000)
def crash(dur=2.2, bright=1.0):
    n = T(dur); t = tt(n)
    x = bp(noise(n), 3500, 11000) * np.exp(-t / .7) + hp(noise(n), 6000) * np.exp(-t / .12) * .5
    x = x * (1 + .3 * metal(3100, dur, .6)[: n] * 3)
    return lp(stereo(x * .35 * bright, 0, .8, 9), 12000)
def ride(dur=.9):
    n = T(dur); t = tt(n); return lp(hp(noise(n), 5000) * np.exp(-t / .25) * .18 + metal(2400, dur, .5, (1, 1.33, 1.71, 2.21)) * .45, 11000)
def tom(midi=note('A2'), dur=.45):
    n = T(dur); t = tt(n); f = mtof(midi)
    x = np.sin(pitch_env(f * 1.6, f, n, .03)) * np.exp(-t / .16) + bp(noise(n), 200, 2500) * np.exp(-t / .02) * .4
    return sat(x, 1.5) * .7
def shaker(dur=.08, accent=1.0):
    n = T(dur); t = tt(n); e = np.minimum(1, t / .008) * np.exp(-t / .02)
    return bp(noise(n), 4500, 10000) * e * .4 * accent
def click(f=3000, dur=.04, g=.6):
    n = T(dur); t = tt(n); return (hp(noise(n), f) * np.exp(-t / .0015) + np.sin(2 * np.pi * f * t) * np.exp(-t / .004) * .5) * g
def shutter(dur=.12):
    n = T(dur); out = np.zeros(n, np.float32)
    for off, g in ((0, 1), (.028, .7)):
        i = T(off); c = click(2500, .03, .55 * g) + np.sin(2 * np.pi * 180 * tt(T(.03))) * exp_env(T(.03), .006) * .3 * g
        out[i:i + len(c)] += c[:n - i]
    return bp(out, 300, 9000)
def heartbeat(dur=.5, f=55, g=1.0):
    n = T(dur); t = tt(n); x = np.sin(pitch_env(f * 1.7, f, n, .03)) * np.exp(-t / .12) * np.minimum(1, t / .004)
    return sat(x * g, 1.3)
def sub_boom(dur=2.0, f0=70, f1=30, g=1.0):
    n = T(dur); t = tt(n); return (np.sin(pitch_env(f0, f1, n, .4)) * np.exp(-t / .7) * np.minimum(1, t / .003) * g).astype(np.float32)
def zap(dur=.4, f0=5000, f1=150):
    n = T(dur); t = tt(n); fr = f1 + (f0 - f1) * np.exp(-t / (dur / 4)); x = osc('saw', fr, n) * .5 + osc('sine', fr * .5, n)
    return lp(x * np.exp(-t / (dur / 2.5)), 9000) * .35
def boing(f0=220, dur=.45):
    n = T(dur); t = tt(n); fr = f0 * (1 + .45 * np.exp(-t / .16) * np.sin(2 * np.pi * 12 * t)) * (1 + .5 * np.exp(-t / .05))
    return lp(osc('sine', fr, n) + .3 * osc('tri', fr * 2, n), 3000) * np.exp(-t / .22) * np.minimum(1, t / .003) * .45
def bubble(f0=400, f1=1500, dur=.07):
    n = T(dur); t = tt(n); fr = f0 + (f1 - f0) * (t / dur) ** .6
    return osc('sine', fr, n) * np.sin(np.pi * t / dur) ** .5 * np.exp(-t / .03) * .5
def whistle_line(events, total, vib=.006, breath=.05):
    """continuous whistle melody: events = [(start_s, dur_s, midi)], gliding between notes."""
    n = T(total); f = np.zeros(n, np.float32); a = np.zeros(n, np.float32); last = None
    for st, d, m in events:
        i, j = T(st), min(n, T(st + d)); fr = mtof(m)
        g = np.full(j - i, fr, np.float32)
        if last is not None: k = min(len(g), T(.035)); g[:k] = np.linspace(last, fr, k)
        f[i:j] = g; a[i:j] = env_adsr(j - i, .02, .05, .85, min(.06, d * .4)); last = fr
    f[f == 0] = 1000; tt_ = tt(n); f = f * (1 + vib * np.sin(2 * np.pi * 5.6 * tt_) * np.minimum(1, tt_ / .3))
    x = osc('sine', f, n) + .04 * osc('sine', f * 2, n); x = x * a + bp(noise(n), 1500, 4000) * a * breath
    return x * .35
def rhodes(midi, dur=1.6, vel=.8):
    """FM electric piano."""
    n = T(dur); t = tt(n); f = mtof(midi); idx = (1.5 * vel) * np.exp(-t / .35) + .2
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) + .15 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / .03) * vel
    return x * env_adsr(n, .002, 1.2, .35, .3) * np.exp(-t / 1.8) * .3
def sawpluck(midi, dur=.2, cut0=5000, cut1=500, decay=.09, voices=5, det=.18):
    """supersaw pluck with a decaying filter envelope (crossfade bright/dark)."""
    n = T(dur); x = supersaw(mtof(midi), n, voices, det); e = exp_env(n, decay)
    return (lp(x, cut0) * e + lp(x, cut1) * (1 - e) * .4) * env_adsr(n, .002, .05, .9, .03) * .6
def granular_glass(dur=.9, density=220, seed=3, lo=2500, hi=9000):
    """granular glass shatter: many tiny resonant shards scattered in stereo with decaying density."""
    r = np.random.default_rng(seed); n = T(dur); out = np.zeros((n, 2), np.float32)
    count = int(density * dur)
    for k in range(count):
        st = (r.random() ** 2.2) * dur * .9; L = T(r.uniform(.006, .05)); fr = r.uniform(lo, hi)
        g = np.sin(2 * np.pi * fr * tt(L) + r.random() * 6) * np.exp(-tt(L) / r.uniform(.004, .02)) * (1 - st / dur) ** 1.5 * r.uniform(.2, 1)
        i = T(st); j = min(n, i + L); pan = r.uniform(-1, 1)
        out[i:j] += stereo(g[:j - i].astype(np.float32), pan)
    out += stereo(hp(noise(n), 4000) * np.exp(-tt(n) / .04) * .5, 0, .8)
    return lp(out * .4, 11500)
def sparkle(dur=3.0, density=18, seed=5, notes=(86, 89, 93, 98), pan_rate=.35):
    """granular high sparkle swirling in stereo (pan rotates)."""
    r = np.random.default_rng(seed); n = T(dur); out = np.zeros((n, 2), np.float32)
    for k in range(int(density * dur)):
        st = r.random() * dur * .95; m = r.choice(notes) + r.choice((0, 12)); L = T(.25)
        g = np.sin(2 * np.pi * mtof(m) * tt(L)) * np.exp(-tt(L) / .06) * r.uniform(.15, .5) * np.minimum(1, tt(L) / .002)
        i = T(st); j = min(n, i + L); pan = math.sin(2 * math.pi * pan_rate * st + r.random() * .5)
        out[i:j] += stereo(g[:j - i].astype(np.float32), pan)
    return lp(out * .5, 12000)
def creak(dur=1.5, seed=7):
    """rubber-stretch creak: irregular stick-slip impulse train through body resonances, pitch sagging."""
    r = np.random.default_rng(seed); n = T(dur); x = np.zeros(n, np.float32); pos = 0.0
    while pos < dur:
        rate = 70 - 40 * pos / dur + r.normal(0, 8); pos += 1 / max(rate, 15); i = T(pos)
        if i < n: x[i] = r.uniform(.5, 1)
    y = sum(bp(x, f * .85, f * 1.18) * g for f, g in ((380, 1), (820, .7), (1650, .45), (2900, .2)))
    return sat(y * 3 * env_adsr(n, .08, .2, .9, .3), 1.5) * .5
def tape_flick(dur=.15):
    n = T(dur); t = tt(n); fr = 300 * (1 + 12 * (t / dur) ** 2); x = osc('saw', fr, n) * .3 + bp(noise(n), 1500, 7000) * .5
    return lp(x * np.sin(np.pi * t / dur), 8000) * .6
def tuned_whoosh(midi, dur=.5, peak=.85, q=7):
    """whoosh whose resonance is tuned to a note (the 'staircase')."""
    n = T(dur); u = tt(n) / dur; e = np.where(u < peak, (u / peak) ** 2.5, ((1 - u) / (1 - peak)) ** 1.2)
    fr = mtof(midi) * (1 + .5 * (1 - np.minimum(1, u / peak))) * 2   # glides down onto 2x the note
    x = tv_bp(noise(n), fr, q) * 2.2 + osc('sine', mtof(midi) * 2, n) * .25 + bp(noise(n), 500, 6000) * .25
    return (x * e).astype(np.float32) * .6
def world_noise(dur, seed=11, density=1.0, murmur=1.0):
    """synthesised city: traffic rumble, sirens (crossing sine sweeps), horns, jackhammer 16ths, pings, crowd babble."""
    r = np.random.default_rng(seed); n = T(dur); t = tt(n); out = np.zeros((n, 2), np.float32)
    out += stereo(lp(pink(n), 260) * 1.4 + lp(osc('saw', 46 + 3 * np.sin(2 * np.pi * .3 * t), n), 180) * .2, 0, .6)
    # crowd babble: formant-modulated noise streams
    for k in range(6):
        f1 = 500 + 300 * np.sin(2 * np.pi * r.uniform(3, 6) * t + r.random() * 6); src = bp(noise(n), 250, 3500)
        v = tv_bp(src, f1, 3, 192) * (.5 + .5 * np.sin(2 * np.pi * r.uniform(2, 5) * t + r.random() * 6)) ** 2
        out += stereo(v * .5 * murmur, r.uniform(-.8, .8))
    if density > 0:
        for k, (lo, hi, rate) in enumerate(((600, 1200, .55), (700, 1150, .8))):          # sirens
            fr = (lo + hi) / 2 + (hi - lo) / 2 * np.sin(2 * np.pi * rate * t + k * 2)
            s = osc('sine', fr, n) * .14 + osc('tri', fr, n) * .05; pan = np.sin(2 * np.pi * .2 * t + k * 3) * .7
            out += pan_curve(s * density, pan)
        hits = int(6 * dur * density)
        for k in range(hits):                                                                     # horns
            st = r.random() * dur; L = T(r.uniform(.12, .35)); f0 = r.choice([370, 415, 466, 523])
            h = lp(osc('square', f0, L) + osc('square', f0 * 1.26, L), 2500) * env_adsr(L, .005, .02, .9, .03) * .06
            i = T(st); j = min(n, i + L); out[i:j] += stereo(h[:j - i], r.uniform(-.9, .9))
        for k in range(int(dur / (BEAT / 4))):                                                    # jackhammer 16ths
            i = T(k * BEAT / 4); L = T(.05); jh = bp(noise(L), 300, 2200) * exp_env(L, .012) * .35 * density
            j = min(n, i + L); out[i:j] += stereo(jh[:j - i], -.5)
        for k in range(int(5 * dur * density)):                                                   # notification pings
            st = r.random() * dur; L = T(.18); p = tick(r.choice([1760, 2093, 2349, 2637]), .18, .12)
            i = T(st); j = min(n, i + L); out[i:j] += stereo(p[:j - i], r.uniform(-1, 1))
    return lp(out, 7000)

def compress(x, thr_db=-18, ratio=2.5, att=.01, rel=.15, makeup_db=0.0, block=64):
    """feed-forward RMS-ish bus compressor (block envelope, one-pole attack/release)."""
    xs = as_st(x); n = len(xs); nb = (n + block - 1) // block
    pk = np.abs(xs).max(1); pad = np.zeros(nb * block, np.float32); pad[:n] = pk ** 2
    lvl = np.sqrt(pad.reshape(nb, block).mean(1)) * 1.414
    aA, aR = math.exp(-block / (att * SR)), math.exp(-block / (rel * SR)); env = np.empty(nb); e = 0.0
    for i in range(nb):
        v = lvl[i]; c = aA if v > e else aR; e = c * e + (1 - c) * v; env[i] = e
    over = np.maximum(to_db(env) - thr_db, 0); gr = -over * (1 - 1 / ratio)
    g = np.interp(np.arange(n), np.arange(nb) * block + block / 2, db(gr + makeup_db)).astype(np.float32)
    return xs * g[:, None]
def limit(x, ceil_db=-1.3, look=.003, rel=.06, block=32):
    """look-ahead brickwall limiter. returns (y, gain-reduction-db array)."""
    xs = as_st(x); n = len(xs); c = db(ceil_db); pk = np.abs(xs).max(1)
    need = np.minimum(1, c / np.maximum(pk, 1e-9))
    L = T(look); g = minimum_filter1d(need, 2 * L + 1, mode='nearest')
    nb = (n + block - 1) // block; pad = np.ones(nb * block); pad[:n] = g; gb = pad.reshape(nb, block).min(1)
    aR = math.exp(-block / (rel * SR)); out = np.empty(nb); e = 1.0
    for i in range(nb):
        v = gb[i]; e = v if v < e else aR * e + (1 - aR) * v; out[i] = e
    gs = np.repeat(out, block)[:n]; gs = np.minimum(gs, g)
    gs = uniform_filter1d(minimum_filter1d(gs, L + 1, mode='nearest'), L + 1, mode='nearest')
    y = xs * gs[:, None]; y = np.clip(y, -c, c)
    return y.astype(np.float32), to_db(gs)
def true_peak_db(x, os=4):
    return to_db(np.abs(signal.resample_poly(x, os, 1, axis=0)).max())
def write_audio(mix, wav_path, mp3_path=None):
    pcm = (np.clip(mix, -1, 1) * 32767).round().astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s16le', wav_path], input=pcm, check=True)
    if mp3_path:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav_path, '-c:a', 'libmp3lame', '-b:a', '192k', mp3_path], check=True)
def tv_lp_at(buf, i0, i1, fc, order=2, pre=.05):
    """tv_lp on buf[i0:i1] with a pre-roll (filter state warmed up on the preceding audio at fc[0]) -> no step at i0."""
    p = min(i0, T(pre)); fc = np.broadcast_to(np.asarray(fc, np.float64), (i1 - i0,))
    y = tv_lp(buf[i0 - p:i1], np.concatenate([np.full(p, fc[0]), fc]), order=order); return y[p:]
