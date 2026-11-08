import json,re,sys,copy
S=sys.argv[1]
d=json.load(open(S+'/asm/xc.json')); A=d['assemblies']
t=json.load(open(S+'/xt/tree.json'))
cache={}
def verts(b):
    if b not in cache:
        s=open(S+'/all/b%s.step'%b).read()
        pts=dict((k,(float(x),float(y),float(z))) for k,x,y,z in re.findall(r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([-\d.eE+]+),([-\d.eE+]+),([-\d.eE+]+)\)\)",s))
        vs=[pts[k] for k in re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)",s) if k in pts] or list(pts.values())
        cache[b]=vs
    return cache[b]
def nbox(n):
    W=[]
    def rec(n):
        if 'body' in n:
            m=n['world']['m']; tt=n['world']['t']
            for x,y,z in verts(n['body']):
                W.append([m[0]*x+m[3]*y+m[6]*z+tt[0], m[1]*x+m[4]*y+m[7]*z+tt[1], m[2]*x+m[5]*y+m[8]*z+tt[2]])
        for c in n.get('kids') or []: rec(c)
    rec(n)
    return [min(w[k] for w in W) for k in range(3)],[max(w[k] for w in W) for k in range(3)]
groups={'frame':[], 'gantry':[], 'toolhead':[], 'bed':[]}
log=[]
top=A[17]; fa=A[16]
for x,n in zip(top['instances'],t['kids']):
    if x.get('sub')==16: continue
    lo,hi=nbox(n); c=[(lo[k]+hi[k])/2 for k in range(3)]
    if c[0]<600: g='frame'
    elif hi[1]-lo[1]<130 and 200<c[1]<400: g='toolhead'
    else: g='gantry'
    groups[g].append(x); log.append((g,x['name'],[round(v) for v in lo],[round(v) for v in hi]))
for x,n in zip(fa['instances'],[k for k in t['kids'] if 'simplecore' in (k.get('name') or '')][0]['kids']):
    nm=x['name']
    lo,hi=nbox(n)
    if nm.startswith('MGN9-H'): g='gantry'
    elif re.match(r'(Bed|MGN12H|Z_Carriage_mount_chain|Z_Bed_)',nm): g='bed'
    else: g='frame'
    groups[g].append(x); log.append((g,nm,[round(v) for v in lo],[round(v) for v in hi]))
for l in sorted(log,key=lambda l:l[0]):
    if l[0]!='frame' or 'idler' in l[1].lower() or l[2][0]>300: print(*l)
json.dump({k:[i['id'] for i in v] for k,v in groups.items()}, open(S+'/mates/groups.json','w'))
print({k:len(v) for k,v in groups.items()})
# build assemblies
names={'frame':'Frame (static)','gantry':'X gantry','toolhead':'Toolhead','bed':'Bed (Z)'}
base=len(A); idx={}
for k in ['frame','gantry','toolhead','bed']:
    insts=[]
    for j,x in enumerate(groups[k]):
        y=copy.deepcopy(x); y['id']=j+1; y['fixed']=True; insts.append(y)
    A.append({'name':names[k],'instances':insts,'mates':[],'next_id':len(insts)+1,'relations':[]})
    idx[k]=len(A)-1
dx=186.0-1022.3
def ident(t): return {'r':[1.0,0,0,0,1.0,0,0,0,1.0],'t':t}
pr=[]
for j,k in enumerate(['frame','gantry','toolhead','bed']):
    pr.append({'id':j+1,'name':names[k]+' <1>','studio':0,'body':[0,0],'pose':ident([dx,0.0,0.0] if k in('gantry','toolhead') else [0.0,0.0,0.0]),'fixed':k=='frame','hidden':False,'sub':idx[k]})
A.append({'name':'Printer','instances':pr,'mates':[],'next_id':5,'relations':[]})
d['active']={'Assembly':len(A)-1}
json.dump(d,open(S+'/mates/printer.json','w'))
print('printer asm', len(A)-1, idx)
