# Stage 2: an analysis JSON (from analyze.rhai) -> Rhai lines that build the part as a feature tree
import json, math

AXN = "xyz"

def r6(v):
    v = round(float(v), 9)
    return repr(0.0 if v == 0 else v)

def plane_of(i):
    """(origin plane name, uv(p), offset(level) for a plane at that level, extrude flags for +axis)"""
    if i == 2:   # Top: u=x v=y, normal +z
        return "Top", (lambda p: (p[0], p[1])), (lambda h: h), {}
    if i == 0:   # Right: u=y v=z, normal +x
        return "Right", (lambda p: (p[1], p[2])), (lambda h: h), {}
    # Front: u=x v=z, normal -y; offset o is y = -o; extrude +y = opposite
    return "Front", (lambda p: (p[0], p[2])), (lambda h: -h), {"opposite": "true"}

def key2(a, b):
    r = lambda q: (round(q[0], 5), round(q[1], 5))
    return tuple(sorted([r(a), r(b)]))

def snap(out, tol=5e-3):
    """join endpoints that the section left a hair apart, and make 2-point splines lines"""
    reps = []
    def rep(p):
        for q in reps:
            if math.dist(p, q) < tol: return q
        reps.append(p); return p
    # prefer exact line/arc ends as representatives
    for it in out:
        if it[0] == "L": rep(it[1]); rep(it[2])
        elif it[0] == "A": rep(it[2]); rep(it[3])
    res = []
    for it in out:
        if it[0] == "L": res.append(("L", rep(it[1]), rep(it[2])))
        elif it[0] == "A": res.append(("A", it[1], rep(it[2]), rep(it[3]), it[4]))
        elif it[0] == "S":
            pts = list(it[1]); pts[0] = rep(pts[0]); pts[-1] = rep(pts[-1])
            if len(pts) == 2: res.append(("L", pts[0], pts[1]))
            else: res.append(("S", pts))
        else: res.append(it)
    return [r for r in res if not (r[0] == "L" and math.dist(r[1], r[2]) < 1e-7)]

def items_uv(items, uv):
    return snap(items_uv0(items, uv))

def items_uv0(items, uv):
    out, seen = [], set()
    for it in items:
        t = it["t"]
        if t == "L":
            a, b = uv(it["s"]), uv(it["e"])
            if math.dist(a, b) < 1e-7: continue
            k = ("L",) + key2(a, b)
            if k in seen: continue
            seen.add(k); out.append(("L", a, b))
        elif t == "C":
            c, s, e, m = uv(it["c"]), uv(it["s"]), uv(it["e"]), uv(it["m"])
            r = it["r"]
            if math.dist(s, e) < 1e-7:
                k = ("O", round(c[0], 5), round(c[1], 5), round(r, 5))
                if k in seen: continue
                seen.add(k); out.append(("O", c, r))
            else:
                cr = (m[0]-s[0])*(e[1]-m[1]) - (m[1]-s[1])*(e[0]-m[0])
                if cr < 0: s, e = e, s
                k = ("A", round(c[0], 5), round(c[1], 5)) + key2(s, e)
                if k in seen: continue
                seen.add(k); out.append(("A", c, s, e, r))
        else:
            pts = [uv(p) for p in it["pts"]]
            k = ("S",) + key2(pts[0], pts[-1]) + (len(pts),)
            if k in seen: continue
            seen.add(k); out.append(("S", pts))
    return out

def p2(p): return "[%s, %s]" % (r6(p[0]), r6(p[1]))

def rhai_item(it):
    if it[0] == "L": return '#{type: "line", from: %s, to: %s, dims: true}' % (p2(it[1]), p2(it[2]))
    if it[0] == "A": return '#{type: "arc", center: %s, start: %s, end: %s, dims: true}' % (p2(it[1]), p2(it[2]), p2(it[3]))
    if it[0] == "O": return '#{type: "circle", center: %s, radius: %s, dims: true}' % (p2(it[1]), r6(it[2]))
    return '#{type: "spline", points: [%s]}' % ", ".join(p2(p) for p in it[1])

def signature(slab, uv):
    its = items_uv([i for f in slab["faces"] for i in f["items"]], uv)
    return sorted(repr(x) for x in its)

def fmt(v):
    v = round(v, 6)
    return ("%g" % v) if abs(v) < 1e6 else repr(v)

