#!/usr/bin/env python3
"""Toolhead keep-out shape below the nozzle, from the rCAD printer model.

    python3 scripts/clearance/mkrun.py X-carriage-no-belts.json OBJDIR > run.json
    rcad run run.json
    python3 scripts/clearance/derive.py X-carriage-no-belts.json OBJDIR clearance/

Places every toolhead and X-gantry body with the Printer assembly's poses, takes the
nozzle tip as the lowest point of the Goliath hotend, and writes into clearance/:

  toolhead-clearance.json   stepped-cone profile (radius -> lowest height above the tip),
                            per-part breakdown, gantry height, OrcaSlicer setting strings
  toolhead-nozzle-frame.stl the toolhead (no gantry) in the nozzle frame, for
                            toolhead_clearance_mesh: tip at the origin, printer
                            (firmware) axes X = CAD -Y, Y = CAD +X, Z up
  toolhead-underside.png    height map and profile plot (if matplotlib is installed)

The Beacon's sensing volume (round bodies below the PCB) is not solid and is left out.
"""
import json
import math
import os
import struct
import sys

import numpy as np

SKIP_STUDIOS = {"Sherpa Mini extruder", "Frame (simplecore_hevort)"}
HOTEND = "LSD Air cooled_1"        # the Goliath body (official VzBoT STEP, scripts/goliath)
BAND = 0.5                         # profile radius bands (mm)
MESH_DZ_MAX = 30.0                 # drop toolhead triangles entirely above this (the gantry is at ~29)


def mat(pose):
    r = np.array(pose["r"], float).reshape(3, 3).T   # column-major
    return r, np.array(pose["t"], float)


def compose(a, b):
    return a[0] @ b[0], a[0] @ b[1] + a[1]


def leaves(doc, ai, pose, path, out):
    for ins in doc["assemblies"][ai]["instances"]:
        if ins.get("hidden"):
            continue
        p = compose(pose, mat(ins["pose"]))
        if ins.get("sub") is not None:
            leaves(doc, ins["sub"], p, path + [ins["name"]], out)
        else:
            out.append((ins, p, path))
    return out


def read_obj(path):
    bodies, verts, cur = [], [], None
    for line in open(path):
        if line.startswith("o "):
            cur = {"name": line[2:].strip(), "v0": len(verts), "f": []}
            bodies.append(cur)
        elif line.startswith("v "):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            cur["f"].append([int(x.split("/")[0]) - 1 for x in line.split()[1:4]])
    V = np.array(verts, float).reshape(-1, 3)
    out = []
    for i, b in enumerate(bodies):
        F = np.array(b["f"], int).reshape(-1, 3)
        used = np.unique(F) if len(F) else np.array([], int)
        out.append({"name": b["name"], "V": V, "F": F, "used": used})
    return out


def body_of(objs, ref):
    # body [feature, k]: imported studios hold k-th body of the import; single-body studios one
    if len(objs) == 1:
        return objs[0]
    k = ref[1]
    return objs[k] if k < len(objs) else None


