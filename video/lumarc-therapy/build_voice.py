"""Assemble the dialogue on the edit timeline: every LINE's audio cut from its take and placed at t0.
-> src/voice_dry.wav (48 kHz mono, dry; sound.py adds the room) and src/voice16k.raw (16 kHz float, word alignment)."""
import os, subprocess
import numpy as np
from timeline import TL, DUR, TAKES
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, 'src'); SR = 48000
out = np.zeros(int((DUR + 1) * SR), np.float32)
for ln in TL:
    b = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f"{ln['s0']:.3f}", '-t', f"{ln['s1'] - ln['s0']:.3f}", '-i', os.path.join(S, TAKES[ln['spk']] + '.mp4'),
                        '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(b, np.float32).copy(); f = int(.010 * SR); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    i = int(round(ln['t0'] * SR)); out[i:i + len(x)] += x
out = out[:int(DUR * SR)]
pcm = (np.clip(out, -1, 1) * 32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', os.path.join(S, 'voice_dry.wav')], input=pcm, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(S, 'voice_dry.wav'), '-ac', '1', '-ar', '16000', '-f', 'f32le', os.path.join(S, 'voice16k.raw')], check=True)
print('ok', DUR)
