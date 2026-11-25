// Off-the-shelf lid hardware as solids. Spring parts in a local frame (x along the spring, ball centre at 0).
// Gas spring: HUOPO 10 in / 18 lb (80 N) kit, measured by Jonas 2026-11-25: 245 mm extended ball centre to ball
// centre, 150 compressed (95 stroke), Ø10 ball sockets. Tube and rod diameters are the usual 15 / 6 (not measured).
let SO = 12.0;            // ball centre to the socket's end
let BODY = 126.0;         // body tube = 245 - 95 - 2*12
let ROD = 109.0;          // 95 stroke + 14 inside the body at full extension
let x = vec3(1, 0, 0);
let sock_b = cylinder(vec3(-6.5, 0, 0), x, 6.5, SO + 6.5);
let body = fuse([sock_b, cylinder(vec3(SO, 0, 0), x, 7.5, BODY)]);
let sock_r = cylinder(vec3(-6.5, 0, 0), x, 6.5, SO + 6.5);
let rod = fuse([sock_r, cylinder(vec3(SO, 0, 0), x, 3.0, ROD)]);
export_step(body, "gas_spring_body.step");
export_step(rod, "gas_spring_rod.step");
// Kit ball stud: Ø29 x 1.5 plate with 3 Ø4.5 holes on a Ø20 circle (one on local +y), Ø10 ball 19 mm tall
// (centre 14 off the plate back); local z out of the plate.
let z = vec3(0, 0, 1);
let plate = cylinder(vec3(0, 0, 0), z, 14.5, 1.5);
let holes = [cylinder(vec3(0, 10, -1), z, 2.25, 4.0), cylinder(vec3(-8.660254, -5, -1), z, 2.25, 4.0), cylinder(vec3(8.660254, -5, -1), z, 2.25, 4.0)];
let stud = fuse([plate.cut(holes), cylinder(vec3(0, 0, 1.5), z, 4.0, 3.0), cylinder(vec3(0, 0, 4.5), z, 2.5, 6.0), sphere_at(vec3(0, 0, 14.0), 5.0)]);
export_step(stud, "ball_stud.step");
#{ok: true}
