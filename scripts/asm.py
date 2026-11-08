# Generates the X-carriage document script: Part Studios (parametric or imported) + nested assemblies
import json, math, re, sys, os
import numpy as np
S = "/tmp/claude-0/-home-user/518fbe24-971e-57ff-a09d-9724b3bf0aa9/scratchpad"
sys.path.insert(0, S + "/gen")
from emit import emit_part3, fmt

OUTDIR = sys.argv[1]          # where the doc's import STEPs live (paths baked into the script)
PARAM = json.loads(sys.argv[2])  # {body id: True} parts with an exact feature tree
NAMES = json.load(open(S + "/gen/names.json"))  # body id -> display name for printed parts
tree = json.load(open(S + "/xt/tree.json"))

def mat(x):
    m = np.array(x["m"]).reshape(3, 3).T   # column-major -> rows
    return m, np.array(x["t"])
def compose(a, b):  # a then b inside a: p -> a(b(p))
    return a[0] @ b[0], a[0] @ b[1] + a[1]
def inv(a):
    r = a[0].T
    return r, -r @ a[1]
IDENT = (np.eye(3), np.zeros(3))

VENDOR = re.compile(r"screw|bearing|Beacon|LSD|FAN|GT2|MGN9 Rail", re.I)
printed = [k["body"] for k in tree["kids"] if "body" in k and not VENDOR.search(k["name"])]
printed = list(dict.fromkeys(printed))

# which studio holds each body, and where it sits in it
studio_of, ref_of, studio_names, studio_bodies = {}, {}, [], []
def studio(name):
    studio_names.append(name); studio_bodies.append([]); return len(studio_names) - 1
for b in printed:
    i = studio(NAMES.get(str(b), "Part %d" % b))
    studio_of[b] = i; ref_of[b] = IDENT; studio_bodies[i].append(b)
def collect(n, world, si):
    if "body" in n:
        b = n["body"]
        if b not in studio_of:
            studio_of[b] = si; ref_of[b] = world; studio_bodies[si].append(b)
        return
    for k in n["kids"]:
        collect(k, compose(world, mat(k["local"])), si)
groups = [("Purchased parts", [k for k in tree["kids"] if "body" in k])]
groups += [(k["name"].split(" <")[0], [k]) for k in tree["kids"] if "asm" in k]
GN = {"3010": "3010 blower fan", "MGN9H": "MGN9H carriage", "sherpa mini": "Sherpa Mini extruder", "simplecore_hevort": "Frame (simplecore_hevort)"}
for gname, kids in groups:
    si = studio(GN.get(gname, gname))
    for k in kids:
        collect(k, mat(k["local"]), si)

L = ['fn add_all(sk, items) { for it in items { sk.add(it); } }', 'let doc = new_document();', 'let parts = #{};']
specs = {}
for si, name in enumerate(studio_names):
    if si > 0:
        L.append('doc.tool("new_part_studio", #{name: %s});' % json.dumps(name))
    bodies = studio_bodies[si]
    if len(bodies) == 1 and str(bodies[0]) in PARAM:
        b = bodies[0]
        an = json.load(open(S + "/an/b%d.json" % b))
        em = emit_part3(an, "s%d_" % si)
        L += em.lines
        L.append('let pb = doc.parts()[0].body;')
        L.append('doc.tool("set_part", #{body: pb, name: %s, color: "#e8a33d"});' % json.dumps(name))
        L.append('parts["%d"] = [%d, pb];' % (b, si))
    else:
        spec = []
        for b in bodies:
            r = ref_of[b]
            m = r[0].T.reshape(-1)   # rows of transpose = columns
            spec.append("%d %s %s %d" % (b, " ".join(repr(float(x)) for x in m), " ".join(repr(float(x)) for x in r[1]), b))
        path = os.path.join(OUTDIR, "studio%d.step" % si)
        specs[path] = "\n".join(spec) + "\n"
        L.append('let r = doc.tool("import_file", #{path: %s, name: %s});' % (json.dumps(path), json.dumps(name if len(bodies) == 1 else name + " (imported)")))
        L.append('let ps = r.parts;')
        for k, b in enumerate(bodies):
            nm = NAMES.get(str(b)) if b in printed else None
            L.append('parts["%d"] = [%d, ps[%d].body];' % (b, si, k))
            L.append('doc.tool("set_part", #{body: ps[%d].body, name: names["%d"]});' % (k, b))
json.dump(specs, open(S + "/asm/specs.json", "w"))
json.dump(studio_names, open(S + "/asm/studios.json", "w"))

# body names (from the file) for set_part
bn = {}
def names(n):
    if "body" in n: bn.setdefault(n["body"], n["name"])
    else: [names(k) for k in n["kids"]]
names(tree)
for b in printed: bn[b] = NAMES.get(str(b), bn[b])
L.insert(3, 'let names = %s;' % ("#{" + ", ".join('"%d": %s' % (b, json.dumps(v)) for b, v in bn.items()) + "}"))

# assemblies, bottom-up
asm_index = {}
count = [0]
def axis_angle(r):
    # quaternion (Shepperd), then axis and angle
    t = np.trace(r)
    if t > 0:
        q = np.array([1 + t, r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]])
    else:
        i = int(np.argmax(np.diag(r)))
        j, k = (i + 1) % 3, (i + 2) % 3
        v = np.zeros(3)
        v[i] = 1 + r[i, i] - r[j, j] - r[k, k]
        v[j] = r[j, i] + r[i, j]
        v[k] = r[k, i] + r[i, k]
        q = np.array([r[k, j] - r[j, k], *v])
    q = q / np.linalg.norm(q)
    if q[0] < 0: q = -q
    ang = 2 * math.atan2(np.linalg.norm(q[1:]), q[0])
    if ang < 1e-12: return [0, 0, 1], 0.0
    ax = q[1:] / np.linalg.norm(q[1:])
    return list(ax), math.degrees(ang)
def place(x):
    ax, ang = axis_angle(x[0])
    s = 'position: [%s, %s, %s]' % tuple(repr(round(float(c), 9)) for c in x[1])
    if ang > 1e-9: s += ', rotate: #{axis: [%s, %s, %s], angle: %s}' % (*[repr(round(float(c), 12)) for c in ax], repr(ang))
    return s
def build(n):
    for k in n["kids"]:
        if "asm" in k and k["asm"] not in asm_index: build(k)
    nm = GN.get(n["name"].split(" <")[0], n["name"].split(" <")[0])
    if n is tree: nm = "X-carriage"
    idx = len(asm_index); asm_index[n["asm"]] = idx
    L.append('doc.tool("create_assembly", #{name: %s});' % json.dumps(nm))
    first = True
    for k in n["kids"]:
        loc = mat(k["local"])
        if "body" in k:
            b = k["body"]
            x = compose(loc, inv(ref_of[b]))
            L.append('doc.tool("assembly_insert", #{assembly: %d, studio: parts["%d"][0], body: parts["%d"][1], %s, fixed: true});' % (idx, b, b, place(x)))
        else:
            L.append('doc.tool("assembly_insert", #{assembly: %d, sub_assembly: %d, %s, fixed: true});' % (idx, asm_index[k["asm"]], place(loc)))
        count[0] += 1
build(tree)
L.append('doc.save(%s);' % json.dumps(sys.argv[3]))
open(sys.argv[3] + ".rhai", "w").write("\n".join(L) + "\n")
print("studios", len(studio_names), "instances", count[0], "asms", len(asm_index))
