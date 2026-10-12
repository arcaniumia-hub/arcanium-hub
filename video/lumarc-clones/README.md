# LUMARC Reel — "We're not real" (3 AI clones, 1080×1920, 34 s)

Three HeyGen takes of the owner's clone on green (`src/b.mp4` blazer = clone #1, `src/c.mp4` hoodie = clone #2,
`src/a.mp4` white tee = clone #3; gitignored) are keyed and composited into one skit:
clone lab intro → "me too" / "yeah… same" → camera pushes onto each speaker → whip-panned week (Paris, investor day,
taxes 101 with crickets) → back in the lab for the CTA (LUMARC logo, "Comment CLONE" comment) → "And the real one?" →
empty beach chair, "On vacation." → LUMARC end card ("Comment “CLONE”").

Sets are drawn in code (`art_*` in edit.py). Each clone's take is re-timed onto the edit timeline (`tracks`): its lines
at their slots, its own silent pause footage (ping-pong) elsewhere, snapped to the 25 fps grid to keep lip sync.

Build: `python3 edit.py tracks && python3 edit.py cues && python3 sound.py && python3 edit.py render && python3 edit.py mux`

## v2 — real locations (`edit_real.py`)
Each clone talks from its own photographic location (plates generated as empty eye-level photos, `src/bg/bg1..7.png`,
gitignored): #1 home studio, #2 coffee shop, #3 rooftop; Paris / boardroom / "TAXES 101" room for the week; empty beach
chair for the punchline. No group shots — the conversation cuts between locations. Natural-look compositing: DOF blur on
the plate, clone graded toward the plate light, light wrap, handheld drift, jump-cut punch-ins, grain + vignette.
Build: `python3 edit.py tracks && python3 edit.py cues && python3 sound.py && python3 edit_real.py render && python3 edit.py mux`

## v3 — tighter, hook, sound of the places, light
- Hook: 1.1 s flash of the three clones in their three places — "ONLY ONE OF THEM IS REAL." — then straight into "I'm not real." ("Hi." cut).
- Gaps tightened, end card shortened: 34 s → 32 s.
- `audio_real.py`: each line gets the acoustics of its place (room size / EQ), plus synthesized location ambience
  (café babble + cup clinks, rooftop wind + city, Paris street, boardroom HVAC, fluorescent buzz) under the mix.
- Directional key + rim light per location on the keyed clone (warm back-rim at sunset, window side in the café,
  purple LED rim in the studio). Darker backing behind captions on the white tee.
Build: `python3 edit.py tracks && python3 edit.py cues && python3 sound.py && python3 edit_real.py prender 4 && python3 audio_real.py`
