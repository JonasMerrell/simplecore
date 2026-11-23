#!/usr/bin/env python3
"""Add the Purge bucket studio (bucket-doc.json from mk.py) to the printer documents given as arguments:
a Part Studio, an assembly with the bucket and the cleat, and one instance of that assembly in Printer."""
import json,sys,copy
B=json.load(open('bucket-doc.json')); bodies=json.load(open('bodies.json'))
st=copy.deepcopy(B['studios'][0]); st['name']='Purge bucket'
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
for src in sys.argv[1:]:
    d=json.load(open(src))
    assert not any(s['name']=='Purge bucket' for s in d['studios'])
    si=len(d['studios']); d['studios'].append(copy.deepcopy(st))
    inst=[{"id":i+1,"name":nm+" <1>","studio":si,"body":bodies[k],"pose":I(),"fixed":True,"hidden":False} for i,(k,nm) in enumerate((('bucket','Purge bucket'),('cleat','Purge bucket cleat'),('brush','Silicone nozzle brush 42x12x15')))]
    ai=len(d['assemblies'])
    d['assemblies'].append({"name":"Purge bucket","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
    # the fixed brush replaces the pad arm on the gantry: hide it (it would pass through the brush)
    for a in d['assemblies']:
        if a['name']=='X gantry':
            for x in a['instances']:
                if x['name'].startswith('Bent bracket'): x['hidden']=True; print('hid',x['name'])
    pr=[k for k,a in enumerate(d['assemblies']) if a['name']=='Printer'][0]
    P=d['assemblies'][pr]
    nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P.get('relations',[])])+1; P['next_id']=nid+1
    P['instances'].append({"id":nid,"name":"Purge bucket <1>","studio":0,"body":[0,0],"pose":I(),"fixed":True,"hidden":False,"sub":ai})
    json.dump(d,open(src,'w'))
    print(src,'studio',si,'assembly',ai,'printer',pr,'instance',nid)
