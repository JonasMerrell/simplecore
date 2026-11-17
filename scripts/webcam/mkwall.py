# Webcam mount for the simplecore printer, right-wall version: bare Logitech C270 board with an M12 wide-angle lens
# (printed "m12_lens_housing_v2" in place of the stock lens holder) in a printed tray with a flat pad that is stuck
# to the inner face of the right upper insulation board with VHB tape, looking across the bed and 45 deg down.
# usage: python3 mkwall.py -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam")
import json, math
TH=45.0                        # tilt below horizontal
WALL_Y=0.9                     # inner face of "PIR right side, upper"
LX,CY,CZ=150.0,15.5,548.0      # lens axis at the board's front face (world); the board's long side runs along +X
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
A=(1.0,0.0,0.0); V=(0.0,c,-s); Wd=(0.0,s,c)       # along the board, view axis, across the board
def P3(x,y,z): return [round(LX*A[i]+(0,CY,CZ)[i]*(i>0)+A[i]*y+V[i]*x+Wd[i]*z,4) for i in range(3)]   # local (view, along, across) -> world
def YZ(x,z): p=P3(x,0,z); return (p[1],p[2])
N=list(V)
# sketch frame rcad picks on faces with normal N (origin = world origin projected on the plane); checked on every run
FX=(-1.0,0.0,0.0); FY=(0.0,s,c)
def SK(y,z,x=0.0):
    p=P3(x,y,z); return [round(sum(p[i]*FX[i] for i in range(3)),4), round(sum(p[i]*FY[i] for i in range(3)),4)]
