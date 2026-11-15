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

## Open design choices (asked in the thread)

1. How the lower-belt motor pulley gets its second support: long-shaft motor, moving the motor, or a separate supported shaft.
2. Where the two front motors go and which way their shafts point.
3. Idler hardware in the motor mounts (same Gates 9 mm 20T idlers and F695 stacks on Ø5 pins as the joints, or something else).

## Firmware

20T pulleys on 2 mm pitch keep `rotation_distance: 40`, so 9 mm belts alone need no Klipper change.
The config backup is in JonasMerrell/simplecore-config. Belt tension and input shaper need re-tuning after the swap.

## Files

- `section-lower-belt-z442.png`, `section-upper-belt-z454.png`: plan sections through each belt level (X up = rear, Y across). Black frame, blue gantry, red toolhead.
- `rear-motor-mount.png`: the existing +Y motor mount.
- `../scripts/belt9_lib.py`, `belt9_sections.py`: the measuring scripts (need `pip install cadquery-ocp`; scratch paths inside).
