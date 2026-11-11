import json,sys
src,dst=sys.argv[1],sys.argv[2]
d=json.load(open(src)); p=json.load(open('pir.json'))
assert not any(s['name']=='PIR insulation' for s in d['studios'])
st=p['studios'][0]; st['name']='PIR insulation'
si=len(d['studios']); d['studios'].append(st)
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
parts=st['doc']['parts']
inst=[]
for n,(k,v) in enumerate(sorted(parts.items(), key=lambda kv:int(kv[0].split(':')[0]))):
    f,i=map(int,k.split(':'))
    inst.append({"id":n+1,"name":v['name'],"studio":si,"body":[f,i],"pose":I(),"fixed":True,"hidden":False})
ai=len(d['assemblies'])
d['assemblies'].append({"name":"PIR insulation","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
pr=[k for k,a in enumerate(d['assemblies']) if a['name']=='Printer'][0]
P=d['assemblies'][pr]
nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P['relations']])+1; P['next_id']=nid
P['instances'].append({"id":nid,"name":"PIR insulation <1>","studio":0,"body":[0,0],"pose":I(),"fixed":True,"hidden":False,"sub":ai})
d['active']={'Assembly':pr}
json.dump(d,open(dst,'w'))
print('studio',si,'assembly',ai,'printer',pr,'instance',nid)
