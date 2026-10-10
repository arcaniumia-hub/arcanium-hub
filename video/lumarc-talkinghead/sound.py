"""LUMARC talking-head Reel — music bed + SFX (no voice). Renders music.wav (48 kHz stereo).
Times are seconds on the edit timeline (== plate time). Reuses the synth kit of ../silence-hyper/sound/lib.py.
120 BPM grid anchored so a downbeat lands on the "like THIS" drop (22.55 s)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import json

CUES = json.load(open(os.path.join(HERE, 'cues.json')))
DUR = CUES['dur']; DROP = CUES['drop']; END = CUES['endcard']
BT = .5; OFF = DROP % BT
mix = Mix(DUR)
def nz(x, p=1.0):
    x = np.asarray(x, np.float32); return x / (np.abs(x).max() + 1e-9) * p
def A(stem, x, at, g=0.0, pan=0.0, p=None):
    if p is not None: x = nz(x, p)
    mix.add(stem, x, at=at, gain=db(g), pan=pan)
def beats(a, z):
    t = OFF + math.ceil((a - OFF) / BT) * BT; out = []
    while t < z - 1e-6: out.append(round(t, 4)); t += BT
    return out

# chords (A minor-ish, warm): Am  F  C  G
PROG = [['A2', 'E3', 'A3', 'C4', 'E4'], ['F2', 'C3', 'F3', 'A3', 'C4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4']]
BASS = ['A1', 'F1', 'C2', 'G1']
def bar_of(t): return int(round((t - OFF) / BT)) // 4

# --- section A: "before" — thin, muffled lo-fi loop (0 → 20.1)
for t in beats(0, 20.1):
    i = int(round((t - OFF) / BT))
    if i % 2 == 0: A('drA', kick(punch=.6, decay=.16), t, -9)
    else: A('drA', rim(), t, -16, pan=.2)
    A('drA', hat(), t + BT / 2, -24, pan=-.3)
for t in beats(0, 20.1)[::4]:
    ch = PROG[bar_of(t) % 4]
    A('padA', pad([note(n) for n in ch], 2.05, att=.08, rel=.3, bright=1100), t, -15)
mix.filter_range('padA', 0, 20.1, 'lp', 900)
# riser into the tension pause: "instead of presenting your product like this…"
A('fx', riser(DROP - 0.6 - 16.6, 300, 6000, .8, .4), 16.6, -10, p=.9)
# hard silence 20.15 → reverse swell into the drop
mix.silence(20.15, DUR, ['drA', 'padA'])
A('fx', reverse_cymbal(1.4), DROP - 1.4, -8, p=.8)

# --- section B: drop (22.55 → end card) — full beat
def full_beat(a, z, g=0.0):
    for t in beats(a, z):
        i = int(round((t - OFF) / BT))
        A('kick', kick(punch=1.0), t, -4 + g)
        if i % 2 == 1: A('drB', clap(), t, -11 + g)
        A('drB', hat(), t + BT / 2, -17 + g, pan=.25)
        A('drB', hat(), t + BT * .75, -23 + g, pan=-.25)
    for t in beats(a, z)[::4]:
        k = bar_of(t) % 4
        A('bass', sub808(note(BASS[k]), 1.9, drive=1.8), t, -8 + g)
        A('pad', pad([note(n) for n in PROG[k]], 2.05, att=.02, rel=.4, bright=2600), t, -14 + g)
        for j, n in enumerate(PROG[k][2:] * 2):
            A('arp', pluck(note(n) + 12, .3, .12, .8), t + j * BT / 2 + BT * 2, -22 + g, pan=(-.4 if j % 2 else .4))
A('fx', impact(2.4, 1.0, .9, .5), DROP, -3, p=.95)
A('fx', braam(note('A1'), 2.2, .8), DROP, -10)
full_beat(DROP, CUES['breakdown'][0])
# breakdown under "Because today…" — pad + soft pulse, builds to "remembered"
bd0, bd1 = CUES['breakdown']
for t in beats(bd0, bd1)[::4]:
    A('bdpad', pad([note(n) for n in PROG[bar_of(t) % 4]], 2.05, att=.3, rel=.5, bright=1800), t, -12)
for t in beats(bd0, bd1):
    A('bdpad', kick(punch=.5, decay=.12), t, -15)
A('fx', riser(2.6, 400, 5000, .7, .5), bd1 - 2.6, -12, p=.8)
full_beat(bd1, END - .05, -1)
# end card: impact + shimmer ring-out, no more beat
A('fx', impact(3.0, .9, .7, .7), END, -3, p=.95)
A('fx', shimmer([note('A4'), note('E5'), note('C6'), note('A5')], DUR - END, 1.8), END, -10)
A('pad', pad([note(n) for n in PROG[0]], DUR - END, att=.01, rel=1.2, bright=2200), END, -11)

# --- SFX
for t in CUES['whoosh']: A('fx', whoosh(.45, .7), t - .45 * .7, -14, pan=.1)
for t in CUES['hits']:   A('fx', kick(punch=1.2, decay=.25, click=.4), t, -9)
for t in CUES['ticks']:  A('fx', tick(2400, .06, .5), t, -24)
for t in CUES['pops']:   A('fx', glock(note('E6'), .6), t, -14)
for t in CUES['swipe']:  A('fx', whoosh(.5, .3, up=True), t, -10)

mix.sidechain('pad', [t for t in beats(DROP, END)], .45, .16)
mix.sidechain('bass', [t for t in beats(DROP, END)], .5, .14)
mix.render(os.path.join(HERE, 'music.wav'), gains=dict(drA=3.2, padA=3.2, bdpad=4.0, kick=.75, drB=.75, bass=.75, pad=.75, arp=.75), keep_silence=[(20.2, DROP - 1.45)])
print('ok', DUR)
