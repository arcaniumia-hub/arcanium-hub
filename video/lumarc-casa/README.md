# LUMARC "Edição que faz o olho ficar" (PT-BR, 1080×1920, 30 fps, 40.6 s)

The founder's HeyGen take (PT-BR, green, seated at a desk) cut tight by `timeline.py` + `build_plate.py`
(53.8 s → 38 s of speech) and keyed into his purple studio. The film proves its own point: "Edição boa não é enfeite —
ela mostra o que você fala": a premium 3D architectural-maquette house (`sections/_house.py`, pure numpy/PIL renderer,
`state_at(t)` = one canonical build timeline keyed to the measured words) builds itself ON the words —
lote (Olha só) · traço de luz (casa) · alicerce/posicionamento · paredes de posts/conteúdo · telhado · janelas que
acendem e passam vídeos · porta/chamado pra ação · freeze (Agora repara…) · replay + gráfico de retenção · cada
palavra um movimento · o vento leva a casa (Sem edição… terreno vazio, tumbleweed) · rewind + luzes + pessoas entram
(Com edição…) · placa LUMARC + comentário digitado + end card.
The score is built like the house (layers on alicerce/paredes/janelas/porta, silence on "repara", wind on "vazio", drop
on "Com edição"); SFX on their own lightly-ducked bus.

Build: `python3 build_plate.py && python3 sections/_house.py prewarm && GRAIN_K=0.55 python3 engine.py prender 4 &&
python3 sound.py && python3 sound.py mux` → `out/lumarc-casa.mp4` (< 30 MB, −14.4 LUFS).
