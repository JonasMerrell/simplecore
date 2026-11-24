#!/usr/bin/env python3
"""Inline holder for the BTT SFS V2.0 filament sensor on the Trad Rack's 2020 extrusion (world mm, Printer frame).
Writes run.json for `cad-app run`; that builds the Part Studio and saves sfs-doc.json. splice.py adds it to the printer.

Where: on the extrusion's top face, motor side of the chain anchor, where the shared bowden leaves the cable
chain's fixed end (all 8 lanes have merged there). Nothing moves: the selector carriage runs on the rail side
(Trad Rack y >= -18), the chain's fixed run never reaches past the anchor toward the motor.
Trad Rack frame (studio 'Trad Rack') -> world: x_w = 166.7 - x, y_w = -87.1 - y, z_w = 311.5 + z (pose diag(-1,-1,1)).
Measured in the Trad Rack STEP (scripts/sfs/step_bboxes.py, MODE=1): extrusion y -48.04..-28.04, top face z 31.5,
slot centre y -38.04; chain anchor x 8.97..38.97, y -55.04..-45.04; bowden leaves the chain's fixed end at about
x 21, y -41, z 58.5, heading -x; carriage parts above z 31.5 stay at y >= -17.94; Motor Mount Lower starts at x -98.9.
SFS V2.0 (BTT manual + 'SFS V2.0 Model.STEP'): body 53.1 long x 27.3 wide x 28.8 high (30.3 with the button), M3
heat-set inserts in the bottom face: two 12.4 apart across the filament at +12.27 from the body centre along it,
one at -12.48 (24.75 pitch); filament axis 15.2 above the bottom face, 12.5 / 14.79 from the long sides.
Print: plate face down, no supports, no brim. Hardware: 3x M3x10 SHCS (SFS), 2x M5x10 SHCS + M5 T-nuts (extrusion)."""
import json,sys
PRINT='print' in sys.argv[1:]   # print-only build: just the holder, exported as STL/STEP
TX,TY,TZ=166.7,-87.1,311.5
def W(x,y,z=0): return (TX-x,TY-y,TZ+z)          # Trad Rack frame -> world
# --- Trad Rack frame numbers ---
SLOT_Y=-38.04; TOP_Z=31.5
PL_X=(-96.5,-2.0)            # plate along the extrusion (M5 screws 16 past each end of the SFS body, clear of its fittings)
PL_Y=(-53.5,-24.8)           # 6.1 from the side panel, 6.9 from the carriage's path
PL_T=5.0                     # plate thickness
SFS_L,SFS_W,SFS_H=53.1,27.3,28.8
AX_UP=15.2                   # filament axis above the SFS bottom face
SIDE_PANEL=14.79             # axis to the long side that faces the panel (-y); 12.5 to the other
BODY_X=(-76.0,-76.0+SFS_L)   # SFS body along the extrusion
PAD=6.0                      # raised seat under the SFS: its axis then sits level with the chain's bowden exit (z 58.5)
SEAT_Z=TOP_Z+PL_T+PAD        # SFS bottom face (Trad Rack z 42.5 -> axis z 57.7)
M5X=(BODY_X[0]-16.0,BODY_X[1]+16.0)
XC=(BODY_X[0]+BODY_X[1])/2
HOLES=[(XC+12.27,SLOT_Y-6.74),(XC+12.27,SLOT_Y+5.66),(XC-12.48,SLOT_Y-6.74)]   # M3, SFS inserts
CB_DEPTH=5.0                 # M3 head counterbore from below: leaves 6 mm under the SFS, so M3x10 takes 4 mm of insert
# --- to world ---
def wrect(x0,x1,y0,y1):
    a=W(x0,y0); b=W(x1,y1)
    return {'type':'rect','corner1':[round(min(a[0],b[0]),3),round(min(a[1],b[1]),3)],'corner2':[round(max(a[0],b[0]),3),round(max(a[1],b[1]),3)]}
def wcirc(x,y,r): p=W(x,y); return {'type':'circle','center':[round(p[0],3),round(p[1],3)],'radius':r}
S=[]; add=S.append; n=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); n[0]+=1; return n[0]
def plane(base,off,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))})
def sketch(pl,name,items):
    add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':pl},'name':name}}); n[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':n[0],'items':items}}); return n[0]
def ex(sid,name,depth,op,opp=False):
    return feat('extrude',name,{'profiles':[{'sketch':sid}],'depth':str(depth),'opposite':opp,'op':op})
