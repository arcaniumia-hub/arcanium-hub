# LUMARC "Break out of the feed" Reel (1080×1920, 30 fps, 29.4 s)

The founder's HeyGen take on green (`src/plate.mp4`, gitignored) is cut tight by `build_plate.py` + `timeline.py`
(33.5 s → 26.8 s of speech, segs 7–11 kept contiguous for the knock/shatter beat) and keyed into his purple-monitor
studio. The take is a floating bust, so `engine.AV_VF` crops/scales it (×1.25) to hide the cut below the frame.
Engine = fork of `../lumarc-showcase/engine.py` with deterministic frame reads (avatar at native 25 fps, clips at 30 fps,
integer frame grid in `render`) and per-section captions. `sections/feedkit.py` is the dark Instagram-style feed.

| | span | moment |
|---|---|---|
| s01 | 0–4.00 | loop-snap onto his Reel in the viewer's feed · "Down here" box behind the glass · infinite wall of feeds, glass-tap ripple |
| s02 | 4.00–5.32 | smash zoom-out into the Explore grid (TINY tooltip) · the feed falls FLAT, colour drains |
| s03 | 5.32–7.80 | finger flick, feed thrown ("gone"), dead silence, knock-knock cracks, feed drags itself back |
| s04 | 7.80–11.96 | NOT MINE spiderweb + light leak · hero shatter toward the lens + dolly out into the studio · "ON THE SCREEN." pane cracks |
| s05 | 11.96–13.32 | LUMARC work orbiting his head as a crown, locks on HEAD |
| s06 | 13.32–15.40 | SILENCE ONE pops out of the phone in 3D · macro "almost touch" dent + ripple |
| s07 | 15.40–17.48 | Reel wakes, loops, VHS rewind ×2 on TWICE |
| s08 | 17.48–19.96 | forgotten feed fog vs the remembered brand · lock screen TODAY→TOMORROW 8:00 AM |
| s09 | 19.96–22.04 | shards fly back and build the big LUMARC logo behind him on the downbeat |
| s10 | 22.04–29.44 | a post breaks out of the feed · typed comment LUMARC + reply · end card · flick back into frame 0 (loop) |

Sound (`sound.py`): feed music plays small/mono "inside the phone", dies with a tape stop on GONE, silence for the
knocks, drone + riser on NOT MINE, boom on the shatter, full-range 120 BPM from 9.28 (LUMARC on a downbeat).
Build: `python3 build_plate.py && python3 engine.py prender 4 && python3 sound.py && python3 sound.py mux`
→ `out/lumarc-breakout.mp4` (< 30 MB). Assets in `src/assets/` (gitignored) are copies of the showcase stills and the
clone location plates.
