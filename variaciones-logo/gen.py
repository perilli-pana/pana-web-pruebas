import math, json, os
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SP, "deck")
os.makedirs(os.path.join(ROOT, "project/slides"), exist_ok=True)

WORD = open(os.path.join(SP, "word_d.txt")).read().split("\n")
GR = json.load(open(os.path.join(SP, "grids.json")))

RED = "#F50000"; INK = "#0B0909"; CREAM = "#F4F0E6"; NAVY = "#0A2A66"; BLUE = "#1530E6"
WHITE = "#FBF8F2"; GOLD = "#C9A24A"; CYAN = "#00D9F5"
C0 = 131.08
RX, RY, ROT = 88.3, 45.01, math.radians(-3.96)

def DEFS(extra=""):
    return ('<defs><g id="w">' + "".join(f'<path d="{d}"/>' for d in WORD) + '</g>'
            f'<ellipse id="o" cx="{C0}" cy="{C0}" rx="{RX}" ry="{RY}" transform="rotate(-3.96 {C0} {C0})"/>' + extra + '</defs>')

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def L(cx, cy, s, word=RED, oval=RED, sw=3, pre="", sx=1, sy=1, wattr="", oattr="", gattr=""):
    sc = f"scale({f(s*sx)} {f(s*sy)})" if (sx != 1 or sy != 1) else f"scale({f(s)})"
    o = f'<use href="#o" fill="none" stroke="{oval}" stroke-width="{sw}" {oattr}/>' if oval else ""
    w = f'<use href="#w" fill="{word}" {wattr}/>' if word else ""
    return f'<g transform="translate({f(cx)} {f(cy)}) {pre} {sc} translate(-{C0} -{C0})" {gattr}>{o}{w}</g>'

def ghost(cx, cy, s, col, bg, pre="", px=1.4):
    """contorno hueco (una copia del eco)"""
    return (f'<g transform="translate({f(cx)} {f(cy)}) {pre} scale({f(s)}) translate(-{C0} -{C0})">'
            f'<use href="#o" fill="none" stroke="{col}" stroke-width="{px}" vector-effect="non-scaling-stroke"/>'
            f'<use href="#w" fill="{bg}" stroke="{col}" stroke-width="{px}" vector-effect="non-scaling-stroke"/></g>')

def eco(cx, cy, s, dx, dy, n, col, bg, solid=True, px=1.4):
    out = [ghost(cx + dx*k, cy + dy*k, s, col, bg, px=px) for k in range(n, 0, -1)]
    if solid: out.append(L(cx, cy, s, col, col))
    return "".join(out)

def mobius(cx, cy, s, a, twist=0.0, M=150, col=RED, Wu=34, spin_k=1.3, tilt_k=1.0, ew=2.6, rw=1.1):
    W = a*Wu; tilt = a*tilt_k; spin = a*spin_k; F = 600
    def P(u, v):
        c, sn = math.cos(u), math.sin(u)
        x, y = RX*c, RY*sn
        nx, ny = RY*c, RX*sn; nl = math.hypot(nx, ny); nx /= nl; ny /= nl
        h = u/2 + twist; cw = math.cos(h)*v*W; sw_ = math.sin(h)*v*W
        x += nx*cw; y += ny*cw; z = sw_
        x1 = x*math.cos(ROT) - y*math.sin(ROT); y1 = x*math.sin(ROT) + y*math.cos(ROT)
        y2 = y1*math.cos(tilt) - z*math.sin(tilt); z2 = y1*math.sin(tilt) + z*math.cos(tilt)
        x3 = x1*math.cos(spin) + z2*math.sin(spin); z3 = -x1*math.sin(spin) + z2*math.cos(spin)
        k = F/(F + z3)
        return (cx + s*x3*k, cy + s*y2*k, z3)
    buckets = {}
    for i in range(M):
        u = i/M*math.pi*2; A = P(u, -1); B = P(u, 1)
        op = max(0.12, min(1, 0.6 - ((A[2]+B[2])/2)/(RX*2+1)*0.5))
        b = round(op*5)/5
        buckets.setdefault(b, []).append(f"M{f(A[0])} {f(A[1])}L{f(B[0])} {f(B[1])}")
    out = [f'<path d="{"".join(v)}" stroke="{col}" stroke-width="{rw}" opacity="{k}" fill="none"/>' for k, v in sorted(buckets.items())]
    pts = [P(j/(M*2)*math.pi*4, -1) for j in range(M*2 + 1)]
    out.append(f'<path d="M' + "L".join(f"{f(p[0])} {f(p[1])}" for p in pts) + f'" stroke="{col}" stroke-width="{ew}" fill="none" stroke-linejoin="round"/>')
    return "".join(out)

def rings(cx, cy, s, n, pitch, col, px=1.4, rot=0, extra=""):
    return "".join(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(RX*s*(1+i*pitch))}" ry="{f(RY*s*(1+i*pitch))}" transform="rotate({f(-3.96+rot)} {f(cx)} {f(cy)})" fill="none" stroke="{col}" stroke-width="{px}" {extra}/>' for i in range(n))