def top(z,name,items,exname,depth,op,opp=False): return ex(sketch(plane('Top',TZ+z,name+' plane'),name,items),exname,depth,op,opp)
add({'tool':'new_document','args':{}})
for k,v in (('plate_t',PL_T),('seat_pad',PAD)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
SFS_Y=(SLOT_Y-SIDE_PANEL,SLOT_Y+(SFS_W-SIDE_PANEL))      # body across the extrusion (axis over the slot)
PLATE=top(TOP_Z,'Plate footprint',[wrect(*PL_X,*PL_Y)],'Plate on the extrusion top face','plate_t','new')
top(TOP_Z+PL_T,'Seat',[wrect(*BODY_X,*SFS_Y)],'Raised seat under the SFS','seat_pad','add')
top(TOP_Z,'M5 holes',[wcirc(x,SLOT_Y,2.75) for x in M5X],'M5 clearance holes (T-nuts in the top slot)',PL_T+1,'remove')
top(TOP_Z,'M3 holes',[wcirc(x,y,1.7) for x,y in HOLES],'M3 clearance holes to the SFS inserts',PL_T+PAD+1,'remove')
top(TOP_Z,'M3 counterbores',[wcirc(x,y,3.0) for x,y in HOLES],'Counterbores for M3 heads (from below)',CB_DEPTH,'remove')
top(TOP_Z+PL_T,'Tie slots',[wrect(BODY_X[0]-9.0,BODY_X[0]-5.0,PL_Y[0]+2.0,PL_Y[0]+9.0),wrect(BODY_X[1]+5.0,BODY_X[1]+9.0,PL_Y[0]+2.0,PL_Y[0]+9.0)],
    'Cable-tie slots for the sensor lead',PL_T+1,'remove',opp=True)
# chamfer the plate's top edges along the extrusion a little (handling, and the carriage side)
if PRINT:
    add({'tool':'set_part','args':{'body':[PLATE,0],'name':'SFS V2 holder (Trad Rack)','color':[232,120,32]}})
    add({'tool':'export','args':{'format':'stl','path':'sfs-v2-holder.stl'}})
    add({'tool':'export','args':{'format':'step','path':'sfs-v2-holder.step'}})
    json.dump(S,open('run-print.json','w'),indent=0); sys.exit(0)
# reference body: the SFS V2.0 as a block with its two push-fit fittings (not printed)
REF=top(SEAT_Z,'SFS body',[wrect(*BODY_X,*SFS_Y)],'BTT SFS V2.0 (bought)',SFS_H,'new')
pl=plane('Right',TX-BODY_X[1],'SFS end (anchor side)')    # Right plane normal +X: sketch x = world y, y = world z
ax=W(0,SLOT_Y,SEAT_Z+AX_UP)
FIT=ex(sketch(pl,'Fitting anchor side',[{'type':'circle','center':[round(ax[1],3),round(ax[2],3)],'radius':5.0}]),'Push-fit fitting (anchor side)',13.0,'new',opp=True)
pl2=plane('Right',TX-BODY_X[0],'SFS end (motor side)')
FIT2=ex(sketch(pl2,'Fitting motor side',[{'type':'circle','center':[round(ax[1],3),round(ax[2],3)],'radius':5.0}]),'Push-fit fitting (motor side)',13.0,'new')
add({'tool':'set_part','args':{'body':[PLATE,0],'name':'SFS V2 holder (Trad Rack)','color':[232,120,32]}})
add({'tool':'set_part','args':{'body':[REF,0],'name':'BTT SFS V2.0 filament sensor','color':[30,30,34]}})
add({'tool':'set_part','args':{'body':[FIT,0],'name':'SFS push-fit (anchor side)','color':[190,190,195]}})
add({'tool':'set_part','args':{'body':[FIT2,0],'name':'SFS push-fit (motor side)','color':[190,190,195]}})
add({'tool':'describe','args':{}})
add({'tool':'printability','args':{}})
add({'tool':'render','args':{'path':'sfs-holder.png','width':1200,'height':900,'direction':[-0.7,0.9,0.8]}})
add({'tool':'render','args':{'path':'sfs-holder-below.png','width':1200,'height':900,'direction':[-0.5,0.6,-0.8]}})
add({'tool':'save_document','args':{'path':'sfs-doc.json'}})
json.dump(S,open('run.json','w'),indent=0)
json.dump({'holder':[PLATE,0],'sfs':[REF,0],'fit1':[FIT,0],'fit2':[FIT2,0]},open('bodies.json','w'))
print('axis world',[round(v,2) for v in ax],'plate world x',W(PL_X[1],0)[0],W(PL_X[0],0)[0])
