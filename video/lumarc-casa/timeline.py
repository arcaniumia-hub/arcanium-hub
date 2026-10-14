"""EDL for "Edição que faz o olho ficar" (PT-BR) — the HeyGen take on green (src/plate.mp4, 53.8 s, 25 fps), seated
waist-up at a dark desk. SEG = (src_in, src_out, caption): '|' page breaks, '*' emphasis, None = silent hold.
Times snap to the 25 fps grid. A line split in two SEGs (11/12, 13/14) is a jump inside the line (tightened pause)."""
G = 0.04
def snap(x): return round(round(x / G) * G, 2)
SEG = [
    (0.26, 2.32, "Edição boa | não é *enfeite."),                                  # 0
    (2.64, 4.38, "Ela *mostra | o que você fala."),                                # 1
    (5.04, 5.62, "Olha *só."),                                                     # 2
    (6.08, 6.40, None),                                                            # 3 beat: the empty lot appears
    (6.40, 8.56, "Pensa na sua marca | como uma *casa."),                          # 4
    (9.24, 11.66, "O *alicerce | é o seu | posicionamento."),                      # 5
    (12.24, 14.34, "As *paredes | são o seu | conteúdo."),                         # 6
    (15.00, 17.00, "As *janelas | são os seus | vídeos."),                         # 7
    (17.50, 19.96, "E a *porta | é o seu chamado | pra ação."),                    # 8
    (20.92, 21.76, "Agora *repara…"),                                              # 9
    (22.24, 26.58, "você assistiu até aqui | porque a casa | tava sendo *construída | na sua frente."),   # 10
    (27.24, 29.10, "É isso que | uma boa edição faz:"),                            # 11
    (29.50, 31.36, "dá um *motivo | pro seu olho *ficar."),                        # 12
    (32.04, 33.72, "Cada frase, | uma *imagem."),                                  # 13
    (34.20, 36.12, "Cada palavra, | um *movimento."),                              # 14
    (36.90, 39.34, "Sem edição, | você tem | um terreno *vazio…"),                  # 15
    (39.80, 41.80, "e ninguém para | pra olhar | um terreno vazio."),              # 16
    (42.66, 45.00, "Com *edição… | as pessoas *entram."),                          # 17
    (45.80, 48.60, "Quer construir | a sua? | Comenta *“LUMARC”."),                # 18
]
def build():
    t = 0.0; out = []
    for s0, s1, cap in SEG:
        s0, s1 = snap(s0), snap(s1); d = round(s1 - s0, 2)
        out.append(dict(s0=s0, s1=s1, t0=round(t, 2), t1=round(t + d, 2), cap=cap)); t = round(t + d, 2)
    return out
TL = build()
VOICE_END = TL[-1]['t1']
