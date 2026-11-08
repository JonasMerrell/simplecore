let a = import_step(A).solids()[0];
let b = import_step(B);
let vs = [];
for v in ["iso", "top", "front", "right"] {
  vs.push(#{parts: [#{shape: a, color: "#88aadd"}], view: v});
}
for v in ["iso", "top", "front", "right"] {
  vs.push(#{parts: [#{shape: b, color: "#ddaa66"}], view: v});
}
render_views(vs, #{path: OUT, columns: 4, width: 1600, height: 800});
