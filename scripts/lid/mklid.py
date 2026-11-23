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
HX,HZ=444.0,Z1+3.75     # hinge axis (along Y): x 444, z 601.95 (10.5 behind the lid's back edge, 3.75 above its top)
PIR_T=25.4
# gas spring ball centres, closed (from the over-centre search, relative to the hinge axis)
B=(151.0,577.0)         # on the frame bracket, level with the top side rail's slot
L=(HX-100.0,HZ-65.0)    # on the lid's spring lever: (344, 536.95), 27 mm in front of the filament tube hole
OPEN=85.0               # the springs are fully extended (250) at 85 deg: that is the open stop
TUBE=(371.5,554.0)      # filament tube hole in the right side panel (Jonas's photos: 36 below the panel top, 62 from its rear edge)
YC=226.5                # enclosure centre line (side panels' outer faces -27.5 / 480.5)
PANEL_O=-27.5
FB_T=13.0               # frame bracket plate on the panel: y -40.5..-27.5, with a 3.2 deep channel over the panel's M5 button heads
LB_Y=(-40.5,-32.5)      # lid spring lever (8 mm plate), 5 mm off the panel: 2.2 mm over the M5 button heads (2.75 high)
BALL_Y=-50.0            # ball centres (spring plane), right side
HINGE_Y=(14.0,439.0)    # hinge centres: at the corners, right beside the spring levers
BOSS_R=5.5              # tongue boss round the pin
ARM_T=HZ-Z1+BOSS_R      # corner arm thickness 9.25: its top is level with the top of the boss, so it prints top face down
EAR_R=9.5               # hinge ear radius: 4.5 mm of plastic round the 10 mm bearing (the lid's back edge passes at 11.1)
TONGUE=6.0              # tongue half width (12 mm tongue)
SLOT=6.3                # slot half width (0.3 mm shoulders each side bear on the bearings' inner races)
EAR_W=10.0              # ear thickness: 4 for the bearing, 6 for the screw head or nut
BLK=SLOT+EAR_W          # block half width 16.3
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
# 1 lid spring levers: 8 mm 6061 plates hanging outside the side panels, bolted sideways (2x M5) to the corner arms.
#   Built first, so the corner arms' features don't fuse with them.
def lever(sgn,tag):
    m=lambda y: y if sgn>0 else 2*YC-y
    ya,yb=sorted([m(LB_Y[0]),m(LB_Y[1])])
    p=yplane(ya,f'Lid spring lever {tag} plane')
    lx,lz=L
    ext(p,f'Lid spring lever {tag}',[poly([(lx-22,Z1+ARM_T),(lx+14,Z1+ARM_T),(lx+14,572.0),(lx+10,lz),(lx-10,lz),(lx-22,572.0)])],8.0,opp=True)
    ext(p,f'Lid spring lever {tag} round end',[circ([lx,lz],10.0)],8.0,op='add',opp=True)
    ext(p,f'Lid spring lever {tag} ball stud hole',[circ([lx,lz],2.5)],8.0,op='remove',opp=True)
    ym=(ya+yb)/2
    fillets.append((f'Lid spring lever {tag} shoulders',[[lx-22,ym,572.0],[lx+14,ym,572.0]],20.0))
if not PRINT_ONLY: lever(+1,'right'); lever(-1,'left')
# 2 frame spring brackets: 10 mm plates on the side panels, 2x M5 through the panel into the top side rail's slot (z 580)
def fbracket(sgn,tag):
    m=lambda y: y if sgn>0 else 2*YC-y
    ya,yb=sorted([m(PANEL_O-FB_T),m(PANEL_O)])
    p=yplane(ya,f'Frame spring bracket {tag} plane')
    bx,bz=B
    ext(p,f'Frame spring bracket {tag}',[rect([bx-30,558.0],[bx+30,RAIL_TOP])],FB_T,opp=True)
    ext(p,f'Frame spring bracket {tag} holes',[circ([bx-20,580.0],2.75),circ([bx+20,580.0],2.75),circ([bx,bz],2.5)],FB_T,op='remove',opp=True)
    pc=yplane(yb-3.2 if sgn>0 else ya,f'Frame spring bracket {tag} channel plane')
    ext(pc,f'Frame spring bracket {tag} channel over the button heads',[rect([bx-30,574.0],[bx+30,586.0])],3.2,op='remove',opp=True)
    ym=(ya+yb)/2
    for cx in (bx-30,bx+30):
        fillets.append((f'Frame spring bracket {tag} corners {cx}',[[cx,ym,RAIL_TOP],[cx,ym,558.0]],6.0))
