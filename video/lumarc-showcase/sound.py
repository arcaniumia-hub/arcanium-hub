"""LUMARC showcase Reel — score + SFX (no voice) -> music.wav, plus final mix -> out/lumarc-showcase.mp4.

    python3 sound.py          # music.wav (score + every section CUE)
    python3 sound.py mux      # voice (src/tight.mov) + music, ducked + loudness-normalised, muxed onto out/video.mp4

Score: 120 BPM, grid anchored so the word "LUMARC" (the logo reveal, s08) is a downbeat. Sections shape it:
hook pulse -> countdown (only clock + drone) -> drop at 6.04 -> lo-fi/filtered under the bad examples ->
silence on "They think..." -> swipe -> build under the glass panes -> boom on "first impression" -> fintech groove ->
riser into the LUMARC downbeat -> full showcase groove -> breath on "You run the business" -> hit on "ignore" ->
CTA groove -> final logo boom + shimmer.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'silence-hyper', 'sound'))
from lib import *
import engine as E

DUR = E.DUR
LUM = E.word_time('LUMARC', 21) or E.TL[21]['t0'] + 1.6
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
PROG = [['A2', 'E3', 'A3', 'C4', 'E4'], ['F2', 'C3', 'F3', 'A3', 'C4'], ['C3', 'G3', 'C4', 'E4', 'G4'], ['G2', 'D3', 'G3', 'B3', 'D4']]
BASS = ['A1', 'F1', 'C2', 'G1']
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

S = {n: E.span(*r) for n, r in dict(hook=(0, 1), insta=(2, 2), bad=(3, 6), nxt=(7, 9), prob=(10, 15), imp=(16, 17), trust=(18, 20),
                                      lum=(21, 21), show=(22, 25), ign=(26, 27), cta=(28, 29), end=(30, 32)).items()}
TS = lambda i: E.TL[i]['t0']

if not (len(sys.argv) > 1 and sys.argv[1] == 'mux'):
  # ---- score
  A('fx', impact(1.8, .9, .9, .3), 0.0, -4, p=.95)
  groove(0.0, TS(1), -3, light=True, arp=False)                                    # hook pulse
  A('drone', pad([note('A1'), note('E2'), note('A2')], 2.2, att=.6, rel=.3, bright=600), TS(1), -10)   # countdown: drone only
  A('fx', riser(1.9, 300, 5000, .9, .3), TS(1) + .1, -12, p=.8)
  groove(S['insta'][0], S['bad'][0])                                              # drop
  groove(S['bad'][0], S['nxt'][0] + 1.6, -4, sfx='_lo', light=True)              # lo-fi under the bad examples
  for k in ('kick_lo', 'drums_lo', 'bass_lo', 'pad_lo'): mix.filter_range(k, S['bad'][0], S['nxt'][0] + 1.6, 'lp', 700)
  # "They think..." -> silence until "next" swipe
  groove(S['prob'][0], S['imp'][0], -2, arp=False)
  A('fx', riser(S['imp'][1] - TS(17) + .2, 250, 6000, 1., .4), TS(17) - .2, -9, p=.85)
  groove(S['imp'][0], TS(17), -5, light=True, arp=False)
  groove(S['trust'][0], S['lum'][0])
  groove(S['lum'][0], LUM - .05, -6, light=True, arp=False)
  A('fx', riser(LUM - S['lum'][0], 300, 7000, 1., .5), S['lum'][0], -8, p=.9)
  groove(LUM, S['ign'][0])                                                        # showcase: full
  groove(S['ign'][0], TS(27), -7, light=True, arp=False)                           # "You run the business" breath
  A('fx', riser(TS(27) - S['ign'][0] + .6, 300, 5000, .9, .4), S['ign'][0], -12, p=.8)
  groove(TS(27), S['cta'][0])
  groove(S['cta'][0], S['end'][0] - .05, -2)
  A('pad', pad([note(n) for n in ['A2', 'E3', 'A3', 'C#4', 'E4']], DUR - S['end'][0], att=.01, rel=1.4, bright=2200), S['end'][0], -10)
  A('fx', shimmer([note('A4'), note('E5'), note('C#6'), note('A5')], DUR - S['end'][0], 1.8), S['end'][0], -12)
  mix.sidechain('pad', beats(0, S['end'][0]), .45, .16)
  mix.sidechain('bass', beats(0, S['end'][0]), .5, .14)

  # ---- section cues
  def glass(dur=.9, seed=0):
      r = np.random.default_rng(seed); n = T_(dur); t = tt(n); x = np.zeros(n, np.float32)
      for f in r.uniform(2400, 7800, 9):
          x += np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t / r.uniform(.12, .45)) * r.uniform(.3, 1)
      sw = hp(noise(n), 3500) * np.exp(-((t - dur * .25) / (dur * .2)) ** 2) * .6
      return (x * .25 + sw).astype(np.float32)
  def shatter(seed=0):
      r = np.random.default_rng(seed); n = T_(1.4); out = np.zeros(n, np.float32)
      for _ in range(40):
          i = int(r.uniform(0, .5) ** 1.8 * n); m = T_(.25); tt_ = np.arange(m) / SR
          out[i:i + m] += (np.sin(2 * np.pi * r.uniform(3000, 9000) * tt_) * np.exp(-tt_ / .04) * r.uniform(.2, 1))[:n - i]
      out[:T_(.3)] += hp(noise(T_(.3)), 2000) * np.exp(-np.arange(T_(.3)) / SR / .08)
      return out
  def T_(s): return int(round(s * SR))
  def clock_tick(i=0):
      n = T_(.12); t = tt(n); f = 2200 if i % 2 == 0 else 1700
      return (np.sin(2 * np.pi * f * t) * np.exp(-t / .012) + .5 * noise(n) * np.exp(-t / .004)).astype(np.float32)
  SFX = {
      'whoosh': lambda c: (whoosh(.5, .7), -.5 * .7, -10),
      'swoosh_up': lambda c: (whoosh(.55, .6, up=True), -.33, -9),
      'swipe': lambda c: (whoosh(.32, .45, up=True), -.14, -6),
      'impact': lambda c: (impact(1.8, .9, .9, .4), 0, -5),
      'boom': lambda c: (nz(impact(2.6, 1.2, .8, .6)) + nz(braam(note('A1'), 2.2, .7)) * .5, 0, -4),
      'tick': lambda c: (tick(2600, .05, .6), 0, -16),
      'clock': lambda c: (clock_tick(c.get('i', 0)), 0, -10),
      'glass': lambda c: (glass(.9, c.get('seed', 1)), 0, -12),
      'shatter': lambda c: (shatter(c.get('seed', 2)), 0, -9),
      'pop': lambda c: (glock(note('E6'), .4), 0, -16),
      'glitch': lambda c: (glitch_burst(.3, c.get('seed', 3)), 0, -10),
      'riser': lambda c: (riser(max(.3, c.get('to', 0) - c['_t']), 300, 6000, .9, .4), 0, -12),
      'shimmer': lambda c: (shimmer([note('A5'), note('E6'), note('C#7')], 1.6, .8), 0, -15),
      'cash': lambda c: (glock(note('A6'), .8) + np.pad(glock(note('E6'), .8), (T_(.08), 0))[:T_(.8)], 0, -12),
      'click': lambda c: (tick(3200, .03, .5), 0, -18),
      'type': lambda c: (tick(3800 + 300 * (c.get('i', 0) % 3), .025, .4), 0, -22),
      'heart': lambda c: (glock(note('A6'), .5), 0, -15),
      'shutter': lambda c: (hp(noise(T_(.08)), 2500) * np.exp(-tt(T_(.08)) / .02), 0, -14),
      'notify': lambda c: (glock(note('E6'), .4) + np.pad(glock(note('B6'), .4), (T_(.1), 0))[:T_(.4)], 0, -13),
  }
  missing = set()
  for t, kind, params in E.collect_cues():
      if kind not in SFX: missing.add(kind); continue
      params = dict(params, _t=t)
      x, off, g = SFX[kind](params)
      A('sfx', x, t + off, g + params.get('gain', 0), pan=params.get('pan', 0))
  if missing: print('unknown cue kinds (skipped):', sorted(missing))

  mix.render(os.path.join(HERE, 'music.wav'), gains=dict(kick=.8, drums=.8, bass=.8, arp=.8),
             keep_silence=[(E.TL[8]['t0'] + .25, E.TL[9]['t0'] - .15)])
  print('music ok', DUR)

def mux():
    out = os.path.join(E.OUT, 'lumarc-showcase.mp4')
    af = ('[0:a]aresample=48000,highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'apad=whole_dur=%.2f,asplit=2[v][key];[1:a]volume=0.42[m];[m][key]sidechaincompress=threshold=0.05:ratio=4:attack=25:release=320[md];'
          '[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]' % DUR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.SRC, 'tight.mov'), '-i', os.path.join(HERE, 'music.wav'), '-filter_complex', af,
                    '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000', os.path.join(E.OUT, 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.OUT, 'video.mp4'), '-i', os.path.join(E.OUT, 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}', out], check=True)
    print(out, os.path.getsize(out) / 1e6, 'MB')

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'mux':
    mux()
