# Videos

| Folder | What |
| --- | --- |
| `birra-reel/` | "É só birra?" — 2D animated reel for a child psychologist (canvas animation) |
| `solara-reel/` | SOLARA orange drink — before/after product reel (AI clips + edit) |
| `burger-reel/` | EMBER & BUN burger — before/after product reel (AI clips + edit) |
| `lumarc-ads/` | LUMARC group-ad images (generic "AI look" flyer vs premium on-brand poster) |

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

## LUMARC brand (from slumarc.com)

- Background `#0e0e14` (also `#12121b`, `#181826`), text `#faf9f6`, muted `#a6a6b8`
- Blue `#3b5bff`, violet `#8b3dff`; gradient `120deg, #4f6bff → #6a55ff → #9a4dff`
- Font: Outfit. Logo: https://slumarc.com/img/logo-640.webp (two interlocking blue→violet rings + "lumarc" lowercase)
- Tagline "Seja visto. Seja lembrado." / "Be seen. Be remembered."
- Contact: @lumarc_studio · slumarc.com · studiolumarc@gmail.com · WhatsApp wa.me/18542952249
- Services: Reels e vídeo (edição, 2D/3D), Carrosséis, Artes e posts, Legendas e calendário, Sites, Cuidado contínuo

Note: the video end card in `burger-reel/lumarc.py` predates this and still uses orange + an uppercase wordmark;
switch it to these colors, Outfit and the real logo before the next reel.
