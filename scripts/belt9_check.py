#!/usr/bin/env python3
"""Interference check of the 9 mm belt drive (9mm-belts/drive-*.step) against itself and against the Printer assembly (model pose).
Prints every pair of solids whose common volume is over 0.2 mm3. Needs cadquery-ocp and belt9_lib's decoded STEP cache.
Only imported (STEP) studios of the printer can be checked; feature-tree studios (PIR, panels) are skipped."""
import json, os, sys
from belt9_lib import *
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "9mm-belts")
def read(fn):
    r = STEPControl_Reader(); r.ReadFile(fn); r.TransferRoots(); sh = r.OneShape()
    out = []; e = TopExp_Explorer(sh, TopAbs_SOLID)
    while e.More(): out.append(TopoDS.Solid(e.Current())); e.Next()
    return out
def vol(a, b):
    c = BRepAlgoAPI_Common(a, b)
    if not c.IsDone(): return -1
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(c.Shape(), g); return g.Mass()
def hit(a, b, pad=0.0): return all(a[i] < b[i + 3] + pad and b[i] < a[i + 3] + pad for i in range(3))
meta = json.load(open(os.path.join(B, "drive-parts.json")))
doc = json.load(open(os.path.join(B, "drive.json")))["studios"][0]["doc"]["parts"]
pn = [v["name"] for k, v in sorted(doc.items(), key=lambda kv: tuple(map(int, kv[0].split(":"))))]
new = [(n, s) for n, s in zip(pn, read(os.path.join(B, "drive-plates.step")))] + [(p["name"], s) for p, s in zip(meta["hardware"], read(os.path.join(B, "drive-hardware.step")))]
assert len(new) == len(pn) + len(meta["hardware"]), len(new)
new = [(n, s, bbox(s)) for n, s in new]
print(len(new), "new solids")
print("== new against new ==")
for i in range(len(new)):
    for j in range(i + 1, len(new)):
        if hit(new[i][2], new[j][2]):
            v = vol(new[i][1], new[j][1])
            if abs(v) > 0.2: print("  %7.2f mm3  %s  x  %s   at %s" % (v, new[i][0], new[j][0], new[j][2]))
print("== new against the printer ==")
for name, ins, T in walk(22):
    if "AWD motor idler" in name or name.startswith("9 mm belt drive"): continue
    try:
        sh = shape(ins, T)
        if sh is None: continue
        b = bbox(sh)
    except Exception: continue
    if abs(b[2]) > 1e6: continue
    for n, s, bb in new:
        if hit(b, bb):
            try: v = vol(sh, s)
            except Exception: v = -1
            if abs(v) > 0.2: print("  %7.2f mm3  %s  x  %s   at %s" % (v, name, n, bb))
