#!/usr/bin/env python3
"""Monta o piloto "Enquanto você dormia" (Cenas 1 e 2, ~16s, 9:16).

Roda no sandbox do Higgsfield (ffmpeg + numpy). Espera em ./dl:
  clip1.mp4  (Kling, quarto / abajur apagando)
  clip2.mp4  (Kling, timelapse)
  vo1.mp3    (narração Cena 1)   vo2b.mp3 (narração Cena 2)
Gera em ./out: piloto_legendado.mp4 e piloto_limpo.mp4
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DL, WORK, OUT = "dl", "work", "out"
FPS = 24

# ---- marcações (segundos) -------------------------------------------------
HOLD = 2.0          # quadro inicial congelado surgindo do preto
LAMP_SRC = 3.75     # instante em que o abajur apaga no clip1 (medido pela luminância)
SLOW = 0.52         # velocidade do trecho antes do clique (câmera lenta)
POST_END = 6.6      # até onde usamos o clip1 depois do clique
XF = 0.5            # dissolve do clip1 para o timelapse
TL_SPEED = 1.4      # acelera o timelapse
TL_LEN = 4.0        # duração do clip2
TAIL = 1.9          # segura o último quadro (manhã) antes do fade
VO1_AT = 0.4
VO2_AT = 13.3

slow_len = LAMP_SRC / SLOW
lamp_t = HOLD + slow_len
post_len = POST_END - LAMP_SRC
seg_a = HOLD + slow_len + post_len          # pré-dissolve
tl_start = seg_a - XF
tl_len = TL_LEN / TL_SPEED
wake = tl_start + tl_len
total = wake + TAIL


def ts(v):
    return round(v, 3)


def run(cmd):
    print("+", " ".join(cmd)[:300], flush=True)
    subprocess.run(cmd, check=True)


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    marks = {
        "total": ts(total), "timelapse_start": ts(tl_start), "timelapse_end": ts(wake),
        "wake": ts(wake), "lamp_off": ts(lamp_t), "rustle": ts(lamp_t + 1.2),
    }
    json.dump(marks, open(f"{WORK}/marcas.json", "w"))
    run([sys.executable, f"{HERE}/sfx_synth.py", f"{WORK}/marcas.json", f"{WORK}/sfx.wav"])

    # legendas: tempos das palavras vindos do Whisper (relativos a cada take)
    falas = [
        (VO1_AT + 0.00, VO1_AT + 1.95, "Imagina que você dormiu"),
        (VO1_AT + 1.95, VO1_AT + 5.40, "numa noite de novembro de 2022."),
        (VO1_AT + 5.90, VO1_AT + 7.35, "Uma noite comum."),
        (VO1_AT + 7.98, VO1_AT + 9.45, "Você apagou a luz,"),
        (VO1_AT + 9.55, VO1_AT + 11.95, "deitou e fechou os olhos."),
        (VO2_AT + 0.25, VO2_AT + 2.55, "E só… acordou hoje."),
    ]
    step = tl_len / 5
    datas = [(VO1_AT + 3.1, tl_start + 0.2, "NOVEMBRO · 2022", 0.8, 0.3)]
    for i, ano in enumerate(["2023", "2024", "2025", "2026"]):
        datas.append((tl_start + 0.2 + i * step, tl_start + 0.2 + (i + 1) * step, ano, 0.05, 0.05))
    datas.append((wake, total - 0.2, "HOJE", 0.4, 0.6))
    json.dump({"falas": falas, "datas": datas}, open(f"{WORK}/timeline.json", "w"), ensure_ascii=False)
    run([sys.executable, f"{HERE}/make_ass.py", f"{WORK}/timeline.json", f"{WORK}/legendas.ass"])
    run([sys.executable, f"{HERE}/make_ass.py", f"{WORK}/timeline.json", f"{WORK}/datas.ass", "--sem-falas"])

    norm = "scale=1080:-2:flags=lanczos,crop=1080:1920,setsar=1,format=yuv420p"
    grade = (
        "eq=contrast=1.05:saturation=0.92,"
        "colorbalance=rs=-0.02:bs=0.03:rh=0.02:bh=-0.02,"
        "curves=all='0/0.025 0.25/0.225 0.5/0.5 0.75/0.775 1/0.97',"
        "vignette=angle=0.55,"
        "unsharp=5:5:0.35,"
        "noise=c0s=7:c0f=t+u,"
        f"fade=t=in:st=0:d=1.6,fade=t=out:st={ts(total - 0.7)}:d=0.7"
    )
    fc = (
        f"[0:v]trim=end_frame=1,loop=loop={int(HOLD * FPS) - 1}:size=1,setpts=N/{FPS}/TB,{norm}[hold];"
        f"[0:v]trim=0:{LAMP_SRC},setpts=(PTS-STARTPTS)/{SLOW},"
        f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,{norm}[slow];"
        f"[0:v]trim={LAMP_SRC}:{POST_END},setpts=PTS-STARTPTS,fps={FPS},{norm}[post];"
        f"[hold][slow][post]concat=n=3:v=1:a=0,settb=1/{FPS},fps={FPS}[a];"
        f"[1:v]setpts=(PTS-STARTPTS)/{TL_SPEED},fps={FPS},{norm},"
        f"tpad=stop_mode=clone:stop_duration={TAIL + 0.1},settb=1/{FPS}[b];"
        f"[a][b]xfade=transition=fade:duration={XF}:offset={ts(tl_start)},{grade},"
        f"trim=0:{ts(total)}[v];"
        # áudio: tratamento leve na voz + desenho de som
        "[2:a]highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200:makeup=2,"
        "aecho=0.85:0.6:35|60:0.10|0.06,aresample=48000,pan=stereo|c0=c0|c1=c0,"
        f"adelay={int(VO1_AT * 1000)}|{int(VO1_AT * 1000)}[vo1];"
        "[3:a]highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200:makeup=2,"
        "aecho=0.85:0.6:35|60:0.10|0.06,aresample=48000,pan=stereo|c0=c0|c1=c0,"
        f"adelay={int(VO2_AT * 1000)}|{int(VO2_AT * 1000)}[vo2];"
        "[4:a]volume=0.75[sfx];"
        "[vo1][vo2][sfx]amix=inputs=3:normalize=0:duration=longest,"
        f"atrim=0:{ts(total)},afade=t=out:st={ts(total - 0.6)}:d=0.6,"
        "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]"
    )
    run([
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "warning", "-y",
        "-i", f"{DL}/clip1.mp4", "-i", f"{DL}/clip2.mp4",
        "-i", f"{DL}/vo1.mp3", "-i", f"{DL}/vo2b.mp3", "-i", f"{WORK}/sfx.wav",
        "-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
        "-c:a", "pcm_s16le", f"{WORK}/master.mov",
    ])
    # versão limpa (só carimbos de data) e versão legendada
    for ass, name in ((f"{WORK}/datas.ass", "piloto_limpo.mp4"), (f"{WORK}/legendas.ass", "piloto_legendado.mp4")):
        run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "warning", "-y",
            "-i", f"{WORK}/master.mov",
            "-vf", f"ass={ass}:fontsdir={WORK}/fonts",
            "-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", "20",
            "-maxrate", "18M", "-bufsize", "36M", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", f"{OUT}/{name}",
        ])
    print(json.dumps({"total": ts(total), "lamp": ts(lamp_t), "tl_start": ts(tl_start), "wake": ts(wake)}))


if __name__ == "__main__":
    main()
