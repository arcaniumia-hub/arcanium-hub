# Videos

| Folder | What |
| --- | --- |
| `birra-reel/` | "É só birra?" — 2D animated reel for a child psychologist (canvas animation) |
| `solara-reel/` | SOLARA orange drink — before/after product reel (AI clips + edit) |
| `burger-reel/` | EMBER & BUN burger — before/after product reel (AI clips + edit) |

## House rule: LUMARC CTA

Every product reel ends with the LUMARC end card (`burger-reel/lumarc.py`, `lumarc_cta(frame, t)`):
"WANT YOUR PRODUCT TO LOOK LIKE THIS?" → LUMARC wordmark → tagline → "DM us "VIDEO"" button.
Give it the last ~2.6 s of the video and a boom hit in the soundtrack at the same moment.

## Before/after reel pipeline

1. Hero product image (GPT Image 2.5, 9:16), then keyframes that use it as a reference so the product stays identical.
2. Four 5 s clips with Kling 3.0 Pro (start/end frames).
3. `sound.py` synthesizes the soundtrack, `edit.py` assembles the "before" photo, the transition, the clips,
   animated text, the before/after split and the LUMARC CTA. Both run in the Higgsfield sandbox
   (this environment cannot reach Higgsfield's CDN).
