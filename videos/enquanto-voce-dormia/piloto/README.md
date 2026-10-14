# Piloto — "Enquanto você dormia" (Cenas 1 e 2)

Piloto de ~16s, vertical 9:16 (1080x1920, 24fps), para validar voz, visual e movimento
antes da produção completa do Vídeo 1.

## Entregas (hospedadas no Higgsfield)

| Versão | Link |
|---|---|
| Com legendas (Reels/TikTok/Shorts) | https://d2ol7oe51mr4n9.cloudfront.net/user_3JnbdRmxqFKlwKubhAVCpRrRka8/420072e1-1f43-4940-8e0c-21cd3feec60c.mp4 |
| Limpa (só o carimbo de data/anos) | https://d2ol7oe51mr4n9.cloudfront.net/user_3JnbdRmxqFKlwKubhAVCpRrRka8/6274b60f-83e6-412d-a6a5-8dd12ca0816b.mp4 |

## Como foi feito

| Etapa | Ferramenta | Custo (créditos) |
|---|---|---|
| Narração pt-BR, voz Arthur (`30fc8796-…` preset), 3 takes | Higgsfield TTS (ElevenLabs) | ~1,65 |
| Keyframe do quarto (9:16, 2K) | Nano Banana Pro | 2 |
| Cena 1 — abajur apagando, push-in lento (9s) | Kling 3.0 Std, a partir do keyframe | 13,5 |
| Cena 2 — timelapse das estações (4s) | Kling 3.0 Std, a partir do último quadro da Cena 1 | 6 |
| Edição, cor, grão, desenho de som, legendas, mix, export | ffmpeg + scripts deste diretório | 0 |
| **Total** | | **~23,15** |

### Linha do tempo (s)

- 0,0–2,0 — surge do preto no quadro inicial congelado
- 2,0–9,2 — Cena 1 em câmera lenta (0,52x, interpolação de movimento) para o clique do abajur
  cair exatamente em "Você apagou a luz" (9,2s)
- 9,2–12,1 — luz fria, ele se ajeita sob o cobertor
- 11,6–14,4 — dissolve para o timelapse (1,4x) com contador 2023 → 2026
- 14,4–16,3 — "HOJE", luz quente da manhã, fade

### Som (sem trilha licenciada)

`sfx_synth.py` gera toda a ambiência: room tone, drone grave em lá menor, tique-taque que acelera no
timelapse, clique do abajur, farfalhar do cobertor, whoosh do tempo e um acorde suave no "acordou hoje".
Mix final: voz ~12 dB acima da ambiência, -14 LUFS integrado (padrão das redes).

## Arquivos

- `montar.py` — monta o vídeo (tempos no topo do arquivo)
- `make_ass.py` — legendas pt-BR e carimbo de data/anos (fonte Montserrat)
- `sfx_synth.py` — desenho de som sintetizado

Os scripts rodam no sandbox do Higgsfield (`piloto/dl` com `clip1.mp4`, `clip2.mp4`, `vo1.mp3`,
`vo2b.mp3`; fontes em `piloto/work/fonts`).

## Aprendizados para a produção completa

1. **Rosto:** o roteiro pede rosto oculto. No keyframe, a pessoa ficou de perfil, e o Kling não a virou
   de costas. Na produção, gerar o keyframe já com a pessoa de costas, cabeça sob o cobertor.
2. **Timing:** a narração calma de cada cena dura mais que o tempo do roteiro (a Cena 1 sozinha tem 12s
   de fala). O Vídeo 1 completo deve fechar entre 3:00 e 3:30 de animação, ou o texto precisa de cortes.
3. **Ação dentro do clipe:** o Kling não respeita bem "espere X segundos". Resolvemos na edição
   (câmera lenta + congelamento); vale gerar clipes com folga.
4. **Continuidade:** usar o último quadro de um clipe como início do próximo funcionou muito bem.
