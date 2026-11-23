# Split the lid studio's STL export into the printed parts and turn each into its print orientation.
#   hinge frame block: on its side (the pin axis upright), so the layers run along the ears; the slot needs support
#   corner arms:       top face down (right and left are mirror images)
#   handle:            on its front face, no supports
# usage: python3 print_files.py lid-prints.stl outdir    (needs trimesh)
import sys, numpy as np, trimesh
m=trimesh.load(sys.argv[1],process=True); out=sys.argv[2]
done=set()
UP=[[1,0,0],[0,-1,0],[0,0,-1]]          # upside down
for c in m.split(only_watertight=False):
    lo,hi=c.bounds; eq=lambda a,b: abs(float(a)-b)<0.15
    if eq(hi[0],474.5): name,R,first='lid-hinge-frame-block',[[1,0,0],[0,0,1],[0,-1,0]],True          # y -> down; the two are identical
    elif hi[0]>440 and lo[0]>300: name,R,first=('lid-corner-arm-right' if lo[1]<200 else 'lid-corner-arm-left'),UP,False   # mirror images
    elif eq(lo[0],-8) and eq(hi[0],6): name,R,first='lid-handle',[[0,1,0],[0,0,1],[1,0,0]],False       # front face down
    else: raise SystemExit(f'unrecognised part {lo} {hi}')
    if name in done: continue
    done.add(name)
    c=c.copy(); c.vertices=c.vertices@np.array(R,float).T; assert abs(np.linalg.det(np.array(R,float))-1)<1e-9
    c.vertices-=c.bounds[0]
    n=c.face_normals; a=c.area_faces; zc=c.triangles_center[:,2]
    bed=(zc<0.01)&(n[:,2]<-0.99); flat=(n[:,2]<-0.98)&~bed
    print(name,'size',c.extents.round(2),'watertight',c.is_watertight,'volume cm3',round(c.volume/1000,1),'bed mm2',round(a[bed].sum()),'flat ceilings mm2',round(a[flat].sum()),'at z',np.unique(zc[flat].round(1)).tolist())
    c.export(f'{out}/{name}.stl')
assert len(done)==4, done
