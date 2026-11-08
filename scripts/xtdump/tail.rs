
pub fn tree(bytes: &[u8]) {
    let xt = Xt::parse(bytes).unwrap();
    let mut used = std::collections::HashSet::new();
    for n in xt.nodes.values() { if n.t == 11 { used.insert(n.ptr("part")); } }
    let mut roots: Vec<u32> = xt.nodes.iter().filter(|(i, n)| (n.t == 10 || n.t == 12) && !used.contains(i)).map(|(i, _)| *i).collect();
    roots.sort();
    fn bbox(xt: &Xt, b: u32, xf: Xf) -> (DVec3, DVec3, usize) {
        let mut lo = DVec3::splat(1e9); let mut hi = DVec3::splat(-1e9); let mut nf = 0;
        // vertices via all point nodes owned by body: walk faces
        let body = xt.node(b).unwrap();
        for r in xt.chain(body.ptr("region"), "next") { let Some(region) = xt.node(r) else {continue};
          for sh in xt.chain(region.ptr("shell"), "next") { let Some(shell) = xt.node(sh) else {continue};
            for (first, next) in [("back_faces", "next_back"), ("front_faces", "next_front")] {
              for f in xt.chain(shell.ptr(first), next) { nf += 1; let face = xt.node(f).unwrap();
                for l in xt.chain(face.ptr("loop"), "next") { let lp = xt.node(l).unwrap();
                  for fin in xt.chain(lp.ptr("fin"), "forward") { let fin = xt.node(fin).unwrap();
                    if let Some(v) = xt.node(fin.ptr("vertex")).and_then(|v| xt.node(v.ptr("point"))) {
                      let p = (xf.m * v.v3("pvec") + xf.t) * 1000.0; lo = lo.min(p); hi = hi.max(p); } } } } } } }
        (lo, hi, nf)
    }
    fn walk(xt: &Xt, i: u32, xf: Xf, d: usize) {
        let n = xt.node(i).unwrap();
        let name = xt.name_of(i).unwrap_or_default();
        if n.t == 12 {
            let (lo, hi, nf) = bbox(xt, i, xf);
            println!("{}B{} '{}' faces {} lo [{:.1} {:.1} {:.1}] hi [{:.1} {:.1} {:.1}]", "  ".repeat(d), i, name, nf, lo.x, lo.y, lo.z, hi.x, hi.y, hi.z);
        } else {
            println!("{}A{} '{}'", "  ".repeat(d), i, name);
            for inst in xt.chain(n.ptr("sub_instance"), "next_in_part") {
                let inst = xt.node(inst).unwrap();
                let local = xt.node(inst.ptr("transform")).map(Xf::of).unwrap_or(Xf::IDENTITY);
                walk(xt, inst.ptr("part"), xf.then(local), d + 1);
            }
        }
    }
    for r in roots { walk(&xt, r, Xf::IDENTITY, 0); }
}
pub fn stats(bytes: &[u8]) {
    let xt = Xt::parse(bytes).unwrap();
    let mut nocurve = 0; let mut fincurve = 0; let mut tot=0;
    for n in xt.nodes.values() { if n.t == 16 { tot+=1; if n.ptr("curve") == 0 { nocurve += 1;
        let fin = xt.node(n.ptr("fin")).unwrap(); if fin.ptr("curve") != 0 { fincurve += 1; if fincurve < 3 { let c = xt.node(fin.ptr("curve")).unwrap(); eprintln!("fin curve type {} fields {:?}", c.t, c.fields.iter().map(|f| f.name.clone()).collect::<Vec<_>>()); } } } } }
    eprintln!("edges {tot} no curve {nocurve} with fin curve {fincurve}");
    let mut types = std::collections::BTreeMap::new();
    for n in xt.nodes.values() { *types.entry(n.t).or_insert(0) += 1; }
    eprintln!("{types:?}");
    // periodic surfaces
    let mut k = 0;
    for n in xt.nodes.values() { if n.t == 126 && k < 5 { k+=1; eprintln!("126: {:?}", n.fields.iter().zip(n.vals.iter()).filter(|(f,_)| f.code != Code::Ptr).map(|(f,v)| format!("{}={:?}", f.name, v)).collect::<Vec<_>>()); } }
}
pub fn blends(bytes: &[u8]) {
    let xt = Xt::parse(bytes).unwrap();
    for (i, n) in xt.nodes.iter() { if n.t == 56 {
        let sp = xt.node(n.ptr("spine")).map(|c| c.t).unwrap_or(0);
        let ss: Vec<u16> = n.get("surface").iter().map(|&p| xt.node(p as u32).map(|c| c.t).unwrap_or(0)).collect();
        let mut o = n.ptr("owner"); let mut k=0; while let Some(on) = xt.node(o) { if on.t == 12 || k > 20 { break; } o = on.ptr("owner"); k+=1; }
        eprintln!("BODY {o} {}", xt.name_of(o).unwrap_or_default());
        eprintln!("blend {i} type {} spine {sp} surfs {ss:?} range {:?} thumb {:?} owner {}", n.ch("blend_type") as char, n.get("range"), n.get("thumb_weight"), n.ptr("owner"));
    } }
}
/// JSON lines: one per face of each placed body (mm, placed), with its loops' edges.
pub fn dump(bytes: &[u8], want: &[u32]) {
    let xt = Xt::parse(bytes).unwrap();
    let bodies = xt.placed_bodies();
    let mut s = Step::default();
    let mut seenb = std::collections::HashMap::new();
    for (body, xf) in bodies.iter() {
        if !want.is_empty() && !want.contains(body) { continue; }
        let inst = { let c = seenb.entry(*body).or_insert(0); *c += 1; *c };
        let c = Conv { xt: &xt, s: &mut s, xf: Xf::IDENTITY, verts: HashMap::new(), edges: HashMap::new(), skipped: 0 };
        let b = xt.node(*body).unwrap();
        println!("{{\"body\":{},\"inst\":{},\"name\":{:?},\"rot\":{:?},\"t\":{:?}}}", body, inst, xt.name_of(*body).unwrap_or_default(), xf.m.to_cols_array(), (xf.t*1000.0).to_array());
        for r in xt.chain(b.ptr("region"), "next") { let region = xt.node(r).unwrap();
          for sh in xt.chain(region.ptr("shell"), "next") { let shell = xt.node(sh).unwrap();
            for (first, next) in [("back_faces", "next_back"), ("front_faces", "next_front")] {
              for f in xt.chain(shell.ptr(first), next) {
                let face = xt.node(f).unwrap();
                let sn = xt.node(face.ptr("surface"));
                let st = sn.map(|n| n.t).unwrap_or(0);
                let fsame = sn.map(|n| face.plus("sense") == n.plus("orientation")).unwrap_or(true);
                let mut geo = String::new();
                if let Some(n) = sn { match n.t {
                    50 => geo = format!("\"o\":{:?},\"n\":{:?}", c.p(n.v3("pvec")).to_array(), c.d(n.v3("normal")).to_array()),
                    51 => geo = format!("\"o\":{:?},\"a\":{:?},\"r\":{}", c.p(n.v3("pvec")).to_array(), c.d(n.v3("axis")).to_array(), c.len(n.num("radius"))),
                    52 => geo = format!("\"o\":{:?},\"a\":{:?},\"r\":{},\"sin\":{},\"cos\":{}", c.p(n.v3("pvec")).to_array(), c.d(n.v3("axis")).to_array(), c.len(n.num("radius")), n.num("sin"), n.num("cos")),
                    53 | 54 => geo = format!("\"o\":{:?},\"a\":{:?}", c.p(n.v3("centre")).to_array(), c.d(n.v3("axis")).to_array()),
                    _ => {} } }
                let mut loops = vec![];
                for l in xt.chain(face.ptr("loop"), "next") { let lp = xt.node(l).unwrap();
                    let mut es = vec![];
                    for fin in xt.chain(lp.ptr("fin"), "forward") { let fin = xt.node(fin).unwrap();
                        let e = fin.ptr("edge"); if e == 0 { continue; }
                        let edge = xt.node(e).unwrap();
                        let other = xt.node(fin.ptr("other")).filter(|o| o.t == 17);
                        let (mut st_, mut en) = (0, 0);
                        for f in std::iter::once(fin).chain(other) { if f.plus("sense") { en = f.ptr("vertex"); } else { st_ = f.ptr("vertex"); } }
                        let at = |v: u32| xt.node(v).and_then(|v| xt.node(v.ptr("point"))).map(|p| format!("{:?}", c.p(p.v3("pvec")).to_array())).unwrap_or("null".into());
                        let mut cid = edge.ptr("curve"); if cid == 0 { cid = fin.ptr("curve"); }
                        let cn = xt.node(cid);
                        let mut ct = cn.map(|n| n.t).unwrap_or(0);
                        let mut cg = String::new();
                        if let Some(n) = cn { let n = if n.t == 133 { xt.node(n.ptr("basis")).unwrap_or(n) } else { n }; ct = n.t; match n.t {
                            31 => cg = format!(",\"c\":{:?},\"n\":{:?},\"r\":{},\"cplus\":{}", c.p(n.v3("centre")).to_array(), c.d(n.v3("normal")).to_array(), c.len(n.num("radius")), n.plus("orientation")),
                            _ => {} } }
                        let pts = if ct != 30 && ct != 31 { c.sample(cid).map(|p| p.iter().map(|q| q.to_array()).collect::<Vec<_>>()).unwrap_or_default() } else { vec![] };
                        es.push(format!("{{\"e\":{e},\"t\":{ct},\"s\":{},\"en\":{},\"fin\":{}{cg},\"pts\":{:?}}}", at(st_), at(en), fin.plus("sense"), pts));
                    }
                    loops.push(format!("[{}]", es.join(",")));
                }
                println!("{{\"f\":{f},\"st\":{st},\"same\":{fsame},{geo}{}\"loops\":[{}]}}", if geo.is_empty() {""} else {","}, loops.join(","));
              } } } }
    }
}
pub fn one(bytes: &[u8], body: u32) -> String {
    let xt = Xt::parse(bytes).unwrap();
    let mut s = Step::default();
    let ctx = s.header();
    let mut c = Conv { xt: &xt, s: &mut s, xf: Xf::IDENTITY, verts: HashMap::new(), edges: HashMap::new(), skipped: 0 };
    let items = c.body(body).unwrap();
    let name = xt.name_of(body).unwrap_or_default();
    s.product(&name, &items, ctx);
    s.finish("part")
}
pub fn treejson(bytes: &[u8]) {
    let xt = Xt::parse(bytes).unwrap();
    fn walk(xt: &Xt, i: u32, xf: Xf, local: Xf) -> String {
        let n = xt.node(i).unwrap();
        let name = xt.name_of(i).unwrap_or_default();
        let m = |x: Xf| format!("{{\"m\":{:?},\"t\":{:?}}}", x.m.to_cols_array(), (x.t * 1000.0).to_array());
        if n.t == 12 {
            let col = xt.colour_of(i).map(|c| format!("{:?}", c)).unwrap_or("null".into());
            format!("{{\"body\":{i},\"name\":{name:?},\"world\":{},\"local\":{},\"colour\":{col}}}", m(xf), m(local))
        } else {
            let kids: Vec<String> = xt.chain(n.ptr("sub_instance"), "next_in_part").iter().map(|&inst| {
                let inst = xt.node(inst).unwrap();
                let l = xt.node(inst.ptr("transform")).map(Xf::of).unwrap_or(Xf::IDENTITY);
                walk(xt, inst.ptr("part"), xf.then(l), l)
            }).collect();
            format!("{{\"asm\":{i},\"name\":{name:?},\"world\":{},\"local\":{},\"kids\":[{}]}}", m(xf), m(local), kids.join(","))
        }
    }
    println!("{}", walk(&xt, 1, Xf::IDENTITY, Xf::IDENTITY));
}
/// spec: lines "body m0..m8 t0 t1 t2 name" (m column-major, t in mm) -> one STEP with a product per line
pub fn placed(bytes: &[u8], spec: &str) -> String {
    let xt = Xt::parse(bytes).unwrap();
    let mut s = Step::default();
    let ctx = s.header();
    let mut styled = vec![];
    for line in spec.lines() {
        let v: Vec<&str> = line.splitn(14, ' ').collect();
        if v.len() < 14 { continue; }
        let body: u32 = v[0].parse().unwrap();
        let f: Vec<f64> = v[1..13].iter().map(|x| x.parse().unwrap()).collect();
        let xf = Xf { m: DMat3::from_cols_array(&[f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8]]), t: DVec3::new(f[9], f[10], f[11]) / 1000.0 };
        let mut c = Conv { xt: &xt, s: &mut s, xf, verts: HashMap::new(), edges: HashMap::new(), skipped: 0 };
        let items = c.body(body).unwrap();
        if let Some(rgb) = xt.colour_of(body) { for &(it, _) in &items { styled.push(s.style(it, rgb)); } }
        s.product(v[13], &items, ctx);
    }
    if !styled.is_empty() { let list = refs(&styled); s.add(format!("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({list}),#{ctx})")); }
    s.finish("group")
}
