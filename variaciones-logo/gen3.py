# Tercera tanda: arranca con el logo de Bruno TAL CUAL y sus aplicaciones (rojo sobre negro), después las variaciones.
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen2.py")).read())

DARK = "#141010"; WALL = "#1C1717"; MUTE = "#7C6F6A"
def bars(x, y, ws, col, h=8, gap=18, op=1):
    return "".join(f'<rect x="{f(x)}" y="{f(y + i*gap)}" width="{f(w)}" height="{h}" rx="{h/2}" fill="{col}" opacity="{op}"/>' for i, w in enumerate(ws))
def LO(cx, cy, s, **k): return L(cx, cy, s, **k)          # el logo original: anillo + palabra en rojo
SH = SHADOW
B = {}

# ---------- 01 portada: el logo tal cual ----------
B["portada"] = sec("portada", INK, CREAM, [
    SVG(f'<rect width="1920" height="1080" fill="{INK}"/>' + LO(960, 545, 5.0), alt="El logo de Pana tal cual lo diseñó Bruno: la palabra pana dentro de un anillo, rojo sobre negro"),
    lab("Pana estudio creativo", 128, 88, 900, RED), lab("Logo — Bruno", 1092, 88, 700, CREAM, align="right"),
    f'<p style="position:absolute;left:128px;top:950px;width:1664px;font-family:\'Pana Italic\', Georgia, serif;font-size:44px;color:{CREAM}">el logo, tal cual — y todo lo que se puede hacer con él</p>',
], "Primero el logo como lo planteó Bruno y sus aplicaciones directas. Después, las variaciones para seguir imaginando.")

# ---------- 02 sistema ----------
s = 3.4; cx, cy = 560, 650
hw, hh = RX*s + 70, RY*s + 70
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
body += f'<rect x="{f(cx-hw)}" y="{f(cy-hh)}" width="{f(2*hw)}" height="{f(2*hh)}" fill="none" stroke="{MUTE}" stroke-width="1.5" stroke-dasharray="8 8"/>' + LO(cx, cy, s)
body += f'<line x1="1080" y1="330" x2="1080" y2="980" stroke="#2A2222"/>'
body += L(1300, 470, 1.25, word=None) + L(1300, 690, 1.25, oval=None)
body += LO(1640, 470, 0.62) + LO(1640, 690, 0.36)
body += f'<rect x="1270" y="850" width="64" height="64" rx="14" fill="{RED}"/>' + L(1302, 882, 0.3, INK, INK, sw=6)
body += f'<rect x="1370" y="858" width="48" height="48" rx="10" fill="{DARK}" stroke="#2A2222"/>' + L(1394, 882, 0.23, RED, RED, sw=7)
body += f'<circle cx="1490" cy="882" r="34" fill="{RED}"/>' + L(1490, 882, 0.3, INK, INK, sw=6)
B["sistema"] = sec("sistema", INK, CREAM, [
    SVG(body, alt="El sistema del logo: el logo con su aire alrededor, el anillo solo, la palabra sola, versiones chicas e íconos"),
    *head("Logo original — el sistema", "Las piezas", CREAM),
    lab("Aire mínimo alrededor", 128, 980, 900, MUTE),
    lab("Anillo solo", 1150, 560, 300, RED, align="center"), lab("Palabra sola", 1150, 760, 300, RED, align="center"),
    lab("Chico", 1540, 760, 200, RED, align="center"), lab("Íconos", 1240, 940, 300, RED)])

