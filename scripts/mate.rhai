let doc = open_document("/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/printer.json");
let r = doc.tool("assembly_mate", #{assembly: 22, kind: "slider", name: "X axis (gantry on Y-rails)", flip: true, limits: [22.0, 351.0],
  a: #{instance: 1, origin: [0.0, -13.5, 427.0], z: [1.0, 0.0, 0.0], x: [0.0, 1.0, 0.0]},
  b: #{instance: 2, origin: [1022.3, -13.5, 427.0], z: [1.0, 0.0, 0.0], x: [0.0, 1.0, 0.0]}});
print(r.failed_mates);
let r = doc.tool("assembly_mate", #{assembly: 22, kind: "slider", name: "Y axis (toolhead on X beam)", flip: true, limits: [81.0, 402.0],
  a: #{instance: 2, origin: [1022.3, 0.0, 467.5], z: [0.0, 1.0, 0.0], x: [1.0, 0.0, 0.0]},
  b: #{instance: 3, origin: [1022.3, 293.3, 467.5], z: [0.0, 1.0, 0.0], x: [1.0, 0.0, 0.0]}});
print(r.failed_mates);
let r = doc.tool("assembly_mate", #{assembly: 22, kind: "slider", name: "Z axis (bed on MGN12 rails)", flip: true, limits: [126.2, 352.9],
  a: #{instance: 1, origin: [68.0, 0.4, 0.0], z: [0.0, 0.0, 1.0], x: [1.0, 0.0, 0.0]},
  b: #{instance: 4, origin: [68.0, 0.4, 308.9], z: [0.0, 0.0, 1.0], x: [1.0, 0.0, 0.0]}});
print(r.failed_mates);
print(r.instances);
doc.save("/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad/mates/printer2.json");
