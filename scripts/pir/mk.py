import json,re
T=25.4
boards=json.load(open('boards.json'))
inward_opp={'base':False,'top':True,'back':True,'right':True,'left':False}
steps=[{'tool':'new_document','args':{'units':'mm'}},{'tool':'set_variable','args':{'name':'pir_t','expr':'25.4'}}]
fid=0
def nid():
    global fid; fid+=1; return fid
def plane(ax,coord,name):
    base={0:'Right',1:'Front',2:'Top'}[ax]
    off=coord if ax!=1 else -coord
    i=nid(); steps.append({'tool':'add_feature','args':{'kind':'plane','name':name,'params':{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))}}}); return i
def uv(ax,p):
    return {0:(p[1],p[2]),1:(p[0],p[2]),2:(p[0],p[1])}[ax]
def clean(s):
    s=re.sub(r'\.step<1>','',s); s=re.sub(r' <\d+>','',s); s=s.replace('_',' ').replace('Front Left Z Motor Mount Rear','Z motor mount')
    return s
def sk_rect(pl,ax,lo,hi,name):
    i=nid(); steps.append({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':pl},'name':name}})
    steps.append({'tool':'sketch_add','args':{'sketch_id':i,'items':[{'type':'rect','corner1':[round(v,3) for v in uv(ax,lo)],'corner2':[round(v,3) for v in uv(ax,hi)]}]}})
    return i
parts=[]
for b in boards:
    ax=b['axis']; key=b['name'].split()[1]; inv=inward_opp[key]
    lo,hi=b['lo'],b['hi']
    outer=lo[ax] if b['outer']=='min' else hi[ax]; inner=hi[ax] if b['outer']=='min' else lo[ax]
    po=plane(ax,outer,b['name']+' outer face'); pi=plane(ax,inner,b['name']+' inner face')
    s=sk_rect(po,ax,lo,hi,b['name']+' sketch')
    e=nid(); steps.append({'tool':'add_feature','args':{'kind':'extrude','name':b['name'],'params':{'profiles':[{'sketch':s}],'depth':'pir_t','opposite':inv,'op':'new'}}})
    parts.append((e,b['name']))
    for c in b['cuts']:
        nm='Cut-out: '+', '.join(dict.fromkeys(clean(x) for x in c['src']))
        if c['mode']=='inner': pl,opp,d=pi,(not inv),str(c['d'])
        else: pl,opp,d=po,inv,('pir_t' if c['mode']=='through' else str(c['d']))
        s=sk_rect(pl,ax,c['lo'],c['hi'],nm[:60]+' sketch')
        e2=nid(); steps.append({'tool':'add_feature','args':{'kind':'extrude','name':nm[:80],'params':{'profiles':[{'sketch':s}],'depth':d,'opposite':opp,'op':'remove'}}})
steps.append({'tool':'describe','args':{}})
json.dump(steps,open('pir_run.json','w'),indent=0)
json.dump(parts,open('parts.json','w'))
print(len(steps),fid)
