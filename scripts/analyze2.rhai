// Stage 1: recognise a part's features. Prepended: IN, OUT, AX (main axis 0/1/2).
fn a3(v) { [v.x, v.y, v.z] }
fn comp(v, i) { if i == 0 { v.x } else if i == 1 { v.y } else { v.z } }
fn par(n, i) { abs(abs(comp(n, i)) - 1.0) < 1e-6 }
fn perp(n, i) { abs(comp(n, i)) < 1e-6 }
fn prismatic(f, i) {
    let k = f.kind();
    if k == "plane" { let n = f.normal(); return par(n, i) || perp(n, i); }
    if k == "cylinder" { return par(f.axis().axis, i); }
    false
}
fn face_items(f) {
    let out = [];
    for e in f.edges() {
        let k = e.kind();
        if k == "line" { out.push(#{t: "L", s: a3(e.start()), e: a3(e.end())}); }
        else if k == "circle" {
            let c = e.circle();
            out.push(#{t: "C", c: a3(c.center), n: a3(c.axis), r: c.radius, s: a3(e.start()), e: a3(e.end()), m: a3(e.mid())});
        } else {
            let pts = []; for p in e.points(0.002) { pts.push(a3(p)); }
            out.push(#{t: "S", pts: pts});
        }
    }
    out
}
fn inner_point(f) {
    let t = f.shape().tessellate(0.05, 20.0);
    let v = t.vertices; let ix = t.indices;
    let best = []; let ba = -1.0;
    let n = ix.len() / 3;
    for k in 0..n {
        let a = ix[3*k]; let b = ix[3*k+1]; let c = ix[3*k+2];
        let p = vec3(v[3*a], v[3*a+1], v[3*a+2]); let q = vec3(v[3*b], v[3*b+1], v[3*b+2]); let r = vec3(v[3*c], v[3*c+1], v[3*c+2]);
        let ar = norm(cross(q - p, r - p));
        if ar > ba { ba = ar; best = a3((p + q + r) / 3.0); }
    }
    best
}
fn slab_box(i, lo, hi) {
    let big = 1e4;
    let mn = [-big, -big, -big]; let mx = [big, big, big];
    mn[i] = lo; mx[i] = hi;
    block(mn, mx)
}
// the faces of a solid's cross-section at level h along axis i (as faces, facing -i)
fn section(s, i, h) {
    let d = 1e-3;
    let bb = s.bbox();
    let mn = [bb.min.x - 1.0, bb.min.y - 1.0, bb.min.z - 1.0]; let mx = [bb.max.x + 1.0, bb.max.y + 1.0, bb.max.z + 1.0];
    mn[i] = h - d; mx[i] = h + d;
    let piece = s.common([block(mn, mx)]);
    let out = [];
    for f in piece.faces() {
        if f.kind() == "plane" && par(f.normal(), i) && comp(f.normal(), i) < 0.0 && abs(comp(f.center(), i) - (h - d)) < 1e-6 { out.push(f.shape()); }
    }
    out
}
fn face_list_json(fs) {
    let out = [];
    for f in fs {
        for g in f.faces() {
            if g.area() < 1e-4 { continue; }
            out.push(#{items: face_items(g), inside: inner_point(g), area: g.area()});
        }
    }
    out
}
fn levels(s, i) {
    let bb = s.bbox();
    let lv = [comp(bb.min, i), comp(bb.max, i)];
    for f in s.faces() { if f.kind() == "plane" && par(f.normal(), i) { lv.push(comp(f.center(), i)); } }
    lv.sort();
    let lev = [];
    for x in lv { if lev.len() == 0 || x - lev[lev.len() - 1] > 1e-5 { lev.push(x); } }
    lev
}
fn slabs(s, i) {
    let lev = levels(s, i);
    let out = [];
    for k in 0..lev.len() - 1 {
        let lo = lev[k]; let hi = lev[k + 1];
        // the middle, or nearby if a boolean there fails
        let sec = [];
        for t in [0.5, 0.37, 0.63, 0.21, 0.79] {
            sec = section(s, i, lo + (hi - lo) * t);
            if sec.len() > 0 { break; }
        }
        if sec.len() == 0 { continue; }
        out.push(#{lo: lo, hi: hi, faces: face_list_json(sec)});
    }
    out
}
// faces connected by shared edges
fn groups(fs) {
    let n = fs.len();
    let gid = []; for k in 0..n { gid.push(k); }
    let es = []; for f in fs { es.push(f.edges()); }
    for a in 0..n { for b in (a + 1)..n {
        let touch = false;
        for x in es[a] { for y in es[b] { if same(x, y) { touch = true; break; } } if touch { break; } }
        if touch { let ga = gid[a]; let gb = gid[b]; for k in 0..n { if gid[k] == gb { gid[k] = ga; } } }
    } }
    let out = #{};
    for k in 0..n { let key = "" + gid[k]; if !(key in out) { out[key] = []; } out[key].push(fs[k]); }
    out.values()
}
fn group_axis(g) {
    for i in 0..3 {
        let ok = true;
        for f in g { if !prismatic(f, i) { ok = false; break; } }
        if ok { return i; }
    }
    -1
}
// a hole: cylinders and cones on one axis along x, y or z (plus flat steps and bottoms)
fn hole_of(P, g) {
    let e = -1; let pt = ();
    for f in g {
        let k = f.kind();
        if k == "cylinder" || k == "cone" {
            let ax = f.axis();
            let ie = -1; for i in 0..3 { if par(ax.axis, i) { ie = i; } }
            if ie < 0 { return (); }
            if e >= 0 && ie != e { return (); }
            e = ie;
            // the axis line: the axis point with its e component dropped
            let q = [ax.point.x, ax.point.y, ax.point.z]; q[e] = 0.0;
            if pt == () { pt = q; } else if abs(q[0] - pt[0]) + abs(q[1] - pt[1]) + abs(q[2] - pt[2]) > 1e-5 { return (); }
        } else if k == "plane" { } else { return (); }
    }
    if e < 0 { return (); }
    for f in g { if f.kind() == "plane" && !par(f.normal(), e) { return (); } }
    let cyl = []; let cones = [];
    let bb = gbox(g); let lo = comp(bb.min, e); let hi = comp(bb.max, e);
    for f in g {
        let fb = f.shape().bbox(); let a = comp(fb.min, e); let b = comp(fb.max, e);
        if f.kind() == "cylinder" { cyl.push(#{r: f.axis().radius, lo: a, hi: b}); }
        if f.kind() == "cone" {
            let ra = 1e9; let rb = 0.0;
            for ed in f.edges() { let c = ed.circle(); if c != () { if c.radius < ra { ra = c.radius; } if c.radius > rb { rb = c.radius; } } }
            cones.push(#{rmin: ra, rmax: rb, lo: a, hi: b});
        }
    }
    if cyl.len() == 0 && cones.len() == 1 && g.len() == 1 {
        // a countersink on a hole the body already has
        let f = g[0]; let r_lo = 0.0; let r_hi = 0.0;
        for ed in f.edges() { let c = ed.circle(); if c != () { if abs(comp(c.center, e) - lo) < 1e-5 { r_lo = c.radius; } else { r_hi = c.radius; } } }
        if min(r_lo, r_hi) < 0.05 { return (); }
        let from_hi = r_hi > r_lo;
        let at1 = |h| { let q = [pt[0], pt[1], pt[2]]; q[e] = h; q };
        let open = if from_hi { hi } else { lo };
        let beyond = if from_hi { hi + 0.01 } else { lo - 0.01 };
        if P.classify(at1.call(beyond), 1e-6) != "out" { return (); }
        let rmax = max(r_lo, r_hi); let rmin = min(r_lo, r_hi);
        return #{kind: "hole", e: e, from_hi: from_hi, open: open, at: at1.call(open), dia: 2.0 * rmin, through: false, type: "countersink",
                 depth: hi - lo, cs_d: 2.0 * rmax, cs_angle: 2.0 * atan((rmax - rmin) / (hi - lo)) * 180.0 / PI(), tip: false};
    }
    if cyl.len() == 0 { return (); }
    let at = |h| { let q = [pt[0], pt[1], pt[2]]; q[e] = h; q };
    let out_hi = P.classify(at.call(hi + 0.01), 1e-6) == "out";
    let out_lo = P.classify(at.call(lo - 0.01), 1e-6) == "out";
    if !out_hi && !out_lo { return (); }
    // a hole, not a boss: its axis is outside the part
    let sm = cyl[0]; for c in cyl { if c.r < sm.r { sm = c; } }
    if P.classify(at.call((sm.lo + sm.hi) / 2.0), 1e-6) != "out" { return (); }
    // which end it is drilled from: the end with the widest part
    let wide_hi = 0.0; let wide_lo = 0.0;
    for c in cyl { if abs(c.hi - hi) < 1e-5 && c.r > wide_hi { wide_hi = c.r; } if abs(c.lo - lo) < 1e-5 && c.r > wide_lo { wide_lo = c.r; } }
    for c in cones { if abs(c.hi - hi) < 1e-5 && c.rmax > wide_hi { wide_hi = c.rmax; } if abs(c.lo - lo) < 1e-5 && c.rmax > wide_lo { wide_lo = c.rmax; } }
    let from_hi = if out_hi && out_lo { wide_hi >= wide_lo } else { out_hi };
    let through = false;
    // the drilled hole: the narrowest cylinder
    let small = cyl[0]; for c in cyl { if c.r < small.r { small = c; } }
    let res = #{kind: "hole", e: e, from_hi: from_hi, open: if from_hi { hi } else { lo }, at: at.call(if from_hi { hi } else { lo }), dia: 2.0 * small.r, through: through, type: "simple"};
    res.depth = if from_hi { hi - small.lo } else { small.hi - lo };
    let tip = false;
    for c in cones { if (from_hi && abs(c.lo - lo) < 1e-5 && !through) || (!from_hi && abs(c.hi - hi) < 1e-5 && !through) { tip = true; } }
    res.tip = tip;
    for c in cones {
        let at_open = if from_hi { abs(c.hi - hi) < 1e-5 } else { abs(c.lo - lo) < 1e-5 };
        if at_open && c.rmax > small.r + 1e-6 {
            res.type = "countersink"; res.cs_d = 2.0 * c.rmax;
            res.cs_angle = 2.0 * atan((c.rmax - c.rmin) / (c.hi - c.lo)) * 180.0 / PI();
        }
    }
    for c in cyl {
        let at_open = if from_hi { abs(c.hi - hi) < 1e-5 } else { abs(c.lo - lo) < 1e-5 };
        if at_open && c.r > small.r + 1e-6 && res.type == "simple" { res.type = "counterbore"; res.cb_d = 2.0 * c.r; res.cb_depth = c.hi - c.lo; }
    }
    // anything else (two steps, a cone mid-way) isn't a plain hole
    let n = cyl.len() + cones.len();
    let want = 1 + (if res.type == "simple" { 0 } else { 1 }) + (if tip { 1 } else { 0 });
    if n != want { return (); }
    res
}
// chamfers and fillets: each sharp edge the group replaced, with the blend nearest to it
fn blend_of(P, g) {
    for f in g { let k = f.kind(); if !(k == "plane" || k == "cone" || k == "cylinder" || k == "torus" || k == "sphere") { return (); } }
    let D = P.delete_faces(g);
    if abs(D.volume() - P.volume()) < 1e-7 { print("blend: delete did nothing"); return (); }
    let out = [];
    for ed in D.edges() {
        let m = ed.mid();
        if P.classify(m, 1e-5) == "on" { continue; }
        let best = 1e9; let bf = ();
        for x in g { let d = distance(m, x.closest(m)); if d < best { best = d; bf = x; } }
        if bf == () || best < 1e-5 { continue; }
        let k = bf.kind();
        if k == "plane" || k == "cone" {
            out.push(#{kind: "chamfer", size: best * sqrt(2.0), at: a3(m)});
        } else {
            let r = 0.0;
            if k == "torus" { r = 1e9; for e2 in bf.edges() { let c = e2.circle(); if c != () && c.radius < r { r = c.radius; } } }
            else { r = bf.axis().radius; }
            // a 90° corner: the sharp edge is r(√2 - 1) from the round

            out.push(#{kind: "fillet", size: r, at: a3(m)});
        }
    }
    if out.len() == 0 { return (); }
    #{kind: "blend", edges: out, dvol: D.volume() - P.volume()}
}
fn gbox(g) {
    let s = compound(g.map(|f| f.shape()));
    s.bbox()
}

let P = import_step(IN).solids()[0];
// main axis: the one most of the surface is extruded along
if AX < 0 {
    let best = 1e18;
    for i in 0..3 {
        let a = 0.0; let caps = 0.0;
        for f in P.faces() { if !prismatic(f, i) { a += f.area(); } else if f.kind() == "plane" && par(f.normal(), i) { caps += f.area(); } }
        let score = a - 1e-3 * caps;
        if score < best { best = score; AX = i; }
    }
}
let res = #{vol: P.volume(), axis: AX};
let other = [];
for f in P.faces() { if !prismatic(f, AX) { other.push(f); } }
// a face whose every edge borders the feature (a hole's bottom, a step between two bores) belongs to it
let all = P.faces();
let changed = true;
while changed {
    changed = false;
    let gs0 = groups(other);
    for f in all {
        if other.some(|g| same(g, f)) { continue; }
        let es = f.edges();
        let ok = true;
        for e in es {
            let hit = false;
            for g in other { for x in g.edges() { if same(x, e) { hit = true; break; } } if hit { break; } }
            if !hit { ok = false; break; }
        }
        if ok && f.kind() == "plane" && f.area() < 0.5 * P.area() / 6.0 { other.push(f); changed = true; }
    }
}
let gs = groups(other);
let feats = [];
let handled = [];
let leftover = [];
for g in gs {
    let e = group_axis(g);
    let kinds = g.map(|f| f.kind());
    if e < 0 || g.some(|f| f.kind() == "cylinder") {
        let h = ();
        try { h = hole_of(P, g); } catch (err) { print("hole? " + err); }
        if h != () {
            let ok = true;
            try { let D = P.delete_faces(g); if abs(D.volume() - P.volume()) < 1e-6 { ok = false; } } catch (err) { ok = false; }
            h.kinds = kinds;
            if ok { feats.push(h); for x in g { handled.push(x); } continue; }
        }
    }
    if e < 0 || kinds.some(|k| k == "cylinder") {
        let b = ();
        try { b = blend_of(P, g); } catch (err) { print("blend? " + err); }
        if b != () { b.kinds = kinds; feats.push(b); for x in g { handled.push(x); } continue; }
    }
    if e < 0 { leftover.push(#{kinds: kinds, bbox: #{min: a3(gbox(g).min), max: a3(gbox(g).max)}}); continue; }
    let D = ();
    try { D = P.delete_faces(g); } catch (err) { leftover.push(#{kinds: kinds, why: "" + err}); continue; }
    let bb = gbox(g);
    let lo = comp(bb.min, e); let hi = comp(bb.max, e);
    let mid = (lo + hi) / 2.0;
    let sp = section(P, e, mid); let sd = section(D, e, mid);
    let rem = []; let add = [];
    try { rem = region_cut(sd, sp); add = region_cut(sp, sd); } catch (err) { leftover.push(#{kinds: kinds, why: "2d " + err}); continue; }
    let dv = D.volume() - P.volume();
    if abs(dv) < 1e-6 { leftover.push(#{kinds: kinds, why: "delete did nothing"}); continue; }
    let f = #{kinds: kinds, e: e, lo: lo, hi: hi, dvol: dv, remove: face_list_json(rem), add: face_list_json(add)};
    feats.push(f);
    for x in g { handled.push(x); }
}
let Q = P;
if handled.len() > 0 {
    try { Q = P.delete_faces(handled); } catch (err) {
        print("all-at-once delete failed: " + err);
        for f in handled {
            let pick = Q.faces().filter(|g| distance(g.center(), f.center()) < 1e-6 && abs(g.area() - f.area()) < 1e-6);
            try { Q = Q.delete_faces(pick); } catch (e2) { }
        }
    }
}
res.qvalid = Q.is_valid();
res.base = slabs(Q, AX);
res.features = feats;
res.leftover = leftover;
write_json(OUT, res);
print("vol " + P.volume() + " groups " + gs.len() + " feats " + feats.len() + " leftover " + leftover.len() + " Q " + Q.volume());
