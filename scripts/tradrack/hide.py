# Which Trad Rack bodies to hide to match Jonas's unit (photo 2026-11-15): 8 lanes (0-7, the motor end) and no Nebula box.
# usage: python3 hide.py imp2.out  -> hide.json (list of body keys "f:i")
import json,sys,collections
P=[json.loads(l) for l in open(sys.argv[1]) if json.loads(l)['tool']=='describe'][0]['result']['parts']
inside=lambda b,lo,hi: all(b[0][k]>=lo[k]-1e-6 and b[1][k]<=hi[k]+1e-6 for k in range(3))
H=[]
for p in P:
    b=p['bbox_mm']; n=p['name']
    lane = inside(b,[22.0,-49.5,-60],[127.5,-5.5,13]) and not any(s in n for s in ('arriage','elector'))
    neb = inside(b,[-123,-59,-94],[-15.5,-18,32]) and ('Nebula' in n or 'TMC' in n or (b[1][2]<-40.3 and not any(s in n for s in ('Collet','ECAS')))) 
    # the hidden lanes' M5 screws and T-nuts in the extrusion slot
    lane = lane or (b[0][0]>21 and b[1][0]<128 and ('5 x 0.8 x 10' in n or 'T-Nut Mockup_M5' in n))
    # the rest of the Nebula box: TradBoard PCB and its connectors, the 40 mm fan, its grill and screws
    neb = neb or n.startswith(('Annex-TradBoard','40x40x10 DC Fan','Fan Grill 40mm')) or (n.startswith('JST-XH-3A') and b[0][2]<-40) \
          or ('3 x 0.5 x 16' in n and b[0][0]<-130 and b[1][1]<-19)
    if lane or neb: H.append((f"{p['body'][0]}:{p['body'][1]}",n,'lane' if lane else 'nebula'))
json.dump([h[0] for h in H],open('hide.json','w'))
print(len(H)); print(collections.Counter((h[2],h[1][:35]) for h in H).most_common(60))
