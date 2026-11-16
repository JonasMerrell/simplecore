# Webcam mount for the simplecore printer: 3DO Enclosure Camera V2.5 (9x9 mm sensor + 30x15 mm USB DSP board, 5 cm FPC)
# hung from the bottom slot of the front top rail, centred, looking back and down at the bed.
# usage: python3 mkcam.py  -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam")
import json, math
TH=38.0                       # tilt below horizontal
CX,CY,CZ=-7.0,226.5,546.5     # lens centre on the mount's front face (world)
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
def L(x,z): return (round(CX+c*x+s*z,4), round(CZ-s*x+c*z,4))   # local (view axis, up-ish) -> world (x,z)
def SK(y,z,x=0.0):                                               # local (y,z) at depth x -> sketch coords on a plane normal to the view axis
    wx,wz=L(x,z); return [round(CY+y,4), round(wx*s+wz*c,4)]
def P3(x,y,z): wx,wz=L(x,z); return [wx, CY+y, wz]
N=[c,0.0,-s]
RAIL_Z=570.2; PAD_T=4.0; PAD_Z=RAIL_Z-PAD_T
BLK_D=14.0; BLK_H=9.0; BLK_W=20.0          # block: depth, half height, half width
POCKET=4.75; SENS=4.65; CHAN_D=6.3; CHAN_H=3.5
WING_Y1=58.0; PL_F=-10.9; PL_T=2.5; BOSS=2.5; DSP_Y0=41.5; DSP_HZ=15.0
EAR=52.0
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
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# 1 block + neck up to the rail
p=yplane(CY-BLK_W,'Mount side plane')
A=L(0,BLK_H); B=L(0,-BLK_H); C=L(-BLK_D,-BLK_H)
sk=sketch({'kind':'feature_plane','feature':p},'Block profile',[poly([A,B,C,(C[0],PAD_Z),(-25.5,PAD_Z),(-25.5,RAIL_Z),(-5.5,RAIL_Z),(-5.5,564.0)])])
feat('extrude','Camera block',{'profiles':[{'sketch':sk}],'depth':str(2*BLK_W),'op':'new','opposite':True})
# 2 pad ear with two M5 holes
sk=sketch({'kind':'feature_plane','feature':p},'Pad profile',[rect([-25.5,PAD_Z],[-5.5,RAIL_Z])])
feat('extrude','Rail pad',{'profiles':[{'sketch':sk}],'depth':str(EAR-BLK_W),'op':'add'})
# 3 wing plate for the DSP board
p2=yplane(CY+BLK_W,'Wing plane')
sk=sketch({'kind':'feature_plane','feature':p2},'Wing profile',[poly([L(PL_F-PL_T,-DSP_HZ-.5),L(PL_F,-DSP_HZ-.5),L(PL_F,DSP_HZ+.5),L(PL_F-PL_T,DSP_HZ+.5)])])
feat('extrude','DSP board plate',{'profiles':[{'sketch':sk}],'depth':str(WING_Y1-BLK_W),'op':'add','opposite':True})

