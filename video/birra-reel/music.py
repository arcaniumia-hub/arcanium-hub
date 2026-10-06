"""Synthesizes the 30s soundtrack: soft felt piano arpeggios + warm pad + reverb.
Harmony follows the story: unsettled minor (0-15s) -> warm major arrival when the
parent kneels (15s) -> gentle resolution at the end card (26-30s).
Usage: python3 music.py out/music.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

def hz(note):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o + 1) - 69) / 12)

def piano(f, dur, vel):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 8):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 9000:
            break
        amp = vel / k ** 1.7
        dec = 0.9 + 0.55 * k + f / 900
        out += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * dec)
    att = np.minimum(1, t / 0.012)          # soft felt attack
    rel = np.minimum(1, (dur - t) / 0.25)   # damper release
    return out * att * np.clip(rel, 0, 1)

def pad(freqs, dur, vol):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            out += np.sin(2 * np.pi * ff * t) + 0.18 * np.sin(2 * np.pi * 2 * ff * t)
    env = np.minimum(1, t / 1.6) * np.minimum(1, (dur - t) / 1.4)
    trem = 1 + 0.06 * np.sin(2 * np.pi * 0.23 * t)
    return out * env * trem * vol / len(freqs)

mix = np.zeros(N + SR * 4)

def add(sig, at):
    i = int(at * SR)
    mix[i:i + len(sig)] += sig[:len(mix) - i]

# (start, end, notes for arpeggio, pad notes, velocity)
CHORDS = [
    (0.0, 4.0, ['B2', 'F#3', 'B3', 'D4', 'C#5', 'D4'], ['B2', 'F#3', 'D4'], .55),
    (4.0, 9.0, ['G2', 'D3', 'B3', 'F#4', 'A4', 'F#4'], ['G2', 'D3', 'B3', 'F#4'], .5),
    (9.0, 12.5, ['E2', 'B2', 'G3', 'D4', 'F#4', 'D4'], ['E2', 'B2', 'G3', 'D4'], .5),
    (12.5, 15.0, ['F#2', 'C#3', 'B3', 'C#4', 'A#3', 'C#4'], ['F#2', 'C#3', 'A#3'], .5),
    (15.0, 18.0, ['D2', 'A2', 'F#3', 'C#4', 'E4', 'A4'], ['D2', 'A2', 'F#3', 'C#4'], .55),
    (18.0, 21.0, ['G2', 'D3', 'A3', 'B3', 'D4', 'F#4'], ['G2', 'D3', 'B3', 'F#4'], .55),
    (21.0, 23.5, ['B2', 'F#3', 'A3', 'D4', 'E4', 'D4'], ['B2', 'F#3', 'A3', 'D4'], .5),
    (23.5, 26.0, ['G2', 'D3', 'B3', 'E4', 'F#4', 'A4'], ['G2', 'D3', 'B3', 'E4'], .52),
    (26.0, 30.0, ['D2', 'A2', 'F#3', 'C#4', 'E4', 'F#4'], ['D2', 'A2', 'F#3', 'C#4', 'E4'], .5),
]
EIGHTH = 60 / 72 / 2
for (a, b, notes, padn, vel) in CHORDS:
    add(pad([hz(n) for n in padn], b - a + 1.4, 0.10), max(0, a - 0.2))
    add(piano(hz(notes[0]) / 2, 4.5, vel * .5), a)  # soft low bass
    t, i = a, 0
    last = a >= 26
    while t < b - 0.05 and not (last and t > 28.2):
        v = vel * (0.85 if i % 6 == 0 else 0.55) * (1 + 0.08 * rng.standard_normal())
        add(piano(hz(notes[i % len(notes)]), 3.2, v * .6), t + rng.uniform(0, 0.012))
        t += EIGHTH
        i += 1

# sparse melody from the warm turn onward
MEL = [(15.0, 'F#5', 1.6), (16.65, 'E5', .8), (17.5, 'A5', 2.2), (19.6, 'F#5', 1.4), (21.0, 'D5', 1.6), (22.7, 'E5', .9),
       (23.5, 'B4', 1.8), (25.2, 'A4', .8), (26.0, 'A5', 1.6), (27.6, 'F#5', 3.5)]
for (at, n, d) in MEL:
    add(piano(hz(n), d + 2.5, .28), at)
# final chord bloom
for n in ['D3', 'A3', 'F#4', 'C#5', 'E5']:
    add(piano(hz(n), 4.0, .22), 28.4 + rng.uniform(0, .05))

dry = mix[:N + SR * 4]

# gentle low-pass (one-pole) to keep it warm
def onepole(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    # vectorised via lfilter-equivalent recursion in chunks
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s
        y[i] = s
    return y

try:
    from scipy.signal import lfilter, fftconvolve
    a = np.exp(-2 * np.pi * 5200 / SR)
    dry = lfilter([1 - a], [1, -a], dry)
    conv = fftconvolve
except ImportError:
    dry = onepole(dry, 5200)
    def conv(x, h):
        L = len(x) + len(h) - 1
        n = 1 << (L - 1).bit_length()
        return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[:L]

def ir(seed):
    r = np.random.default_rng(seed)
    n = int(SR * 3.2)
    t = np.arange(n) / SR
    h = r.standard_normal(n) * np.exp(-t * 2.2)
    h[: int(SR * .02)] *= np.linspace(0, 1, int(SR * .02))
    return h / np.sqrt(np.sum(h ** 2))

L = dry + 0.55 * conv(dry, ir(1))[:len(dry)]
R = dry + 0.55 * conv(dry, ir(2))[:len(dry)]
st = np.stack([L, R], 1)[:N]
tt = np.arange(N) / SR
fade = np.minimum(1, tt / 0.6) * np.clip((DUR - tt) / 2.2, 0, 1)
st *= fade[:, None]
st /= np.max(np.abs(st)) / 0.6   # leave headroom; loudness set by ffmpeg loudnorm later
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('wrote', sys.argv[1])
