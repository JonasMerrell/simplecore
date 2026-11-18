# Webcam for the simplecore printer: a closed box around the bare Logitech C270 board.
#   Part A "box":  front wall with the M12 lens holder (Jonas's "m12_lens_housing_v2") behind it, walls all round the board.
#                  The board screws to the back of the holder with the stock lens holder's two screws.
#   Part B "back": the lid that closes the box, in one piece with the VHB tape pad that goes on the aluminium right side panel.
#   Two M3 x 20 screws from the front, one at each end, hold the box to the back.
# usage: python3 mkbox.py -> cam_run.json ; rcad run cam_run.json -> cam-doc.json (studio 0 = "Webcam"),
#        box-body.stl, both.stl (print_files.py splits them, adds the real holder mesh and turns the parts for printing)
import json, math
TH=45.0                        # tilt below horizontal; the pad geometry below assumes 45
WALL_Y=-24.5                   # inner face of the aluminium right side panel (Jonas's printer has no upper side insulation)
c,s=math.cos(math.radians(TH)),math.sin(math.radians(TH))
A=(1.0,0.0,0.0); V=(0.0,c,-s); Wd=(0.0,s,c)       # along the board, view axis, across the board
# camera-local: x along the view axis, y along the board (world X), z across the board
BF=-0.15                       # board front face = back face of the lens holder
HT=BF+3.99; HF=BF+12.01        # top of the holder's flange; front of the holder = outside of the box's front wall
HY=7.24; HZ=10.58              # holder half sizes: along the board, across it
FLOOR=1.5; XF=HF-FLOOR         # front wall thickness, inside face of the front wall
XL=-5.0                        # box rim = inside face of the lid (4 mm behind the board for the USB connector)
LID_T=2.0; XB=XL-LID_T
IY0,IY1=-13.6,45.6; IZ=10.9    # cavity: along the board (board -12.9..45.1), half width (board 21.0 to 21.2)
WT=2.0; OZ=IZ+WT               # wall thickness, outer half width
LUG=7.0; OY0,OY1=IY0-WT-LUG,IY1+WT+LUG      # solid end lugs for the two M3 screws
SY=(IY0-WT-LUG/2, IY1+WT+LUG/2)             # screw positions along the board (z = 0)
PAD_T=3.0
LX=191.2                                      # lens on the bed's centre line
CY=round(WALL_Y+PAD_T-(c*XB+s*(-OZ)),3)      # the pad's inner face passes through the lid's lower back edge
CZ=535.0                                      # pad top stays under the top side rail (z 570.2)
def P3(x,y,z): return [round((LX,CY,CZ)[i]+A[i]*y+V[i]*x+Wd[i]*z,4) for i in range(3)]   # local (view, along, across) -> world
def YZ(x,z): p=P3(x,0,z); return (p[1],p[2])
FR={ 1:((-1.0,0.0,0.0),(0.0,s,c)), -1:((1.0,0.0,0.0),(0.0,s,c)) }   # sketch frames on faces with normal +v / -v (checked by chk.py output)
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
def xplane(y,name): return feat('plane',name,{'base':{'kind':'origin_plane','plane':'Right'},'offset':str(round(LX+y,4))})
def poly(pts): return {'type':'polyline','points':[[round(a,4),round(b,4)] for a,b in pts],'closed':True}
def circ(p,r): return {'type':'circle','center':p,'radius':r}
def face(x,y,z,side=1): return {'kind':'face','point':P3(x,y,z),'normal':[side*V[0],side*V[1],side*V[2]]}
def prism(plane,name,pts,depth,op='add'):
    sk=sketch({'kind':'feature_plane','feature':plane},name+' profile',[poly([YZ(x,z) for x,z in pts])])
    return feat('extrude',name,{'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':op})
def rect(side,x,y0,y1,z0,z1): return {'type':'rect','corner1':SK(y0,z0,x,side),'corner2':SK(y1,z1,x,side)}
def onface(at,side,name,items,depth,op,into):
    sk=sketch(face(*at,side),name+' sketch',items)
    p={'profiles':[{'sketch':sk}],'depth':str(round(depth,3)),'op':op}
    if into: p['opposite']=True
    return feat('extrude',name,p)
