# LUMARC — "Pick three." (EN, US Meta ad, 3 hook versions)

Paid ad for Meta (Reels/Stories, US): "Fast. Cheap. Good — you've always had to pick two… That rule was written before
AI. LUMARC is AI-first, not AI-only… Pick three." One HeyGen take (src/take.mp4, 48.8 s) holds three alternative
hooks + the body. The MASTER timeline plays A1 | A2 | A3 | BODY; `versions.py` splices hook_k + body (frame-exact: blocks
on the 0.2 s grid) into three ads for hook testing: A1 31.4 s, A2 33.4 s, A3 32.6 s.

Ad rules baked in (sections/README.md): muted-autoplay readability, frame-1 hook per version, Meta safe zones (all key
text inside x 70–960, y 280–1250), no prices/deadlines/digits, phone (854) 295-2249 on screen only.

Built with an ultracode workflow: a shared glass-triangle kit (`sections/_tri.py` — FAST/CHEAP/GOOD, pick-two, crack/
shatter, assemble, complete, logo morph), then 4 builders (hooks H, pick-two jokes P, LUMARC + portfolio montage L, pick
three + CTA + end card T), each followed by an adversarial reviewer/fixer.

## Rebuild
```
python3 build_plate.py                    # src/take.mp4 -> src/tight.mov + tight16k.raw
python3 -c "import engine as E; E.house().prewarm()"
GRAIN_K=0.55 python3 engine.py prender 4  # out/video.mp4 (master, silent)
python3 sound.py                          # music.wav + sfx.wav (master; hook beds/cues trimmed to their blocks)
python3 versions.py                       # out/lumarc-pick3-A1/A2/A3.mp4 (-14 LUFS, < 30 MB)
```
