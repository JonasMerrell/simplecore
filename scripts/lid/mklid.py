# Top lid for the simplecore enclosure: hinged at the back, held shut / held open by two over-centre gas springs,
# perimeter hollow silicone seal on the top extrusions, the top PIR board carried under the lid.
# usage: python3 mklid.py OUTDIR -> OUTDIR/lid_run.json ; rcad run lid_run.json -> lid-doc.json
import json, math, sys, os
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
# ---- key numbers (world mm; front = -X, right = -Y) ----
RAIL_TOP=590.2          # top of the top extrusions
SEAL_H=5.0              # hollow D seal, 8 free -> 5 compressed
LID_T=3.0
Z0=RAIL_TOP+SEAL_H      # lid underside 595.2
Z1=Z0+LID_T             # lid top 598.2
LEAF_T=1.5
HX,HZ=441.0,Z1+LEAF_T/2 # hinge axis (along Y): x 441, z 598.95
PIR_T=25.4
# gas spring ball centres, closed (from the over-centre search, relative to the hinge axis)
B=(HX-158.5,HZ-75.5)    # on the frame bracket: (282.5, 523.45)
L=(HX-37.5,HZ-60.0)     # on the lid bracket:   (403.5, 538.95)
YC=226.5                # enclosure centre line (side panels' outer faces -27.5 / 480.5)
PANEL_O=-27.5
FB_T=8.0                # frame bracket plate on the panel: y -35.5..-27.5 (studs on both brackets start at y -35.5)
LB_Y=(-35.5,-29.5)      # lid bracket plate, 2 mm off the panel
BALL_Y=-45.0            # ball centres (spring plane), right side
S=[{'tool':'new_document','args':{}},{'tool':'switch_part_studio','args':{'index':0}}]
add=S.append
fid=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); fid[0]+=1; return fid[0]
def sketch(plane,name,items):
    add({'tool':'create_sketch','args':{'plane':plane,'name':name}}); fid[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':fid[0],'items':items}}); return fid[0]
def yplane(y,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Front'},'offset':str(round(-y,4))})
def zplane(z,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Top'},'offset':str(round(z,4))})
def poly(pts): return {'type':'polyline','points':[[round(a,4),round(b,4)] for a,b in pts],'closed':True}
def rect(a,b): return {'type':'rect','corner1':[round(v,4) for v in a],'corner2':[round(v,4) for v in b]}
def circ(p,r): return {'type':'circle','center':[round(v,4) for v in p],'radius':r}
def ext(pl,name,items,depth,op='new',opp=False):
    sk=sketch({'kind':'feature_plane','feature':pl},name+' sketch',items)
    return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(depth),'op':op,'opposite':opp})
for k,v in (('lid_t',LID_T),('seal_h',SEAL_H),('lid_pir_t',PIR_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
parts=[]
# 1 lid panel: same footprint as the old top panel, raised by the compressed seal
pz0=zplane(Z0,'Lid underside plane')
LID=ext(pz0,'Lid panel (3 mm 6061)',[rect([-25.5,-27.5],[433.5,480.5])],'lid_t')
parts.append((LID,'Top lid panel (3 mm 6061)','#b0b4ba'))
# 2 PIR board carried under the lid, 2 mm clear of the top extrusions all round
PIR=ext(pz0,'Lid insulation (25.4 mm PIR)',[rect([-3.5,-1.5],[402.5,454.5])],'lid_pir_t',opp=True)
parts.append((PIR,'Lid insulation, PIR 25.4 mm (bonded under the lid)','#e2cc78'))
# 3 seal ring on the top extrusions (centred on each rail, 10 wide, shown compressed)
pr=zplane(RAIL_TOP,'Rail top plane')
SEAL=ext(pr,'Lid seal (hollow silicone D, compressed)',[rect([-20.5,-18.5],[419.5,471.5]),rect([-10.5,-8.5],[409.5,461.5])],'seal_h')
parts.append((SEAL,'Lid seal, hollow silicone D 10 x 8 (shown compressed to 5)','#c03a2b'))
# 4 hinges: two 50 x 50 x 1.5 stainless butt hinges, flat, barrel at the lid's back edge
HY=[(40.0,90.0),(363.0,413.0)]
for i,(y0,y1) in enumerate(HY):
    p=zplane(Z1,f'Hinge {i+1} leaf plane') if i==0 else p
    lf=ext(p,f'Hinge {i+1} lid leaf',[rect([HX-25.0,y0],[HX-2.6,y1])],LEAF_T)
    parts.append((lf,f'Lid hinge {i+1}, lid leaf','#9aa0a6'))
    ff=ext(p,f'Hinge {i+1} frame leaf',[rect([HX,y0],[HX+25.0,y1])],LEAF_T)
    yp=yplane(y0,f'Hinge {i+1} barrel plane')
    ext(yp,f'Hinge {i+1} barrel',[circ([HX,HZ],2.5)],y1-y0,op='add',opp=True)
    parts.append((ff,f'Lid hinge {i+1}, frame leaf and pin','#9aa0a6'))
    sp=ext(pr,f'Hinge {i+1} spacer block',[rect([454.5,y0],[474.5,y1])],round(Z1-RAIL_TOP,3))
    parts.append((sp,f'Lid hinge {i+1} spacer, 6061 20 x 8 x 50 (on the rear-most top rail)','#8a9099'))
# 5 spring brackets, right side (y<0) and mirrored left side
def side(sgn,tag):
    m=lambda y: y if sgn>0 else 2*YC-y
    # frame bracket: 6 mm plate on the side panel, 2x M5 through the panel into the top side rail's slot (z 580)
    ya,yb=sorted([m(PANEL_O-FB_T),m(PANEL_O)])
    p=yplane(ya,f'Frame spring bracket {tag} plane')
    bx,bz=B
    fb=ext(p,f'Frame spring bracket {tag}',[poly([(bx-20.5,RAIL_TOP),(bx+21.5,RAIL_TOP),(bx+21.5,bz+6.5),(bx+9.5,bz-10.5),(bx-9.5,bz-10.5),(bx-20.5,bz+1.5)])],FB_T,opp=True)
    ext(p,f'Frame spring bracket {tag} M5 holes',[circ([bx-12.5,580.0],2.75),circ([bx+12.5,580.0],2.75),circ([bx,bz],2.5)],FB_T,op='remove',opp=True)
    parts.append((fb,f'Frame spring bracket, {tag} (8 mm 6061, CNC)','#5a6470'))
    # lid bracket: 6 mm hanging plate 2 mm off the panel, flange screwed to the lid top (2x M4)
    ya,yb=sorted([m(LB_Y[0]),m(LB_Y[1])])
    p=yplane(ya,f'Lid spring bracket {tag} plane')
    lx,lz=L
    fa,fb2=sorted([m(LB_Y[1]),m(-20.0)])
    pt=zplane(Z1,f'Lid bracket {tag} flange plane')
    lb=ext(pt,f'Lid spring bracket {tag} flange',[rect([lx-10.5,fa],[lx+19.5,fb2])],6.0)
    ext(p,f'Lid spring bracket {tag}',[poly([(lx-10.5,Z1+6.0),(lx+19.5,Z1+6.0),(lx+19.5,lz+6.0),(lx+9.5,lz-10.0),(lx-10.5,lz-10.0)])],6.0,op='add',opp=True)
    ext(pt,f'Lid spring bracket {tag} M4 holes',[circ([lx-2.0,m(-24.0)],2.0),circ([lx+11.0,m(-24.0)],2.0)],6.0,op='remove')
    ext(p,f'Lid spring bracket {tag} ball stud hole',[circ([lx,lz],2.5)],6.0,op='remove',opp=True)
    parts.append((lb,f'Lid spring bracket, {tag} (6 mm 6061, CNC)','#5a6470'))
side(+1,'right'); side(-1,'left')
add({'tool':'set_parts','args':{'parts':[{'body':[f,0],'name':n,'color':c} for f,n,c in parts]}})
add({'tool':'describe','args':{}})
# second studio: purchased spring hardware (local frames)
add({'tool':'new_part_studio','args':{'name':'Lid gas springs'}})
for f in ('gas_spring_body','gas_spring_rod','ball_stud'):
    add({'tool':'import_file','args':{'path':os.path.abspath(os.path.join(OUT,f+'.step')),'name':f}})
add({'tool':'set_parts','args':{'parts':[{'body':[1,0],'name':'Gas spring body, 150 mm / 50 stroke, 100 N (Ø15 tube)','color':'#202020'},{'body':[2,0],'name':'Gas spring rod with ball socket (Ø6 rod)','color':'#c8c8c8'},{'body':[3,0],'name':'Ball stud M6, Ø10 ball','color':'#c8c8c8'}]}})
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':os.path.abspath(os.path.join(OUT,'lid-doc.json'))}})
json.dump(S,open(os.path.join(OUT,'lid_run.json'),'w'),indent=0)
json.dump(dict(B=B,L=L,H=[HX,HZ],BALL_Y=BALL_Y,YC=YC,LB_Y=LB_Y,FB_T=FB_T,PANEL_O=PANEL_O,Z0=Z0,Z1=Z1),open(os.path.join(OUT,'lid_geom.json'),'w'))
print(len(S),'steps')