def main():
    model, objdir, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    doc = json.load(open(model))
    pr = next(a for a in doc["assemblies"] if a["name"] == "Printer")
    ident = (np.eye(3), np.zeros(3))
    groups = {}
    for ins in pr["instances"]:
        for g in ("Toolhead", "X gantry"):
            if ins["name"].startswith(g + " <"):
                groups[g] = leaves(doc, ins["sub"], compose(ident, mat(ins["pose"])), [ins["name"]], [])
    cache = {}
    parts = []   # (group, name, triangles Nx3x3 world)
    missing = []
    for g, items in groups.items():
        for ins, (R, t), path in items:
            s = ins["studio"]
            sname = doc["studios"][s]["name"]
            if sname in SKIP_STUDIOS:
                continue
            f = os.path.join(objdir, f"studio{s}.obj")
            if not os.path.exists(f):
                missing.append(sname)
                continue
            if s not in cache:
                cache[s] = read_obj(f)
            b = body_of(cache[s], ins["body"])
            if b is None or not len(b["F"]):
                missing.append(f"{ins['name']} (studio {s} body {ins['body']}, no mesh)")
                continue
            tri = b["V"][b["F"]] @ R.T + t
            parts.append({"group": g, "name": ins["name"].rsplit(" <", 1)[0], "inst": ins["name"], "obj": b["name"], "tri": tri})

    hot = [p for p in parts if p["name"] == HOTEND]
    if not hot:
        sys.exit("no Goliath hotend body found")
    tip_i = np.argmin(hot[0]["tri"][:, :, 2])
    tip = hot[0]["tri"].reshape(-1, 3)[tip_i]
    # Beacon sensing volume: Beacon bodies reaching below the tip (round, not solid)
    sensing = [p for p in parts if p["name"] == "Beacon_RevH" and p["tri"][:, :, 2].min() < tip[2] - 0.05]
    for p in sensing:
        p["sensing"] = True

    def nozzle_frame(tri):
        d = tri - tip
        return np.stack([-d[..., 1], d[..., 0], d[..., 2]], axis=-1)   # firmware X=-Ycad, Y=+Xcad

    # per part: lowest point above the tip and where (radius from the nozzle axis)
    rows = []
    for p in parts:
        n = nozzle_frame(p["tri"]).reshape(-1, 3)
        k = np.argmin(n[:, 2])
        r = np.hypot(n[:, 0], n[:, 1])
        low = n[:, 2] < n[k, 2] + 0.5
        rows.append({"part": p["name"], "group": p["group"], "sensing_volume_ignored": bool(p.get("sensing")),
                     "lowest_mm": round(float(n[k, 2]), 3),
                     "at_xy_mm": [round(float(n[k, 0]), 2), round(float(n[k, 1]), 2)],
                     "radius_mm": [round(float(r[low].min()), 2), round(float(r[low].max()), 2)],
                     "x_range_mm": [round(float(n[:, 0].min()), 1), round(float(n[:, 0].max()), 1)],
                     "y_range_mm": [round(float(n[:, 1].min()), 1), round(float(n[:, 1].max()), 1)]})
    rows.sort(key=lambda r: r["lowest_mm"])

    tool = [p for p in parts if p["group"] == "Toolhead" and not p.get("sensing")]
    gantry = [p for p in parts if p["group"] == "X gantry"]
    gantry_low = min(nozzle_frame(p["tri"])[..., 2].min() for p in gantry) if gantry else math.inf

    # Height field of the toolhead underside on a 0.25 mm grid (vertices + face centres +
    # edge samples, so thin faces aren't missed), then the radial envelope.
    pts = []
    for p in tool:
        n = nozzle_frame(p["tri"])
        keep = n[..., 2].min(axis=1) < MESH_DZ_MAX
        n = n[keep]
        # subdivide triangles: sample barycentric points so big faces are covered
        if not len(n):
            continue
        e = np.max(np.linalg.norm(n[:, [1, 2, 0]] - n, axis=2), axis=1)
        for m in (1, 2, 4, 8, 16, 32, 64):
            sel = (e <= m * 0.25) if m < 64 else (e > 16 * 0.25)
            if m > 1:
                sel &= e > (m // 2) * 0.25
            if not sel.any():
                continue
            t = n[sel]
            a = np.array([(i, j) for i in range(m + 1) for j in range(m + 1 - i)], float) / m
            w = np.stack([a[:, 0], a[:, 1], 1 - a[:, 0] - a[:, 1]], 1)
            pts.append(np.einsum("kb,tbc->tkc", w, t).reshape(-1, 3))
    P = np.concatenate(pts)
    P[:, 2] = np.maximum(P[:, 2], 0.0)
    cell = 0.25
    ext = 100.0
    P = P[(np.abs(P[:, 0]) <= ext) & (np.abs(P[:, 1]) <= ext)]
    ix = np.round(P[:, 0] / cell).astype(int)
    iy = np.round(P[:, 1] / cell).astype(int)
    h = int(ext / cell)
    H = np.full((2 * h + 1, 2 * h + 1), np.inf)
    np.minimum.at(H, (iy + h, ix + h), P[:, 2])
    gy, gx = np.mgrid[-h:h + 1, -h:h + 1] * cell
    R = np.hypot(gx, gy)
    nb = int(ext / BAND) + 1
    band_low = np.full(nb, np.inf)
    fin = np.isfinite(H)
    np.minimum.at(band_low, (R[fin] / BAND).astype(int).clip(0, nb - 1), H[fin])
    # stepped profile: merge bands of equal (rounded) height, keep it conservative
    steps = []
    for b in range(nb):
        hb = band_low[b]
        if not np.isfinite(hb):
            continue
        hb = math.floor(hb * 100) / 100
        if steps and abs(steps[-1][1] - hb) < 1e-9:
            steps[-1][0] = (b + 1) * BAND
        else:
            steps.append([(b + 1) * BAND, hb])
    # A coarser version for the setting: merge neighbouring bands whose heights lie within
    # MERGE mm of each other, keeping the lowest (so it is never higher than the envelope).
    MERGE = 0.6
    simple, lo, hi = [], None, None
    for r, hb in steps:
        if simple and max(hi, hb) - min(lo, hb) <= MERGE:
            lo, hi = min(lo, hb), max(hi, hb)
            simple[-1] = [r, lo]
        else:
            lo = hi = hb
            simple.append([r, hb])
    if np.isfinite(gantry_low):
        simple.append([1000.0, math.floor(gantry_low * 10) / 10])
        steps.append([1000.0, math.floor(gantry_low * 100) / 100])

    def setting(st):
        return ", ".join(f"{r:g}x{hb:g}" for r, hb in st)

    os.makedirs(outdir, exist_ok=True)
    tool_frame_bb = np.concatenate([nozzle_frame(p["tri"]).reshape(-1, 3) for p in tool])
    res = {
        "source": os.path.basename(model),
        "frame": "nozzle tip at the origin; printer (firmware) axes: X = CAD -Y, Y = CAD +X, Z up",
        "nozzle_tip_cad_mm": [round(float(v), 3) for v in tip],
        "gantry_lowest_above_tip_mm": round(float(gantry_low), 3),
        "toolhead_bbox_nozzle_frame_mm": [[round(float(v), 2) for v in tool_frame_bb.min(0)], [round(float(v), 2) for v in tool_frame_bb.max(0)]],
        "profile_steps": [{"radius": r, "height": hb} for r, hb in steps],
        "profile_simple": [{"radius": r, "height": hb} for r, hb in simple],
        "orca": {"toolhead_clearance_profile": setting(simple), "toolhead_clearance_mesh": "toolhead-nozzle-frame.stl",
                 "toolhead_clearance_margin": 0.2},
        "parts_by_lowest_point": rows,
        "not_meshed": sorted(set(missing)),
    }
    json.dump(res, open(os.path.join(outdir, "toolhead-clearance.json"), "w"), indent=1)

    # STL: toolhead only (the gantry spans the bed, it's the profile's far step)
    tris = np.concatenate([nozzle_frame(p["tri"]) for p in tool])
    tris = tris[tris[..., 2].min(axis=1) < MESH_DZ_MAX]
    with open(os.path.join(outdir, "toolhead-nozzle-frame.stl"), "wb") as f:
        f.write(b"rCAD simplecore toolhead, nozzle frame".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for t in tris.astype(np.float32):
            nrm = np.cross(t[1] - t[0], t[2] - t[0])
            ln = np.linalg.norm(nrm)
            nrm = nrm / ln if ln > 0 else nrm
            f.write(struct.pack("<12fH", *nrm, *t.reshape(-1), 0))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
        show = np.where(np.isfinite(H), np.minimum(H, 25), np.nan)
        im = ax[0].imshow(show, origin="lower", extent=[-ext, ext, -ext, ext], cmap="viridis_r")
        ax[0].set_xlim(-60, 60); ax[0].set_ylim(-60, 60)
        ax[0].set_xlabel("printer X from nozzle (mm)"); ax[0].set_ylabel("printer Y from nozzle (mm)")
        ax[0].set_title("Toolhead underside, height above nozzle tip (mm, capped 25)")
        fig.colorbar(im, ax=ax[0])
        rr = [0]; hh = []
        for r, hb in steps[:-1] if np.isfinite(gantry_low) else steps:
            rr.append(r); hh.append(hb)
        ax[1].stairs(hh, rr, label="band minimum", color="C0")
        rs = [0] + [r for r, _ in simple[:-1]]
        ax[1].stairs([hb for _, hb in simple[:-1]], rs, label="setting (simplified)", color="C3", lw=2)
        if np.isfinite(gantry_low):
            ax[1].axhline(gantry_low, color="gray", ls="--", label=f"X gantry {gantry_low:.1f}")
        ax[1].set_xlim(0, 70); ax[1].set_ylim(0, min(40, max(hh) + 2))
        ax[1].set_xlabel("radius from nozzle axis (mm)"); ax[1].set_ylabel("lowest toolhead point above tip (mm)")
        ax[1].set_title("Stepped-cone keep-out"); ax[1].legend(); ax[1].grid(alpha=.3)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "toolhead-underside.png"), dpi=110)
    except ImportError:
        pass
    print(json.dumps({k: res[k] for k in ("nozzle_tip_cad_mm", "gantry_lowest_above_tip_mm", "orca")}, indent=1))
    for r in rows[:14]:
        print(f"  {r['lowest_mm']:8.3f}  r {r['radius_mm'][0]:6.2f}-{r['radius_mm'][1]:6.2f}  {r['part']}{' (sensing, ignored)' if r['sensing_volume_ignored'] else ''}")


if __name__ == "__main__":
    main()