def pixel(ox, oy, cell, gap, col, thr=0.42, grid="pix"):
    g = GR[grid]; d = []
    for j, r in enumerate(g):
        for i, v in enumerate(r):
            if v > thr: d.append(f"M{f(ox+i*cell)} {f(oy+j*cell)}h{f(cell-gap)}v{f(cell-gap)}h-{f(cell-gap)}z")
    return f'<path d="{"".join(d)}" fill="{col}"/>'

def halftone(ox, oy, cell, col):
    g = GR["dots"]; out = []
    for j, r in enumerate(g):
        for i, v in enumerate(r):
            if v > 0.16:
                out.append(f'<circle cx="{i}" cy="{j}" r="{("%.2f" % (math.sqrt(v)*0.62)).lstrip("0")}"/>')
    return f'<g fill="{col}" transform="translate({ox+cell/2} {oy+cell/2}) scale({cell})">' + "".join(out) + '</g>'

def SVG(body, x=0, y=0, w=1920, h=1080, alt="", extra_defs=""):
    return (f'<svg aria-label="{alt}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px">' + DEFS(extra_defs) + body + '</svg>')

SHADOW = '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" flood-opacity=".28"/></filter>'

def sec(id, bg, fg, kids, notes=None, tr="fade"):
    a = f"<aside>{notes}</aside>" if notes else ""
    return (f'<section id="{id}" data-transition="{tr}" style="background:{bg};color:{fg};font-family:\'Pana Regular\', Arial, sans-serif;'
            f'padding:128px;display:flex;flex-direction:column">\n' + "\n".join(kids) + a + "\n</section>\n")

def lab(t, x, y, w, col, size=24, align="left", ls=5):
    return (f'<p style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;letter-spacing:{ls}px;'
            f'text-transform:uppercase;text-align:{align};color:{col};line-height:1.2">{t}</p>')

def head(label, title, col, accent=RED, sub=None, subcol=None):
    k = [lab(label, 128, 88, 1400, accent),
         f'<h2 style="position:absolute;left:128px;top:128px;width:1664px;font-family:\'Pana Black\', Impact, sans-serif;font-size:120px;'
         f'font-weight:400;line-height:0.9;text-transform:uppercase;color:{col}">{title}</h2>']
    if sub:
        k.append(f'<p style="position:absolute;left:128px;top:246px;width:1500px;font-family:\'Pana Italic\', Georgia, serif;font-size:40px;'
                 f'line-height:1.2;color:{subcol or col}">{sub}</p>')
    return k

S = {}

# ---------- 01 portada ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
for k in range(7, 0, -1):
    body += f'<g opacity="{f(0.55-k*0.06)}">' + ghost(960 - k*20, 600 - k*13, 6.2, RED, INK) + '</g>'
body += L(960, 600, 6.2)
S["portada"] = sec("portada", INK, CREAM, [
    SVG(body, alt="El logo de pana enorme en rojo sobre negro, con contornos que se alejan"),
    lab("Pana estudio creativo — oct 2026", 128, 88, 1000, RED),
    lab("Variaciones del logo", 1092, 88, 700, CREAM, align="right"),
    f'<p style="position:absolute;left:128px;top:930px;width:1664px;font-family:\'Pana Italic\', Georgia, serif;font-size:44px;color:{CREAM}">el logo de Bruno, estirado para ver hasta dónde da</p>',
], "Presentación de juego: colores, formas y aplicaciones posibles del logo de Pana. Nada de esto es final, es para seguir imaginando.")

# ---------- 02 anatomía ----------
body = (f'<rect width="1920" height="1080" fill="{CREAM}"/>' + L(560, 700, 4.3)
        + f'<line x1="1080" y1="420" x2="1080" y2="960" stroke="{INK}" stroke-width="1" opacity=".25"/>'
        + L(1330, 560, 2.1, word=None) + L(1330, 840, 2.1, oval=None))
S["anatomia"] = sec("anatomia", CREAM, INK, [
    SVG(body, alt="El logo completo, y al lado sus dos piezas por separado: el anillo y la palabra"),
    *head("00 — El punto de partida", "Un anillo y una palabra", INK,
          sub="Todo lo que sigue sale de jugar con estas dos piezas: separarlas, multiplicarlas, girarlas, romperlas."),
    lab("El anillo", 1590, 545, 220, RED), lab("La palabra", 1590, 825, 220, RED),
])

# ---------- 03 color: grilla ----------
tiles = [("Original", INK, RED, RED), ("Papel", CREAM, RED, RED), ("Americano", CREAM, RED, NAVY), ("Racing", "#FBFAF7", RED, BLUE),
         ("Marino", NAVY, RED, CREAM), ("Rojo pleno", RED, CREAM, CREAM), ("Vibra", BLUE, RED, RED), ("Fotocopia", CREAM, INK, INK)]
