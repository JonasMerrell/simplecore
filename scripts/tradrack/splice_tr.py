# Add the Trad Rack (Annex Engineering, R1 2024-03-04, default config) to the document.
# usage: python3 splice_tr.py tr-doc.json X-carriage.json   -> writes X-carriage.json.new
# tr-doc.json: a document whose studio 1 is the STEP import (imp.json, rcad with PR #128 so names/colours survive).
import json,sys,copy
T=json.load(open(sys.argv[1])); src=sys.argv[2]
d=json.load(open(src))
assert not any(s['name']=='Trad Rack' for s in d['studios'])
st=copy.deepcopy(T['studios'][1]); st['name']='Trad Rack'
for k,v in st['doc']['parts'].items():
    n=v['name']
    if '^' in n: a,b=n.split('^',1); n=f'{a} ({b})'
    v['name']=n
si=len(d['studios']); d['studios'].append(st)
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
key=lambda k: tuple(map(int,k.split(':')))
parts=sorted(st['doc']['parts'].items(),key=lambda kv:key(kv[0]))
inst=[{"id":n+1,"name":v['name']+f' <{n+1}>',"studio":si,"body":list(key(k)),"pose":I(),"fixed":True,"hidden":False} for n,(k,v) in enumerate(parts)]
ai=len(d['assemblies'])
d['assemblies'].append({"name":"Trad Rack","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
P=[a for a in d['assemblies'] if a['name']=='Printer'][0]
nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P['relations']])+1; P['next_id']=nid+1
# Trad Rack frame: X along the rack's extrusion, +Y = the side the lanes face, brackets' back face at y = -59.6.
# Placed on the left side (+Y): brackets flat on the left panel's outer face (y 480.5), turned 180 deg about Y so the
# lane inputs face up, centred on the panel in X (bracket pair centre x 5.6 -> 204), bracket centre at world z 335.65.
P["instances"].append({"id":nid,"name":"Trad Rack <1>","studio":0,"body":[0,0],"pose":{"r":[-1.0,0,0,0,1.0,0,0,0,-1.0],"t":[209.6,540.1,361.3]},"fixed":True,"hidden":False,"sub":ai})
json.dump(d,open(src+'.new','w'))
print(src,'studio',si,'assembly',ai,'printer instance',nid,'parts',len(inst))
