#!/usr/bin/env python3
"""Purge bucket + frame cleat for the simplecore printer (world mm, Printer assembly frame).
Writes run.json for `rcad run`; that builds the Part Studio and saves bucket-doc.json. splice.py adds it to the printer.
Both parts print without supports: the bucket upright (open side up), the cleat on its back (rail face down)."""
import json
# --- where things are in the printer (measured from the model) ---
BED_EDGE=382.84      # MIC6 left (+Y) edge
PIR_FACE=452.1       # inner face of the left lower PIR board (top at z 398)
RAIL_FACE=456.5      # inner face of the left mid 2020 (z 401..421, slot centre z 411)
WIPER_Z=394.83       # underside of the gantry's wiper bracket (sweeps y 386.5..436.5)
NOZZLE_Z=401.76
# --- cleat (screwed to the rail, stays on the printer) ---
ZC0,ZC1=401.0,421.0
YC=450.5                     # cleat front face = bucket back face
ZS=411.0                     # screw height = rail slot centre
KX=(122.0,198.0)             # M5 screws
PEGX=(140.0,180.0)           # peg centres
PEGW=10.0                    # peg width
PEGL=5.0                     # peg reach from the cleat face
PEGZ0,PEGZ1=403.0,411.0      # peg underside, and top where it meets the cleat face; the top rises 45 deg away from the rail
# --- bucket ---
X0,X1=110.0,210.0            # along the gap, front to back (purge spot: x 160)
Y0=389.5                     # bed-side wall (6.7 off the bed edge, so the bucket can come 5.3 forward off the pegs)
Y1=YC
ZB,ZR=215.0,390.0            # underside, rim. Underside is above the bed's top at the END_PRINT height (z 186.8)
T=2.4                        # walls and floor
ZW=420.0                     # top of the back wall
WINZ0=399.5                  # window bottom
WINZ1=PEGZ1+T                # window top: sits on the peg's slope with the wall against the cleat face
S=[]; add=S.append
def r(a,b): return {'type':'rect','corner1':[round(a[0],3),round(a[1],3)],'corner2':[round(b[0],3),round(b[1],3)]}
n=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); n[0]+=1; return n[0]
def plane(base,off,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))})
def sketch(pl,name,items):
    add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':pl},'name':name}}); n[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':n[0],'items':items}}); return n[0]
def ex(sid,name,depth,op,opp=False):
    return feat('extrude',name,{'profiles':[{'sketch':sid}],'depth':str(depth),'opposite':opp,'op':op})
def top(z,name,items,exname,depth,op): return ex(sketch(plane('Top',z,name+' plane'),name,items),exname,depth,op)
add({'tool':'new_document','args':{}})
for k,v in (('bucket_len',X1-X0),('bucket_depth',ZR-ZB),('wall',T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# bucket
BODY=top(ZB,'Bucket footprint',[r((X0,Y0),(X1,Y1))],'Bucket body','bucket_depth','new')
top(ZR,'Back wall',[r((X0,Y1-T),(X1,Y1))],'Back wall up to the cleat',ZW-ZR,'add')
top(ZB+T,'Cavity',[r((X0+T,Y0+T),(X1-T,Y1-T))],'Cavity',ZR-ZB-T,'remove')
feat('fillet','Outer corners',{'edges':[{'kind':'edge','point':[X0,Y0,(ZB+ZR)/2]},{'kind':'edge','point':[X1,Y0,(ZB+ZR)/2]}],'radius':'4'})
pw=plane('Front',-(Y1-T),'Back wall inner face')     # Front plane normal is -Y; sketch x = world x, y = world z
ex(sketch(pw,'Hanging windows',[r((px-PEGW/2-0.5,WINZ0),(px+PEGW/2+0.5,WINZ1)) for px in PEGX]),'Windows that hang on the cleat pegs',T+1,'remove',opp=True)
# cleat
CLEAT=top(ZC0,'Cleat footprint',[r((X0,YC),(X1,RAIL_FACE))],'Cleat',ZC1-ZC0,'new')
for i,px in enumerate(PEGX):
    pr=plane('Right',px-PEGW/2,'Peg %d side'%(i+1))  # Right plane: sketch x = world y, y = world z
    ex(sketch(pr,'Peg %d profile'%(i+1),[{'type':'polyline','closed':True,'points':[[YC+0.5,PEGZ0],[YC-PEGL,PEGZ0],[YC-PEGL,PEGZ1+PEGL],[YC+0.5,PEGZ1-0.5]]}]),'Peg %d (top slopes 45 deg toward the rail)'%(i+1),PEGW,'add')
pf=plane('Front',-YC,'Cleat front face')
ex(sketch(pf,'Screw holes',[{'type':'circle','center':[kx,ZS],'radius':2.75} for kx in KX]),'M5 clearance holes',RAIL_FACE-YC+1,'remove',opp=True)
ex(sketch(pf,'Counterbores',[{'type':'circle','center':[kx,ZS],'radius':5.0} for kx in KX]),'Counterbores for M5 button heads',3.0,'remove',opp=True)
add({'tool':'set_part','args':{'body':[BODY,0],'name':'Purge bucket','color':[232,120,32]}})
add({'tool':'set_part','args':{'body':[CLEAT,0],'name':'Purge bucket cleat','color':[40,40,44]}})
add({'tool':'describe','args':{}})
add({'tool':'render','args':{'path':'bucket.png','width':1200,'height':900,'direction':[-1,-0.8,0.7]}})
add({'tool':'render','args':{'path':'bucket-back.png','width':1200,'height':900,'direction':[0.6,1,0.6]}})
add({'tool':'export','args':{'format':'step','path':'purge-bucket-and-cleat.step'}})
add({'tool':'save_document','args':{'path':'bucket-doc.json'}})
json.dump(S,open('run.json','w'),indent=0)
json.dump({'bucket':[BODY,0],'cleat':[CLEAT,0]},open('bodies.json','w'))