body = f'<rect width="1920" height="1080" fill="#1C1717"/>'
kids = []
TW, TH = 398, 270
for i, (n, bg, ov, wd) in enumerate(tiles):
    x = 128 + (i % 4)*(TW + 24); y = 300 + (i//4)*340
    body += f'<rect x="{x}" y="{y}" width="{TW}" height="{TH}" fill="{bg}"/>' + L(x + TW/2, y + TH/2, 1.55, wd, ov)
    kids.append(lab(n, x, y + TH + 12, TW, CREAM))
S["color-grilla"] = sec("color-grilla", "#1C1717", CREAM, [
    SVG(body, alt="Ocho combinaciones de color del logo en una grilla"),
    *head("01 — Color", "Ocho pieles", CREAM), *kids])

# ---------- 04 color loco ----------
grad = (f'<linearGradient id="fuego" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE14A"/><stop offset=".45" stop-color="{RED}"/><stop offset="1" stop-color="#5A0000"/></linearGradient>'
        f'<linearGradient id="fuego2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE14A"/><stop offset=".5" stop-color="{RED}"/><stop offset="1" stop-color="#FF2F8E"/></linearGradient>')
PW, PH, PY = 392, 520, 330
px_ = [128 + i*(PW + 32) for i in range(4)]
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>'
# riso
x = px_[0]; cx = x + PW/2; cy = PY + PH/2
body += f'<rect x="{x}" y="{PY}" width="{PW}" height="{PH}" fill="#EFE7D6"/>'
body += f'<g style="mix-blend-mode:multiply">{L(cx-7, cy-5, 1.9, "#1F6BFF", "#1F6BFF")}</g><g style="mix-blend-mode:multiply">{L(cx+7, cy+5, 1.9, "#FF3D6E", "#FF3D6E")}</g>'
# anaglifo
x = px_[1]; cx = x + PW/2
body += f'<rect x="{x}" y="{PY}" width="{PW}" height="{PH}" fill="{INK}"/>'
body += f'<g style="mix-blend-mode:screen">{L(cx-9, cy, 1.9, CYAN, CYAN)}</g><g style="mix-blend-mode:screen">{L(cx+9, cy, 1.9, RED, RED)}</g>'
# fuego
x = px_[2]; cx = x + PW/2
body += f'<rect x="{x}" y="{PY}" width="{PW}" height="{PH}" fill="{INK}"/>' + L(cx, cy, 1.9, "url(#fuego)", "url(#fuego2)", sw=4)
# térmica
x = px_[3]; cx = x + PW/2
body += f'<clipPath id="ct"><rect x="{x}" y="{PY}" width="{PW}" height="{PH}"/></clipPath><rect x="{x}" y="{PY}" width="{PW}" height="{PH}" fill="{NAVY}"/>'
cols = ["#FFE14A", "#FFB21F", "#FF7A12", "#FF3D1F", RED, "#C4002E", "#86004A", "#4A0060"]
body += '<g clip-path="url(#ct)">' + "".join(
    f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(RX*1.9*(1+i*0.17))}" ry="{f(RY*1.9*(1+i*0.17))}" transform="rotate(-3.96 {f(cx)} {f(cy)})" fill="none" stroke="{c}" stroke-width="7"/>'
    for i, c in enumerate(cols)) + '</g>' + L(cx, cy, 1.9, CREAM, None)
names = ["Riso / sobreimpresión", "Anaglifo 3D", "Degradé fuego", "Térmica"]
S["color-loco"] = sec("color-loco", CREAM, INK, [
    SVG(body, alt="Cuatro versiones de color experimentales del logo", extra_defs=grad),
    *head("01 — Color", "Color, versión loca", INK), *[lab(n, px_[i], PY + PH + 18, PW, RED) for i, n in enumerate(names)]])

# ---------- 05 möbius secuencia ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
kids = []
for i in range(5):
    a = i/4; cx = 128 + 166 + i*333; cy = 640
    if i == 0:
        body += L(cx, cy, 1.55)
    else:
        body += mobius(cx, cy, 1.6, a*0.85, twist=i*0.5, M=110, Wu=30, ew=2, rw=0.9)
        body += f'<g opacity="{f(1-a*0.8)}">' + L(cx, cy, 1.55*(1-a*0.25), RED, None) + '</g>'
    kids.append(lab(f"{i+1:02d}", cx - 100, 900, 200, RED if i in (0, 4) else "#7C6F6A", align="center"))
S["mobius-secuencia"] = sec("mobius-secuencia", INK, CREAM, [
    SVG(body, alt="Cinco cuadros: el anillo del logo se transforma de a poco en una cinta de Möbius"),
    *head("02 — Möbius", "El anillo se da vuelta", CREAM, sub="Lo bueno del Möbius es el camino: cada cuadro puede ser una pieza distinta.", subcol="#BFB3AC"),
    *kids], "Cada cuadro es una foto fija del efecto que ya está en la web de prueba. El 03 o el 04 pueden ser una versión quieta del logo.")

