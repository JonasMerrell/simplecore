# Put the real M12 lens holder mesh (m12_lens_housing_v2.stl, kept in the project files, not in the repo) into the
# mount body from mkmount.py and write the printable STL, turned so the holder's front face lies on the bed.
# The holder's STL is not a closed mesh (a few cracks and T-junctions), so a mesh boolean fails on it. The two shells
# are written into one STL overlapping each other; slicers fuse overlapping shells of one object.
# usage: python3 fuse_holder.py mount-body.stl m12_lens_housing_v2.stl pose.json webcam-mount-with-lens-holder.stl
import sys, json, math, numpy as np, trimesh
body_p, hold_p, pose_p, out_p = sys.argv[1:5]
P=json.load(open(pose_p)); c,s=math.cos(math.radians(P['TH'])),math.sin(math.radians(P['TH']))
A=np.array([1.0,0,0]); V=np.array([0,c,-s]); W=np.array([0,s,c]); C=np.array([P['LX'],P['CY'],P['CZ']])
body=trimesh.load(body_p,process=True); hold=trimesh.load(hold_p,process=True)
print('body watertight',body.is_watertight,'vol',round(body.volume))
def to_local(w): w=np.asarray(w)-C; return np.stack([w@V,w@A,w@W],1)          # world -> (x view, y along, z across)
def to_print(l): return np.stack([l[:,1],l[:,2],P['HF']-l[:,0]],1)            # holder front (x = HF) down on the bed
h=np.asarray(hold.vertices); zmin=h[:,2].min()
hl=np.stack([h[:,2]-zmin+P['BF'], h[:,1], h[:,0]],1)                           # holder (across, along, up the axis) -> local
bl=to_local(body.vertices)
# the mount must not fill the holder's openings: bore, sensor pocket, screw slots
pts=[(x,0,0) for x in np.arange(P['BF']+0.2,P['HF'],0.5)]+[(x,y,z) for x in (P['BF']+0.3,P['BF']+2) for y in (-5.5,5.5) for z in (-5.5,5.5)]+[(x,0,z) for x in (P['BF']+0.3,P['BF']+3.5) for z in (-8.6,8.6)]
pw=C+np.outer([p[1] for p in pts],A)+np.outer([p[0] for p in pts],V)+np.outer([p[2] for p in pts],W)
assert not body.contains(pw).any(), 'the mount body intrudes into the holder openings'
# and it must overlap the holder's outer walls so the two fuse
ov=[(P['BF']+1,0,-10.4),(P['BF']+1,0,10.4),(P['BF']+8,0,-7.1),(P['BF']+8,0,7.1)]
ow=C+np.outer([p[1] for p in ov],A)+np.outer([p[0] for p in ov],V)+np.outer([p[2] for p in ov],W)
print('overlap points inside the mount body:',body.contains(ow).tolist())
B=trimesh.Trimesh(to_print(bl),body.faces,process=False); H=trimesh.Trimesh(to_print(hl),hold.faces,process=False)
for m in (B,H):   # both maps are proper rotations; keep the facets outward
    pass
t=trimesh.util.concatenate([B,H]); off=[t.vertices[:,0].min(),t.vertices[:,1].min(),0]; t.vertices-=off; B.vertices-=off; H.vertices-=off
print('print size',t.extents.round(2),'z min',t.vertices[:,2].min().round(3),'holder z',H.vertices[:,2].min().round(3),H.vertices[:,2].max().round(3))
for name,m in (('mount body',B),('holder',H)):
    n=m.face_normals; a=m.area_faces; zc=m.triangles_center[:,2]
    bed=(zc<1e-3)&(n[:,2]<-0.99); down=(n[:,2]<-0.02)&~bed; ang=np.degrees(np.arcsin(np.clip(-n[down,2],0,1)))
    print(name,'bed contact mm2',a[bed].sum().round(1),'| overhang mm2 by angle from vertical:',{f'{lo}-{hi}':float(a[down][(ang>=lo)&(ang<hi)].sum().round(1)) for lo,hi in ((0,41),(41,46),(46,51),(51,80),(80,91))})
    if name=='mount body':
        flat=down.nonzero()[0][ang>=80]; print('  flat ceilings at z:',np.unique(zc[flat].round(1)).tolist()[:12], 'centres',m.triangles_center[flat][:4].round(1).tolist())
t.export(out_p); print('wrote',out_p,len(t.faces),'facets')
