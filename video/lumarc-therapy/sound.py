"""LUMARC "Couples Therapy — for brands": voice room + office ambience + score + SFX -> mix -> out/lumarc-therapy.mp4.

    python3 sound.py          # src/voice_room.wav, src/amb.wav, music.wav (score + every section CUE)
    python3 sound.py mux      # voice + music (ducked) + ambience, loudness-normalised, muxed onto out/video.mp4

Score: soft "waiting-room" lounge (Rhodes chords, upright bass, brushes, 92 BPM) under the session, dropping out for
the comedic beats (dead air + crickets after "…Creative?"); Kevin's croissant MOVIE gets a full trailer treatment
(braam, taiko, riser, title impact); after it the session music comes back brighter for "I'm listening" and the
LUMARC CTA; end card = soft boom + shimmer.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import engine as E

DUR = E.DUR; TL = E.TL; MOVIE = E.MOVIE
TS = lambda i: TL[i]['t0']; TE = lambda i: TL[i]['t1']
SR_ = SR
mix = Mix(DUR)
def nz(x, p=1.0):
    x = np.asarray(x, np.float32); return x / (np.abs(x).max() + 1e-9) * p
def A(stem, x, at, g=0.0, pan=0.0, p=None):
    if p is not None: x = nz(x, p)
    mix.add(stem, x, at=at, gain=db(g), pan=pan)
def T_(s): return int(round(s * SR))
def addl(a, b):
    a, b = as_st(a), as_st(b); n = max(len(a), len(b)); return pad_to(a, n) + pad_to(b, n)

# ------------------------------------------------------------------ lounge bed
BPM_L = 92; BT = 60 / BPM_L
CH = [['D3', 'F3', 'A3', 'C4', 'E4'], ['G2', 'F3', 'B3', 'E4', 'A4'], ['C3', 'E3', 'G3', 'B3', 'D4'], ['A2', 'G3', 'C4', 'E4', 'B4']]
BASS = [['D2', 'A2', 'D2', 'E2'], ['G1', 'D2', 'G2', 'F2'], ['C2', 'G2', 'C2', 'B1'], ['A1', 'E2', 'A2', 'C#2']]
def rhodes(midis, dur):
    n = T(dur); t = tt(n); x = np.zeros(n, np.float32)
    for m in midis:
        f = mtof(m); x += (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .25) + .08 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t / .04))
    trem = 1 + .18 * np.sin(2 * np.pi * 4.2 * t)
    return (x / len(midis) * np.exp(-t / 1.6) * np.minimum(1, t / .004) * trem * .5).astype(np.float32)
def upright(midi, dur):
    n = T(dur); t = tt(n); f = mtof(midi)
    x = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t) * np.exp(-t / .15)
    return (lp(x, 900) * np.exp(-t / .5) * np.minimum(1, t / .006) * .6).astype(np.float32)
def brush(dur=.25, g=1.0):
    n = T(dur); t = tt(n); return (bp(noise(n), 1800, 8000) * np.minimum(1, t / .03) * np.exp(-t / .09) * .25 * g).astype(np.float32)
def lounge(a, z, g=0.0, sfx='', bright=1.0):
    """bars of lounge from a to z (seconds), aligned to its own grid starting at 0."""
    t = math.ceil(a / BT - 1e-6) * BT
    while t < z - 1e-6:
        i = int(round(t / BT)); bar = (i // 4) % 4; beat = i % 4
        if beat == 0: A('keys' + sfx, rhodes([note(m) for m in CH[bar]], BT * 4), t, -14 + g, pan=-.15)
        if beat == 2 and bar % 2: A('keys' + sfx, rhodes([note(m) for m in CH[bar][2:]], BT * 2), t + BT * .5, -19 + g, pan=.2)
        A('bass' + sfx, upright(note(BASS[bar][beat]), BT * .95), t, -13 + g)
        A('drums' + sfx, brush(.3, .8 if beat % 2 else .5), t, -22 + g, pan=.2)
        A('drums' + sfx, brush(.12, .5), t + BT * .66, -27 + g, pan=-.2)
        if beat % 2 == 1: A('drums' + sfx, rim(), t, -30 + g, pan=.1)
        t += BT

# ------------------------------------------------------------------ comedic SFX
def crickets(dur):
    n = T(dur); t = tt(n); env = np.zeros(n, np.float32)
    for g0 in np.arange(0, dur, .55):
        for c in range(3):
            s = T(g0 + c * .045); e = min(n, s + T(.03)); env[s:e] = np.hanning(e - s) if e > s else 0
    return (np.sin(2 * np.pi * 4600 * t) * env * .4).astype(np.float32)
def sad_trombone():
    out = np.zeros(T(2.2), np.float32)
    for k, (m, at, d) in enumerate((('D#4', 0, .38), ('D4', .42, .38), ('C#4', .84, .38), ('C4', 1.26, .9))):
        x = lead(note(m) - 12, d, 1500, .9 if k == 3 else .2); i = T(at); out[i:i + len(x)] += x[:len(out) - i]
    return lp(out, 2200)
def sting():
    """dramatic 'dun dun DUNNN' (low brass-ish stabs)."""
    out = np.zeros(T(2.0), np.float32)
    for m, at, d, g in (('D2', 0, .22, .8), ('D2', .28, .22, .8), ('C#2', .58, .62, 1.1)):
        x = (reese(note(m), d) + reese(note(m) + 12, d) * .5) * g; i = T(at); out[i:i + len(x)] += x[:len(out) - i]
    out = out[:T(1.25)]; out[T(.9):] *= np.linspace(1, 0, T(1.25) - T(.9))       # short tail: never under the next line
    return lp(out, 1400)
def tissue():
    n = T(.45); t = tt(n); return (bp(noise(n), 2000, 7000) * np.sin(np.pi * t / .45) ** 2 * .35).astype(np.float32)
def ping():
    return (glock(note('B6'), .35) + np.pad(glock(note('E7'), .35), (T(.09), 0))[:T(.35)]).astype(np.float32)
def clock_tick(i=0):
    n = T(.08); t = tt(n); f = 2100 if i % 2 == 0 else 1800
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / .008) + .4 * noise(n) * np.exp(-t / .003)).astype(np.float32)
def zoom_whoosh():
    return whoosh(.32, .5, up=True)

SFX = {
    'whoosh': lambda c: (whoosh(.5, .7), -.35, -11),
    'swoosh_up': lambda c: (whoosh(.55, .6, up=True), -.33, -10),
    'swipe': lambda c: (whoosh(.32, .45, up=True), -.14, -8),
    'zoom': lambda c: (zoom_whoosh(), -.16, -12),                 # crash-zoom punch-in
    'impact': lambda c: (impact(1.8, .9, .9, .4), 0, -6),
    'boom': lambda c: (addl(nz(impact(2.6, 1.2, .8, .6)), nz(braam(note('D1'), 2.2, .7)) * .5), 0, -5),
    'braam': lambda c: (braam(note(c.get('note', 'D1')), c.get('dur', 2.4), 1.0), 0, -5),
    'taiko': lambda c: (taiko(1.2), 0, -6),
    'thud': lambda c: (heartbeat(.5, 60, 1.0), 0, -8),
    'tick': lambda c: (tick(2600, .05, .6), 0, -16),
    'clock': lambda c: (clock_tick(c.get('i', 0)), 0, -14),
    'pop': lambda c: (glock(note('E6'), .4), 0, -16),
    'ding': lambda c: (bell(note(c.get('note', 'E6')), 1.2, .6), 0, -12),
    'notify': lambda c: (ping(), 0, -13),
    'heart': lambda c: (glock(note('A6'), .5), 0, -15),
    'type': lambda c: (click(3600 + 300 * (c.get('i', 0) % 3), .03, .4), 0, -20),
    'click': lambda c: (click(3200, .03, .5), 0, -18),
    'shutter': lambda c: (shutter(), 0, -12),
    'scratch': lambda c: (scratch(.45), 0, -8),                    # record scratch
    'crickets': lambda c: (crickets(c.get('dur', 1.5)), 0, -20),
    'trombone': lambda c: (sad_trombone(), 0, -12),               # wah-wah-wah-waaah
    'sting': lambda c: (sting(), 0, -9),                          # dun dun DUNNN
    'tissue': lambda c: (tissue(), 0, -14),
    'riser': lambda c: (riser(max(.3, c.get('to', 0) - c['_t']), 300, 6000, .9, .4), 0, -12),
    'shimmer': lambda c: (shimmer([note('D5'), note('A5'), note('F#6')], 1.6, .8), 0, -15),
    'cash': lambda c: (glock(note('A6'), .8) + np.pad(glock(note('E6'), .8), (T(.08), 0))[:T(.8)], 0, -12),
    'glitch': lambda c: (glitch_burst(.3, c.get('seed', 3)), 0, -12),
    'shing': lambda c: (shing(1400, .9), 0, -12),
}

def score():
    M0, M1 = MOVIE
    lounge(0.0, TS(10) - .05, 7)                                       # the session…
    # "…Creative?" -> dead air (crickets come from the section cue) until "My algorithm cried."
    lounge(TS(11) - .02, M0 - .30, 8)                                    # …continues to the movie
    for k in ('keys', 'bass', 'drums'):
        if k in mix.stems: mix.stems[k][T(M0 - .30):] *= 0
    # the MOVIE: trailer treatment
    A('trailer', braam(note('D1'), 2.0, 1.0), M0, -4)
    A('trailer', taiko(1.2), M0 + .02, -7)
    A('trailer', pad([note('D3'), note('A3'), note('F4')], M1 - M0, att=.3, rel=.4, bright=1600), M0, -12)
    A('trailer', riser(M1 - M0 - 1.3, 250, 7000, 1., .5), M0 + .3, -12)
    for k, at in enumerate((M0 + 1.15, M0 + 1.75, M0 + 2.2)): A('trailer', taiko(1.0), at, -8 - k)
    A('trailer', addl(nz(impact(2.4, 1.2, .9, .6)), nz(braam(note('D1'), 1.6, .9)) * .6), M1 - 1.15, -3)
    # after the movie: bright session groove under "I'm listening" + CTA
    lounge(TS(16) + .5, E.VOICE_END - .05, 4, sfx='2', bright=1.2)
    A('pad', pad([note(n) for n in ['D3', 'A3', 'D4', 'F#4', 'A4']], DUR - E.VOICE_END, att=.01, rel=1.4, bright=2200), E.VOICE_END, -11)
    A('fx', shimmer([note('D5'), note('A5'), note('F#6'), note('D6')], DUR - E.VOICE_END, 1.8), E.VOICE_END, -12)
    A('fx', addl(nz(impact(2.2, 1.0, .5, .5)), nz(sub_boom(2.0, 60, 30)) * .6), E.VOICE_END, -7)

def cues():
    missing = set()
    for t, kind, params in E.collect_cues():
        if kind not in SFX: missing.add(kind); continue
        params = dict(params, _t=t)
        x, off, g = SFX[kind](params)
        A('sfx', x, t + off, g + params.get('gain', 0), pan=params.get('pan', 0))
    if missing: print('unknown cue kinds (skipped):', sorted(missing))

def write(x, path):
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm, check=True)

def voice_room():
    """one small furnished office for everyone: gentle EQ + short room."""
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(E.SRC, 'voice_dry.wav'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                       capture_output=True, check=True).stdout
    x = np.frombuffer(b, np.float32).copy(); x = lp(hp(x, 85), 14500)
    y = reverb(np.concatenate([x, np.zeros(T(.6), np.float32)]), size=.35, mix=.07, damp=5200, predelay=.006)[:len(x)]
    write(y, os.path.join(E.SRC, 'voice_room.wav'))

def ambience():
    """quiet office: room tone, a wall clock, faint street through the window. Silent during the MOVIE."""
    n = T(DUR); out = np.zeros(n, np.float32)
    rt = lp(pink(n), 700); out += rt / (np.sqrt((rt ** 2).mean()) + 1e-9) * db(-54)
    st = lp(noise(n), 260) * (.7 + .3 * np.sin(2 * np.pi * tt(n) / 7.0)); out += st / (np.sqrt((st ** 2).mean()) + 1e-9) * db(-60)
    for k, t in enumerate(np.arange(.5, DUR, 1.0)):
        c = clock_tick(k) * db(-40); i = T(t); out[i:i + len(c)] += c[:n - i]
    M0, M1 = MOVIE; f = T(.15)
    out[T(M0):T(M1)] = 0; out[T(M0) - f:T(M0)] *= np.linspace(1, 0, f); out[T(M1):T(M1) + f] *= np.linspace(0, 1, f)
    write(stereo(out, 0, .4), os.path.join(E.SRC, 'amb.wav'))

def mux():
    out = os.path.join(E.OUT, 'lumarc-therapy.mp4')
    af = ('[0:a]aresample=48000,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];[1:a]volume=0.32[m];[m][key]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=300[md];'
          '[2:a]volume=1.0[am];[v][md][am]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.SRC, 'voice_room.wav'), '-i', os.path.join(HERE, 'music.wav'),
                    '-i', os.path.join(E.SRC, 'amb.wav'), '-filter_complex', af, '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000',
                    os.path.join(E.OUT, 'mix.wav')], check=True)
    kb = min(14000, int(28.6 * 8 * 1024 / DUR) - 192)                      # 2-pass to land under the 30 MB chat limit
    for ps in (1, 2):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.OUT, 'video.mp4'), '-i', os.path.join(E.OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
               '-c:v', 'libx264', '-preset', 'slow', '-b:v', f'{kb}k', '-pass', str(ps), '-passlogfile', os.path.join(E.OUT, 'x264'),
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}']
        subprocess.run(cmd + (['-f', 'mp4', '/dev/null'] if ps == 1 else [out]), check=True)
    print(out, os.path.getsize(out) / 1e6, 'MB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'mux': mux()
    else:
        voice_room(); ambience(); score(); cues()
        mix.render(os.path.join(HERE, 'music.wav'), gains=dict(bass=.9, drums=.8))
        print('sound ok', DUR)
