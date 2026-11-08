import json,re,sys
S=sys.argv[1]; P=sys.argv[2]
d=json.load(open(P))
t=json.load(open(S+'/xt/tree.json'))
col={}
def w(n):
    if 'body' in n and n.get('colour') and n['body'] not in col: col[n['body']]=n['colour']
    for k in n.get('kids') or []: w(k)
w(t)
specs=json.load(open(S+'/asm/specs.json'))
names=json.load(open(S+'/gen/names.json'))
byname={v:int(k) for k,v in names.items()}
done=0; miss=[]
for si,st in enumerate(d['studios']):
    parts=st['doc'].setdefault('parts',{})
    key=[k for k in specs if k.endswith('/studio%d.step'%si)]
    if key:
        ids=[int(l.split()[0]) for l in specs[key[0]].strip().split('\n')]
        for k,b in enumerate(ids):
            bk='1:%d'%k
            if b in col:
                parts.setdefault(bk,{'name':None,'color':None,'material':None})['color']=[round(c*255) for c in col[b]]; done+=1
            else: miss.append(b)
    else:
        for bk,p in parts.items():
            b=byname.get(p.get('name') or st['name'])
            if b in col: p['color']=[round(c*255) for c in col[b]]; done+=1
            else: miss.append((si,bk))
json.dump(d,open(P,'w'))
print('coloured',done,'missing',miss)