# ---------- 03 afiches ----------
PW_, PH_ = 440, 622; pxs = [150, 740, 1330]; py = 330
extra = SH + "".join(f'<clipPath id="pa{i}"><rect x="{x}" y="{py}" width="{PW_}" height="{PH_}"/></clipPath>' for i, x in enumerate(pxs))
body = f'<rect width="1920" height="1080" fill="{WALL}"/>'
x = pxs[0]   # 1: logo chico arriba, mucho negro
body += f'<g filter="url(#sh)"><rect x="{x}" y="{py}" width="{PW_}" height="{PH_}" fill="{INK}"/></g>' + LO(x + PW_/2, py + 170, 1.5)
body += bars(x + 40, py + PH_ - 92, [180, 120, 150], CREAM, h=7, gap=18, op=.55) + bars(x + PW_ - 140, py + PH_ - 92, [100, 70], RED, h=7, gap=18)
x = pxs[1]   # 2: rojo, logo negro gigante girado
body += f'<g filter="url(#sh)"><rect x="{x}" y="{py}" width="{PW_}" height="{PH_}" fill="{RED}"/></g>'
body += f'<g clip-path="url(#pa1)">{L(x + PW_/2 + 10, py + PH_/2, 4.6, INK, INK, pre="rotate(-90)")}</g>'
x = pxs[2]   # 3: columna de logos
body += f'<g filter="url(#sh)"><rect x="{x}" y="{py}" width="{PW_}" height="{PH_}" fill="{INK}"/></g>'
body += f'<g clip-path="url(#pa2)">' + "".join(LO(x + PW_/2, py + 40 + j*108, 1.05) for j in range(6)) + '</g>'
B["afiches"] = sec("afiches", WALL, CREAM, [
    SVG(body, alt="Tres afiches con el logo: negro con el logo chico arriba, rojo con el logo negro gigante girado y negro con el logo repetido en columna", extra_defs=extra),
    *head("Logo original — aplicaciones", "Afiches", CREAM),
    *[lab(n, pxs[i], py + PH_ + 16, PW_, RED) for i, n in enumerate(["Silencio", "Grito", "Repetición"])]],
    "Tres tonos de afiche con el mismo logo: uno callado, uno que grita y uno que se repite como empapelado de calle.", tr="push")

# ---------- 04 papelería ----------
body = f'<rect width="1920" height="1080" fill="{WALL}"/>'
# hoja A4
body += f'<g filter="url(#sh)"><rect x="150" y="320" width="460" height="650" fill="{CREAM}" transform="rotate(-3 380 645)"/></g>'
body += f'<g transform="rotate(-3 380 645)">{LO(240, 380, 0.55)}' + bars(200, 470, [300, 330, 280, 320, 250, 300, 180], "#3A3030", h=6, gap=22, op=.35) + bars(200, 900, [140, 90], RED, h=6, gap=18) + '</g>'
# tarjetas
body += f'<g filter="url(#sh)"><rect x="700" y="360" width="420" height="240" rx="8" fill="{INK}" transform="rotate(4 910 480)"/></g><g transform="rotate(4 910 480)">{LO(910, 480, 1.4)}</g>'
body += f'<g filter="url(#sh)"><rect x="760" y="640" width="420" height="240" rx="8" fill="{RED}" transform="rotate(-5 970 760)"/></g>'
body += f'<g transform="rotate(-5 970 760)">{L(850, 710, 0.5, INK, INK)}' + bars(800, 780, [200, 150, 170], INK, h=8, gap=22, op=.8) + '</g>'
# sobre
body += f'<g filter="url(#sh)"><rect x="1250" y="350" width="520" height="280" rx="4" fill="{INK}"/></g><path d="M1250 350L1510 500L1770 350" fill="none" stroke="#2A2222" stroke-width="2"/>'
body += LO(1320, 590, 0.42) + bars(1560, 560, [160, 120], CREAM, h=6, gap=16, op=.5)
# sello en papel
body += f'<g filter="url(#sh)"><rect x="1300" y="690" width="420" height="300" fill="{CREAM}" transform="rotate(3 1510 840)"/></g>'
body += f'<g transform="rotate(3 1510 840)" opacity=".82">' + L(1510, 840, 1.45, RED, RED, sw=4) + f'<ellipse cx="1510" cy="840" rx="{f(RX*1.45*1.18)}" ry="{f(RY*1.45*1.32)}" transform="rotate(-3.96 1510 840)" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="3 7"/></g>'
B["papeleria"] = sec("papeleria", WALL, CREAM, [
    SVG(body, alt="Papelería: hoja membretada, tarjetas negra y roja, sobre negro y el logo como sello de goma sobre papel", extra_defs=SH),
    *head("Logo original — aplicaciones", "Papelería", CREAM),
    lab("Hoja", 150, 990, 300, RED), lab("Tarjetas", 700, 920, 400, RED), lab("Sobre", 1250, 300, 300, RED, align="left"), lab("Sello de goma", 1300, 1010, 420, RED)])

