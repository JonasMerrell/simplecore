# Torque about the lid hinge vs opening angle for the chosen spring geometry (two springs), and the numbers in the README.
# usage: python3 torque_plot.py OUT.png   (needs matplotlib)
import sys, numpy as np
from oc import evaluate
H=np.array([444.0,601.95]); B=np.array([175.5,571.0])      # hinge axis and frame ball centre, see mklid.py
U,V=100.0,-50.0                                             # lid ball: 100 in front of the hinge axis, 50 below it
LEXT,STROKE,OPEN=245,95,85                                  # HUOPO 10 in kit (245 ball to ball, 95 stroke); fully extended at 85 deg
MASS,UCG,VCG=2.6,239.0,-11.0                                 # lid + PIR + brackets (kg), CG from the hinge axis
F1,K=80.0,1.3                                               # force at full extension per spring (N), F2/F1
R=evaluate(H,B,U,V,LEXT,STROKE,F1,K,MASS,UCG,VCG,OPEN,n=2)
th,T,Ts,Tg,l=R['th'],R['T'],R['Ts'],R['Tg'],R['l']
lever=H[0]+25.5
print(f"closed: net {T[0]:.1f} N m (springs {Ts[0]:.1f}, lid weight {Tg[0]:.1f}); lift at the front edge {-T[0]/lever*1000:.0f} N")
print(f"springs' dead point {th[l.argmin()]:.0f} deg (shortest {l.min():.1f} mm, fully in at {LEXT-STROKE})")
print(f"net torque turns opening at {th[np.argmax(T>0)]:.0f} deg; at {OPEN} deg {T[-1]:.1f} N m holding it open; spring {l[-1]:.1f} mm long ({LEXT} = full stroke = stop); closed {l[0]:.1f} mm; highest spring force {F1*(1+(K-1)*(LEXT-l.min())/STROKE):.0f} N")
if len(sys.argv)>1:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.6),dpi=150)
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis='y',color='#e4e3df',lw=0.8); ax.axhline(0,color='#8c8b85',lw=1)
    ax.plot(th,Ts,color='#eb6834',lw=2,label=f'Gas springs (2 x {F1:.0f} N)')
    ax.plot(th,Tg,color='#1baf7a',lw=2,label='Lid weight')
    ax.plot(th,T,color='#2a78d6',lw=2.5,label='Net')
    i=np.argmax(T>0); ax.plot([th[i]],[0],'o',ms=8,color='#2a78d6',mec='white',mew=2)
    ax.annotate(f'opens by itself past {th[i]:.0f}°',(th[i],0),(th[i]+2.5,-2.2),fontsize=9,color='#3d3c38')
    ax.annotate(f'held shut: {T[0]:.0f} N·m',(0,T[0]),(3,T[0]+0.6),fontsize=9,color='#3d3c38')
    ax.annotate(f'held open: {T[-1]:.0f} N·m',(OPEN,T[-1]),(OPEN-28,T[-1]+1.5),fontsize=9,color='#3d3c38')
    ax.set_xlabel('Lid opening angle (°)',color='#3d3c38'); ax.set_ylabel('Torque about the hinge (N·m)\n+ opens, − closes',color='#3d3c38')
    ax.tick_params(colors='#6b6a64'); ax.set_xlim(0,OPEN)
    ax.legend(frameon=False,loc='upper left',fontsize=9)
    ax.set_title('Top lid: over-centre gas springs',loc='left',fontsize=11,color='#1a1a19')
    fig.tight_layout(); fig.savefig(sys.argv[1])
