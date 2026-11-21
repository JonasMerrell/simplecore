# Top lid for the simplecore enclosure: hinged at the back on two printed hinges with 623 bearings, held shut /
# held open by two over-centre gas springs, perimeter hollow silicone seal on the top extrusions, the top PIR
# board carried under the lid, printed handle at the front.
# usage: python3 mklid.py OUTDIR -> OUTDIR/lid_run.json ; rcad run lid_run.json -> lid-doc.json
#        python3 mklid.py OUTDIR print -> OUTDIR/print_run.json ; rcad run print_run.json -> lid-prints.stl
# Order matters: an "add" extrude fuses with every body it touches, and a "remove" cuts every body it crosses,
# so each multi-feature part is finished before its neighbours exist, and the lid panel comes last.
import json, math, sys, os
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
PRINT_ONLY=len(sys.argv)>2 and sys.argv[2]=='print'   # only the printed parts, exported as print/lid-prints.stl for print_files.py
# ---- key numbers (world mm; front = -X, right = -Y) ----
RAIL_TOP=590.2          # top of the top extrusions
SEAL_H=5.0              # hollow D seal, 8 free -> 5 compressed
LID_T=3.0
Z0=RAIL_TOP+SEAL_H      # lid underside 595.2
Z1=Z0+LID_T             # lid top 598.2
HX,HZ=441.0,Z1+0.75     # hinge axis (along Y): x 441, z 598.95
PIR_T=25.4
# gas spring ball centres, closed (from the over-centre search, relative to the hinge axis)
B=(HX-158.5,HZ-75.5)    # on the frame bracket: (282.5, 523.45)
L=(HX-37.5,HZ-60.0)     # on the lid bracket:   (403.5, 538.95)
YC=226.5                # enclosure centre line (side panels' outer faces -27.5 / 480.5)
PANEL_O=-27.5
FB_T=8.0                # frame bracket plate on the panel: y -35.5..-27.5 (studs on both brackets start at y -35.5)
LB_Y=(-35.5,-29.5)      # lid bracket plate, 2 mm off the panel
BALL_Y=-45.0            # ball centres (spring plane), right side
HINGE_Y=(65.0,388.0)    # hinge centres
ARM_T=5.25              # lid arm thickness: its top is level with the top of the pin boss, so it prints top face down
EAR_R=7.0               # hinge ear radius round the 10 mm bearing (the lid's back edge passes at 7.5)
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
def xplane(x,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Right'},'offset':str(round(x,4))})
def poly(pts): return {'type':'polyline','points':[[round(a,4),round(b,4)] for a,b in pts],'closed':True}
def rect(a,b): return {'type':'rect','corner1':[round(v,4) for v in a],'corner2':[round(v,4) for v in b]}
def circ(p,r): return {'type':'circle','center':[round(v,4) for v in p],'radius':r}
def ext(pl,name,items,depth,op='new',opp=False):
    sk=sketch({'kind':'feature_plane','feature':pl},name+' sketch',items)
    return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(depth),'op':op,'opposite':opp})
