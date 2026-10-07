# corta el anillo donde se acerca a las letras (lee wd.bmp: la palabra engordada, 8px por unidad)
import struct, math
b=open('wd.bmp','rb').read()
off=struct.unpack('<I',b[10:14])[0]; w,h=struct.unpack('<ii',b[18:26]); row=(w*3+3)//4*4
def inside(x,y):
    px=int((x-40)*8); py=int((y-80)*8)
    return 0<=px<w and 0<=py<abs(h) and b[off+py*row+px*3]<128
r=math.radians(-3.96); N=1400
def ov(t):
    x,y=88.3*math.cos(t),45.01*math.sin(t)
    return (131.08+x*math.cos(r)-y*math.sin(r),131.08+x*math.sin(r)+y*math.cos(r))
pts=[ov(i/N*2*math.pi) for i in range(N)]; flags=[inside(*p) for p in pts]
s0=flags.index(False); pts=pts[s0:]+pts[:s0]; flags=flags[s0:]+flags[:s0]
segs=[];cur=[]
for p,fl in zip(pts+[pts[0]],flags+[flags[0]]):
    if fl:
        if cur: segs.append(cur); cur=[]
    else: cur.append(p)
if cur: segs.append(cur)
if len(segs)>1 and not flags[-1]: segs[0]=segs[-1]+segs[0]; segs.pop()
print("tramos del anillo:", len(segs))
open('ovalcut.txt','w').write("".join("M"+"L".join(f"{x:.2f} {y:.2f}" for x,y in s[::2]+[s[-1]]) for s in segs))
