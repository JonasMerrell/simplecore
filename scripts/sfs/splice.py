#!/usr/bin/env python3
"""Add the 'SFS V2 holder' studio (sfs-doc.json from mk.py) to the printer documents given as arguments:
a Part Studio, an assembly with the holder, the SFS and its two push-fits, and one instance of that
assembly in Printer. Additive only: refuses if the studio is already there."""
import json,sys,copy,os
here=os.path.dirname(os.path.abspath(__file__))
B=json.load(open(os.path.join(here,'sfs-doc.json'))); bodies=json.load(open(os.path.join(here,'bodies.json')))
st=copy.deepcopy(B['studios'][0]); st['name']='SFS V2 holder'
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
parts=(('holder','SFS V2 holder (Trad Rack)'),('sfs','BTT SFS V2.0 filament sensor'),('fit1','SFS push-fit (anchor side)'),('fit2','SFS push-fit (motor side)'))
for src in sys.argv[1:]:
    d=json.load(open(src))
    assert not any(s['name']=='SFS V2 holder' for s in d['studios']), src+' already has it'
    si=len(d['studios']); d['studios'].append(copy.deepcopy(st))
    inst=[{"id":i+1,"name":nm+" <1>","studio":si,"body":bodies[k],"pose":I(),"fixed":True,"hidden":False} for i,(k,nm) in enumerate(parts)]
    ai=len(d['assemblies'])
    d['assemblies'].append({"name":"SFS V2 filament sensor","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
    pr=[k for k,a in enumerate(d['assemblies']) if a['name']=='Printer'][0]
    P=d['assemblies'][pr]
    nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P.get('relations',[])])+1; P['next_id']=nid+1
    P['instances'].append({"id":nid,"name":"SFS V2 filament sensor <1>","studio":0,"body":[0,0],"pose":I(),"fixed":True,"hidden":False,"sub":ai})
    open(src,'w',encoding='utf-8').write(json.dumps(d,indent=2,ensure_ascii=False))   # same layout as the repo files
    print(src,'studio',si,'assembly',ai,'printer',pr,'instance',nid)
