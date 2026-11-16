# 9 mm belt conversion

Branch `claude/project-thread-t6m1uz`. Started 2026-11-15. All numbers are measured from `X-carriage.json`
(Printer assembly, world coordinates, mm). The model has no belts in it, so the belt runs below are
inferred from the idler and pulley positions.

Requirements from Jonas:

- The printer runs 9 mm GT2 belts.
- Every pulley and idler is in double shear (its axle is held on both sides of the belt).
- The CNC XY joints (gantry ends) already work for 9 mm and stay as they are.
- The front motor mounts are missing from the CAD and need designing (AWD: four motors).

## Belt levels (set by the XY joints)

| | Lower belt | Upper belt |
|---|---|---|
| Tooth face on the joint's toothed idler | z 436.56 to 447.56 | z 448.56 to 459.56 |
| Belt centre | z 442.06 | z 454.06 |
| Toothed idler, flange to flange (14 mm) | z 435.06 to 449.06 | z 447.06 to 461.06 |
| Smooth stack (F695 + 695 + F695, 12 mm) | z 436.06 to 448.06 | z 448.06 to 460.06 |

The levels are 12 mm apart. A flanged 9 mm idler or pulley is about 14 mm tall, so anything that
carries both belts needs a clear height of z 435.0 to 461.1 (26.1 mm) between its plates.

## Part by part

| Part | State for 9 mm | Double shear | Action |
|---|---|---|---|
| Front and rear gantry ends + end caps (XY joints) | Already 9 mm: 20T Gates 9 mm idlers, 11 mm tooth face | Yes. Each Ø5 pin sits in the end (below) and the cap (above) | None |
| Toothed idler pins | (207.6, 456.5) lower level and (207.6, −3.5) upper level | Yes | None |
| Smooth F695 stacks | (197.6, 443.8) upper level and (197.6, 9.2) lower level | Yes | None |
| Belt clamps (Part 7 upper, Part 8 lower) | Belt slots are 9.1 mm tall (z 449.66 to 458.76 and 437.36 to 446.46) | n/a | None expected. 0.1 mm clearance is tight, check on a print |
| Belt clamp block (Part 5), clamp plate (Part 4) | Tooth slots 9.8 and 8.8 mm | n/a | None expected |
| Carriage top, fan and side plates | Don't touch the belts | n/a | None |
| AWD motor idler V2 (the two existing motor mounts, +X end) | **Not 9 mm.** Three plates with a 2 mm shelf at z 447.5 to 449.5. Upper bay is 11.0 mm tall (z 449.5 to 460.5), lower bay 11.9 mm (z 435.56 to 447.5). A 14 mm pulley or idler fits neither. Total height 24.94 mm, 1.2 mm short of the 26.1 needed | **No.** The motor pulley hangs on the shaft below the motor with nothing holding the shaft tip. The shelf only has a Ø17 clearance hole. Idler axles are M3 | Redesign |
| Motor mounts at the −X end | Not in the CAD | | Design new |
| Motor pulleys | Model assumes GT2 20T | | 9 mm wide 20T, 5 mm bore |

## The rear motor mounts in detail

- Motor axis: (403.35, 429.35) on the +Y side and (403.35, 23.65) on the −Y side. Motor face at z 463.5, shaft down.
- The +Y motor lines up with the upper-level smooth stack (belt run at y ≈ 436), the −Y motor with the lower-level stack (run at y ≈ 17).
- With a standard 24 mm shaft the tip is at z 439.5.
  - Upper belt pulley (teeth z 448.56 to 459.56): 7 mm of shaft is left below the pulley, enough for a support bearing (695, 5×13×4, or 625, 5×16×5) in a plate under it.
  - Lower belt pulley (teeth z 436.56 to 447.56): the shaft ends 3 mm above the bottom of the teeth. Double shear from above is impossible with a 24 mm shaft.
- Hanging the lower-belt motor from below (shaft up) at the same position doesn't fit: the body (42 mm square) would overlap the rear 2020 (x 404.5 to 424.5, z 401 to 421).
- M3 screw axles with Ø6.5 printed spacer posts: (385.5, 456.5), (394.5, 416.2), (407.0, 443.7) on the +Y mount, mirrored on the −Y mount.

## Belt path (from Jonas's photos of 2026-11-15 and the idler positions in the CAD)

`beltpath.py` computes it and draws `beltpath.png`. It also checks that each belt's length stays constant over the whole travel.
Front is −X, rear is +X. Seen from the front door, +Y is the left side and −Y the right side, and the picture is drawn that way (the first version of it was mirrored).
The upper belt's motors are on the left, the lower belt's on the right.

