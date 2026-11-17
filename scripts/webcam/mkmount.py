# Webcam mount for the simplecore printer, one piece with the M12 lens holder: a tape pad on the aluminium right side
# panel carries the lens holder (Jonas's "m12_lens_housing_v2") at 45 deg down. The bare Logitech C270 board screws
# to the back of the holder with the stock lens holder's two screws. No tray and no clamp bars.
# usage: python3 mkmount.py -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam"),
#        mount-body.stl (the mount without the holder; fuse_holder.py unions the real holder mesh into it for printing)
import json, math
TH=45.0                        # tilt below horizontal (steeper cuts off the bed's far edge, see webcam/README.md)
WALL_Y=-24.5                   # inner face of the aluminium right side panel (Jonas's printer has no upper side insulation)
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
LX,CZ=191.2,548.0              # lens axis: world x (bed centre) and z where it crosses local x = 0
CY=round(WALL_Y+1.0+c*4.95+s*14.3,3)
A=(1.0,0.0,0.0); V=(0.0,c,-s); Wd=(0.0,s,c)       # along the board, view axis, across the board
def P3(x,y,z): return [round((LX,CY,CZ)[i]+A[i]*y+V[i]*x+Wd[i]*z,4) for i in range(3)]   # local (view, along, across) -> world
def YZ(x,z): p=P3(x,0,z); return (p[1],p[2])
# camera-local: x along the view axis, y along the board (world X), z across the board
BF=-0.15                       # board front face = back face of the lens holder
HT=BF+3.99; HF=BF+12.01        # top of the holder's flange, front of the holder (the face that lies on the print bed)
HY=7.24; HZ=10.58              # holder half sizes: along the board, across it
SCREW_Z=8.6                    # the holder's two screw slots (board screws, from the back)
PAD_T=3.0; PAD_HALF=35.0; PADM=WALL_Y+2.0     # PADM: a plane 1 mm inside the pad, where the ribs end
def xp(z,yw=PADM): return (yw-CY-s*z)/c          # local x where the line z=const meets the plane world y = yw
def zp(x,yw=PADM): return (yw-CY-c*x)/s
def wz_bed(yw): return P3(HF,0,zp(HF,yw))[2]    # world z where the print-bed plane (x = HF) meets world y = yw
# sketch frames rcad picks on faces normal to the view axis (origin = world origin projected); asserted by check_frames.py
FR={ 1:((-1.0,0.0,0.0),(0.0,s,c)), -1:((1.0,0.0,0.0),(0.0,s,c)) }
def SK(y,z,x=0.0,side=1):
    p=P3(x,y,z); fx,fy=FR[side]; return [round(sum(p[i]*fx[i] for i in range(3)),4), round(sum(p[i]*fy[i] for i in range(3)),4)]
S=[{'tool':'new_document','args':{}},{'tool':'switch_part_studio','args':{'index':0}}]
add=S.append
fid=[0]
def feat(kind,name,params):
    add({'tool':'add_feature','args':{'kind':kind,'name':name,'params':params}}); fid[0]+=1; return fid[0]
def sketch(plane,name,items):
    add({'tool':'create_sketch','args':{'plane':plane,'name':name}}); fid[0]+=1
    add({'tool':'sketch_add','args':{'sketch_id':fid[0],'items':items}}); return fid[0]
