import json, numpy as np
T=25.4
rows=json.load(open('world.json'))
STRUCT=('2020','spacer','Bottom_pannel','backer')
sweep={'X gantry <1>':[(0,-164,165)], 'Toolhead <1>':[(0,-164,165),(1,-212.3,108.7)], 'Bed (Z) <1>':[(2,-182.7,44.0)]}
comps=[]
for r in rows:
    if r['top'] in ('Enclosure <1>','Front door <1>'): continue
    lo=np.array(r['lo'],float); hi=np.array(r['hi'],float)
    for ax,a,b in sweep.get(r['top'],[]):
        lo[ax]+=a; hi[ax]+=b
    c=0.0 if any(s in r['name'] for s in STRUCT) else 2.0
    comps.append((r['name'],r['top'],lo-c,hi+c))
# boards: name, lo, hi, axis, outer ('min'|'max')
B=[
 ('PIR base',        [-25.5,-23.5,104.18],[424.5,476.5,104.18+T],2,'min'),
 ('PIR top',         [-5.5,-3.5,590.2-T], [404.5,456.5,590.2],   2,'max'),
 ('PIR back lower',  [430.5-T,-3.5,104.18+T],[430.5,456.5,401],  0,'max'),
 ('PIR back upper',  [430.5-T,-3.5,421],  [430.5,456.5,570.2],   0,'max'),
 ('PIR right lower', [-5.5,-24.5,104.18+T],[404.5,-24.5+T,398],  1,'min'),
 ('PIR right upper', [-5.5,-24.5,468.01], [404.5,-24.5+T,590.2-T], 1,'min'),
 ('PIR left lower',  [-5.5,477.5-T,104.18+T],[404.5,477.5,398],  1,'max'),
 ('PIR left upper',  [-5.5,477.5-T,468.01], [404.5,477.5,590.2-T],   1,'max'),
]
B=[(n,np.array(l),np.array(h),ax,o) for n,l,h,ax,o in B]
# earlier boards are obstacles for later ones
out=[]
for i,(n,lo,hi,ax,o) in enumerate(B):
    obst=list(comps)+[(B[j][0],'PIR',B[j][1],B[j][2]) for j in range(i)]
    cuts=[]
    for cn,top,clo,chi in obst:
        ilo=np.maximum(lo,clo); ihi=np.minimum(hi,chi)
        if np.all(ihi-ilo>0.05):
            tin = ilo[ax]<=lo[ax]+1e-6; tax = ihi[ax]>=hi[ax]-1e-6   # touches min / max face
            touch_outer = tin if o=='min' else tax
            touch_inner = tax if o=='min' else tin
            if touch_outer and touch_inner or not(touch_outer or touch_inner): mode='through'; d=T
            elif touch_outer: mode='outer'; d=ihi[ax]-ilo[ax]
            else: mode='inner'; d=ihi[ax]-ilo[ax]
            cuts.append(dict(src=[cn],mode=mode,d=d,lo=ilo,hi=ihi))
    ia=[k for k in range(3) if k!=ax]
    dropped=[c for c in cuts if c['mode']!='through' and c['d']<1.0]
    for c in dropped: print('  near (dropped <1mm pocket):',n,c['src'],round(c['d'],2))
    cuts=[c for c in cuts if not(c['mode']!='through' and c['d']<1.0)]
    # snap to board edges within 3 mm
    for c in cuts:
        for k in ia:
            if c['lo'][k]-lo[k]<3: c['lo'][k]=lo[k]
            if hi[k]-c['hi'][k]<3: c['hi'][k]=hi[k]
        if c['mode']!='through' and c['d']>T-3: c['mode']='through'; c['d']=T
    # merge overlapping/near rects of same mode
    changed=True
    while changed:
        changed=False
        for a in range(len(cuts)):
            for b in range(a+1,len(cuts)):
                A,Bc=cuts[a],cuts[b]
                if A['mode']!=Bc['mode']: continue
                ar=lambda l,h:(h[ia[0]]-l[ia[0]])*(h[ia[1]]-l[ia[1]])
                ul=np.minimum(A['lo'],Bc['lo']); uh=np.maximum(A['hi'],Bc['hi'])
                if all(A['lo'][k]<=Bc['hi'][k]+3 and Bc['lo'][k]<=A['hi'][k]+3 for k in ia) and ar(ul,uh)<=1.15*(ar(A['lo'],A['hi'])+ar(Bc['lo'],Bc['hi'])) and abs(A['d']-Bc['d'])<3:
                    A['lo']=np.minimum(A['lo'],Bc['lo']); A['hi']=np.maximum(A['hi'],Bc['hi'])
                    A['d']=max(A['d'],Bc['d']); A['src']+=Bc['src']; del cuts[b]; changed=True; break
            if changed: break
    th=[c for c in cuts if c['mode']=='through']
    cuts=[c for c in cuts if not any(t is not c and all(t['lo'][k]<=c['lo'][k]+1e-6 and c['hi'][k]<=t['hi'][k]+1e-6 for k in ia) for t in th)]
    out.append(dict(name=n,lo=lo.tolist(),hi=hi.tolist(),axis=ax,outer=o,cuts=[dict(src=sorted(set(c['src'])),mode=c['mode'],d=round(float(c['d']),2),lo=[round(float(x),2) for x in c['lo']],hi=[round(float(x),2) for x in c['hi']]) for c in cuts]))
json.dump(out,open('boards.json','w'),indent=1)
for b in out:
    print('==',b['name'],b['lo'],b['hi'])
    for c in b['cuts']: print('   ',c['mode'],c['d'],c['lo'],c['hi'],', '.join(s[:30] for s in c['src'])[:150])