# ---------- 05 stickers del original ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
body += st_logo(420, 500, 2.1, -7, INK, RED, RED)
body += st_logo(980, 470, 1.35, 6, INK, RED, RED)
body += st_word(1500, 470, 1.8, -4, RED)
body += st_ring(1300, 640, 0.95, 18, RED)
body += st_logo(330, 830, 1.15, 9, RED, INK, INK)
body += st_logo(760, 820, 0.85, -12, INK, RED, RED)
body += st_word(1090, 840, 1.25, 5, INK, outline=None)
body += st_logo(1560, 820, 1.55, -3, INK, RED, RED)
B["stickers-original"] = sec("stickers-original", INK, CREAM, [
    SVG(body, alt="Stickers troquelados del logo original en varios tamaños, rojo y negro con borde blanco", extra_defs=SH),
    *head("Logo original — aplicaciones", "Stickers del original", CREAM)])

# ---------- 06 redes ----------
body = f'<rect width="1920" height="1080" fill="{WALL}"/>'
ph_x, ph_y = 150, 300
body += f'<g filter="url(#sh)"><rect x="{ph_x}" y="{ph_y}" width="420" height="740" rx="46" fill="#000" stroke="#3A3030" stroke-width="3"/></g>'
body += f'<circle cx="{ph_x+80}" cy="{ph_y+100}" r="44" fill="{INK}" stroke="{RED}" stroke-width="3"/>' + LO(ph_x + 80, ph_y + 100, 0.4)
body += bars(ph_x + 150, ph_y + 78, [150, 200, 120], CREAM, h=8, gap=20, op=.45)
for i in range(4):
    hx = ph_x + 60 + i*96
    body += f'<circle cx="{hx}" cy="{ph_y+200}" r="30" fill="{INK}" stroke="#3A3030" stroke-width="2"/>' + (L(hx, ph_y + 200, 0.27) if i != 2 else L(hx, ph_y + 200, 0.27, word=None, sw=6))
tile = 128; gx0, gy0 = ph_x + 18, ph_y + 262
kinds = ["logo", "rojo", "anillo", "palabra", "logo", "rojo", "rojo", "chico", "logo", "anillo", "logo", "rojo"]
for j in range(3):
    for i in range(3):
        k = kinds[j*3 + i]; x = gx0 + i*(tile + 2); y = gy0 + j*(tile + 2)
        bg = RED if k == "rojo" else INK
        body += f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" fill="{bg}"/>'
        c = (x + tile/2, y + tile/2)
        if k == "logo": body += LO(*c, 0.6)
        elif k == "rojo": body += L(*c, 0.6, INK, INK)
        elif k == "anillo": body += L(*c, 0.62, word=None)
        elif k == "palabra": body += L(*c, 0.62, oval=None)
        else: body += LO(c[0] - 30, c[1] - 34, 0.22)
body += f'<rect x="{ph_x}" y="{ph_y + 262 + 4*130 - 40}" width="420" height="0"/>'
# tres posteos grandes
P = [(700, RED), (1060, INK), (1420, INK)]
for i, (x, bg) in enumerate(P):
    y = 330
    body += f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="340" height="340" fill="{bg}"/></g>'
    if i == 0: body += L(x + 170, y + 170, 1.4, INK, INK)
    elif i == 1: body += LO(x + 64, y + 50, 0.32) + bars(x + 30, y + 220, [250, 200, 160], CREAM, h=14, gap=30, op=.8)
    else: body += LO(x + 170, y + 170, 1.4)