def xplane(x,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Right'},'offset':str(round(x,4))})
def poly(pts): return {'type':'polyline','points':[[round(a,4),round(b,4)] for a,b in pts],'closed':True}
def circ(p,r): return {'type':'circle','center':p,'radius':r}
def rect(a,b): return {'type':'rect','corner1':list(a),'corner2':list(b)}
def face(x,y,z,side=1): return {'kind':'face','point':P3(x,y,z),'normal':[side*V[0],side*V[1],side*V[2]]}
def prism(plane,name,pts,depth,op='add'):
    sk=sketch({'kind':'feature_plane','feature':plane},name+' profile',[poly(pts)])
    return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':op})
SB=YZ(0.0,13.3); ST=math.tan(math.radians(10.0)); SL=SB[0]-PADM    # strut: starts inside the upper cheek, rises 10 deg toward the pad
PAD_TOP=round(SB[1]+3.0+SL*ST,1)
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# 1 tape pad on the panel. Its lower edge is cut along the print-bed plane so it stands on the bed when printing.
pp=xplane(LX-PAD_HALF,'Pad end plane')
MOUNT=prism(pp,'VHB tape pad',[(WALL_Y,wz_bed(WALL_Y)),(WALL_Y+PAD_T,wz_bed(WALL_Y+PAD_T)),(WALL_Y+PAD_T,PAD_TOP),(WALL_Y,PAD_TOP)],2*PAD_HALF,'new')
# 2 lower rib: from the holder's lower side to the pad, outside the board's lower edge
pr=xplane(LX-HY,'Rib end plane')
prism(pr,'Lower rib',[YZ(HF,-7.0),YZ(HT,-7.0),YZ(HT,-10.2),YZ(BF,-10.2),YZ(BF,-10.9),YZ(xp(-10.9),-10.9),YZ(HF,zp(HF))],2*HY)
# 3 upper cheek on the holder's upper side, outside the board's upper edge, and the strut from it to the pad
prism(pr,'Upper cheek',[YZ(HF,7.0),YZ(HT,7.0),YZ(HT,10.2),YZ(BF,10.2),YZ(BF,10.9),YZ(-3.0,10.9),YZ(-3.0,15.5),YZ(HF,15.5)],2*HY)
# (the sketch for step 4 sits on the cheek's back face, so it comes before the strut that covers that face)
ska=sketch(face(-3.0,0.0,13.0,-1),'Screw access sketch',[circ(SK(0,SCREW_Z,-3.0,-1),2.6),circ(SK(0,-SCREW_Z,-3.0,-1),2.6)])
prism(pr,'Upper strut (rises 10 deg toward the pad)',[SB,(SB[0],SB[1]+3.0),(PADM,SB[1]+3.0+SL*ST),(PADM,SB[1]+SL*ST)],2*HY)
# 4 screwdriver access to the two board screws, straight back along the view axis: through the strut and through the pad
feat('extrude','Screw access holes',{'profiles':[{'sketch':ska}],'depth':'45','op':'remove'})
add({'tool':'export','args':{'format':'stl','path':'mount-body.stl'}})
# 5 the lens holder, simplified (the printed part uses the real holder mesh): flange, tower, bore
prism(pr,'Lens holder flange',[YZ(BF,-HZ),YZ(HT,-HZ),YZ(HT,HZ),YZ(BF,HZ)],2*HY)
BEDF=(HF,0.0,-15.0)     # a point on the lower rib's bed face
sk=sketch(face(*BEDF),'Tower sketch',[circ(SK(0,0,HF),7.25)])
feat('extrude','Lens holder tower',{'profiles':[{'sketch':sk}],'depth':str(round(HF-HT+0.5,3)),'op':'add','opposite':True})
sk=sketch(face(*BEDF),'Bore sketch',[circ(SK(0,0,HF),6.15)])
feat('extrude','Lens bore (M12)',{'profiles':[{'sketch':sk}],'depth':str(round(HF-BF+0.5,3)),'op':'remove','opposite':True})
# 6 reference bodies: board, the visible part of the M12 2.1 mm lens (length and flange estimated from the listing photo)
def body(at,side,name,items,depth):
    sk=sketch(face(*at,side),name+' sketch',items); return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':'new'})
BRD=body((BF,5.0,9.0),-1,'Logitech C270 board 58 x 21 x 0.8',[rect(SK(-12.9,-10.5,BF,-1),SK(45.1,10.5,BF,-1))],0.8)
LB=body(BEDF,1,'M12 lens 2.1 mm, barrel',[circ(SK(0,0,HF),5.9)],17.0-(HF-BF))
LF=body((BF+17.0,0,0),1,'M12 lens 2.1 mm, front flange',[circ(SK(0,0,BF+17.0),9.0)],5.0)
add({'tool':'set_parts','args':{'parts':[
 {'body':[MOUNT,0],'name':'Webcam mount with M12 lens holder (print, ABS/ASA)','color':'#8a9099'},
 {'body':[BRD,0],'name':'Logitech C270 board (reference)','color':'#1c6e3c'},
 {'body':[LB,0],'name':'M12 2.1 mm lens barrel (reference)','color':'#101010'},
 {'body':[LF,0],'name':'M12 2.1 mm lens flange (reference)','color':'#181818'}]}})
add({'tool':'describe','args':{}})
add({'tool':'render','args':{'direction':[0.5,-0.6,-0.5],'width':1100,'height':800,'path':'cam_34.png'}})
add({'tool':'render','args':{'direction':[1,0,0],'width':1100,'height':800,'path':'cam_end.png'}})
add({'tool':'render','args':{'direction':[-0.5,0.7,0.4],'width':1100,'height':800,'path':'cam_back.png'}})
add({'tool':'export','args':{'format':'step','path':'webcam-parts.step'}})
add({'tool':'save_document','args':{'path':'cam-doc.json'}})
json.dump(S,open('cam_run.json','w'),indent=0)
json.dump({'LX':LX,'CY':CY,'CZ':CZ,'TH':TH,'BF':BF,'HF':HF},open('pose.json','w'))
