#!/usr/bin/env python3
"""Write an `rcad run` script that exports every Part Studio the toolhead and X gantry
use as OBJ (one `o` group per body, in the studio's own frame).

    python3 scripts/clearance/mkrun.py X-carriage-no-belts.json OUT_DIR > run.json
    rcad run run.json            # a few minutes per studio, headless

derive.py then places the bodies with the assembly poses from the same JSON.
"""
import json
import os
import sys

SKIP = {"Sherpa Mini extruder", "Frame (simplecore_hevort)"}  # on top / static: can't reach below the nozzle


def studios_under(doc, ai, acc):
    for ins in doc["assemblies"][ai]["instances"]:
        if ins.get("hidden"):
            continue
        if ins.get("sub") is not None:
            studios_under(doc, ins["sub"], acc)
        else:
            acc.add(ins["studio"])
    return acc


def group(doc, name):
    pr = next(a for a in doc["assemblies"] if a["name"] == "Printer")
    ins = next(i for i in pr["instances"] if i["name"].startswith(name + " <"))
    return ins["sub"]


def main():
    model, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    doc = json.load(open(model))
    used = set()
    for g in ("Toolhead", "X gantry"):
        studios_under(doc, group(doc, g), used)
    steps = [{"tool": "open_document", "args": {"path": model}}]
    for s in sorted(used):
        if doc["studios"][s]["name"] in SKIP:
            continue
        steps.append({"tool": "switch_part_studio", "args": {"index": s}})
        steps.append({"tool": "export", "args": {"format": "obj", "path": os.path.join(out, f"studio{s}.obj")}})
    json.dump(steps, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
