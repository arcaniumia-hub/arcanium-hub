"""Edit decision list for the green-screen take "Break out of the feed" (33.5 s source).
SEG = (src_in, src_out, caption) — caption uses '|' for page breaks and '*' for emphasis; None = silent hold.
Times snap to the 25 fps source grid so the re-timed plate stays lip-synced.
Segments 7..11 are CONTIGUOUS in the source (no jump): "and it's gone" -> knock pause -> "Not mine." -> shatter pause
-> "Good content…" play as one continuous take."""
G = 0.04
def snap(x): return round(round(x / G) * G, 2)
SEG = [
    (0.20, 0.72, "*Hey."),
    (1.16, 2.04, "Yeah, | *you."),
    (2.32, 3.08, "*Down *here."),
    (3.60, 5.44, "Your content | lives in *here."),
    (5.92, 6.64, "*Tiny."),
    (7.12, 7.72, "*Flat."),
    (8.16, 9.04, "One *swipe..."),
    (9.32, 10.20, "and it's *gone."),
    (10.20, 10.92, None),                                       # silent beat: knock, knock (contiguous)
    (10.92, 11.68, "*Not *mine."),                              # contiguous
    (11.68, 12.40, None),                                       # the glass shatters (contiguous)
    (12.40, 15.08, "Good content | doesn't stay | on the *screen."),   # contiguous
    (15.32, 16.68, "It stays | in your *head."),
    (17.36, 19.44, "The product | you can | almost *touch."),
    (19.80, 21.88, "The video | you watch *twice."),
    (22.36, 24.84, "The brand | you still | *remember | tomorrow."),
    (25.40, 27.48, "That's what | we build | at *LUMARC."),
    (27.96, 30.20, "Want your brand | to *break *out | of the feed?"),
    (30.60, 31.96, "Comment | *“LUMARC”"),
    (32.20, 33.40, "and I'll | show you *how."),
]
def build():
    t = 0.0; out = []
    for s0, s1, cap in SEG:
        s0, s1 = snap(s0), snap(s1); d = round(s1 - s0, 2)
        out.append(dict(s0=s0, s1=s1, t0=round(t, 2), t1=round(t + d, 2), cap=cap)); t = round(t + d, 2)
    return out
TL = build()
VOICE_END = TL[-1]['t1']
