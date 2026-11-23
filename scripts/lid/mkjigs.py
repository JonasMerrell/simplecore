# Printed drilling jigs for the top lid (right-hand versions; jig_files.py mirrors them for the left side).
#   lid corner jig:   hooks over the lid's rear corner (rear and side edge), 6 guide holes for the corner arm's M4 screws
#   handle jig:       hooks over the lid's front edge, centre sight slot, 2 guide holes for the handle's M4 screws
#   side panel jig:   hooks over the side panel's top and front edge, channel over the M5 button heads,
#                     2 guide holes for the frame spring bracket's M5 screws (into the top side rail's slot, z 580)
# All guide holes are 3.4 mm for a 3.3 mm pilot drill (also the M4 tap drill); open up afterwards.
# usage: python3 mkjigs.py OUTDIR -> OUTDIR/jigs_run.json ; rcad run jigs_run.json -> lid-jigs.stl, lid-drill-jigs.json, jigs.png
import json, sys, os
OUT=sys.argv[1] if len(sys.argv)>1 else '.'
Z1=598.2; RAIL_TOP=590.2; YC=226.5; PANEL_O=-27.5
HX=444.0; L=(HX-100.0,0); B=(151.0,577.0); HINGE_Y=14.0
T=8.0; LIP=4.0; LIP_D=2.8; G=1.7      # plate thickness, lip thickness, lip depth below the lid's top face, guide hole radius
S=[{'tool':'new_document','args':{}},{'tool':'switch_part_studio','args':{'index':0}}]
add=S.append; fid=[0]
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
pz=zplane(Z1,'Lid top plane'); pl=zplane(Z1-LIP_D,'Lip bottom plane')
# 1 lid corner jig (right rear corner; lid edges at x 433.5 and y -27.5)
X0=L[0]-28.0
ext(pz,'Corner jig plate',[poly([(X0,PANEL_O),(433.5,PANEL_O),(433.5,HINGE_Y+26),(396.0,HINGE_Y+26),(396.0,-4.0),(X0,-4.0)])],T)
ext(pl,'Corner jig rear lip',[rect([433.5,PANEL_O-LIP],[433.5+LIP,HINGE_Y+26])],T+LIP_D,op='add')
ext(pl,'Corner jig side lip',[rect([X0,PANEL_O-LIP],[433.5,PANEL_O])],T+LIP_D,op='add')
ext(pz,'Corner jig guide holes',[circ(p,G) for p in ((426.5,HINGE_Y+14),(426.5,HINGE_Y-12),(426.5,-23.0),(L[0]+58,-23.0),(L[0]+29,-23.0),(L[0]-4,-23.0))],T,op='remove')
ext(pl,'Corner jig corner relief',[circ((433.5,PANEL_O),1.5)],T+LIP_D,op='remove')
# 2 handle jig (front edge x -25.5; handle screws at x -1, y centre +-47.5)
ext(pz,'Handle jig plate',[rect([-25.5,YC-60],[12.0,YC+60])],T)
ext(pl,'Handle jig front lip',[rect([-25.5-LIP,YC-60],[-25.5,YC+60])],T+LIP_D,op='add')
ext(pz,'Handle jig guide holes',[circ((-1.0,YC-47.5),G),circ((-1.0,YC+47.5),G)],T,op='remove')
ext(pz,'Handle jig centre sight slot',[rect([2.0,YC-0.6],[12.0,YC+0.6]),rect([-18.0,YC-25],[4.0-8.0,YC+25])],T,op='remove')
# 3 side panel jig (right panel outer face y -27.5, top edge z 590.2, front edge x -25.5)
JT=12.0; ya=PANEL_O-JT
py=yplane(ya,'Panel jig outer plane')
ext(py,'Panel jig plate',[rect([-25.5,562.0],[B[0]+34,RAIL_TOP])],JT,opp=True)
ext(py,'Panel jig top lip',[rect([-25.5,RAIL_TOP],[B[0]+34,RAIL_TOP+LIP])],JT+5.0,op='add',opp=True)
ext(py,'Panel jig front lip',[rect([-25.5-LIP,562.0],[-25.5,RAIL_TOP+LIP])],JT+3.0,op='add',opp=True)
ext(py,'Panel jig guide holes',[circ((B[0]-20,580.0),G),circ((B[0]+20,580.0),G)],JT,op='remove',opp=True)
pc=yplane(PANEL_O-3.2,'Panel jig channel plane')
ext(pc,'Panel jig channel over the button heads',[rect([-25.5,574.0],[B[0]+34,586.0])],3.2,op='remove',opp=True)
ext(py,'Panel jig lightening windows',[rect([0.0,566.0],[50.0,571.0]),rect([60.0,566.0],[110.0,571.0])],JT,op='remove',opp=True)
add({'tool':'describe','args':{}})
add({'tool':'export','args':{'format':'stl','path':os.path.abspath(os.path.join(OUT,'lid-jigs.stl'))}})
add({'tool':'render','args':{'direction':[-0.45,-0.7,0.55],'width':1400,'height':900,'path':os.path.abspath(os.path.join(OUT,'jigs.png'))}})
add({'tool':'save_document','args':{'path':os.path.abspath(os.path.join(OUT,'lid-drill-jigs.json'))}})
json.dump(S,open(os.path.join(OUT,'jigs_run.json'),'w'),indent=0); print(len(S),'steps')
