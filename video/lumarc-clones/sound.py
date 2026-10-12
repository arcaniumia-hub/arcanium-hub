"""LUMARC Reel "We're not real" — music bed + SFX (no voice) -> music.wav. Times = edit timeline (s), from cues.json.
Dark synth intro with glitches -> groove kicks in when clone #2 enters -> full groove in the clone lab and the
whip-panned week (Paris / investors) -> muzak + crickets for the taxes bit -> full groove for the CTA -> dead
silence on "And the real one?" -> ukulele + waves on the beach -> end-card impact."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *

C = json.load(open(os.path.join(HERE, 'cues.json')))
DUR, END = C['dur'], C['end']
BT = .5; OFF = C['trio'] % BT
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
PROG = [['D3', 'A3', 'D4', 'F4', 'A4'], ['A#2', 'F3', 'A#3', 'D4', 'F4'], ['F2', 'C3', 'F3', 'A3', 'C4'], ['C3', 'G3', 'C4', 'E4', 'G4']]
BASS = ['D2', 'A#1', 'F1', 'C2']
def bar_of(t): return int(round((t - OFF) / BT)) // 4

def groove(a, z, g=0.0, sfx='', light=False):
    for t in beats(a, z):
        i = int(round((t - OFF) / BT))
        A('kick' + sfx, kick(punch=.9), t, -5 + g)
        if not light and i % 2 == 1: A('drums' + sfx, clap(), t, -12 + g)
        A('drums' + sfx, hat(), t + BT / 2, -17 + g, pan=.25)
        if not light: A('drums' + sfx, hat(), t + BT * .75, -23 + g, pan=-.25)
        if i % 4 == 0:
            k = bar_of(t) % 4
            A('bass' + sfx, sub808(note(BASS[k]), 1.9, drive=1.6), t, -9 + g)
            A('pad' + sfx, pad([note(n) for n in PROG[k]], 2.05, att=.02, rel=.4, bright=2400), t, -15 + g)
            if not light:
                for j, n in enumerate(PROG[k][2:] * 2):
                    A('arp' + sfx, pluck(note(n) + 12, .3, .12, .8), t + j * BT / 2 + BT * 2, -21 + g, pan=(-.4 if j % 2 else .4))

# hook: three hits on the location flash, riser into "I'm not real"
for t in (0.0, .38, .76): A('fx', kick(punch=1.1, decay=.2, click=.5), t, -10); A('fx', tick(2600, .05, .6), t, -18)
A('fx', riser(C['hook'] - .1, 400, 5000, .8, .3), .1, -16, p=.8)
# intro: dark pad + digital blips + glitches
A('pad', pad([note('D2'), note('A2'), note('F3')], C['duo'] + .3, att=.6, rel=.4, bright=900), 0, -12)
A('fx', impact(1.6, .7, .8, .3), 0, -7, p=.9)
for i, t in enumerate(np.arange(.4, C['duo'], .37)): A('fx', tick(1800 + 600 * (i % 3), .04, .5), t, -24, pan=(-.5 if i % 2 else .5))
for k, t in enumerate(C['glitch']): A('fx', glitch_burst(.28, k), t, -8, p=.8)
# clone #2 enters: light groove; clone #3: full
A('fx', glock(note('A5'), .6), C['duo'], -12); A('fx', whoosh(.4, .7), C['duo'] - .28, -12)
T3 = C['lines'][2][2]                                  # end of "Yeah... same."
groove(C['duo'], T3, -5, light=True)
# (v3: no group entrance hit — clone #3 arrives on a cut)
groove(T3, C['tax'])
# taxes: muzak, then crickets
groove(C['tax'], C['crickets'] - .05, -6, sfx='_mz', light=True)
for k in ('kick_mz', 'drums_mz', 'bass_mz', 'pad_mz'): mix.filter_range(k, C['tax'], C['crickets'], 'lp', 650)
def cricket(dur):
    n = T(dur); t = tt(n); env = np.zeros(n, np.float32)
    for g0 in np.arange(0, dur, .55):
        for c in range(3):
            s = T(g0 + c * .045); e = min(n, s + T(.03)); env[s:e] = np.hanning(e - s) if e > s else 0
    return np.sin(2 * np.pi * 4600 * t) * env * .4
A('amb', cricket(C['back'] - C['crickets'] - .1), C['crickets'], -16, pan=.3)
# back in the lab: impact + full groove until "And the real one?"
A('fx', impact(2.0, .9, .8, .4), C['back'], -5, p=.9)
groove(C['back'], C['realone'] - .05)
A('fx', shimmer([note('D5'), note('A5'), note('F6')], 1.4, .7), C['logo'], -14)
A('fx', glock(note('A5'), .5), C['comment'], -18)
# beach: ukulele strum + waves
uk = [['D4', 'F#4', 'A4', 'D5'], ['G4', 'B4', 'D5', 'G5']]
for i, t in enumerate(np.arange(C['beach'], END + .6, .5)):
    for j, n in enumerate(uk[(i // 2) % 2]): A('uke', ukulele(note(n), .7), t + j * .018, -12)
w = pink(T(DUR - C['beach'])); w = lp(w, 900) * (.6 + .4 * np.sin(2 * np.pi * tt(len(w)) / 3.2)); A('amb', w, C['beach'], -16)
A('fx', impact(3.0, .9, .7, .7), END, -4, p=.95)
A('fx', shimmer([note('D5'), note('A5'), note('D6'), note('F#5')], DUR - END, 1.6), END, -11)
A('pad', pad([note(n) for n in ['D3', 'A3', 'D4', 'F#4']], DUR - END, att=.01, rel=1.2, bright=2200), END, -12)
# transitions
for t in C['whips']: A('fx', whoosh(.45, .7), t - .45 * .7, -9)
mix.sidechain('pad', beats(C['duo'], C['realone']), .45, .16)
mix.sidechain('bass', beats(C['duo'], C['realone']), .5, .14)
mix.render(os.path.join(HERE, 'music.wav'), gains=dict(kick=.8, drums=.8, bass=.8, arp=.8),
           keep_silence=[(C['realone'] + .02, C['beach'] - .3)])
print('ok', DUR)
