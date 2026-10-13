# LUMARC showcase Reel — "Your content is your first impression" (1080×1920, 30 fps, 58.8 s)

The founder's HeyGen take on green (`src/plate.mp4`, gitignored) is cut tight (`timeline.py`: 72 s → 56.6 s of speech,
a 2.0 s hold for the countdown), keyed and composited into his own purple-monitor studio (`src/studio_plate.png`,
rebuilt from his earlier takes). `engine.py` is the compositor (studio → behind layers → keyed avatar → front layers →
virtual camera → frame-in-frame wrap → screen layers → voice-aligned captions → post FX). Twelve section modules in
`sections/` own the signature moments (see `sections/README.md` for the contract):

| | span | moment |
|---|---|---|
| s01 | 0–6.04 | giant "2" behind him, 2.00→0.00 countdown dial, glitch hit |
| s02 | 6.04–9.32 | pull-back reveal: he is a Reel inside a phone |
| s03 | 9.32–14.44 | bad page: blurry photo / shaky video / flyer fly out of the profile |
| s04 | 14.44–18.00 | GREAT BUSINESS struck out, "They think…", Instagram swipe on "next" |
| s05 | 18.00–25.24 | PROBLEM snap, "online" glass screen, TASTE / FEEL / SEE glass triptych |
| s06 | 25.24–28.92 | triptych shatter, FIRST IMPRESSION behind him (dolly feel) |
| s07 | 28.92–35.04 | frosted-glass trust / reviews / revenue / new-order UI |
| s08 | 35.04–37.28 | fluted-glass slats → LUMARC logo on the downbeat |
| s09 | 37.28–48.16 | portfolio: before→after scan, Reel phone (SILENCE ONE), carousel + Saved, poster, website + booking |
| s10 | 48.16–51.08 | clone split + IMPOSSIBLE / TO IGNORE layered type |
| s11 | 51.08–54.36 | typed "LUMARC" comment, profile grid assembling |
| s12 | 54.36–58.84 | logo slam, Be seen. Be remembered., Comment “LUMARC” end card |

Build: `python3 engine.py prender 4 && python3 sound.py && python3 sound.py mux` → `out/lumarc-showcase.mp4` (< 30 MB).
Assets (`src/assets/`, gitignored): generated stills — bad examples, close-ups, carousel, poster, website.
