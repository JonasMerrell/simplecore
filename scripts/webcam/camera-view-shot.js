const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1280,height:720}});
  p.on('console',m=>{ if(m.type()==='error') console.log('ERR',m.text().slice(0,200)); });
  await p.goto('file:///home/user/work/view/p.html');
  await p.waitForFunction(()=>window.__v && window.__v.scene.children.length>3,{timeout:240000});
  await p.waitForTimeout(8000);
  const shots=JSON.parse(process.argv[2]);
  for(const s of shots){
    for(const [label,val] of Object.entries(s.joints||{})){
      await p.evaluate(([label,val])=>{ const el=[...document.querySelectorAll('#joints input')].find(e=>(e.getAttribute('aria-label')||'').startsWith(label)); if(!el) throw new Error('no joint '+label); el.value=val; el.dispatchEvent(new Event('input')); },[label,val]);
    }
    await p.waitForTimeout(1500);
    const url=await p.evaluate((s)=>{
      const {renderer,scene}=window.__v;
      renderer.setPixelRatio(1); renderer.setSize(s.w,s.h,false);
      const cam=new THREE.PerspectiveCamera(s.vfov,s.w/s.h,3,3000);
      cam.up.set(...s.up); cam.position.set(...s.pos); cam.lookAt(new THREE.Vector3(...s.at));
      const l1=new THREE.DirectionalLight(0xffffff,0.35); l1.position.set(0.3,-0.2,1); cam.add(l1);
      const extra=[cam];
      scene.traverse(o=>{ if(o.isHemisphereLight){ o.userData.i=o.intensity; o.intensity=0.5; } });
      for(const bx of (s.boxes||[])){ const m=new THREE.Mesh(new THREE.BoxGeometry(...bx.size),new THREE.MeshStandardMaterial({color:bx.color,roughness:0.7})); m.position.set(...bx.pos); extra.push(m); }
      extra.forEach(o=>scene.add(o));
      scene.background=new THREE.Color(0x15181c);
      renderer.render(scene,cam);
      const u=renderer.domElement.toDataURL('image/png');
      extra.forEach(o=>scene.remove(o));
      return u;
    },s);
    fs.writeFileSync(s.out,Buffer.from(url.split(',')[1],'base64')); console.log('wrote',s.out);
  }
  await b.close();
})();