class Emitter:
    def __init__(self, prefix):
        self.lines, self.n, self.prefix, self.planes = [], 0, prefix, {}
    def w(self, s): self.lines.append(s)
    def var(self):
        self.n += 1; return "%s%d" % (self.prefix, self.n)
    def plane(self, i, h):
        name, uv, off, flags = plane_of(i)
        o = off(h)
        if abs(o) < 1e-9: return '"%s"' % name.lower()
        k = (i, round(h, 6))
        if k in self.planes: return self.planes[k]
        v = self.var()
        self.w('let %s = doc.feature("plane", #{base: #{kind: "origin_plane", plane: "%s"}, offset: "%s", flip: false}, "%s = %s");' % (v, name, fmt(o), AXN[i], fmt(h)))
        self.planes[k] = v
        return v
    def extrude(self, i, lo, hi, faces, op, name):
        """faces: the section faces (items + inside point) at level lo, extruded to hi"""
        _, uv, _, flags = plane_of(i)
        pl = self.plane(i, lo)
        sk = self.var()
        its = items_uv([x for f in faces for x in f["items"]], uv)
        self.w('let %s = doc.sketch(%s, "%s");' % (sk, pl, name))
        self.w('add_all(%s, [%s]);' % (sk, ", ".join(rhai_item(x) for x in its)))
        profs = ", ".join('#{kind: "region", sketch: %s.id, point: %s}' % (sk, p2(uv(f["inside"]))) for f in faces)
        extra = "".join(", %s: %s" % kv for kv in flags.items())
        self.w('doc.feature("extrude", #{profiles: [%s], depth: "%s", op: "%s"%s}, "%s");' % (profs, fmt(hi - lo), op, extra, name))

def slab_runs(slabs, i):
    """merge neighbouring slabs with the same section"""
    _, uv, _, _ = plane_of(i)
    runs = []
    for s in slabs:
        if not s["faces"]: continue
        sig = signature(s, uv)
        if runs and runs[-1]["sig"] == sig and abs(runs[-1]["hi"] - s["lo"]) < 1e-6:
            runs[-1]["hi"] = s["hi"]
        else:
            runs.append({"lo": s["lo"], "hi": s["hi"], "faces": s["faces"], "sig": sig})
    return runs

def describe(feat):
    """a name for a cut or added piece"""
    runs = slab_runs(feat["slabs"], feat["axis"])
    its = [x for f in runs[0]["faces"] for x in f["items"]]
    circles = [x for x in its if x["t"] == "C" and math.dist(x["s"], x["e"]) < 1e-7]
    if feat["op"] == "remove" and len(its) == 1 and circles:
        return "Hole Ø%s (%s)" % (fmt(2 * circles[0]["r"]), AXN[feat["axis"]])
    arcs = [x for x in its if x["t"] == "C"]
    if feat["op"] == "remove" and arcs and len(its) <= 4 and all(math.dist(a["s"], a["e"]) > 1e-7 for a in arcs):
        return "Round R%s (%s)" % (fmt(arcs[0]["r"]), AXN[feat["axis"]])
    if feat["op"] == "add" and arcs and len(its) <= 4:
        return "Fillet R%s (%s)" % (fmt(arcs[0]["r"]), AXN[feat["axis"]])
    if feat["op"] == "remove" and len(its) == 3 and all(x["t"] == "L" for x in its):
        return "Chamfer (%s)" % AXN[feat["axis"]]
    return ("Cut" if feat["op"] == "remove" else "Boss") + " (%s)" % AXN[feat["axis"]]

def emit_part(an, prefix):
    e = Emitter(prefix)
    i = an["axis"]
    runs = slab_runs(an["base"], i)
    for k, r in enumerate(runs):
        nm = "Body %s %s → %s" % (AXN[i], fmt(r["lo"]), fmt(r["hi"]))
        e.extrude(i, r["lo"], r["hi"], r["faces"], "new" if k == 0 else "add", nm)
    left = []
    for f in sorted(an["features"], key=lambda f: f["op"] != "remove"):
        if f["axis"] < 0:
            left.append(f); continue
        nm = describe(f)
        for r in slab_runs(f["slabs"], f["axis"]):
            e.extrude(f["axis"], r["lo"], r["hi"], r["faces"], f["op"], nm)
    return e, left

def name_piece(faces, e, op):
    its = [x for f in faces for x in f["items"]]
    circles = [x for x in its if x["t"] == "C" and math.dist(x["s"], x["e"]) < 1e-7]
    arcs = [x for x in its if x["t"] == "C" and math.dist(x["s"], x["e"]) >= 1e-7]
    lines = [x for x in its if x["t"] == "L"]
    if op == "remove" and circles and len(circles) == len(its):
        ds = sorted(set(fmt(2 * c["r"]) for c in circles))
        return "Hole Ø%s (%s)" % ("/".join(ds), AXN[e])
    if op == "remove" and len(arcs) == 1 and len(lines) == 2 and len(its) == 3:
        return "Round R%s (%s)" % (fmt(arcs[0]["r"]), AXN[e])
    if op == "add" and len(arcs) == 1 and len(lines) == 2 and len(its) == 3:
        return "Fillet R%s (%s)" % (fmt(arcs[0]["r"]), AXN[e])
    if op == "remove" and len(its) == 3 and len(lines) == 3:
        return "Chamfer (%s)" % AXN[e]
    if op == "remove" and arcs and len(lines) >= 2:
        return "Slot (%s)" % AXN[e] if len(arcs) == 2 and len(lines) == 2 else "Pocket (%s)" % AXN[e]
    return ("Cut" if op == "remove" else "Boss") + " (%s)" % AXN[e]

