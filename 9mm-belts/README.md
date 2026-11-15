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
Front is −X, rear is +X.

- **Belt U (upper level):** carriage → +Y joint smooth stack → forward at y 450.67 → **front +Y motor**, 180° →
  back along the +Y side at y ≈ 463.4, through the joint → rear +Y idler A → idler C → **rear +Y motor**, 187° →
  across the back → rear −Y guide B → rear −Y idler A → forward at y −9.87 → −Y joint toothed idler → carriage.
- **Belt L (lower level)** is the mirror image: −Y joint smooth stack → front −Y motor → −Y side → rear −Y A, C,
  **rear −Y motor** → across the back → rear +Y B, A → +Y joint toothed idler.
- The two belts cross at the back on their own levels. Each front corner carries one belt, each rear corner both.
- The front pulley centres follow from the joints: (x free, y 457.04) upper level at +Y and (x free, y −4.04) lower level at −Y.

## Rear motor mounts, rev B

Jonas chose a separate supported shaft for the motor pulleys, and the parts are to be CNC machined.
`rear-mounts.rhai` builds both rear mounts as an editable rCAD document (`rear-mounts.json`, four named 6061 parts), with
`rear-mount-plates.step`, `rear-mount-hardware.step` and the pictures `rear-mount-revB.png` and `rear-mount-revB-bay.png` (bay from above).
The −Y mount mirrors the +Y one about y = 226.5. Positions below are for +Y.

- **Two 6 mm 6061 plates** with the same outline (44.5 × 82.5 mm, notched round the upright, R3 corners).
  - Lower plate z 429 to 435, every feature cut from the top face. Upper plate z 461.2 to 467.2, every feature cut from the underside. One setup each.
  - The bay between them is 26.2 mm (z 435.0 to 461.2), clear for both belt levels.
- **Drive shaft** Ø5 × 48 at (403.3, 433.0) in two 695 bearings (5 × 13 × 4), one in a 4 mm pocket in each plate with an Ø8 hole behind it.
  The 9 mm 20T pulley sits between them: on the upper belt at +Y, on the lower belt at −Y. The other belt passes the bare shaft with 1.9 mm to spare, so the pulley is held by its set screws and a spacer on its own side only.
- **Idlers:** two Ø5 pins through both plates, each carrying two F695 + 695 + F695 stacks (one per belt level), the same stack the joints use.
  - A at (385.5, 455.36) turns both belts off the side runs.
  - C at (391.0, 422.4): on the motor's level the belt back wraps it 201° and feeds the pulley for a 187° wrap (the old mount gave about 45°). On the other level it guides the crossing belt past the shaft.
  - Toothed Gates idlers don't fit here: two of them on one pin are 28 mm tall and the bay is 26.2 mm. So the belt teeth run on smooth bearings at A, as they do on small idlers today.
- **Motor** above on four Ø7 × 35 standoffs (M3 × 45 from counterbores in the bay roof), joined to the shaft by a 5 to 5 mm coupler (Ø19 × 25).
  Motor face at z 502.2, top of a 40 mm motor at z 542.2.
- **Fixing:** three M5 × 50 go down through upper plate, Ø8 × 26.2 standoff, lower plate and an Ø10 × 8 riser into T-nuts in the top slots of
  the rear 2020 (414.5, 400 and 414.5, 441) and the side 2020 (399.5, 466.5). A fourth standoff at (386, 402) threads into the lower plate.

Open in rev B:

- Tightest gaps: belt to the (414.5, 400) standoff 1.4 mm, motor screw counterbore to pin C 0.1 mm of plate between them.
- Nothing ties the mount to the upright sideways. The old part had two M5 into each face of the upright.
- At X max with Y near either end, the toolhead's belt clamp screws reach x 386, into the plate (x from 380). The old mount had the same overlap (it starts at x 378.7).
- The PIR back board's pockets were cut for the old mount and need re-cutting for the taller one.
- Not yet in `X-carriage.json` (another thread is editing that file).

## Front motor mounts (not modelled yet)

- A motor directly above the front pulley (centre y 457.04) reaches y 478.2 with a 42.3 mm NEMA 17. The side panel's inner face is at y 477.5, so it is 0.7 mm into the panel. It also needs x ≥ 17 to clear the front upright.
- The mount has to bolt to the upright faces, because the rail covers the top slot of the side 2020 and there is no cross extrusion at the front at this height.
- New front plates stop the gantry earlier than the model's X min of 22.

## Firmware

20T pulleys on 2 mm pitch keep `rotation_distance: 40`, so 9 mm belts alone need no Klipper change.
The config backup is in JonasMerrell/simplecore-config. Belt tension and input shaper need re-tuning after the swap.

## Files

- `section-lower-belt-z442.png`, `section-upper-belt-z454.png`: plan sections through each belt level (X up = rear, Y across). Black frame, blue gantry, red toolhead.
- `rear-motor-mount.png`: the existing +Y motor mount.
- `beltpath.py`, `beltpath.png`: the belt path.
- `../scripts/belt9_lib.py`, `belt9_sections.py`: the measuring scripts (need `pip install cadquery-ocp`; scratch paths inside).
