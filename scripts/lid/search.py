# Search that picked the spring geometry (rev 3: springs in front of the filament tube).
# For each spring size, open angle and lid ball position (u in front of the hinge axis, v below it), the frame ball
# sits on the circle where the spring is fully extended at the open angle (the spring is the open stop). Kept: the
# frame ball on the side panel beside the top side rail, the lid ball at least 100 in front of the hinge (27 mm in
# front of the filament tube hole), 4 mm of stroke spare, dead point 12..40 deg, 15..24 N m shut, >= 5 N m open.
# usage: python3 search.py     (columns: score, extended, stroke, open angle, N per spring, frame ball x z, u, v,
#                               N m shut, N m open, dead point, self-opening angle, length closed, shortest)
import numpy as np
g=9.81
H=np.array([444.0,601.95]); mass=2.6; ucg=239; vcg=-11; k=1.3
out=[]
for (Lext,st) in [(250,80),(245,80),(245,90)]:
 for tm in (80,85,90,95,100):
  th=np.radians(np.linspace(0,tm,181)); c,s=np.cos(th),np.sin(th)
  Tg=-mass*g*(ucg*c-vcg*s)/1000
  for u in np.arange(100,131,2.5):
    for v in np.arange(-80,-39,2.5):
      Lx=H[0]-u*c+v*s; Lz=H[1]+u*s+v*c
      a=np.radians(np.arange(170,271,0.5))
      bx=Lx[-1]+Lext*np.cos(a); bz=Lz[-1]+Lext*np.sin(a)
      ok=(bx>40)&(bx<335)&(bz>540)&(bz<583)
      for BX,BZ in zip(bx[ok],bz[ok]):
        l=np.hypot(Lx-BX,Lz-BZ)
        if l.min()<Lext-st+4: continue
        dead=np.degrees(th[l.argmin()])
        if not 12<dead<40: continue
        dl=np.gradient(l,th)
        for F1 in (50,60,80,100):
          T=2*F1*(1+(k-1)*(Lext-l)/st)*dl/1000+Tg
          T0=-T[0]; Te=T[-1]
          if T0<15 or T0>24 or Te<5: continue
          cross=np.degrees(th[np.argmax(T>0)])
          if cross>48: continue
          out.append((round(float(abs(T0-18)+abs(Te-12)*0.3+cross*0.05),2),Lext,st,tm,F1,round(float(BX),1),round(float(BZ),1),float(u),float(v),round(float(T0),1),round(float(Te),1),round(float(dead)),round(float(cross)),round(float(l[0]),1),round(float(l.min()),1)))
out.sort(); seen={}
for o in out:
    key=o[1:5]; seen[key]=seen.get(key,0)+1
    if seen[key]<=2: print(o)
print(len(out),'candidates')
