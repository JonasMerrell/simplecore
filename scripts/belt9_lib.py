import json, functools
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Trsf, gp_Mat, gp_XYZ
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
D=json.load(open('/home/user/simplecore/X-carriage.json'))
G='/tmp/claude-0/-home-user/b4ed2eb0-ec11-5e8b-baf6-17227d59f068/scratchpad/geo/'
@functools.lru_cache(None)
def solids(studio):
    import os
    if not os.path.exists(G+f's{studio}_f0.step'): return None
    r=STEPControl_Reader(); r.ReadFile(G+f's{studio}_f0.step'); r.TransferRoots(); sh=r.OneShape()
    out=[]; e=TopExp_Explorer(sh,TopAbs_SOLID)
    while e.More(): out.append(TopoDS.Solid(e.Current())); e.Next()
    return out
def trsf(pose):
    r=pose['r']; t=pose['t']
    # column-major
    T=gp_Trsf(); m=[[r[c*3+row] for c in range(3)] for row in range(3)]
    T.SetValues(m[0][0],m[0][1],m[0][2],t[0], m[1][0],m[1][1],m[1][2],t[1], m[2][0],m[2][1],m[2][2],t[2]); return T
def walk(ai, T=None, path=''):
    T=T or gp_Trsf()
    for ins in D['assemblies'][ai]['instances']:
        Ti=T.Multiplied(trsf(ins['pose']))
        if ins.get('assembly') is not None or ins['body']==[0,0] and False: pass
        if ins.get('sub') is not None:
            yield from walk(ins['sub'],Ti,path+ins['name']+'/')
        else:
            yield path+ins['name'], ins, Ti
def shape(ins,Ti):
    ss=solids(ins['studio'])
    if ss is None: return None
    s=ss[ins['body'][1]]
    return BRepBuilderAPI_Transform(s,Ti,True).Shape()
def bbox(sh):
    b=Bnd_Box(); BRepBndLib.Add_s(sh,b); a=b.CornerMin(); c=b.CornerMax(); return [round(x,2) for x in (a.X(),a.Y(),a.Z(),c.X(),c.Y(),c.Z())]
def cyls(sh):
    out=[]; e=TopExp_Explorer(sh,TopAbs_FACE)
    while e.More():
        f=TopoDS.Face(e.Current()); a=BRepAdaptor_Surface(f)
        if a.GetType()==GeomAbs_Cylinder:
            c=a.Cylinder(); ax=c.Axis(); l=ax.Location(); dd=ax.Direction()
            out.append((round(c.Radius(),3),[round(l.X(),2),round(l.Y(),2),round(l.Z(),2)],[round(dd.X(),3),round(dd.Y(),3),round(dd.Z(),3)],bbox(f)))
        e.Next()
    return out
