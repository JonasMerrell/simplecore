// 9 mm belt rear motor mount, +Y corner, rev A (2026-11-15).
// CNC plates on round standoffs. World coordinates of the Printer assembly, mm.
// Run from this folder: rcad script rear-mount.rhai   (writes rear-mount.json, .step and .png)
fn zplane(d, z, name) { d.feature("plane", #{mode: "offset", base: #{kind: "origin_plane", plane: "Top"}, offset: z}, name) }
fn ext(d, s, depth, up, op, name) { d.feature("extrude", #{profiles: [s], depth: depth, op: op, opposite: !up}, name) }
fn region(s, u, v) { #{kind: "region", sketch: s.id, point: [u, v]} }

let d = new_document();
// --- numbers that drive the design
d.variable("bay_z0", 435.0);        // underside of the belt bay (top of the lower plate)
d.variable("bay_h", 26.2);          // both belt levels: z 435.0 to 461.2
d.variable("plate_t", 6);           // 6061 plate
d.variable("brg_od", 13);           // 695 bearing 5 x 13 x 4, light press fit
d.variable("brg_w", 4);
d.variable("pin_d", 5);             // idler pins, same as the XY joints
d.variable("m5_clear", 5.5);
d.variable("m3_clear", 3.4);
d.variable("shaft_clear", 8);       // hole behind each bearing for the 5 mm shaft

let SX = 403.35; let SY = 429.35;                    // drive shaft axis (unchanged motor axis)
let PINS = [[385.5, 456.5], [394.5, 416.2], [407.0, 443.7]];   // idler axles, positions of the old mount
let FRAME = [[414.5, 403.0], [414.5, 452.0], [399.5, 466.5]];  // M5 through the stack into T-nuts in the top slots
let TIE = [[386.0, 402.0]];                          // fourth standoff, M5 tapped in the lower plate
let MOTOR = [[SX - 15.5, SY - 15.5], [SX + 15.5, SY - 15.5], [SX - 15.5, SY + 15.5], [SX + 15.5, SY + 15.5]];
// outline: clears the upright (x 404.5 to 424.5, y 456.5 to 476.5) by 0.2
let OUT = [[381.0, 396.0], [424.5, 396.0], [424.5, 456.3], [404.3, 456.3], [404.3, 476.5], [381.0, 476.5]];

// --- lower plate: z 429 to 435, every feature cut from the top face
let p0 = zplane(d, 429.0, "Lower plate underside");
let s = d.sketch(p0, "Lower plate outline"); s.polygon(OUT);
ext(d, s, "plate_t", true, "new", "Lower plate");
let pt = zplane(d, 435.0, "Lower plate top (bay floor)");
s = d.sketch(pt, "Lower plate through holes");
for p in PINS { s.circle(p, "pin_d"); }
for p in FRAME { s.circle(p, "m5_clear"); }
for p in TIE { s.circle(p, 4.2); }                   // M5 tap drill
s.circle([SX, SY], "shaft_clear");
ext(d, s, "plate_t", false, "remove", "Lower plate holes");
s = d.sketch(pt, "Lower bearing bore"); s.circle([SX, SY], "brg_od");
ext(d, s, "brg_w", false, "remove", "Lower bearing pocket");

// --- upper plate: z 461.2 to 467.2, every feature cut from the underside
let pu = zplane(d, 461.2, "Upper plate underside (bay roof)");
s = d.sketch(pu, "Upper plate outline"); s.polygon(OUT);
ext(d, s, "plate_t", true, "new", "Upper plate");
s = d.sketch(pu, "Upper plate through holes");
for p in PINS { s.circle(p, "pin_d"); }
for p in FRAME { s.circle(p, "m5_clear"); }
for p in TIE { s.circle(p, "m5_clear"); }
for p in MOTOR { s.circle(p, "m3_clear"); }
s.circle([SX, SY], "shaft_clear");
ext(d, s, "plate_t", true, "remove", "Upper plate holes");
s = d.sketch(pu, "Upper bearing bore"); s.circle([SX, SY], "brg_od");
ext(d, s, "brg_w", true, "remove", "Upper bearing pocket");
s = d.sketch(pu, "Motor screw counterbores");
for p in MOTOR { s.circle(p, 6.5); }
ext(d, s, 3.4, true, "remove", "Motor screw counterbores (M3 heads in the bay roof)");

// round the outside corners (R3 outside; the one inside corner gets R3 for a 6 mm cutter)
let es = d.edges().filter(|e| e.type == "line" && (e.start[0] - e.end[0]).abs() < 1e-6 && (e.start[1] - e.end[1]).abs() < 1e-6 && e.length_mm > 5.9);
d.fillet(es, 3);
print(d.parts());
d.save("rear-mount.json");
d.export_file("rear-mount-plates.step");

// --- hardware, as plain solids for the picture and the clearance check
fn cyl(x, y, z0, z1, r) { cylinder(vec3(x, y, z0), vec3(0, 0, 1), r, z1 - z0) }
let hw = [];
let col = #{};
let shaft = cyl(SX, SY, 431.0, 478.2, 2.5);
let brg = [cyl(SX, SY, 431.0, 435.0, 6.5) - cyl(SX, SY, 430.0, 436.0, 2.5), cyl(SX, SY, 461.2, 465.2, 6.5) - cyl(SX, SY, 460.0, 466.0, 2.5)];
// 9 mm 20T pulley on the upper belt: teeth z 448.56 to 459.56, flanges 16 dia
let pulley = cyl(SX, SY, 447.06, 461.06, 8.0) - cyl(SX, SY, 448.56, 459.56, 9.0) + cyl(SX, SY, 448.56, 459.56, 6.1);
let spacer_lo = cyl(SX, SY, 435.1, 447.06, 4.0) - cyl(SX, SY, 435.0, 448.0, 2.5);
let coupler = cyl(SX, SY, 468.7, 493.7, 9.5);
let motor = block(vec3(SX - 21.15, SY - 21.15, 502.2), vec3(SX + 21.15, SY + 21.15, 542.2)) + cyl(SX, SY, 500.2, 502.2, 11.0) + cyl(SX, SY, 478.2, 500.2, 2.5);
let posts = [];
for p in MOTOR { posts.push(cyl(p[0], p[1], 467.2, 502.2, 4.0)); }
for p in FRAME { posts.push(cyl(p[0], p[1], 435.0, 461.2, 5.0)); posts.push(cyl(p[0], p[1], 421.0, 429.0, 5.0)); }
for p in TIE { posts.push(cyl(p[0], p[1], 435.0, 461.2, 5.0)); }
let pins = [];
for p in PINS { pins.push(cyl(p[0], p[1], 429.0, 467.2, 2.5)); }
let idlers = [cyl(407.0, 443.7, 447.06, 461.06, 7.5), cyl(385.5, 456.5, 435.06, 449.06, 7.5), cyl(394.5, 416.2, 435.06, 449.06, 7.5)];
export_step([shaft, brg[0], brg[1], pulley, spacer_lo, coupler, motor] + posts + pins, "rear-mount-hardware.step");
let plates = import_step("rear-mount-plates.step");
let parts = [#{shape: plates, color: "#b8bec6"}, #{shape: shaft, color: "#404040"}, #{shape: brg[0], color: "#d08020"}, #{shape: brg[1], color: "#d08020"},
    #{shape: pulley, color: "#2060c0"}, #{shape: spacer_lo, color: "#808080"}, #{shape: coupler, color: "#c03030"}, #{shape: motor, color: "#202020"}];
for q in posts { parts.push(#{shape: q, color: "#909aa5"}); }
for q in pins { parts.push(#{shape: q, color: "#e0e0e0"}); }
for q in idlers { parts.push(#{shape: q, color: "#30a060", opacity: 0.6}); }
render(parts, #{path: "rear-mount-revA.png", width: 1400, height: 1100, eye: [130, 250, 640], target: [403, 436, 478], up: [0, 0, 1], fov: 28});
// clearance: idler flange against the pulley flange on the same level
#{pulley_to_idler_gap: distance(vec3(SX, SY, 0), vec3(407.0, 443.7, 0)) - 8.0 - 7.5}
