"""SILENCE ONE — "On Mute" (hyper edit) — original score + sound design.

Renders ../music.wav (48 kHz, stereo, 16-bit, exactly 34.4 s) and ../music.mp3 (192 kbps).
150 BPM, beat b starts at b*0.4 s.  Source of truth: ../storyboard.json (cueSheet + every scene's "sound").

    python3 sound/score.py            # render + print verification numbers
    python3 sound/score.py --png      # also draw sound/score.png (spectrogram + RMS, time axis in beats)

Structure: every cue is written into a named stem (Mix bus). Section-level processing (lo-fi muzak chain,
tape stop, ANC sweeps, squeeze, gate steps, stutter, muffle, LP close) happens on stems / on the summed bus,
then glue compression -> look-ahead limiter (-1.3 dBFS) -> the SILENCE masks (exact zeros) -> end fade.
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib import *

DUR = 34.4; N = T(DUR)
SILENCES = [(b(13), b(15.5)), (b(37), b(39.5))]          # 5.2-6.2 s and 14.8-15.8 s -> exact zeros
mix = Mix(DUR)
KICKS = []                                                # every kick time (s) -> sidechain


def nz(x, peak=1.0):
    x = np.asarray(x, np.float32); return x / (np.abs(x).max() + 1e-9) * peak
def A(stem, x, beat, gain_db=0.0, pan=0.0, peak=None):
    if peak is not None: x = nz(x, peak)
    mix.add(stem, x, at=b(beat), gain=db(gain_db), pan=pan)
def K(beat, g=0.0, punch=1.0, stem='kick', **kw):
    A(stem, kick(punch=punch, **kw), beat, g); KICKS.append(b(beat))
def whoosh_at(stem, beat, dur=.5, peak=.75, g=0.0, pan=0.0):
    """whoosh whose loudest point lands exactly on `beat`."""
    A(stem, whoosh(dur, peak), beat - dur * peak / BEAT, g, pan)
def rev_into(stem, x, beat, length, g=0.0, curve=1.5, gap=.022):
    """reverse a sound so its (former) attack lands on `beat`; only the last `length` s is kept (fade-in).
    `gap`: the swell is cut a hair before the downbeat (a 'suck' of air) so the hit punches."""
    r = as_st(rev(as_st(x))); L = min(len(r), T(length)); r = r[-L:].copy()
    r *= (np.linspace(0, 1, L) ** curve)[:, None]
    gp = T(gap); r[len(r) - gp:] = 0; r[len(r) - gp - T(.006):len(r) - gp] *= np.linspace(1, 0, T(.006))[:, None]
    A(stem, r, beat - L / SR / BEAT, g)

D = {k: note(k) for k in ['D1', 'D2', 'A1', 'A2', 'G1', 'G2', 'F1', 'F2', 'C2', 'E2']}
CH = {   # pad voicings
    'Dm': ['D3', 'F3', 'A3', 'E4'], 'Dm9': ['D3', 'F3', 'A3', 'C4', 'E4'], 'Bb': ['Bb2', 'D3', 'F3', 'A3'],
    'Gm': ['G2', 'Bb2', 'D3', 'F3'], 'A': ['A2', 'C#3', 'E3', 'G3'], 'D': ['D3', 'F#3', 'A3', 'E4'],
    'G': ['G2', 'B2', 'D3', 'F#3'], 'F': ['F3', 'A3', 'C4', 'G4'], 'Bbmaj7': ['Bb2', 'D3', 'F3', 'A3'],
}
def nm(lst): return [note(x.replace('Bb', 'A#')) for x in lst]
def NT(s): return note(s.replace('Bb', 'A#').replace('Eb', 'D#'))


# =========================================================================== BEFORE  b0-11  (cheap muzak, C major)
def before():
    uke = {'C': ['G4', 'C4', 'E4', 'C5'], 'Am': ['A4', 'C4', 'E4', 'A4'], 'F': ['A4', 'C4', 'F4', 'A4']}
    def chord_at(bt): return 'C' if bt < 4 else 'Am' if bt < 8 else 'F'
    for k in range(26):                                   # 8th strums through b13 (tape stop eats the rest)
        bt = k * .5; down = k % 2 == 0; vel = 1.0 if bt % 2 == 0 else .8 if down else .6
        A('muzak', strum(nm(uke[chord_at(bt)]), .5, .010 if down else .007, down, vel, .55), bt, -4)
    bass = {'C': ('C3', 'G2'), 'Am': ('A2', 'E2'), 'F': ('F2', 'C3')}
    for k in range(13):                                   # bouncy plucked bass on quarters (root / fifth)
        r, f = bass[chord_at(k)]; A('muzak', pluck(NT(r if k % 2 == 0 else f), .38, .12, 1.6), k, -3)
    for k in range(0, 13, 2): A('muzak', kick(.3, .6, 120, 60, .08, .3), k, -8)
    for k in (1, 3, 5, 7, 9, 11): A('muzak', clap(), k, -2)
    for k in range(13 * 4):                               # shaker 16ths, -20 dB-ish
        A('muzak', shaker(.07, 1.0 if k % 2 else .55), k / 4, -16)
    mel = [(0, 1, 'G5'), (1, .5, 'E5'), (1.5, .5, 'G5'), (2, .5, 'A5'), (2.5, .5, 'G5'), (3, 1, 'E5'),
           (4, .5, 'C6'), (4.5, .5, 'B5'), (5, .5, 'A5'), (5.5, .5, 'E5'), (6, 1, 'A5'), (7, 1, 'G5'),
           (8, .5, 'F5'), (8.5, .5, 'A5'), (9, 1, 'C6'), (10, 1, 'A5'), (11, .75, 'G5'), (11.75, 1, 'F5')]
    A('muzak', whistle_line([(b(s), b(d) * .95, NT(m)) for s, d, m in mel], b(13)), 0, -1)
    for s, d, m in mel[::2]: A('muzak', glock(NT(m) + 12, .6), s, -12)        # glock doubling, sparse
    # ---- cheap SFX (own stem: lighter lo-fi)
    A('bsfx', glock(note('C6'), .5) + glock(note('G6'), .5) * .6, 0, -4)            # PowerPoint chime-whoosh
    A('bsfx', whoosh(.45, .35), 0, -6, peak=.6)
    A('bsfx', boing(200), 1, -2); A('bsfx', boing(260), 1.5, -3)
    A('bsfx', glock(note('C6'), .9), 2, 0)                                          # NEW!!! ding
    n = T(.35); A('bsfx', whoosh(.35, .5) * 1.0 + stereo(osc('sine', np.linspace(600, 1600, n), n) * np.sin(np.pi * tt(n) / .35) * .15), 4 - .5 * .35 / BEAT, -6)
    for k, bt in enumerate((5, 5.5, 6)): A('bsfx', bubble(380 + 60 * k, 1500 + 200 * k), bt, -3)
    whoosh_at('bsfx', 8, .3, .6, -8)                                                 # swish (swivel)
    for k, m in enumerate(('C6', 'E6', 'G6', 'C7')): A('bsfx', glock(note(m), .6), 9 + k * .25, -2)
    A('bsfx', boing(240), 9.75, -3); A('bsfx', click(4000, .03, .5), 9.75, -6)       # BUY NOW: boing + mouse click


# =========================================================================== BREAK  b11-16
def brk():
    A('fx', scratch(.25), 11, -7)                         # noisy formant scratch layer (the real scratch is varispeed, below)
    A('resid', vinyl(b(2)) * 5, 11, 0)                    # crackle tail
    n = T(b(2)); hum = sum(np.sin(2 * np.pi * 50 * h * tt(n)) / h for h in (1, 2, 3, 5)) * .02
    A('resid', hum, 11, 0)
    A('resid', downlifter(b(1)), 12, -10)                 # soft downlifter under the ANC sweep
    tik = click(6000, .05, .5) + np.sin(2 * np.pi * 6000 * tt(T(.05))) * exp_env(T(.05), .012) * .25
    A('fx', tik, 11.75, -8)
    # reversed braam + reversed cymbal sucking into b16 (b15.5-16)
    rev_into('fx', braam(D['D2'], 1.6, .8), 16, b(.5), -6)
    rev_into('fx', crash(1.2), 16, b(.5), -4)


# =========================================================================== THIS.  b16-20
def this_():
    A('fx', braam(D['D2'], 2.4, 1.0), 16, -2, peak=1)
    A('fx', impact(2.2, 1.0, .8), 16, -2, peak=1)
    A('fx', taiko(1.4), 16, -6, peak=1)
    A('fx', granular_glass(1.3, 260), 16, -6, peak=1)
    A('fx', crash(2.4), 16, -10, peak=1)
    A('bass', sub_boom(2.0, 75, 32), 16, -3)
    K(16, 0, 1.25)
    for bt in (16.5, 17, 17.25): A('fx', shutter(), bt, -8, pan=.3 if bt == 17 else -.3)
    A('fx', shing(1500, 1.2), 17.5, -8, peak=1); rev_into('fx', whoosh(.5, .2), 17.5, b(.5), -10)
    A('pad', pad(nm(['D2', 'A2']), b(2.2), att=.6, rel=.3, bright=700), 18, -12)
    A('bass', heartbeat(.5), 18.5, -2)
    n = T(.18); sw = hp(noise(n), 3500) * np.sin(np.pi * tt(n) / .18) ** 2 * .6           # 'shhwip' L -> R
    A('fx', pan_curve(lp(sw, 11000), np.linspace(-.95, .95, n)), 18.75, -10)
    n = T(b(.75)); u = tt(n) / b(.75); x = np.zeros(n, np.float32)                       # glass-harmonic shimmer rising
    for m in nm(['D5', 'A5', 'D6', 'E6']):
        x += np.sin(2 * np.pi * np.cumsum(mtof(m) * 2 ** (u * 2 / 12)) / SR) * u ** 2
    A('fx', reverb(x * .2, 2.0, .4), 19, -10)
    A('fx', tick(3200, .06, .4), 19.75, -12)


# =========================================================================== REVEAL  b20-24
def reveal():
    A('fx', reverb(bell(NT('D5'), 4.0, 1.6), 3.2, .45), 20, -6, peak=1)                 # ring TING
    A('bass', sub_boom(1.6, 65, 30), 20, -7)
    A('pad', pad(nm(['D2', 'A2']), b(4.2), att=.05, rel=.4, bright=700), 20, -13)
    A('pad', pad(nm(['E3', 'F3', 'A3']), b(4.2), att=.5, rel=.4, bright=1400), 20, -14)
    for bt in (20, 21, 22, 23): A('bass', heartbeat(.45), bt, -8 if bt > 20 else -11)
    # the world-noise sea: -16 dB bed, then low-passed + faded to nothing with the ring (b20.5-22.5)
    n = T(b(2.6)); sea = bp(world_noise(b(2.6), 21, .25, 1.2) + stereo(pink(n) * .6, 0, .7), 200, 3000)
    i0, i1 = T(b(.5)), T(b(2.5)); u = np.linspace(0, 1, i1 - i0)
    sea[i0:i1] = tv_lp_at(sea, i0, i1, 3000 * (60 / 3000) ** (u ** .8)) * ((1 - u) ** 1.6)[:, None]; sea[i1:] = 0
    A('sea', sea, 20, 0, peak=.5)
    A('fx', reverb(glock(note('D6'), 1.2) + glock(note('A6'), 1.2) * .7, 2.5, .45), 21, -10)
    for bt, p0 in ((22, -.8), (23, .8)):                                                 # light-sweep whooshes, panned
        w = whoosh(.6, .5)[:, 0] * 1.4; A('fx', pan_curve(w, np.linspace(p0, -p0, len(w))), bt - .6 * .5 / BEAT, -9)
    for k in range(8):                                                                   # 16th hats fade in -30 -> -14
        A('drums', hat(), 22 + k / 4, -28 + 14 * k / 7 + (2 if k % 2 == 0 else 0))
    A('fx', riser(b(2), 180, 3000, 1.0, .35), 22, -10, peak=1)
    whoosh_at('fx', 23.5, .25, .8, -8)
    rev_into('fx', impact(1.0, .4, 1.0), 24, b(.25), -6)


# =========================================================================== DROP 1  b24-28
def drop1():
    A('fx', impact(2.0, 1.0, .9), 24, -2, peak=1); A('fx', crash(2.2), 24, -7, peak=1)
    A('bass', sub808(D['D1'], 1.4, glide_from=D['D2']), 24, -3)
    for bt in (24, 25.5, 26, 27.5): K(bt, 0 if bt == 24 else -1.5)
    for bt in (25.5, 26, 27.5): A('bass', sub808(D['D1'], .55), bt, -4)
    A('drums', snare(.35), 26, -3); A('drums', clap(), 26, -5)
    for k in range(12):
        acc = 0 if k % 4 == 2 else -5 if k % 2 == 0 else -9
        A('drums', hat(), 24 + k / 4, acc - 4)
    for k in range(8): A('drums', hat(.03), 27 + k / 8, -15 + k * .9)                      # 1/32 hat roll b27-28
    A('bass', reese(D['D2'], b(4), 700), 24, -12)
    A('pad', pad(nm(CH['Dm']), b(4), .02, .3, 1600), 24, -12)
    for bt, m in ((24.5, 'D4'), (25, 'E4'), (25.5, 'F4'), (26, 'G4'), (26.5, 'A4'), (26.75, 'Bb4'), (27, 'C5')):
        A('synth', sawpluck(NT(m), .25, 6000, 600, .06) + pad_to(shutter(), T(.25)) * .3, bt, -6)
    rev_into('fx', crash(1.0), 28, b(.5), -6)                                             # reverse suck into b28


# =========================================================================== THE NOISE  b28-36
def noise_():
    A('fx', impact(1.6, .9, .9), 28, -3, peak=1); A('fx', crash(1.6), 28, -10, peak=1)
    for k in range(8): K(28 + k, -1)                                                      # 4/4 (b28-35; squeezed from b34)
    for k in range(16):                                                                   # reese 8ths D1+D2 -> A1+A2
        r = D['D1'] if k < 8 else D['A1']
        A('bass', reese(r, .19, 600) + reese(r + 12, .19, 1500) * .5, 28 + k / 2, -6)
    for k in range(16):
        r = D['D1'] if k < 8 else D['A1']
        A('bass', sub808(r if k % 2 == 0 else r + 12, .2), 28 + k / 2, -7)
    A('pad', pad(nm(['D3', 'F3', 'A3']), b(4), .05, .2, 1100), 28, -12)
    A('pad', pad(nm(['A2', 'C#3', 'E3', 'G3']), b(4), .05, .2, 1300), 32, -11)
    sn = [29, 31, 32, 32.5] + [33 + k / 4 for k in range(4)]                              # density doubling
    for i, bt in enumerate(sn): A('drums', snare(.3), bt, -4 + (i - 4) * .6 if bt >= 33 else -4)
    for bt in (29, 31): A('drums', clap(), bt, -7)
    for k in range(32): A('drums', hat(), 28 + k / 4, -12 if k % 2 else -8)
    # WORLD NOISE: swells +18 dB from b28 to b34 (kept going to b36 for the squeeze)
    n = T(b(8)); wn = world_noise(b(8), 33, 1.0, 1.0); wn = nz(wn, .7)
    gdb = np.clip(np.linspace(-18, 6, n), -18, 0); wn *= db(gdb)[:, None]
    A('noise', wn, 28, -3)
    for bt in (29, 30, 31, 32, 32.5, 33, 33.5):                                           # pitched-up glitches on doublings
        gb = varispeed(glitch_burst(.18, int(bt * 4)), 1.6, T(.11)); A('fx', fade(gb, .001, .01), bt, -9, pan=(bt * 7 % 3 - 1) * .6)
    A('fx', riser(b(6), 150, 2500, 1.0, .4), 28, -9, peak=1)
    # b34 the spin stops: metallic CHUNK + tom
    chunk = metal(210, .7, .18, (1, 1.62, 2.37, 3.15, 4.4)) + lp(impact(.7, .8, .6)[:, 0], 3000) * .5
    A('fx', chunk, 34, -3, peak=1); A('fx', tom(note('A1'), .6), 34, -4)
    A('fx', creak(b(3.75)), 34.05, -8, peak=1)


# =========================================================================== THE MUTE  b36-40
def mute():
    latch = click(3000, .05, .9) + np.sin(2 * np.pi * 120 * tt(T(.05))) * exp_env(T(.05), .015) * .6
    A('fx', latch, 36, -3)
    A('fx', impact(2.0, 1.1, 1.0), 36, -1, peak=1); A('fx', crash(2.0), 36, -7, peak=1)
    A('fx', braam(D['D2'], 2.0, 1.1), 36, -2, peak=1); K(36, 0, 1.2)
    # b39.5-40: reverse cymbal + reversed impact + reversed braam into DROP 2
    rev_into('fx', crash(1.4), 40, b(.5), -6)
    rev_into('fx', impact(1.5, 1.0, 1.0), 40, b(.5), -7)
    rev_into('fx', braam(D['D2'], 1.6, 1.0), 40, b(.5), -8, gap=.03)


# =========================================================================== DROP 2 / GATES / PEAK  b40-62
def yaw_deg(bt):
    """camera yaw of s08 (storyboard implementationNotes). sound/yaw.json (per frame, b40-48) overrides if present."""
    def seg(x, a, z): return min(1, max(0, (x - a) / (z - a)))
    def expoIO(x): return 0 if x <= 0 else 1 if x >= 1 else (2 ** (20 * x - 10)) / 2 if x < .5 else (2 - 2 ** (-20 * x + 10)) / 2
    if 44 <= bt < 46: return 180 + (0, -40, 60, 0)[int((bt - 44) * 2) % 4]                # hard-cut presets
    y = 120 * expoIO(seg(bt, 40, 40.5)) + 60 * seg(bt, 40.5, 44)
    return y + 120 * expoIO(seg(bt, 46, 46.5)) + 60 * seg(bt, 46.5, 48)
_yjs = os.path.join(HERE, 'yaw.json')
YAW = json.load(open(_yjs)) if os.path.exists(_yjs) else None
def spatial(x, beat):
    """auto-pan a mono sound by the camera yaw (pan = sin(yaw)); slight low-pass when 'behind' (cos(yaw) < 0)."""
    x = np.asarray(x, np.float32); n = len(x); bts = beat + tt(n) / BEAT
    if YAW is not None: yw = np.interp(bts, 40 + np.arange(len(YAW)) / 12, YAW)
    else: yw = np.array([yaw_deg(v) for v in bts[::96]]); yw = np.interp(np.arange(n), np.arange(len(yw)) * 96, yw)
    r = np.radians(yw); behind = np.clip(-np.cos(r), 0, 1)
    xf = x * (1 - behind * .6) + lp(x, 2500) * behind * .6
    return pan_curve(xf, np.sin(r))

HOOK = {  # (beat offset, length, note) — 2-bar phrases
    'Dm/Bb': [(0, .75, 'D5'), (.75, .75, 'F5'), (1.5, .5, 'A5'), (2, 1, 'C6'), (3, .5, 'A5'), (3.5, .5, 'F5'),
              (4, .75, 'D5'), (4.75, .75, 'F5'), (5.5, .5, 'A5'), (6, .75, 'C6'), (6.75, .25, 'D6'), (7, 1, 'A5')],
    'Gm/A':  [(0, .75, 'D5'), (.75, .75, 'F5'), (1.5, .5, 'G5'), (2, 1, 'Bb5'), (3, .5, 'G5'), (3.5, .5, 'F5'),
              (4, .75, 'E5'), (4.75, .75, 'G5'), (5.5, .5, 'A5'), (6, .75, 'C#6'), (6.75, .25, 'D6'), (7, 1, 'E6')],
}
def hook(phrase, start, g=-6, octave=False, until=None):
    for off, L, m in HOOK[phrase]:
        bt = start + off
        if until and bt >= until: break
        x = lead(NT(m), b(L) * .95, 3800)
        A('lead', x, bt, g)
        if octave and bt >= 52: A('lead', lp(lead(NT(m) + 12, b(L) * .95, 5000), 7000), bt, g - 7)

def groove(b0, b1, chords, sub=True, claps=True, hats_spatial=False, arp=None, arp_g=-11):
    """4/4 groove: kick every beat, claps on 2&4, 16th hats + open off-beats, 808 octave 8ths, pads.
    chords: list of (beat, chord, root808)."""
    for bt in np.arange(b0, b1, 1.0):
        K(bt, -1)
        if claps and (bt - b0) % 2 == 1: A('drums', clap(), bt, -3); A('drums', snare(.25), bt, -8)
    for k in range(int((b1 - b0) * 4)):
        bt = b0 + k / 4; acc = -6 if k % 4 == 2 else -9 if k % 2 == 0 else -13
        h = hat(); hs = spatial(h, bt) if hats_spatial else h
        A('drums', hs, bt, acc + (3 if hats_spatial else 0))
        if k % 4 == 2: oh = hat(open_=True); A('drums', spatial(oh, bt) if hats_spatial else oh, bt, -12)
    if hats_spatial:
        for bt in np.arange(b0, b1, 1.0): A('drums', spatial(ride(), bt), bt, -10)
    for i, (cb, ch, root) in enumerate(chords):
        ce = chords[i + 1][0] if i + 1 < len(chords) else b1
        A('pad', pad(nm(CH[ch]), b(ce - cb) + .1, .01, .2, 2400), cb, -10)
        if sub:
            for k in range(int((ce - cb) * 2)):
                m = root + (12 if k % 2 else 0); A('bass', sub808(m, .21, drive=2.6), cb + k / 2, -4 if k % 2 == 0 else -6)
        if arp:
            notes = nm(CH[ch])[1:] + [nm(CH[ch])[1] + 12]; seq = [0, 1, 2, 3, 2, 1, 3, 1]
            for k in range(int((ce - cb) * 4)):
                m = notes[seq[k % 8] % len(notes)] + 12; x = sawpluck(m, .14, 7000, 700, .05)
                if arp == 'spatial': A('arp', spatial(x, cb + k / 4), cb + k / 4, arp_g)
                else: A('arp', x, cb + k / 4, arp_g, pan=(.35 if k % 2 else -.35))

def drop2():
    A('fx', impact(2.2, 1.2, 1.0), 40, 0, peak=1); A('fx', crash(2.4), 40, -6, peak=1)
    A('fx', braam(D['D2'], 2.4, 1.1), 40, -2, peak=1)
    A('synth', sum(sawpluck(m, 1.2, 4500, 900, .35, 7, .25) for m in nm(CH['Dm9'])), 40, -4, peak=1)
    for bt, f in ((40, 1400), (40.5, 1870), (41, 2500)): A('fx', shing(f, .9), bt, -9, peak=1, pan=(bt - 40.5) * 1.2)
    whoosh_at('fx', 40, .35, .85, -8); whoosh_at('fx', 46, .35, .85, -8)
    groove(40, 48, [(40, 'Dm', D['D1']), (44, 'Bb', NT('Bb1'))], hats_spatial=True, arp='spatial', arp_g=-13)
    hook('Dm/Bb', 40, -7)
    for cb, r in ((40, D['D2']), (44, NT('Bb1'))):                                            # growling reese + wide pad lift: the loudest section
        A('bass', reese(r, b(4), 900), cb, -9); A('pad', pad(nm(CH['Dm9' if cb == 40 else 'Bb']) , b(4) + .1, .01, .2, 3200), cb, -11)
    for bt in (44, 44.5, 45, 45.5):                                                       # stutter-gated hits on the cuts
        hit = sawpluck(NT('D4'), .1, 6000, 800, .04) + snare(.1) * .6 + kick(.1) * .5
        A('fx', stutter(nz(hit, .8), .05 / 2, 4, .8), bt, -6)
    for k, m in enumerate(('A2', 'C3', 'D3', 'F3', 'G3', 'A3')): A('drums', tom(NT(m)), 46 + k / 4, -5 + k * .5)
    whoosh_at('fx', 48, .5, .9, -7); rev_into('fx', crash(1.2), 48, b(1), -6)

def gates():
    groove(48, 56, [(48, 'Gm', D['G1']), (52, 'A', D['A1'])])
    hook('Gm/A', 48, -7, octave=True)
    for bt in (48, 50, 52, 54):                                                           # spec slams + counter rattle
        A('drums', snare(.35), bt, -2); A('fx', impact(.9, .8, .9), bt, -8, peak=1)
        A('bass', sub808(D['D1'] if bt < 52 else D['A1'], .6, glide_from=D['D2']), bt, -4)
        for k in range(6): A('fx', tick(2600 + 180 * k, .04, .4), bt + k / 7.5, -14)      # 6 ticks at 30 fps (frame-rate)
    for bt in (48.5, 50.5, 52.5, 54.5): A('fx', shimmer(nm(['D6', 'A6']), 1.5, .5), bt, -14, peak=.5)
    for i, m in enumerate(('D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5')):            # the staircase
        w = tuned_whoosh(NT(m), .55, .85); bt = 49 + i
        A('fx', stereo(w, -.7 if i % 2 == 0 else .7), bt - .55 * .85 / BEAT, -6, peak=1)
    A('fx', riser(b(2.5), 200, 5000, 1.0, .5), 53.5, -8, peak=1)
    for k in range(4): A('drums', snare(.2), 55 + k / 4, -8 + k * 1.5)

def peak():
    A('fx', impact(2.0, 1.1, 1.0), 56, -1, peak=1); A('fx', crash(2.2), 56, -6, peak=1)
    groove(56, 64, [(56, 'Dm', D['D1']), (58, 'Bb', NT('Bb1')), (60, 'Gm', D['G1']), (61, 'A', D['A1'])],
           arp='plain', arp_g=-12)
    hook('Dm/Bb', 56, -8.5)
    A('bass', sub_boom(.9, 80, 34, 1.0) * np.minimum(1, tt(T(.9)) / .08), 57, -4)        # sub whomp (breath)
    st = sum(sawpluck(m, .1, 7000, 900, .04) for m in nm(CH['Bb'])) + snare(.1) * .5
    A('fx', stutter(nz(st, .9), .05, 8, .9), 58, -6)                                      # stutter (twist)
    A('fx', zap(.4), 58.5, -9, peak=1)                                                    # laser filter sweep
    A('fx', shutter(), 59, -6); A('fx', bell(NT('E6'), .8, .3), 59.5, -9, peak=.6)
    A('bass', sub808(D['G1'], .5, glide_from=D['G2'], drive=3), 60, -2); A('fx', impact(.7, .7, .5), 60, -8, peak=1)
    A('fx', tape_flick(.15), 60.5, -8, peak=1)
    for k in range(4):                                                                    # 16th snare fill pitched up (rides above the stutter)
        A('fill', varispeed(snare(.22), 1 + k * .12), 61 + k / 4, -6 + k)
    # 'Hear nothing.' b62-64: clean high pad + reversed inhale (bus muffle happens in master())
    n = T(b(2.2)); hp_ = sum(osc('tri', mtof(m), n) * .4 + osc('sine', mtof(m) * 2, n) * .1 for m in nm(['D6', 'A6']))
    A('clean', reverb(hp_ * env_adsr(n, .05, .2, .9, .25), 2.5, .4), 62, -24)
    n = T(b(.25)); inh = bp(noise(n), 800, 5000) * (tt(n) / tt(n)[-1]) ** 2.5
    A('clean', stereo(inh, 0, .6), 63.75, -17)


# =========================================================================== HERO  b64-70 (D major)
def hero():
    K(64, 0, 1.3); A('bass', sub_boom(2.2, 75, 36, 1.0), 64, -2); A('fx', crash(2.6), 64, -5, peak=1)
    A('fx', impact(2.4, .9, .7), 64, -3, peak=1); A('fx', braam(D['D2'] + 12, 2.4, .6), 64, -8, peak=1)
    A('synth', sum(sawpluck(m, 1.6, 5000, 1200, .5, 7, .22) for m in nm(CH['D'] + ['D4', 'F#4'])), 64, -4, peak=1)
    A('pad2', pad(nm(CH['D'] + ['D4']), b(7.6), .02, .6, 2600), 64, -8)
    A('pad2', pad(nm(['G2', 'B2', 'D3', 'F#3']), b(2) + .2, .15, .3, 2000), 66, -14)
    for bt in (65.5, 66, 67.5, 68, 69.5): K(bt, -3)
    for bt in (66, 68): A('drums', snare(.35), bt, -2); A('drums', clap(), bt, -6)
    for k in range(24): A('drums', hat(), 64 + k / 4, -11 if k % 2 == 0 else -15)
    for bt, m, L in ((64, 'D1', 1.4), (65.5, 'D1', .4), (66, 'G1', 1.4), (67.5, 'G1', .4), (68, 'D1', 1.6), (69.5, 'A1', .4)):
        A('bass', sub808(NT(m), b(L), drive=2.2), bt, -5)
    for bt, m, L in ((64.5, 'D5', .5), (65, 'F#5', 1), (66, 'A5', 1), (67, 'E5', 1.5), (68.5, 'D5', 1.4)):
        A('lead', lead(NT(m), b(L) * .95, 4200), bt, -6)
    A('fx', shimmer(nm(['D6', 'F#6', 'A6']), 2.0, .8), 65, -12, peak=.6)
    for k in range(4): A('fx', tick(3000, .04, .3), 66 + k / 8, -15)
    A('fx', bell(NT('A6'), 1.2, .5), 66.5, -12, peak=.6)
    for k, m in enumerate(('D6', 'A6', 'E7')): A('fx', reverb(glock(NT(m), 1.0), 2.0, .4), 67 + k / 8, -13, peak=.5)
    for bt, m in ((67.5, 'E7'), (68, 'D7')): A('fx', bell(NT(m), .8, .35), bt, -14, peak=.5)
    A('fx', downlifter(b(3)), 68.5, -9, peak=1)                                            # warm downward ring whoosh
    rev_into('fx', shimmer(nm(['D6', 'A6']), 1.5, .6), 70, b(.25), -12)


# =========================================================================== HANDOFF  b70-76 -> F major
def handoff():
    whoosh_at('fx', 70, .8, .3, -12)
    A('fx', sparkle(b(5.5), 22, 5, nm(['D6', 'F#6', 'A6', 'E6'])), 70, -17, peak=.6)
    A('fx', reverb(bell(NT('F5'), 5.0, 2.2), 3.5, .5), 71, -12, peak=1)
    A('pad2', pad(nm(['F2', 'C3', 'F3', 'A3', 'C4']), b(4.8), .25, .5, 2400), 71.5, -9)
    for k, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        x = ks(NT(m), 1.4, .7) * .7 + pluck(NT(m), 1.4, .35)
        A('synth2', delay(x, b(.75), .3, .25), 71.5 + k / 4, -8, pan=-.5 + k * .2)
    A('fx', sparkle(.8, 30, 9, nm(['F6', 'A6', 'C7'])), 73, -12, peak=.6)
    A('fx', lp(riser(b(2), 150, 1800, .7, .25), 3500), 74, -12, peak=1)
    rev_into('fx', reverb(bell(NT('F5'), 2, 1.2), 2.0, .5), 76, b(1.5), -10)


# =========================================================================== LUMARC END CARD  b76-86
def endcard():
    A('pad2', pad(nm(CH['F']), b(4.2), .08, .5, 2600), 76, -9)
    A('pad2', pad(nm(CH['Bbmaj7']), b(4.2), .3, .5, 2400), 80, -10)
    A('pad2', pad(nm(CH['F'] + ['C5']), b(2) + .3, .25, .7, 2400), 84, -9)
    for bt, m, L in ((76, 'F1', 4), (80, 'A#1', 4), (84, 'F1', 2)): A('endbass', sub808(NT(m), b(L), drive=1.2), bt, -20)
    for k, m in enumerate(('F5', 'A5', 'C6')): A('fx', reverb(bell(NT(m), 2.5, 1.2), 2.5, .4), 76 + k / 2, -14, peak=.7)
    for bt in (76, 78, 80, 82): K(bt, -11, .8, stem='endkick')
    for k in range(16):
        A('endhat', hat(.05), 76 + k / 2, -15 if k % 2 else -19)
    for cb, ch in ((76, 'F'), (77.5, 'F'), (78.5, 'F'), (80, 'Bbmaj7'), (81.5, 'Bbmaj7'), (82.5, 'Bbmaj7')):
        A('synth2', sum(rhodes(m + 12 if m < 55 else m, 1.6, .7) for m in nm(CH[ch])), cb, -9)
    for k in range(4): A('fx', tick(2800, .04, .25), 76 + k / 2, -24)                    # word ticks (-30 dB)
    A('fx', bubble(500, 1400, .06), 78, -10); A('fx', reverb(glock(NT('A6'), 1.0), 2.0, .4), 78, -14, peak=.6)
    for bt in (80, 82, 84): A('fx', shimmer(nm(['C7', 'F7', 'G6']), 2.0, .7), bt, -18, peak=.6)
    rev_into('fx', crash(1.5), 84, b(1.5), -14)
    for k, m in enumerate(('F5', 'A5', 'C6', 'F6')): A('fx', reverb(bell(NT(m), 2.4, 1.1), 3.0, .45), 84 + k / 4, -14, peak=.7)
    A('synth2', sum(rhodes(m + 12 if m < 55 else m, 2.4, .6) for m in nm(CH['F'])), 84, -10)


# =========================================================================== MASTER
GROOVE = ['kick', 'drums', 'bass', 'synth', 'lead', 'pad', 'noise', 'arp']
STEM_GAIN = {'kick': -4, 'bass': -4, 'pad': 13, 'lead': 11, 'arp': 10, 'synth': 7, 'drums': 2, 'muzak': 0, 'bsfx': 0, 'synth2': -5, 'pad2': 7}    # trims (dB), tuned by the numbers

def seg_idx(b0, b1): return T(b(b0)), T(b(b1))

def master():
    s = mix.stems
    for k in GROOVE + ['muzak', 'bsfx', 'resid', 'fx', 'clean', 'fill', 'pad2', 'synth2', 'sea', 'endkick', 'endhat']: mix.bus(k)
    # ---- BEFORE: cheap lo-fi chain (HP 250, LP 6k, near-mono, 10-bit crush, a little wow)
    m = s['muzak']; m = hp(m, 250, 4); m = width(m, .2)
    m = varispeed(m, 1 + .0025 * np.sin(2 * np.pi * .8 * tt(N)), N)
    m = lp(bitcrush(m, 10, 2), 6000, 4)
    # tape stop on the muzak bus at b11.0 (rate 1 -> 0 over 0.3 s, quadratic) + vinyl scratch (forward-back varispeed)
    i11 = T(b(11)); L = T(.3); src = m[i11:].copy()
    ts = varispeed(src, (1 - np.linspace(0, 1, L)) ** 2, L); m[i11:] = 0; m[i11:i11 + L] = fade(ts, 0, .02)
    rate = 3.2 * np.sin(2 * np.pi * np.arange(T(.25)) / T(.25))
    scr = varispeed(s['muzak'][T(b(10.5)):T(b(11.5))], 1.0 + rate, T(.25))
    s['fx'][i11:i11 + len(scr)] += fade(lp(hp(scr, 300), 7000), .004, .02) * db(2)
    s['resid'][i11:i11 + T(1.5)] += reverb(pad_to(ts, T(1.5)), 1.6, 1.0) * .25          # tape-stop room tail
    s['muzak'][:] = m
    bf = s['bsfx']; s['bsfx'][:] = lp(bitcrush(width(hp(bf, 220, 4), .3), 12, 1), 7000)
    # residue b12-13: low-passed 8 kHz -> 40 Hz with the ring (ein curve), amplitude to zero at b13
    i0, i1 = seg_idx(12, 13); u = np.linspace(0, 1, i1 - i0); ein = u ** 3
    r = s['resid']; r[i0:i1] = tv_lp_at(r, i0, i1, 8000 * (40 / 8000) ** ein) * ((1 - ein) ** 1.5)[:, None]; r[i1:] = 0
    # ---- sidechains (kick pump)
    kt = [t for t in KICKS if t < b(70)]
    mix.sidechain('bass', kt, .55, .12); mix.sidechain('pad', kt, .6, .2); mix.sidechain('synth', kt, .4, .15)
    mix.sidechain('lead', kt, .25, .12); mix.sidechain('noise', kt, .3, .15)
    mix.sidechain('arp', [t for t in kt if t >= b(56)], .8, .16); mix.sidechain('arp', [t for t in kt if t < b(56)], .45, .14)
    mix.sidechain('endhat', [b(x) for x in (76, 78, 80, 82)], .3, .2)
    # ---- b34-36: everything pitched down and squeezed (varispeed on the groove)
    i0, i1 = seg_idx(34, 36); n = i1 - i0; u = np.arange(n) / T(b(3.75)); rate = np.maximum(.42, 1 - .58 * np.minimum(1, u) ** .7)
    for k in GROOVE:
        seg = s[k][i0:i1 + T(.5)].copy(); s[k][i0:i1] = sat(varispeed(seg, rate, n) * 1.3, 1.6) / 1.3 * db(-4.5)
    # ---- b68.5-70: low-pass closing over the hero groove (pad2 sustains open into the handoff)
    i0, i1 = seg_idx(68.5, 70); u = np.linspace(0, 1, i1 - i0); fc = np.where(u < 1.25 / 1.5, 14000 * (280 / 14000) ** np.minimum(1, u / (1.25 / 1.5)), 280)
    fo = np.ones(i1 - i0, np.float32); fo[-T(.03):] = np.linspace(1, 0, T(.03))                # drums + bass out on b70
    for k in GROOVE + ['fill']: s[k][i0:i1] = tv_lp_at(s[k], i0, i1, fc) * fo[:, None]; s[k][i1:i1 + T(.5)] *= 0
    # ---- sum (with trims)
    main = sum(buf * db(STEM_GAIN.get(k, 0)) for k, buf in s.items() if k not in ('clean', 'fill'))
    # b35.5-36: master LP 16 kHz -> 60 Hz (exponential) + heavy 16th pumping
    i0, i1 = seg_idx(35.5, 36); n = i1 - i0; u = np.linspace(0, 1, n)
    ph = (tt(n) % (BEAT / 4)) / (BEAT / 4); pump = 1 - .75 * np.exp(-ph / .25) * np.minimum(1, ph / .05)
    main[i0:i1] = tv_lp_at(main, i0, i1, 16000 * (60 / 16000) ** u, order=2) * (pump * (1 + .6 * u))[:, None]
    main[T(b(37)):T(b(39.5))] = 0                                                          # nothing rings into the mute
    # section fader: PEAK sits a hair under DROP 2 (DROP 2 is the loudest section)
    fg = np.ones(N, np.float32); fg[T(b(56)) - T(.01):T(b(62))] = db(-1.2); main *= uniform_filter1d(fg, T(.02))[:, None]
    # b61-62: the whole mix gated into a rising 32nd-note stutter
    i0, _ = seg_idx(61, 62); slot = T(b(.125)); src = main[i0:i0 + 3 * slot].copy(); out = np.zeros((8 * slot, 2), np.float32)
    for k in range(8):
        piece = varispeed(src, 2 ** (k / 8), slot) * np.r_[np.ones(int(slot * .62)), np.zeros(slot - int(slot * .62))][:, None]
        out[k * slot:(k + 1) * slot] = fade(piece, .001, .004) * (.8 + .05 * k)
    main[i0:i0 + 8 * slot] = out
    clean_post = s['clean'] * db(STEM_GAIN.get('clean', 0)); clean_pre = clean_post.copy()
    clean_post[T(b(64)):] = 0; clean_pre[:T(b(64))] = 0                                   # tails past b64 go through the limiter
    total = main + s['fill'] * db(STEM_GAIN.get('fill', 0)) + clean_pre
    total = hp(total, 22, 2)                                                               # DC / rumble
    total[T(b(11)):] = lp(total[T(b(11)):], 15000, 2)                                      # tame the very top (AFTER)
    mid, side = (total[:, 0] + total[:, 1]) / 2, hp((total[:, 0] - total[:, 1]) / 2, 120, 2)   # mono below ~120 Hz
    total = np.stack([mid + side, mid - side], 1).astype(np.float32)
    pre = total.copy()
    total = compress(total, -16, 1.8, .015, .2, 0)
    i0, i1 = seg_idx(40, 48); makeup = db(LOUD_TARGET - rms_db(total[i0:i1])); total *= makeup   # DROP 2 = the reference level
    total, gr = limit(total, -1.8, .003, .08)
    # ---- post-limiter level moves (exact dB, no compressor recovery):
    # b36-37 dB dive in 1/16 steps: -18 / -36 + LP 2 kHz / -54 + LP 300 Hz / exact zero at b37
    g = np.ones(N, np.float32)
    for a, z, gd, f in ((36.25, 36.5, -18, None), (36.5, 36.75, -36, 2000), (36.75, 37.0, -54, 300)):
        i0, i1 = seg_idx(a, z)
        if f: total[i0:i1] = lp(total[i0 - T(.02):i1], f, 4)[T(.02):]
        g[i0:i1] = db(gd)
    g[T(b(37)):T(b(39.5))] = 0
    g = uniform_filter1d(g, T(.0015)); total *= g[:, None]
    # b62-64 'Hear nothing.': the music is low-passed to ~350 Hz and ducked 12 dB, the clean D6+A6 pad floats above; rips open on b64
    i0, i1 = seg_idx(62, 64); total[i0:i1] = lp(total[i0 - T(.05):i1], 350, 4)[T(.05):] * db(-12)
    print('makeup dB', round(float(to_db(makeup)), 1), 'muffle music', round(rms_db(total[T(b(62)):T(b(64))]), 1), 'clean', round(rms_db(clean_post[T(b(62)):T(b(64))] * makeup), 1))
    total += clean_post * makeup
    total, gr2 = limit(total, -1.8, .003, .08); gr = np.minimum(gr, gr2)                   # safety pass (no-op unless something poked over)
    # BEFORE trim: the muzak sits ~3 dB under the AFTER grooves (only ever turned down, so the ceiling holds)
    aft = np.concatenate([total[T(b(24)):T(b(34))], total[T(b(40)):T(b(61))]])
    trim = min(0.0, rms_db(aft) - 3.0 - rms_db(total[:T(b(11))])); total[:T(b(13))] *= db(trim); print('BEFORE trim dB', round(trim, 2))
    # ---- the SILENCE masks (after glue + limiter), exact zeros
    for a, z in SILENCES: total[T(a):T(z)] = 0
    total[:T(.003)] *= np.linspace(0, 1, T(.003))[:, None]
    f = T(.4); total[-f:] *= (np.cos(np.linspace(0, np.pi / 2, f)) ** 2)[:, None]; total[-1] = 0
    return total, pre, gr

LOUD_TARGET = -10.5


# =========================================================================== verification + picture
SECTIONS = [('BEFORE', 0, 11), ('BREAK', 11, 13), ('THIS.', 16, 20), ('REVEAL', 20, 24), ('DROP1', 24, 28), ('NOISE', 28, 34),
            ('SQUEEZE', 34, 36), ('MUTE', 36, 37), ('DROP2', 40, 48), ('GATES', 48, 56), ('PEAK', 56, 61), ('STUTTER', 61, 62),
            ('MUFFLE', 62, 64), ('HERO', 64, 68.5), ('HANDOFF', 70, 76), ('END', 76, 84), ('TAIL', 84, 86)]
def rms_db(x): return float(to_db(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12))
def report(y, gr):
    out = {}
    out['samples'] = len(y); out['seconds'] = len(y) / SR
    out['sample_peak_dbfs'] = round(float(to_db(np.abs(y).max())), 2)
    out['true_peak_dbfs'] = round(true_peak_db(y), 2)
    out['max_gain_reduction_db'] = round(float(-gr.min()), 1)
    out['silence'] = {f'{a:.1f}-{z:.1f}s': {'max_abs': float(np.abs(y[T(a):T(z)]).max()), 'n': T(z) - T(a)} for a, z in SILENCES}
    out['last_sample'] = float(np.abs(y[-1]).max()); out['last_10ms_peak_db'] = round(float(to_db(np.abs(y[-T(.01):]).max())), 1)
    out['sections_rms_dbfs'] = {nm_: round(rms_db(y[T(b(a)):T(b(z))]), 1) for nm_, a, z in SECTIONS}
    aft = np.concatenate([y[T(b(24)):T(b(34))], y[T(b(40)):T(b(61))]])
    out['limiter_gr_db_max_per_section'] = {nm_: round(float(-gr[T(b(a)):T(b(z))].min()), 1) for nm_, a, z in SECTIONS}
    out['AFTER_groove_rms'] = round(rms_db(aft), 1)
    out['BEFORE_minus_AFTER_db'] = round(out['sections_rms_dbfs']['BEFORE'] - out['AFTER_groove_rms'], 1)
    sp = np.abs(np.fft.rfft(y[T(b(16)):T(b(70)), 0] * np.hanning(T(b(54)))))
    fr = np.fft.rfftfreq(T(b(54)), 1 / SR); e = sp ** 2
    out['energy_share_above_8k_pct'] = round(float(e[fr > 8000].sum() / e.sum() * 100), 2)
    out['energy_share_below_120_pct'] = round(float(e[fr < 120].sum() / e.sum() * 100), 1)
    m, s_ = (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2
    out['low_end_side_ratio_db(<150Hz)'] = round(rms_db(lp(s_, 150, 4)) - rms_db(lp(m, 150, 4)), 1)
    return out

def draw_png(y, path):
    from PIL import Image, ImageDraw
    PX = 20; W = 86 * PX + 60; Hs, Hr = 360, 200; H = Hs + Hr + 60
    img = Image.new('RGB', (W, H), (12, 12, 16)); dr = ImageDraw.Draw(img)
    mono = y.mean(1); hop = int(SR * BEAT / PX); win = 2048
    nfr = len(mono) // hop; fmin, fmax = 30, 20000
    freqs = np.fft.rfftfreq(win, 1 / SR); rows = np.geomspace(fmin, fmax, Hs)[::-1]; ridx = np.searchsorted(freqs, rows).clip(0, len(freqs) - 1)
    spec = np.zeros((Hs, nfr)); hw = np.hanning(win)
    for i in range(nfr):
        c = i * hop; fr_ = mono[max(0, c - win // 2): c + win // 2]
        if len(fr_) < win: fr_ = np.pad(fr_, (0, win - len(fr_)))
        spec[:, i] = to_db(np.abs(np.fft.rfft(fr_ * hw))[ridx] / (win / 4))
    v = np.clip((spec + 100) / 100, 0, 1)
    rgb = np.stack([v ** .7 * 255, v ** 1.6 * 220, (1 - v) * v * 4 * 120 + v ** 3 * 100], -1).astype(np.uint8)
    img.paste(Image.fromarray(rgb).resize((86 * PX, Hs)), (40, 10))
    for f in (100, 1000, 10000):
        yy = 10 + int(np.searchsorted(-rows, -f)); dr.line([(36, yy), (40, yy)], fill=(200, 200, 200)); dr.text((2, yy - 6), f'{f // 1000}k' if f >= 1000 else str(f), fill=(200, 200, 200))
    top = Hs + 20
    for dbl in (0, -10, -20, -30, -40, -60):
        yy = top + int(-dbl / 60 * Hr); dr.line([(40, yy), (40 + 86 * PX, yy)], fill=(40, 40, 50)); dr.text((4, yy - 6), str(dbl), fill=(150, 150, 150))
    w = T(BEAT / 4)
    for i in range(0, len(mono) - w, w // 2):
        seg = y[i:i + w]; r = rms_db(seg); p = to_db(np.abs(seg).max())
        x0 = 40 + int(i / SR / BEAT * PX)
        if p > -120: dr.point((x0, top + int(min(60, -p) / 60 * Hr)), fill=(255, 120, 90))
        if r > -120: dr.line([(x0, top + Hr), (x0, top + int(min(60, -r) / 60 * Hr))], fill=(230, 200, 150))
    for a, z in SILENCES:
        dr.rectangle([40 + int(a / BEAT * PX), top - 4, 40 + int(z / BEAT * PX), top - 1], fill=(80, 160, 255))
    for bt in range(0, 87):
        x = 40 + bt * PX; col = (90, 90, 110) if bt % 4 else (200, 200, 220)
        dr.line([(x, H - 40), (x, H - 34 if bt % 4 else H - 28)], fill=col)
        if bt % 4 == 0: dr.line([(x, 10), (x, Hs + 10)], fill=(255, 255, 255, 40) if False else (60, 60, 80)); dr.text((x - 6, H - 24), str(bt), fill=col)
    for nm_, a, z in SECTIONS: dr.text((40 + int(a * PX) + 2, top + 2), nm_, fill=(140, 220, 160))
    img.save(path)


if __name__ == '__main__':
    import time; t0 = time.time()
    before(); brk(); this_(); reveal(); drop1(); noise_(); mute(); drop2(); gates(); peak(); hero(); handoff(); endcard()
    y, pre, gr = master()
    assert len(y) == N
    write_audio(y, os.path.join(ROOT, 'music.wav'), os.path.join(ROOT, 'music.mp3'))
    rep = report(y, gr); rep['render_s'] = round(time.time() - t0, 1)
    print(json.dumps(rep, indent=1, default=float))
    if '--png' in sys.argv: draw_png(y, os.path.join(HERE, 'score.png'))
    if '--stems' in sys.argv:
        print({k: round(rms_db(v), 1) for k, v in mix.stems.items()})
