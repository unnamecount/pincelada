"""Dibuja los iconos de Pincelada (gota de pintura + pincel) en PNG.
Uso: python iconos.py   → crea icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png
"""
from PIL import Image, ImageDraw

BG = (255, 244, 248)
BLOB = (207, 51, 107)
INK = (31, 26, 29)


def bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# Contorno en la caja de 40×40 del logotipo de la app
BLOB_PTS = (bez((8, 31), (12, 30), (14, 27), (14, 24)) + bez((14, 24), (14, 21.6), (15.8, 19.8), (18, 19.8))[1:]
            + bez((18, 19.8), (20.3, 19.8), (22, 21.6), (22, 23.9))[1:] + bez((22, 23.9), (22, 29), (15.5, 33.5), (8, 31))[1:])
HANDLE = [(19.5, 18.6), (32, 5.5)] + bez((32, 5.5), (33, 4.5), (34.6, 6.1), (33.6, 7.1))[1:] + [(21.3, 21)]
CENTER = (21.3, 19.0)
SPAN = 30.0  # alto aproximado del dibujo en la caja de 40


def icon(size, glyph, rounded, path):
    k = 4
    S = size * k
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=BG)
    else:
        d.rectangle([0, 0, S, S], fill=BG)
    sc = S * glyph / SPAN
    tr = lambda p: (S / 2 + (p[0] - CENTER[0]) * sc, S / 2 + (p[1] - CENTER[1]) * sc)
    d.polygon([tr(p) for p in BLOB_PTS], fill=BLOB)
    w = 2.6 * sc
    pts = [tr(p) for p in HANDLE]
    d.polygon(pts, fill=INK)
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=INK, width=int(round(w)))
    for p in pts:
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=INK)
    img = img.resize((size, size), Image.LANCZOS)
    if not rounded:
        img = img.convert('RGB')
    img.save(path)


if __name__ == '__main__':
    icon(192, 0.64, True, 'icon-192.png')
    icon(512, 0.64, True, 'icon-512.png')
    icon(512, 0.50, False, 'icon-maskable-512.png')
    icon(180, 0.58, False, 'apple-touch-icon.png')
    print('iconos listos')
