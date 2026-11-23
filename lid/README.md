# Top lid with over-centre gas springs and a seal

The top panel is now a lid hinged along the back on two printed corner hinges that turn on 623 ball bearings. Two gas springs pull it shut when it is closed and push it open past about 36°, and it stays up at 85° by itself. A hollow silicone seal runs round the top of the frame. The top PIR board is bonded under the lid, so it lifts out of the way with it.

Rev 3 (2026-11-22): heavier hinges moved to the lid's rear corners, each one printed in one piece with an arm that runs forward along the lid's side edge to the spring lever, so the spring force goes lever → arm → pin and not through the 3 mm lid. The springs and their brackets moved forward so that everything outside the side panel is in front of the filament tube, and the brackets clear the M5 button heads that hold the side panels.

![closed](renders/lid-closed-overview.png)
![open](renders/lid-open-rear.png)
![spring corner](renders/lid-closed-spring-corner.png)
![hinge](renders/lid-closed-hinge.png)

## How it works

| | |
|---|---|
| Hinges | Two printed hinges at the lid's rear corners (y 14 and 439), pin along Y at x 444, z 601.95 (just behind the lid's back edge). Each has a **frame block** on the rear-most top rail (x 454.5–474.5, 2× M5 into T-nuts) with two 10 mm ears, a **623 bearing (3 × 10 × 4)** pressed into each ear from the slot side with 4.5 mm of plastic round it, and a **corner arm** whose 12 mm tongue sits between the ears. An M3 × 25 screw with a locknut goes through both bearings and the tongue and clamps the inner races against the tongue, so the screw turns with the lid in the bearings. |
| Corner arms | One printed part per side, 127.5 × 66.5 × 11: a 9.25 mm pad over the lid's rear corner that carries the tongue, and a 24.5 mm wide strip along the lid's side edge forward to x 322. 6× M4 into the lid, all outside the seal line (three at x 426.5, three along the edge at x 340, 373, 402). The spring lever bolts to the strip's outer side with 2× M5 × 30 (nuts in slots in the strip). |
| Lid | 3 mm 6061, the same 459 × 508 footprint as the old top panel (x −25.5..433.5, y −27.5..480.5), front corners rounded R12. It sits on the seal, so it is now at z 595.2–598.2 (5 mm higher). |
| Insulation | The old top board (25.4 mm PIR) is bonded under the lid: x −3.5..402.5, y −1.5..454.5, z 569.8..595.2. It is 2 mm clear of the top extrusions all round. When the lid opens it swings up and forward, away from the rear rail. |
| Seal | Self-adhesive hollow silicone D-profile, about 10 wide × 8 high, on the top face of the four top extrusions (centred on each rail; centre-line rectangle 430 × 480, about 1.82 m). It is modelled compressed to 5 mm. A close catalogue profile is Parker TechSeal hollow-D D010 (12.4 × 7.9) with the PSA backing, ordered in silicone. |
| Gas springs | Two, one on each side, OUTSIDE the side panels (y −50 and 503), so they stay at room temperature and clear of everything in the chamber. Size: **250 mm extended (ball to ball), 80 mm stroke, Ø15 body, Ø6 rod, 80 N (18 lb)** each, Ø10 ball sockets on M6 ball studs. This is the common 10 inch cabinet lid strut; any 245–250 mm strut with at least 76 mm of stroke works. Jonas picked a 10 inch / 18 lb pair (2026-11-21); its kit has ball studs on screw plates, so either buy four M6 threaded Ø10 ball studs or the brackets get redrawn for the plates. |
| Lid spring levers | Machined 8 mm 6061 plates, x 322–358, hanging outside the side panels 5 mm off them (2.2 mm over the 2.75 mm button heads). Ball stud at (344, 536.95) when closed. |
| Frame brackets | Machined 13 mm 6061 blocks, 60 × 32 (x 121–181, z 558–590.2), on the side panels with 2× M5 × 20 through the panel into the top side rail's slot (x 131 and 171, z 580). A 12 × 3.2 mm channel runs along the back at z 574–586, so the bracket sits over the panel's M5 button heads wherever they are. Ball stud at (151, 577). If one of the panel's own screws lands on a bracket hole, use that position with a longer screw. |
| Handle | Printed arch at the middle of the front edge, 110 long, 22 high, with an 80 × 16 finger opening. 2× M4 from under the lid, fitted before the insulation is bonded on. |

### Over-centre numbers

From `scripts/lid/torque_plot.py` (lid + PIR + arms ≈ 2.6 kg, CG 239 mm in front of the pin, 80 N springs with F2/F1 = 1.3):