def emit_part2(an, prefix):
    e = Emitter(prefix)
    i = an["axis"]
    runs = slab_runs(an["base"], i)
    for k, r in enumerate(runs):
        nm = "Body %s %s → %s" % (AXN[i], fmt(r["lo"]), fmt(r["hi"]))
        e.extrude(i, r["lo"], r["hi"], r["faces"], "new" if k == 0 else "add", nm)
    for op in ("remove", "add"):
        for f in an["features"]:
            faces = f[op]
            if not faces: continue
            e.extrude(f["e"], f["lo"], f["hi"], faces, op, name_piece(faces, f["e"], op))
    return e


def hole_plane(e, h, outward_pos):
    """plane at level h along axis e whose normal points +e (outward_pos) or -e; returns (base, offset, flip, uv)"""
    base = {2: "Top", 0: "Right", 1: "Front"}[e]
    uv0 = {2: lambda p: (p[0], p[1]), 0: lambda p: (p[1], p[2]), 1: lambda p: (p[0], p[2])}[e]
    base_pos = e != 1          # Top and Right face +e, Front faces -y
    flip = outward_pos != base_pos
    off = h if e != 1 else -h
    uv = (lambda p: (-uv0(p)[0], uv0(p)[1])) if flip else uv0
    return base, off, flip, uv

def emit_holes(em, holes):
    """group holes with the same size, direction and plane into one Hole feature"""
    groups = {}
    for h in holes:
        k = (h["e"], h["from_hi"], round(h["open"], 5), h["type"], round(h["dia"], 5), h["through"], round(h["depth"], 5),
             round(h.get("cs_d", 0), 5), round(h.get("cs_angle", 0), 4), round(h.get("cb_d", 0), 5), round(h.get("cb_depth", 0), 5))
        groups.setdefault(k, []).append(h)
    for k, hs in groups.items():
        h = hs[0]
        base, off, flip, uv = hole_plane(h["e"], h["open"], h["from_hi"])
        pl = em.var()
        em.w('let %s = doc.feature("plane", #{base: #{kind: "origin_plane", plane: "%s"}, offset: "%s", flip: %s}, "%s = %s");' % (pl, base, fmt(off), "true" if flip else "false", AXN[h["e"]], fmt(h["open"])))
        sk = em.var()
        kind = {"simple": "Hole", "countersink": "Countersunk hole", "counterbore": "Counterbored hole"}[h["type"]]
        nm = "%s Ø%s%s" % (kind, fmt(h["dia"]), "" if len(hs) == 1 else " ×%d" % len(hs))
        em.w('let %s = doc.sketch(%s, "%s");' % (sk, pl, nm))
        em.w('let %s_pts = [];' % sk)
        for x in hs:
            em.w('%s_pts.push(#{kind: "sketch_point", sketch: %s.id, point: %s.add(#{type: "point", at: %s}).point});' % (sk, sk, sk, p2(uv(x["at"]))))
        params = 'hole_type: "%s", diameter: "%s", through: %s, depth: "%s"' % (h["type"], fmt(h["dia"]), "true" if h["through"] else "false", fmt(h["depth"]))
        if h["type"] == "countersink": params += ', cs_diameter: "%s", cs_angle: "%s"' % (fmt(h["cs_d"]), fmt(h["cs_angle"]))
        if h["type"] == "counterbore": params += ', cb_diameter: "%s", cb_depth: "%s"' % (fmt(h["cb_d"]), fmt(h["cb_depth"]))
        em.w('doc.feature("hole", #{points: %s_pts, %s}, "%s");' % (sk, params, nm))

def emit_part3(an, prefix):
    e = Emitter(prefix)
    i = an["axis"]
    runs = slab_runs(an["base"], i)
    for k, r in enumerate(runs):
        nm = "Body %s %s → %s" % (AXN[i], fmt(r["lo"]), fmt(r["hi"]))
        e.extrude(i, r["lo"], r["hi"], r["faces"], "new" if k == 0 else "add", nm)
    ext = [f for f in an["features"] if f.get("kind") not in ("hole", "blend")]
    for op in ("remove", "add"):
        for f in ext:
            faces = f[op]
            if not faces: continue
            e.extrude(f["e"], f["lo"], f["hi"], faces, op, name_piece(faces, f["e"], op))
    ext = [f for f in an["features"] if f.get("kind") not in ("hole", "blend")]
    emit_holes(e, [f for f in an["features"] if f.get("kind") == "hole"])
    # fillets, then chamfers, grouped by size
    for kind in ("fillet", "chamfer"):
        by = {}
        for f in an["features"]:
            if f.get("kind") != "blend": continue
            for x in f["edges"]:
                if x["kind"] == kind: by.setdefault(round(x["size"], 3), []).append(x["at"])
        for size, pts in sorted(by.items()):
            refs = ", ".join('#{kind: "edge", point: [%s, %s, %s]}' % tuple(r6(c) for c in p) for p in pts)
            nm = ("Fillet R%s" if kind == "fillet" else "Chamfer %s") % fmt(size)
            par = 'radius: "%s"' % fmt(size) if kind == "fillet" else 'distance: "%s"' % fmt(size)
            e.w('try { doc.feature("%s", #{edges: [%s], %s}, "%s"); } catch (err) { print("SKIPPED %s: " + err); }' % (kind, refs, par, nm, nm))
    return e
