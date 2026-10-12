"""LUMARC Reel "Your video is the problem" — music bed + SFX (no voice) -> music.wav. Times = edit timeline (s).
120 BPM, grid anchored on the WOW drop. Hook hits at 0; the "scrolled past" feed goes lo-fi and tape-stops on the
fling; full drop on "This one gets watched"; breakdown under "The difference isn't the product"; hits on the
"how you show it" montage; end-card impact + shimmer."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *

C = json.load(open(os.path.join(HERE, 'cues.json')))
DUR, END = C['dur'], C['end']; WOW = C['wow'][0]; FEED = C['feed']; FLING = C['fling']; MON = C['montage']
BT = .5; OFF = WOW % BT
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
PROG = [['A2', 'E3', 'A3', 'C4', 'E4'], ['F2', 'C3', 'F3', 'A3', 'C4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4']]
BASS = ['A1', 'F1', 'C2', 'G1']
def bar_of(t): return int(round((t - OFF) / BT)) // 4

def groove(a, z, g=0.0, stem=''):
    for t in beats(a, z):
        i = int(round((t - OFF) / BT))
        A('kick' + stem, kick(punch=1.0), t, -4 + g)
        if i % 2 == 1: A('drums' + stem, clap(), t, -11 + g)
        A('drums' + stem, hat(), t + BT / 2, -17 + g, pan=.25)
        A('drums' + stem, hat(), t + BT * .75, -23 + g, pan=-.25)
    for t in beats(a, z):
        if int(round((t - OFF) / BT)) % 4: continue
        k = bar_of(t) % 4
        A('bass' + stem, sub808(note(BASS[k]), 1.9, drive=1.8), t, -8 + g)
        A('pad' + stem, pad([note(n) for n in PROG[k]], 2.05, att=.02, rel=.4, bright=2600), t, -14 + g)
        for j, n in enumerate(PROG[k][2:] * 2):
            A('arp' + stem, pluck(note(n) + 12, .3, .12, .8), t + j * BT / 2 + BT * 2, -22 + g, pan=(-.4 if j % 2 else .4))

# hook + "same product / same budget" — full groove from frame 0
A('fx', impact(2.0, 1.0, .9, .4), 0.0, -4, p=.95)
groove(0.0, FEED[0])
# feed: muffled lo-fi version, tape-stop on the fling, a beat of air
groove(FEED[0], FLING + .1, -2, stem='_lo')
for k in ('kick_lo', 'drums_lo', 'bass_lo', 'pad_lo', 'arp_lo'):
    mix.filter_range(k, FEED[0], FLING + .1, 'lp', 700)
lo = sum(mix.bus(k) for k in ('kick_lo', 'drums_lo', 'bass_lo', 'pad_lo', 'arp_lo'))
i0, i1 = T(FLING - .45), T(FLING + .1)
mix.bus('tape')[i0:i1] += tape_stop(lo[i0:i1].copy())
for k in ('kick_lo', 'drums_lo', 'bass_lo', 'pad_lo', 'arp_lo'): mix.bus(k)[i0:] = 0
for t in C['ticks']: A('fx', tick(3200, .05, .6), t, -14)
A('fx', whoosh(.5, .35, up=True), FLING - .1, -6)
A('fx', reverse_cymbal(1.0), WOW - 1.0, -9, p=.8)
# drop: "This one gets watched"
A('fx', impact(2.4, 1.0, .9, .5), WOW, -3, p=.95)
groove(WOW, C['wow'][1])
# breakdown: "The difference isn't the product" — pad + riser into the montage
for t in beats(C['wow'][1], MON[0]):
    if int(round((t - OFF) / BT)) % 4 == 0:
        A('pad', pad([note(n) for n in PROG[bar_of(t) % 4]], 2.05, att=.2, rel=.5, bright=1800), t, -12)
A('fx', riser(MON[0] - C['wow'][1], 300, 6000, .8, .4), C['wow'][1], -11, p=.85)
for t in [MON[0], 19.25, 19.55, 19.85]: A('fx', kick(punch=1.3, decay=.3, click=.5), t, -5); A('fx', clap(), t, -12)
# CTA groove (a bit lower), end card
groove(MON[1], END - .05, -2)
A('fx', impact(3.0, .9, .7, .7), END, -3, p=.95)
A('fx', shimmer([note('A4'), note('E5'), note('C6'), note('A5')], DUR - END, 1.6), END, -10)
A('pad', pad([note(n) for n in PROG[0]], DUR - END, att=.01, rel=1.2, bright=2200), END, -11)
# SFX
for t in C['cuts'][1:]:
    if all(abs(t - h) > .05 for h in (WOW, END, *[MON[0], 19.25, 19.55, 19.85])): A('fx', whoosh(.45, .7), t - .45 * .7, -13)
for t in C['pops']: A('fx', glock(note('E6'), .6), t, -21)
A('fx', glock(note('A6'), .9), C['sold'], -18); A('fx', glock(note('E6'), .9), C['sold'] + .08, -20)
mix.sidechain('pad', [t for t in beats(0, END)], .45, .16)
mix.sidechain('bass', [t for t in beats(0, END)], .5, .14)
mix.render(os.path.join(HERE, 'music.wav'), gains=dict(kick=.8, drums=.8, bass=.8, pad=.8, arp=.8))
print('ok', DUR)
