# LUMARC "Couples Therapy — for brands" (1080×1920, 30 fps, 59.9 s) — comedy Reel

Three HeyGen takes on green (`src/therapist.mp4`, `kevin.mp4`, `instagram.mp4`, gitignored) — the therapist (LUMARC),
Kevin (bakery owner) and his Instagram personified — keyed into three angles of one photographic office (Higgsfield plates
in `src/assets/`: wide, angle_therapist/kevin/instagram + flyer, xmas2021, croissant stills, croissant_pull.mp4).
`timeline.py` = the dialogue EDL (one line at a time, comedic gaps; lines may be several PARTS to tighten pauses),
`build_voice.py` assembles the dialogue on the edit timeline, `engine.py` = multi-take compositor (clean matte, per-angle
grade/light, default picture = the speaker, sections cut to reactions), `sound.py` = office room + ambience, lounge bed
(stops for the jokes), trailer score for the movie, per-hit SFX on their own lightly-ducked bus.

| | span | beats |
|---|---|---|
| s01 | 0–3.02 | cover frame "KEVIN & HIS INSTAGRAM" over the offended hoodie, cutaways on "you two" |
| s02 | 3.02–10.46 | name chips, crash zoom on "Support you?", Kevin's guilty reaction, "That's not true!" |
| s03 | 10.46–15.04 | the abandoned Christmas 2021 post (3 likes, mom's comment), "I've been busy!" |
| s04 | 15.04–22.94 | the flyer slaps on the table, red-marker count of the 7 fonts, dun-dun-DUNNN on SEVEN |
| s05 | 22.94–28.66 | "…Creative?" dead air + crickets + reactions, Insights crash on "cried." |
| s06 | 28.66–36.84 | the therapist's legal pad list, the lamp clicks on for "Good lighting", diva push |
| s07 | 36.84–46.50 | "not movies!", 2.39 Leone close-up, THE MOVIE (A LUMARC FILM, croissant pull, KEVIN'S BAKERY) |
| s08 | 46.50–59.90 | "Oh. OH. Okay… I'm listening." escalating zooms + follower pings, typed LUMARC comment, end card |

Build: `python3 build_voice.py && GRAIN_K=0.55 python3 engine.py prender 4 && python3 sound.py && python3 sound.py mux`
→ `out/lumarc-therapy.mp4` (< 30 MB, −14.7 LUFS).