- **Belt U (upper level):** carriage → +Y joint smooth stack → forward at y 450.67 → front idler I1 → **front +Y motor**, 180° → front idler I3 →
  back along the +Y side at y ≈ 463.4, through the joint → rear +Y idler A → idler C → **rear +Y motor**, 187° →
  across the back → rear −Y guide B → rear −Y idler A → forward at y −9.87 → −Y joint toothed idler → carriage.
- **Belt L (lower level)** is the mirror image: −Y joint smooth stack → front −Y motor → −Y side → rear −Y A, C,
  **rear −Y motor** → across the back → rear +Y B, A → +Y joint toothed idler.
- The two belts cross at the back on their own levels. Each front corner carries one belt, each rear corner both.

## The drive, rev C (2026-11-16): every component modelled, in the full printer CAD

Rev C replaces rear rev B and front rev A (their files are in git history). The layout in plan is unchanged; what changed is the height
of the bay, because a real 9 mm 20T pulley has a 6 mm hub (Ø16, two set screws) that must not sit in the other belt's level:
at the rear the crossing belt passes 1.9 mm from the shaft. So each pulley's hub points away from the other belt.

| | Lower plate | Bay (32.2 mm) | Upper plate | Motor face | Pulley |
|---|---|---|---|---|---|
| Left mounts (+Y), upper belt | z 429 to 435 | 435 to 467.2 | 467.2 to 473.2 | z 511.2 | teeth on the upper level, hub up (z 461.06 to 467.06) |
| Right mounts (−Y), lower belt | z 423 to 429 | 429 to 461.2 | 461.2 to 467.2 | z 505.2 | teeth on the lower level, hub down (z 429.06 to 435.06) |

The right-hand parts are the mirror image about y = 226.5, 6 mm lower. Their lower plates sit beside the Y rail (top z 427.5), so they are cut back round it.

`drive.py` builds everything: it takes the belt outlines from `beltpath.py`, writes `drive.rhai` from `drive.rhai.in` and runs rCAD on it.

- `drive.json`: editable rCAD document with the **10 machined parts** (6061, 6 mm plate and two 19.6 × 12.2 × 32.2 bars), all sizes as variables.
  Lower plates are cut from the top face, upper plates from the underside: one setup each. R3 outside corners, Ø6.4 corner reliefs where a plate wraps an extrusion or the rail end.
- `drive-plates.step`, `drive-hardware.step`, `drive-parts.json` (name, colour, material of every hardware solid; the motor poses).
- In `X-carriage.json`: Part Studios "9 mm drive, machined parts" and "9 mm drive, hardware and belts", assembly "9 mm belt drive" (200 instances),
  placed in the Printer assembly. The two old rear motors and the two old "AWD motor idler V2" mounts are hidden, not deleted.
  `../scripts/belt9_splice.py` does this and can be re-run after `drive.py`.

### What is in each mount

- **Drive shaft** Ø5 × 55 in two 695 bearings (5 × 13 × 4), one in a 4 mm pocket in each plate. On it: the **GT2 20T 9 mm pulley** and an Ø8 × 12 spacer that fills the other belt's level.
  Rear shafts at (403.3, 433.0), front shafts at (3.5, 422.0), mirrored on the right.
- **Motor** NEMA 17 (40 mm) shaft down above the upper plate on Ø7 × 38 standoffs with M3 × 45 from counterbores in the bay roof, joined to the shaft by a rigid clamp coupling 5 to 5 mm (Ø19 × 25).
  Front motors have four screws. **Rear motors have three:** the fourth hole would break into idler pin C's hole (0.1 mm of plate left), so it is left out.
- **Idlers** on Ø5 × 44 pins through both plates, F695 + 695 + F695 stacks as on the XY joints. Rear: pins A (385.5, 455.36) and C (391.0, 422.4), a stack on each level, 1 mm shim and 7 mm sleeve to fill the bay.
  Front: pins I1 (16.74, 443.8) and I3 (4.64, 455.89), one stack on the corner's belt level, 13 mm and 7 mm sleeves.
- **Rear fixing:** three M5 (× 55 left, × 50 right) down through upper plate, Ø8 × 32.2 standoff, lower plate and an Ø9 riser (8 mm left, 2 mm right) into T-nuts in the top slots
  of the rear 2020 (414.5, 400 and 414.5, 441.5) and the side 2020 (399.5, 466.5). A fourth standoff at (386, 402) with M5 × 45 tapped into the lower plate.
