import sys; sys.path.insert(0,'.')
from lib import *
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
items=[]
for p,ins,T in walk(22):
    if any(k in p for k in ['PIR','Enclosure','door','Sherpa','Bed','heater','blower']): continue
    sh=shape(ins,T)
    if sh is None: continue
    b=bbox(sh)
    if b[5]>430 and b[2]<470: items.append((p,sh,b))
def section(z,fn,xl=None,yl=None):
    fig,ax=plt.subplots(figsize=(16,16))
    cols={'Frame':'k','X gantry':'b','Toolhead':'r'}
    for p,sh,b in items:
        if not (b[2]<z<b[5]): continue
        s=BRepAlgoAPI_Section(sh,gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1))); s.Build()
        e=TopExp_Explorer(s.Shape(),TopAbs_EDGE)
        c=[v for k,v in cols.items() if p.startswith(k)]; c=c[0] if c else 'g'
        while e.More():
            cu=BRepAdaptor_Curve(TopoDS.Edge(e.Current())); d=GCPnts_QuasiUniformDeflection(cu,0.05)
            pts=[d.Value(i+1) for i in range(d.NbPoints())]
            ax.plot([q.Y() for q in pts],[q.X() for q in pts],c,lw=0.7); e.Next()
    ax.set_aspect('equal'); ax.set_xlabel('Y'); ax.set_ylabel('X (rear up)'); ax.grid(True,lw=0.3)
    if xl: ax.set_xlim(*xl)
    if yl: ax.set_ylim(*yl)
    ax.set_title(f'z={z}'); plt.savefig(fn,dpi=60); plt.close()
section(442,'z442.png'); section(454,'z454.png')
section(442,'z442_rr.png',(395,480),(370,430)); section(454,'z454_rr.png',(395,480),(370,430))
section(442,'z442_j.png',(420,480),(150,220)); section(454,'z454_j.png',(420,480),(150,220))
