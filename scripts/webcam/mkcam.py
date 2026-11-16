# Webcam mount for the simplecore printer: bare Logitech C270 board with an M12 wide-angle lens
# (printed "m12_lens_housing_v2" in place of the stock lens holder), in a printed tray hung from the
# bottom slot of the rear top rail, centred, looking forward and down at the bed. It sits in a 108 x 40 opening
# cut in the top edge of the back upper insulation board (see pir_notch.py).
# Board sizes: Jonas's "C270" STEP model and his scan "Logitech C270 Chip v2.0.stl" (2026-11-16); they agree within 1 mm,
# and the pocket takes either.
# usage: python3 mkcam.py  -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam")
import json, math
TH=38.0                        # tilt below horizontal
CX,CY,CZ=412.0,226.5,550.0     # lens axis at the board's front face (world)
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
def L(x,z): return (round(CX-c*x-s*z,4), round(CZ-s*x+c*z,4))   # local (view axis, up-ish) -> world (x,z)
def SK(y,z,x=0.0):                                               # local (y,z) at depth x -> sketch coords on a plane normal to the view axis
    wx,wz=L(x,z); return [round(SX*(CY+y),4), round(SY*(wx*s-wz*c),4)]
def P3(x,y,z): wx,wz=L(x,z); return [wx, CY+y, wz]
N=[-c,0.0,-s]
SX,SY=-1,-1   # signs of the sketch frame rcad picks on faces with normal N (checked against the create_sketch results)
RAIL_Z=570.2; PAD_T=4.0; PAD_Z=RAIL_Z-PAD_T
# camera-local layout: x along the view axis (0 = board front = top of the tray walls), y along the board, z across it
F=0.0
BRD_B=-0.95                      # pocket floor (the board is 0.8 to 1.0 thick)
CAV=BRD_B-2.0; BACK=CAV-2.0      # cavity floor (parts on the back about 1 mm), back of the tray
PY0,PY1=-13.6,45.4               # pocket along the board (board -12.9..45.1 in the STEP, -13.4..44.5 in the scan)
PZ=10.9                          # pocket half width (board 21.0 to 21.2)
WALL=2.5; HZ=14.3; SCR_Z=12.55
Y0,Y1=PY0-WALL,PY1+WALL
EAR=20.0; BAR_T=2.0
HOUS_Y=7.25; HOUS_Z=10.6; HOUS_H=12.0   # m12_lens_housing_v2: 14.5 along the board, 21.2 across, 12 tall
S=[{'tool':'new_document','args':{}},{'tool':'switch_part_studio','args':{'index':0}}]
add=S.append
fid=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); fid[0]+=1; return fid[0]
def sketch(plane,name,items):
    add({'tool':'create_sketch','args':{'plane':plane,'name':name}}); fid[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':fid[0],'items':items}}); return fid[0]
def yplane(y,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Front'},'offset':str(-y)})
def poly(pts): return {'type':'polyline','points':[list(p) for p in pts],'closed':True}
def rect(a,b): return {'type':'rect','corner1':a,'corner2':b}
def circ(p,r): return {'type':'circle','center':p,'radius':r}
def face(x,y,z): return {'kind':'face','point':P3(x,y,z),'normal':N}
def cut(at,name,items,depth):
    sk=sketch(face(*at),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'remove','opposite':True})
def body(at,name,items,depth):
    sk=sketch(face(*at),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'new'})
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# 1 tray block + neck up to the rail
p=yplane(CY+Y0,'Mount side plane')
sk=sketch({'kind':'feature_plane','feature':p},'Block profile',[poly([L(F,HZ),L(F,-HZ),L(BACK,-HZ),L(BACK,6),(421,PAD_Z),(424.5,PAD_Z),(424.5,RAIL_Z),(404.5,RAIL_Z),(404.5,564.0)])])
MOUNT=feat('extrude','Tray block',{'profiles':[{'sketch':sk}],'depth':str(round(Y1-Y0,3)),'op':'new','opposite':True})
# 2 pad ears, one each side, M5 clearance holes (into T-nuts in the rail's bottom slot)
sk=sketch({'kind':'feature_plane','feature':p},'Pad profile',[rect([404.5,PAD_Z],[424.5,RAIL_Z])])
feat('extrude','Rail pad ear (-Y)',{'profiles':[{'sketch':sk}],'depth':str(EAR),'op':'add'})
p2=yplane(CY+Y1,'Mount far side plane')
sk=sketch({'kind':'feature_plane','feature':p2},'Pad profile 2',[rect([404.5,PAD_Z],[424.5,RAIL_Z])])
feat('extrude','Rail pad ear (+Y)',{'profiles':[{'sketch':sk}],'depth':str(EAR),'op':'add','opposite':True})
pt=feat('plane','Pad underside plane',{'base':{'kind':'origin_plane','plane':'Top'},'offset':str(PAD_Z)})
sk=sketch({'kind':'feature_plane','feature':pt},'M5 holes',[circ([414.5,CY+Y0-EAR/2],2.65),circ([414.5,CY+Y1+EAR/2],2.65)])
feat('extrude','M5 clearance holes',{'profiles':[{'sketch':sk}],'depth':'pad_t','op':'remove'})
# 3 board pocket, cavity for the parts on the back, window for the USB connector and cable
W=(F,Y0+1.0,0)   # a point on the end wall's top face, which survives every cut
cut(W,'Board pocket 59 x 21.8',[rect(SK(PY0,-PZ),SK(PY1,PZ))],F-BRD_B)
cut(W,'Cavity behind the board',[rect(SK(PY0+2.0,-PZ),SK(PY1-2.0,PZ))],F-CAV)
cut(W,'USB connector and cable window',[rect(SK(30.5,-PZ),SK(42.5,PZ))],F-BACK+1)
# 4 clamp bar screw pilot holes
BS1=[(-11.0,SCR_Z),(-11.0,-SCR_Z)]; BS2=[(44.2,SCR_Z),(44.2,-SCR_Z)]
cut(W,'Clamp pilot holes (M2 self-tapping)',[circ(SK(y,z),0.85) for y,z in BS1+BS2],BACK*-1-0.8)
# 5 clamp bars (two more printed parts): hold the board's two ends down
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
 {'body':[MOUNT,0],'name':'Webcam mount (print, ASA)','color':'#8a9099'},
 {'body':[B1,0],'name':'Webcam clamp bar, lens end (print, ASA)','color':'#e07020'},
 {'body':[B2,0],'name':'Webcam clamp bar, cable end (print, ASA)','color':'#e07020'},
 {'body':[BRD,0],'name':'Logitech C270 board (reference)','color':'#1c6e3c'},
 {'body':[HOU,0],'name':'M12 lens housing (reference, printed separately)','color':'#2b5fb3'},
 {'body':[LB,0],'name':'M12 2.1 mm lens barrel (reference)','color':'#101010'},
 {'body':[LF,0],'name':'M12 2.1 mm lens flange (reference)','color':'#181818'}]}})
add({'tool':'describe','args':{}})
for v in ('iso_back_right','iso_front_right','iso_front_left'):
    add({'tool':'render','args':{'view':v,'width':1100,'height':800,'path':f'cam_{v}.png'}})
add({'tool':'render','args':{'direction':[-c,0.0,-s],'width':1100,'height':800,'path':'cam_face.png'}})
add({'tool':'render','args':{'direction':[-0.5,-0.7,-0.5],'width':1100,'height':800,'path':'cam_34.png'}})
add({'tool':'save_document','args':{'path':'cam-doc.json'}})
json.dump(S,open('cam_run.json','w'),indent=0)