# ---------- 06 möbius como isotipo ----------
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>'
body += mobius(640, 650, 3.0, 0.62, twist=1.1, M=180, Wu=30, ew=3.2, rw=1.2) + L(640, 650, 2.3, RED, None)
body += f'<circle cx="1330" cy="560" r="170" fill="{RED}"/>' + mobius(1330, 560, 1.15, 0.7, twist=1.1, M=120, col=CREAM, Wu=30, ew=2.4, rw=1)
body += f'<rect x="1580" y="490" width="140" height="140" rx="28" fill="{INK}"/>' + mobius(1650, 560, 0.55, 0.7, twist=1.1, M=60, col=RED, Wu=30, ew=2, rw=1.4)
body += f'<rect x="1230" y="800" width="560" height="110" rx="55" fill="{INK}"/>' + mobius(1320, 855, 0.38, 0.7, twist=1.1, M=60, col=RED, Wu=30, ew=1.6, rw=1) + L(1520, 855, 0.75, CREAM, None)
S["mobius-marca"] = sec("mobius-marca", CREAM, INK, [
    SVG(body, alt="La cinta de Möbius como isotipo: grande con la palabra, en un perfil redondo, como ícono y en una barra"),
    *head("02 — Möbius", "La cinta como isotipo", INK, sub="Cuando la palabra no entra, la cinta sola ya es Pana."),
    lab("Perfil", 1180, 750, 300, RED, align="center"), lab("Ícono", 1560, 650, 180, RED, align="center"),
    lab("Firma / pie de mail", 1230, 930, 560, RED, align="center")])

# ---------- 07 moiré ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
body += f'<clipPath id="m1"><rect x="128" y="330" width="816" height="650"/></clipPath><clipPath id="m2"><rect x="976" y="330" width="816" height="650"/></clipPath>'
body += f'<g clip-path="url(#m1)">{rings(536, 655, 1.6, 34, 0.12, RED, px=1.3)}<rect x="300" y="560" width="0" height="0"/></g>'
body += f'<ellipse cx="536" cy="655" rx="{f(RX*1.6*0.97)}" ry="{f(RY*1.6*0.92)}" transform="rotate(-3.96 536 655)" fill="{INK}"/>' + L(536, 655, 1.6)
body += f'<g clip-path="url(#m2)">{rings(1384, 655, 1.6, 34, 0.12, RED, px=1.3)}{rings(1384+26, 655+10, 1.6, 34, 0.125, RED, px=1.3, rot=4)}</g>'
body += f'<ellipse cx="1384" cy="655" rx="{f(RX*1.6*0.97)}" ry="{f(RY*1.6*0.92)}" transform="rotate(-3.96 1384 655)" fill="{INK}"/>' + L(1384, 655, 1.6)
S["moire"] = sec("moire", INK, CREAM, [
    SVG(body, alt="El anillo repetido en ondas finas; a la derecha dos ondas cruzadas que vibran"),
    *head("02 — Möbius", "Onda y moiré", CREAM, sub="Fino, como te gustó: el anillo que se repite hasta vibrar.", subcol="#BFB3AC"),
    lab("Onda", 128, 992, 400, RED), lab("Dos ondas cruzadas", 976, 992, 600, RED)])

# ---------- 08 eco ----------
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>' + eco(900, 640, 4.0, 13, 11, 10, RED, CREAM)
S["eco"] = sec("eco", CREAM, INK, [
    SVG(body, alt="El logo con diez contornos detrás que forman un relieve, como en la hoja de VICIO"),
    *head("03 — Eco", "El eco de VICIO", INK, sub="El logo deja rastro, como si se moviera. Quieto también funciona: parece un sello en relieve.")])

# ---------- 09 eco variantes ----------
BG2 = INK
body = f'<rect width="1920" height="1080" fill="{BG2}"/>'
s = 1.3; cy = PY + PH/2
for i, x in enumerate(px_):
    body += f'<clipPath id="e{i}"><rect x="{x}" y="{PY}" width="{PW}" height="{PH}"/></clipPath><rect x="{x}" y="{PY}" width="{PW}" height="{PH}" fill="none" stroke="#3A3030"/>'
    cx = x + PW/2; g = ""
    if i == 0:   # escalera
        g = eco(cx, cy + 90, s, 0, -22, 8, RED, BG2)
    elif i == 1:  # túnel
        g = "".join(ghost(cx, cy, s*(1 + k*0.22), RED, BG2) for k in range(9, 0, -1)) + L(cx, cy, s)
    elif i == 2:  # abanico
        g = "".join(ghost(cx, cy, s, RED, BG2, pre=f"rotate({k*-7})") for k in range(8, 0, -1)) + L(cx, cy, s)
    else:  # ola
        g = "".join(ghost(cx - 120 + k*0 + (8-k)*30, cy + math.sin(k*0.9)*38, s*0.8, RED, BG2) for k in range(8, 0, -1)) + L(cx + 120, cy + math.sin(0)*38, s*0.8)
    body += f'<g clip-path="url(#e{i})">{g}</g>'
