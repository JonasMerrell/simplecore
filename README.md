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

## Changes on 2026-11-10

- **Spinning parts.** Revolute mates now hold the 3010 blower's impeller (both halves) on its pin, the Sherpa Mini's drive shaft (with the 50T gear, the drive gear and the set screw fastened to it), the Sherpa idler gear on its shaft, and the six GT2 idlers on the gantry ends. A gear relation (ratio 1, opposite directions) couples the two Sherpa filament gears. The 40 mm fan is a single body, so it can't spin. The motor's 10T pinion is part of the NEMA14 body, so it doesn't spin either.
- **CoreXY drive.** Two NEMA 17 steppers (40 mm) now sit in the motor pockets of the AWD motor idlers, shaft down: Motor A on the rear mount, Motor B on the front. Each has a revolute mate to the frame. Two **belt** relations (pitch radius 40/2π mm, a GT2 20T pulley) tie them to the X and Y sliders: Motor A turns with X + Y, Motor B with X − Y. Moving the toolhead 60 mm in X turns both motors 1.5 turns, and moving it 80 mm in Y turns them 2 turns in opposite directions. Which motor is A and which is B is a guess.
- **Needs rCAD with the belt relation** (PR #129) to open. `X-carriage-no-belts.json` has everything except the two belt relations and opens on master at or after PR #120. The file as it was is the first commit in the history.

## Changes on 2026-11-11: enclosure panels and front door

- **Panels.** A new Part Studio, **Enclosure panels**, holds four 3 mm aluminium (6061) panels and the 6 mm polycarbonate front door. They are plain sketch-and-extrude features in world position, and the thicknesses are the variables `panel_t` (3) and `door_t` (6).
  - The printer's front is −X. The frame's own `back_panel_spacers` sit on the +X side.
  - Side panels sit on the existing 1 mm side spacer strips. Right side (−Y): y −27.5 to −24.5. Left side (+Y): y 477.5 to 480.5. Both are 459 × 509.2 mm (x −25.5 to 433.5, z 81 to 590.2), so they lap the back panel's edges.
  - Back panel: 500 × 509.2 mm on the 6 mm back spacers, at x 430.5 to 433.5. The 50 mm bay behind it (x 433.5 to 474.5) stays outside the enclosure.
  - Top panel: 459 × 508 mm on the top rails (z 590.2 to 593.2). It laps the side panels.
  - Bottom: the frame already has `Bottom_pannel` (3.175 mm, inside on the bottom rails), so no new bottom panel was added.
  - Front door: 500 × 509.2 mm, 6 mm PC, R5 corners. It is hinged on the left side (+Y) when you face the front. It sits between the hinge arms and the frame (x −34.8 to −28.8, 3.3 mm off the frame), screwed to the arms' flat face. Each hinge has a cut-out on the door edge and two Ø3.4 holes, 23 and 38 mm in from the edge. The cut-out follows the K3 door DXF: 14 deep over 73 mm, with 21 deep lobes where the bearing blocks' mounting feet pass through.
- **Hinge: the real Annex Gasherbrum K3 door hinge.** These are the published STLs from github.com/Annex-Engineering/Gasherbrum-K3, `Release_1_2/STLs/Summit_Enclosure/Front_Panel_Hinges_and_Locks` (ANNEX Engineering License Agreement). Copies are in `k3-hinge/`.
  - They are imported as meshes into the **Annex K3 door hinge** Part Studio, so they are exact but not editable.
  - Each hinge is three parts: the door arm, with bearing block 2 above it and bearing block 1 turned over below it. There are two hinges, centred at z 156 and z 515.
  - The pivot is vertical at x −38.35, y 485, which is 13 mm in front of the frame's front face and 8.5 mm outside the left edge. The blocks bolt to the front face of the front-left upright, with an M5 screw on the upright's slot centre (y ≈ 466). The door sits on the arms' flat face, on the frame side (fixed 2026-11-11: it was first on the arms' outer side).
  - **What's approximate:** the published files are STLs, not an assembly. I placed the parts from their geometry: the arm's door-screw holes and the block rings line up on one axis, and I matched the screw spacing to the K3 door DXF. There is a 0.5 mm gap above and below the arm for the bearings. The handle and magnet catch from the same folder are not added.
