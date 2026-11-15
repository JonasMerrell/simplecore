# Mounting holes for the Trad Rack's K3 side mount brackets: 4 x M3 (Ø3.4) through the left side panel,
# and 12 x 12 mm pockets, 10 deep, in the left lower PIR board behind them for the nuts and screw tips.
# Hole centres = the bracket screw axes (x 54/354, z 289.8/375.55) with the Trad Rack pose in splice_tr.py.
import json,sys
doc=sys.argv[1]; out=sys.argv[2]
X=(54.0,354.0); Z=(289.8,375.55)
S=[{'tool':'open_document','args':{'path':doc}}]; add=S.append
add({'tool':'switch_part_studio','args':{'index':25}})
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':10},'name':'Trad Rack mounting holes sketch'}})   # 21
add({'tool':'sketch_add','args':{'sketch_id':21,'items':[{'type':'circle','center':[x,z],'radius':1.7} for x in X for z in Z]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Trad Rack mounting holes (4x M3)','params':{'profiles':[{'sketch':21}],'depth':'panel_t','opposite':False,'op':'remove'}}})  # 22
add({'tool':'describe','args':{}})
add({'tool':'switch_part_studio','args':{'index':27}})
add({'tool':'add_feature','args':{'kind':'plane','name':'Trad Rack nut pocket plane','params':{'base':{'kind':'origin_plane','plane':'Front'},'offset':'-477.5'}}})  # 108
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':108},'name':'Cut-out: Trad Rack mounting nuts sketch'}})  # 109
add({'tool':'sketch_add','args':{'sketch_id':109,'items':[{'type':'rect','corner1':[x-6,z-6],'corner2':[x+6,z+6]} for x in X for z in Z]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Cut-out: Trad Rack mounting nuts','params':{'profiles':[{'sketch':109}],'depth':'10','opposite':False,'op':'remove'}}})  # 110
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':out}})
json.dump(S,open('holes_run.json','w'),indent=0)