names = ["Escalera", "Túnel", "Abanico", "Ola"]
S["eco-variantes"] = sec("eco-variantes", INK, CREAM, [
    SVG(body, alt="Cuatro variantes del eco: subiendo, en túnel, en abanico y en ola"),
    *head("03 — Eco", "El eco para otros lados", CREAM), *[lab(n, px_[i], PY + PH + 18, PW, RED) for i, n in enumerate(names)]])

# ---------- 10 elástico ----------
body = (f'<rect width="1920" height="1080" fill="{RED}"/>' + L(470, 690, 2.0, INK, INK, sx=1.75, sy=0.55)
        + L(1060, 680, 2.0, INK, INK, sx=0.55, sy=1.85) + L(1530, 690, 1.9, INK, INK, pre="skewX(-28)"))
S["elastico"] = sec("elastico", RED, INK, [
    SVG(body, alt="El logo aplastado a lo ancho, estirado a lo alto y torcido como en velocidad"),
    *head("04 — Formas", "Elástico", INK, accent=INK, sub="La palabra aguanta que la estiren: ancho de cartel, alto de afiche, torcida de velocidad."),
    lab("Cartel", 170, 930, 600, INK, align="center"), lab("Afiche", 860, 930, 400, INK, align="center"), lab("Velocidad", 1330, 930, 400, INK, align="center")])

# ---------- 11 pixel y punto ----------
pv = SVG(f'<rect width="816" height="560" fill="{INK}"/>' + pixel(24, 64, 12, 2, RED), x=128, y=360, w=816, h=560, alt="El logo hecho con bloques cuadrados, como un cartel de luces")
ht = SVG(f'<rect width="816" height="560" fill="{INK}"/>' + halftone(23, 60, 11, CREAM), x=976, y=360, w=816, h=560, alt="El logo hecho con puntos de distinto tamaño, como una fotocopia")
S["pixel-punto"] = sec("pixel-punto", INK, CREAM, [
    pv, ht, *head("04 — Formas", "Pixel y punto", CREAM, sub="Cartel de feria y fotocopia vieja: el mismo logo hecho de bloques o de puntos.", subcol="#BFB3AC"),
    lab("Pixel", 128, 940, 400, RED), lab("Medio tono", 976, 940, 600, RED)])

# ---------- 12 el anillo como idea ----------
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>'
cxs = [128 + 277, 128 + 277 + 555, 128 + 277 + 1110]; cy = 660; s = 2.2
# órbita
cx = cxs[0]; body += L(cx, cy, s)
for k, t in enumerate([0.55, 0.45, 0.35, 0.25]):
    ang = t*math.pi; x0 = RX*math.cos(ang)*s; y0 = RY*math.sin(ang)*s
    xr = x0*math.cos(ROT) - y0*math.sin(ROT); yr = x0*math.sin(ROT) + y0*math.cos(ROT)
    body += f'<circle cx="{f(cx+xr)}" cy="{f(cy+yr)}" r="{14 if k==0 else 9-k*2}" fill="{RED}" opacity="{1 if k==0 else 0.5-k*0.1}"/>'
# átomo
cx = cxs[1]
for r in (-4, 56, -64):
    body += f'<ellipse cx="{cx}" cy="{cy}" rx="{f(RX*s)}" ry="{f(RY*s*0.62)}" transform="rotate({r} {cx} {cy})" fill="none" stroke="{RED}" stroke-width="4"/>'
body += L(cx, cy, s*0.62, RED, None)
# sello
cx = cxs[2]
body += L(cx, cy, s*0.86) + f'<ellipse cx="{cx}" cy="{cy}" rx="{f(RX*s*1.12)}" ry="{f(RY*s*1.22)}" transform="rotate(-3.96 {cx} {cy})" fill="none" stroke="{RED}" stroke-width="2"/>'
for k in range(64):
    u = k/64*math.pi*2; c, sn = math.cos(u), math.sin(u)
    a1 = (RX*s*1.18*c, RY*s*1.3*sn); a2 = (RX*s*1.27*c, RY*s*1.45*sn)
    def rt(p): return (cx + p[0]*math.cos(ROT) - p[1]*math.sin(ROT), cy + p[0]*math.sin(ROT) + p[1]*math.cos(ROT))
    p1, p2 = rt(a1), rt(a2)
    body += f'<line x1="{f(p1[0])}" y1="{f(p1[1])}" x2="{f(p2[0])}" y2="{f(p2[1])}" stroke="{RED}" stroke-width="3"/>'
