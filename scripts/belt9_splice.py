#!/usr/bin/env python3
"""Add the 9 mm belt drive (9mm-belts/drive.py output) to X-carriage.json. Additive and re-runnable:
a second run replaces the two studios and the assembly it made the first time, and touches nothing else.
usage: python3 scripts/belt9_splice.py hw-doc.json X-carriage.json   -> writes X-carriage.json.new
hw-doc.json: a document whose last studio is the STEP import of 9mm-belts/drive-hardware.step (9mm-belts/import.json)."""
import json, sys, copy, os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "9mm-belts")
src = sys.argv[2]
d = json.load(open(src))
plates = json.load(open(os.path.join(B, "drive.json")))["studios"][0]
hwdoc = json.load(open(sys.argv[1]))["studios"][-1]
meta = json.load(open(os.path.join(B, "drive-parts.json")))
SP, SH, AN = "9 mm drive, machined parts", "9 mm drive, hardware and belts", "9 mm belt drive"
rgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
key = lambda k: tuple(map(int, k.split(":")))

plates = copy.deepcopy(plates); plates["name"] = SP
hw = copy.deepcopy(hwdoc); hw["name"] = SH
fid = hw["doc"]["features"][-1]["id"]
assert len(hw["doc"]["features"]) == 1 and hw["doc"]["features"][0]["op"]["type"] == "import"
hw["doc"]["parts"] = {f"{fid}:{i}": {"name": p["name"], "color": rgb(p["color"]), "material": p["material"]} for i, p in enumerate(meta["hardware"])}

def put_studio(st):
    for i, s in enumerate(d["studios"]):
        if s["name"] == st["name"]: d["studios"][i] = st; return i
    d["studios"].append(st); return len(d["studios"]) - 1
sp, sh = put_studio(plates), put_studio(hw)
nema = [i for i, s in enumerate(d["studios"]) if s["name"] == "Standard parts"][0]
assert d["studios"][nema]["doc"]["parts"]["1:0"]["name"].startswith("NEMA 17 stepper, 40 mm")

I = lambda: {"r": [1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0], "t": [0.0, 0.0, 0.0]}
inst = []
def add(name, studio, body, pose=None):
    n = len(inst) + 1
    inst.append({"id": n, "name": f"{name} <{n}>", "studio": studio, "body": list(body), "pose": pose or I(), "fixed": True, "hidden": False})
for k, v in sorted(plates["doc"]["parts"].items(), key=lambda kv: key(kv[0])): add(v["name"], sp, key(k))
for i, p in enumerate(meta["hardware"]): add(p["name"], sh, (fid, i))
# the standard NEMA 17 has its mounting face on z = 0 and the shaft along +Z: turn it shaft down, face at t
for m in meta["motors"]: add(m["name"], nema, (1, 0), {"r": [1.0, 0, 0, 0, -1.0, 0, 0, 0, -1.0], "t": m["t"]})
asm = {"name": AN, "instances": inst, "mates": [], "next_id": len(inst) + 1, "relations": []}
ai = [i for i, a in enumerate(d["assemblies"]) if a["name"] == AN]
if ai: ai = ai[0]; d["assemblies"][ai] = asm
else: d["assemblies"].append(asm); ai = len(d["assemblies"]) - 1

P = [a for a in d["assemblies"] if a["name"] == "Printer"][0]
if not any(x.get("sub") == ai for x in P["instances"]):
    nid = max([P["next_id"] - 1] + [x["id"] for x in P["instances"]] + [m["id"] for m in P["mates"]] + [r["id"] for r in P["relations"]]) + 1; P["next_id"] = nid + 1
    P["instances"].append({"id": nid, "name": AN + " <1>", "studio": 0, "body": [0, 0], "pose": I(), "fixed": True, "hidden": False, "sub": ai})
# the 6 mm belt parts this replaces stay in the document, hidden: the two old rear motors and the two old AWD idler mounts
hid = []
for x in P["instances"]:
    if x["name"].startswith("NEMA 17 stepper") and x.get("sub") is None: x["hidden"] = True; hid.append(x["name"])
for a in d["assemblies"]:
    for x in a["instances"]:
        if x["name"].startswith("AWD motor idler V2"): x["hidden"] = True; hid.append(x["name"])
json.dump(d, open(src + ".new", "w"))
print(src, "studios", sp, sh, "assembly", ai, "parts", len(inst), "hidden:", hid)
