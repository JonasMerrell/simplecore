#!/usr/bin/env python3
"""Purge bucket + frame cleat for the simplecore printer (world mm, Printer assembly frame).
Writes run.json for `rcad run`; that builds the Part Studio and saves bucket-doc.json. splice.py adds it to the printer."""
import json
# --- where things are in the printer (measured from the model) ---
BED_EDGE=382.84      # MIC6 left (+Y) edge
PIR_FACE=452.1       # inner face of the left lower PIR board (top at z 398)
RAIL_FACE=456.5      # inner face of the left mid 2020 (z 401..421, slot centre z 411)
WIPER_Z=394.83       # underside of the gantry's wiper bracket (sweeps y 386.5..436.5)
NOZZLE_Z=401.76
# --- bucket ---
X0,X1=110.0,210.0            # along the gap, front to back (purge spot: x 160)
Y0=387.0                     # bed-side wall (4.2 off the bed edge)
YC=449.5                     # cleat front face
Y1=YC-0.3                    # bucket back face
ZB,ZR=290.0,390.0            # underside, rim
T=2.4                        # walls and floor
# --- cleat (screwed to the rail, stays on the printer) ---
ZC0,ZC1=401.0,421.0
ZS=411.0                     # screw height = rail slot centre
KX=(122.0,198.0)             # M5 screws
SLOT_Y0,SLOT_Y1=452.0,455.0  # slot in the top of the cleat
SLOT_X0,SLOT_X1=136.0,184.0
SLOT_Z=411.0                 # slot floor
# --- hook on the bucket ---
C=0.4                        # clearance around the tongue
ZH=ZC1+0.4                   # underside of the hook bridge
TH=2.6                       # bridge thickness
S=[]; add=S.append
def r(a,b): return {'type':'rect','corner1':[round(a[0],3),round(a[1],3)],'corner2':[round(b[0],3),round(b[1],3)]}
n=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); n[0]+=1; return n[0]
def plane(base,off,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))})
def sketch(pl,name,items):
    add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':pl},'name':name}}); n[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':n[0],'items':items}}); return n[0]
def ex(sid,name,depth,op,opp=False,all_=False):
    p={'sketch':sid}
    if all_: p['all']=True
    return feat('extrude',name,{'profiles':[p],'depth':str(depth),'opposite':opp,'op':op})
def top(z,name,items,exname,depth,op): return ex(sketch(plane('Top',z,name+' plane'),name,items),exname,depth,op)
add({'tool':'new_document','args':{}})
for k,v in (('bucket_len',X1-X0),('bucket_depth',ZR-ZB),('wall',T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# bucket
BODY=top(ZB,'Bucket footprint',[r((X0,Y0),(X1,Y1))],'Bucket body','bucket_depth','new')
top(ZR,'Back wall',[r((X0,Y1-T),(X1,Y1))],'Back wall up past the cleat',ZH+TH-ZR,'add')
top(ZH,'Hook bridge',[r((SLOT_X0+C,Y1-T),(SLOT_X1-C,SLOT_Y1-C))],'Hook bridge over the cleat',TH,'add')
top(SLOT_Z+1,'Hook tongue',[r((SLOT_X0+C,SLOT_Y0+C),(SLOT_X1-C,SLOT_Y1-C))],'Hook tongue (drops into the cleat slot)',ZH-SLOT_Z-1,'add')
top(ZB+T,'Cavity',[r((X0+T,Y0+T),(X1-T,Y1-T))],'Cavity',ZR-ZB-T,'remove')
feat('fillet','Outer corners',{'edges':[{'kind':'edge','point':[X0,Y0,(ZB+ZR)/2]},{'kind':'edge','point':[X1,Y0,(ZB+ZR)/2]}],'radius':'4'})
# cleat
CLEAT=top(ZC0,'Cleat footprint',[r((X0,YC),(X1,RAIL_FACE))],'Cleat',ZC1-ZC0,'new')
top(SLOT_Z,'Cleat slot',[r((SLOT_X0,SLOT_Y0),(SLOT_X1,SLOT_Y1))],'Slot for the bucket hook',ZC1-SLOT_Z,'remove')
pf=plane('Front',-YC,'Cleat front face')     # Front plane normal is -Y; sketch x = world x, y = world z
ex(sketch(pf,'Screw holes',[{'type':'circle','center':[kx,ZS],'radius':2.75} for kx in KX]),'M5 clearance holes',RAIL_FACE-YC+1,'remove',opp=True)
ex(sketch(pf,'Counterbores',[{'type':'circle','center':[kx,ZS],'radius':5.0} for kx in KX]),'Counterbores for M5 button heads',3.0,'remove',opp=True)
add({'tool':'set_part','args':{'body':[BODY,0],'name':'Purge bucket','color':[232,120,32]}})
add({'tool':'set_part','args':{'body':[CLEAT,0],'name':'Purge bucket cleat','color':[40,40,44]}})
add({'tool':'describe','args':{}})
add({'tool':'render','args':{'path':'bucket.png','width':1200,'height':900,'direction':[-1,-0.8,0.7]}})
add({'tool':'render','args':{'path':'bucket-back.png','width':1200,'height':900,'direction':[0.6,1,0.6]}})
add({'tool':'save_document','args':{'path':'bucket-doc.json'}})
json.dump(S,open('run.json','w'),indent=0)
json.dump({'bucket':[BODY,0],'cleat':[CLEAT,0]},open('bodies.json','w'))
