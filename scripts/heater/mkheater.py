import json,sys
# heater envelope (placeholder until measured): depth along X, width along Y, height Z
HX,HY,HZ=[float(v) for v in (sys.argv[1:4] if len(sys.argv)>3 else (52,87.5,60))]
GAP_BACK=18.0   # intake gap to back PIR face (x 405.1)
LIFT=10.0       # heater underside above base PIR top (129.58)
YC=105.0
x1=405.1-GAP_BACK; x0=x1-HX; y0=YC-HY/2; y1=YC+HY/2; z0=129.58+LIFT; z1=z0+HZ
LEG=10.0
geo=dict(x0=x0,x1=x1,y0=y0,y1=y1,z0=z0,z1=z1)
json.dump(geo,open('geo.json','w'))
S=[{'tool':'open_document','args':{'path':'/mnt/project-files/x-carriage/X-carriage/X-carriage-no-belts.json'}}]
fid=[0]
def add(step): S.append(step)
# --- PIR studio 27: new features start after 98
def plane(base,off,name):
    add({'tool':'add_feature','args':{'kind':'plane','name':name,'params':{'base':{'kind':'origin_plane','plane':base},'offset':str(round(off,3))}}})
def sk(planefeat,items,name):
    add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':planefeat},'name':name}})
def r(a,b): return {'type':'rect','corner1':[round(a[0],3),round(a[1],3)],'corner2':[round(b[0],3),round(b[1],3)]}
add({'tool':'switch_part_studio','args':{'index':27}})
n=98
plane('Top',104.18,'Heater stand cut-out plane'); n+=1; P1=n
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':P1},'name':'Cut-out: heater stand sketch'}}); n+=1; S1=n
add({'tool':'sketch_add','args':{'sketch_id':S1,'items':[r((x0-2,y0-2),(x1+2,y0+LEG+2)),r((x0-2,y1-LEG-2),(x1+2,y1+2))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Cut-out: heater stand (2 legs)','params':{'profiles':[{'sketch':S1}],'depth':'pir_t','opposite':False,'op':'remove'}}}); n+=1
plane('Right',430.5,'Heater cord hole plane'); n+=1; P2=n
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':P2},'name':'Cut-out: heater cord sketch'}}); n+=1; S2=n
zc=(z0+z1)/2
add({'tool':'sketch_add','args':{'sketch_id':S2,'items':[r((YC-12,zc-12),(YC+12,zc+12))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Cut-out: heater power cord','params':{'profiles':[{'sketch':S2}],'depth':'pir_t','opposite':True,'op':'remove'}}}); n+=1
add({'tool':'describe','args':{}})
# --- Enclosure panels studio 25: cord hole in back panel
add({'tool':'switch_part_studio','args':{'index':25}})
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':4},'name':'Heater cord hole sketch'}}); m=19
add({'tool':'sketch_add','args':{'sketch_id':m,'items':[{'type':'circle','center':[YC,round(zc,3)],'radius':8}]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Heater cord hole (16 mm grommet)','params':{'profiles':[{'sketch':m}],'depth':'panel_t','opposite':False,'op':'remove'}}})
add({'tool':'describe','args':{}})
# --- new studio: heater
add({'tool':'new_part_studio','args':{'name':'Chamber heater'}})
for k,v in (('heater_x',HX),('heater_y',HY),('heater_z',HZ)): add({'tool':'set_variable','args':{'name':k,'expr':str(v)}})
plane('Top',z0,'Heater underside'); # id1
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':1},'name':'Heater footprint'}}) # 2
add({'tool':'sketch_add','args':{'sketch_id':2,'items':[r((x0,y0),(x1,y1))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'PTC fan heater 500W (envelope)','params':{'profiles':[{'sketch':2}],'depth':'heater_z','op':'new'}}}) #3
plane('Top',104.18,'Bottom panel top') #4
add({'tool':'create_sketch','args':{'plane':{'kind':'feature_plane','feature':4},'name':'Stand legs'}}) #5
add({'tool':'sketch_add','args':{'sketch_id':5,'items':[r((x0,y0),(x1,y0+LEG)),r((x0,y1-LEG),(x1,y1))]}})
add({'tool':'add_feature','args':{'kind':'extrude','name':'Heater stand legs','params':{'profiles':[{'sketch':5}],'depth':str(round(z0-104.18,3)),'op':'new'}}}) #6
add({'tool':'describe','args':{}})
add({'tool':'save_document','args':{'path':'heater-doc.json'}})
json.dump(S,open('heater_run.json','w'),indent=0)
print(geo)