- **Assemblies.** **Enclosure** holds the four panels and the four bearing blocks, all fixed. **Front door** holds the door and both arms. Both are inserted into **Printer**: Enclosure is fixed (instance 15) and Front door is instance 16. In X-carriage-no-belts.json they are instances 13 and 14, and the door mate is 15.
- **Door mate.** The revolute mate **Front door hinge** (mate 17) joins the door to Enclosure on the pivot axis, with limits −240° to 0°. At 0° the door is shut, and negative angles open it outwards. A sweep in 5° to 15° steps found no contact until about 245°, where the folded-back door touches the left side panel. The limit is 240°. Dragging the door past a limit in the GUI pulled it off its hinge. rCAD PR #134 fixes that. Until it merges, don't drag the door past either end.
- **Checks.** The panels' bounding boxes were checked against every frame part. They touch the spacers and rails and don't overlap anything. The door and arms don't touch the blocks or panels anywhere from 0° to 240°. This was checked in a small test document, because rCAD's interference check times out on the whole Printer.
- **Files.** X-carriage.json and X-carriage-no-belts.json both have the enclosure. The file as it was before this change is in the history (commit "Spinning parts and the CoreXY drive"). Renders are in `renders/enclosure-*.png`.

## Changes on 2026-11-11: PIR insulation

- **What.** A new Part Studio, **PIR insulation**, holds eight 25.4 mm (1 inch) PIR foam boards: the base, the top, the back (lower and upper) and both sides (lower and upper). The thickness is the variable `pir_t`. The assembly **PIR insulation** holds them, fixed, and is in **Printer** as instance 18 (instance 16 in X-carriage-no-belts.json). Hide that one instance to see the printer without it. No material is set, because rCAD's only foam (Urethane foam, 0.24 g/cm³) is about seven times denser than PIR.
- **Where the boards sit.** Each wall board sits in the bay between the extrusions, flat against the inside of its aluminium panel, and stands 4.4 mm (sides) or 0.6 mm (back) proud of the extrusions' inner faces.
  - **Base:** on top of the existing `Bottom_pannel`, z 104.18 to 129.58, over the whole panel. Notches go round the four uprights.
  - **Top:** the full top bay between the top extrusions, z 564.8 to 590.2, under the top panel.
  - **Back:** x 405.1 to 430.5 against the back panel. Lower board z 129.6 to 401 (sits on the base board), upper board z 421 to 570.2.
  - **Sides:** right (−Y) y −24.5 to 0.9, left (+Y) y 452.1 to 477.5. Lower boards z 129.6 to 398 (they stop under the `backer-y-axis` strips under the mid rails), upper boards z 468 to 564.8 (they stop under the top board).
  - **Front (door):** not insulated, so the PC door stays clear.
- **Cut-outs.** Every frame part, motor and moving part was checked against every board. Moving parts were checked over their full travel: the gantry over X 22 to 351, the toolhead over X and Y, and the bed over Z 126.2 to 352.9. Each overlap became a rectangular cut-out with 2 mm clearance. Each cut-out is a feature named after what it clears. If the part reaches through the board, the cut goes through. If not, it's a pocket from the side the part comes from.
  - **Base:** through holes for the three Z rails and their MGN12H blocks. 18.8 mm pockets from below over the three Z motor mounts, plus shallow ones over the Z motor enclosure caps. 21.6 mm pockets from above where the Z carriage mounts come down at the bottom of Z travel. At the lowest Z the bed frame clears the base board by 5.9 mm, so Z travel is unchanged.
  - **Sides, lower:** a vertical groove for the Z rail (6.4 mm deep) and for its MGN12H block over its travel (3.4 mm). A notch through at the top for the Z rail top mount.
  - **Sides, upper:** the gantry ends ride flush with the frame's outer face, so there's no room for a board where they travel. That leaves an uninsulated band from the mid extrusion up to z 468 along both sides (47 mm above the extrusion). There's also a notch through for the AWD motor idler at the back corner.
  - **Back:** a 1.5 mm groove for the rear Z rail. A 21.5 mm pocket for the rail's top mount. 21.4 mm pockets for the AWD idlers and motors in the upper corners. 6 mm rebates on the panel side over the back-panel spacers.
  - The NEMA 17 bodies sit 1.6 mm from the upper side boards, and the gantry's 695 bearings sit 1.8 mm away. Both are just inside the 2 mm clearance, so they get no pocket.
