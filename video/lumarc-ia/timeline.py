"""EDL for "IA só faz conteúdo genérico?" (PT-BR, AI-first showreel) — the HeyGen take on green (src/take.mp4, 88.9 s,
25 fps), seated waist-up at a dark desk.  Built from the 38 speech islands measured on the take's audio (10 ms RMS,
-40 dB; HeyGen silences are clean, floor -68 dB).

ISL = (start, end, caption, join, hold)
    caption  '|' page breaks, '*' emphasis, None = silent
    join     True: this island continues the previous one in the SAME source run (the natural pause is kept, no jump)
    hold     extra seconds of the take's own silent pause kept after the island (a dramatic beat; mouth closed)
Islands are cut with PRE / POST padding; every non-joined island start is a JUMP in the take (cover it with a framing
change).  Times snap to the 25 fps grid.  The last SEG is the silent smile (end card)."""
G = 0.04
def snap(x): return round(round(x / G) * G, 2)
PRE, POST = 0.10, 0.12
ISL = [
    (0.42, 4.67, "Você já deve | ter ouvido… | ou até *concorda… | que IA só faz | conteúdo *genérico, | né?", False, 0),   # 0
    (5.09, 7.88, "Imagem que parece | *banco de imagem… | texto sem *alma…", True, 0),                                  # 1
    (8.27, 9.88, "vídeo que parece | todos os *outros.", True, .16),                                                     # 2
    (10.85, 12.74, "Mas será que | o problema | é a *IA…", False, 0),                                                    # 3
    (13.05, 16.33, "ou você só | não encontrou alguém | que saiba usar | o potencial | *máximo dela?", True, .20),       # 4
    (17.00, 18.87, "Ah, e pode | me *desconsiderar | nesse vídeo…", False, 0),                                           # 5
    (19.20, 20.63, "eu claramente | sou *IA, né?", True, 0),                                                             # 6
    (21.03, 23.23, "Só tô aqui pra | *prender | a sua atenção | por alguns segundos.", True, 0),                          # 7
    (24.08, 26.12, "Um *pincel | não pinta um quadro | sozinho.", False, 0),                                             # 8
    (26.60, 28.11, "A IA é a | *ferramenta.", False, 0),                                                                 # 9
    (28.73, 30.19, "A diferença | tá em *quem usa.", False, .10),                                                        # 10
    (31.18, 33.74, "Deixa eu te mostrar | o que acontece | quando a IA | tá na *mão certa.", False, 0),                   # 11
    (34.40, 36.34, "Um produto | com cara de | comercial de *cinema.", False, 0),                                        # 12
    (36.96, 39.04, "Um texto | que *dança | no ritmo | da sua fala.", False, 0),                                         # 13
    (39.65, 41.26, "Um cenário | que muda | num *estalo.", False, 0),                                                    # 14
    (41.89, 42.72, "Um *clone seu…", False, 0),                                                                          # 15
    (43.11, 43.63, "ou *três.", True, 0),                                                                                # 16
    (44.33, 46.18, "Uma *casa | que se constrói | na sua frente.", False, 0),                                            # 17
    (46.73, 48.84, "E um vídeo | que você não consegue | parar de *assistir.", False, 0),                                # 18
    (49.74, 52.02, "Aqui na *LUMARC, | a gente é | *AI-FIRST:", False, 0),                                               # 19
    (52.53, 54.59, "a IA faz | grande parte | do trabalho *pesado…", False, 0),                                          # 20
    (55.12, 56.88, "e o nosso time | coloca o que | ela não tem:", False, 0),                                            # 21
    (57.49, 58.15, "*estratégia,", False, 0),                                                                            # 22
    (58.51, 59.29, "*criatividade,", True, 0),                                                                           # 23
    (59.65, 60.31, "*bom *gosto…", True, 0),                                                                             # 24
    (60.76, 62.44, "e, principalmente, | a IA *certa,", True, 0),                                                        # 25
    (62.83, 64.06, "usada do | jeito *certo.", True, .10),                                                               # 26
    (65.09, 65.68, "O *resultado?", False, .12),                                                                         # 27
    (66.19, 67.17, "Entrega | mais *rápida.", False, 0),                                                                 # 28
    (67.59, 68.37, "Preço | mais *baixo.", True, 0),                                                                     # 29
    (68.87, 70.96, "E um conteúdo | que ninguém diria | que é *genérico.", False, .14),                                  # 30
    (71.84, 73.16, "Ah… | e o resto | desse *vídeo?", False, .12),                                                       # 31
    (73.68, 75.91, "A *edição, | os *efeitos, | a *trilha…", False, 0),                                                  # 32
    (76.57, 78.60, "Também foi feito | *noventa *por *cento | com IA.", False, .14),                                     # 33
    (79.48, 80.52, "Quer o mesmo | pra sua *marca?", False, 0),                                                          # 34
    (81.15, 82.08, "Entre em *contato | com a gente.", False, 0),                                                        # 35
    (82.54, 83.47, "O número | tá aqui na *tela.", True, 0),                                                             # 36
]
SMILE = 3.20          # the silent confident smile after the last line = the end card (the take's own frames)

def _seg():
    out = []
    for k, (a, b, cap, join, hold) in enumerate(ISL):
        s0 = snap(a - PRE); s1 = snap(b + POST + hold)
        if join and out:                      # same source run: previous seg ends where this one starts (pause kept)
            out[-1][1] = s0 = out[-1][1]
        out.append([s0, s1, cap])
    out[-1][1] = snap(ISL[-1][1] + .30); out.append([out[-1][1], snap(out[-1][1] + SMILE), None])
    return [tuple(x) for x in out]
SEG = _seg()

def build():
    t = 0.0; out = []
    for s0, s1, cap in SEG:
        d = round(s1 - s0, 2)
        out.append(dict(s0=s0, s1=s1, t0=round(t, 2), t1=round(t + d, 2), cap=cap)); t = round(t + d, 2)
    for i, s in enumerate(out): s['jump'] = i > 0 and abs(out[i - 1]['s1'] - s['s0']) > 1e-6
    return out
TL = build()
VOICE_END = TL[-1]['t1']

if __name__ == '__main__':
    for i, s in enumerate(TL): print(i, s['s0'], s['s1'], s['t0'], s['t1'], 'JUMP' if s['jump'] else '    ', s['cap'])
    print('DUR', VOICE_END)