# historia
body += f'<g filter="url(#sh)"><rect x="1060" y="700" width="200" height="340" rx="16" fill="{INK}"/></g>' + LO(1160, 870, 0.75) + bars(1100, 990, [120], CREAM, h=8, op=.5)
body += f'<g filter="url(#sh)"><rect x="1300" y="700" width="200" height="340" rx="16" fill="{RED}"/></g>' + L(1400, 780, 0.5, INK, INK) + bars(1330, 900, [140, 110, 130], INK, h=10, gap=24, op=.85)
B["redes"] = sec("redes", WALL, CREAM, [
    SVG(body, alt="El logo en Instagram: perfil con foto de perfil, destacadas y grilla; posteos cuadrados e historias", extra_defs=SH),
    *head("Logo original — aplicaciones", "Redes", CREAM),
    lab("Perfil y grilla", 150, 260, 420, RED), lab("Posteos", 700, 690, 400, RED), lab("Historias", 1540, 860, 250, RED)])

# ---------- 07 ropa y objetos ----------
body = f'<rect width="1920" height="1080" fill="#E6DFD4"/>'
body += tee(110, 350, 0.75, "#141010", LO(390, 190, 0.5), collar="#2A2222")
# gorra
gx, gy = 740, 600
body += (f'<g filter="url(#sh)"><path d="M{gx-170} {gy} C{gx-170} {gy-190} {gx+170} {gy-190} {gx+170} {gy} Z" fill="#141010"/>'
         f'<path d="M{gx+110} {gy-8} C{gx+180} {gy-12} {gx+240} {gy+4} {gx+262} {gy+30} C{gx+210} {gy+38} {gx+170} {gy+30} {gx+100} {gy+18}Z" fill="#0E0B0B"/></g>'
         f'<path d="M{gx} {gy-140} L{gx} {gy}" stroke="#2A2222" stroke-width="2"/><circle cx="{gx}" cy="{gy-142}" r="8" fill="#141010"/>' + LO(gx - 70, gy - 70, 0.55))
# bolsa negra
body += (f'<path d="M1150 520 Q1150 390 1250 390 Q1350 390 1350 520" fill="none" stroke="#141010" stroke-width="14"/>'
         f'<g filter="url(#sh)"><path d="M1080 510H1420L1440 960H1060Z" fill="#141010"/></g>' + LO(1250, 740, 1.2))
# taza
body += (f'<path d="M1680 640 C1790 640 1790 790 1680 790" fill="none" stroke="{INK}" stroke-width="26"/>'
         f'<g filter="url(#sh)"><rect x="1500" y="600" width="200" height="240" rx="18" fill="{INK}"/></g><ellipse cx="1600" cy="604" rx="100" ry="14" fill="#2A2222"/>' + LO(1600, 720, 0.85))
B["ropa"] = sec("ropa", "#E6DFD4", INK, [
    SVG(body, alt="El logo en ropa y objetos: remera negra, gorra negra bordada, bolsa negra y taza negra", extra_defs=SH),
    *head("Logo original — aplicaciones", "Ropa y objetos", INK),
    lab("Remera", 110, 840, 450, RED, align="center"), lab("Gorra bordada", 600, 840, 450, RED, align="center"),
    lab("Bolsa", 1060, 990, 380, RED, align="center"), lab("Taza", 1500, 870, 200, RED, align="center")])

