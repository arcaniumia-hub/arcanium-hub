"""v3 audio: voice with a room per location, synthesized location ambience, final mix.

    python3 audio_real.py           # -> work/voice_room.wav, work/amb.wav, out/lumarc-clones.mp4 (muxed with out/video.mp4 + music.wav)
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
import numpy as np
import lib as S
import edit_real as R
from edit import TL, DUR, SRC, WORK, OUT

SR = S.SR; N = int(DUR * SR)
rng = np.random.default_rng(11)
ROOM = {  # reverb size, mix, highpass, lowpass
    'studio': (.5, .06, 80, 16000), 'cafe': (.9, .14, 90, 9000), 'rooftop': (.3, .03, 120, 16000),
    'paris': (.4, .05, 100, 14000), 'board': (1.0, .12, 90, 12000), 'taxes': (.8, .16, 200, 6000), 'beach': (.3, .03, 100, 14000)}

def line_loc(i):
    return 'beach' if i == 13 else R.LOC[i]

def voice():
    out = np.zeros((N + SR, 2), np.float32)
    for i, ln in enumerate(TL):
        b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ln["s0"]:.3f}', '-t', f'{ln["s1"] - ln["s0"]:.3f}', '-i', SRC[ln['k']], '-vn',
                            '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
        x = np.frombuffer(b, np.float32).copy(); f = int(.012 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
        size, mix, hpf, lpf = ROOM[line_loc(i)]
        x = S.lp(S.hp(x, hpf), lpf)
        x = np.concatenate([x, np.zeros(int(size * SR), np.float32)])     # let the tail ring
        y = S.reverb(x, size=size, mix=mix, damp=5000, predelay=.008)
        j = int(ln['t0'] * SR); out[j:j + len(y)] += y[:len(out) - j]
    write(out[:N], os.path.join(WORK, 'voice_room.wav'))

def gate(n, rate, duty, smooth=.04):
    g = np.zeros(n, np.float32); i = 0
    while i < n:
        on = int(rng.uniform(.6, 1.4) * duty / rate * SR); off = int(rng.uniform(.5, 1.5) * (1 - duty) / rate * SR)
        g[i:i + on] = rng.uniform(.5, 1); i += on + off
    k = int(smooth * SR); return np.convolve(g, np.ones(k) / k, 'same').astype(np.float32)

def babble(n, voices=14):
    x = np.zeros(n, np.float32)
    for _ in range(voices):
        c = rng.uniform(350, 1500); v = S.bp(S.noise(n), c * .7, c * 1.6) * gate(n, rng.uniform(3, 5.5), .55, .03)
        v *= gate(n, rng.uniform(.25, .5), .6, .3); x += v
    return S.lp(x, 3200)

def clinks(n, every=(1.5, 4.0)):
    x = np.zeros(n, np.float32); t = rng.uniform(.3, 1.5)
    while t < n / SR - .3:
        m = int(.25 * SR); tt = np.arange(m) / SR; f0 = rng.uniform(2000, 3200)
        s = sum(np.sin(2 * np.pi * f0 * r * tt) * a for r, a in ((1, 1), (1.63, .6), (2.41, .4))) * np.exp(-tt / .07)
        i = int(t * SR); x[i:i + m] += s[:n - i].astype(np.float32) * rng.uniform(.2, .5); t += rng.uniform(*every)
    return x

def nrm(x, db):
    r = np.sqrt((x ** 2).mean()) + 1e-9; return (x / r * 10 ** (db / 20)).astype(np.float32)

def ambience(loc, n):
    if loc == 'studio': return nrm(S.lp(S.pink(n), 900), -50) + nrm(np.sin(2 * np.pi * 60 * np.arange(n) / SR).astype(np.float32), -60)
    if loc == 'cafe': return nrm(babble(n), -36) + nrm(clinks(n), -44) + nrm(S.lp(S.pink(n), 1500), -48)
    if loc == 'rooftop':
        w = S.lp(S.pink(n), 500) * (.6 + .4 * np.sin(2 * np.pi * np.arange(n) / SR / 6.5)).astype(np.float32)
        return nrm(w, -38) + nrm(S.lp(S.noise(n), 140), -42)
    if loc == 'paris': return nrm(babble(n, 8), -42) + nrm(S.lp(S.noise(n), 220), -40) + nrm(clinks(n, (2.5, 5)), -48)
    if loc == 'board': return nrm(S.lp(S.pink(n), 300), -42) + nrm(np.sin(2 * np.pi * 120 * np.arange(n) / SR).astype(np.float32), -62)
    if loc == 'taxes':
        t = np.arange(n) / SR; buzz = S.lp((((120 * t) % 1) * 2 - 1).astype(np.float32), 900)
        return nrm(buzz, -50) + nrm(S.lp(S.pink(n), 400), -46)
    return np.zeros(n, np.float32)       # beach: waves come from the score

def amb():
    out = np.zeros(N, np.float32); fade = int(.03 * SR)
    for s in R.SHOTS:
        i0, i1 = int(s['a'] * SR), min(N, int(s['z'] * SR)); n = i1 - i0
        if n <= 0: continue
        x = ambience(s['loc'], n + 2 * fade)[:n]; x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
        out[i0:i1] += x
    write(S.stereo(out, width=.4) if out.ndim == 1 else out, os.path.join(WORK, 'amb.wav'))

def write(x, path):
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm, check=True)

def mux():
    fin = os.path.join(OUT, 'lumarc-clones.mp4')
    af = ('[0:a]aresample=48000,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,apad=whole_dur=%.2f,asplit=2[v][key];'
          '[1:a]volume=0.42[m];[m][key]sidechaincompress=threshold=0.05:ratio=4:attack=25:release=320[md];[2:a]volume=1.0[am];'
          '[v][md][am]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(WORK, 'voice_room.wav'), '-i', os.path.join(HERE, 'music.wav'),
                    '-i', os.path.join(WORK, 'amb.wav'), '-filter_complex', af, '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000',
                    os.path.join(OUT, 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'video.mp4'), '-i', os.path.join(OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '6.5M', '-bufsize', '13M', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}', fin], check=True)
    print(fin, os.path.getsize(fin) / 1e6, 'MB')

if __name__ == '__main__':
    what = sys.argv[1:] or ['voice', 'amb', 'mux']
    for w in what: globals()[w]()