for k,v in (('cam_tilt',TH),('pad_t',PAD_T)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
# ---------------- Part A: box
pe=xplane(OY0,'End plane (lens end)')
BOX=prism(pe,'Box block',[(XL,-OZ),(HF,-OZ),(HF,OZ),(XL,OZ)],OY1-OY0,'new')
RIM=(XL,SY[0],8.0)             # a point on the box's rim face, on the lens-end lug
onface(RIM,-1,'Cavity for the board',[rect(-1,XL,IY0,IY1,-IZ,IZ)],XF-XL,'remove',True)
CF=(XF,25.0,0.0)               # a point on the cavity floor (inside face of the front wall)
onface(CF,-1,'Board ledge at the cable end',[rect(-1,XF,IY1-1.5,IY1+0.3,-IZ-0.3,IZ+0.3)],XF-BF,'add',False)
for sg,nm in ((1,'upper'),(-1,'lower')):
    z0,z1=sorted((sg*7.0,sg*(IZ+0.3)))
    onface(CF,-1,f'Holder support, {nm}',[rect(-1,XF,-HY,HY,z0,z1)],XF-HT,'add',False)
    z0,z1=sorted((sg*10.2,sg*(IZ+0.3)))
    onface(CF,-1,f'Holder cheek, {nm}',[rect(-1,XF,-HY,HY,z0,z1)],XF-BF,'add',False)
FRONT=(HF,25.0,0.0)            # a point on the front face
onface(FRONT,1,'Lens opening in the front wall',[circ(SK(0,0,HF),7.0)],FLOOR+0.1,'remove',True)
onface(FRONT,1,'M3 clearance holes',[circ(SK(y,0,HF),1.7) for y in SY],HF-XL+0.03,'remove',True)
onface(FRONT,1,'M3 head counterbores',[circ(SK(y,0,HF),3.1) for y in SY],5.0,'remove',True)
onface(RIM,-1,'Cable slot in the lower wall',[rect(-1,XL,33.0,40.0,-OZ-0.5,-IZ+0.5)],4.0,'remove',True)
add({'tool':'export','args':{'format':'stl','path':'box-body.stl'}})
# ---------------- Part B: back (lid + tape pad), built after the box so its sketch faces are not confused with the box's rim
P0=(XB,-OZ); P1=(XB-2*OZ,OZ); d=PAD_T/math.sqrt(2)          # pad inner face runs from the lid's lower back edge up the wall
XG=XL-0.05      # the lid's inside face, 0.05 off the rim so the two bodies stay separate in the model
BACK=prism(pe,'Lid and tape pad',[(XG,-OZ),(XG,OZ),(XB,OZ),P0,P1,(P1[0]-d,P1[1]-d),(P0[0]-d,P0[1]-d)],OY1-OY0,'new')
TRI=[(XB+0.5,-OZ-1.0),(XB+0.5,OZ),(P1[0]-1.0,OZ)]      # overlaps the lid and the pad by 0.5 and 0.35
prism(pe,'End web (lens end)',TRI,LUG+WT)
pf=xplane(OY1-LUG-WT,'End web plane (cable end)')
prism(pf,'End web (cable end)',TRI,LUG+WT)
pm=xplane((IY0+IY1)/2-1.5,'Middle web plane')
prism(pm,'Middle web',TRI,3.0)
LIDF=(XG,(IY0+IY1)/2,3.0)       # a point on the lid's inside face
onface(LIDF,1,'M3 pilot holes (self-tapping, 2.8)',[circ(SK(y,0,XG),1.4) for y in SY],11.0,'remove',True)
add({'tool':'export','args':{'format':'stl','path':'both.stl'}})
# ---------------- the lens holder, simplified (the printed part uses the real holder mesh): tower, flange, bore
onface(CF,-1,'Lens holder tower',[circ(SK(0,0,XF,-1),7.25)],XF-HT,'add',False)
onface((HT,0.0,8.5),-1,'Lens holder flange',[rect(-1,HT,-HY,HY,-HZ,HZ)],HT-BF,'add',False)
onface(FRONT,1,'Lens bore (M12)',[circ(SK(0,0,HF),6.15)],HF-BF+0.1,'remove',True)
# ---------------- reference bodies: board, the visible part of the M12 2.1 mm lens (length and flange estimated)
BRD=onface((BF,5.0,9.0),-1,'Logitech C270 board 58 x 21 x 0.8',[rect(-1,BF,-12.9,45.1,-10.5,10.5)],0.8,'new',False)
LB=onface(FRONT,1,'M12 lens 2.1 mm, barrel',[circ(SK(0,0,HF),5.9)],17.0-(HF-BF),'new',False)
LF=onface((BF+17.0,0,0),1,'M12 lens 2.1 mm, front flange',[circ(SK(0,0,BF+17.0),9.0)],5.0,'new',False)
add({'tool':'set_parts','args':{'parts':[
 {'body':[BOX,0],'name':'Webcam box with M12 lens holder (print, ABS/ASA)','color':'#8a9099'},
 {'body':[BACK,0],'name':'Webcam back with tape pad (print, ABS/ASA)','color':'#e07020'},
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
json.dump({'LX':LX,'CY':CY,'CZ':CZ,'TH':TH,'BF':BF,'HF':HF,'XL':XL},open('pose.json','w'))
print('CY',CY,'pad top z',P3(P1[0]-d,0,P1[1]-d)[2],'pad bottom z',P3(P0[0]-d,0,P0[1]-d)[2])
