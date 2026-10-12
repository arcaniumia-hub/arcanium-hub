# LUMARC Reel — "We're not real" (3 AI clones, 1080×1920, 34 s)

Three HeyGen takes of the owner's clone on green (`src/b.mp4` blazer = clone #1, `src/c.mp4` hoodie = clone #2,
`src/a.mp4` white tee = clone #3; gitignored) are keyed and composited into one skit:
clone lab intro → "me too" / "yeah… same" → camera pushes onto each speaker → whip-panned week (Paris, investor day,
taxes 101 with crickets) → back in the lab for the CTA (LUMARC logo, "Comment CLONE" comment) → "And the real one?" →
empty beach chair, "On vacation." → LUMARC end card ("Comment “CLONE”").

Sets are drawn in code (`art_*` in edit.py). Each clone's take is re-timed onto the edit timeline (`tracks`): its lines
at their slots, its own silent pause footage (ping-pong) elsewhere, snapped to the 25 fps grid to keep lip sync.

Build: `python3 edit.py tracks && python3 edit.py cues && python3 sound.py && python3 edit.py render && python3 edit.py mux`
