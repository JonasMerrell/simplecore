import json, numpy as np, itertools
bb={}
for line in open('bb.out'):
    r=json.loads(line)
    if r['tool']!='switch_part_studio': continue
    s=r['result'].get('part_studio')
    for p in r['result'].get('parts',[]):
        bb[(s,tuple(p['body']))]=(np.array(p['bbox_mm']),p['name'])
leaves=json.load(open('leaves.json'))
rows=[]
for o in leaves:
    k=(o['studio'],tuple(o['body']))
    if k not in bb: print('missing',k,o['path']); continue
    b,_=bb[k]; T=np.array(o['T'])
    pts=np.array([[x,y,z,1] for x in b[:,0] for y in b[:,1] for z in b[:,2]])@T.T
    rows.append(dict(top=o['top'],name=o['path'][-1],path=o['path'],lo=pts[:,:3].min(0).round(2).tolist(),hi=pts[:,:3].max(0).round(2).tolist()))
json.dump(rows,open('world.json','w'),indent=0)
for t in sorted(set(r['top'] for r in rows)):
    R=[r for r in rows if r['top']==t]
    lo=np.min([r['lo'] for r in R],0); hi=np.max([r['hi'] for r in R],0)
    print(t, lo, hi)