# ---------- 08 el estudio (puerta y cartel) ----------
extra = SH + (f'<linearGradient id="vid" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1B2326"/><stop offset=".5" stop-color="#0D1214"/><stop offset="1" stop-color="#151C1F"/></linearGradient>'
              f'<linearGradient id="ref" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
body = f'<rect width="1920" height="1080" fill="{WALL}"/><rect y="1000" width="1920" height="80" fill="#120E0E"/>'
# puerta de vidrio
body += f'<rect x="220" y="300" width="560" height="700" fill="#2A2525"/><rect x="246" y="326" width="508" height="674" fill="url(#vid)"/>'
body += f'<path d="M300 326L520 326L340 1000L246 1000Z" fill="url(#ref)"/>' + LO(500, 580, 1.75)
body += bars(380, 700, [240, 200, 220], CREAM, h=7, gap=20, op=.55) + f'<rect x="700" y="560" width="14" height="180" rx="7" fill="#8A8080"/>'
# cartel de fachada (bandera saliente + caja)
body += f'<rect x="980" y="300" width="840" height="700" fill="#241E1E"/>'
body += f'<g filter="url(#sh)"><rect x="1080" y="380" width="640" height="300" rx="10" fill="{INK}"/></g>' + LO(1400, 530, 2.6)
body += f'<rect x="1360" y="300" width="80" height="80" fill="#2E2828"/>'
body += f'<g filter="url(#sh)"><circle cx="1400" cy="830" r="110" fill="{RED}"/></g>' + L(1400, 830, 0.92, INK, INK)
B["estudio"] = sec("estudio", WALL, CREAM, [
    SVG(body, alt="El logo en el estudio: vinilo rojo en una puerta de vidrio y un cartel negro en la fachada con un timbre redondo rojo", extra_defs=extra),
    *head("Logo original — aplicaciones", "En el estudio", CREAM),
    lab("Vinilo en la puerta", 220, 1020, 560, RED), lab("Cartel y bandera redonda", 980, 1020, 840, RED)])

# ---------- 09 cosas varias ----------
body = f'<rect width="1920" height="1080" fill="{CREAM}"/>'
tape = f'<path d="M0 0H900l-12 15 12 15-12 15 12 15-12 15 12 15-12 15 12 15V120H0l12-15-12-15 12-15-12-15 12-15-12-15 12-15z" fill="{INK}"/>'
tape += "".join(LO(75 + i*150, 60, 0.52) for i in range(6))
body += f'<g transform="translate(130 400) rotate(-5)"><g filter="url(#sh)">{tape}</g></g>'
# caja
body += (f'<g filter="url(#sh)"><path d="M180 700L480 640L720 720L420 790Z" fill="#2A2222"/><path d="M180 700L420 790L420 1000L180 900Z" fill="{INK}"/><path d="M420 790L720 720L720 920L420 1000Z" fill="#1A1414"/></g>'
         f'<g transform="matrix(1 0.37 0 1 0 0)">{LO(300, 735, 0.95)}</g>')
# encendedor
body += f'<g filter="url(#sh)"><rect x="880" y="640" width="120" height="300" rx="16" fill="{RED}"/><rect x="890" y="590" width="100" height="60" rx="8" fill="#B9B2AC"/></g>'
body += f'<g transform="rotate(-90 940 800)">{L(940, 800, 0.85, INK, INK)}</g>'
# pin
body += (f'<g filter="url(#sh)"><g transform="{T(1220, 790, 1.15)}"><use href="#o" fill="{GOLD}" stroke="{GOLD}" stroke-width="12"/></g></g>'
         f'<g transform="{T(1220, 790, 1.15)}"><use href="#o" fill="{INK}" stroke="{RED}" stroke-width="3"/><use href="#w" fill="{RED}"/></g>')
# lápiz
body += f'<g transform="rotate(-20 1620 500)"><g filter="url(#sh)"><rect x="1420" y="480" width="400" height="38" fill="{INK}"/><path d="M1820 480L1880 499L1820 518Z" fill="#E2C9A0"/><path d="M1866 495L1880 499L1866 503Z" fill="#222"/><rect x="1400" y="480" width="24" height="38" fill="{RED}"/></g>{L(1560, 499, 0.3, oval=None)}</g>'
# llavero
body += (f'<circle cx="1640" cy="700" r="26" fill="none" stroke="#B9B2AC" stroke-width="6"/><line x1="1640" y1="726" x2="1640" y2="760" stroke="#B9B2AC" stroke-width="5"/>'
         f'<g filter="url(#sh)"><rect x="1560" y="760" width="160" height="230" rx="80" fill="{RED}"/></g><g transform="rotate(-90 1640 880)">{L(1640, 880, 0.75, INK, INK)}</g>')
B["varios"] = sec("varios", CREAM, INK, [
    SVG(body, alt="Cosas varias con el logo: cinta de embalar negra, caja negra, encendedor rojo, pin, lápiz negro y llavero rojo", extra_defs=SH),
    *head("Logo original — aplicaciones", "Cosas varias", INK),
    lab("Cinta de embalar", 130, 310, 500, RED), lab("Caja", 180, 1010, 300, RED), lab("Encendedor", 820, 960, 240, RED, align="center"),
    lab("Pin", 1120, 900, 200, RED, align="center"), lab("Lápiz", 1500, 330, 200, RED), lab("Llavero", 1540, 1010, 200, RED, align="center")])

# ---------- 10 pantallas ----------
body = f'<rect width="1920" height="1080" fill="{WALL}"/>'
# notebook con fondo de pantalla
body += f'<g filter="url(#sh)"><rect x="150" y="320" width="900" height="560" rx="22" fill="#2A2525"/></g><rect x="176" y="346" width="848" height="508" fill="{INK}"/>' + LO(600, 600, 2.4)
body += f'<path d="M90 880H1110L1070 920H130Z" fill="#3A3434"/>'
# pestaña del navegador
body += f'<rect x="1180" y="330" width="600" height="300" rx="14" fill="#2A2525"/><rect x="1200" y="350" width="240" height="56" rx="10" fill="#3A3434"/>'
body += f'<rect x="1214" y="364" width="28" height="28" rx="6" fill="{RED}"/>' + L(1228, 378, 0.13, INK, INK, sw=8) + bars(1256, 374, [150], CREAM, h=8, op=.6)
body += f'<rect x="1200" y="406" width="560" height="204" fill="{INK}"/>' + LO(1480, 508, 1.0)
# firma de mail
body += f'<rect x="1180" y="680" width="600" height="200" rx="14" fill="{CREAM}"/>' + bars(1210, 710, [340, 280], "#3A3030", h=8, gap=22, op=.35)
body += f'<line x1="1210" y1="775" x2="1750" y2="775" stroke="#3A3030" stroke-opacity=".2"/>' + L(1270, 828, 0.48) + bars(1350, 808, [180, 140], INK, h=8, gap=20, op=.75)
B["pantallas"] = sec("pantallas", WALL, CREAM, [
    SVG(body, alt="El logo en pantallas: fondo de la notebook, ícono de la pestaña del navegador y la firma del mail", extra_defs=SH),
    *head("Logo original — aplicaciones", "Pantallas", CREAM),
    lab("Fondo de pantalla", 150, 940, 600, RED), lab("Pestaña de la web", 1180, 640, 600, RED), lab("Firma del mail", 1180, 890, 600, RED)])

# ---------- separador: variaciones (la portada vieja con eco) ----------
body = f'<rect width="1920" height="1080" fill="{INK}"/>'
for k in range(7, 0, -1):
    body += f'<g opacity="{f(0.55-k*0.06)}">' + ghost(960 - k*20, 600 - k*13, 6.2, RED, INK) + '</g>'
body += L(960, 600, 6.2)
B["variaciones"] = sec("variaciones", INK, CREAM, [
    SVG(body, alt="El logo enorme con contornos que se alejan: separador de la parte de variaciones"),
    lab("Segunda parte", 128, 88, 1000, RED),
    f'<p style="position:absolute;left:128px;top:930px;width:1664px;font-family:\'Pana Italic\', Georgia, serif;font-size:44px;color:{CREAM}">variaciones: el logo estirado para ver hasta dónde da</p>'])

first = ["portada", "sistema", "afiches", "papeleria", "stickers-original", "redes", "ropa", "estudio", "varios", "pantallas", "variaciones"]
for k, v in B.items():
    open(os.path.join(ROOT, "project/slides", k + ".html"), "w").write(v); print(k, len(v))
S.update(B)
order = first + order[1:]
deck["order"] = order
secs = {"s0": {"description": "El logo de Bruno tal cual.", "start": "portada"},
        "sa": {"description": "Aplicaciones del logo original: afiches, papelería, stickers, redes, ropa, el estudio, objetos y pantallas.", "start": "sistema"},
        "sb": {"description": "Variaciones: un anillo y una palabra, estirados.", "start": "variaciones"}}
for k, v in deck["sections"].items():
    if k != "s0": secs[k] = v
deck["sections"] = secs
json.dump(deck, open(os.path.join(ROOT, "project/deck.json"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(SP, "preview3.html"), "w").write(pv.split("<body>")[0] + "<body>" + "".join(S[k] for k in first) + "</body></html>")
print(order)