S["anillo-idea"] = sec("anillo-idea", CREAM, INK, [
    SVG(body, alt="Tres ideas con el anillo: una órbita con un punto, un átomo de tres anillos y un sello con rayitas"),
    *head("04 — Formas", "El anillo como idea", INK, sub="Un óvalo puede ser órbita, átomo o sello. Cada uno cuenta algo distinto del estudio."),
    *[lab(n, cxs[i] - 250, 930, 500, RED, align="center") for i, n in enumerate(["Órbita", "Átomo", "Sello"])]])

# ---------- 13 patrón ----------
body = f'<rect width="1920" height="1080" fill="{RED}"/>'
for j in range(10):
    for i in range(12):
        x = i*180 + (90 if j % 2 else 0) - 40; y = j*118 + 20
        body += L(x, y, 0.78, CREAM, CREAM, pre=f"rotate({-8 if (i+j) % 2 else 6})")
S["patron"] = sec("patron", RED, CREAM, [
    SVG(body, alt="El logo repetido como patrón de papel de envolver, crema sobre rojo"),
    f'<div style="position:absolute;left:128px;top:128px;width:860px;background:{INK};padding:48px;display:flex;flex-direction:column;gap:16px">'
    f'<p style="font-size:24px;letter-spacing:5px;text-transform:uppercase;color:{RED}">04 — Formas</p>'
    f'<h2 style="font-family:\'Pana Black\', Impact, sans-serif;font-size:120px;font-weight:400;line-height:0.9;text-transform:uppercase;color:{CREAM}">Patrón</h2>'
    f'<p style="font-family:\'Pana Italic\', Georgia, serif;font-size:40px;line-height:1.2;color:#BFB3AC">Papel de envolver, fondo de stories, forro de caja, cinta.</p></div>'])

# ---------- 14 stickers ----------
def diecut(inner, cx, cy, s, rot, pad=9, shape="logo", bodycol=WHITE):
    t = f'translate({f(cx)} {f(cy)}) rotate({rot}) scale({f(s)}) translate(-{C0} -{C0})'
    if shape == "logo":
        cut = f'<use href="#w" fill="{WHITE}" stroke="{WHITE}" stroke-width="{pad*2}" stroke-linejoin="round"/><use href="#o" fill="{bodycol}" stroke="{WHITE}" stroke-width="{pad*2}"/>'
    elif shape == "word":
        cut = f'<use href="#w" fill="{WHITE}" stroke="{WHITE}" stroke-width="{pad*2}" stroke-linejoin="round"/>'
    return f'<g filter="url(#sh)"><g transform="{t}">{cut}</g></g><g transform="{t}">{inner}</g>'
body = f'<rect width="1920" height="1080" fill="#D6CEC2"/>'
LU = lambda word=RED, oval=RED, sw=3: (f'<use href="#o" fill="none" stroke="{oval}" stroke-width="{sw}"/>' if oval else "") + (f'<use href="#w" fill="{word}"/>' if word else "")
body += diecut(LU(), 400, 480, 1.75, -6, bodycol=INK)                                    # 1 original
body += f'<g filter="url(#sh)"><circle cx="960" cy="470" r="168" fill="{WHITE}"/></g><circle cx="960" cy="470" r="154" fill="{RED}"/>' + mobius(960, 470, 1.05, 0.7, twist=1.1, M=110, col=CREAM, Wu=30, ew=2.4, rw=1)
body += diecut(LU(CREAM, CREAM), 1530, 480, 1.7, 5, bodycol=BLUE)                          # 3 vibra azul
body += f'<g filter="url(#sh)"><rect x="232" y="700" width="340" height="215" rx="22" fill="{WHITE}" transform="rotate(4 402 807)"/></g>'
body += f'<g transform="rotate(4 402 807)"><rect x="244" y="712" width="316" height="191" rx="14" fill="{INK}"/>{pixel(262, 728, 4.45, 0.7, RED)}</g>'  # 4 pixel
# 5 eco die-cut
ecog = "".join(f'<use href="#o" transform="translate({k*3.2} {k*2.6})" fill="{WHITE}" stroke="{WHITE}" stroke-width="20"/>' for k in range(0, 8))
t5 = f'translate(930 800) rotate(-4) scale(1.45) translate(-{C0} -{C0})'
body += f'<g filter="url(#sh)"><g transform="{t5}">{ecog}</g></g>' + f'<g transform="translate(930 800) rotate(-4)">' + eco(0, 0, 1.45, 4.6, 3.8, 7, RED, WHITE) + '</g>'
body += diecut(LU(RED, None), 1530, 810, 1.9, 7, shape="word")                             # 6 palabra sola
S["stickers"] = sec("stickers", "#D6CEC2", INK, [
    SVG(body, alt="Una plancha de seis stickers troquelados con distintas versiones del logo", extra_defs=SHADOW),
    *head("05 — Para usar", "Stickers", INK)], "Plancha de 6: original, Möbius, azul vibra, pixel, eco troquelado y la palabra sola.", tr="push")

