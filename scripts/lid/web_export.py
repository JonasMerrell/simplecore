# Interactive 3D page (rcad export_web) of an assembly with the top lid.
# The page does not solve closed loops, so the gas springs would come apart when the lid opens. Here the springs'
# sliding mates are suppressed in a temporary copy and the "Open top lid" motion drives the four ball joints with
# the angles the springs really take (piecewise linear, 5 degree steps), so body and rod stay in line.
# usage: python3 web_export.py DOC.json ASSEMBLY_NAME lid_geom.json OUT.html [PAGE TITLE] [--hide=INSTANCE ...] -> web_run.json ; rcad run web_run.json
import json,math,sys,os
src,asm,geom,out=sys.argv[1:5]; args=[a for a in sys.argv[5:] if not a.startswith('--hide=')]; title=args[0] if args else None
hide=[a[7:] for a in sys.argv[5:] if a.startswith('--hide=')]   # instances left out of the page, e.g. --hide="Trad Rack" (it is 6 of the 7 million triangles)
d=json.load(open(src)); ai=[i for i,a in enumerate(d['assemblies']) if a['name']==asm][0]; T=d['assemblies'][ai]
G=json.load(open(geom)); H,B,L0=G['H'],G['B'],G['L']
ids={m['name']:m['id'] for m in T['mates']}
for m in T['mates']:
    if m['name'].endswith(', stroke'): m['suppressed']=True
if title: T['name']=title
T['instances']=[i for i in T['instances'] if not any(i['name'].startswith(h) for h in hide)]
tmp=os.path.abspath(out)+'.doc.json'; json.dump(d,open(tmp,'w'))
def psi(th):
    t=math.radians(th); u,v=H[0]-L0[0],L0[1]-H[1]; c,s=math.cos(t),math.sin(t)
    return math.degrees(math.atan2(B[1]-(H[1]+u*s+v*c),B[0]-(H[0]-u*c+v*s)))
dpsi=lambda th:(psi(th)-psi(0)+180)%360-180
OPEN=G.get('OPEN',90.0); N=round(OPEN/5)
links=[{'mate':ids['Top lid hinge'],'from':0,'to':OPEN}]
for k in range(N):
    a,b=5*k,5*k+5
    for side in ('right','left'):
        links.append({'mate':ids[f'Gas spring {side}, frame ball'],'from':-dpsi(a),'to':-dpsi(b),'start':a/OPEN,'end':b/OPEN})
        links.append({'mate':ids[f'Gas spring {side}, lid ball'],'from':-dpsi(a)-a,'to':-dpsi(b)-b,'start':a/OPEN,'end':b/OPEN})
json.dump([{'tool':'open_document','args':{'path':tmp}},
 {'tool':'assembly_animation','args':{'assembly':ai,'motions':[{'name':'Open top lid','links':links}],'animations':[{'name':'Open and close the lid','repeat':'bounce','clips':[{'motion':'Open top lid','length':4,'ease':'smooth'}]}]}},
 {'tool':'export_web','args':{'assembly':ai,'path':os.path.abspath(out)}}],open('web_run.json','w'))
print('assembly',ai,'links',len(links))
