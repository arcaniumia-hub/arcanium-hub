"""LUMARC "IA só faz conteúdo genérico?" (PT-BR) — score + SFX (no voice) -> music.wav + sfx.wav, then the final mix ->
out/lumarc-ia.mp4.

    python3 sound.py          # music.wav (score) + sfx.wav (every section CUE)
    python3 sound.py mux      # voice (src/tight.mov) + music (hard-ducked) + sfx (lightly ducked), -14 LUFS, muxed

The score tells the film's story. The generic world is a deliberately CHEESY stock-music ukulele loop (the joke); a
record scratch kills it on "Mas será que…"; tension pulse + riser into "MÁXIMO" (hit); a playful pizzicato bit under the
self-aware-AI joke; a lone piano/rhodes "artist" motif for the paintbrush; a build into "mão certa" and the SHOWREEL DROP
(half-time trap/cinematic: 808, braams) that stops dead for the "um clone seu… / ou três" pause; the LUMARC groove
(confident 112 BPM, thins out for "o que ela não tem:" then re-enters on "estratégia"); a hard stop on "O resultado?";
punchy 128 BPM for the results; tape-stop into the twist; a low pulse that lands "noventa por cento" on a hit; a warm
final groove under the CTA; end boom + shimmer.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import engine as E

DUR = E.DUR; TL = E.TL
TS = lambda i: TL[i]['t0']; TE = lambda i: TL[i]['t1']
# word onsets the score is keyed on (edit timeline; measured on src/tight16k.raw)
ON = dict(MAXIMO=14.76, MAO_CERTA=30.25, CLONE_END=37.96, TRES=38.565, LIGHTS_ON=44.00, AI_FIRST=44.95,
          ESTRATEGIA=50.27, RESULTADO=57.21, GENERICO=62.29, NOVENTA=68.025)
mix = Mix(DUR)
def nz(x, p=1.0):
    x = np.asarray(x, np.float32); return x / (np.abs(x).max() + 1e-9) * p
def A(stem, x, at, g=0.0, pan=0.0, p=None):
    if p is not None: x = nz(x, p)
    mix.add(stem, x, at=at, gain=db(g), pan=pan)
def T_(s): return int(round(s * SR))
def addl(a, b):
    a, b = as_st(a), as_st(b); n = max(len(a), len(b)); return pad_to(a, n) + pad_to(b, n)
def grid(a, z, bpm, sub=1):
    """beat times from a (downbeat) to z, `sub` subdivisions per beat -> [(t, index)]."""
    bt = 60 / bpm / sub; out = []; i = 0
    while a + i * bt < z - 1e-6: out.append((a + i * bt, i)); i += 1
    return out

# ------------------------------------------------------------------ 1. the generic world: cheesy stock ukulele (0 -> 9.84)
def cheesy(a, z):
    bpm = 112; bt = 60 / bpm
    prog = [['C4', 'E4', 'G4', 'C5'], ['G3', 'D4', 'G4', 'B4'], ['A3', 'E4', 'A4', 'C5'], ['F3', 'C4', 'F4', 'A4']]
    bass = ['C2', 'G1', 'A1', 'F1']
    for t, i in grid(a, z, bpm, 2):                       # eighth-note strum pattern D . D U . U D U
        bar = (i // 8) % 4; k = i % 8
        if k in (0, 2, 3, 5, 6, 7):
            ch = [note(n) for n in prog[bar]]
            A('uke', strum(ch, .32 if k else .5, .011, down=k in (0, 2, 6), vel=1.0 if k in (0, 6) else .7, bright=.75), t, -15, pan=-.15)
        if k % 2 == 0:
            beat = k // 2
            if beat in (1, 3): A('clap', clap(.22), t, -19, pan=.1)
            A('clap', shaker(.07, 1.0 if beat % 2 else .6), t + bt / 2, -27, pan=.3)
            if beat in (0, 2): A('bass', pluck(note(bass[bar]), bt * 1.6, .25, .6), t, -14)
    # the whistle hook everyone has heard a thousand times
    mel = [('E5', 0, .5), ('G5', .5, .5), ('A5', 1.0, 1.0), ('G5', 2.0, .5), ('E5', 2.5, .5), ('D5', 3.0, 1.0),
           ('C5', 4.0, .5), ('D5', 4.5, .5), ('E5', 5.0, 1.0), ('G5', 6.0, .5), ('E5', 6.5, 1.5)]
    t0 = a + 4 * bt * 1                                   # enters after one bar
    while t0 < z - 1:
        ev = [(s * bt, d * bt, note(m)) for m, s, d in mel]
        tot = 8 * bt
        x = whistle_line(ev, tot)
        A('whistle', x[:T_(max(.1, min(tot, z - t0)))], t0, -20, pan=.15); t0 += 8 * bt
    for t, i in grid(a, z, bpm, 1):
        if i % 4 == 0: A('glock', glock(note('C6') if (i // 4) % 2 == 0 else note('G5'), .6), t + bt * 3.5, -26, pan=.35)

# ------------------------------------------------------------------ 2. tension into MÁXIMO (9.84 -> 15.72)
def tension(a, hit, z):
    for t in np.arange(a + .35, hit - .05, .62):
        A('pulse', heartbeat(.5, 52, 1.0), t, -11)
    A('pad', pad([note('D2'), note('A2'), note('F3')], hit - a, att=1.0, rel=.2, bright=900), a + .2, -17)
    A('fx', riser(hit - (a + 1.0), 180, 5200, 1.0, .5), a + 1.0, -13, p=.8)
    A('hit', addl(nz(impact(2.4, 1.2, .9, .6)), nz(sub_boom(2.0, 62, 28)) * .7), hit, -4)
    A('pad', pad([note('D3'), note('A3'), note('D4'), note('F#4')], z - hit + .2, att=.02, rel=.5, bright=2600), hit, -16)
    A('fx', shimmer([note('D5'), note('A5'), note('F#6')], z - hit + .3, 1.2), hit + .05, -18)

# ------------------------------------------------------------------ 3. playful pizzicato (15.72 -> 22.20)
def playful(a, z):
    bpm = 104; bt = 60 / bpm
    prog = [['G3', 'B3', 'D4'], ['E3', 'G3', 'B3'], ['C3', 'E3', 'G3'], ['D3', 'F#3', 'A3']]
    for t, i in grid(a, z, bpm, 2):
        bar = (i // 8) % 4; k = i % 8
        notes = prog[bar]
        if k in (0, 3, 4, 6): A('pizz', ks(note(notes[k % 3]) + 12, .35, .5, .992), t, -16, pan=(-.3 if k % 2 else .3))
        if k in (0, 4): A('kick', kick(.3, .6), t, -14)
        if k in (2, 6): A('snap', bp(noise(T_(.05)), 1800, 6000) * np.exp(-tt(T_(.05)) / .006), t, -20, pan=.2)
        if k == 0: A('bass', pluck(note(notes[0]) - 12, bt * 1.8, .3, .5), t, -13)

# ------------------------------------------------------------------ 4. the artist motif (22.20 -> 28.00) + build to the drop
def artist(a, z):
    arp = ['A3', 'E4', 'A4', 'C5', 'E5', 'C5', 'A4', 'E4']; bt = .30
    for t, i in grid(a + .1, z, 60 / bt / 1, 1):
        m = arp[i % 8] if (i // 8) % 2 == 0 else ['F3', 'C4', 'F4', 'A4', 'C5', 'A4', 'F4', 'C4'][i % 8]
        A('keys', rhodes(note(m), .9, .55), t, -17, pan=(-.25 if i % 2 else .25))
    A('strings', pad([note('A2'), note('E3'), note('C4')], z - a, att=1.2, rel=.6, bright=1300, detune=.08), a, -19)

def build(a, drop):
    A('fx', riser(drop - a, 250, 7000, 1.0, .5), a, -11, p=.8)
    t = a; k = 0
    while t < drop - .02:                                  # snare roll, accelerating
        A('roll', snare(.12, 210, .7), t, -24 + 10 * (t - a) / (drop - a)); k += 1
        t += max(.035, .25 * (1 - (t - a) / (drop - a)) ** 1.5)
    A('fx', reverse_cymbal(min(1.4, drop - a)), drop - min(1.4, drop - a), -14)

# ------------------------------------------------------------------ 5. the showreel drop (half-time trap / cinematic)
def trap(a, z, rest=None):
    bpm = 140; bt = 60 / bpm
    BASS = ['D1', 'D1', 'A#0', 'C1']
    for t, i in grid(a, z, bpm, 4):                        # sixteenths
        if rest and rest[0] - .02 <= t < rest[1]: continue
        k = i % 16; bar = (i // 16) % 4
        if k in (0, 10): A('kick', kick(.5, 1.0, 160, 42), t, -6)
        if k == 8: A('clap', addl(clap(.3), snare(.25, 200, 1.0) * .6), t, -10)
        roll = bar % 2 == 1 and k >= 12
        if k % 2 == 0 or roll: A('hat', hat(.05), t, -21 + (3 if k % 4 == 0 else 0), pan=.2)
        if k == 0: A('bass', sub808(note(BASS[bar]), bt * 3.6, drive=2.0), t, -8)
        if k == 0 and bar % 2 == 0:
            A('pad', pad([note('D3'), note('F3'), note('A3'), note('C4')], bt * 7.8, att=.05, rel=.6, bright=1700), t, -17)
    A('hit', addl(nz(impact(2.2, 1.2, .9, .5)), nz(braam(note('D1'), 2.0, .9)) * .6), a, -4)

# ------------------------------------------------------------------ 6. LUMARC groove (casa's house groove, 112 BPM)
PROG = [['E3', 'B3', 'E4', 'G4', 'B4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4'], ['D3', 'A3', 'D4', 'F#4', 'A4']]
GBASS = ['E1', 'C2', 'G1', 'D2']
def groove(a, z, g=0.0, thin=None):
    bpm = 112; bt = 60 / bpm
    for t, i in grid(a, z, bpm, 1):
        th = thin and thin[0] <= t < thin[1]
        if not th: A('kick', kick(punch=1.0), t, -6 + g)
        if not th and i % 2 == 1: A('clap', clap(), t, -13 + g)
        A('hat', hat(), t + bt / 2, -18 + g - (6 if th else 0), pan=.25)
        if not th: A('hat', hat(), t + bt * .75, -24 + g, pan=-.25)
        if i % 4 == 0:
            k = (i // 4) % 4
            if not th: A('bass', sub808(note(GBASS[k]), bt * 3.9, drive=1.6), t, -10 + g)
            A('pad', pad([note(n) for n in PROG[k]], bt * 4.05, att=.02, rel=.4, bright=2400 if not th else 1200), t, -16 + g)
            if not th:
                for j, n in enumerate(PROG[k][2:] * 2):
                    A('arp', pluck(note(n) + 12, .3, .12, .8), t + j * bt / 2 + bt * 2, -22 + g, pan=(-.4 if j % 2 else .4))

# ------------------------------------------------------------------ 7. results: punchy 128
def punchy(a, z):
    bpm = 128; bt = 60 / bpm
    for t, i in grid(a, z, bpm, 1):
        A('kick', kick(.45, 1.1), t, -6)
        if i % 2 == 1: A('clap', clap(), t, -12)
        A('hat', hat(.05, open_=True), t + bt / 2, -20, pan=.2)
        if i % 4 == 0: A('bass', sub808(note(['A1', 'F1', 'C2', 'G1'][(i // 4) % 4]), bt * 3.9, drive=1.8), t, -10)
        if i % 2 == 0: A('stab', pad([note('A3'), note('C4'), note('E4')], bt * .45, att=.005, rel=.08, bright=3200), t, -17)

def pulse(a, hit, z):
    for t in np.arange(a, z - .05, 60 / 96):
        A('pulse', kick(.5, .7, 110, 38), t, -12)
        A('hat', tick(5200, .03, .5), t + 60 / 96 / 2, -26)
    A('pad', pad([note('F2'), note('C3'), note('A3')], hit - a, att=1.5, rel=.2, bright=800), a, -18)
    A('fx', riser(hit - a - .2, 200, 4500, 1.0, .4), a + .2, -15, p=.8)
    A('hit', addl(nz(impact(2.0, 1.0, .8, .5)), nz(braam(note('F1'), 1.6, .8)) * .5), hit, -5)

def final(a, z):
    bpm = 100; bt = 60 / bpm
    prog = [['F3', 'A3', 'C4', 'E4'], ['D3', 'F3', 'A3', 'C4'], ['A#2', 'D3', 'F3', 'A3'], ['C3', 'E3', 'G3', 'C4']]
    for t, i in grid(a, z, bpm, 1):
        if i % 4 == 0:
            k = (i // 4) % 4
            A('keys', sum(rhodes(note(n), bt * 4, .6) for n in prog[k]) / 3, t, -15, pan=-.1)
            A('bass', pluck(note(prog[k][0]) - 12, bt * 3.5, .4, .5), t, -12)
        A('kick', kick(.35, .7), t, -12 if i % 2 == 0 else -40)
        if i % 2 == 1: A('clap', clap(.2), t, -18)
        A('hat', shaker(.06, .8), t + bt / 2, -24, pan=.3)

# ------------------------------------------------------------------ SFX for the section cues
def stamp():
    n = T_(.45); t = tt(n)
    body = np.sin(2 * np.pi * (85 + 60 * np.exp(-t / .02)) * t) * np.exp(-t / .07) * 1.3
    slap = bp(noise(n), 300, 3500) * np.exp(-t / .018) * 1.4
    paper = hp(noise(n), 2500) * np.exp(-t / .05) * .35
    return (body + slap + paper).astype(np.float32)
def snap_():
    n = T_(.12); t = tt(n)
    return (bp(noise(n), 1500, 7000) * np.exp(-t / .007) * 1.6 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / .01) * .3).astype(np.float32)
def flatline(dur=1.4):
    n = T_(dur); t = tt(n); x = np.zeros(n, np.float32); f = 988
    for b in (0.0, .42):
        i, j = T_(b), T_(b + .12); x[i:j] = np.sin(2 * np.pi * f * t[:j - i]) * np.hanning(j - i) ** .3
    i = T_(.84); x[i:] = np.sin(2 * np.pi * f * t[:n - i]) * np.minimum(1, (dur - t[i:]) / .25)
    return x * .5
def scan(dur=.9):
    n = T_(dur); t = tt(n); f = 300 + 2600 * (t / dur) ** 1.4
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (.6 + .4 * np.sin(2 * np.pi * 32 * t))
    nzs = bp(noise(n), 1500, 7000) * (t / dur) * .35
    return ((tone * .4 + nzs) * np.minimum(1, t / .05) * np.minimum(1, (dur - t) / .12)).astype(np.float32)
def lock_():
    n = T_(.5); t = tt(n)
    clunk = np.sin(2 * np.pi * 180 * t) * np.exp(-t / .04) + lp(noise(n), 1200) * np.exp(-t / .015) * .8
    return (clunk + pad_to(metal(1700, .4, .12), n) * .45 + pad_to(np.pad(click(3600, .03, .6), (T_(.06), 0)), n) * .6).astype(np.float32)
def ff(dur=.8):
    n = T_(dur); t = tt(n); ph = (t / .07) % 1.0
    chirp = np.sin(2 * np.pi * (900 + 3200 * ph) * t) * (1 - ph) * .35
    w = whoosh(dur, .6, up=True); w = pad_to(w.mean(1) if w.ndim == 2 else w, n)
    return ((chirp + w * .8) * np.minimum(1, t / .03) * np.minimum(1, (dur - t) / .1)).astype(np.float32)
def counter(dur=1.0):
    n = T_(dur); out = np.zeros(n, np.float32); t = 0.0; k = 0
    while t < dur - .03:
        c = click(2600 + 400 * (k % 2), .025, .5); i = T_(t); out[i:i + len(c)] += c[:n - i]
        u = t / dur; t += .03 + .09 * (1 - np.sin(np.pi * u)) ** 2; k += 1
    return out
def film(dur=1.0):
    n = T_(dur); t = tt(n)
    rattle = hp(noise(n), 1500) * (np.sin(2 * np.pi * 24 * t) > .6) * .3
    return ((rattle + np.sin(2 * np.pi * 60 * t) * .05) * np.minimum(1, t / .1) * np.minimum(1, (dur - t) / .2)).astype(np.float32)
def crickets(dur):
    n = T_(dur); t = tt(n); env = np.zeros(n, np.float32)
    for g0 in np.arange(0, dur, .30):
        for c in range(3):
            s = T_(g0 + c * .045); e = min(n, s + T_(.03)); env[s:e] = np.hanning(e - s) if e > s else 0
    return (np.sin(2 * np.pi * 4600 * t) * env * .4).astype(np.float32)
def sting():
    out = np.zeros(T_(2.0), np.float32)
    for m, at, d, g in (('D2', 0, .22, .8), ('D2', .28, .22, .8), ('C#2', .58, .62, 1.1)):
        x = (reese(note(m), d) + reese(note(m) + 12, d) * .5) * g; i = T_(at); out[i:i + len(x)] += x[:len(out) - i]
    out = out[:T_(1.25)]; out[T_(.9):] *= np.linspace(1, 0, T_(1.25) - T_(.9)); return lp(out, 1400)
def glass(dur=.9, seed=0):
    r = np.random.default_rng(seed); n = T_(dur); t = tt(n); x = np.zeros(n, np.float32)
    for f in r.uniform(2400, 7800, 9):
        x += np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t / r.uniform(.12, .45)) * r.uniform(.3, 1)
    return (x * .25 + hp(noise(n), 3500) * np.exp(-((t - dur * .25) / (dur * .2)) ** 2) * .6).astype(np.float32)
def shatter(seed=0, dur=1.6, n_bits=60):
    r = np.random.default_rng(seed); n = T_(dur); out = np.zeros(n, np.float32)
    for _ in range(n_bits):
        i = int(r.uniform(0, .6) ** 1.8 * n); m = T_(.25); tt_ = np.arange(m) / SR
        out[i:i + m] += (np.sin(2 * np.pi * r.uniform(2500, 9500) * tt_) * np.exp(-tt_ / r.uniform(.02, .07)) * r.uniform(.2, 1))[:n - i]
    out[:T_(.35)] += hp(noise(T_(.35)), 1800) * np.exp(-np.arange(T_(.35)) / SR / .09) * 1.4
    return out
def knock(seed=0):
    r = np.random.default_rng(seed); n = T_(.35); t = tt(n)
    body = lp(noise(n), 420) * np.exp(-t / .035) * 3 + np.sin(2 * np.pi * (140 + 30 * r.random()) * t) * np.exp(-t / .05) * .8
    return (body + hp(noise(n), 2500) * np.exp(-t / .006) * .7).astype(np.float32)
def crack(seed=0, dur=.45):
    r = np.random.default_rng(seed); n = T_(dur); out = np.zeros(n, np.float32)
    for k in range(26):
        i = int((k / 26) ** 1.6 * n * .8 + r.uniform(0, 300)); m = T_(.03); tt_ = np.arange(m) / SR
        out[i:i + m] += (hp(noise(m), 3000) * np.exp(-tt_ / .004) * r.uniform(.3, 1))[:n - i]
    out += hp(noise(n), 4500) * np.exp(-tt(n) / .08) * .35
    out[:T_(.12)] += lp(noise(T_(.12)), 600) * np.exp(-tt(T_(.12)) / .02) * 1.2
    return out
def rewind(dur=.7):
    n = T_(dur); t = tt(n); f = 900 + 2600 * np.sin(np.pi * t / dur) ** 2; ph = 2 * np.pi * np.cumsum(f) / SR
    sq = np.sign(np.sin(ph * 3)) * .15 + np.sin(ph) * .35; mot = bp(noise(n), 800, 4000) * .3
    return ((sq + mot) * np.minimum(1, t / .03) * np.minimum(1, (dur - t) / .08)).astype(np.float32)
def thud():
    n = T_(.5); t = tt(n); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-t / .03)) * t) * np.exp(-t / .12)).astype(np.float32)
def clock_tick(i=0):
    n = T_(.12); t = tt(n); f = 2200 if i % 2 == 0 else 1700
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / .012) + .5 * noise(n) * np.exp(-t / .004)).astype(np.float32)
def stone():
    n = T_(.6); t = tt(n); return (np.sin(2 * np.pi * (55 + 40 * np.exp(-t / .05)) * t) * np.exp(-t / .18) * 1.2 + lp(noise(n), 700) * np.exp(-t / .06) * .8).astype(np.float32)
def block(seed=0):
    r = np.random.default_rng(seed); n = T_(.25); t = tt(n); f = r.uniform(180, 260)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / .045) + bp(noise(n), 400, 2500) * np.exp(-t / .012) * .6).astype(np.float32)
def wind(dur=2.0):
    n = T_(dur); t = tt(n); x = bp(noise(n), 300, 1400) * (.5 + .5 * np.sin(2 * np.pi * t / dur * 1.3) ** 2)
    return (x * np.minimum(1, t / .4) * np.minimum(1, (dur - t) / .5)).astype(np.float32)
def door():
    n = T_(.5); t = tt(n); return (hp(noise(n), 2500) * np.exp(-t / .008) * .8 + np.sin(2 * np.pi * 120 * t) * np.exp(-t / .05) * .9).astype(np.float32)
def switch():
    n = T_(.08); t = tt(n); return (hp(noise(n), 3000) * np.exp(-t / .004) + np.sin(2 * np.pi * 2400 * t) * np.exp(-t / .01) * .4).astype(np.float32)
def murmur(dur=1.5):
    n = T_(dur); x = np.zeros(n, np.float32)
    for k in range(6):
        c = 400 + 180 * k; x += bp(noise(n), c * .7, c * 1.5) * (.5 + .5 * np.sin(2 * np.pi * tt(n) * (3 + k * .7) + k)) ** 2
    return (x * np.minimum(1, tt(n) / .3) * np.minimum(1, (dur - tt(n)) / .4) * .3).astype(np.float32)

SFX = {
    'whoosh': lambda c: (whoosh(.5, .7), -.35, -10),
    'swoosh_up': lambda c: (whoosh(.55, .6, up=True), -.33, -9),
    'swoosh': lambda c: (whoosh(.45, .55, up=False), -.25, -10),
    'swipe': lambda c: (whoosh(.32, .45, up=True), -.14, -7),
    'flick': lambda c: (whoosh(.28, .35, up=True), -.1, -11),
    'zoom': lambda c: (whoosh(.32, .5, up=True), -.16, -11),
    'impact': lambda c: (impact(1.8, .9, .9, .4), 0, -5),
    'boom': lambda c: (addl(nz(impact(2.6, 1.2, .8, .6)), nz(braam(note('D1'), 2.2, .7)) * .5), 0, -4),
    'braam': lambda c: (braam(note(c.get('note', 'D1')), c.get('dur', 2.4), 1.0), 0, -5),
    'taiko': lambda c: (taiko(1.2), 0, -6),
    'thud': lambda c: (thud(), 0, -7),
    'tick': lambda c: (tick(2600, .05, .6), 0, -16),
    'clock': lambda c: (clock_tick(c.get('i', 0)), 0, -11),
    'glass': lambda c: (glass(.9, c.get('seed', 1)), 0, -12),
    'knock': lambda c: (knock(c.get('seed', 0)), 0, -5),
    'crack': lambda c: (crack(c.get('seed', 0), c.get('dur', .45)), 0, -7),
    'shatter': lambda c: (shatter(c.get('seed', 2), c.get('dur', 1.6)), 0, -5),
    'pop': lambda c: (glock(note('E6'), .4), 0, -15),
    'ding': lambda c: (bell(note(c.get('note', 'E6')), 1.2, .6), 0, -11),
    'glitch': lambda c: (glitch_burst(.3, c.get('seed', 3)), 0, -10),
    'riser': lambda c: (riser(max(.3, c.get('to', 0) - c['_t']), 300, 6000, .9, .4), 0, -12),
    'shimmer': lambda c: (shimmer([note('B5'), note('E6'), note('G#6')], 1.6, .8), 0, -15),
    'rewind': lambda c: (rewind(c.get('dur', .7)), 0, -11),
    'cash': lambda c: (glock(note('A6'), .8) + np.pad(glock(note('E6'), .8), (T_(.08), 0))[:T_(.8)], 0, -12),
    'click': lambda c: (tick(3200, .03, .5), 0, -17),
    'type': lambda c: (tick(3800 + 300 * (c.get('i', 0) % 3), .025, .4), 0, -21),
    'heart': lambda c: (glock(note('A6'), .5), 0, -15),
    'shutter': lambda c: (shutter(), 0, -12),
    'notify': lambda c: (glock(note('E6'), .4) + np.pad(glock(note('B6'), .4), (T_(.1), 0))[:T_(.4)], 0, -12),
    'scratch': lambda c: (scratch(.45), 0, -6),
    'crickets': lambda c: (crickets(c.get('dur', 1.5)), 0, -19),
    'sting': lambda c: (sting(), 0, -5),
    'shing': lambda c: (shing(1400, .9), 0, -12),
    'stone': lambda c: (stone(), 0, -6),
    'block': lambda c: (block(c.get('seed', 0)), 0, -12),
    'wind': lambda c: (wind(c.get('dur', 2.0)), 0, -14),
    'door': lambda c: (door(), 0, -8),
    'switch': lambda c: (switch(), 0, -12),
    'murmur': lambda c: (murmur(c.get('dur', 1.5)), 0, -16),
    'stamp': lambda c: (stamp(), 0, -3),
    'snap': lambda c: (snap_(), 0, -5),
    'flatline': lambda c: (flatline(c.get('dur', 1.4)), 0, -15),
    'scan': lambda c: (scan(c.get('dur', .9)), 0, -15),
    'lock': lambda c: (lock_(), 0, -7),
    'ff': lambda c: (ff(c.get('dur', .8)), 0, -11),
    'counter': lambda c: (counter(c.get('dur', 1.0)), 0, -15),
    'sub': lambda c: (sub_boom(1.6, 60, 28), 0, -6),
    'film': lambda c: (film(c.get('dur', 1.0)), 0, -16),
}

def score():
    END = E.VOICE_END - (TL[-1]['t1'] - TL[-1]['t0'])        # start of the end card (the smile)
    cheesy(0.0, TS(3) - .02)
    tension(TS(3), ON['MAXIMO'], TS(5))
    playful(TS(5), TS(8) - .02)
    artist(TS(8), TS(11) + .3)
    build(TS(11) + .4, ON['MAO_CERTA'])
    trap(ON['MAO_CERTA'], TS(19) - .02, rest=(ON['CLONE_END'], ON['TRES']))
    A('hit', addl(nz(impact(1.6, 1.0, .9, .4)), nz(sub_boom(1.2, 70, 30)) * .5), ON['TRES'], -6)
    # LUMARC: the stage goes dark on the cut (43.40, the section's 'switch'), the lights slam on at "-MARC" -> groove
    groove(ON['LIGHTS_ON'], TS(27) - .02, thin=(TS(21), ON['ESTRATEGIA'] - .05))
    A('hit', addl(nz(impact(2.0, 1.1, .8, .5)), nz(braam(note('E1'), 1.4, .7)) * .5), ON['LIGHTS_ON'], -6)
    A('hit', addl(nz(impact(2.2, 1.2, .9, .5)), nz(sub_boom(1.6, 64, 28)) * .6), ON['RESULTADO'], -5)
    punchy(TS(28), TS(31) - .02)
    A('hit', addl(nz(impact(2.4, 1.2, 1.0, .6)), nz(braam(note('A1'), 1.6, .9)) * .5), ON['GENERICO'], -5)
    pulse(TS(32), ON['NOVENTA'], TS(34) - .02)
    final(TS(34), END - .02)
    A('pad', pad([note(n) for n in ['F3', 'C4', 'F4', 'A4', 'C5']], DUR - END, att=.01, rel=1.2, bright=2200), END, -11)
    A('fx', shimmer([note('F5'), note('C6'), note('A6'), note('F6')], DUR - END, 1.8), END, -12)
    A('hit', addl(nz(impact(2.2, 1.0, .5, .5)), nz(sub_boom(2.0, 60, 30)) * .6), END, -6)
    # tape-stop into the twist ("Ah… e o resto desse vídeo?"): punchy groove dies in pitch over 0.35 s
    for k in ('kick', 'clap', 'hat', 'bass', 'stab'):
        if k in mix.stems:
            b = mix.stems[k]; i0, i1 = T_(TS(31) - .35), T_(TS(31))
            ts_ = pad_to(tape_stop(b[i0:i1], .35), i1 - i0); b[i0:i1] = ts_ * np.linspace(1, .2, i1 - i0)[:, None]; b[i1:i1 + T_(.3)] *= 0
    # hard silences: the record scratch, "O resultado?", the clone pause
    allm = lambda: [k for k in mix.stems if k not in ('sfx', 'hit')]
    mix.silence(TS(3) - .02, TS(3) + .30, stems=allm(), fade_ms=10)
    mix.silence(TS(27) - .02, TS(28) - .04, stems=allm(), fade_ms=12)                 # "O resultado?" (one hit)
    mix.silence(TS(19) - .02, ON['LIGHTS_ON'] - .01, stems=allm(), fade_ms=12)        # the dark stage before "-MARC"
    mix.sidechain('pad', [t for t, _ in grid(ON['MAO_CERTA'], END, 112, 1)], .4, .16)

def cues():
    missing = set()
    for t, kind, params in E.collect_cues():
        if kind not in SFX: missing.add(kind); continue
        params = dict(params, _t=t)
        x, off, g = SFX[kind](params)
        A('sfx', x, t + off, g + min(params.get('gain', 0), 3), pan=params.get('pan', 0))
    if missing: print('unknown cue kinds (skipped):', sorted(missing))

def write(x, path):
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm, check=True)

def render_split(gains, target_peak=.89):
    stems = {k: v * gains.get(k, 1.0) for k, v in mix.stems.items()}
    sfx = stems.pop('sfx', np.zeros((mix.n, 2), np.float32)); music = sum(stems.values())
    scale = target_peak / (np.abs(music + sfx).max() + 1e-9); tail = np.linspace(1, 0, T_(.3))[:, None]
    for x, name in ((music, 'music.wav'), (sfx, 'sfx.wav')):
        y = np.tanh(x * scale * 1.1) / 1.1; y[-T_(.3):] *= tail
        write(y, os.path.join(HERE, name))

def mux():
    out = os.path.join(E.OUT, 'lumarc-ia.mp4')
    af = ('[0:a]aresample=48000,highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=3[v][key][key2];[1:a]volume=0.30[m];[m][key]sidechaincompress=threshold=0.035:ratio=7:attack=15:release=300[md];'
          '[2:a]volume=0.32[s];[s][key2]sidechaincompress=threshold=0.1:ratio=2:attack=10:release=200[sd];'
          '[v][md][sd]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.SRC, 'tight.mov'), '-i', os.path.join(HERE, 'music.wav'),
                    '-i', os.path.join(HERE, 'sfx.wav'), '-filter_complex', af,
                    '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(E.OUT, 'mix.wav')], check=True)
    kb = min(int(28.6 * 8 * 1024 / DUR) - 192, 14000)                       # 2-pass to land under the 30 MB chat limit
    for ps in (1, 2):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.OUT, 'video.mp4'), '-i', os.path.join(E.OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
               '-c:v', 'libx264', '-preset', 'slow', '-tune', 'film', '-x264-params', 'aq-mode=3:aq-strength=1.0:deblock=-1,-1', '-b:v', f'{kb}k', '-pass', str(ps), '-passlogfile', os.path.join(E.OUT, 'x264'),
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}']
        subprocess.run(cmd + (['-f', 'mp4', '/dev/null'] if ps == 1 else [out]), check=True)
    print(out, os.path.getsize(out) / 1e6, 'MB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'mux': mux()
    else:
        score(); cues()
        render_split(dict(kick=.85, clap=.85, hat=.8, bass=.85, arp=.8, uke=1.0, whistle=.9))
        print('music ok', DUR)
