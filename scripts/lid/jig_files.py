# Split the jig studio's STL into the three jigs, turn each lips-up for printing (no supports) and write right and
# left (mirrored) versions of the corner and side panel jigs. The handle jig is symmetric.
# usage: python3 jig_files.py lid-jigs.stl outdir    (needs trimesh)
import sys, numpy as np, trimesh
m=trimesh.load(sys.argv[1],process=True); out=sys.argv[2]; n=0
for c in m.split(only_watertight=False):
    lo,hi=c.bounds
    if lo[2]<570: name,R,sides='lid-jig-side-panel',[[1,0,0],[0,0,-1],[0,1,0]],True      # outer face (-y) down
    elif hi[0]>400: name,R,sides='lid-jig-corner',[[1,0,0],[0,-1,0],[0,0,-1]],True        # top face down
    else: name,R,sides='lid-jig-handle',[[1,0,0],[0,-1,0],[0,0,-1]],False
    c=c.copy(); c.vertices=c.vertices@np.array(R,float).T; c.vertices-=c.bounds[0]
    for side in (('right','left') if sides else ('',)):
        d=c.copy()
        if side=='left': d.vertices[:,1]*=-1; d.invert(); d.vertices-=d.bounds[0]
        f=f'{out}/{name}{"-"+side if side else ""}.stl'; d.export(f); n+=1
        print(f,'size',d.extents.round(1),'watertight',d.is_watertight,'volume cm3',round(d.volume/1000,1))
assert n==5
