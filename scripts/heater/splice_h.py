import json,sys,copy
src=sys.argv[1]
H=json.load(open('heater-doc.json'))
d=json.load(open(src))
assert [s['name'] for s in d['studios']]==[s['name'] for s in H['studios'][:28]]
assert not any(s['name']=='Chamber heater' for s in d['studios'])
for i in (25,27): d['studios'][i]=copy.deepcopy(H['studios'][i])
st=copy.deepcopy(H['studios'][28])
st['doc']['parts']={
 '3:0':{'name':'PTC fan heater 500W 110V (envelope)','color':[30,30,30],'material':None,'finish':'matte'},
 '6:0':{'name':'Heater stand leg','color':[170,170,175],'material':None,'finish':'matte'},
 '6:1':{'name':'Heater stand leg','color':[170,170,175],'material':None,'finish':'matte'}}
si=len(d['studios']); d['studios'].append(st)
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
inst=[{"id":n+1,"name":v['name']+f' <{n+1}>',"studio":si,"body":list(map(int,k.split(':'))),"pose":I(),"fixed":True,"hidden":False} for n,(k,v) in enumerate(st['doc']['parts'].items())]
ai=len(d['assemblies'])
d['assemblies'].append({"name":"Chamber heater","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
pr=[k for k,a in enumerate(d['assemblies']) if a['name']=='Printer'][0]
P=d['assemblies'][pr]
nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P['relations']])+1; P['next_id']=nid+1
P['instances'].append({"id":nid,"name":"Chamber heater <1>","studio":0,"body":[0,0],"pose":I(),"fixed":True,"hidden":False,"sub":ai})
json.dump(d,open(src+'.new','w'))
print(src,'studio',si,'assembly',ai,'printer',pr,'instance',nid)
