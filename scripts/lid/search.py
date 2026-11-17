import numpy as np
g=9.81
H=np.array([441.0,598.0]); mass=2.6; ucg=441-205+0.0; vcg=-8
th=np.radians(np.linspace(0,90,91))
c,s=np.cos(th),np.sin(th)
bx,bz,u,v=np.meshgrid(np.arange(300,476,5),np.arange(380,591,5),np.arange(10,301,10),np.arange(-200,1,10),indexing='ij')
bx,bz,u,v=[a.ravel()[:,None] for a in (bx,bz,u,v)]
Lx=H[0]-u*c+v*s; Lz=H[1]+u*s+v*c
l=np.hypot(Lx-bx,Lz-bz)
dl=np.gradient(l,th,axis=1)
Tg=-mass*g*(u*0+ (ucg*c - vcg*s))/1000   # gravity closing torque
Tg=Tg[0]
SIZES=[(150,50),(180,60),(200,70),(225,80),(245,100),(265,110),(305,130)]
k=1.3; out=[]
for Lext,st in SIZES:
    ok=(l[:,-1]<=Lext)&(l[:,-1]>Lext-15)&(l.max(1)<=Lext+0.01)&(l.min(1)>=Lext-st+3)
    imin=l.argmin(1); ok&=(imin>4)&(imin<50)
    idx=np.where(ok)[0]
    if not len(idx): continue
    L=l[idx]; D=dl[idx]
    Fu=(1+(k-1)*(Lext-L)/st)          # per N of F1
    Ts1=2*Fu*D/1000
    F1=(-12.0-Tg[0])/Ts1[:,0]
    T=F1[:,None]*Ts1+Tg
    T0=-T[:,0]; peak=-T.min(1)
    cross=np.argmax(T>0,axis=1)

    Te=T[:,-1]; good=(F1>20)&(F1<400)&(Te>=3)&(Te<=15)&(cross<60)
    for j in np.where(good)[0]:
        i=idx[j]
        out.append((round(peak[j]/0.466,1),Lext,st,float(bx[i,0]),float(bz[i,0]),float(u[i,0]),float(v[i,0]),round(F1[j]),round(T0[j],1),round(Te[j],1),int(cross[j]),int(imin[i]),round(float(L[j].min()),1)))
out.sort()
print(len(out))
for o in out[:30]: print(o)
import json; json.dump(out,open('cands.json','w'))
