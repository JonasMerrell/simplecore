# Jonas's printer has no upper side insulation boards (2026-11-17). Hide them in the "PIR insulation" assembly.
# usage: python3 hide_upper_pir.py X-carriage.json   (rewrites the file in place)
import json,sys
src=sys.argv[1]; d=json.load(open(src))
a=[x for x in d['assemblies'] if x['name']=='PIR insulation'][0]
n=0
for i in a['instances']:
    if i['name'].startswith(('PIR right side, upper','PIR left side, upper')): i['hidden']=True; n+=1; print(src,'hid',i['name'])
assert n==2
json.dump(d,open(src,'w'))
