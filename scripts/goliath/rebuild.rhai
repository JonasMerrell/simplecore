let s = import_step("purchased.stp");
let g = import_step("gol-air.step");
let bs = s.solids();
let m = bs[8];
let h = g.rotate(vec3(0.0,0.0,0.0), vec3(0.0,0.0,1.0), 180.0);
h = h.translate(m.bbox().min - h.bbox().min);
let r = h.solids();
print(`gol solids ${r.len()} valid ${h.is_valid()}`);
bs[8] = r[0];
export_step(bs, "purchased-new.stp");
let n = import_step("purchased-new.stp").solids();
let i = 0;
for b in n {
  let o = s.solids()[i];
  let t = b.tessellate(0.05, 10.0);
  let seen = #{}; for f in t.faces { seen[`${f}`] = true; }
  let miss = b.face_count() - seen.len();
  print(`${i} dvol=${b.volume() - o.volume()} dmin=${b.bbox().min - o.bbox().min} dmax=${b.bbox().max - o.bbox().max} valid=${b.is_valid()} unmeshed=${miss}`);
  i += 1;
}
render([#{shape: n[8], color: "#e5eaed"}], #{path: "goliath-fixed-front.png", width: 900, height: 900, view: "front"});
