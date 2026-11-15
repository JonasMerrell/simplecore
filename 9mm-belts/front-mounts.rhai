// 9 mm belt front motor mounts, both corners, rev A (2026-11-15).
// CNC plates; motor inboard of the side panel: idler I1 turns the joint run inboard, the motor pulley turns it 180 deg,
// idler I3 puts it on the side run (see beltpath.py). World coordinates of the Printer assembly, mm.
// The -Y (right) mount is the mirror image about y = 226.5 with the belt on the lower level.
// Run from this folder: rcad script front-mounts.rhai
fn zplane(d, z, name) { d.feature("plane", #{mode: "offset", base: #{kind: "origin_plane", plane: "Top"}, offset: z}, name) }
fn yplane(d, y, name) { d.feature("plane", #{mode: "offset", base: #{kind: "origin_plane", plane: "Front"}, offset: -y}, name) }
fn ext(d, s, depth, up, op, name) { d.feature("extrude", #{profiles: [s], depth: depth, op: op, opposite: !up}, name) }
fn exty(d, s, depth, plus, op, name) { d.feature("extrude", #{profiles: [s], depth: depth, op: op, opposite: plus}, name) }
fn my(p, m) { if m { [p[0], 453.0 - p[1]] } else { p } }
fn cyl(x, y, z0, z1, r) { cylinder(vec3(x, y, z0), vec3(0, 0, 1), r, z1 - z0) }
fn ring(x, y, z0, z1, r, ri) { cyl(x, y, z0, z1, r) - cyl(x, y, z0 - 1, z1 + 1, ri) }
fn stack(x, y, z0) { ring(x, y, z0, z0 + 12.0, 6.5, 2.5) + ring(x, y, z0, z0 + 1.0, 7.5, 2.5) + ring(x, y, z0 + 11.0, z0 + 12.0, 7.5, 2.5) }

let d = new_document();
d.variable("plate_t", 6);
d.variable("brg_od", 13);           // 695 bearing 5 x 13 x 4
d.variable("brg_w", 4);
d.variable("pin_d", 5);
d.variable("m5_clear", 5.5);
d.variable("m5_tap", 4.2);
d.variable("m4_clear", 4.5);
d.variable("m4_tap", 3.3);
d.variable("m3_clear", 3.4);
d.variable("m3_head", 6.5);
d.variable("shaft_clear", 8);

let Z_LO = 429.0; let Z_BAY = 435.0; let Z_ROOF = 461.2;
let P = [3.5, 422.0];                                            // drive shaft
let PINS = [[16.74, 443.8], [4.64, 455.89]];                     // I1, I3
let STAND = [[20.0, 420.0], [21.0, 456.9], [-14.0, 424.0]];      // M5 from the top, tapped in the lower plate
let BAR = [[-22.5, 450.3], [-8.5, 450.3]];                       // M4 into the ends of the spine bar
let MOTOR = [[P[0] - 15.5, P[1] - 15.5], [P[0] + 15.5, P[1] - 15.5], [P[0] - 15.5, P[1] + 15.5], [P[0] + 15.5, P[1] + 15.5]];
let OUT = [[-25.3, 401.0], [27.3, 401.0], [27.3, 466.0], [-5.3, 466.0], [-5.3, 456.3], [-25.3, 456.3]];   // 0.2 clear of the front upright
let BAR_BOX = [[-25.3, 444.3], [-5.7, 456.3]];                   // spine bar against the upright's inner face

let hw = []; let show = [];
for m in [false, true] {
    let side = if m { "-Y" } else { "+Y" };
    let p0 = zplane(d, Z_LO, side + " lower plate underside");
    let s = d.sketch(p0, side + " lower plate outline"); s.polygon(OUT.map(|p| my(p, m)));
    ext(d, s, "plate_t", true, "new", side + " lower plate");
    let pt = zplane(d, Z_BAY, side + " bay floor");
    s = d.sketch(pt, side + " lower plate holes");
    for p in PINS { s.circle(my(p, m), "pin_d"); }
    for p in STAND { s.circle(my(p, m), "m5_tap"); }
    for p in BAR { s.circle(my(p, m), "m4_clear"); }
    s.circle(my(P, m), "shaft_clear");
    ext(d, s, "plate_t", false, "remove", side + " lower plate holes");
    s = d.sketch(pt, side + " lower bearing bore"); s.circle(my(P, m), "brg_od");
    ext(d, s, "brg_w", false, "remove", side + " lower bearing pocket");

    let pu = zplane(d, Z_ROOF, side + " bay roof");
    s = d.sketch(pu, side + " upper plate outline"); s.polygon(OUT.map(|p| my(p, m)));
    ext(d, s, "plate_t", true, "new", side + " upper plate");
    s = d.sketch(pu, side + " upper plate holes");
    for p in PINS { s.circle(my(p, m), "pin_d"); }
    for p in STAND { s.circle(my(p, m), "m5_clear"); }
    for p in BAR { s.circle(my(p, m), "m4_clear"); }
    for p in MOTOR { s.circle(my(p, m), "m3_clear"); }
    s.circle(my(P, m), "shaft_clear");
    ext(d, s, "plate_t", true, "remove", side + " upper plate holes");
    s = d.sketch(pu, side + " upper bearing bore"); s.circle(my(P, m), "brg_od");
    ext(d, s, "brg_w", true, "remove", side + " upper bearing pocket");
    s = d.sketch(pu, side + " motor screw counterbores");
    for p in MOTOR { s.circle(my(p, m), "m3_head"); }
    ext(d, s, 3.4, true, "remove", side + " motor screw counterbores");

    // spine bar: 19.6 x 12 x 26.2, between the plates, bolted to the upright's inner face with two M5
    s = d.sketch(pt, side + " spine bar section"); s.rect_corners(my(BAR_BOX[0], m), my(BAR_BOX[1], m));
    ext(d, s, 26.2, true, "new", side + " spine bar");
    s = d.sketch(pt, side + " spine bar M4 (bottom)"); for p in BAR { s.circle(my(p, m), "m4_tap"); }
    ext(d, s, 8, true, "remove", side + " spine bar M4 tapped, bottom end");
    s = d.sketch(pu, side + " spine bar M4 (top)"); for p in BAR { s.circle(my(p, m), "m4_tap"); }
    ext(d, s, 8, false, "remove", side + " spine bar M4 tapped, top end");
    let yface = if m { 453.0 - 444.3 } else { 444.3 };
    let py = yplane(d, yface, side + " spine bar inner face");
    s = d.sketch(py, side + " spine bar M5 to upright"); s.circle([-15.5, 442.0], "m5_clear"); s.circle([-15.5, 454.0], "m5_clear");
    exty(d, s, 12, !m, "remove", side + " spine bar M5 through to the upright");

    let q = my(P, m);
    let zb = if m { 436.06 } else { 448.06 };        // this corner's belt level (stack base)
    let zo = if m { 448.06 } else { 435.0 };         // the empty level gets a plain sleeve
    let pulley = ring(q[0], q[1], zb - 1.0, zb + 13.0, 8.0, 2.5) - ring(q[0], q[1], zb + 0.5, zb + 11.5, 9.0, 6.1);
    let parts = [
        #{shape: cyl(q[0], q[1], 431.0, 478.2, 2.5), color: "#404040"},
        #{shape: ring(q[0], q[1], 431.0, 435.0, 6.5, 2.5), color: "#d08020"},
        #{shape: ring(q[0], q[1], 461.2, 465.2, 6.5, 2.5), color: "#d08020"},
        #{shape: pulley, color: "#2060c0"},
        #{shape: cyl(q[0], q[1], 468.7, 493.7, 9.5), color: "#c03030"},
        #{shape: block(vec3(q[0] - 21.15, q[1] - 21.15, 502.2), vec3(q[0] + 21.15, q[1] + 21.15, 542.2)) + cyl(q[0], q[1], 500.2, 502.2, 11.0) + cyl(q[0], q[1], 478.2, 500.2, 2.5), color: "#202020"}];
    for p in MOTOR { let a = my(p, m); parts.push(#{shape: cyl(a[0], a[1], 467.2, 502.2, 3.5), color: "#909aa5"}); }
    for p in STAND { let a = my(p, m); parts.push(#{shape: cyl(a[0], a[1], 435.0, 461.2, 4.0), color: "#909aa5"}); }
    for p in PINS { let a = my(p, m);
        parts.push(#{shape: cyl(a[0], a[1], 429.0, 467.2, 2.5), color: "#e0e0e0"});
        parts.push(#{shape: stack(a[0], a[1], zb), color: "#30a060"});
        parts.push(#{shape: ring(a[0], a[1], zo + 0.06, zo + 13.0, 4.0, 2.5), color: "#909aa5"}); }
    for h in parts { hw.push(h.shape); if !m { show.push(h); } }
}
let es = d.edges().filter(|e| e.type == "line" && (e.start[0] - e.end[0]).abs() < 1e-6 && (e.start[1] - e.end[1]).abs() < 1e-6 && e.length_mm > 5.9 && e.length_mm < 6.1);
d.fillet(es, 3);
let names = ["Front motor mount lower plate (+Y)", "Front motor mount upper plate (+Y)", "Front motor mount spine bar (+Y)", "Front motor mount lower plate (-Y)", "Front motor mount upper plate (-Y)", "Front motor mount spine bar (-Y)"];
let ps = d.parts();
for i in 0..ps.len() { d.tool("set_part", #{body: ps[i].body, name: names[i], material: "Aluminium 6061", color: "#b8bec6"}); }
print(d.parts().map(|p| `${p.name}: ${p.volume_mm3} mm3, bbox ${p.bbox_mm}`));
d.save("front-mounts.json");
d.export_file("front-mount-plates.step");
export_step(hw, "front-mount-hardware.step");
let plates = import_step("front-mount-plates.step");
let near = plates & block(vec3(-40, 380, 420), vec3(40, 480, 470));
show.push(#{shape: near, color: "#b8bec6"});
show.push(#{shape: block(vec3(-25.5, 456.5, 400), vec3(-5.5, 476.5, 520)), color: "#303030", opacity: 0.35});   // front upright
render(show, #{path: "front-mount-revA.png", width: 1400, height: 1100, eye: [330, 200, 700], target: [3, 432, 478], up: [0, 0, 1], fov: 26});
let bay = show.filter(|h| h.shape.bbox().min.z < 462.0 && h.shape.bbox().max.z < 480.0);
bay.pop(); bay.pop();
bay.push(#{shape: plates & block(vec3(-40, 380, 420), vec3(40, 480, 461.0)), color: "#b8bec6"});
render(bay, #{path: "front-mount-revA-bay.png", width: 1100, height: 1100, eye: [1, 433, 900], target: [1, 433, 440], up: [1, 0, 0], fov: 0});
