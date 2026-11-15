// 9 mm belt rear motor mounts, both corners, rev B (2026-11-15).
// CNC plates on round standoffs; pulley on its own shaft between two bearings; idlers on the belt path of beltpath.py.
// World coordinates of the Printer assembly, mm. The -Y mount is the mirror image about y = 226.5.
// Run from this folder: rcad script rear-mounts.rhai   (writes rear-mounts.json, .step files and the picture)
fn zplane(d, z, name) { d.feature("plane", #{mode: "offset", base: #{kind: "origin_plane", plane: "Top"}, offset: z}, name) }
fn ext(d, s, depth, up, op, name) { d.feature("extrude", #{profiles: [s], depth: depth, op: op, opposite: !up}, name) }
fn my(p, m) { if m { [p[0], 453.0 - p[1]] } else { p } }
fn cyl(x, y, z0, z1, r) { cylinder(vec3(x, y, z0), vec3(0, 0, 1), r, z1 - z0) }
fn ring(x, y, z0, z1, r, ri) { cyl(x, y, z0, z1, r) - cyl(x, y, z0 - 1, z1 + 1, ri) }
// F695 + 695 + F695 stack, 12 mm tall from z0
fn stack(x, y, z0) { ring(x, y, z0, z0 + 12.0, 6.5, 2.5) + ring(x, y, z0, z0 + 1.0, 7.5, 2.5) + ring(x, y, z0 + 11.0, z0 + 12.0, 7.5, 2.5) }

let d = new_document();
d.variable("plate_t", 6);           // 6061 plate
d.variable("brg_od", 13);           // 695 bearing 5 x 13 x 4, light press fit
d.variable("brg_w", 4);
d.variable("pin_d", 5);             // idler pins, same as the XY joints
d.variable("m5_clear", 5.5);
d.variable("m5_tap", 4.2);
d.variable("m3_clear", 3.4);
d.variable("m3_head", 6.5);
d.variable("shaft_clear", 8);       // hole behind each bearing for the 5 mm shaft

let Z_LO = 429.0; let Z_BAY = 435.0; let Z_ROOF = 461.2;         // lower plate 429-435, bay 435-461.2, upper plate 461.2-467.2
let P = [403.3, 433.0];                                          // drive shaft
let PINS = [[385.5, 455.36], [391.0, 422.4]];                    // A (turns both belts off the side runs), C (wraps the belt onto the pulley; other belt's guide B)
let FRAME = [[414.5, 400.0], [414.5, 441.0], [399.5, 466.5]];    // M5 through the stack into T-nuts in the top slots
let TIE = [[386.0, 402.0]];                                      // fourth standoff, M5 tapped in the lower plate
let MOTOR = [[P[0] - 15.5, P[1] - 15.5], [P[0] + 15.5, P[1] - 15.5], [P[0] - 15.5, P[1] + 15.5], [P[0] + 15.5, P[1] + 15.5]];
let OUT = [[380.0, 394.0], [424.5, 394.0], [424.5, 456.3], [404.3, 456.3], [404.3, 476.5], [380.0, 476.5]];   // 0.2 clear of the upright

let hw = []; let show = [];
for m in [false, true] {
    let side = if m { "-Y" } else { "+Y" };
    let p0 = zplane(d, Z_LO, side + " lower plate underside");
    let s = d.sketch(p0, side + " lower plate outline"); s.polygon(OUT.map(|p| my(p, m)));
    ext(d, s, "plate_t", true, "new", side + " lower plate");
    let pt = zplane(d, Z_BAY, side + " lower plate top (bay floor)");
    s = d.sketch(pt, side + " lower plate holes");
    for p in PINS { s.circle(my(p, m), "pin_d"); }
    for p in FRAME { s.circle(my(p, m), "m5_clear"); }
    for p in TIE { s.circle(my(p, m), "m5_tap"); }
    s.circle(my(P, m), "shaft_clear");
    ext(d, s, "plate_t", false, "remove", side + " lower plate holes");
    s = d.sketch(pt, side + " lower bearing bore"); s.circle(my(P, m), "brg_od");
    ext(d, s, "brg_w", false, "remove", side + " lower bearing pocket");

    let pu = zplane(d, Z_ROOF, side + " upper plate underside (bay roof)");
    s = d.sketch(pu, side + " upper plate outline"); s.polygon(OUT.map(|p| my(p, m)));
    ext(d, s, "plate_t", true, "new", side + " upper plate");
    s = d.sketch(pu, side + " upper plate holes");
    for p in PINS { s.circle(my(p, m), "pin_d"); }
    for p in FRAME + TIE { s.circle(my(p, m), "m5_clear"); }
    for p in MOTOR { s.circle(my(p, m), "m3_clear"); }
    s.circle(my(P, m), "shaft_clear");
    ext(d, s, "plate_t", true, "remove", side + " upper plate holes");
    s = d.sketch(pu, side + " upper bearing bore"); s.circle(my(P, m), "brg_od");
    ext(d, s, "brg_w", true, "remove", side + " upper bearing pocket");
    s = d.sketch(pu, side + " motor screw counterbores");
    for p in MOTOR { s.circle(my(p, m), "m3_head"); }
    ext(d, s, 3.4, true, "remove", side + " motor screw counterbores");

    // hardware as plain solids (picture and clearance only)
    let q = my(P, m);
    let zp = if m { 435.06 } else { 447.06 };        // pulley on the lower belt at -Y, on the upper belt at +Y
    let pulley = ring(q[0], q[1], zp, zp + 14.0, 8.0, 2.5) - ring(q[0], q[1], zp + 1.5, zp + 12.5, 9.0, 6.1);
    let parts = [
        #{shape: cyl(q[0], q[1], 431.0, 478.2, 2.5), color: "#404040"},                 // shaft 5 x 48
        #{shape: ring(q[0], q[1], 431.0, 435.0, 6.5, 2.5), color: "#d08020"},           // 695
        #{shape: ring(q[0], q[1], 461.2, 465.2, 6.5, 2.5), color: "#d08020"},
        #{shape: pulley, color: "#2060c0"},
        #{shape: cyl(q[0], q[1], 468.7, 493.7, 9.5), color: "#c03030"},                 // coupler 5-5, 19 x 25
        #{shape: block(vec3(q[0] - 21.15, q[1] - 21.15, 502.2), vec3(q[0] + 21.15, q[1] + 21.15, 542.2)) + cyl(q[0], q[1], 500.2, 502.2, 11.0) + cyl(q[0], q[1], 478.2, 500.2, 2.5), color: "#202020"}];
    for p in MOTOR { let a = my(p, m); parts.push(#{shape: cyl(a[0], a[1], 467.2, 502.2, 3.5), color: "#909aa5"}); }
    for p in FRAME { let a = my(p, m); parts.push(#{shape: cyl(a[0], a[1], 435.0, 461.2, 4.0), color: "#909aa5"}); parts.push(#{shape: cyl(a[0], a[1], 421.0, 429.0, 5.0), color: "#909aa5"}); }
    for p in TIE { let a = my(p, m); parts.push(#{shape: cyl(a[0], a[1], 435.0, 461.2, 4.0), color: "#909aa5"}); }
    for p in PINS { let a = my(p, m);
        parts.push(#{shape: cyl(a[0], a[1], 429.0, 467.2, 2.5), color: "#e0e0e0"});
        parts.push(#{shape: stack(a[0], a[1], 436.06), color: "#30a060"});
        parts.push(#{shape: stack(a[0], a[1], 448.06), color: "#30a060"}); }
    for h in parts { hw.push(h.shape); if !m { show.push(h); } }
}
// R3 on the outline corners (a 6 mm cutter does the inside corner)
let es = d.edges().filter(|e| e.type == "line" && (e.start[0] - e.end[0]).abs() < 1e-6 && (e.start[1] - e.end[1]).abs() < 1e-6 && e.length_mm > 5.9);
d.fillet(es, 3);
let names = ["Rear motor mount lower plate (+Y)", "Rear motor mount upper plate (+Y)", "Rear motor mount lower plate (-Y)", "Rear motor mount upper plate (-Y)"];
let ps = d.parts();
for i in 0..ps.len() { d.tool("set_part", #{body: ps[i].body, name: names[i], material: "Aluminium 6061", color: "#b8bec6"}); }
print(d.parts().map(|p| `${p.name}: ${p.volume_mm3} mm3, bbox ${p.bbox_mm}`));
d.save("rear-mounts.json");
d.export_file("rear-mount-plates.step");
export_step(hw, "rear-mount-hardware.step");
let plates = import_step("rear-mount-plates.step");
show.push(#{shape: plates & block(vec3(370, 380, 420), vec3(430, 480, 470)), color: "#b8bec6"});
render(show, #{path: "rear-mount-revB.png", width: 1400, height: 1100, eye: [130, 250, 640], target: [403, 436, 478], up: [0, 0, 1], fov: 28});
let top = show.filter(|h| true); top.pop(); top.push(#{shape: (plates & block(vec3(370, 380, 420), vec3(430, 480, 436))), color: "#b8bec6"});
render(top.filter(|h| h.shape.bbox().min.z < 462.0), #{path: "rear-mount-revB-bay.png", width: 1100, height: 1100, eye: [402, 435, 900], target: [402, 435, 440], up: [1, 0, 0], fov: 0});