# ---------- 15 remera frente / espalda ----------
TEE = "M150 40L232 18Q300 64 368 18L450 40L592 128L532 244L470 210L470 622L130 622L130 210L68 244L8 128Z"
def tee(ox, oy, sc, col, inner, collar="#00000033"):
    return (f'<g transform="translate({ox} {oy}) scale({sc})"><g filter="url(#sh)"><path d="{TEE}" fill="{col}"/></g>'
            f'<path d="M232 18Q300 64 368 18" fill="none" stroke="{collar}" stroke-width="10"/>{inner}</g>')
body = f'<rect width="1920" height="1080" fill="#E6DFD4"/>'
body += tee(250, 360, 1.0, "#141010", L(390, 190, 0.5), collar="#2A2222")
body += tee(1070, 360, 1.0, "#141010", eco(300, 330, 1.45, 4, 6, 9, RED, "#141010", px=1.1), collar="#2A2222")
S["remera"] = sec("remera", "#E6DFD4", INK, [
    SVG(body, alt="Remera negra: adelante el logo chiquito en el pecho, atrás el eco grande", extra_defs=SHADOW),
    *head("05 — Para usar", "Remera", INK, sub="Chiquito adelante, el eco grande atrás."),
    lab("Frente", 250, 1000, 600, RED, align="center"), lab("Espalda", 1070, 1000, 600, RED, align="center")])

# ---------- 16 más remeras ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
sc = 0.84; ws = 600*sc
xs = [128 + (554 - ws)/2 + i*555 for i in range(3)]; ty = 340
body += tee(xs[0], ty, sc, CREAM, mobius(300, 310, 1.55, 0.62, twist=1.1, M=120, Wu=30, ew=2.6, rw=1) + L(300, 310, 1.2, RED, None))
body += tee(xs[1], ty, sc, RED, pixel(108, 210, 5.8, 1, INK))
body += tee(xs[2], ty, sc, "#FBFAF7",
            f'<g style="mix-blend-mode:multiply">{L(294, 296, 1.35, "#1F6BFF", "#1F6BFF")}</g><g style="mix-blend-mode:multiply">{L(306, 304, 1.35, "#FF3D6E", "#FF3D6E")}</g>')
S["remeras"] = sec("remeras", INK, CREAM, [
    SVG(body, alt="Tres remeras: crema con el Möbius, roja con el logo en pixel y blanca con el logo en riso", extra_defs=SHADOW),
    *head("05 — Para usar", "Más remeras", CREAM),
    *[lab(n, xs[i] - 20, 880, ws + 40, RED, align="center") for i, n in enumerate(["Möbius en crema", "Pixel en rojo", "Riso en blanco"])]])

# ---------- 17 otras cosas ----------
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>'
# cinta de embalar
tape = f'<path d="M0 0H880l-12 15 12 15-12 15 12 15-12 15 12 15-12 15 12 15V120H0l12-15-12-15 12-15-12-15 12-15-12-15 12-15z" fill="{RED}"/>'
tape += "".join(L(70 + i*150, 60, 0.52, CREAM, CREAM, pre=("" if i % 2 else "")) for i in range(6))
body += f'<g transform="translate(150 470) rotate(-7)"><g filter="url(#sh)">{tape}</g></g>'
# tarjetas
body += f'<g filter="url(#sh)"><rect x="180" y="720" width="350" height="200" rx="6" fill="{INK}" transform="rotate(-5 355 820)"/></g>' + f'<g transform="rotate(-5 355 820)">{L(355, 820, 1.25)}</g>'
body += (f'<g filter="url(#sh)"><rect x="470" y="740" width="350" height="200" rx="6" fill="{RED}" transform="rotate(6 645 840)"/></g>'
         f'<g transform="rotate(6 645 840)">{mobius(560, 840, 0.45, 0.7, twist=1.1, M=60, col=CREAM, Wu=30, ew=1.8, rw=1)}'
         f'<rect x="640" y="815" width="140" height="6" fill="{CREAM}"/><rect x="640" y="835" width="100" height="6" fill="{CREAM}" opacity=".6"/><rect x="640" y="855" width="120" height="6" fill="{CREAM}" opacity=".6"/></g>')
# tote
body += (f'<path d="M1150 470 Q1150 330 1260 330 Q1370 330 1370 470" fill="none" stroke="#C9B48C" stroke-width="16"/>'
         f'<g filter="url(#sh)"><path d="M1080 460H1440L1460 960H1060Z" fill="#E2D2AE"/></g>' + eco(1262, 700, 1.35, 3.5, 4, 7, RED, "#E2D2AE", px=1.1))
# pin
body += (f'<g filter="url(#sh)"><g transform="translate(1660 560) scale(1.1) translate(-{C0} -{C0})"><use href="#o" fill="{GOLD}" stroke="{GOLD}" stroke-width="14"/></g></g>'
         f'<g transform="translate(1660 560) scale(1.1) translate(-{C0} -{C0})"><use href="#o" fill="{RED}" stroke="#E8CF8A" stroke-width="3"/><use href="#w" fill="#F3DF9E" stroke="{GOLD}" stroke-width="1.2"/></g>'
         f'<circle cx="1640" cy="560" r="0" fill="none"/>')
