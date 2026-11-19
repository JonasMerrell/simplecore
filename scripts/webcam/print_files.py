# Write the two printable STLs of the webcam box from mkbox.py's exports.
#   box:  box-body.stl plus the real M12 lens holder mesh (m12_lens_housing_v2.stl, kept in the project files, not in
#         the repo), turned so the front wall lies on the bed and the M12 thread prints upright.
#         The holder's STL is not a closed mesh (a few cracks and T-junctions), so a mesh boolean fails on it. The two
#         shells are written into one STL overlapping each other; slicers fuse overlapping shells of one object.
#   back: the lid with the wedge base, taken out of both.stl, turned so the face that goes on the panel lies on the bed.
# usage: python3 print_files.py box-body.stl both.stl m12_lens_housing_v2.stl pose.json outdir
import sys, json, math, numpy as np, trimesh
box_p, both_p, hold_p, pose_p, out = sys.argv[1:6]
P=json.load(open(pose_p)); c,s=math.cos(math.radians(P['TH'])),math.sin(math.radians(P['TH']))
A=np.array([1.0,0,0]); V=np.array([0,c,-s]); W=np.array([0,s,c]); C=np.array([P['LX'],P['CY'],P['CZ']])
L=np.stack([V,A,W])                                   # world -> camera-local (x view, y along the board, z across)
def to_local(w): return (np.asarray(w)-C)@L.T
def report(name,m):
    n=m.face_normals; a=m.area_faces; zc=m.triangles_center[:,2]
    bed=(zc<0.01)&(n[:,2]<-0.99); down=(n[:,2]<-0.02)&~bed; ang=np.degrees(np.arcsin(np.clip(-n[down,2],0,1)))
    print(name,'size',m.extents.round(2),'bed contact mm2',a[bed].sum().round(1),'| overhang mm2 by angle from vertical:',{f'{lo}-{hi}':float(a[down][(ang>=lo)&(ang<hi)].sum().round(1)) for lo,hi in ((0,46),(46,80),(80,91))})
    fl=down.nonzero()[0][ang>=80]
    if len(fl): print('   flat ceilings at print z',np.unique(zc[fl].round(1)).tolist())
box=trimesh.load(box_p,process=True); both=trimesh.load(both_p,process=True); hold=trimesh.load(hold_p,process=True)
comps=both.split(only_watertight=False)
back=trimesh.util.concatenate([m for m in comps if to_local(m.vertices)[:,0].max()<P['XL']-0.01])   # everything behind the box rim (outer shell and any sealed hollows)
print('box watertight',box.is_watertight,round(box.volume),'| back watertight',back.is_watertight,round(back.volume))
# ---- box + holder, front wall down
RB=np.array([[0,1,0],[0,0,1],[-1,0,0]],float)          # local -> print: x = along the board, y = across, z = towards the back
assert abs(np.linalg.det(RB@L)-1)<1e-9                 # a rotation, not a mirror image
h=np.asarray(hold.vertices); zmin=h[:,2].min()
hl=np.stack([h[:,2]-zmin+P['BF'], h[:,1], h[:,0]],1)    # holder (across, along, up the lens axis) -> local
pts=[(x,0,0) for x in np.arange(P['BF']+0.2,P['HF']+0.5,0.5)]+[(x,y,z) for x in (P['BF']+0.3,P['BF']+2) for y in (-5.5,5.5) for z in (-5.5,5.5)]+[(x,0,z) for x in (P['BF']+0.3,P['BF']+3.5) for z in (-8.6,8.6)]
pw=C+np.array(pts)@L
assert not box.contains(pw).any(), 'the box intrudes into the holder openings (bore, sensor pocket, screw slots)'
ov=[(P['BF']+1,0,-10.4),(P['BF']+1,0,10.4),(P['BF']+8,0,-7.1),(P['BF']+8,0,7.1),(P['HF']-0.7,0,7.1),(P['HF']-0.7,7.1,0)]
print('holder walls inside the box body at',box.contains(C+np.array(ov)@L).tolist())
def pr(l): q=np.asarray(l)@RB.T; q[:,2]+=P['HF']; return q
B=trimesh.Trimesh(pr(to_local(box.vertices)),box.faces,process=False); H=trimesh.Trimesh(pr(hl),hold.faces,process=False)
t=trimesh.util.concatenate([B,H]); off=np.array([t.vertices[:,0].min(),t.vertices[:,1].min(),0]); 
for m in (t,B,H): m.vertices-=off
print('holder print z',H.vertices[:,2].min().round(3),H.vertices[:,2].max().round(3))
report('box body',B); report('holder',H)
t.export(out+'/webcam-box-with-lens-holder.stl')
# ---- back, tape face down
ez=np.array([c,0,s]); ex=np.array([0.0,1,0]); ey=np.cross(ex,ez); RK=np.stack([ex,ey,ez])
assert abs(np.linalg.det(RK@L)-1)<1e-9
K=trimesh.Trimesh(to_local(back.vertices)@RK.T,back.faces,process=False); K.vertices-=K.vertices.min(0)
report('back',K); K.export(out+'/webcam-base-screw-on.stl')
