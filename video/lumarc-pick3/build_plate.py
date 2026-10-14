"""src/take.mp4 (HeyGen green take) -> src/tight.mov: the EDL in timeline.py cut together (pauses removed), plus
src/tight16k.raw (mono 16 kHz float voice used for word alignment)."""
import os, subprocess
from timeline import SEG, snap
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, 'src')
parts = []
for i, (_blk, a, b, _) in enumerate(SEG):
    a, b = snap(a), snap(b)
    parts.append(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}];')
fc = ''.join(parts) + ''.join(f'[v{i}][a{i}]' for i in range(len(SEG))) + f'concat=n={len(SEG)}:v=1:a=1[v][a]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(S, 'take.mp4'), '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-crf', '10', '-preset', 'medium', '-g', '25', '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', os.path.join(S, 'tight.mov')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(S, 'tight.mov'), '-ac', '1', '-ar', '16000', '-f', 'f32le', os.path.join(S, 'tight16k.raw')], check=True)
print('ok')
