// Off-the-shelf lid hardware as solids. Spring parts in a local frame (x along the spring, ball centre at 0).
// Gas spring: 150 mm extended (ball centre to ball centre), 50 mm stroke, Ø15 body, Ø6 rod, Ø10 ball sockets.
let SO = 12.0;            // ball centre to the socket's end
let BODY = 76.0;          // body tube = 150 - 50 - 2*12
let ROD = 64.0;           // 50 stroke + 14 inside the body at full extension
let x = vec3(1, 0, 0);
let sock_b = cylinder(vec3(-6.5, 0, 0), x, 6.5, SO + 6.5);
let body = fuse([sock_b, cylinder(vec3(SO, 0, 0), x, 7.5, BODY)]);
let sock_r = cylinder(vec3(-6.5, 0, 0), x, 6.5, SO + 6.5);
let rod = fuse([sock_r, cylinder(vec3(SO, 0, 0), x, 3.0, ROD)]);
export_step(body, "gas_spring_body.step");
export_step(rod, "gas_spring_rod.step");
// Ball stud: M6, Ø10 ball, 9.5 from the plate face to the ball centre; local z out of the plate.
let stud = fuse([cylinder(vec3(0, 0, 0), vec3(0, 0, 1), 5.0, 2.0), cylinder(vec3(0, 0, 2), vec3(0, 0, 1), 3.5, 5.0), sphere_at(vec3(0, 0, 9.5), 5.0)]);
export_step(stud, "ball_stud.step");
#{ok: true}
