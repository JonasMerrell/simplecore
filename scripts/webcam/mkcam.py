# Webcam mount for the simplecore printer: bare Logitech C270 board (case removed) in a printed tray,
# hung from the bottom slot of the front top rail, centred, looking back and down at the bed.
# Board sizes are from Jonas's 3D scan "Logitech C270 Chip v2.0.stl" (2026-11-16):
#   board 57.96 x 21.19 x 1.0, lens 7.0 from one long... see webcam/README.md.
# usage: python3 mkcam.py  -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam")
import json, math
TH=38.0                       # tilt below horizontal
CX,CY,CZ=-9.0,226.5,548.0     # lens axis where it leaves the bezel front (world)
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
def L(x,z): return (round(CX+c*x+s*z,4), round(CZ-s*x+c*z,4))   # local (view axis, up-ish) -> world (x,z)
def SK(y,z,x=0.0):                                               # local (y,z) at depth x -> sketch coords on a plane normal to the view axis
    wx,wz=L(x,z); return [round(CY+y,4), round(wx*s+wz*c,4)]
def P3(x,y,z): wx,wz=L(x,z); return [wx, CY+y, wz]
N=[c,0.0,-s]
RAIL_Z=570.2; PAD_T=4.0; PAD_Z=RAIL_Z-PAD_T
# camera-local layout (x along the view axis, 0 = bezel front; y along the board's long side; z across it)
BZ_T=1.4; F=-BZ_T                 # bezel thickness; tray front (wall tops)
BRD_F=F-2.8; BRD_B=BRD_F-1.0      # board front and back faces (the bezel sits on the lens holder base, 2.7 above the board)
CAV=BRD_B-2.0; BACK=CAV-2.0       # cavity floor (parts on the back are about 1 mm, screw heads 0.8), back of the tray
BY0,BY1=-13.4,44.5                # board along y (lens centre at 0; USB cable end at +y)
BZ0,BZ1=-10.4,10.7                # board across
CL=0.3; WALL=2.5; HZ=14.5
PY0,PY1=BY0-CL,BY1+CL; PZ0,PZ1=BZ0-CL-0.2,BZ1+CL
Y0,Y1=PY0-WALL,PY1+WALL
EAR=20.0
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
def cut(at,name,items,depth,x=F):
    sk=sketch(face(*at),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'remove','opposite':True})
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# 1 tray block + neck up to the rail
p=yplane(CY+Y0,'Mount side plane')
sk=sketch({'kind':'feature_plane','feature':p},'Block profile',[poly([L(F,HZ),L(F,-HZ),L(BACK,-HZ),L(BACK,6),(-22,PAD_Z),(-25.5,PAD_Z),(-25.5,RAIL_Z),(-5.5,RAIL_Z),(-5.5,564.0)])])
MOUNT=feat('extrude','Tray block',{'profiles':[{'sketch':sk}],'depth':str(round(Y1-Y0,3)),'op':'new','opposite':True})
# 2 pad ears, one each side, 3 M5 clearance holes (into T-nuts in the rail's bottom slot)
sk=sketch({'kind':'feature_plane','feature':p},'Pad profile',[rect([-25.5,PAD_Z],[-5.5,RAIL_Z])])
feat('extrude','Rail pad ear (-Y)',{'profiles':[{'sketch':sk}],'depth':str(EAR),'op':'add'})
p2=yplane(CY+Y1,'Mount far side plane')
sk=sketch({'kind':'feature_plane','feature':p2},'Pad profile 2',[rect([-25.5,PAD_Z],[-5.5,RAIL_Z])])
feat('extrude','Rail pad ear (+Y)',{'profiles':[{'sketch':sk}],'depth':str(EAR),'op':'add','opposite':True})
pt=feat('plane','Pad underside plane',{'base':{'kind':'origin_plane','plane':'Top'},'offset':str(PAD_Z)})
sk=sketch({'kind':'feature_plane','feature':pt},'M5 holes',[circ([-15.5,CY+Y0-EAR/2],2.65),circ([-15.5,CY+Y1+EAR/2],2.65)])
feat('extrude','M5 clearance holes',{'profiles':[{'sketch':sk}],'depth':'pad_t','op':'remove'})
# 3 board pocket, cavity for the parts on the back, window for the USB connector and cable
W=(F,Y0+1.0,0)   # a point on the end wall's top face, which survives every cut
cut(W,'Board pocket 58.6 x 21.9',[rect(SK(PY0,PZ0,F),SK(PY1,PZ1,F))],F-BRD_B)
cut(W,'Cavity behind the board',[rect(SK(PY0+1.9,PZ0,F),SK(PY1-2.0,PZ1,F))],F-CAV)
cut(W,'USB connector and cable window',[rect(SK(30.5,-10.6,F),SK(42.0,-1.0,F))],F-BACK+1)
# 4 lip that holds the cable end of the board
sk=sketch(face(*W),'Lip sketch',[rect(SK(PY1-1.5,-6,F),SK(PY1+0.2,6,F))])
feat('extrude','Board end lip',{'profiles':[{'sketch':sk}],'depth':str(round(F-BRD_F-0.15,3)),'op':'add','opposite':True})
# 5 bezel screw pilot holes
BS=[(-9,12.75),(-9,-12.75),(8,12.75),(8,-12.75)]
cut(W,'Bezel pilot holes (M2 self-tapping)',[circ(SK(y,z,F),0.85) for y,z in BS],6)
# 6 bezel (second printed part): clamps the lens holder base, lens and its two posts stick through
sk=sketch(face(*W),'Bezel outline',[rect(SK(Y0,-HZ,F),SK(11,HZ,F))]+[circ(SK(y,z,F),1.15) for y,z in BS])
BEZ=feat('extrude','Lens bezel',{'profiles':[{'sketch':sk}],'depth':str(BZ_T),'op':'new'})
BF=(0,Y0+1.0,0)
for nm,(y,z,r) in (('Lens opening',(0,0,6.6)),('Lens post opening 1',(0,8.2,2.5)),('Lens post opening 2',(0,-8.2,2.5))):
    sk=sketch(face(*BF),nm+' sketch',[circ(SK(y,z,0),r)])
    feat('extrude',nm,{'profiles':[{'sketch':sk}],'depth':str(BZ_T),'op':'remove','opposite':True})
