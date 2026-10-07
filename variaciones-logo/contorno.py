# Silueta de cada letra -> un solo contorno limpio (sin las piezas encimadas de la tipografía)
import struct, json, subprocess, os
SP = os.path.dirname(os.path.abspath(__file__)); R = 12  # px por unidad
CH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WORD = open(os.path.join(SP, "word_d.txt")).read().split("\n")
W, H = 182*R, 102*R
def raster(d, name):
    open(f"{SP}/{name}.html", "w").write(f'<html><body style="margin:0;background:#fff"><svg width="{W}" height="{H}" viewBox="40 80 182 102"><path d="{d}" fill="#000"/></svg></body></html>')
    subprocess.run([CH, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}", f"--screenshot={SP}/{name}.png", f"file://{SP}/{name}.html"], capture_output=True)
    subprocess.run(["sips", "-s", "format", "bmp", f"{SP}/{name}.png", "--out", f"{SP}/{name}.bmp"], capture_output=True)
    b = open(f"{SP}/{name}.bmp", "rb").read()
    off = struct.unpack('<I', b[10:14])[0]; w, h = struct.unpack('<ii', b[18:26]); row = (w*3+3)//4*4
    return [[1 - b[off+y*row+x*3]/255 for x in range(w)] for y in range(abs(h))], w, abs(h)
def contours(v, w, h):
    segs = {}
    def ept(e):
        k, x, y = e
        if k == 'h': a, c = v[y][x], v[y][x+1]; t = (0.5-a)/(c-a); return (x+t, y)
        a, c = v[y][x], v[y+1][x]; t = (0.5-a)/(c-a); return (x, y+t)
    def link(e1, e2):
        segs.setdefault(e1, []).append(e2); segs.setdefault(e2, []).append(e1)
    for y in range(h-1):
        r0, r1 = v[y], v[y+1]
        for x in range(w-1):
            a, b_, c, d = r0[x] > .5, r0[x+1] > .5, r1[x+1] > .5, r1[x] > .5
            idx = a*8 + b_*4 + c*2 + d
            if idx == 0 or idx == 15: continue
            T, Rr, B, L = ('h', x, y), ('v', x+1, y), ('h', x, y+1), ('v', x, y)
            tab = {1: [(L, B)], 2: [(B, Rr)], 3: [(L, Rr)], 4: [(T, Rr)], 6: [(T, B)], 7: [(T, L)], 8: [(T, L)], 9: [(T, B)],
                   11: [(T, Rr)], 12: [(L, Rr)], 13: [(B, Rr)], 14: [(L, B)]}
            if idx in (5, 10):
                cen = (r0[x]+r0[x+1]+r1[x]+r1[x+1])/4 > .5
                if idx == 5: pairs = [(T, Rr), (L, B)] if not cen else [(T, L), (B, Rr)]
                else: pairs = [(T, L), (B, Rr)] if not cen else [(T, Rr), (L, B)]
            else: pairs = tab[idx]
            for p in pairs: link(*p)
    loops, seen = [], set()
    for e0 in segs:
        if e0 in seen: continue
        loop = [e0]; seen.add(e0); prev, cur = None, e0
        while True:
            nx = [n for n in segs[cur] if n != prev and n not in seen]
            if not nx: break
            prev, cur = cur, nx[0]; seen.add(cur); loop.append(cur)
        if len(loop) > 20: loops.append([ept(e) for e in loop])
    return loops
def dp(pts, tol):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]; L = ((x2-x1)**2+(y2-y1)**2)**.5 or 1e-9
    i, dm = 0, 0
    for k in range(1, len(pts)-1):
        dd = abs((x2-x1)*(y1-pts[k][1]) - (x1-pts[k][0])*(y2-y1))/L
        if dd > dm: i, dm = k, dd
    if dm > tol: return dp(pts[:i+1], tol)[:-1] + dp(pts[i:], tol)
    return [pts[0], pts[-1]]
out = []
for i, d in enumerate(WORD):
    v, w, h = raster(d, f"let{i}")
    paths = []
    for lp in contours(v, w, h):
        n = len(lp); half = n//2
        sp = dp(lp[:half+1], 0.35)[:-1] + dp(lp[half:] + [lp[0]], 0.35)[:-1]
        paths.append("M" + "L".join(f"{x/R+40:.2f} {y/R+80:.2f}" for x, y in sp) + "Z")
    out.append("".join(paths)); print("letra", i, "contornos:", len(paths), "puntos:", sum(p.count("L") for p in paths))
json.dump(out, open(os.path.join(SP, "word_union.json"), "w"))
