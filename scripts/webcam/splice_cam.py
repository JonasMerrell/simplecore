# Add the webcam (closed two-part box with the lens holder, and the reference bodies for the board and lens) to the document.
# usage: python3 mkbox.py && rcad run cam_run.json            (writes cam-doc.json, box-body.stl, both.stl, pose.json)
#        python3 splice_cam.py cam-doc.json X-carriage.json   -> writes X-carriage.json.new
#        python3 hide_upper_pir.py X-carriage.json.new        (hides the two upper side insulation boards)
#        python3 print_files.py box-body.stl both.stl m12_lens_housing_v2.stl pose.json outdir   (the two printable STLs)
# The splice only adds: a new Part Studio "Webcam", a new assembly "Webcam", and one instance in Printer.
import json,sys,copy
C=json.load(open(sys.argv[1])); src=sys.argv[2]
d=json.load(open(src))
assert not any(s['name']=='Webcam' for s in d['studios'])
st=copy.deepcopy(C['studios'][0]); st['name']='Webcam'
si=len(d['studios']); d['studios'].append(st)
I=lambda: {"r":[1.0,0,0,0,1.0,0,0,0,1.0],"t":[0.0,0.0,0.0]}
key=lambda k: tuple(map(int,k.split(':')))
parts=sorted(st['doc']['parts'].items(),key=lambda kv:key(kv[0]))
inst=[{"id":n+1,"name":v['name']+f' <{n+1}>',"studio":si,"body":list(key(k)),"pose":I(),"fixed":True,"hidden":False} for n,(k,v) in enumerate(parts)]
ai=len(d['assemblies'])
d['assemblies'].append({"name":"Webcam","instances":inst,"mates":[],"next_id":len(inst)+1,"relations":[]})
P=[a for a in d['assemblies'] if a['name']=='Printer'][0]
nid=max([P['next_id']-1]+[x['id'] for x in P['instances']]+[m['id'] for m in P['mates']]+[r['id'] for r in P['relations']])+1; P['next_id']=nid+1
P["instances"].append({"id":nid,"name":"Webcam <1>","studio":0,"body":[0,0],"pose":I(),"fixed":True,"hidden":False,"sub":ai})
json.dump(d,open(src+'.new','w'))
print(src,'studio',si,'assembly',ai,'printer instance',nid,'parts',len(inst))
