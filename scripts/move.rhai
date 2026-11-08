let doc = open_document("/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/printer2.json");
fn show(r) { for i in r.instances { print(i.name + " " + i.position); } }
doc.tool("render_assembly", #{assembly: 22, path: "/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/home_iso.png", view: "iso"});
let r = doc.tool("assembly_move", #{assembly: 22, instance: 2, position: [-522.3, 0.0, 0.0]}); show(r);
let r = doc.tool("assembly_move", #{assembly: 22, instance: 3, position: [-700.0, 200.0, 0.0]}); show(r);
let r = doc.tool("assembly_move", #{assembly: 22, instance: 4, position: [0.0, 0.0, 100.0]}); show(r);
doc.tool("render_assembly", #{assembly: 22, path: "/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/max_iso.png", view: "iso"});
let r = doc.tool("assembly_move", #{assembly: 22, instance: 2, position: [-2000.0, 0.0, 0.0]}); show(r);
let r = doc.tool("assembly_move", #{assembly: 22, instance: 3, position: [-700.0, -500.0, 0.0]}); show(r);
let r = doc.tool("assembly_move", #{assembly: 22, instance: 4, position: [0.0, 0.0, -400.0]}); show(r);
doc.tool("render_assembly", #{assembly: 22, path: "/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/min_iso.png", view: "iso"});