# 4 M5 clearance holes in the pad ear (into T-nuts in the rail's bottom slot)
pt=feat('plane','Pad underside plane',{'base':{'kind':'origin_plane','plane':'Top'},'offset':str(PAD_Z)})
sk=sketch({'kind':'feature_plane','feature':pt},'M5 holes',[circ([-15.5,CY-EAR+7],2.65),circ([-15.5,CY-BLK_W-7],2.65)])
feat('extrude','M5 clearance holes',{'profiles':[{'sketch':sk}],'depth':'pad_t','op':'remove'})
# 5 bosses + pilot holes for the DSP board (holes 26 x 11)
HY=[DSP_Y0+2, DSP_Y0+13]; HZ=[-13,13]
sk=sketch(face(PL_F,BLK_W+5,0),'DSP bosses',[circ(SK(y,z,PL_F),2.5) for y in HY for z in HZ])
feat('extrude','DSP bosses',{'profiles':[{'sketch':sk}],'depth':str(BOSS),'op':'add'})
sk=sketch(face(PL_F+BOSS,HY[0],HZ[0]),'DSP pilot holes',[circ(SK(y,z,PL_F+BOSS),0.85) for y in HY for z in HZ])
feat('extrude','DSP pilot holes (M2 self-tapping)',{'profiles':[{'sketch':sk}],'depth':str(BOSS+PL_T),'op':'remove','opposite':True})
# 6 sensor pocket, 7 FPC channel out of the +Y side
sk=sketch(face(0,-12,0),'Sensor pocket',[rect(SK(-SENS,-SENS),SK(SENS,SENS))])
feat('extrude','Sensor pocket 9.3 x 9.3',{'profiles':[{'sketch':sk}],'depth':str(POCKET),'op':'remove','opposite':True})
sk=sketch(face(0,-12,0),'FPC channel',[rect(SK(-SENS,-CHAN_H),SK(BLK_W+1,CHAN_H))])
feat('extrude','FPC channel',{'profiles':[{'sketch':sk}],'depth':str(CHAN_D),'op':'remove','opposite':True})
# 8 bezel screw pilot holes
BZ=[(-10,0),(10,6.5),(10,-6.5)]
sk=sketch(face(0,-12,0),'Bezel pilot holes',[circ(SK(y,z),0.85) for y,z in BZ])
feat('extrude','Bezel pilot holes (M2 self-tapping)',{'profiles':[{'sketch':sk}],'depth':'6','op':'remove','opposite':True})
# 9 bezel (second printed part)
sk=sketch(face(0,-12,0),'Bezel outline',[rect(SK(-15,-BLK_H),SK(BLK_W,BLK_H)),circ(SK(0,0),3.6)]+[circ(SK(y,z),1.15) for y,z in BZ])
feat('extrude','Lens bezel',{'profiles':[{'sketch':sk}],'depth':'1.2','op':'new'})
# 10 reference bodies: camera sensor module and DSP board (3DO Enclosure Camera V2.5, sizes from 3DO's tolerances.pdf / EC_V2.5.step)
sk=sketch(face(-POCKET,0,4.2),'Lens outline',[circ(SK(0,0,-POCKET),3.225)])
feat('extrude','3DO lens',{'profiles':[{'sketch':sk}],'depth':'6.7','op':'new'})
sk=sketch(face(-POCKET,0,4.2),'Sensor module outline',[rect(SK(-4.5,-4.5,-POCKET),SK(4.5,4.5,-POCKET))])
feat('extrude','3DO sensor module 9 x 9',{'profiles':[{'sketch':sk}],'depth':'4.7','op':'new'})
sk=sketch(face(PL_F+BOSS,HY[0]+1.7,HZ[0]),'DSP board outline',[rect(SK(DSP_Y0,-15,PL_F+BOSS),SK(DSP_Y0+15,15,PL_F+BOSS))])
feat('extrude','3DO USB DSP board 30 x 15',{'profiles':[{'sketch':sk}],'depth':'1.6','op':'new'})
add({'tool':'set_parts','args':{'parts':[
 {'body':[3,0],'name':'Webcam mount (print, ASA)','color':'#8a9099'},
 {'body':[23,0],'name':'Webcam lens bezel (print, ASA)','color':'#e07020'},
 {'body':[25,0],'name':'3DO Enclosure Camera V2.5 lens (reference)','color':'#101010'},
 {'body':[27,0],'name':'3DO Enclosure Camera V2.5 sensor (reference)','color':'#1c6e3c'},
 {'body':[29,0],'name':'3DO USB camera DSP board (reference)','color':'#1c6e3c'}]}})
add({'tool':'describe','args':{}})

for v in ('iso_front_left','iso_back_right','iso_front_right','front','right'):
    add({'tool':'render','args':{'view':v,'width':1100,'height':800,'path':f'cam_{v}.png'}})
add({'tool':'save_document','args':{'path':'cam-doc.json'}})
json.dump(S,open('cam_run.json','w'),indent=0)