# camera-local layout: x along the view axis (0 = board front = top of the tray walls), y along the board, z across it
F=0.0
BRD_B=-0.95                      # pocket floor (the board is 0.8 to 1.0 thick)
CAV=BRD_B-2.0; BACK=CAV-2.0      # cavity floor (parts on the back about 1 mm), back of the tray
PY0,PY1=-13.6,45.4               # pocket along the board (board -12.9..45.1 in the STEP, -13.4..44.5 in the scan)
PZ=10.9                          # pocket half width (board 21.0 to 21.2)
WALL=2.5; HZ=14.3; SCR_Z=12.55
Y0,Y1=PY0-WALL,PY1+WALL
BAR_T=2.0
HOUS_Y=7.25; HOUS_Z=10.6; HOUS_H=12.0   # m12_lens_housing_v2: 14.5 along the board, 21.2 across, 12 tall
PAD_T=3.0; PAD_OVER=10.0; PAD_Z0=CZ-16.0; WEB_T=3.0
TOP=YZ(BACK,HZ)                   # top back corner of the tray
S=[{'tool':'new_document','args':{}},{'tool':'switch_part_studio','args':{'index':0}}]
add=S.append
fid=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); fid[0]+=1; return fid[0]
def sketch(plane,name,items):
    add({'tool':'create_sketch','args':{'plane':plane,'name':name}}); fid[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':fid[0],'items':items}}); return fid[0]
def xplane(x,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Right'},'offset':str(round(x,4))})
def poly(pts): return {'type':'polyline','points':[list(p) for p in pts],'closed':True}
def rect(a,b): return {'type':'rect','corner1':list(a),'corner2':list(b)}
def circ(p,r): return {'type':'circle','center':p,'radius':r}
def face(x,y,z): return {'kind':'face','point':P3(x,y,z),'normal':N}
def cut(at,name,items,depth):
    sk=sketch(face(*at),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'remove','opposite':True})
def body(at,name,items,depth):
    sk=sketch(face(*at),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'new'})
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# 1 tray block (constant section along the board)
p=xplane(LX+Y0,'Tray end plane')
sk=sketch({'kind':'feature_plane','feature':p},'Tray profile',[poly([YZ(F,HZ),YZ(F,-HZ),YZ(BACK,-HZ),YZ(BACK,HZ)])])
MOUNT=feat('extrude','Tray block',{'profiles':[{'sketch':sk}],'depth':str(round(Y1-Y0,3)),'op':'new'})
# 2 tape pad against the wall (10 mm longer than the tray at each end) and the top web that ties the tray's top edge to it.
#   The triangle left open behind the tray is the cable channel, open at both ends.
p2=xplane(LX+Y0-PAD_OVER,'Pad end plane')
sk=sketch({'kind':'feature_plane','feature':p2},'Pad profile',[rect((WALL_Y,PAD_Z0),(WALL_Y+PAD_T,TOP[1]))])
feat('extrude','VHB tape pad',{'profiles':[{'sketch':sk}],'depth':str(round(Y1-Y0+2*PAD_OVER,3)),'op':'add'})
sk=sketch({'kind':'feature_plane','feature':p},'Web profile',[rect((WALL_Y+PAD_T-0.5,TOP[1]-WEB_T),(TOP[0],TOP[1]))])
feat('extrude','Top web',{'profiles':[{'sketch':sk}],'depth':str(round(Y1-Y0,3)),'op':'add'})
# 3 board pocket, cavity for the parts on the back, window for the USB connector and cable
W=(F,Y0+1.0,0)   # a point on the end wall's top face, which survives every cut
cut(W,'Board pocket 59 x 21.8',[rect(SK(PY0,-PZ),SK(PY1,PZ))],F-BRD_B)
cut(W,'Cavity behind the board',[rect(SK(PY0+2.0,-PZ),SK(PY1-2.0,PZ))],F-CAV)
cut(W,'USB connector and cable window',[rect(SK(30.5,-PZ),SK(42.5,PZ))],F-BACK+1)
# 4 clamp bar screw pilot holes
BS1=[(-11.0,SCR_Z),(-11.0,-SCR_Z)]; BS2=[(44.2,SCR_Z),(44.2,-SCR_Z)]
cut(W,'Clamp pilot holes (M2 self-tapping)',[circ(SK(y,z),0.85) for y,z in BS1+BS2],BACK*-1-0.8)
# 5 clamp bars (the same two parts as before): hold the board's two ends down
W2=(F,Y1-1.0,0)
B1=body(W,'Clamp bar, lens end',[rect(SK(Y0,-HZ),SK(-HOUS_Y-1.0,HZ))]+[circ(SK(y,z),1.15) for y,z in BS1],BAR_T)
B2=body(W2,'Clamp bar, cable end',[rect(SK(42.9,-HZ),SK(Y1,HZ))]+[circ(SK(y,z),1.15) for y,z in BS2],BAR_T)
# 6 reference bodies: board, M12 lens housing, M12 2.1 mm lens (length and flange estimated from the listing photo)
FL=(BRD_B,PY0+1.0,0)    # the ledge under the board's lens end
BRD=body(FL,'Logitech C270 board 58 x 21 x 0.8',[rect(SK(-12.9,-10.5,BRD_B),SK(45.1,10.5,BRD_B))],0.8)
BT=(BRD_B+0.8,20,0)
HOU=body(BT,'M12 lens housing (m12_lens_housing_v2)',[rect(SK(-HOUS_Y,-HOUS_Z,BRD_B+0.8),SK(HOUS_Y,HOUS_Z,BRD_B+0.8)),circ(SK(0,0,BRD_B+0.8),5.6)],HOUS_H)
LB=body(BT,'M12 lens 2.1 mm, barrel',[circ(SK(0,0,BRD_B+0.8),5.9)],17.0)
LF=body((BRD_B+0.8+17.0,0,0),'M12 lens 2.1 mm, front flange',[circ(SK(0,0,BRD_B+0.8+17.0),9.0)],5.0)
add({'tool':'set_parts','args':{'parts':[
 {'body':[MOUNT,0],'name':'Webcam wall mount (print, ABS/ASA)','color':'#8a9099'},
 {'body':[B1,0],'name':'Webcam clamp bar, lens end (print, ABS/ASA)','color':'#e07020'},
 {'body':[B2,0],'name':'Webcam clamp bar, cable end (print, ABS/ASA)','color':'#e07020'},
 {'body':[BRD,0],'name':'Logitech C270 board (reference)','color':'#1c6e3c'},
 {'body':[HOU,0],'name':'M12 lens housing (reference, printed separately)','color':'#2b5fb3'},
 {'body':[LB,0],'name':'M12 2.1 mm lens barrel (reference)','color':'#101010'},
 {'body':[LF,0],'name':'M12 2.1 mm lens flange (reference)','color':'#181818'}]}})
add({'tool':'describe','args':{}})
add({'tool':'render','args':{'direction':[0.5,-0.6,-0.5],'width':1100,'height':800,'path':'cam_34.png'}})
add({'tool':'render','args':{'direction':[1,0,0],'width':1100,'height':800,'path':'cam_end.png'}})
add({'tool':'render','args':{'direction':[-0.4,0.7,0.5],'width':1100,'height':800,'path':'cam_back.png'}})
add({'tool':'export','args':{'format':'step','path':'webcam-parts.step'}})
add({'tool':'export','args':{'format':'stl','path':'webcam-all.stl'}})
add({'tool':'save_document','args':{'path':'cam-doc.json'}})
json.dump(S,open('cam_run.json','w'),indent=0)
