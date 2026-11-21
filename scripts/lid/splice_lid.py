# Add the top lid to a document: Part Studios "Top lid" and "Lid gas springs", assemblies "Top lid" (moves) and
# "Lid frame hardware" (fixed), and in the target assembly: both, two gas spring bodies and rods, and the mates:
# lid hinge (revolute, 0..90 deg), each spring body pivoting on the lid's ball stud, each rod on the frame's, and
# body/rod sliding on one axis (cylindrical). Hides the old top panel and the old top PIR board (the lid carries it).
# usage: python3 splice_lid.py lid-doc.json TARGET.json [--test]   -> TARGET.json.new
# TARGET must not have the lid yet (start from main's documents to redo it).
import json,sys,copy,math
C=json.load(open(sys.argv[1])); src=sys.argv[2]; test='--test' in sys.argv
G=json.load(open(sys.argv[1].replace('lid-doc.json','lid_geom.json')))
d=json.load(open(src))
assert not any(s['name']=='Top lid' for s in d['studios'])
key=lambda k: tuple(map(int,k.split(':')))
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
st=copy.deepcopy(C['studios'][0]); st['name']='Top lid'; si=len(d['studios']); d['studios'].append(st)
sp=copy.deepcopy(C['studios'][1]); sp['name']='Lid gas springs'; gi=len(d['studios']); d['studios'].append(sp)
P={v['name']:list(key(k)) for k,v in st['doc']['parts'].items()}
def find(s): return [n for n in P if n.startswith(s)]
MOVES=('Top lid panel','Lid insulation','lid arm','pin, M3','Lid spring bracket','Lid handle')
moving=[n for n in P if any(t in n for t in MOVES)]
fixed=[n for n in P if n not in moving]
HX,HZ=G['H']; BY=G['BALL_Y']; YC=G['YC']; Bx,Bz=G['B']; Lx,Lz=G['L']; STUD_Y=G['LB_Y'][0]
RX_R={"r":[1,0,0, 0,0,1, 0,-1,0],"t":None}   # columns: local z -> world -y
RX_L={"r":[1,0,0, 0,0,-1, 0,1,0],"t":None}   # local z -> world +y
def stud(name,x,z,left,iid):
    y=2*YC-STUD_Y if left else STUD_Y
    return {"id":iid,"name":name,"studio":gi,"body":[3,0],"pose":{"r":[float(v) for v in (RX_L if left else RX_R)['r']],"t":[x,y,z]},"fixed":True,"hidden":False}
def asm(name,names,extra=[]):
    inst=[{"id":n+1,"name":nm+f' <{n+1}>',"studio":si,"body":P[nm],"pose":I(),"fixed":True,"hidden":False} for n,nm in enumerate(names)]
    for e in extra: e['id']=len(inst)+1; inst.append(e)
    d['assemblies'].append({"name":name,"instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]}); return len(d['assemblies'])-1
lid_a=asm('Top lid',moving,[stud('Ball stud M6, lid, right <1>',Lx,Lz,False,0),stud('Ball stud M6, lid, left <2>',Lx,Lz,True,0)])
hw_a=asm('Lid frame hardware',fixed,[stud('Ball stud M6, frame, right <1>',Bx,Bz,False,0),stud('Ball stud M6, frame, left <2>',Bx,Bz,True,0)])
if test:
    d['assemblies'].append({"name":"Lid test","instances":[],"mates":[],"next_id":1,"relations":[]})
    T=d['assemblies'][-1]
else:
    T=[a for a in d['assemblies'] if a['name']=='Printer'][0]
    # hide the old top panel and the old top PIR board
    for a in d['assemblies']:
        for i in a['instances']:
            if (a['name']=='Enclosure' and i['name']=='Top panel') or (a['name']=='PIR insulation' and i['name'].startswith('PIR top')): i['hidden']=True
nid=[max([T['next_id']-1]+[x['id'] for x in T['instances']]+[m['id'] for m in T['mates']]+[r['id'] for r in T['relations']])]
def new():
    nid[0]+=1; return nid[0]
def put(name,studio,body,pose,fixed,sub=None):
    e={"id":new(),"name":name,"studio":studio,"body":body,"pose":pose,"fixed":fixed,"hidden":False}
    if sub is not None: e['sub']=sub
    T['instances'].append(e); return e['id']
def conn(inst,o,z,x): return {"inst":inst,"origin":[float(v) for v in o],"z":[float(v) for v in z],"x":[float(v) for v in x]}
def mate(name,kind,a,b,limits=None,flip=True):
    T['mates'].append({"id":new(),"name":name,"kind":kind,"a":a,"b":b,"flip":flip,"offset":0.0,"offset_xy":[0.0,0.0],"rotation":0.0,"limits":limits,"suppressed":False}); return nid[0]
hw=put('Lid frame hardware <1>',0,[0,0],I(),True,hw_a)
lid=put('Top lid <1>',0,[0,0],I(),False,lid_a)
hinge=mate('Top lid hinge','Revolute',conn(hw,[HX,0,HZ],[0,1,0],[1,0,0]),conn(lid,[HX,0,HZ],[0,1,0],[1,0,0]),[0.0,90.0])
dx,dz=Bx-Lx,Bz-Lz; n=math.hypot(dx,dz); ux,uz=dx/n,dz/n
for side,left in (('right',False),('left',True)):
    y=2*YC-BY if left else BY
    rb={"r":[ux,0,uz, 0,1,0, -uz,0,ux],"t":[Lx,y,Lz]}        # body: local x from the lid ball towards the frame ball
    rr={"r":[-ux,0,-uz, 0,1,0, uz,0,-ux],"t":[Bx,y,Bz]}      # rod: local x from the frame ball towards the lid ball
    b=put(f'Gas spring body, {side} <1>',gi,[1,0],rb,False)
    r=put(f'Gas spring rod, {side} <1>',gi,[2,0],rr,False)
    mate(f'Gas spring {side}, lid ball','Revolute',conn(lid,[Lx,y,Lz],[0,1,0],[1,0,0]),conn(b,[0,0,0],[0,1,0],[ux,0,-uz]))
    mate(f'Gas spring {side}, frame ball','Revolute',conn(hw,[Bx,y,Bz],[0,1,0],[1,0,0]),conn(r,[0,0,0],[0,1,0],[-ux,0,uz]))
    mate(f'Gas spring {side}, stroke','Cylindrical',conn(b,[0,0,0],[1,0,0],[0,1,0]),conn(r,[0,0,0],[-1,0,0],[0,1,0]),[100.0-n,150.0-n] if False else None)
T['next_id']=nid[0]+1
json.dump(d,open(src+'.new','w'))
print(src,'studios',si,gi,'assemblies',lid_a,hw_a,'target',T['name'],'hinge mate',hinge,'instances',lid,hw)
