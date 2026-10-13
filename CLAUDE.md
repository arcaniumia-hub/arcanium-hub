# LUMARC — working memory for video sessions

The owner runs **LUMARC** (social media / content studio). Site **slumarc.com**, Instagram **@lumarc_studio**.
Talk to the owner in **Portuguese**, concise and practical. Videos/copy for the audience are in **English**.

## Brand
- Colours: night bg `#0e0e14`, gradient `#4f6bff → #6a55ff → #9a4dff`, white `#faf9f6`, muted `#a6a6b8`.
- Font **Outfit** (`video/*/fonts/outfit.woff2`). Logo: `video/silence-motion/img/logo.png` (640×218 RGBA).
- Taglines: "Be seen. Be remembered." · CTA keyword: **Comment "LUMARC"** / "VIDEO" / "CLONE" (comment beats DM for reach).
- Every video ends with a LUMARC CTA card. Never say a video/product is AI-made — **except** the clone skit, where the
  clone being AI is the openly stated joke/product.

## The owner's taste (what got "Esse é o nível que eu quero!")
- `video/lumarc-showcase/` is the reference standard: talking head keyed from green into his own purple-monitor
  studio, a signature effect on almost every phrase, landing exactly on the spoken word, glass UI, text behind him,
  frame-in-frame phone, glass slats, clone split, before→after, portfolio mockups, voice-synced captions, original
  score + per-hit SFX, ~60 s, hooks in the first 2 s, no dead air.
- He prefers: the work shown more than the talking head; real-looking locations (not drawn); natural compositing
  (DOF, light match, rim, grain); fast tight cuts; short.
- Max-quality edits were built with multi-agent workflows ("ultracode"): parallel section builders → critics →
  fixers → adversarial verifiers. Only run workflows when the owner asks (ultracode / "use workflow").

## How to start a new talking-head edit (fast path)
1. Owner generates the HeyGen avatar on **green #00FF00**, waist-up, static camera, no captions/music (prompt pattern
   in the showcase conversation: "Create a vertical 9:16 talking-avatar video… solid pure green background…").
2. Copy `video/lumarc-showcase/` structure: `timeline.py` (EDL that removes pauses — measure speech islands from the
   audio energy), `engine.py` (compositor, reuse as is), `sections/sNN_*.py` (one per beat, contract in
   `sections/README.md`), `sound.py` (score + cue SFX + mix + 2-pass encode under 30 MB).
3. Word timing: automatic alignment + hand-measured `WORD_FIX` table in engine.py (check onsets on the voice track).
4. Render: `python3 engine.py prender 4 && python3 sound.py && python3 sound.py mux`.

## Environment constraints (cloud container)
- Network blocks HeyGen/Higgsfield CDNs: the owner must send files in chat (≤ ~30 MB; compress if larger).
- Higgsfield sandbox (mcp sandbox_exec) has internet + ffmpeg: use it to generate/package assets, upload a .zip via
  media_upload (PUT with `If-None-Match: *`), give the owner the link, and he re-sends it here.
- Deliver files with SendUserFile (limit 30 MB). Media files are gitignored; commit code + small assets and push to the
  working branch after each milestone.

## Asset map
- Products/films: SILENCE ONE (fictional headphone): `silence-motion/silence-motion.mp4` (teardown, vertical),
  `silence-hyper/master.mp4` (hyper film; LUMARC end card at 28.3–34.4 s), 16:9 cinematic ad lives on Higgsfield.
- LUMARC motion: `lumarc-motion-en/lumarc-3d-en.mp4` (service cards 12–18 s, post wall ~8 s, logo reveal ~6–8 s).
- Studio plate: `lumarc-showcase/src/studio_plate.png`. Real-location plates (studio/café/rooftop/Paris/boardroom/
  classroom/beach): `lumarc-clones/src/bg/` (gitignored — regenerate in Higgsfield if missing).
- Showcase assets (bad examples, close-ups, carousel, poster, website): `lumarc-showcase/src/assets/` (gitignored).
- `video/lumarc-breakout/` ("Break out of the feed", ultracode build): fake Instagram feed kit (`sections/feedkit.py`),
  glass crack/shatter kit (`sections/_glasskit.py`), engine fork with deterministic frame reads — reuse for feed/glass ideas.
- Per-project READMEs in each `video/*/` folder explain how each film was built.
