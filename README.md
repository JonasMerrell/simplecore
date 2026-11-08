# X-carriage: rCAD project from x-carriage-assembly.x_t

This was built on 2026-11-07 from Jonas's Onshape Parasolid export (`source/x-carriage-assembly.x_t`, 157 bodies, 18 sub-assemblies, 273 placed parts).

To use it, open `X-carriage.json` in rCAD, or import the ZIP next to this folder as a project. It opens on the **Printer** assembly, the working machine. The model needs rCAD master at or after PR #120. Older builds refuse the file (swept surfaces), drop about 2,400 faces, and hang meshing the Sherpa Mini.

Opening the full assembly takes about 3 to 4 minutes the first time, mostly meshing the Sherpa Mini and the printer frame. Single Part Studios open quickly.

## What is in it

| Tabs | Contents |
|---|---|
| 19 printed-part studios | One Part Studio per printed part, in its own local frame (see the table below). |
| Purchased parts | Screws, bearings, GT2 idlers, the MGN9 rail, the Beacon probe and the LSD fan (28 bodies). |
| 3010 blower fan, MGN9H carriage, Sherpa Mini extruder | Each vendor sub-assembly gets its own studio, with parts kept separate and named as in the file. |
| Frame (simplecore_hevort) | The printer frame the carriage was drawn against. |
| 18 assemblies | Built bottom up to mirror the Onshape tree (Corner_B, Z_motor_enclosure, Bed, MGN12H, MGN9-H, Frame, …). **X-carriage** is the top one. Every instance is fixed where the file put it. |

In the original **X-carriage** assembly, the gantry sits about 600 mm past the end of the frame's rails, as it does in the export (the carriage is at x ≈ 1000 mm, the frame at 0 to 500 mm). The **Printer** assembly puts it back on the rails.

## Printer assembly (added 2026-11-07)

The **Printer** tab is the machine with working motion. It is made of four groups, each its own assembly:

| Group | What moves with it |
|---|---|
| Frame (static) | Fixed. Extrusions, panels, feet, corners, the Y rails, the Z rails, the Z motor mounts and enclosures, the Z idler and rail mounts, and both AWD motor idlers. |
| X gantry | The 1 inch tube (X beam), its MGN9 rail, the front and rear gantry ends and caps, the GT2 idlers and bearings on the ends, the bent bracket, and the two MGN9-H blocks that ride the frame rails. |
| Toolhead | The MGN9H block on the beam rail, the carriage top, fan and side plates, the belt clamps, the Sherpa Mini, the LSD hotend, the 3010 blower and the 40 mm fan, the duct, the probe mount, the Beacon, the cable chain mount, and their screws. |
| Bed (Z) | The bed frame and MIC6 plate, the bed mounts, the three MGN12H blocks, the Z carriage mounts, and the Z bed brackets. |

There are three slider mates, with limits taken from where the parts would hit something:

| Mate | Axis | Travel (mm) | What sets the ends |
|---|---|---|---|
| X axis (gantry on Y-rails) | world X | 22 to 351 (gantry centre), 329 of travel | The front-left upright, then the AWD motor idlers |
| Y axis (toolhead on X beam) | world Y | 81 to 402 (MGN9H centre), 321 of travel | The toolhead hits the front and rear gantry ends |
| Z axis (bed on MGN12 rails) | world Z | 126 to 353 (MGN12H centre), 227 of travel | The blocks reach the rail bottom, then the bed top meets the hotend tip |

Drag the toolhead and the gantry follows it in X. Drag the bed and it slides on its rails. The model opens with the gantry and toolhead in the middle and the bed 44 mm below the nozzle.

Not modelled: belts and motors, so CoreXY coupling and leadscrews don't drive anything. The Sherpa gears, fans and idlers don't spin. Ask if you want any of these as revolute mates or gear relations.

`scripts/group.py` splits the parts into the four groups and `scripts/mate.rhai` adds the mates. `scripts/move.rhai` drives each axis past both limits to check them; the screenshots `printer-*.png` come from it.

## Printed parts

The tool tried to rebuild every printed part as a feature tree (sketch, extrude, hole, fillet, chamfer) and compared the result with the imported solid. Only parts that came out **exact** keep the feature tree. The others hold the exact imported body, so nothing is approximated.

| Part | In rCAD | Original mm³ | Rebuilt mm³ | Extra / missing |
|---|---|---|---|---|
| Carriage side plate (Part 2) | **Feature tree:** 3 stacked extrudes, 2 Ø3.2 holes | 14111.507 | 14111.507 | 0 / 0 |
| Belt clamp block (Part 5) | **Feature tree:** stepped extrudes, chamfers, 3 Ø3.2 holes | 3509.498 | 3509.498 | 0 / 0 |
| Belt clamp plate (Part 4) | **Feature tree:** 1 extrude, 0.5 chamfer | 3970.275 | 3970.275 | 0 / 0 |
| Carriage top plate (Part 1) | Imported body | | | |
| Carriage fan plate (Part 3) | Imported body | | | |
| Belt clamp (Part 7), (Part 8) | Imported body | | | |
| 3010 fan mount (Part 6) | Imported body | | | |
| Part cooling duct (Part 10) | Imported body | | | |
| Probe mount (Part 6) | Imported body | | | |
| Rear gantry end + end cap | Imported body | | | |
| Front gantry end + end cap | Imported body | | | |
| AWD motor idler V2 (front, rear) | Imported body | | | |
| Bent bracket, Cable chain mount, 1 inch tube (X beam) | Imported body | | | |

Every part has the colour it had in Onshape, taken from the Parasolid file (`scripts/colour.py`).

What stopped the others:
- Belt clamps, the probe mount, the cable chain mount and the X beam came within 15 to 150 mm³. The difference is one fillet or chamfer loop that OpenCascade would not build.
- The gantry ends, end caps and top plate came out as several separate bodies, because their stepped sections only touch along curved faces.
- The 3010 fan mount, bent bracket and motor idlers have profiles the recogniser couldn't close into sketch regions.
- The cooling duct is a freeform shape that a sketch-and-extrude tree can't represent.

Hand-modelling any of these in rCAD is possible if you want one parametric. Say which.

## STEP files

`step/` has one STEP per printed part, in its local frame and named after the part, ready to slice. These are converted straight from the Parasolid, so they are exact for every part, including the imported ones.

## Known limits

- Validity: 150 of 157 bodies pass OpenCascade's check. The cooling duct (Part 10) has some zero-area faces from the export. It renders and slices, but booleans on it may fail. Six frame and extruder parts (Z idler mount, Corner_B, bed mount, Z carriage mount, Sherpa housing) have the same issue.
- The Sherpa Mini's four knurled heat-set inserts mesh coarsely on screen, because the fine mesh takes minutes. The geometry itself is exact.
- Instances are fixed, with no mates. The Onshape mates are not in a Parasolid export.

## Scripts

These are kept for reference, and they use scratch paths.
- `scripts/x-carriage.rhai` rebuilds the whole document (`rcad script x-carriage.rhai`).
- `scripts/asm.py` generated it from the Parasolid tree. `specs.json` lists every body's placement.
- `scripts/analyze2.rhai`, `emit.py`, `one.py`, `cmp.rhai` and `run1.sh` are the feature recogniser and its comparison check.
- `scripts/xtdump/` is the standalone dump tool built from rCAD's `parasolid.rs`.