![torque](renders/torque.png)

- **Closed:** 22.1 N·m holding it shut (16.0 from the springs, 6.1 from the lid's weight). That is about 92 N on the seal (≈ 5 N per 100 mm), and you lift with about 47 N at the front edge to open it.
- **Springs' dead point:** 28°, where they are shortest (174.8 mm, 4.8 mm before they bottom out).
- **Past 36°** it opens by itself. **At 85°** the springs hold it open with 18.0 N·m and are fully extended (250 mm), so the springs themselves are the end stop. Closing works the other way round: push it down past 36° and it pulls itself shut.
- The torques scale with spring force: 45 N (10 lb) springs give 15.1 N·m shut / 9.8 N·m open, 60 N (13 lb) give 18.1 / 13.3.
- Spring length over the swing: 197.1 (closed) → 174.8 (28°) → 250 (85°), checked in the assembly (the mates solve the loop: no failed mates at 0°, 28° and 85°). Highest spring force 103 N per side.

`scripts/lid/search.py` is the search that picked the geometry: spring sizes, open angles and ball positions, keeping the ones that hold shut and open with the lid ball at least 27 mm in front of the filament tube hole and the frame ball beside the top side rail.

## Clearances

- Toolhead: the toolhead never moves in Z (the bed does). Its top (cable chain mount) is at z 537.0, the lid's insulation at 569.8: **32.8 mm**, 5 mm more than under the old board. The X gantry tops out at 468.9. The cable chain itself is not modelled; it has those 32.8 mm to arc in.
- Filament tube (right side): from the photos its hole is about 36 mm below the panel's top edge and 62 mm in front of its rear edge, about (371.5, 554), and the tube runs back and down along the rear edge. Everything on the outside of the panel is in front of it: the lever's rear edge is at x 358 when closed (11.5 mm from the tube) and moves forward and up as the lid opens; the spring is always in front of the lever. The tube stub is in the model as a reference part.
- Side panel screws: M5 button heads (2.75 high) along the top edge and down the rear edge. The levers pass 2.2 mm over them, the frame brackets have the channel, and nothing sits on the rear edge any more.
- Right side: the Trad Rack's highest point is z 397.8, 130 mm below the springs.
- Back: the hinge blocks sit on the rear-most top rail, outside the back panel. Nothing inside the chamber.
- Door: its top is at 590.2 and in front of x −28.8; the lid starts at x −25.5, 5 mm higher. No change.
- Lid swing (0–85°): the lid, corner arms and levers don't touch the hinge blocks, frame brackets or the tube at 0°, 42.5° or 85° (interference check).

## Model

- Part Studios **Top lid** (sketch-and-extrude features in world position, variables `lid_t`, `seal_h`, `lid_pir_t`) and **Lid gas springs** (spring body, rod and ball stud imported as STEP in local frames).
- Assemblies **Top lid** (moves: panel, PIR, handle, corner arms and pins, spring levers, lid ball studs) and **Lid frame hardware** (fixed: seal, hinge blocks with their bearings, frame brackets, frame ball studs, the filament tube reference).
- In **Printer**: both, plus each spring's body and rod. Mates: **Top lid hinge** (revolute, 0..85°; mate 24 in X-carriage.json, 22 in X-carriage-no-belts.json), each body on the lid's ball (revolute), each rod on the frame's ball (revolute), body and rod on one axis (cylindrical). The motion slider **Open top lid** opens it 0 → 85° and the springs follow.
- The old top panel (Enclosure) and the old top PIR board (PIR insulation) are hidden, not deleted.

## Interactive 3D page

`lid/web/top-lid-only.html` is rCAD's `export_web` page of the lid, hinges, springs and seal on their own (0.5 MB, needs internet for three.js). Drag the **Open top lid** slider or press Play. The page for the whole printer is 31 MB without the Trad Rack (120 MB with it), so it is not in the repository; build it with:

```
python3 scripts/lid/web_export.py X-carriage.json Printer lid_geom.json printer-with-top-lid.html "--hide=Trad Rack" && rcad run web_run.json
```

The page does not solve closed loops, so the gas springs would come apart as the lid opens. `web_export.py` works on a temporary copy: it suppresses the springs' sliding mates and makes the **Open top lid** slider drive the four ball joints with the angles the springs really take, so they stay in line. The single **Top lid hinge** slider further down moves the lid alone, without the springs. The documents themselves are unchanged.

## Printed parts

STLs in print orientation are in `lid/print/` (ASA or ABS; the hinges sit outside the chamber on top of the frame).

| Part | Qty | Orientation | Supports |
|---|---|---|---|
| `lid-hinge-frame-block.stl` (40 × 21.2 × 32.6) | 2 | On its side, pin axis upright, so the layers run along the ears | Only in the 12.6 mm slot between the ears |
| `lid-corner-arm-right.stl`, `lid-corner-arm-left.stl` (127.5 × 66.5 × 11) | 1 each | Top face down | None (the nut slots bridge 8.3 mm) |
| `lid-handle.stl` (110 × 22 × 14) | 1 | On its front face | None |

Hardware: 4× 623 bearing, 2× M3 × 25 socket screw + locknut, 4× M5 × 12 + T-nut (blocks), 12× M4 (corner arms), 4× M5 × 30 + nut (levers), 4× M5 × 20 + T-nut (frame brackets), 4× M6 ball stud, 2× M4 (handle). The bearing pockets are drawn at exactly 10.0 mm, so set your usual press-fit allowance in the slicer or ream them. The screw head and the nut sit in 6.8 mm bores in the ears and bear on the inner races only; hold the nut with needle-nose pliers.

## Drilling jigs

Printed jigs for the holes you drill yourself, in `lid/jigs/` (STLs lips-up, no supports; any filament; model `lid-drill-jigs.json`, built by `scripts/lid/mkjigs.py` and `jig_files.py`). Every guide hole is 3.4 mm for a 3.3 mm pilot drill; open the holes up afterwards (4.3 for M4, 5.5 for M5). Run the drill through the printed guides once before use.

![jigs](jigs/lid-drill-jigs.png)

| Jig | Qty | Registers on | Holes |
|---|---|---|---|
| `lid-jig-corner-right.stl`, `-left.stl` (121.5 × 71.5 × 10.8) | 1 each | Top of the lid, lips against the lid's rear edge and side edge | The corner arm's 6× M4: three 7 mm in front of the rear edge, three 4.5 mm in from the side edge |
| `lid-jig-handle.stl` (41.5 × 120 × 10.8) | 1 | Top of the lid, lip against the front edge; line the sight slot up with a centre line scribed 254 mm from either side edge | The handle's 2× M4, 95 mm apart, 24.5 mm behind the front edge |
| `lid-jig-side-panel-right.stl`, `-left.stl` (214.5 × 32.2 × 17) | 1 each | Outside of the side panel with the old top panel off: lips over the panel's top edge and front edge (door open) | The frame bracket's 2× M5 at 156.5 and 196.5 mm from the panel's front edge, 10.2 mm below its top edge (the top side rail's slot). A channel on the back clears the M5 button heads |

