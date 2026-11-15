import json,sys
# Real heater 125 x 80 x 87 mm. Placed with 80 along X (depth from back wall), 125 along Y, 87 up.
HX,HY,HZ=80.0,125.0,87.0
RECESS=18.0      # heater sits this far into the back lower PIR board (inner face x 405.1)
POCKET=RECESS+2  # pocket depth into the 25.4 board (5.4 mm foam left)
x1=405.1+RECESS; x0=x1-HX
y0=20.9; y1=y0+HY         # 20 mm off the right side PIR (inner face y 0.9)
LIFT=10.0; z0=129.58+LIFT; z1=z0+HZ
LEG=10.0; LEGX1=403.1     # legs stop in front of the back board
geo=dict(x0=x0,x1=x1,y0=y0,y1=y1,z0=z0,z1=z1,legx1=LEGX1)
json.dump(geo,open('geo.json','w'))
S=[{'tool':'open_document','args':{'path':'/tmp/claude-0/-home-user/ce2a2d95-d392-569c-92ca-ff706c34332a/scratchpad/h/X-carriage-no-belts.json'}}]
add=S.append
def r(a,b): return {'type':'rect','corner1':[round(a[0],3),round(a[1],3)],'corner2':[round(b[0],3),round(b[1],3)]}
def plane(base,off,name): add({'tool':'add_feature','args':{'kind':'plane','name':name,'params':{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))}}})
def cut(planefeat,sid,items,name,depth,opp):
    add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':planefeat},'name':name+' sketch'}})
    add({'tool':'sketch_add','args':{'sketch_id':sid,'items':items}})
    add({'tool':'add_feature','args':{'kind':'extrude','name':name,'params':{'profiles':[{'sketch':sid}],'depth':depth,'opposite':opp,'op':'remove'}}})
add({'tool':'switch_part_studio','args':{'index':27}})
plane('Top',104.18,'Heater stand cut-out plane')            # 99
cut(99,100,[r((x0-2,y0-2),(LEGX1+2,y0+LEG+2)),r((x0-2,y1-LEG-2),(LEGX1+2,y1+2))],'Cut-out: heater stand (2 legs)','pir_t',False)  # 100,101
plane('Right',405.1,'Heater recess plane')                    # 102
cut(102,103,[r((y0-2,z0-2),(y1+2,z1+2))],'Cut-out: heater recess',str(POCKET),False)  # 103,104
plane('Right',430.5,'Heater cord hole plane')                 # 105
yc=(y0+y1)/2; zc=(z0+z1)/2
cut(105,106,[r((yc-12,zc-12),(yc+12,zc+12))],'Cut-out: heater power cord','pir_t',True)  # 106,107
add({'tool':'describe','args':{}})
add({'tool':'switch_part_studio','args':{'index':25}})
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':4},'name':'Heater cord hole sketch'}})
add({'tool':'sketch_add','args':{'sketch_id':19,'items':[{'type':'circle','center':[round(yc,3),round(zc,3)],'radius':8}]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Heater cord hole (16 mm grommet)','params':{'profiles':[{'sketch':19}],'depth':'panel_t','opposite':False,'op':'remove'}}})
add({'tool':'describe','args':{}})
add({'tool':'new_part_studio','args':{'name':'Chamber heater'}})
for k,v in (('heater_x',HX),('heater_y',HY),('heater_z',HZ)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
plane('Top',z0,'Heater underside')
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':1},'name':'Heater footprint'}})
add({'tool':'sketch_add','args':{'sketch_id':2,'items':[r((x0,y0),(x1,y1))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'PTC fan heater 500W 125x80x87','params':{'profiles':[{'sketch':2}],'depth':'heater_z','op':'new'}}})
plane('Top',104.18,'Bottom panel top')
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':4},'name':'Stand legs'}})
add({'tool':'sketch_add','args':{'sketch_id':5,'items':[r((x0,y0),(LEGX1,y0+LEG)),r((x0,y1-LEG),(LEGX1,y1))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Heater stand legs','params':{'profiles':[{'sketch':5}],'depth':str(round(z0-104.18,3)),'op':'new'}}})
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':'heater-doc.json'}})
json.dump(S,open('heater_run.json','w'),indent=0)
print(geo)