- **What's assumed.** The cut-outs are inferred from the model, not from your boards. The model has no wiring, cable chain runs, fans or electronics, so any pass-throughs for them aren't cut. The cut-outs are rectangles around each part's bounding box, so they are a little generous on round or angled parts.
- **Checks.** All eight boards build with no feature errors, and their volumes match an independent calculation of the same cuts. The clash check uses bounding boxes, which over-cover every part, so a board can't touch a part's real shape when it clears the box. rCAD's own interference check on the whole Printer still times out.
- **Renders:** `renders/pir-printer.png` (enclosure and door hidden) and `renders/pir-boards.png`.
- **Scripts:** `scripts/pir/` regenerates the boards: `walk.py` + `wb.py` (world bounding boxes of every part), `gen.py` (boards and cut-outs, `boards.json`), `mk.py` (the rCAD run script) and `splice.py` (adds the studio and assembly to the document).

## Changes on 2026-11-11: chamber heater

- **What.** A PTCYIDU 500 W 110 V PTC fan heater (Amazon B0CP1XPW67). Its real size isn't published, so the model uses a **placeholder envelope of 52 × 87.5 × 60 mm** (depth × width × height), from PTCYIDU's closest listed fan heater (87.5 × 60 × 52 mm, 400 W). Replace it once the heater is measured: `scripts/heater/mkheater.py X Y Z` rebuilds everything.
- **Where.** The back-right corner (−Y side), low, behind the bed: x 335.1 to 387.1, y 61.25 to 148.75, z 139.6 to 199.6. The outlet faces the front (−X), so warm air runs under the bed and up past the door. The intake has 18 mm of air to the back insulation.
  - Why there: it's the only spot that's free over the whole travel and low in the chamber. The bed covers almost all of the floor and comes down to 5.9 mm above the base board, so nothing fits under it. The strip in front of the bed (58 mm deep) would also work, but it is behind the uninsulated door. The back corners are 80 mm deep behind the bed plate (MIC6 ends at x 324.6), and the rear Z rail splits them in two.
  - Clearances, from swept bounding boxes over all X, Y and Z travel: 10.5 mm to the bed plate's back edge (at the bottom of Z), 18 mm to the back PIR, 60 mm to the right side PIR, about 120 mm to the rear Z rail and its carriage, and nearly 200 mm below the gantry and toolhead.
- **Stand.** Two 10 mm placeholder legs under the heater, standing on the aluminium `Bottom_pannel` through the base insulation. They hold the heater 10 mm above the foam, so the foam doesn't take the heater's weight or its housing heat.
- **Cut-outs.**
  - PIR base: two through slots for the legs (56 × 14 mm each, 2 mm clearance).
  - PIR back, lower: a 24 × 24 mm through hole for the power cord, centred at y 105, z 169.6.
  - Back aluminium panel: a Ø16 mm hole behind it for a cord grommet.
- **Model.** Part Studio **Chamber heater** (variables `heater_x`, `heater_y`, `heater_z`), assembly **Chamber heater**, in Printer as instance 19 (instance 17 in X-carriage-no-belts.json). The cut-outs are new features at the end of the PIR insulation and Enclosure panels studios. The file before this change is in the history.
- **Renders:** `renders/heater-overview.png` and `renders/heater-closeup.png` (door and panels hidden, bed at the bottom of Z).
