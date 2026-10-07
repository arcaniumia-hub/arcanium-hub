"""Lays LUMARC's real logo and Outfit typography over the AI-rendered 4K scene.
Inputs (cwd): bg.png (2880x2880 scene), lumarc-logo.png (logo from slumarc.com), Outfit.ttf (variable)
Usage: python3 compose_premium.py out.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = 2880
BLUE, VIOLET = (59, 91, 255), (139, 61, 255)
WHITE, MUTED, LINE = (250, 249, 246), (166, 166, 184), (255, 255, 255, 40)

def font(size, wght):
    f = ImageFont.truetype('Outfit.ttf', size)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

def gradient(w, h, a=(79, 107, 255), b=(154, 77, 255)):
    g = Image.new('RGBA', (w, h))
    px = g.load()
    for x in range(w):
        k = x / max(1, w - 1); c = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3)) + (255,)
        for y in range(h): px[x, y] = c
    return g

def grad_text(canvas, xy, text, f):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    b = d0.textbbox((0, 0), text, font=f)
    w, h = b[2], b[3]
    mask = Image.new('L', (w, h)); ImageDraw.Draw(mask).text((0, 0), text, font=f, fill=255)
    g = gradient(w, h); g.putalpha(mask)
    P = 90  # pad so the blur is not clipped into a visible box
    gp = gradient(w + 2 * P, h + 2 * P); mp = Image.new('L', gp.size); mp.paste(mask, (P, P)); gp.putalpha(mp)
    gl = gp.filter(ImageFilter.GaussianBlur(30))
    gl.putalpha(gl.split()[3].point(lambda v: int(v * .7)))
    canvas.alpha_composite(gl, (xy[0] - P, xy[1] - P)); canvas.alpha_composite(g, xy)
    return w

src = Image.open('bg.png').convert('RGBA').resize((S, S), Image.LANCZOS)
# shrink the scene and anchor it bottom-right, so the left column stays clear for type
K, OFF = .88, 346
sc = src.resize((int(S * K), int(S * K)), Image.LANCZOS)
corner = src.resize((8, 8)).getpixel((0, 0))
c = Image.new('RGBA', (S, S), corner[:3] + (255,))
# feather the scene's top and left edges into the flat background
left = Image.linear_gradient('L').rotate(90).resize((220, sc.height))   # 0 at the left edge -> 255
top = Image.linear_gradient('L').resize((sc.width, 220))                 # 0 at the top edge -> 255
ml = Image.new('L', sc.size, 255); ml.paste(left, (0, 0))
mt = Image.new('L', sc.size, 255); mt.paste(top, (0, 0))
mask = ImageChops.multiply(ml, mt)
c.paste(sc, (OFF, OFF), mask)
# soft dark scrim on the left so type always reads
scrim = Image.new('RGBA', (S, S), (0, 0, 0, 0)); sd = ImageDraw.Draw(scrim)
for x in range(S):
    a = int(170 * max(0, 1 - x / (S * .62)) ** 1.4)
    sd.line([(x, 0), (x, S)], fill=(14, 14, 20, a))
c.alpha_composite(scrim)
d = ImageDraw.Draw(c)
X = 190

# logo
logo = Image.open('lumarc-logo.png').convert('RGBA')
lw = 640; logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
# drop the logo's faint low-alpha haze (it read as a box on the dark background)
logo.putalpha(logo.split()[3].point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 255 / 215))))
c.alpha_composite(logo, (X - 20, 170))

# eyebrow
f_eb = font(46, 500)
d.text((X, 520), 'ESTÚDIO DE CONTEÚDO', font=f_eb, fill=MUTED + (255,), spacing=0)
# headline
f_h = font(196, 400)
d.text((X, 620), 'Conteúdo que faz', font=f_h, fill=WHITE + (255,))
d.text((X, 840), 'o seu negócio', font=f_h, fill=WHITE + (255,))
grad_text(c, (X, 1060), 'parar o scroll.', font(196, 500))
d = ImageDraw.Draw(c)
# sub
f_sub = font(62, 300)
d.text((X, 1340), 'Tudo o que a sua marca precisa nas redes,', font=f_sub, fill=MUTED + (255,))
d.text((X, 1420), 'do post ao vídeo.', font=f_sub, fill=MUTED + (255,))

# services
SERV = ['Gestão de mídias sociais', 'Artes e posts', 'Carrosséis', 'Reels e vídeos', 'Edição de vídeo', 'Sites sob medida']
f_n, f_s = font(46, 500), font(76, 400)
y0, step = 1600, 142
for i, s in enumerate(SERV):
    y = y0 + i * step
    ImageDraw.Draw(c).line([(X, y), (X + 1000, y)], fill=LINE, width=3)
    grad_text(c, (X, y + 44), f'{i + 1:02d}', f_n)
    ImageDraw.Draw(c).text((X + 130, y + 30), s, font=f_s, fill=WHITE + (255,))
d = ImageDraw.Draw(c)
d.line([(X, y0 + 6 * step), (X + 1000, y0 + 6 * step)], fill=LINE, width=3)

# CTA pill
f_cta = font(64, 500)
txt = 'Pedir orçamento grátis'
tb = d.textbbox((0, 0), txt, font=f_cta)
pw, ph = tb[2] + 140, 150
py = 2560
pill = gradient(pw, ph, BLUE, VIOLET)
m = Image.new('L', (pw, ph)); ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=255)
pill.putalpha(m)
glow = Image.new('RGBA', (pw + 200, ph + 200), (0, 0, 0, 0)); glow.alpha_composite(pill, (100, 100))
c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)), (X - 100, py - 100))
c.alpha_composite(pill, (X, py))
d = ImageDraw.Draw(c)
d.text((X + 70, py + (ph - (tb[3] - tb[1])) // 2 - tb[1]), txt, font=f_cta, fill=(255, 255, 255, 255))

# contacts, next to the button (the bottom-right corner belongs to the scene)
f_c = font(54, 400)
for j, t in enumerate(['@lumarc_studio', 'slumarc.com']):
    d.text((X + pw + 90, py + 4 + j * 74), t, font=f_c, fill=(WHITE if j == 0 else MUTED) + (255,))

c.convert('RGB').save(sys.argv[1])
print('ok')
