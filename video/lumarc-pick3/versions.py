"""Splice the three ads from the MASTER render: hook_k + BODY (picture, voice, music, sfx), mix and encode.

    python3 versions.py            # all three -> out/lumarc-pick3-A1.mp4, -A2.mp4, -A3.mp4
    python3 versions.py A2         # one

Blocks sit on the 0.2 s grid, so the cut points are exact frames at 30 fps (picture) and exact samples at 48 kHz.
Mix = the casa/ia recipe: voice (HPF, presence, compression) + music hard-ducked under the voice + SFX lightly ducked,
loudness -14 LUFS / -1.2 dBTP; 2-pass x264 under the 30 MB chat limit.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E

def spans(v):
    return [E.BLOCK_SPAN[v], E.BLOCK_SPAN['B']]

def build(v):
    (h0, h1), (b0, b1) = spans(v); dur = round(h1 - h0 + b1 - b0, 3)
    F = lambda t: int(round(t * E.FPS)); S = lambda t: int(round(t * 48000))
    def acut(i, tag):
        return (f'[{i}:a]aresample=48000,asplit=2[{tag}a][{tag}b];'
                f'[{tag}a]atrim=start_sample={S(h0)}:end_sample={S(h1)},asetpts=PTS-STARTPTS[{tag}0];'
                f'[{tag}b]atrim=start_sample={S(b0)}:end_sample={S(b1)},asetpts=PTS-STARTPTS[{tag}1];'
                f'[{tag}0][{tag}1]concat=n=2:v=0:a=1[{tag}];')
    af = (acut(0, 'vo') + acut(1, 'mu') + acut(2, 'fx') +
          '[vo]highpass=f=80,equalizer=f=3200:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,'
          'asplit=3[v][key][key2];[mu]volume=0.30[m];[m][key]sidechaincompress=threshold=0.035:ratio=7:attack=15:release=300[md];'
          '[fx]volume=0.32[s];[s][key2]sidechaincompress=threshold=0.1:ratio=2:attack=10:release=200[sd];'
          '[v][md][sd]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=11[a]')
    mixwav = os.path.join(E.OUT, f'mix-{v}.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.SRC, 'tight.mov'), '-i', os.path.join(HERE, 'music.wav'),
                    '-i', os.path.join(HERE, 'sfx.wav'), '-filter_complex', af, '-map', '[a]', '-c:a', 'pcm_s16le', '-ar', '48000', mixwav], check=True)
    vf = (f'[0:v]split=2[p][q];[p]trim=start_frame={F(h0)}:end_frame={F(h1)},setpts=PTS-STARTPTS[v0];'
          f'[q]trim=start_frame={F(b0)}:end_frame={F(b1)},setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[v]')
    out = os.path.join(E.OUT, f'lumarc-pick3-{v}.mp4')
    kb = min(int(27.8 * 8 * 1024 / dur) - 192, 12000)
    for ps in (1, 2):
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(E.OUT, 'video.mp4'), '-i', mixwav, '-filter_complex', vf,
               '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-tune', 'film',
               '-x264-params', 'aq-mode=3:aq-strength=1.0:deblock=-1,-1', '-b:v', f'{kb}k', '-pass', str(ps),
               '-passlogfile', os.path.join(E.OUT, f'x264-{v}'), '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
               '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.3f}']
        subprocess.run(cmd + (['-f', 'mp4', '/dev/null'] if ps == 1 else [out]), check=True)
    print(out, round(os.path.getsize(out) / 1e6, 2), 'MB', dur, 's')

if __name__ == '__main__':
    for v in (sys.argv[1:] or ['A1', 'A2', 'A3']): build(v)
