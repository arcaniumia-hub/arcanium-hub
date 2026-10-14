#!/usr/bin/env python3
"""Desenho de som sintetizado para o piloto "Enquanto você dormia".

Gera uma trilha de ambiência (sem música licenciada) a partir de um JSON de
marcações de tempo:
  - room tone (ruído marrom filtrado)
  - drone grave em lá menor que cresce no timelapse
  - tique-taque de relógio que acelera durante o timelapse
  - clique do abajur e farfalhar do cobertor
  - whoosh ascendente do tempo passando
  - acorde brilhante (lá maior com nona) no "acordou hoje"

Uso: python3 sfx_synth.py marcas.json saida.wav
"""
import json
import math
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a, r, sustain=1.0):
    e = np.full(n, sustain, dtype=np.float64)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, sustain, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def onepole_lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def svf_bandpass(x, fc_curve, q=1.2):
    """Filtro state-variable com frequência central variável (para o whoosh)."""
    low = band = 0.0
    y = np.empty_like(x)
    damp = 1.0 / q
    for i, v in enumerate(x):
        f = 2 * math.sin(math.pi * min(fc_curve[i], SR / 6) / SR)
        high = v - low - damp * band
        band += f * high
        low += f * band
        y[i] = band
    return y


def place(track, clip, start):
    s = int(start * SR)
    if s >= len(track):
        return
    e = min(len(track), s + len(clip))
    track[s:e] += clip[: e - s]


def tick(tone=2600.0, gain=1.0):
    n = int(0.035 * SR)
    t = np.arange(n) / SR
    burst = rng.standard_normal(n) * np.exp(-t * 900)
    ping = np.sin(2 * np.pi * tone * t) * np.exp(-t * 260)
    body = np.sin(2 * np.pi * 900 * t) * np.exp(-t * 400)
    return gain * (0.35 * burst + 0.5 * ping + 0.3 * body)


def lamp_click():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    snap = rng.standard_normal(n) * np.exp(-t * 1400)
    snap = snap - onepole_lp(snap, 1800)  # passa-altas simples
    thump = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 60)
    click2 = np.zeros(n)
    k = int(0.012 * SR)
    click2[k:] = (rng.standard_normal(n - k) * np.exp(-t[: n - k] * 2000)) * 0.6
    return 0.9 * snap + 0.35 * thump + 0.5 * click2


def rustle(dur=1.6):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    noise = onepole_lp(onepole_lp(noise, 1800), 1800)
    noise = noise - onepole_lp(noise, 250)
    t = np.arange(n) / SR
    # várias "dobras" de tecido
    env = np.zeros(n)
    for c in (0.15, 0.45, 0.8, 1.15):
        env += np.exp(-((t - c * dur / 1.3) ** 2) / (2 * 0.09 ** 2))
    return noise * env * 0.8


def main():
    marks = json.load(open(sys.argv[1]))
    out_path = sys.argv[2]
    total = marks["total"]
    n = int(total * SR)
    t = t_axis(total)
    L = np.zeros(n)
    R = np.zeros(n)

    tl0, tl1 = marks["timelapse_start"], marks["timelapse_end"]
    wake = marks["wake"]

    # room tone
    brown = np.cumsum(rng.standard_normal(n))
    brown -= onepole_lp(brown, 8)
    brown /= np.max(np.abs(brown)) + 1e-9
    room = onepole_lp(brown, 900)
    room = (room - onepole_lp(room, 60)) * 0.06  # tira o grave excessivo
    L += room
    R += np.roll(room, 311)

    # drone em lá menor (A1, E2, A2, C3, E3) com batimento lento
    drone = np.zeros(n)
    for f, g in ((55.0, 0.5), (82.41, 0.35), (110.0, 0.3), (130.81, 0.18), (164.81, 0.12)):
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.07 + f / 4000) * t + f)
        drone += g * lfo * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t))
    drone = onepole_lp(drone, 700)
    d_env = np.clip(t / 4.0, 0, 1) * 0.55
    swell = np.clip((t - tl0) / max(tl1 - tl0, 0.1), 0, 1)
    d_env = d_env + 0.6 * swell * (t < wake)
    after = t >= wake
    d_env[after] = (0.55 + 0.6) * np.exp(-(t[after] - wake) * 1.8) + 0.25
    fade_out = np.clip((total - t) / 1.2, 0, 1)
    drone *= d_env * fade_out * 0.16
    L += drone
    R += np.roll(drone, 97)

    # tique-taque: lento até o timelapse, acelerando até virar um borrão
    tick_t, k = 1.2, 0
    while tick_t < wake - 0.15:
        if tick_t < tl0:
            interval, g = 1.0, 0.10
        else:
            p = (tick_t - tl0) / max(wake - tl0, 0.1)
            interval = max(0.035, 0.5 * (0.035 / 0.5) ** p)
            g = 0.10 + 0.12 * p
        clip = tick(2600 if k % 2 == 0 else 2150, g)
        pan = 0.4 if k % 2 == 0 else -0.4
        place(L, clip * (1 - pan) * 0.6, tick_t)
        place(R, clip * (1 + pan) * 0.6, tick_t)
        tick_t += interval
        k += 1

    # clique do abajur e farfalhar do cobertor
    if marks.get("lamp_off") is not None:
        c = lamp_click() * 0.32
        place(L, c, marks["lamp_off"] - 0.02)
        place(R, c * 0.85, marks["lamp_off"] - 0.02)
    if marks.get("rustle") is not None:
        r = rustle() * 0.10
        place(L, r, marks["rustle"])
        place(R, np.roll(r, 240), marks["rustle"])

    # whoosh ascendente do timelapse
    wd = wake - tl0 + 0.25
    wn = int(wd * SR)
    wt = np.arange(wn) / SR
    fc = 160 * (3200 / 160) ** (wt / wd)
    w = svf_bandpass(rng.standard_normal(wn), fc, q=1.6)
    w_env = (wt / wd) ** 2.2 * np.clip((wd - wt) / 0.08, 0, 1)
    w *= w_env * 0.20
    place(L, w, tl0)
    place(R, np.roll(w, 180), tl0)

    # acorde do despertar (lá maior com nona), suave e brilhante
    cd = total - wake
    cn = int(cd * SR)
    ct = np.arange(cn) / SR
    chord = np.zeros(cn)
    for f, g in ((440.0, 0.30), (554.37, 0.22), (659.25, 0.22), (987.77, 0.12), (1318.5, 0.07)):
        chord += g * np.sin(2 * np.pi * f * ct + f) * (0.8 + 0.2 * np.sin(2 * np.pi * 4.5 * ct + f))
    chord *= env_adsr(cn, 0.35, min(1.4, cd * 0.6)) * 0.07
    place(L, chord, wake)
    place(R, np.roll(chord, 150), wake)
    # sub-impacto bem discreto no despertar
    bn = int(1.8 * SR)
    bt = np.arange(bn) / SR
    boom = np.sin(2 * np.pi * 48 * bt) * np.exp(-bt * 2.2) * 0.10
    place(L, boom, wake)
    place(R, boom, wake)

    st = np.stack([L, R], axis=1)
    st /= max(1.0, np.max(np.abs(st)) / 0.89)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
