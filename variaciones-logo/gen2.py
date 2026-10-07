# Segunda tanda: negro + rojo, neón y stickers troquelados. Corre gen.py primero y agrega placas.
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen.py")).read())

UNION = json.load(open(os.path.join(SP, "word_union.json")))   # un contorno limpio por letra
OG = open(os.path.join(SP, "ovalcut.txt")).read()   # el anillo cortado donde toca las letras

def DEFS(extra="", body=""):
    use = body + extra
    return ('<defs><g id="w">' + "".join(f'<path id="w{i}" d="{d}"/>' for i, d in enumerate(WORD)) + '</g>'
            + (f'<path id="og" d="{OG}"/>' if "#og" in use else "")
            + "".join(f'<path id="u{i}" d="{d}"/>' for i, d in enumerate(UNION) if f"#u{i}" in use)
            + f'<ellipse id="o" cx="{C0}" cy="{C0}" rx="{RX}" ry="{RY}" transform="rotate(-3.96 {C0} {C0})"/>' + extra + '</defs>')

def SVG(body, x=0, y=0, w=1920, h=1080, alt="", extra_defs=""):
    return (f'<svg aria-label="{alt}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px">' + DEFS(extra_defs, body) + body + '</svg>')

def T(cx, cy, s, pre="", sx=1, sy=1):
    sc = f"scale({f(s*sx)} {f(s*sy)})" if (sx != 1 or sy != 1) else f"scale({f(s)})"
    return f'translate({f(cx)} {f(cy)}) {pre} {sc} translate(-{C0} -{C0})'

# ---------- neón ----------
def neon_defs(p, s, gap=48):
    return (f'<mask id="{p}gap" maskUnits="userSpaceOnUse" x="-50" y="-50" width="362" height="362">'
            f'<rect x="-50" y="-50" width="362" height="362" fill="#fff"/>'
            + "".join(f'<use href="#c{i}" fill="none" stroke="#000" stroke-width="{f(gap/s)}" stroke-linecap="round"/>' for i in range(4)) + '</mask>' +
            f'<filter id="{p}b1" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="16"/></filter>'
            f'<filter id="{p}b2" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>'
            f'<radialGradient id="{p}wall"><stop offset="0" stop-color="{RED}" stop-opacity=".32"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>')

def tubes(t, p, stroke, w, letters=(0, 1, 2, 3), oval=True, op=1):
    o = f'<use href="#og" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>' if oval else ""
    l = "".join(f'<use href="#u{i}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>' for i in letters)
    return f'<g transform="{t}" opacity="{op}">{o}{l}</g>'

