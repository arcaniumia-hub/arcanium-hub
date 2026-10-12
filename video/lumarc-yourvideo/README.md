# LUMARC Reel — "Your product isn't boring… your video is." (1080×1920, 28 s)

HeyGen talking head (`plate.mp4`, gitignored) + motion edit. Shares the caption / zoom / PiP toolkit with
`../lumarc-talkinghead/edit.py` (imported).

Structure: hook on the SILENCE ONE teardown → "your VIDEO is" punch-in → split screen same product / same budget
(BEFORE vs LUMARC) → generic posts flung out of a feed with a 1.0 s timer → premium film with views / Saved / SOLD
UI → "how you show it" 4-cut montage → Instagram comment "VIDEO" CTA → LUMARC end card ("Comment “VIDEO”").

Build: `python3 edit.py cues && python3 sound.py && python3 edit.py render && python3 edit.py mux`
