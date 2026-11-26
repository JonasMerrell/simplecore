# Name and colour the lid studio's parts from their bounding boxes (run after lid_run.json).
# usage: python3 name_parts.py lid.out lid-doc.json [lid_geom.json] -> name_run.json ; rcad run name_run.json
import json,sys
PRINT='#e07020'; ALU='#5a6470'; STEEL='#c8c8c8'
G=json.load(open(sys.argv[3] if len(sys.argv)>3 else 'lid_geom.json')); HX=G['H'][0]
parts=None
for line in open(sys.argv[1]):
    r=json.loads(line)
    if r['tool']=='describe' and parts is None: parts=r['result']['parts']
out=[]; seen={}
eq=lambda a,b: abs(a-b)<0.15
for p in parts:
    (x0,y0,z0),(x1,y1,z1)=p['bbox_mm']; n=1 if y0<200 else 2; side='right' if y0<200 else 'left'
    if eq(x0,G['PAD_X0']) and eq(x1,HX+G['BOSS_R']): name,c=f'Lid hinge {n}, corner arm (print, ASA)',PRINT
    elif eq(x0,HX-G['EAR_R']) and eq(x1,474.5): name,c=f'Lid hinge {n}, frame block (print, ASA)',PRINT
    elif eq(x0,G['B'][0]-G['FB_W']): name,c=f'Frame spring bracket, {side} (print, ASA, 3x M4 inserts)',PRINT
    elif eq(x0,G['L'][0]-22) and eq(y1-y0,G['LB_Y'][1]-G['LB_Y'][0]): name,c=f'Lid spring lever, {side} (print, ASA, 3x M4 inserts)',PRINT
    elif eq(x0,G['TUBE'][0]-2): name,c='Filament tube (reference, from the photos)','#9fd0ff'
    elif eq(x0,-8): name,c='Lid handle (print, ASA)',PRINT
    elif eq(x0,HX-5) and eq(y1-y0,4):
        k=f'b{n}'; seen[k]=seen.get(k,0)+1; name,c=f'Lid hinge {n} bearing 623 (3 x 10 x 4), {"+Y" if seen[k]==1 else "-Y"}',STEEL
    elif eq(x0,HX-1.45): name,c=f'Lid hinge {n} pin, M3 x 30 screw and locknut','#303030'
    elif eq(z0,590.2) and eq(x0,-20.5): name,c='Lid seal, hollow silicone D 10 x 8 (shown compressed to 5)','#c03a2b'
    elif eq(z0,569.8): name,c='Lid insulation, PIR 25.4 mm (bonded under the lid)','#e2cc78'
    elif eq(x0,-25.5): name,c='Top lid panel (3 mm 6061)','#b0b4ba'
    else: raise SystemExit(f'unrecognised part {p}')
    out.append({'body':p['body'],'name':name,'color':c})
names=[o['name'] for o in out]; assert len(set(names))==len(names)==19, names
json.dump([{'tool':'open_document','args':{'path':sys.argv[2]}},{'tool':'switch_part_studio','args':{'index':0}},{'tool':'set_parts','args':{'parts':out}},{'tool':'describe','args':{}},
  {'tool':'render','args':{'direction':[0.6,-0.7,0.4],'width':1200,'height':850,'path':'studio.png'}},
  {'tool':'save_document','args':{'path':sys.argv[2]}}],open('name_run.json','w'))
print(len(out),'parts named')
