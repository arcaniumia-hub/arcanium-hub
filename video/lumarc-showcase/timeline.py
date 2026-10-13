"""Edit decision list for the green-screen take: dead air removed, phrases kept whole.
SEG = (src_in, src_out, caption) — caption uses '|' for page breaks and '*' for emphasis; None = silent hold.
Times snap to the 25 fps source grid so the re-timed plate stays lip-synced."""
G = 0.04
def snap(x): return round(round(x / G) * G, 2)
SEG = [
    (0.26, 4.28, "In the next | *two *seconds, | you'll decide | if this video | is worth | your *time."),
    (4.32, 6.32, None),                                        # 2.0 s countdown hold
    (6.97, 10.26, "Your customers | do the *exact *same thing | with your *Instagram."),
    (10.73, 11.78, "They find | your page."),
    (12.17, 13.31, "A *blurry photo."),
    (13.51, 14.59, "A *shaky video."),
    (14.92, 16.77, "A *flyer | made in | five minutes."),
    (17.25, 19.00, "They don't think | “great business.”"),
    (19.36, 20.60, "They think..."),
    (20.68, 21.24, "*“next.”"),
    (22.27, 23.09, "Here's the *problem."),
    (23.42, 25.30, "Your work | might be *amazing."),
    (25.78, 26.64, "But online,"),
    (26.88, 28.53, "nobody can | *taste your food,"),
    (28.80, 29.89, "*feel your service,"),
    (30.02, 31.00, "or *see your skill."),
    (31.57, 33.15, "They only see | your *content."),
    (33.86, 35.90, "Your content | is your | *first *impression."),
    (36.33, 39.11, "And a great | first impression | doesn't just | look good."),
    (39.43, 40.55, "It builds *trust."),
    (40.95, 43.15, "And trust | is what makes | people *buy."),
    (43.43, 45.66, "That's why | we created | *LUMARC."),
    (46.17, 50.63, "We turn the photos | and videos | you already have | into *Reels | that stop the scroll..."),
    (51.63, 52.99, "*carousels | people save..."),
    (53.99, 56.27, "*designs that look | like a big brand | made them..."),
    (57.19, 59.97, "and a *website | that turns followers | into *customers."),
    (60.62, 61.72, "You run | the business."),
    (61.99, 63.83, "We make it | *impossible | to *ignore."),
    (64.45, 65.68, "Comment | *“LUMARC”,"),
    (65.77, 67.79, "and we'll show you | what your page | could look like."),
    (68.34, 69.04, "*LUMARC."),
    (69.43, 70.15, "Be *seen."),
    (70.49, 71.33, "Be *remembered."),
]
def build():
    t = 0.0; out = []
    for s0, s1, cap in SEG:
        s0, s1 = snap(s0), snap(s1); d = round(s1 - s0, 2)
        out.append(dict(s0=s0, s1=s1, t0=round(t, 2), t1=round(t + d, 2), cap=cap)); t = round(t + d, 2)
    return out
TL = build()
VOICE_END = TL[-1]['t1']