S["objetos"] = sec("objetos", CREAM, INK, [
    SVG(body, alt="Otras aplicaciones: cinta de embalar roja, tarjetas, una bolsa de tela con el eco y un pin dorado", extra_defs=SHADOW),
    *head("05 — Para usar", "Otras cosas", INK),
    lab("Cinta de embalar", 150, 330, 500, RED), lab("Tarjetas", 180, 990, 500, RED),
    lab("Bolsa", 1060, 990, 400, RED, align="center"), lab("Pin esmaltado", 1520, 720, 280, RED, align="center")])

# ---------- 18 cierre ----------
cards = [("Para Bruno", "Elegir 3 o 4 favoritas y que las dibuje en limpio. El Möbius quieto y el eco son las que más dan."),
         ("Para imprimir", "Una plancha de prueba con los 6 stickers y una remera muestra antes de hacer tanda."),
         ("Para el feed", "El patrón y la secuencia del Möbius sirven directo como fondos y transiciones.")]
S["cierre"] = sec("cierre", RED, INK, [
    f'<p style="font-size:24px;letter-spacing:5px;text-transform:uppercase;color:{INK}">08 — Para seguir</p>',
    f'<h2 style="font-family:\'Pana Black\', Impact, sans-serif;font-size:160px;font-weight:400;line-height:0.88;text-transform:uppercase;color:{INK}">¿Con cuáles<br>seguimos?</h2>',
    '<div style="flex:1"></div>',
    '<div style="display:flex;gap:48px">' + "".join(
        f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;border-top:3px solid {INK};padding:24px 0 0 0">'
        f'<h3 style="font-family:\'Pana Black\', Impact, sans-serif;font-size:56px;font-weight:400;text-transform:uppercase;color:{INK}">{h}</h3>'
        f'<p style="font-size:32px;line-height:1.3;color:{INK}">{t}</p></div>' for h, t in cards) + '</div>'])

order = ["portada", "anatomia", "color-grilla", "color-loco", "mobius-secuencia", "mobius-marca", "moire", "eco", "eco-variantes",
         "elastico", "pixel-punto", "anillo-idea", "patron", "stickers", "remera", "remeras", "objetos", "cierre"]
for k, v in S.items():
    open(os.path.join(ROOT, "project/slides", k + ".html"), "w").write(v)
    print(k, len(v))
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-03T05:00:00Z"}, "lists": "css", "title": "Pana — variaciones del logo",
        "order": order, "cover": "portada",
        "sections": {"s0": {"description": "De dónde partimos: el logo de Bruno, un anillo y una palabra.", "start": "portada"},
                     "s1": {"description": "Color: las pieles clásicas y las locas.", "start": "color-grilla"},
                     "s2": {"description": "Möbius: el anillo que se da vuelta, como secuencia y como isotipo.", "start": "mobius-secuencia"},
                     "s3": {"description": "Eco: el relieve de VICIO y sus variantes.", "start": "eco"},
                     "s4": {"description": "Formas y conceptos: elástico, pixel, el anillo como idea, patrón.", "start": "elastico"},
                     "s5": {"description": "Para usar: stickers, remeras y otras cosas.", "start": "stickers"},
                     "s6": {"description": "Cómo seguir.", "start": "cierre"}},
        "faces": {"pana-black": {"family": "Pana Black", "src": "/_blob/20558b040e2a6722963b50f3b1c0b3c7"},
                  "pana-italic": {"family": "Pana Italic", "src": "/_blob/b3e430177c28b083fa0eb4cf3c02ec5a"},
                  "pana-regular": {"family": "Pana Regular", "src": "/_blob/66052036993cd491786f95f354490f74"}},
        "designSystems": []}
json.dump(deck, open(os.path.join(ROOT, "project/deck.json"), "w"), ensure_ascii=False, indent=1)

# preview local para mirar la maqueta
FD = "/Users/marcosperilli/Desktop/Pana web - pruebas/fonts/"
pv = ('<html><head><meta charset="utf-8"><style>'
      f'@font-face{{font-family:"Pana Black";src:url("file://{FD}PPRightGrotesk-CompactBlack.woff2")}}'
      f'@font-face{{font-family:"Pana Italic";src:url("file://{FD}PPEditorialNew-UltralightItalic.woff2")}}'
      f'@font-face{{font-family:"Pana Regular";src:url("file://{FD}PPRightGrotesk-CompactRegular.woff2")}}'
      'body{margin:0} section{position:relative;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden} p,h2,h3{margin:0} aside{display:none}</style></head><body>'
      + "".join(S[k] for k in order) + '</body></html>')
open(os.path.join(SP, "preview.html"), "w").write(pv)
