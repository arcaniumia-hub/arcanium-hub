"""LUMARC "Break out of the feed" — score + SFX (no voice) -> music.wav, plus final mix -> out/lumarc-breakout.mp4.

    python3 sound.py          # music.wav (score + every section CUE)
    python3 sound.py mux      # voice (src/tight.mov) + music, ducked + loudness-normalised, muxed onto out/video.mp4

Sonic idea = the film's idea: while he is trapped in the feed the music plays INSIDE the phone (small, mono, band-passed
like a phone speaker). "and it's gone" -> the feed music stops dead; knock, knock in silence; "Not mine." -> low drone +
riser; the glass shatters -> BOOM, and from "Good content…" the score is full-range, wide, 120 BPM (anchored so the
word "LUMARC" lands on a downbeat). CTA groove -> end-card boom + shimmer.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import engine as E

DUR = E.DUR
TS = lambda i: E.TL[i]['t0']
LUM = E.word_time('LUMARC', 16) or TS(16) + 1.5
BT = .5; OFF = LUM % BT
mix = Mix(DUR)
def nz(x, p=1.0):
    x = np.asarray(x, np.float32); return x / (np.abs(x).max() + 1e-9) * p
def A(stem, x, at, g=0.0, pan=0.0, p=None):
    if p is not None: x = nz(x, p)
    mix.add(stem, x, at=at, gain=db(g), pan=pan)
def beats(a, z):
    t = OFF + math.ceil((a - OFF) / BT - 1e-6) * BT; out = []
    while t < z - 1e-6: out.append(round(t, 4)); t += BT
    return out
PROG = [['E3', 'B3', 'E4', 'G4', 'B4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4'], ['D3', 'A3', 'D4', 'F#4', 'A4']]
BASS = ['E1', 'C2', 'G1', 'D2']
def bar_of(t): return int(round((t - OFF) / BT)) // 4
def groove(a, z, g=0.0, sfx='', light=False, arp=True):
    for t in beats(a, z):
        i = int(round((t - OFF) / BT))
        A('kick' + sfx, kick(punch=1.0), t, -5 + g)
        if not light and i % 2 == 1: A('drums' + sfx, clap(), t, -12 + g)
        A('drums' + sfx, hat(), t + BT / 2, -17 + g, pan=.25)
        if not light: A('drums' + sfx, hat(), t + BT * .75, -23 + g, pan=-.25)
        if i % 4 == 0:
            k = bar_of(t) % 4
            A('bass' + sfx, sub808(note(BASS[k]), 1.9, drive=1.7), t, -9 + g)
            A('pad' + sfx, pad([note(n) for n in PROG[k]], 2.05, att=.02, rel=.4, bright=2400), t, -15 + g)
            if arp and not light:
                for j, n in enumerate(PROG[k][2:] * 2):
                    A('arp' + sfx, pluck(note(n) + 12, .3, .12, .8), t + j * BT / 2 + BT * 2, -21 + g, pan=(-.4 if j % 2 else .4))

def T_(s): return int(round(s * SR))
def addl(a, b):
    a, b = as_st(a), as_st(b); n = max(len(a), len(b)); return pad_to(a, n) + pad_to(b, n)
def glass(dur=.9, seed=0):
    r = np.random.default_rng(seed); n = T_(dur); t = tt(n); x = np.zeros(n, np.float32)
    for f in r.uniform(2400, 7800, 9):
        x += np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t / r.uniform(.12, .45)) * r.uniform(.3, 1)
    sw = hp(noise(n), 3500) * np.exp(-((t - dur * .25) / (dur * .2)) ** 2) * .6
    return (x * .25 + sw).astype(np.float32)
def shatter(seed=0, dur=1.6, n_bits=60):
    r = np.random.default_rng(seed); n = T_(dur); out = np.zeros(n, np.float32)
    for _ in range(n_bits):
        i = int(r.uniform(0, .6) ** 1.8 * n); m = T_(.25); tt_ = np.arange(m) / SR
        out[i:i + m] += (np.sin(2 * np.pi * r.uniform(2500, 9500) * tt_) * np.exp(-tt_ / r.uniform(.02, .07)) * r.uniform(.2, 1))[:n - i]
    out[:T_(.35)] += hp(noise(T_(.35)), 1800) * np.exp(-np.arange(T_(.35)) / SR / .09) * 1.4
    return out
def knock(seed=0):
    """knuckle on the inside of the phone glass: dull body thump + hard glassy tick."""
    r = np.random.default_rng(seed); n = T_(.35); t = tt(n)
    body = lp(noise(n), 420) * np.exp(-t / .035) * 3 + np.sin(2 * np.pi * (140 + 30 * r.random()) * t) * np.exp(-t / .05) * .8
    tick_ = hp(noise(n), 2500) * np.exp(-t / .006) * .7 + np.sin(2 * np.pi * 3100 * t) * np.exp(-t / .03) * .15
    return (body + tick_).astype(np.float32)
def crack(seed=0, dur=.45):
    """glass cracking: a fast cascade of sharp ticks with a bright noise spine."""
    r = np.random.default_rng(seed); n = T_(dur); out = np.zeros(n, np.float32)
    for k in range(26):
        i = int((k / 26) ** 1.6 * n * .8 + r.uniform(0, 300)); m = T_(.03); tt_ = np.arange(m) / SR
        out[i:i + m] += (hp(noise(m), 3000) * np.exp(-tt_ / .004) * r.uniform(.3, 1))[:n - i]
    out += hp(noise(n), 4500) * np.exp(-tt(n) / .08) * .35
    out[:T_(.12)] += lp(noise(T_(.12)), 600) * np.exp(-tt(T_(.12)) / .02) * 1.2
    return out
def flick(dur=.28):
    """finger flick on the screen: short, airy, up-sweeping."""
    return whoosh(dur, .35, up=True)
def rewind(dur=.7):
    """VHS / tape rewind: chirpy squeal + motor noise with falling-then-rising speed."""
    n = T_(dur); t = tt(n); f = 900 + 2600 * np.sin(np.pi * t / dur) ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    sq = np.sign(np.sin(ph * 3)) * .15 + np.sin(ph) * .35
    mot = bp(noise(n), 800, 4000) * .3
    env = np.minimum(1, t / .03) * np.minimum(1, (dur - t) / .08)
    return ((sq + mot) * env).astype(np.float32)
def thud():
    n = T_(.5); t = tt(n); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-t / .03)) * t) * np.exp(-t / .12)).astype(np.float32)
def clock_tick(i=0):
    n = T_(.12); t = tt(n); f = 2200 if i % 2 == 0 else 1700
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / .012) + .5 * noise(n) * np.exp(-t / .004)).astype(np.float32)

SFX = {
    'whoosh': lambda c: (whoosh(.5, .7), -.5 * .7, -10),
    'swoosh_up': lambda c: (whoosh(.55, .6, up=True), -.33, -9),
    'swipe': lambda c: (whoosh(.32, .45, up=True), -.14, -6),
    'flick': lambda c: (flick(), -.1, -11),
    'impact': lambda c: (impact(1.8, .9, .9, .4), 0, -5),
    'boom': lambda c: (addl(nz(impact(2.6, 1.2, .8, .6)), nz(braam(note('E1'), 2.2, .7)) * .5), 0, -4),
    'thud': lambda c: (thud(), 0, -8),
    'tick': lambda c: (tick(2600, .05, .6), 0, -16),
    'clock': lambda c: (clock_tick(c.get('i', 0)), 0, -10),
    'glass': lambda c: (glass(.9, c.get('seed', 1)), 0, -12),
    'knock': lambda c: (knock(c.get('seed', 0)), 0, -4),
    'crack': lambda c: (crack(c.get('seed', 0), c.get('dur', .45)), 0, -7),
    'shatter': lambda c: (shatter(c.get('seed', 2), c.get('dur', 1.6)), 0, -5),
    'pop': lambda c: (glock(note('E6'), .4), 0, -16),
    'glitch': lambda c: (glitch_burst(.3, c.get('seed', 3)), 0, -10),
    'riser': lambda c: (riser(max(.3, c.get('to', 0) - c['_t']), 300, 6000, .9, .4), 0, -12),
    'shimmer': lambda c: (shimmer([note('B5'), note('E6'), note('G#6')], 1.6, .8), 0, -15),
    'rewind': lambda c: (rewind(c.get('dur', .7)), 0, -12),
    'cash': lambda c: (glock(note('A6'), .8) + np.pad(glock(note('E6'), .8), (T_(.08), 0))[:T_(.8)], 0, -12),
    'click': lambda c: (tick(3200, .03, .5), 0, -18),
    'type': lambda c: (tick(3800 + 300 * (c.get('i', 0) % 3), .025, .4), 0, -22),
    'heart': lambda c: (glock(note('A6'), .5), 0, -15),
    'shutter': lambda c: (hp(noise(T_(.08)), 2500) * np.exp(-tt(T_(.08)) / .02), 0, -14),
    'notify': lambda c: (glock(note('E6'), .4) + np.pad(glock(note('B6'), .4), (T_(.1), 0))[:T_(.4)], 0, -13),
}

GONE, NOT, BREAK = TS(8), TS(9), TS(11)            # 7.08 knock silence, 7.80 "Not mine.", 9.28 out in the studio
if not (len(sys.argv) > 1 and sys.argv[1] == 'mux'):
    # ---- inside the phone: small, mono, band-passed feed music
    groove(0.0, GONE - .02, -2, sfx='_ph', arp=True)
    for k in ('kick_ph', 'drums_ph', 'bass_ph', 'pad_ph', 'arp_ph'):
        if k in mix.stems:
            mix.filter_range(k, 0, GONE + .5, 'hp', 380); mix.filter_range(k, 0, GONE + .5, 'lp', 3200)
            mix.stems[k][:] = mix.stems[k].mean(1, keepdims=True)
    # ---- "Not mine.": low drone + riser into the shatter, then the full-range world
    A('drone', pad([note('E1'), note('B1'), note('E2')], BREAK - NOT + .4, att=.25, rel=.3, bright=500), NOT, -9)
    A('fx', riser(BREAK - NOT - .2, 200, 7000, 1., .5), NOT, -10, p=.9)
    groove(BREAK, TS(12), 0, arp=False)                                   # "Good content doesn't stay on the screen"
    groove(TS(12), TS(16))                                                 # head / touch / twice / remember
    groove(TS(16), LUM - .05, -7, light=True, arp=False)
    A('fx', riser(LUM - TS(16), 300, 7000, 1., .5), TS(16), -9, p=.9)
    groove(LUM, TS(17))                                                    # LUMARC downbeat
    groove(TS(17), E.VOICE_END - .05, -1)                                  # CTA
    A('pad', pad([note(n) for n in ['E3', 'B3', 'E4', 'G#4', 'B4']], DUR - E.VOICE_END, att=.01, rel=1.4, bright=2200), E.VOICE_END, -10)
    A('fx', shimmer([note('E5'), note('B5'), note('G#6'), note('E6')], DUR - E.VOICE_END, 1.8), E.VOICE_END, -12)
    mix.sidechain('pad', beats(BREAK, E.VOICE_END), .45, .16)
    mix.sidechain('bass', beats(BREAK, E.VOICE_END), .5, .14)

    # ---- section cues
    missing = set()
    for t, kind, params in E.collect_cues():
        if kind not in SFX: missing.add(kind); continue
        params = dict(params, _t=t)
        x, off, g = SFX[kind](params)
        A('sfx', x, t + off, g + params.get('gain', 0), pan=params.get('pan', 0))
    if missing: print('unknown cue kinds (skipped):', sorted(missing))

    mix.render(os.path.join(HERE, 'music.wav'), gains=dict(kick=.8, drums=.8, bass=.8, arp=.8))
    print('music ok', DUR)

def mux():
    out = os.path.join(E.OUT, 'lumarc-breakout.mp4')
    af = ('[0:a]aresample=48000,highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];[1:a]volume=0.30[m];[m][key]sidechaincompress=threshold=0.035:ratio=8:attack=15:release=300[md];'
          '[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.SRC, 'tight.mov'), '-i', os.path.join(HERE, 'music.wav'), '-filter_complex', af,
                    '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(E.OUT, 'mix.wav')], check=True)
    kb = int(28.6 * 8 * 1024 / DUR) - 192                                  # 2-pass to land under the 30 MB chat limit
    kb = min(kb, 14000)
    for ps in (1, 2):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.OUT, 'video.mp4'), '-i', os.path.join(E.OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
               '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{kb}k', '-pass', str(ps), '-passlogfile', os.path.join(E.OUT, 'x264'),
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}']
        subprocess.run(cmd + (['-f', 'mp4', '/dev/null'] if ps == 1 else [out]), check=True)
    print(out, os.path.getsize(out) / 1e6, 'MB')

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'mux':
    mux()
