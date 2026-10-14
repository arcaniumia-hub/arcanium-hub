#!/usr/bin/env python3
"""Gera as legendas (ASS) do piloto: falas em pt-BR + carimbo de data/contador de anos.

Uso: python3 make_ass.py timeline.json saida.ass [--sem-falas]
"""
import json
import sys


def ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int(sec % 3600 // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fala,Montserrat SemiBold,58,&H00F4F4F4,&H000000FF,&H64000000,&H96000000,0,0,0,0,100,100,0.5,0,1,1.2,2.5,2,90,90,560,1
Style: Data,Montserrat Medium,42,&H1AFFFFFF,&H000000FF,&H00000000,&H78000000,0,0,0,0,100,100,8,0,1,0,2,8,60,60,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    tl = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    with_lines = "--sem-falas" not in sys.argv
    ev = []
    if with_lines:
        for start, end, text in tl["falas"]:
            ev.append(f"Dialogue: 0,{ts(start)},{ts(end)},Fala,,0,0,0,,{{\\fad(180,180)\\blur0.6}}{text}")
    for start, end, text, fade_in, fade_out in tl["datas"]:
        ev.append(
            f"Dialogue: 1,{ts(start)},{ts(end)},Data,,0,0,0,,"
            f"{{\\fad({int(fade_in * 1000)},{int(fade_out * 1000)})\\blur0.4}}{text}"
        )
    with open(out, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n".join(ev) + "\n")


if __name__ == "__main__":
    main()
