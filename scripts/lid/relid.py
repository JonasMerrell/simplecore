# Update the top lid in a document that already has it (splice_lid.py adds it to one that does not), in place:
# the "Top lid" and "Lid gas springs" Part Studios are replaced by the new lid-doc.json's, the "Top lid" and
# "Lid frame hardware" assemblies are rebuilt at the same indices, and in Printer the gas spring bodies and rods are
# moved to the new ball positions and their ball mates re-pointed. Every other studio and assembly keeps its index,
# so other workstreams' parts are untouched.
# usage: python3 relid.py lid-doc.json TARGET.json   -> TARGET.json.new
import json,sys,math,copy
C=json.load(open(sys.argv[1])); src=sys.argv[2]
G=json.load(open(sys.argv[1].replace('lid-doc.json','lid_geom.json')))
d=json.load(open(src))
si=[i for i,s in enumerate(d['studios']) if s['name']=='Top lid']; gi=[i for i,s in enumerate(d['studios']) if s['name']=='Lid gas springs']
assert len(si)==1 and len(gi)==1, 'target has no lid (use splice_lid.py)'
si,gi=si[0],gi[0]
st=copy.deepcopy(C['studios'][0]); st['name']='Top lid'; d['studios'][si]=st
sp=copy.deepcopy(C['studios'][1]); sp['name']='Lid gas springs'; d['studios'][gi]=sp
key=lambda k: tuple(map(int,k.split(':')))
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
P={v['name']:list(key(k)) for k,v in st['doc']['parts'].items()}
MOVES=('Top lid panel','Lid insulation','corner arm','pin, M3','Lid spring lever','Lid handle')
moving=[n for n in P if any(t in n for t in MOVES)]
fixed=[n for n in P if n not in moving]
HX,HZ=G['H']; BY=G['BALL_Y']; YC=G['YC']; Bx,Bz=G['B']; Lx,Lz=G['L']; STUD_Y=G['LB_Y'][0]
RX_R=[1,0,0, 0,0,1, 0,-1,0]   # columns: local z -> world -y
RX_L=[1,0,0, 0,0,-1, 0,1,0]   # local z -> world +y
def stud(name,x,z,left):
    y=2*YC-STUD_Y if left else STUD_Y
    return {"id":0,"name":name,"studio":gi,"body":[3,0],"pose":{"r":[float(v) for v in (RX_L if left else RX_R)],"t":[x,y,z]},"fixed":True,"hidden":False}
def rebuild(name,names,extra):
    ai=[i for i,a in enumerate(d['assemblies']) if a['name']==name]; assert len(ai)==1; ai=ai[0]
    inst=[{"id":n+1,"name":nm+f' <{n+1}>',"studio":si,"body":P[nm],"pose":I(),"fixed":True,"hidden":False} for n,nm in enumerate(names)]
    for e in extra: e['id']=len(inst)+1; inst.append(e)
    d['assemblies'][ai]={"name":name,"instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]}
SN='Ball stud on Ø29 plate'
rebuild('Top lid',moving,[stud(f'{SN}, lid, right <1>',Lx,Lz,False),stud(f'{SN}, lid, left <2>',Lx,Lz,True)])
rebuild('Lid frame hardware',fixed,[stud(f'{SN}, frame, right <1>',Bx,Bz,False),stud(f'{SN}, frame, left <2>',Bx,Bz,True)])
# nothing else may use the two studios
for a in d['assemblies']:
    if a['name'] in ('Top lid','Lid frame hardware','Printer'): continue
    assert not any(i.get('studio') in (si,gi) and 'sub' not in i for i in a['instances']), a['name']
T=[a for a in d['assemblies'] if a['name']=='Printer'][0]
inst={i['name']:i for i in T['instances']}; mates={m['name']:m for m in T['mates']}
dx,dz=Bx-Lx,Bz-Lz; n=math.hypot(dx,dz); ux,uz=dx/n,dz/n
for side,left in (('right',False),('left',True)):
    y=2*YC-BY if left else BY
    inst[f'Gas spring body, {side} <1>']['pose']={"r":[ux,0,uz, 0,1,0, -uz,0,ux],"t":[Lx,y,Lz]}
    inst[f'Gas spring rod, {side} <1>']['pose']={"r":[-ux,0,-uz, 0,1,0, uz,0,-ux],"t":[Bx,y,Bz]}
    m=mates[f'Gas spring {side}, lid ball']; m['a']['origin']=[float(Lx),float(y),float(Lz)]; m['b']['x']=[ux,0.0,-uz]
    m=mates[f'Gas spring {side}, frame ball']; m['a']['origin']=[float(Bx),float(y),float(Bz)]; m['b']['x']=[-ux,0.0,uz]
    for k in ('lid ball','frame ball','stroke'): T.get('turns',{}).pop(str(mates[f'Gas spring {side}, {k}']['id']),None)
h=mates['Top lid hinge']; assert h['a']['origin']==[HX,0,HZ] and h['limits']==[0.0,G['OPEN']], h
T.get('turns',{}).pop(str(h['id']),None)
json.dump(d,open(src+'.new','w'))
print(src,'studios',si,gi,'moving',len(moving),'fixed',len(fixed),'spring length closed',round(n,2))
