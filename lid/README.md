# Top lid with over-centre gas springs and a seal

The top panel is now a lid hinged along the back on two printed hinges that turn on 623 ball bearings. Two gas springs pull it shut when it is closed and push it open past about 42°, and it stays up at 90° by itself. A hollow silicone seal runs round the top of the frame. The top PIR board is bonded under the lid, so it lifts out of the way with it.

![closed](renders/lid-closed-overview.png)
![open](renders/lid-open-rear.png)
![hinge](renders/lid-closed-hinge.png)

## How it works

| | |
|---|---|
| Hinges | Two printed hinges at y 65 and 388, pin along Y at x 441, z 598.95 (just behind the lid's back edge). Each has a **frame block** on the rear-most top rail (x 454.5–474.5, one M5 into a T-nut) with two ears, a **623 bearing (3 × 10 × 4)** pressed into each ear from the slot side, and a **lid arm** whose tongue sits between the ears. An M3 × 20 screw with a locknut goes through both bearings and the tongue and clamps the inner races against the tongue, so the screw turns with the lid in the bearings. The arm's pad is held to the lid with 2× M4 at x 426.5, behind the seal (tap the 3 mm lid, or thin nuts underneath). |
| Lid | 3 mm 6061, the same 459 × 508 footprint as the old top panel (x −25.5..433.5, y −27.5..480.5), front corners rounded R12. It sits on the seal, so it is now at z 595.2–598.2 (5 mm higher). |
| Insulation | The old top board (25.4 mm PIR) is bonded under the lid: x −3.5..402.5, y −1.5..454.5, z 569.8..595.2. It is 2 mm clear of the top extrusions all round. When the lid opens it swings up and forward, away from the rear rail. At the front it moves at most 1 mm forward before it rises, so the 2 mm gap clears. |
| Seal | Self-adhesive hollow silicone D-profile, about 10 wide × 8 high, on the top face of the four top extrusions (centred on each rail; centre-line rectangle 430 × 480, about 1.82 m). It is modelled compressed to 5 mm. A close catalogue profile is Parker TechSeal hollow-D D010 (12.4 × 7.9) with the PSA backing, ordered in silicone. |
| Gas springs | Two, one on each side, OUTSIDE the side panels (y −45 and 498), so they stay at room temperature and clear of everything in the chamber: the cable chain at the back, the webcam on the right wall. Size: 150 mm extended (ball to ball), 50 mm stroke (100 compressed), Ø15 body, Ø6 rod, **100 N** each, Ø10 ball sockets on M6 ball studs. For example Bansbach easylift (made to length and force). Ordering one with a bleed valve at 120 N lets you tune it down. |
| Handle | Printed arch at the middle of the front edge, 110 long, 22 high, with an 80 × 16 finger opening. 2× M4 from under the lid, fitted before the insulation is bonded on. |
| Brackets | Machined 6061, flat plates with rounded ends. **Frame bracket** (8 mm, x 261.5–303.5, z 512.5–590.2) sits on the side panel with 2× M5 through the panel into the top side rail's slot at z 580; ball stud at (282.5, 523.45). **Lid bracket** (6 mm plate 2 mm off the panel + a 6 mm flange on the lid top with 2× M4); ball stud at (403.5, 538.95) when closed. |

### Over-centre numbers

From `scripts/lid/torque_plot.py` (lid + PIR + brackets ≈ 2.6 kg, CG 236 mm in front of the pin, 100 N springs with F2/F1 = 1.3):

![torque](renders/torque.png)

- **Closed:** 18.7 N·m holding it shut (12.7 from the springs, 6.0 from the lid's weight). That is about 80 N on the seal (≈ 4.4 N per 100 mm), and you lift with about 40 N at the front edge to open it.
- **Springs' dead point:** 32°, where they are shortest (104.8 mm, 4.8 mm before they bottom out).
- **Past 42°** it opens by itself. **At 90°** the springs hold it open with 13.8 N·m and are fully extended (150 mm), so the springs themselves are the end stop. Closing works the other way round: push it down past 42° and it pulls itself shut.
- The torques scale with spring force: 80 N springs give 16.2 N·m shut / 11.0 N·m open, 120 N give 21.3 / 16.6.
- Spring length over the swing: 122.0 (closed) → 104.8 (32°) → 150 (90°), checked in the assembly (the mates solve the loop: no failed mates at 0°, 32° and 90°).

`scripts/lid/search.py` is the search that picked the geometry: ball positions on a grid, spring sizes 150/50 to 305/130, keeping the ones that hold shut and open with the ball points outside the panels and above the Trad Rack.

## Clearances

- Toolhead: the toolhead never moves in Z (the bed does). Its top (cable chain mount) is at z 537.0, the lid's insulation at 569.8: **32.8 mm**, 5 mm more than under the old board. The X gantry tops out at 468.9. The cable chain itself is not modelled; it has those 32.8 mm to arc in.
- Right side: the Trad Rack's highest point is z 397.8, 115 mm below the frame bracket. Nothing else is on the outside of either side panel above z 500.
- Back: the hinge blocks sit on the rear-most top rail, outside the back panel. Nothing inside the chamber.
- Door: its top is at 590.2 and in front of x −28.8; the lid starts at x −25.5, 5 mm higher. No change.
- Lid swing (0–90°): the lid bracket comes no closer than 50 mm to the frame bracket; the lid and its arms don't touch the hinge blocks at 0°, 45° or 90° (interference check). At 90° the lid's back edge stands 0.5 mm above the hinge ears, so 90° is the limit.

## Model

- Part Studios **Top lid** (sketch-and-extrude features in world position, variables `lid_t`, `seal_h`, `lid_pir_t`) and **Lid gas springs** (spring body, rod and ball stud imported as STEP in local frames).
- Assemblies **Top lid** (moves: panel, PIR, handle, hinge arms and pins, lid brackets, lid ball studs) and **Lid frame hardware** (fixed: seal, hinge blocks with their bearings, frame brackets, frame ball studs).
- In **Printer**: both, plus each spring's body and rod. Mates: **Top lid hinge** (revolute, 0..90°; mate 24 in X-carriage.json, 22 in X-carriage-no-belts.json), each body on the lid's ball (revolute), each rod on the frame's ball (revolute), body and rod on one axis (cylindrical). The motion slider **Open top lid** opens it 0 → 90° and the springs follow.
- The old top panel (Enclosure) and the old top PIR board (PIR insulation) are hidden, not deleted.

## Printed parts

STLs in print orientation are in `lid/print/` (ASA or ABS; the hinges sit outside the chamber on top of the frame).

| Part | Qty | Orientation | Supports |
|---|---|---|---|
| `lid-hinge-frame-block.stl` (40.5 × 15.8 × 24) | 2 | On its side, pin axis upright, so the layers run along the ears | Only in the 8 mm slot between the ears |
| `lid-hinge-lid-arm.stl` (25.5 × 30 × 9) | 2 | Top face down | None |
| `lid-handle.stl` (110 × 22 × 14) | 1 | On its front face | None |

Hardware: 4× 623 bearing, 2× M3 × 20 socket screw + locknut, 2× M5 × 10 + T-nut (blocks), 4× M4 (arms), 2× M4 (handle). The bearing pockets are drawn at exactly 10.0 mm, so set your usual press-fit allowance in the slicer or ream them. The screw head and the nut sit in 6.8 mm bores in the ears and bear on the inner races only; hold the nut with needle-nose pliers.

## Rebuild

```
rcad script scripts/lid/hw.rhai                                  # gas spring + ball stud STEPs
python3 scripts/lid/mklid.py . && rcad run lid_run.json          # lid-doc.json
python3 scripts/lid/name_parts.py lid.out lid-doc.json && rcad run name_run.json   # names and colours (lid.out = the first run's output)
python3 scripts/lid/splice_lid.py lid-doc.json X-carriage.json   # -> X-carriage.json.new; the target must not have the lid yet
python3 scripts/lid/mklid.py . print && rcad run print_run.json  # lid-prints.stl
python3 scripts/lid/print_files.py lid-prints.stl lid/print      # the three STLs in print orientation
```

## Not checked / open

- The real top insulation: the CAD had a 25.4 mm PIR board in the top bay; if your sheet is a different thickness or sits under the rails, the plug changes.
- Seal compression force is an estimate for a soft hollow profile; the closed torque gives ≈ 80 N over 1.82 m. If the profile you buy is much stiffer, go up a spring force.
- The springs act as the 90° end stop. A rubber bump stop on the rear rail would take that load off them.
- No latch: the springs hold it shut.
- The printed hinges carry the springs' reaction (up to about 130 N per side). The ears are 8 mm thick with 2 mm of plastic round the bearing; printed on the side as above the load runs along the layers.
- Mounting holes in the lid panel itself (hinge arms, handle, lid brackets) are not cut in the model.