def neon(cx, cy, s, p, lit=(0, 1, 2, 3), oval_lit=True, wall=True, k=1.0, dim=()):
    t = T(cx, cy, s)
    out = ""
    if wall and (lit or oval_lit):
        out += f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(RX*s*1.7)}" ry="{f(RY*s*2.2)}" fill="url(#{p}wall)"/>'
    U = lambda u, mn: f(max(u, mn/s))          # ancho del tubo en unidades del logo, con un mínimo en px
    out += tubes(t, p, "#2B2424", U(2.1, 3.5))            # el vidrio apagado
    out += tubes(t, p, "#463B3B", U(0.5, 1))
    ls = tuple(i for i in lit if i not in dim)
    for letters, ov, op in ((ls, oval_lit, 1), (tuple(dim), False, 0.35)):
        if not letters and not ov: continue
        out += f'<g filter="url(#{p}b1)">' + tubes(t, p, RED, U(5, 10), letters, ov, op*0.75) + '</g>'
        out += f'<g filter="url(#{p}b2)">' + tubes(t, p, "#FF2020", U(3, 5), letters, ov, op) + '</g>'
        out += tubes(t, p, "#FF4A3D", U(1.85, 3), letters, ov, op)
        out += tubes(t, p, "#FFE3DA", U(0.75, 1.2), letters, ov, op)
    return out

# ---------- troquelado genérico ----------
def cut(t, shapes, pad):
    """borde blanco: las formas engordadas en blanco, con sombra"""
    return f'<g filter="url(#sh)"><g transform="{t}">' + shapes.replace("STROKE", f'stroke="{WHITE}" stroke-width="{f(pad*2)}" stroke-linejoin="round"') + '</g></g>'
CUT_LOGO = '<use href="#w" fill="#FBF8F2" STROKE/><use href="#o" fill="#FBF8F2" STROKE/>'
CUT_WORD = '<use href="#w" fill="#FBF8F2" STROKE/>'
CUT_RING = '<use href="#o" fill="none" STROKE/>'

def st_word(cx, cy, s, rot, col, pre="", sx=1, sy=1, outline=None):
    t = T(cx, cy, s, pre=f"rotate({rot}) {pre}", sx=sx, sy=sy)
    inner = f'<use href="#w" fill="{col}"' + (f' stroke="{outline}" stroke-width="1.6" vector-effect="non-scaling-stroke"' if outline else "") + '/>'
    return cut(t, CUT_WORD, 8/s*1.6) + f'<g transform="{t}">{inner}</g>'

def st_logo(cx, cy, s, rot, body, ring, word, sw=3):
    t = T(cx, cy, s, pre=f"rotate({rot})")
    inner = f'<use href="#o" fill="{body}" stroke="{ring}" stroke-width="{sw}"/><use href="#w" fill="{word}"/>'
    return cut(t, CUT_LOGO, 8/s*1.6) + f'<g transform="{t}">{inner}</g>'

def st_ring(cx, cy, s, rot, col):
    t = T(cx, cy, s, pre=f"rotate({rot})")
    return (f'<g filter="url(#sh)"><g transform="{t}"><use href="#o" fill="none" stroke="{WHITE}" stroke-width="{f(9+2*8/s*1.6)}"/></g></g>'
            f'<g transform="{t}"><use href="#o" fill="none" stroke="{col}" stroke-width="9"/></g>')

def pix_path(ox, oy, cell, gap, thr=0.42):
    d = []
    for j, r in enumerate(GR["pix"]):
        for i, v in enumerate(r):
            if v > thr: d.append(f"M{f(ox+i*cell)} {f(oy+j*cell)}h{f(cell-gap)}v{f(cell-gap)}h-{f(cell-gap)}z")
    return "".join(d)

PIXDEFS = None
def pix_runs(ox, oy, thr=0.42):
    d = []
    for j, r in enumerate(GR["pix"]):
        i = 0
        while i < len(r):
            if r[i] > thr:
                k = i
                while k < len(r) and r[k] > thr: k += 1
                d.append(f"M{ox+i} {oy+j}h{k-i}v1h-{k-i}z"); i = k
            else: i += 1
    return "".join(d)

def pixdefs():
    return (f'<path id="pf" d="{pix_runs(-32, -18)}"/>'
            f'<pattern id="pp" width="1" height="1" patternUnits="userSpaceOnUse"><rect width=".84" height=".84" fill="{RED}"/></pattern>')

def st_pixel(cx, cy, cell, rot, col, body=None):
    t = f"translate({cx} {cy}) rotate({rot}) scale({cell})"
    under = f'<use href="#pf" fill="{body}" stroke="{body}" stroke-width="1.6" stroke-linejoin="round"/>' if body else ""
    return (f'<g filter="url(#sh)"><g transform="{t}"><use href="#pf" fill="{WHITE}" stroke="{WHITE}" stroke-width="{4.6 if body else 3}" stroke-linejoin="round"/></g></g>'
            f'<g transform="{t}">{under}<use href="#pf" fill="url(#pp)"/></g>')

def st_eco(cx, cy, s, rot, body, col):
    t0 = f"translate({cx} {cy}) rotate({rot})"
    dx, dy, n = 3.6, 3.0, 7
    shapes = "".join(f'<use href="#o" transform="translate({f(k*dx/s)} {f(k*dy/s)})" fill="{WHITE}" stroke="{WHITE}" stroke-width="{f(22/s+3)}"/>' for k in range(n + 1))
    bodyl = "".join(f'<use href="#o" transform="translate({f(k*dx/s)} {f(k*dy/s)})" fill="{body}" stroke="{body}" stroke-width="{f(6/s+3)}"/>' for k in range(n + 1))
    return (f'<g filter="url(#sh)"><g transform="{t0} scale({f(s)}) translate(-{C0} -{C0})">{shapes}</g></g>'
            f'<g transform="{t0} scale({f(s)}) translate(-{C0} -{C0})">{bodyl}</g>'
            f'<g transform="{t0}">' + eco(0, 0, s, dx, dy, n, col, body, px=1.2) + '</g>')

NEW = {}

# ---------- neón: héroe ----------
p = "n1"; s = 5.6
body = f'<rect width="1920" height="1080" fill="#080606"/>' + neon(960, 600, s, p)
NEW["neon"] = sec("neon", "#080606", CREAM, [
    SVG(body, alt="El logo de pana como cartel de neón rojo prendido sobre una pared negra", extra_defs=neon_defs(p, s)),
    lab("06 — Negro y rojo", 128, 88, 800, RED), lab("Neón", 1092, 88, 700, CREAM, align="right"),
    f'<p style="position:absolute;left:128px;top:950px;width:1664px;font-family:\'Pana Italic\', Georgia, serif;font-size:40px;color:#BFB3AC">Las letras son las del logo, en tubo. El anillo se corta donde toca la palabra: nada se encima.</p>',
], "El contorno de cada letra es un tubo, igual al logo. El anillo se interrumpe en cada lugar donde toca la palabra, así ninguna línea pasa por encima de otra.", tr="fade")

# ---------- neón: estados ----------
s = 2.0; xs3 = [128 + 266, 128 + 266 + 566, 128 + 266 + 1132]; cy = 620
body = f'<rect width="1920" height="1080" fill="#080606"/>'
dfs = ""
for i, (lit, ov, dim) in enumerate([((0, 1, 2, 3), True, ()), ((), False, ()), ((0, 1, 3), True, (2,))]):
    p = f"e{i}"; dfs += neon_defs(p, s, gap=20)
    body += neon(xs3[i], cy, s, p, lit=lit, oval_lit=ov, dim=dim, k=0.6)
NEW["neon-estados"] = sec("neon-estados", "#080606", CREAM, [
    SVG(body, alt="Tres neones: prendido, apagado y con la letra n titilando", extra_defs=dfs),
    *head("06 — Negro y rojo", "Prendido, apagado, titila", CREAM, sub="El apagado también es lindo: el vidrio solo, como de día.", subcol="#BFB3AC"),
    *[lab(n, xs3[i] - 250, 900, 500, RED, align="center") for i, n in enumerate(["Prendido", "Apagado", "La n titila"])]])

# ---------- neón: usos ----------
p1, p2, p3 = "u1", "u2", "u3"
body = f'<rect width="1920" height="1080" fill="#080606"/>'
# remera
body += f'<g transform="translate(140 330) scale(1.0)"><path d="{TEE}" fill="#141010"/><path d="M232 18Q300 64 368 18" fill="none" stroke="#2A2222" stroke-width="10"/></g>'
body += neon(440, 600, 1.15, p1, k=0.42, wall=False)
# story
body += f'<rect x="830" y="300" width="400" height="712" rx="44" fill="#000" stroke="#3A3030" stroke-width="3"/>'
body += neon(1030, 600, 1.75, p2, k=0.5)
body += f'<rect x="980" y="318" width="100" height="14" rx="7" fill="#1A1414"/>'
# cartel cuadrado (post)
body += f'<rect x="1340" y="330" width="452" height="452" fill="#000" stroke="#3A3030" stroke-width="3"/>'
body += neon(1566, 556, 2.0, p3, lit=(0, 1, 3), dim=(2,), k=0.55)
NEW["neon-usos"] = sec("neon-usos", "#080606", CREAM, [
    SVG(body, alt="El neón aplicado: estampado en una remera negra, en una historia de Instagram y en un posteo cuadrado",
        extra_defs=neon_defs(p1, 1.15, 11) + neon_defs(p2, 1.75, 16) + neon_defs(p3, 2.0, 18)),
    *head("06 — Negro y rojo", "Neón, aplicado", CREAM),
    lab("Remera (estampa con brillo)", 140, 970, 600, RED, align="center"), lab("Historia", 830, 1030, 400, RED, align="center"),
    lab("Posteo", 1340, 800, 452, RED, align="center")])

# ---------- negro y rojo: seis tratamientos ----------
GW, GH = 533, 290; gx = [128 + i*(GW + 32) for i in range(3)]; gy = [300, 650]
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
extra = (f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>')
cells = []
for r in range(2):
    for c in range(3):
        cells.append((gx[c], gy[r]))
s = 1.35
for i, (x, y) in enumerate(cells):
    cx, cy = x + GW/2, y + GH/2
    body += f'<rect x="{x}" y="{y}" width="{GW}" height="{GH}" fill="#0F0C0C" stroke="#2A2222"/>'
    if i == 0:   # persiana
        stripes = "".join(f'<rect x="{x}" y="{f(y + 60 + j*9)}" width="{GW}" height="{f(0.4 + j*0.24)}" fill="#000"/>' for j in range(19))
        extra += f'<mask id="pers" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{GW}" height="{GH}"><rect x="{x}" y="{y}" width="{GW}" height="{GH}" fill="#fff"/>{stripes}</mask>'
        body += f'<g mask="url(#pers)">{L(cx, cy, s)}</g>'
    elif i == 1:  # contorno
        extra += neon_defs("cg", s, 12)
        body += (f'<g transform="{T(cx, cy, s)}"><use href="#o" fill="none" stroke="{RED}" stroke-width="5"/>'
                 + "".join(f'<use href="#u{j}" fill="none" stroke="{RED}" stroke-width="1.2"/>' for j in range(4)) + '</g>')
    elif i == 2:  # negativo
        body += f'<g transform="{T(cx, cy, s)}"><use href="#o" fill="{RED}" stroke="{RED}" stroke-width="3"/><use href="#w" fill="#0F0C0C"/></g>'
    elif i == 3:  # sombra dura
        body += f'<g transform="{T(cx+10, cy+10, s)}"><use href="#o" fill="none" stroke="#6E0000" stroke-width="3"/><use href="#w" fill="#6E0000"/></g>' + L(cx, cy, s)
    elif i == 4:  # espejo
        body += L(cx, cy - 40, s*0.85)
        body += (f'<mask id="esp" maskUnits="userSpaceOnUse" x="{x}" y="{cy}" width="{GW}" height="{GH}"><rect x="{x}" y="{f(cy+5)}" width="{GW}" height="140" fill="url(#fade)"/></mask>'
                 f'<g mask="url(#esp)">{L(cx, cy + 50, s*0.85, sy=-1)}</g>')
    else:  # recorte
        extra += f'<clipPath id="rec"><rect x="{x}" y="{y}" width="{GW}" height="{GH}"/></clipPath>'
        body += f'<g clip-path="url(#rec)">{L(cx + 80, cy + 30, 4.6)}</g>'
names = ["Persiana", "Contorno", "Negativo", "Sombra dura", "Reflejo", "Recorte"]
NEW["negro-rojo"] = sec("negro-rojo", INK, CREAM, [
    SVG(body, alt="Seis tratamientos del logo en rojo sobre negro: persiana, contorno, negativo, sombra dura, reflejo y recorte", extra_defs=extra),
    *head("06 — Negro y rojo", "Seis maneras de rojo", CREAM),
    *[lab(n, cells[i][0], cells[i][1] + GH + 12, GW, RED) for i, n in enumerate(names)]])

# ---------- afiche ----------
extra = '<clipPath id="af"><rect width="1920" height="1080"/></clipPath>'
body = f'<rect width="1920" height="1080" fill="{INK}"/><g clip-path="url(#af)">{L(1010, 610, 12.5)}</g>'
NEW["afiche"] = sec("afiche", INK, CREAM, [
    SVG(body, alt="El logo gigante, cortado por los bordes, como un afiche", extra_defs=extra),
    lab("Pana estudio creativo", 128, 88, 800, CREAM), lab("06 — Afiche", 1092, 88, 700, CREAM, align="right"),
    lab("Estudio creativo — 2026", 128, 970, 1000, CREAM)])

# ---------- stickers rojos ----------
SX = [400, 960, 1520]; SY = [480, 810]
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
body += st_word(SX[0], SY[0], 1.85, -6, RED)
body += st_logo(SX[1], SY[0], 1.75, 4, RED, INK, INK)
body += st_ring(SX[2], SY[0], 1.65, -8, RED)
body += st_pixel(SX[0], SY[1], 4.6, 5, RED, body=RED)
body += st_word(SX[1], SY[1], 1.5, -3, RED, sx=1.55, sy=0.62)
body += st_word(SX[2], SY[1], 1.7, 6, RED, pre="skewX(-24)")
NEW["stickers-rojos"] = sec("stickers-rojos", INK, CREAM, [
    SVG(body, alt="Seis stickers rojos troquelados con borde blanco sobre fondo negro", extra_defs=SHADOW + pixdefs()),
    *head("07 — Stickers", "Rojos, borde blanco", CREAM)],
    "Palabra sola, logo lleno, el anillo solo, pixel troquelado al borde de los cuadraditos, la versión cartel y la de velocidad.", tr="push")

# ---------- stickers negros ----------
pn = "sn"
body = f'<rect width="1920" height="1080" fill="#1E1919"/>'
body += st_logo(SX[0], SY[0], 1.75, -5, INK, RED, RED)
body += st_eco(SX[1], SY[0], 1.55, 3, INK, RED)
nt = T(SX[2], SY[0], 1.7, pre="rotate(-4)")
body += cut(nt, CUT_LOGO, 8/1.7*1.6) + f'<g transform="{nt}"><use href="#o" fill="#080606" stroke="#080606" stroke-width="3"/></g>'
body += f'<g transform="translate({SX[2]} {SY[0]}) rotate(-4) translate(-{SX[2]} -{SY[0]})">' + neon(SX[2], SY[0], 1.45, pn, wall=False, k=0.45) + '</g>'
body += st_word(SX[0], SY[1], 1.85, 5, INK, outline=RED)
body += st_pixel(SX[1], SY[1], 4.6, -4, RED, body=INK)
body += f'<g filter="url(#sh)"><circle cx="{SX[2]}" cy="{SY[1]}" r="152" fill="{WHITE}"/></g><circle cx="{SX[2]}" cy="{SY[1]}" r="138" fill="{INK}"/>' + mobius(SX[2], SY[1], 0.95, 0.7, twist=1.1, M=44, col=RED, Wu=30, ew=2.2, rw=1)
NEW["stickers-negros"] = sec("stickers-negros", "#1E1919", CREAM, [
    SVG(body, alt="Seis stickers negros con rojo y borde blanco: logo, eco, neón, palabra en contorno, pixel y Möbius", extra_defs=SHADOW + pixdefs() + neon_defs(pn, 1.45, 12)),
    *head("07 — Stickers", "Negros, borde blanco", CREAM)])

# ---------- notebook ----------
pl = "lp"
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
body += f'<g filter="url(#sh)"><rect x="330" y="300" width="1260" height="720" rx="34" fill="#2A2525"/></g><rect x="330" y="300" width="1260" height="720" rx="34" fill="none" stroke="#3B3434" stroke-width="2"/>'
body += st_word(620, 470, 1.25, -9, RED)
body += st_logo(1040, 520, 1.45, 5, INK, RED, RED)
body += st_ring(1380, 430, 0.95, 12, RED)
body += st_pixel(560, 800, 3.0, 8, RED, body=INK)
body += st_eco(990, 860, 1.05, -6, INK, RED)
body += st_word(1370, 760, 1.2, -4, RED, pre="skewX(-24)")
body += f'<g filter="url(#sh)"><circle cx="1440" cy="930" r="62" fill="{WHITE}"/></g><circle cx="1440" cy="930" r="54" fill="{RED}"/>' + mobius(1440, 930, 0.36, 0.7, twist=1.1, M=60, col=INK, Wu=30, ew=1.6, rw=0.8)
NEW["notebook"] = sec("notebook", INK, CREAM, [
    SVG(body, alt="La tapa de una notebook llena de stickers de pana", extra_defs=SHADOW + pixdefs()),
    *head("07 — Stickers", "Así quedan pegados", CREAM)])

new_order = ["neon", "neon-estados", "neon-usos", "negro-rojo", "afiche", "stickers-rojos", "stickers-negros", "notebook"]
for k, v in NEW.items():
    open(os.path.join(ROOT, "project/slides", k + ".html"), "w").write(v)
    print(k, len(v))
S.update(NEW)
order = order[:-1] + new_order + ["cierre"]
deck["order"] = order
deck["sections"]["s6"] = {"description": "Segunda tanda en negro y rojo: neón, seis tratamientos y un afiche.", "start": "neon"}
deck["sections"]["s7"] = {"description": "Stickers troquelados con borde blanco, rojos y negros.", "start": "stickers-rojos"}
deck["sections"]["s8"] = {"description": "Cómo seguir.", "start": "cierre"}
json.dump(deck, open(os.path.join(ROOT, "project/deck.json"), "w"), ensure_ascii=False, indent=1)
pv = pv.split("<body>")[0] + "<body>" + "".join(S[k] for k in new_order) + "</body></html>"
open(os.path.join(SP, "preview2.html"), "w").write(pv)