for k,v in (('lid_t',LID_T),('seal_h',SEAL_H),('lid_pir_t',PIR_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
parts=[]; fillets=[]; late=[]
PRINT='#e07020'; ALU='#5a6470'
pz1=zplane(Z1,'Lid top plane')
# 1 printed hinges: frame block with two ears (a 623 bearing pressed into each from the slot side) on the rear-most
#   top rail, lid arm with a tongue between the ears, M3 x 20 screw through both bearings as the pin
for i,yc in enumerate(HINGE_Y):
    n=i+1
    p=yplane(yc-12,f'Hinge {n} block plane')
    blk=ext(p,f'Hinge {n} frame block',[poly([(HX,HZ+EAR_R),(474.5,600.5),(474.5,RAIL_TOP),(453.0,RAIL_TOP),(HX,HZ-EAR_R)])],24,opp=True)
    ext(p,f'Hinge {n} ears',[circ([HX,HZ],EAR_R)],24,op='add',opp=True)
    ps=yplane(yc-4,f'Hinge {n} slot plane')
    ext(ps,f'Hinge {n} slot for the lid arm',[rect([430.0,588.0],[451.5,610.0])],8,op='remove',opp=True)
    ext(p,f'Hinge {n} pin bore (screw head and nut pockets)',[circ([HX,HZ],3.4)],24,op='remove',opp=True)
    pe=yplane(yc+4,f'Hinge {n} ear face plane')
    ext(pe,f'Hinge {n} bearing pocket +Y',[circ([HX,HZ],5.0)],4,op='remove',opp=True)
    ext(ps,f'Hinge {n} bearing pocket -Y',[circ([HX,HZ],5.0)],4,op='remove')
    pt=zplane(604.0,f'Hinge {n} block top plane')
    ext(pt,f'Hinge {n} M5 counterbore',[circ([464.5,yc],4.75)],8.8,op='remove',opp=True)
    ext(pt,f'Hinge {n} M5 hole',[circ([464.5,yc],2.75)],14,op='remove',opp=True)
    parts.append((blk,f'Lid hinge {n}, frame block (print, ASA)',PRINT))
    arm=ext(pz1,f'Hinge {n} lid arm pad',[rect([420.0,yc-15],[433.5,yc+15])],ARM_T)
    pa=yplane(yc-3.7,f'Hinge {n} tongue plane')
    ext(pa,f'Hinge {n} tongue',[rect([428.0,Z1],[HX,Z1+ARM_T])],7.4,op='add',opp=True)
    ext(pa,f'Hinge {n} tongue boss',[circ([HX,HZ],4.5)],7.4,op='add',opp=True)
    ext(ps,f'Hinge {n} race shoulders',[circ([HX,HZ],2.6)],8,op='add',opp=True)
    ext(ps,f'Hinge {n} M3 pin hole',[circ([HX,HZ],1.6)],8,op='remove',opp=True)
    ext(pz1,f'Hinge {n} lid arm M4 holes',[circ([426.5,yc-10],2.1),circ([426.5,yc+10],2.1)],ARM_T,op='remove')
    parts.append((arm,f'Lid hinge {n}, lid arm (print, ASA)',PRINT))
    late.append((n,yc,ps,pe))
# 2 spring brackets, right side (y<0) and mirrored left side
def side(sgn,tag):
    m=lambda y: y if sgn>0 else 2*YC-y
    # frame bracket: 8 mm plate on the side panel, 2x M5 through the panel into the top side rail's slot (z 580)
    ya,yb=sorted([m(PANEL_O-FB_T),m(PANEL_O)])
    p=yplane(ya,f'Frame spring bracket {tag} plane')
    bx,bz=B
    fb=ext(p,f'Frame spring bracket {tag}',[poly([(bx-21,RAIL_TOP),(bx+21,RAIL_TOP),(bx+21,570.0),(bx+11,bz),(bx-11,bz),(bx-21,570.0)])],FB_T,opp=True)
    ext(p,f'Frame spring bracket {tag} round end',[circ([bx,bz],11.0)],FB_T,op='add',opp=True)
    ext(p,f'Frame spring bracket {tag} holes',[circ([bx-12.5,580.0],2.75),circ([bx+12.5,580.0],2.75),circ([bx,bz],2.5)],FB_T,op='remove',opp=True)
    parts.append((fb,f'Frame spring bracket, {tag} (8 mm 6061, CNC)',ALU))
    ym=(ya+yb)/2
    fillets.append((f'Frame spring bracket {tag} corners',[[bx-21,ym,RAIL_TOP],[bx+21,ym,RAIL_TOP]],5.0))
    fillets.append((f'Frame spring bracket {tag} shoulders',[[bx-21,ym,570.0],[bx+21,ym,570.0]],20.0))
    # lid bracket: 6 mm hanging plate 2 mm off the panel, flange screwed to the lid top (2x M4)
    ya,yb=sorted([m(LB_Y[0]),m(LB_Y[1])])
    p=yplane(ya,f'Lid spring bracket {tag} plane')
    lx,lz=L
    fa,fb2=sorted([m(LB_Y[1]),m(-18.0)])
    lb=ext(pz1,f'Lid spring bracket {tag} flange',[rect([lx-12,fa],[lx+18,fb2])],6.0)
    ext(p,f'Lid spring bracket {tag}',[poly([(lx-12,Z1+6.0),(lx+18,Z1+6.0),(lx+18,572.0),(lx+10,lz),(lx-10,lz),(lx-12,572.0)])],6.0,op='add',opp=True)
    ext(p,f'Lid spring bracket {tag} round end',[circ([lx,lz],10.0)],6.0,op='add',opp=True)
    ext(pz1,f'Lid spring bracket {tag} M4 holes',[circ([lx-3.0,m(-23.0)],2.1),circ([lx+9.0,m(-23.0)],2.1)],6.0,op='remove')
    ext(p,f'Lid spring bracket {tag} ball stud hole',[circ([lx,lz],2.5)],6.0,op='remove',opp=True)
    parts.append((lb,f'Lid spring bracket, {tag} (6 mm 6061, CNC)',ALU))
    ym=(ya+yb)/2
    fillets.append((f'Lid spring bracket {tag} shoulders',[[lx-12,ym,572.0],[lx+18,ym,572.0]],20.0))
side(+1,'right'); side(-1,'left')
# 3 handle at the front, printed arch 110 long with an 80 x 16 finger opening, 2x M4 from under the lid
hd=ext(pz1,'Lid handle',[rect([-8.0,YC-55],[6.0,YC+55])],22)
px=xplane(-8.0,'Handle front plane')
ext(px,'Lid handle finger opening',[rect([YC-40,Z1-1],[YC+40,Z1+15])],14,op='remove')
parts.append((hd,'Lid handle (print, ASA)',PRINT))
fillets.append(('Lid handle top corners',[[-1.0,YC-55,Z1+22],[-1.0,YC+55,Z1+22]],9.0))
fillets.append(('Lid handle opening corners',[[-1.0,YC-40,Z1+15],[-1.0,YC+40,Z1+15]],6.0))
if not PRINT_ONLY:
    # 4 bearings and pins (after the printed parts, so nothing fuses with them)
    for n,yc,ps,pe in late:
        b1=ext(pe,f'Hinge {n} bearing +Y',[circ([HX,HZ],5.0),circ([HX,HZ],1.5)],4,opp=True)
        b2=ext(ps,f'Hinge {n} bearing -Y',[circ([HX,HZ],5.0),circ([HX,HZ],1.5)],4)
        parts.append((b1,f'Lid hinge {n} bearing 623 (3 x 10 x 4), +Y','#c8c8c8')); parts.append((b2,f'Lid hinge {n} bearing 623 (3 x 10 x 4), -Y','#c8c8c8'))
        pp=yplane(yc-11,f'Hinge {n} pin plane')
        pin=ext(pp,f'Hinge {n} pin',[circ([HX,HZ],1.45)],22,opp=True)
        parts.append((pin,f'Lid hinge {n} pin, M3 x 20 screw and locknut','#303030'))
    # 5 seal ring on the top extrusions (centred on each rail, 10 wide, shown compressed)
    pr=zplane(RAIL_TOP,'Rail top plane')
    SEAL=ext(pr,'Lid seal (hollow silicone D, compressed)',[rect([-20.5,-18.5],[419.5,471.5]),rect([-10.5,-8.5],[409.5,461.5])],'seal_h')
    parts.append((SEAL,'Lid seal, hollow silicone D 10 x 8 (shown compressed to 5)','#c03a2b'))
    # 6 lid panel (same footprint as the old top panel, raised by the compressed seal) and the PIR board under it
    pz0=zplane(Z0,'Lid underside plane')
    PIR=ext(pz0,'Lid insulation (25.4 mm PIR)',[rect([-3.5,-1.5],[402.5,454.5])],'lid_pir_t',opp=True)
    parts.append((PIR,'Lid insulation, PIR 25.4 mm (bonded under the lid)','#e2cc78'))
    LID=ext(pz0,'Lid panel (3 mm 6061)',[rect([-25.5,-27.5],[433.5,480.5])],'lid_t')
    parts.append((LID,'Top lid panel (3 mm 6061)','#b0b4ba'))
    fillets.append(('Lid front corners R12',[[-25.5,-27.5,Z0+1.5],[-25.5,480.5,Z0+1.5]],12.0))
# fillets last: one that fails is dropped without shifting the ids above
for name,pts,r in fillets:
    feat('fillet',name,{'edges':[{'kind':'edge','point':[round(v,3) for v in p]} for p in pts],'radius':r})
# part names and colours are set by name_parts.py from the bounding boxes (body ids depend on how adds merge)
if PRINT_ONLY:
    add({'tool':'export','args':{'format':'stl','path':os.path.abspath(os.path.join(OUT,'lid-prints.stl'))}})
    json.dump(S,open(os.path.join(OUT,'print_run.json'),'w'),indent=0); print(len(S),'steps (printed parts only)'); sys.exit()
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
