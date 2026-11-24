"""Gera as imagens do README do perfil (banner, cards, ícones).

Roda com os repos pedro-dapps-website, ashar_website, trevo-card-site, vai-site e
playhireling clonados lado a lado em /home/claude, e as fontes da marca convertidas
de pedro-dapps-website/assets/fonts para work/fonts (precisa de brotli).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os

R = "/home/claude"
OUT = f"{R}/pedrosgmagalhaes/assets"
os.makedirs(OUT, exist_ok=True)
F = f"{R}/work/fonts"

BG = (9, 8, 7)
CREAM = (246, 241, 231)
GOLD = (200, 155, 82)
GOLD_L = (217, 182, 116)
MUTED = (160, 150, 135)


def font(name, size, wght=None):
    f = ImageFont.truetype(f"{F}/{name}", size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


SIX = lambda s: font("six-caps-latin-400.ttf", s)
PLAY = lambda s, w=600: font("playfair-display-variable.ttf", s, w)
MAN = lambda s, w=500: font("Manrope-VariableFont_wght.ttf", s, w)


def rounded(im, r):
    im = im.convert("RGBA")
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    im.putalpha(m)
    return im


def spaced(draw, xy, text, f, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def load(p):
    return Image.open(f"{R}/{p}").convert("RGBA")


ICONS = {
    "pedrodapps": "pedro-dapps-website/assets/images/pedrodapps_logo.png",
    "ashar": "ashar_website/public/icon-512.png",
    "trevo": "trevo-card-site/org-github-profile/profile/assets/trevo-card-icon.png",
    "vai": "vai-site/site/favicon-512.png",
    "hireling": "playhireling/apps/site/public/icon-512.png",
}


def icon(key, size):
    im = load(ICONS[key])
    im = ImageOps.fit(im, (size, size), Image.LANCZOS)
    if key == "pedrodapps":
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
        im.putalpha(Image.composite(im.getchannel("A"), m, m))
        return im
    return rounded(im, int(size * 0.22))


# ---------- ícones avulsos (cabeçalho dos cards) ----------
for k in ICONS:
    icon(k, 160).save(f"{OUT}/icon-{k}.png")

# ---------- banner ----------
W, H = 1600, 520
b = Image.new("RGBA", (W, H), BG + (255,))

# brilho dourado sutil
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-300, -380, 900, 520], fill=GOLD + (38,))
glow = glow.filter(ImageFilter.GaussianBlur(160))
b.alpha_composite(glow)

# foto do Pedro numa janela arredondada com borda dourada (padrão do kit react)
ph = Image.open(f"{R}/pedro-dapps-website/assets/images/pedro.jpg").convert("RGB")
pw, phh = ph.size
WIN = 400
crop = ImageOps.fit(ph.crop((int(pw * 0.27), 0, int(pw * 0.73), phh)), (WIN, WIN), Image.LANCZOS, centering=(0.5, 0.15))
win = rounded(crop, 36)
wx, wy = W - WIN - 110, (H - WIN) // 2
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle([wx + 10, wy + 22, wx + WIN + 10, wy + WIN + 22], 36, fill=(0, 0, 0, 200))
b.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(26)))
b.alpha_composite(win, (wx, wy))
ImageDraw.Draw(b).rounded_rectangle([wx - 2, wy - 2, wx + WIN + 1, wy + WIN + 1], 38, outline=GOLD, width=3)

d = ImageDraw.Draw(b)
X = 88
spaced(d, (X, 70), "PEDRO MAGALHÃES", PLAY(24, 600), GOLD_L, 5)
T = SIX(132)
d.text((X, 112), "NEGÓCIOS", font=T, fill=CREAM)
d.text((X, 226), "SEM FRONTEIRA", font=T, fill=GOLD)
bot = d.textbbox((X, 226), "SEM FRONTEIRA", font=T)[3]
SUB = "Fundador · Fintech, IA e blockchain · 20+ anos em tecnologia"
d.text((X, bot + 22), SUB, font=MAN(25, 500), fill=(214, 206, 192))
sub_bot = d.textbbox((X, bot + 22), SUB, font=MAN(25, 500))[3]

# linha de logos
y = sub_bot + 30
x = X
for k in ["pedrodapps", "ashar", "trevo", "vai", "hireling"]:
    ic = icon(k, 44)
    b.alpha_composite(ic, (x, y))
    d.rounded_rectangle([x, y, x + 43, y + 43], 10 if k != "pedrodapps" else 22, outline=(90, 80, 65), width=1)
    x += 44 + 14
d.line([(X, sub_bot + 16), (X + 5 * 58 - 14, sub_bot + 16)], fill=GOLD + (90,), width=1)

b.convert("RGB").save(f"{OUT}/banner.png", optimize=True)


# ---------- cards de produto (820x512, mesmo formato) ----------
CW, CH = 1200, 750


def frame(img, name):
    """Print com cantos arredondados e borda fina, fundo transparente."""
    im = ImageOps.fit(img.convert("RGB"), (CW, CH), Image.LANCZOS, centering=(0.5, 0.0))
    im = rounded(im, 28)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, CH - 1], 28, outline=(120, 110, 95, 140), width=2)
    im.save(f"{OUT}/card-{name}.webp", quality=86, method=6)


for n in ["trevo", "vai", "hireling"]:
    frame(Image.open(f"{R}/pedro-dapps-website/assets/images/projects/{n}.jpg"), n)

# Pedro dApps: capa do ep01 (Negócios sem fronteira)
p = Image.new("RGBA", (CW, CH), BG + (255,))
p.alpha_composite(Image.open(f"{R}/pedro-dapps-website/uruguai/ep01/og-ep01-capa-v2-1200x630.jpg").convert("RGBA"))
pd_ = ImageDraw.Draw(p)
pd_.line([(0, 630), (CW, 630)], fill=GOLD, width=2)
txt = "YOUTUBE  ·  BLOG  ·  NEWSLETTER  ·  PEDRODAPPS.COM"
f_ = PLAY(26, 600)
tw = sum(pd_.textlength(c, font=f_) + 3 for c in txt)
spaced(pd_, ((CW - tw) / 2, 672), txt, f_, GOLD_L, 3)
frame(p, "pedrodapps")

# Ashar: três telas do app sobre fundo escuro
a = Image.new("RGBA", (CW, CH), (14, 13, 12, 255))
ag = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
ImageDraw.Draw(ag).ellipse([200, 100, 1000, 900], fill=(232, 90, 50, 30))
a.alpha_composite(ag.filter(ImageFilter.GaussianBlur(140)))
mk = load("ashar_website/src/assets/symbol/ashar-wordmark.svg") if False else None
screens = ["screen-03.webp", "screen-07.webp", "screen-10.webp"]
sh = 620
positions = [(170, 95), (470, 65), (770, 95)]
for s, (px, py) in zip(screens, positions):
    im = Image.open(f"{R}/ashar_website/src/assets/images/mobile/{s}").convert("RGBA")
    im = im.resize((int(im.size[0] * sh / im.size[1]), sh), Image.LANCZOS)
    shadow = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([px + 8, py + 18, px + im.size[0] + 8, py + sh + 18], 40, fill=(0, 0, 0, 160))
    a.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
    a.alpha_composite(im, (px, py))
frame(a, "ashar")
print("ok", sorted(os.listdir(OUT)))
