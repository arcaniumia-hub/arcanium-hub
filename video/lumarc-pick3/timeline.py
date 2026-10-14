"""EDL for the "Pick three." ad (EN, US Meta ads) — HeyGen take on green (src/take.mp4, 48.8 s, 25 fps), seated waist-up.

MASTER timeline = three alternative HOOK blocks (A1, A2, A3) followed by the BODY block. Each hook is a self-contained
opening; the deliverables are three ads: hook_k + body (see versions.py). Block boundaries sit on the 0.2 s grid (a
multiple of both 1/25 and 1/30 s) so blocks can be cut and spliced frame-exactly.

ISL = (block, start, end, caption, join, hold)   — speech islands measured on the take (10 ms RMS, -40 dB)
    caption  '|' page breaks, '*' emphasis, None = silent
    join     True: continues the previous island in the same source run (natural pause kept, no jump)
    hold     extra seconds of the take's own silent pause kept after the island
Islands are cut with PRE / POST padding; every non-joined island start is a JUMP in the take. A tuple with start=None is
an INSERT: (block, None, (src_in, src_out), caption, False, 0) — a silent source range used as picture-less time (the
avatar is hidden there: the portfolio montage)."""
G = 0.04
def snap(x, g=G): return round(round(x / g) * g, 2)
PRE, POST = 0.10, 0.12
ISL = [
    # ---- hook A1
    ('A1', 0.20, 0.51, "*FAST.", False, 0),
    ('A1', 1.00, 1.20, "*CHEAP.", False, 0),
    ('A1', 1.71, 1.92, "*GOOD.", False, 0),
    ('A1', 2.37, 3.55, "You've always | had to | *pick *two.", False, .10),
    # ---- hook A2
    ('A2', 5.46, 6.59, "Every agency | says:", False, 0),
    ('A2', 6.94, 7.30, "*fast,", True, 0),
    ('A2', 7.63, 7.87, "*cheap", True, 0),
    ('A2', 8.13, 8.54, "or *good —", True, 0),
    ('A2', 9.05, 9.53, "pick *two.", False, 0),
    ('A2', 9.94, 10.37, "They're *wrong.", True, .10),
    # ---- hook A3
    ('A3', 12.36, 13.34, "Content that's | *fast,", False, 0),
    ('A3', 13.68, 14.22, "*cheap | AND *good?", True, 0),
    ('A3', 14.66, 16.30, "Everyone says | that's *impossible.", False, .10),
    # ---- body
    ('B', 18.28, 18.86, "Fast | and *cheap?", False, 0),
    ('B', 19.37, 19.89, "It looks | *cheap.", False, 0),
    ('B', 20.40, 21.05, "Good | and *fast?", False, 0),
    ('B', 21.56, 22.51, "It costs | a *fortune.", False, 0),
    ('B', 22.94, 23.42, "Good | and *cheap?", False, 0),
    ('B', 23.93, 24.47, "Get in *line.", False, .15),
    ('B', 25.40, 26.98, "That rule was written | *before *AI.", False, .10),
    ('B', 27.39, 29.20, "At *LUMARC, | we're *AI-first.", False, 0),
    ('B', 29.73, 30.52, "Not *AI-only.", False, 0),
    ('B', 30.96, 32.32, "AI does the | *heavy *lifting…", False, 0),
    ('B', 32.64, 34.03, "our team does | the *thinking.", True, 0),
    ('B', 34.95, 36.41, "So you get content | that's *faster,", False, 0),
    ('B', 36.71, 37.49, "costs *less…", True, 0),
    ('B', 37.75, 38.54, "and looks | like *this.", True, .70),
    ('B', None, (16.48, 18.08), None, False, 0),                      # INSERT: montage time (take silent, avatar hidden)
    ('B', 39.48, 40.75, "You don't have to | pick two | *anymore.", False, 0),
    ('B', 41.21, 41.73, "*Pick *three.", True, .25),
    ('B', 42.66, 42.84, "Tap", False, 0),
    ('B', 43.17, 43.90, "*“Send *message”,", True, 0),
    ('B', 44.18, 45.48, "or call the number | on the *screen.", True, 0),
]
SMILE = 3.00          # silent confident smile = the end card (the take's own frames)
BLOCKS = ['A1', 'A2', 'A3', 'B']

def _seg():
    out = []
    for blk, a, b, cap, join, hold in ISL:
        if a is None:
            out.append([blk, snap(b[0]), snap(b[1]), None]); continue
        s0 = snap(a - PRE); s1 = snap(b + POST + hold)
        if join and out and out[-1][0] == blk: out[-1][2] = s0 = out[-1][2]
        out.append([blk, s0, s1, cap])
    last = out[-1]; out.append(['B', last[2], snap(last[2] + SMILE), None])
    # block lengths -> multiples of 0.2 s (extend each block's last segment into the take's following silence)
    for blk in BLOCKS:
        idx = [i for i, s in enumerate(out) if s[0] == blk]
        d = round(sum(out[i][2] - out[i][1] for i in idx), 2)
        pad = round((-d) % 0.2, 2) % 0.2
        if pad > 1e-6: out[idx[-1]][2] = round(out[idx[-1]][2] + pad, 2)
    return [tuple(x) for x in out]
SEG = _seg()

def build():
    t = 0.0; out = []
    for blk, s0, s1, cap in SEG:
        d = round(s1 - s0, 2)
        out.append(dict(block=blk, s0=s0, s1=s1, t0=round(t, 2), t1=round(t + d, 2), cap=cap)); t = round(t + d, 2)
    for i, s in enumerate(out): s['jump'] = i > 0 and abs(out[i - 1]['s1'] - s['s0']) > 1e-6
    return out
TL = build()
VOICE_END = TL[-1]['t1']
BLOCK_SPAN = {b: (min(s['t0'] for s in TL if s['block'] == b), max(s['t1'] for s in TL if s['block'] == b)) for b in BLOCKS}

if __name__ == '__main__':
    for i, s in enumerate(TL): print(i, s['block'], s['s0'], s['s1'], s['t0'], s['t1'], 'JUMP' if s['jump'] else '    ', s['cap'])
    print('BLOCKS', BLOCK_SPAN, 'DUR', VOICE_END)
    for b in ('A1', 'A2', 'A3'):
        print('version', b, round(BLOCK_SPAN[b][1] - BLOCK_SPAN[b][0] + BLOCK_SPAN['B'][1] - BLOCK_SPAN['B'][0], 2), 's')