If one of the side panel's own screws already sits within a few millimetres of a bracket hole, tell me and I'll move the bracket holes onto it. Drill the side panel only through the 3 mm sheet: the rail's slot is right behind it.

## Rebuild

```
rcad script scripts/lid/hw.rhai                                  # gas spring + ball stud STEPs
python3 scripts/lid/mklid.py . && rcad run lid_run.json          # lid-doc.json
python3 scripts/lid/name_parts.py lid.out lid-doc.json && rcad run name_run.json   # names and colours (lid.out = the first run's output)
python3 scripts/lid/splice_lid.py lid-doc.json X-carriage.json   # -> X-carriage.json.new; the target must not have the lid yet
python3 scripts/lid/mklid.py . print && rcad run print_run.json  # lid-prints.stl
python3 scripts/lid/print_files.py lid-prints.stl lid/print      # the four STLs in print orientation
```

## Not checked / open

- The real top insulation: the CAD had a 25.4 mm PIR board in the top bay; if your sheet is a different thickness or sits under the rails, the plug changes.
- Seal compression force is an estimate for a soft hollow profile; the closed torque gives ≈ 92 N over 1.82 m. If the profile you buy is much stiffer, go up a spring force.
- The springs act as the 85° end stop. A rubber bump stop on the rear rail would take that load off them.
- No latch: the springs hold it shut.
- The printed hinges carry the springs' reaction (up to about 103 N per side). The ears are 10 mm thick with 4.5 mm of plastic round the bearing; printed on the side as above the load runs along the layers.
- The tube and screw positions are read from photos (± a few mm). The exact spacing of the top row of panel screws is not known, so the frame bracket holes are not lined up with them yet.
- Only the right side's tube is known; the left side is a mirror image.
- Mounting holes in the lid panel itself (corner arms, handle) are not cut in the model.
