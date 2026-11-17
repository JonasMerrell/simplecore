# over-centre lid spring geometry search (side plane, x forward=-X world, z up)
import numpy as np, itertools, sys, json
g=9.81
def lidpt(H,u,v,th):  # lid local (u forward of hinge along lid, v up normal) -> world (x,z); forward = -x
    c,s=np.cos(th),np.sin(th)
    return np.array([H[0]-u*c+v*s, H[1]+u*s+v*c])
def evaluate(H,B,u,v,Lext,stroke,F1,k,mass,ucg,vcg,thmax,n=2):
    th=np.radians(np.linspace(0,thmax,181))
    L=np.array([lidpt(H,u,v,t) for t in th]); l=np.linalg.norm(L-B,axis=1)
    dl=np.gradient(l,th)
    comp=Lext-l
    F=F1*(1+(k-1)*comp/stroke)
    Ts=n*F*dl/1000   # opening torque N m
    cg=np.array([lidpt(H,ucg,vcg,t) for t in th]); Tg=-mass*g*(H[0]-cg[:,0])/1000  # gravity: positive opening; cg forward of hinge closes
    T=Ts+Tg
    return dict(th=np.degrees(th),l=l,comp=comp,T=T,Ts=Ts,Tg=Tg,L=L)
