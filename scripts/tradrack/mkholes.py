# Mounting holes for the Trad Rack's K3 side mount brackets: 4 x M3 tapped (Ø2.5 tap drill) in the right side
# panel (-Y, the door-latch side; Jonas drilled and tapped the 3 mm panel), and 8 x 8 mm pockets, 10 deep, in the
# right lower PIR board behind them for the screw tips (they stand 7 mm past the panel).
# Hole centres = the bracket screw axes (x 11.1/311.1, z 297.25/383.0) with the Trad Rack pose in splice_tr.py.
import json,sys
doc=sys.argv[1]; out=sys.argv[2]
X=(11.1,311.1); Z=(297.25,383.0)
S=[{'tool':'open_document','args':{'path':doc}}]; add=S.append
add({'tool':'switch_part_studio','args':{'index':25}})
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':7},'name':'Trad Rack mounting holes sketch'}})   # 21
add({'tool':'sketch_add','args':{'sketch_id':21,'items':[{'type':'circle','center':[x,z],'radius':1.25} for x in X for z in Z]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Trad Rack mounting holes (4x M3 tapped)','params':{'profiles':[{'sketch':21}],'depth':'panel_t','opposite':False,'op':'remove'}}})  # 22
add({'tool':'describe','args':{}})
add({'tool':'switch_part_studio','args':{'index':27}})
add({'tool':'add_feature','args':{'kind':'plane','name':'Trad Rack screw tip pocket plane','params':{'base':{'kind':'origin_plane','plane':'Front'},'offset':'24.5'}}})  # 108
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':108},'name':'Cut-out: Trad Rack screw tips sketch'}})  # 109
add({'tool':'sketch_add','args':{'sketch_id':109,'items':[{'type':'rect','corner1':[x-4,z-4],'corner2':[x+4,z+4]} for x in X for z in Z]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Cut-out: Trad Rack screw tips','params':{'profiles':[{'sketch':109}],'depth':'10','opposite':True,'op':'remove'}}})  # 110
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':out}})
json.dump(S,open('holes_run.json','w'),indent=0)
