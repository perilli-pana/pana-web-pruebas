import math
K = 13.58/63.86; YB = 155.24; ANG = math.degrees(math.atan(K))
def bowl_right(x0, xr):   # stem at x0, bowl bulging right to xr
    m = x0 + (xr-x0)*0.55
    return f"H{m:.1f}C{xr-1.9:.1f} 114 {xr} 121 {xr} 132C{xr} 143 {xr-1.9:.1f} 150 {m:.1f} 150H{x0}"
def bowl_left(x0, xl):
    m = x0 - (x0-xl)*0.55
    return f"H{m:.1f}C{xl+1.9:.1f} 114 {xl} 121 {xl} 132C{xl} 143 {xl+1.9:.1f} 150 {m:.1f} 150H{x0}"
def a(x):  # x = stem center
    return f"M{x} 155.4V121C{x} 116.5 {x-2.5:.1f} 114 {x-6:.1f} 114" + bowl_left(x-6, x-21.1)[0:0] + \
           f"H{x-11.6:.1f}C{x-19.2:.1f} 114 {x-21.1:.1f} 121 {x-21.1:.1f} 132C{x-21.1:.1f} 143 {x-19.2:.1f} 150 {x-11.6:.1f} 150H{x}"
CL = [
 "M56.5 172.6V121C56.5 116.5 59 114 62.5 114H68C75.5 114 77.4 121 77.4 132C77.4 143 75.5 150 68 150H56.5",
 a(115.6),
 "M133.9 155.4V122C133.9 116.5 138 114 144 114C150 114 154 116.5 154 122V155.4",
 a(192.9),
]
TR = f'translate({K*YB:.3f} 0) skewX({-ANG:.3f})'

# anillo abierto: se corta donde lo cruza el palo de la p (un tubo pasa por detrás del otro)
def _ov(t):
    import math
    c, s_ = math.cos(t), math.sin(t); r = math.radians(-3.96)
    x, y = 88.3*c, 45.01*s_
    return (131.08 + x*math.cos(r) - y*math.sin(r), 131.08 + x*math.sin(r) + y*math.cos(r))
def _side(t):
    x, y = _ov(t); return x - (56.5 + K*(YB - y))
def oval_gap(g=4.0, n=240):
    import math
    ts = [i/2000*2*math.pi for i in range(2000)]
    tc = None
    for a_, b_ in zip(ts, ts[1:]):
        ya = _ov(a_)[1]
        if 121 < ya < 172.6 and _side(a_)*_side(b_) < 0: tc = (a_+b_)/2
    dt = g/math.hypot(*[p-q for p, q in zip(_ov(tc+0.001), _ov(tc))])*0.001
    t0, t1 = tc + dt, tc - dt + 2*math.pi
    pts = [_ov(t0 + (t1-t0)*i/n) for i in range(n+1)]
    return "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
