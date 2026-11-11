# walk Printer assembly → list of (path names, studio, body key, world pose 4x4)
import json, sys, numpy as np
d=json.load(open(sys.argv[1]))
A=d['assemblies']
def M(p):
    m=np.eye(4); m[:3,:3]=np.array(p['r']).reshape(3,3).T; m[:3,3]=p['t']; return m
out=[]
def walk(ai, T, path, top):
    for ins in A[ai]['instances']:
        Ti=T@M(ins['pose'])
        if 'sub' in ins: walk(ins['sub'], Ti, path+[ins['name']], top if top else ins['name'])
        else: out.append(dict(top=top or ins['name'], path=path+[ins['name']], studio=ins['studio'], body=ins['body'], T=Ti.tolist(), hidden=ins.get('hidden',False)))
walk(int(sys.argv[2]) if len(sys.argv)>2 else 22, np.eye(4), [], None)
json.dump(out, open('leaves.json','w'))
from collections import Counter
print(len(out), Counter(o['top'] for o in out))
print(sorted(set((o['studio'],tuple(o['body'])) for o in out)).__len__())
