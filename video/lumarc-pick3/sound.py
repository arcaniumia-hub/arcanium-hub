"""LUMARC "Pick three." (EN, US Meta ad) — score + SFX on the MASTER timeline (hooks A1 | A2 | A3 | BODY) ->
music.wav + sfx.wav; versions.py splices hook_k + body (picture, voice, music, sfx) into the three ads and mixes them.

    python3 sound.py          # music.wav + sfx.wav (master timeline)
    python3 versions.py       # out/lumarc-pick3-A1.mp4, -A2.mp4, -A3.mp4

Score: each hook has its own dry tension bed (sub + ticking hats + riser) that ends clean at its block end, so any hook
splices onto the body; BODY: a punchy, playful-confident groove under the three "pick two" jokes; it drops out to a
ticking tension pad for "That rule was written before AI"; the rule shatters on "AI" → a beat of silence → the LUMARC
DROP (big hit + confident groove); a build into "this."; the MONTAGE gets a half-time cinematic trap beat (the
section's trailer hits ride on top); breakdown for "You don't have to pick two anymore"; "Pick three." = the biggest
drop; groove under the CTA; end boom + shimmer.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import engine as E

DUR = E.DUR; TL = E.TL
TS = lambda i: TL[i]['t0']; TE = lambda i: TL[i]['t1']
# word onsets the score is keyed on (edit timeline; measured on src/tight16k.raw)
ON = dict(AI_SHATTER=18.90, THIS=29.55, PICK3=33.35)       # measured onsets (updated from the section reports)
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

def trombone():
    out = np.zeros(T_(2.2), np.float32)
    for k, (m, at, d) in enumerate((('D#4', 0, .38), ('D4', .42, .38), ('C#4', .84, .38), ('C4', 1.26, .9))):
        x = lead(note(m) - 12, d, 1500, .9 if k == 3 else .2); i = T_(at); out[i:i + len(x)] += x[:len(out) - i]
    return lp(out, 2200)
def buzzer(dur=.55):
    n = T_(dur); t = tt(n)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) * .5 + np.sign(np.sin(2 * np.pi * 116.5 * t)) * .5
    return (lp(x, 1800) * np.minimum(1, t / .01) * np.minimum(1, (dur - t) / .05) * .5).astype(np.float32)
def tap_():
    n = T_(.12); t = tt(n)
    return (bp(noise(n), 900, 5000) * np.exp(-t / .006) * 1.2 + np.sin(2 * np.pi * 420 * t) * np.exp(-t / .02) * .5).astype(np.float32)

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
    'trombone': lambda c: (trombone(), 0, -11),
    'buzzer': lambda c: (buzzer(c.get('dur', .55)), 0, -12),
    'tap': lambda c: (tap_(), 0, -8),
}

def hook_bed(a, z, hits=()):
    """dry tension bed for one hook block: sub drone + 16th-note ticks + a riser into its last beat; ends clean at z."""
    A('hbed', pad([note('D2'), note('A2')], z - a, att=.05, rel=.05, bright=700), a, -18)
    for t, i in grid(a, z - .05, 120, 4):
        A('hbed', tick(5200 if i % 4 else 3800, .03, .45), t, -27 if i % 4 else -22, pan=.2 if i % 2 else -.2)
    for t, i in grid(a, z - .05, 120, 1):
        if i % 2 == 0: A('hbed', kick(.35, .6, 120, 40), t, -16)
    A('hbed', riser(min(1.4, z - a - .2), 300, 5500, 1.0, .4), z - min(1.4, z - a - .2) - .05, -16, p=.8)
    for t in hits: A('hit', addl(nz(impact(1.2, .9, .9, .3)), nz(sub_boom(.8, 70, 35)) * .4), t, -8)

def bouncy(a, z):
    """the 'pick two' groove: playful, punchy (116 BPM): kick/clap, plucky bass, staccato stabs."""
    bpm = 116; bt = 60 / bpm
    prog = [['C3', 'E3', 'G3', 'B3'], ['A2', 'C3', 'E3', 'G3'], ['F2', 'A2', 'C3', 'E3'], ['G2', 'B2', 'D3', 'F3']]
    for t, i in grid(a, z, bpm, 2):
        k = i % 8; bar = (i // 8) % 4
        if k in (0, 3, 4): A('kick', kick(.4, 1.0), t, -7)
        if k in (2, 6): A('clap', clap(.25), t, -12)
        A('hat', hat(.04), t + bt / 4, -22, pan=.25)
        if k in (0, 3, 5): A('bass', pluck(note(prog[bar][0]) - 12, bt * .45, .12, .8), t, -10)
        if k in (1, 5): A('stab', pad([note(n) + 12 for n in prog[bar][1:]], bt * .3, att=.003, rel=.06, bright=3500), t, -17)

def tension_pad(a, z):
    A('pad', pad([note('D2'), note('A2'), note('D3'), note('F3')], z - a, att=.4, rel=.1, bright=900), a, -15)
    for t, i in grid(a, z, 120, 1): A('tick', clock_tick(i), t, -18)
    A('fx', riser(z - a, 200, 6000, 1.0, .5), a, -13, p=.8)

def lumarc_groove(a, z, g=0.0, light=False):
    bpm = 112; bt = 60 / bpm
    PROG = [['E3', 'B3', 'E4', 'G4', 'B4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4'], ['D3', 'A3', 'D4', 'F#4', 'A4']]
    BASS = ['E1', 'C2', 'G1', 'D2']
    for t, i in grid(a, z, bpm, 1):
        A('kick', kick(punch=1.0), t, -6 + g - (4 if light else 0))
        if i % 2 == 1: A('clap', clap(), t, -13 + g)
        A('hat', hat(), t + bt / 2, -18 + g, pan=.25)
        if not light: A('hat', hat(), t + bt * .75, -24 + g, pan=-.25)
        if i % 4 == 0:
            k = (i // 4) % 4
            A('bass', sub808(note(BASS[k]), bt * 3.9, drive=1.6), t, -10 + g)
            A('pad', pad([note(n) for n in PROG[k]], bt * 4.05, att=.02, rel=.4, bright=2400), t, -16 + g)
            if not light:
                for j, n in enumerate(PROG[k][2:] * 2):
                    A('arp', pluck(note(n) + 12, .3, .12, .8), t + j * bt / 2 + bt * 2, -22 + g, pan=(-.4 if j % 2 else .4))

def cinematic(a, z):
    """half-time trap/cinematic under the montage (140 BPM, 808 + claps + rolling hats)."""
    bpm = 140; bt = 60 / bpm
    for t, i in grid(a, z, bpm, 4):
        k = i % 16
        if k in (0, 10): A('kick', kick(.5, 1.1, 160, 42), t, -6)
        if k == 8: A('clap', addl(clap(.3), snare(.25, 200, 1.0) * .6), t, -10)
        if k % 2 == 0 or k >= 12: A('hat', hat(.05), t, -20, pan=.2)
        if k == 0: A('bass', sub808(note('D1'), bt * 3.6, drive=2.0), t, -8)
    A('hit', addl(nz(impact(2.2, 1.2, .9, .5)), nz(braam(note('D1'), 2.0, .9)) * .6), a, -4)

def score():
    B0, B1 = E.BLOCK_SPAN['B']
    END = TL[-1]['t0']                                                     # end card (the smile)
    for b in ('A1', 'A2', 'A3'):
        a, z = E.BLOCK_SPAN[b]; hook_bed(a, z)
    bouncy(B0, TL[19]['t0'] - .02)                                         # the three "pick two" jokes
    tension_pad(TL[19]['t0'], ON['AI_SHATTER'])                            # "That rule was written before AI"
    A('hit', addl(nz(impact(2.4, 1.2, 1.0, .6)), nz(sub_boom(1.6, 64, 28)) * .6), TL[20]['t0'], -4)   # the LUMARC drop
    lumarc_groove(TL[20]['t0'], ON['THIS'] - .02)
    A('fx', riser(ON['THIS'] - TL[24]['t0'], 250, 7000, 1.0, .5), TL[24]['t0'], -12, p=.8)              # build: faster / costs less
    cinematic(ON['THIS'], TL[28]['t0'] - .02)                              # the montage
    A('pad', pad([note('E3'), note('B3'), note('E4'), note('G4')], ON['PICK3'] - TL[28]['t0'] + .1, att=.15, rel=.1, bright=1500), TL[28]['t0'], -14)
    A('fx', riser(ON['PICK3'] - TL[28]['t0'] - .1, 300, 7500, 1.0, .5), TL[28]['t0'] + .1, -12, p=.8)
    A('hit', addl(nz(impact(2.8, 1.3, 1.0, .7)), nz(braam(note('E1'), 2.2, .9)) * .6), ON['PICK3'], -3)  # PICK THREE
    lumarc_groove(ON['PICK3'], END - .02, g=1)
    A('pad', pad([note(n) for n in ['E3', 'B3', 'E4', 'G#4', 'B4']], B1 - END, att=.01, rel=1.2, bright=2200), END, -11)
    A('fx', shimmer([note('E5'), note('B5'), note('G#6'), note('E6')], B1 - END, 1.8), END, -12)
    A('hit', addl(nz(impact(2.2, 1.0, .5, .5)), nz(sub_boom(2.0, 60, 30)) * .6), END, -6)
    allm = [k for k in mix.stems if k not in ('sfx', 'hit')]
    mix.silence(ON['AI_SHATTER'] + .05, TL[20]['t0'] - .01, stems=allm, fade_ms=15)               # the beat of stillness
    for b in ('A1', 'A2', 'A3'):                                                                   # hooks end dry, exactly
        z = E.BLOCK_SPAN[b][1]; mix.silence(z - .015, z + .0001, stems=[k for k in mix.stems if k != 'sfx'], fade_ms=25)
    mix.sidechain('pad', [t for t, _ in grid(TL[20]['t0'], END, 112, 1)], .4, .16)

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

if __name__ == '__main__':
    score(); cues()
    render_split(dict(kick=.85, clap=.85, hat=.8, bass=.85, arp=.8))
    print('music ok', DUR)
