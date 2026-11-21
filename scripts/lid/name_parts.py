# Name and colour the lid studio's parts from their bounding boxes (run after lid_run.json).
# usage: python3 name_parts.py lid.out lid-doc.json -> name_run.json ; rcad run name_run.json
import json,sys
PRINT='#e07020'; ALU='#5a6470'; STEEL='#c8c8c8'
parts=None
for line in open(sys.argv[1]):
    r=json.loads(line)
    if r['tool']=='describe' and parts is None: parts=r['result']['parts']
out=[]; seen={}
def nm(base):
    seen[base]=seen.get(base,0)+1; return base
for p in parts:
    (x0,y0,z0),(x1,y1,z1)=p['bbox_mm']; n=1 if y0<200 else 2; side='right' if y0<200 else 'left'
    r=lambda v:round(v,1)
    if r(x0)==420 and r(x1)==445.5: name,c=f'Lid hinge {n}, lid arm (print, ASA)',PRINT
    elif r(x0)==434 and r(x1)==474.5: name,c=f'Lid hinge {n}, frame block (print, ASA)',PRINT
    elif r(x0)==261.5: name,c=f'Frame spring bracket, {side} (8 mm 6061, CNC)',ALU
    elif r(x0)==391.5: name,c=f'Lid spring bracket, {side} (6 mm 6061, CNC)',ALU
    elif r(x0)==-8: name,c='Lid handle (print, ASA)',PRINT
    elif r(x0)==436 and r(y1-y0)==4:
        k=f'b{n}'; seen[k]=seen.get(k,0)+1; name,c=f'Lid hinge {n} bearing 623 (3 x 10 x 4), {"+Y" if seen[k]==1 else "-Y"}',STEEL
    elif r(x0)==439.6: name,c=f'Lid hinge {n} pin, M3 x 20 screw and locknut','#303030'
    elif r(z0)==590.2 and r(x0)==-20.5: name,c='Lid seal, hollow silicone D 10 x 8 (shown compressed to 5)','#c03a2b'
    elif r(z0)==569.8: name,c='Lid insulation, PIR 25.4 mm (bonded under the lid)','#e2cc78'
    elif r(x0)==-25.5: name,c='Top lid panel (3 mm 6061)','#b0b4ba'
    else: raise SystemExit(f'unrecognised part {p}')
    out.append({'body':p['body'],'name':name,'color':c})
names=[o['name'] for o in out]; assert len(set(names))==len(names)==18, names
json.dump([{'tool':'open_document','args':{'path':sys.argv[2]}},{'tool':'switch_part_studio','args':{'index':0}},{'tool':'set_parts','args':{'parts':out}},{'tool':'describe','args':{}},
  {'tool':'render','args':{'direction':[0.6,-0.7,0.4],'width':1200,'height':850,'path':'studio.png'}},
  {'tool':'save_document','args':{'path':sys.argv[2]}}],open('name_run.json','w'))
print(len(out),'parts named')
