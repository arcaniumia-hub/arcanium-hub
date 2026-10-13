"""Dialogue EDL for "Couples Therapy — for brands": three HeyGen takes on green (src/therapist.mp4, kevin.mp4,
instagram.mp4, 25 fps), one line at a time, in story order.

LINE = (speaker, src_in, src_out, caption, gap_before)
  speaker  'T' therapist · 'K' Kevin (bakery owner) · 'I' his Instagram
  caption  '|' page breaks, '*' emphasis
  gap_before  seconds of silence on the edit timeline before the line starts (comedic timing)
Specials on the edit timeline: TITLE (cold open card over the empty office), MOVIE (Kevin's croissant "film"),
END (LUMARC end card). The default PICTURE for a line is its speaker's take, continuing past src_out into the take's
own silent pause (mouth closed, in character) until the next line starts; sections can cut to reactions instead.
Silent reaction tails (no speech) in each take: T 25.9–33.3 · K 18.5–25.7 · I 34.7–42.0 (plus every 2 s pause between lines).
"""
G = 0.04
def snap(x): return round(round(x / G) * G, 2)

TITLE = 0.40          # the first line ("So…") starts under the title card
LINES = [
    ('T', 0.30, 2.70, "So… | what brings you two | here *today?", TITLE),
    ('K', 0.30, 2.74, "My *Instagram | doesn't support me | anymore.", .22),
    ('I', 0.26, 3.92, "*Support you? | You only talk to me | when you need | something.", .14),
    ('K', 4.56, 5.56, "That's | not *true!", .08),
    ('I', 5.84, 9.20, "Your last post | was *Christmas. | *Twenty *twenty-one.", .14),
    ('K', 7.34, 8.26, "I've been *busy!", .10),
    ('I', 11.08, 13.98, "And when you *DO | show up… | it's a *flyer.", .24),
    ('K', 10.06, 11.64, "People *love | flyers!", .12),
    ('I', 15.58, 18.26, "*Seven fonts, | Kevin. | *SEVEN.", .18),
    ('T', 4.56, 6.68, "Kevin… | how did that | make you *feel?", .44),
    ('K', 13.52, 14.20, "*…Creative?", .56),
    ('I', 20.10, 21.54, "My algorithm | *cried.", .52),
    ('T', 8.50, 10.98, "Instagram, | what do you | need from *him?", .40),
    ('I', 23.40, 28.74, "*Consistency. | Good *lighting. | *Reels. | Is that too much | to ask?", .24),
    ('K', 16.08, 18.46, "I sell croissants, | not *movies!", .14),
    ('T', 12.80, 15.98, "Kevin… | your croissants | deserve a *movie.", .34),
    ('I', 30.96, 34.72, "…Oh. | *OH. | Okay… | I'm *listening.", None),     # gap = after the MOVIE insert
    ('T', 17.86, 24.80, "If your Instagram | stopped talking | to you… | comment | *“LUMARC”. | We do | couples therapy. | For *brands.", .40),
]
MOVIE_AFTER = 15      # the croissant "movie" plays after this line …
MOVIE_LEN = 3.60      # … for this long (no dialogue), then line 16 starts
END_HOLD = 2.60       # end card after the last line

def build():
    t = 0.0; out = []
    for i, (spk, s0, s1, cap, gap) in enumerate(LINES):
        if gap is None: gap = 0.0
        t = round(t + gap, 2)
        s0, s1 = snap(s0), snap(s1); d = round(s1 - s0, 2)
        out.append(dict(i=i, spk=spk, s0=s0, s1=s1, t0=t, t1=round(t + d, 2), cap=cap))
        t = round(t + d, 2)
        if i == MOVIE_AFTER:
            out[-1]['movie'] = (t + .12, t + .12 + MOVIE_LEN); t = round(t + .12 + MOVIE_LEN, 2)
    return out
TL = build()
MOVIE = TL[MOVIE_AFTER]['movie']
VOICE_END = TL[-1]['t1']
DUR = round(VOICE_END + END_HOLD, 2)
TAKES = {'T': 'therapist', 'K': 'kevin', 'I': 'instagram'}

if __name__ == '__main__':
    for s in TL: print(s['i'], s['spk'], s['t0'], s['t1'], s['cap'], s.get('movie', ''))
    print('MOVIE', MOVIE, 'VOICE_END', VOICE_END, 'DUR', DUR)
