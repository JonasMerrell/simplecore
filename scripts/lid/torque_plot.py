# Torque about the lid hinge vs opening angle for the chosen spring geometry (two springs), and the numbers in the README.
# usage: python3 torque_plot.py OUT.png   (needs matplotlib)
import sys, numpy as np
from oc import evaluate
H=np.array([441.0,598.95]); B=H+np.array([-158.5,-75.5])   # ball centres, see mklid.py
U,V=37.5,-60.0                                              # lid ball: 37.5 in front of the hinge axis, 60 below it
MASS,UCG,VCG=2.6,236.0,-8.0                                 # lid + PIR + brackets (kg), CG from the hinge axis
F1,K=100.0,1.3                                              # force at full extension per spring (N), F2/F1
R=evaluate(H,B,U,V,150,50,F1,K,MASS,UCG,VCG,90,n=2)
th,T,Ts,Tg,l=R['th'],R['T'],R['Ts'],R['Tg'],R['l']
lever=H[0]+25.5
print(f"closed: net {T[0]:.1f} N m (springs {Ts[0]:.1f}, lid weight {Tg[0]:.1f}); lift at the front edge {-T[0]/lever*1000:.0f} N")
print(f"springs' dead point {th[l.argmin()]:.0f} deg (shortest {l.min():.1f} mm, fully in at 100)")
print(f"net torque turns opening at {th[np.argmax(T>0)]:.0f} deg; at 90 deg {T[-1]:.1f} N m holding it open; spring {l[-1]:.1f} mm long (150 = full stroke = stop)")
if len(sys.argv)>1:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.6),dpi=150)
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis='y',color='#e4e3df',lw=0.8); ax.axhline(0,color='#8c8b85',lw=1)
    ax.plot(th,Ts,color='#eb6834',lw=2,label='Gas springs (2 x 100 N)')
    ax.plot(th,Tg,color='#1baf7a',lw=2,label='Lid weight')
    ax.plot(th,T,color='#2a78d6',lw=2.5,label='Net')
    i=np.argmax(T>0); ax.plot([th[i]],[0],'o',ms=8,color='#2a78d6',mec='white',mew=2)
    ax.annotate(f'opens by itself past {th[i]:.0f}°',(th[i],0),(th[i]+2.5,-2.2),fontsize=9,color='#3d3c38')
    ax.annotate(f'held shut: {T[0]:.0f} N·m',(0,T[0]),(3,T[0]+0.6),fontsize=9,color='#3d3c38')
    ax.annotate(f'held open: {T[-1]:.0f} N·m',(90,T[-1]),(62,T[-1]+1.5),fontsize=9,color='#3d3c38')
    ax.set_xlabel('Lid opening angle (°)',color='#3d3c38'); ax.set_ylabel('Torque about the hinge (N·m)\n+ opens, − closes',color='#3d3c38')
    ax.tick_params(colors='#6b6a64'); ax.set_xlim(0,90)
    ax.legend(frameon=False,loc='upper left',fontsize=9)
    ax.set_title('Top lid: over-centre gas springs',loc='left',fontsize=11,color='#1a1a19')
    fig.tight_layout(); fig.savefig(sys.argv[1])
