import json,re,sys
S=sys.argv[1]
t=json.load(open(S+'/xt/tree.json'))
cache={}
def verts(b):
    if b in cache: return cache[b]
    s=open(S+'/all/b%s.step'%b).read()
    pts=dict((k,(float(x),float(y),float(z))) for k,x,y,z in re.findall(r"#(\d+)=CARTESIAN_POINT\('[^']*',\(([-\d.eE+]+),([-\d.eE+]+),([-\d.eE+]+)\)\)",s))
    vs=[pts[k] for k in re.findall(r"VERTEX_POINT\('[^']*',#(\d+)\)",s) if k in pts]
    if not vs: vs=list(pts.values())
    cache[b]=vs; return vs
out=[]
def walk(n,path):
    nm=n.get('name') or ''
    p=path+[nm]
    if 'body' in n:
        m=n['world']['m']; tt=n['world']['t']
        W=[]
        for x,y,z in verts(n['body']):
            W.append([m[0]*x+m[3]*y+m[6]*z+tt[0], m[1]*x+m[4]*y+m[7]*z+tt[1], m[2]*x+m[5]*y+m[8]*z+tt[2]])
        lo=[min(w[k] for w in W) for k in range(3)]; hi=[max(w[k] for w in W) for k in range(3)]
        out.append({'path':'/'.join(p[1:]),'body':n['body'],'lo':[round(v,1) for v in lo],'hi':[round(v,1) for v in hi]})
    for c in n.get('kids') or []: walk(c,p)
walk(t,[])
json.dump(out,open(S+'/mates/bbox.json','w'),indent=0)
for o in out:
    if not re.search(r'screw|plate_electronic|impeller|needle|insert|Hex|socket|Beacon|shim|MR85|bearing\^|set_screw|pin$|bushing',o['path']):
        print(o['path'][:60].ljust(60),o['body'],o['lo'],o['hi'])