if not PRINT_ONLY: fbracket(+1,'right'); fbracket(-1,'left')
# 3 printed corner hinges. Frame block on the rear-most top rail (2x M5 into T-nuts) with two ears and a 623 bearing
#   pressed into each from the slot side. Corner arm on the lid: a thick pad over the lid's rear corner (4x M4 outside
#   the seal line) with the tongue that sits between the ears, and the spring lever bolted to its outer side, so the
#   spring force goes lever -> arm -> pin without loading the 3 mm lid. M3 x 25 screw through both bearings as the pin.
PAD_X0=L[0]-22.0; PAD_XM=400.0
for i,yc in enumerate(HINGE_Y):
    n=i+1; sgn=1 if i==0 else -1; tag='right' if i==0 else 'left'
    m=lambda y: y if sgn>0 else 2*YC-y
    p=yplane(yc-BLK,f'Hinge {n} block plane')
    ext(p,f'Hinge {n} frame block',[poly([(HX,HZ+EAR_R),(474.5,604.0),(474.5,RAIL_TOP),(454.5,RAIL_TOP),(HX,HZ-EAR_R)])],2*BLK,opp=True)
    ext(p,f'Hinge {n} ears',[circ([HX,HZ],EAR_R)],2*BLK,op='add',opp=True)
    ps=yplane(yc-SLOT,f'Hinge {n} slot plane')
    ext(ps,f'Hinge {n} slot for the tongue',[rect([430.0,586.0],[HX+BOSS_R+1.5,616.0])],2*SLOT,op='remove',opp=True)
    ext(p,f'Hinge {n} pin bore (screw head and nut pockets)',[circ([HX,HZ],3.4)],2*BLK,op='remove',opp=True)
    pe=yplane(yc+SLOT,f'Hinge {n} ear face plane')
    ext(pe,f'Hinge {n} bearing pocket +Y',[circ([HX,HZ],5.0)],4,op='remove',opp=True)
    ext(ps,f'Hinge {n} bearing pocket -Y',[circ([HX,HZ],5.0)],4,op='remove')
    pt=zplane(608.0,f'Hinge {n} block top plane')
    ext(pt,f'Hinge {n} M5 counterbores',[circ([464.5,yc-9],4.75),circ([464.5,yc+9],4.75)],11.8,op='remove',opp=True)
    ext(pt,f'Hinge {n} M5 holes',[circ([464.5,yc-9],2.75),circ([464.5,yc+9],2.75)],18,op='remove',opp=True)
    y_out=m(LB_Y[1]); y_in=yc+sgn*20.0
    ext(pz1,f'Hinge {n} corner arm pad',[poly([(PAD_X0,y_out),(433.5,y_out),(433.5,y_in),(PAD_XM,y_in),(PAD_XM,m(-8.0)),(PAD_X0,m(-8.0))])],ARM_T)
    pa=yplane(yc-TONGUE,f'Hinge {n} tongue plane')
    ext(pa,f'Hinge {n} tongue',[rect([428.0,Z1],[HX,Z1+ARM_T])],2*TONGUE,op='add',opp=True)
    ext(pa,f'Hinge {n} tongue boss',[circ([HX,HZ],BOSS_R)],2*TONGUE,op='add',opp=True)
    ext(ps,f'Hinge {n} race shoulders',[circ([HX,HZ],2.6)],2*SLOT,op='add',opp=True)
    ext(ps,f'Hinge {n} M3 pin hole',[circ([HX,HZ],1.6)],2*SLOT,op='remove',opp=True)
    ext(pz1,f'Hinge {n} corner arm M4 holes',[circ([426.5,yc+sgn*14],2.1),circ([426.5,yc-sgn*12],2.1),circ([426.5,m(-23.0)],2.1),circ([L[0]+58,m(-23.0)],2.1),circ([L[0]+29,m(-23.0)],2.1),circ([L[0]-4,m(-23.0)],2.1)],ARM_T,op='remove')
    # the lever's two M5 screws: through the lever and 22 mm into the pad, nuts in slots cut from the top
    pl=yplane(min(m(LB_Y[0]),m(LB_Y[0]+31.0)),f'Hinge {n} lever screw plane')
    ext(pl,f'Lever {tag} M5 holes',[circ([L[0]-15,Z1+ARM_T/2],2.75),circ([L[0]+7,Z1+ARM_T/2],2.75)],31.0,op='remove',opp=True)
    pn=zplane(Z1+ARM_T,f'Hinge {n} pad top plane')
    yn=sorted([m(-20.0),m(-15.7)])
    ext(pn,f'Lever {tag} M5 nut slots',[rect([L[0]-15-4.15,yn[0]],[L[0]-15+4.15,yn[1]]),rect([L[0]+7-4.15,yn[0]],[L[0]+7+4.15,yn[1]])],ARM_T/2+4.7,op='remove',opp=True)
    fillets.append((f'Hinge {n} corner arm inner corner',[[PAD_XM,m(-8.0),Z1+ARM_T/2]],10.0))
    fillets.append((f'Hinge {n} corner arm front corners',[[PAD_X0,m(-8.0),Z1+ARM_T/2]],6.0))
    late.append((n,yc,ps,pe))
# 4 handle at the front, printed arch 110 long with an 80 x 16 finger opening, 2x M4 from under the lid
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
        pp=yplane(yc-13.3,f'Hinge {n} pin plane')
        pin=ext(pp,f'Hinge {n} pin',[circ([HX,HZ],1.45)],27.6,opp=True)
        parts.append((pin,f'Lid hinge {n} pin, M3 x 25 screw and locknut','#303030'))
    # filament tube stub where it leaves the right side panel (reference only)
    pt2=yplane(PANEL_O-30.0,'Filament tube plane')
    ext(pt2,'Filament tube (reference)',[circ(list(TUBE),2.0)],30.0,opp=True)
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
add({'tool':'set_parts','args':{'parts':[{'body':[1,0],'name':'Gas spring body, 250 mm / 80 stroke, 80 N (18 lb) (Ø15 tube)','color':'#202020'},{'body':[2,0],'name':'Gas spring rod with ball socket (Ø6 rod)','color':'#c8c8c8'},{'body':[3,0],'name':'Ball stud M6, Ø10 ball','color':'#c8c8c8'}]}})
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':os.path.abspath(os.path.join(OUT,'lid-doc.json'))}})
json.dump(S,open(os.path.join(OUT,'lid_run.json'),'w'),indent=0)
json.dump(dict(B=B,L=L,H=[HX,HZ],BALL_Y=BALL_Y,YC=YC,LB_Y=LB_Y,FB_T=FB_T,PANEL_O=PANEL_O,Z0=Z0,Z1=Z1,PAD_X0=PAD_X0,OPEN=OPEN,TUBE=TUBE,BOSS_R=BOSS_R,EAR_R=EAR_R),open(os.path.join(OUT,'lid_geom.json'),'w'))
print(len(S),'steps')
