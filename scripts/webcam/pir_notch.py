# Cut the opening for the webcam in the back upper insulation board (Part Studio "PIR insulation").
# 108 wide (y 188.4..296.4), 40 tall (z 531 up to the board's top edge at 570.2), right through the 25.4 mm board,
# under the middle of the rear top rail, so the rail's bottom slot is reachable and the mount sits in the opening.
# usage: python3 pir_notch.py X-carriage.json  -> notch_run.json ; rcad run notch_run.json  (rewrites the document in place)
import json,sys
src=sys.argv[1]
d=json.load(open(src)); si=[i for i,s in enumerate(d['studios']) if s['name']=='PIR insulation'][0]
n=max(f['id'] for f in d['studios'][si]['doc']['features'])
S=[{'tool':'open_document','args':{'path':src}},{'tool':'switch_part_studio','args':{'index':si}},
 {'tool':'add_feature','args':{'kind':'plane','name':'Webcam opening plane (inner face of the back boards)','params':{'base':{'kind':'origin_plane','plane':'Right'},'offset':'405.1'}}},
 {'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':n+1},'name':'Cut-out: webcam opening sketch'}},
 {'tool':'sketch_add','args':{'sketch_id':n+2,'items':[{'type':'rect','corner1':[188.4,531.0],'corner2':[296.4,571.0]}]}},
 {'tool':'add_feature','args':{'kind':'extrude','name':'Cut-out: webcam opening','params':{'profiles':[{'sketch':n+2}],'depth':'pir_t','op':'remove','opposite':False}}},
 {'tool':'describe','args':{}},{'tool':'save_document','args':{'path':src}}]
json.dump(S,open('notch_run.json','w'))