- **Front fixing:** spine bar against the upright's inner face with two M5 × 16 into T-nuts in that face's slot, two M4 × 12 into each end of the bar from the plates, and three Ø8 × 32.2 standoffs with M5 × 45 tapped into the lower plate.
- **Belts:** both drawn as the 9 mm backing band in the model pose, 1852 mm each between the clamp points on the carriage (add the length inside the clamps).

Bill of materials (hardware, all four mounts): 4 pulleys GT2 20T 9 mm bore 5; 4 shafts Ø5 × 55; 4 couplings 5-5; 4 NEMA 17; 20 × 695; 24 × F695; 8 pins Ø5 × 44; 4 spacers Ø8 × 5 × 12;
8 sleeves Ø8 × 5 × 7; 4 sleeves Ø8 × 5 × 13; 4 shims Ø8 × 5 × 1; 14 plate standoffs Ø8 × 5.3 × 32.2; 14 motor standoffs Ø7 × 3.2 × 38; 3 risers Ø9 × 8 and 3 Ø9 × 2;
14 M3 × 45; 8 M4 × 12; 4 M5 × 16; 8 M5 × 45; 3 M5 × 50; 3 M5 × 55; 10 M5 T-nuts; 2 belts.

### Checked

`../scripts/belt9_check.py` intersects all 196 new solids with each other and with every imported part of the Printer assembly (model pose).
Result: no interference, apart from screw threads in their tapped holes and one thing that is not part of the new mounts:

- The drawn belt run from each joint's toothed idler to the carriage (x 201.2) cuts 0.6 mm into the boss round the smooth-stack pin in the gantry end.
  The joints are existing parts that work, so the real run must sit about 1 mm further out than drawn (the clamp starts at x 202.5).

The PIR boards, panels and the standard NEMA motors are feature-tree parts and are not in that check.

### Pictures (rendered from `X-carriage.json` with `render-full.json`; enclosure, door and PIR hidden)

`full-overview.png`, `full-rear-left.png`, `full-rear-right.png`, `full-front-left.png`, `full-front-right.png`.
`bay.py` draws each bay from above with the upper plate and motor left out: `bay-rear-left.png`, `bay-rear-right.png`, `bay-front-left.png`, `bay-front-right.png` (rear of the printer at the top, left side on the left).
Opening `X-carriage.json` needs rCAD 0.8.0 or newer.

### Open

- **X travel.** At the front the bent bracket on the left gantry end (x 151 at the model pose) meets the front-left plates (x 27.3) at gantry X 62; the model's limit was 22.
  At the rear the joint's toothed idler meets idler A's flanges at X 348 (limit was 351). The real printer already loses front travel to its printed mounts; how much is not known.
- **Toolhead in the corners.** By bounding box, the toolhead reaches 71 mm in front of the gantry centre and 35 mm behind it. With the gantry within about 36 mm of either X end and the carriage
  within about 30 mm of either Y end it would meet a mount. This is a conservative estimate, not refined part against part.
- **PIR back board** pockets were cut for the old motors (face z 463.5). The new rear motors sit 42 to 48 mm higher and 3.7 mm further out in Y, so the pockets need re-cutting.
- The front mount hangs off one face of the upright through the spine bar. A second fixing would stiffen it. The rear mounts have nothing tying them to the upright sideways.
- Tight spots: coupling to the (414.5, 441.5) M5 head 0.4 mm, that head to the motor standoff 0.4 mm, belt to the (414.5, 400) standoff 1.4 mm, front idler I1 pin to a motor screw counterbore 0.95 mm.
- Shaft, spacer and sleeve lengths are nominal; the pulley has 0.14 mm end float to shim.

## Firmware

20T pulleys on 2 mm pitch keep `rotation_distance: 40`, so 9 mm belts alone need no Klipper change.
The config backup is in JonasMerrell/simplecore-config. Belt tension and input shaper need re-tuning after the swap.

## Files

- `section-lower-belt-z442.png`, `section-upper-belt-z454.png`: plan sections through each belt level (X up = rear, Y across). Black frame, blue gantry, red toolhead.
- `rear-motor-mount.png`: the existing +Y motor mount.
- `beltpath.py`, `beltpath.png`: the belt path.
- `drive.py`, `drive.rhai.in`, `drive.rhai`, `drive.json`, `drive-*.step`, `drive-parts.json`, `import.json`, `render-full.json`, `full-*.png`, `bay.py`, `bay-*.png`: the rev C drive (above).
- `../scripts/belt9_splice.py`, `belt9_check.py`: put the drive into `X-carriage.json`; interference check.
- `../scripts/belt9_lib.py`, `belt9_sections.py`: the measuring scripts (need `pip install cadquery-ocp`; scratch paths inside).