# 7 reference bodies: the C270 board and lens (simplified from the scan)
sk=sketch(face(BRD_B,PY0+0.9,0),'C270 board outline',[rect(SK(BY0,BZ0,BRD_B),SK(BY1,BZ1,BRD_B))])
BRD=feat('extrude','Logitech C270 board 58 x 21.2 x 1',{'profiles':[{'sketch':sk}],'depth':'1.0','op':'new'})
sk=sketch(face(BRD_F,20,0),'C270 lens outline',[circ(SK(0,0,BRD_F),5.9)])
LENS=feat('extrude','Logitech C270 lens',{'profiles':[{'sketch':sk}],'depth':'7.68','op':'new'})
add({'tool':'set_parts','args':{'parts':[
 {'body':[MOUNT,0],'name':'Webcam mount (print, ASA)','color':'#8a9099'},
 {'body':[BEZ,0],'name':'Webcam lens bezel (print, ASA)','color':'#e07020'},
 {'body':[BRD,0],'name':'Logitech C270 board (reference)','color':'#1c6e3c'},
 {'body':[LENS,0],'name':'Logitech C270 lens (reference)','color':'#101010'}]}})
add({'tool':'describe','args':{}})
for v in ('iso_front_left','iso_back_right','iso_front_right'):
    add({'tool':'render','args':{'view':v,'width':1100,'height':800,'path':f'cam_{v}.png'}})
add({'tool':'render','args':{'direction':[c,0.0,-s],'width':1100,'height':800,'path':'cam_face.png'}})
add({'tool':'render','args':{'direction':[-c,0.0,s],'width':1100,'height':800,'path':'cam_fromlens.png'}})
add({'tool':'save_document','args':{'path':'cam-doc.json'}})
json.dump(S,open('cam_run.json','w'),indent=0)
