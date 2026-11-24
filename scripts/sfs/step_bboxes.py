#!/usr/bin/env python3
"""World bounding boxes of every solid in a (SolidWorks AP214) STEP assembly, from its vertices.
usage: step_bboxes.py file.step out.json   -> [{name, path, lo, hi}] in the STEP's own frame"""
import re,sys,json
import numpy as np, os
MODE=int(os.environ.get("MODE","0"))
txt=open(sys.argv[1],encoding='latin-1').read()
E={}
for m in re.finditer(r'#(\d+)\s*=\s*(.*?);\s*\r?\n(?=#|ENDSEC)',txt,re.S):
    E[int(m.group(1))]=m.group(2).replace('\r','').replace('\n',' ')
def typ(s): return s.split('(',1)[0].strip()
def refs(s): return [int(x) for x in re.findall(r'#(\d+)',s)]
def strs(s): return re.findall(r"'([^']*)'",s)
def nums(s): return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',s.split('(',1)[1])]
byt={}
for k,s in E.items(): byt.setdefault(typ(s),[]).append(k)
def pt(k): return np.array(nums(E[k])[-3:])
def direction(k): return np.array(nums(E[k])[-3:])
def axis(k):
    r=refs(E[k]); o=pt(r[0]); z=direction(r[1]) if len(r)>1 else np.array([0,0,1.]); x=direction(r[2]) if len(r)>2 else np.array([1,0,0.])
    z=z/np.linalg.norm(z); x=x-z*np.dot(x,z); x=x/np.linalg.norm(x); y=np.cross(z,x)
    M=np.eye(4); M[:3,0]=x; M[:3,1]=y; M[:3,2]=z; M[:3,3]=o; return M
# solid vertex bboxes
WALK={'CLOSED_SHELL','OPEN_SHELL','ADVANCED_FACE','FACE_BOUND','FACE_OUTER_BOUND','EDGE_LOOP','ORIENTED_EDGE','MANIFOLD_SOLID_BREP','BREP_WITH_VOIDS','ORIENTED_CLOSED_SHELL'}
def solid_pts(b):
    seen=set(); st=[b]; P=[]
    while st:
        k=st.pop()
        if k in seen: continue
        seen.add(k); t=typ(E[k])
        if t=='VERTEX_POINT': P.append(pt(refs(E[k])[0])); continue
        if t=='EDGE_CURVE': st+=refs(E[k])[:2]; continue
        if t in WALK: st+=refs(E[k])
    return np.array(P) if P else np.zeros((0,3))
# product definitions -> names
pdname={}
for k in byt.get('PRODUCT_DEFINITION',[]):
    f=refs(E[k])[0]; p=refs(E[f])[0]; pdname[k]=strs(E[p])[0]
pds_pd={k:refs(E[k])[-1] for k in byt.get('PRODUCT_DEFINITION_SHAPE',[])}
pd_sr={}
for k in byt.get('SHAPE_DEFINITION_REPRESENTATION',[]):
    a,b=refs(E[k])[:2]
    if a in pds_pd: pd_sr[pds_pd[a]]=b
# SR -> reps with solids (via SHAPE_REPRESENTATION_RELATIONSHIP, plain type only)
sr_links={}
for k in byt.get('SHAPE_REPRESENTATION_RELATIONSHIP',[]):
    a,b=refs(E[k])[:2]; sr_links.setdefault(a,[]).append(b); sr_links.setdefault(b,[]).append(a)
def solids_of(sr):
    out=[]
    for rep in [sr]+sr_links.get(sr,[]):
        for it in refs(E[rep]):
            if typ(E.get(it,'')) in ('MANIFOLD_SOLID_BREP','BREP_WITH_VOIDS'): out.append(it)
    return out
# assembly links
nauo={k:refs(E[k])[:2] for k in byt.get('NEXT_ASSEMBLY_USAGE_OCCURRENCE',[])}  # parent pd, child pd
pds_of_nauo={v:k for k,v in pds_pd.items() if v in nauo}
children={}
for k in byt.get('CONTEXT_DEPENDENT_SHAPE_REPRESENTATION',[]):
    rel,pds=refs(E[k])[:2]; n=pds_pd[pds]; parent,child=nauo[n]
    s=E[rel]; m=re.search(r'REPRESENTATION_RELATIONSHIP\s*\(\s*\'[^\']*\'\s*,\s*\'[^\']*\'\s*,\s*#(\d+)\s*,\s*#(\d+)',s)
    t=re.search(r'REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION\s*\(\s*#(\d+)',s)
    a1,a2=refs(E[int(t.group(1))])[:2]
    T=axis(a2)@np.linalg.inv(axis(a1)) if MODE==0 else axis(a1)@np.linalg.inv(axis(a2))
    children.setdefault(parent,[]).append((child,T,n))
allchild={c for v in children.values() for c,_,_ in v}
roots=[p for p in children if p not in allchild] or list(pd_sr)
out=[]; cache={}
def walk(pd,M,path):
    for s in solids_of(pd_sr.get(pd,-1)) if pd in pd_sr else []:
        if s not in cache: cache[s]=solid_pts(s)
        P=cache[s]
        if len(P):
            W=(M[:3,:3]@P.T).T+M[:3,3]
            out.append({'name':pdname[pd],'path':path,'lo':W.min(0).round(2).tolist(),'hi':W.max(0).round(2).tolist()})
    for c,T,n in children.get(pd,[]): walk(c,M@T,path+'/'+pdname[c])
for r in roots: walk(r,np.eye(4),pdname[r])
json.dump(out,open(sys.argv[2],'w'),indent=0)
print(len(out),'solids; roots',[pdname[r] for r in roots])
