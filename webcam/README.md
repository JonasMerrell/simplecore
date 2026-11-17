# Webcam

A chamber camera for the simplecore printer: the camera, where it goes, the printed mount and the streaming setup.

## Camera: Logitech C270 bare board with an M12 wide-angle lens

Jonas chose a C270 (2026-11-16). The case comes off, the stock lens holder is swapped for a printed M12 holder, and the mount holds the bare board. Files from Jonas (third-party models, kept in the project files under `x-carriage/webcam/parts/`, not in this repository):

- `C270 board (from Jonas).step`: a model of the board. 58 × 21 × 0.8 mm, lens axis 12.9 mm from one short end, on the centre line. Lens holder screws 16.5 mm apart, either side of the lens. Two 2 mm corner holes. USB connector on the back near the far end, 3 mm tall.
- `m12_lens_housing_v2.stl`: the printed M12 lens holder. Footprint 14.5 mm along the board × 21.2 mm across, 12 mm tall, M12 bore. It replaces the stock holder and uses the stock holder's two screws, from the back of the board.
- His earlier scan of the board ("Logitech C270 Chip v2.0.stl") agrees with the STEP within 1 mm. The tray pocket takes either.

**Lens (ordered 2026-11-16):** Richer-R 2.1 mm M12 "150°" lens for 1/3 and 1/4 inch chips.

- On the C270's small sensor I estimate about 95 to 110° diagonal (the stock lens is 55°). The predicted views below use 100°.
- Its length and front flange in the model (17 mm barrel, 18 mm flange, 22 mm overall) are estimates from the listing photo.
- Not confirmed: whether it has an IR-cut filter. If it has none and the C270's filter was in the stock holder, colours will look washed out and pinkish.
- Focus by screwing the lens in or out of the holder, then lock it (a dab of paint or a wrap of PTFE tape on the thread).

Other things to expect:

- **Heat.** The board has no published heat rating. It should be fine with the chamber heater off. At 60 °C and up it may misbehave, and the top of the chamber is the hottest spot.
- **Pi 3B load.** The C270 sends MJPEG itself at 1280 × 720, so the Pi only forwards frames.

## Where it goes

On the **right wall, high up**, stuck to the inner face of the right upper insulation board with VHB tape, looking across the bed and 45° down. Jonas chose this on 2026-11-17: at the back the camera was in the way of the toolhead's cable chain, and before that it was drawn under the front rail. Both earlier versions are in the history.

- Right is the −Y side, the side the Trad Rack hangs on outside. The lens axis crosses the board's front face at x 150, y 15.5, z 548 (front of the printer is −X, so the lens is 41 mm in front of the bed centre line). The board's long side runs front to back.
- The mount covers x 123.9 to 207.9 and z 532 to 561.6, and stands 24.7 mm off the wall. The lens rim reaches 36.4 mm off the wall (y 37.3) and is the lowest point at z 526.2. The top of the mount is 3.2 mm under the top insulation board.
- Clearance: with the toolhead as far right as it goes (Y slider 81), everything on it above the gantry stays 54.5 mm or more off the wall, so 18 mm clear of the lens rim. The extruder tops out at z 521 and the cable chain mount (z 537) stays 60 mm off the wall.
- The nozzle stays at one height (z ≈ 402) and the bed drops, so the camera always sees the current layer. The centre of the picture meets the nozzle plane 162 mm from the wall, 65 mm short of the bed centre, and the picture reaches from the bed's right edge to past its left edge.
- **What the view is like.** The door is on the left of the picture and the gantry beam on the right, so the camera sees the nozzle side of the toolhead. When the toolhead is right under the camera it fills the picture (`wall-4`).
- Because it is taped, it can go anywhere along the wall. Further forward shows more of the toolhead's front, further back more of the beam.
- **Top insulation.** The model does have a 25.4 mm insulation board under the top panel (its underside is at z 564.8). If the real sheet is thicker or hangs lower, the mount needs to sit lower by the same amount. There is 60 mm of board below it.
- **Not checked:** wires or tubes along the right wall are not in the model.

## The mount (Part Studio "Webcam", assembly "Webcam", in Printer)

Three small printed parts plus the lens holder, in ABS or ASA:

- **Webcam wall mount.** A flat pad, 84 × 29.6 × 3 mm, that takes the VHB tape, with a shallow tray for the board held 45° off it. The tray's lower edge grows out of the pad and a web ties its top edge to the pad. The triangle left open behind the tray is the cable channel, open at both ends. The board sits on a 2 mm ledge at each short end, with a 2 mm cavity behind it for the parts on the back and a window right across the back wall for the USB connector and cable.
- **Two clamp bars**, one over each short end of the board, each with two M2 self-tapping screws into the tray walls. They only touch the bare ends of the board, so the lens holder and lens are free. They are the same two bars as on the earlier mounts, so the ones printed on 2026-11-16 still fit.
- **M12 lens holder** (`m12_lens_housing_v2.stl`), printed as it is.
- Assembly: unscrew the stock lens holder from the back of the board, screw the printed holder on in its place, thread the lens in, lay the board in the tray with the lens at the front end, fit the two bars, lead the cable out of the channel. Clean the foil face of the insulation, then tape the pad on with the tray's open side facing down and into the chamber.
- VHB: cover most of the pad (about 25 cm²). The whole camera weighs about 30 g. The tape holds on the insulation's foil facing, so it is only as strong as that facing is bonded to the foam.
- The board, holder and lens in the model are plain reference blocks.
- `webcam/print/` has the three printed parts as STL files, already turned the way they print (`webcam-wall-mount.stl`, `webcam-clamp-bar-lens-end.stl`, `webcam-clamp-bar-cable-end.stl`). The mount prints with the pad flat on the bed and needs no supports: nothing overhangs more than 45°. The clamp bars print flat.
- `step/Webcam mount + bezel.step` has the same parts as modelled (it also holds the reference blocks).
- The pocket has 0.3 to 0.5 mm clearance, the same pocket as the mount printed on 2026-11-16, so that print is a valid test fit for the board.
- Which way up the picture comes out depends on the sensor's orientation on the board. If it is upside down, set `rotation: 180` in the Moonraker webcam section.

`scripts/webcam/mkwall.py` builds the studio (tilt, position and board sizes are at the top) and `splice_cam.py` adds it to the documents. Both documents have it. The change only adds a studio, an assembly and one Printer instance. The insulation opening made for the rear position is gone again.

## Streaming

- **crowsnest with ustreamer** (`crowsnest.conf`): MJPEG pass-through. On a Pi 3B this costs very little CPU. camera-streamer with WebRTC uses less network but has to decode and re-encode every frame, which is the wrong trade on a Pi 3B that also runs Klipper.
- **Moonraker** (`moonraker-webcam.conf`): one `[webcam chamber]` section. Mainsail, including the fork, reads the camera from Moonraker, so no Mainsail change is needed.
- Timelapse (moonraker-timelapse) renders video on the Pi with ffmpeg. On a 3B that should only run after a print, never during one.
- The Pi 3B has one USB 2.0 bus for everything, including the Ethernet port and the printer's boards. 720p MJPEG is a few Mbit/s, which is fine.

Install steps (not done yet):

1. Plug the camera in, `ls /dev/v4l/by-id/` and put the path in `crowsnest.conf`.
2. If crowsnest isn't installed: `git clone https://github.com/mainsail-crew/crowsnest.git && cd crowsnest && sudo make install`.
3. Copy `crowsnest.conf` to `~/printer_data/config/`, add the Moonraker section, then restart crowsnest and Moonraker. Restarting Moonraker is safe only when no print is running.

## First proposal (not used)

The first proposal was a 3DO Enclosure Camera V2.5: 120° lens, rated to 65 °C, 9 × 9 mm sensor. Its mount is in the history (commit "Webcam: 3DO enclosure camera on the front top rail").

## Predicted view

`webcam/predicted-view/` has renders of the model from the lens position on the right wall, 1280 × 720, with the 2.1 mm M12 lens taken as 100° diagonal. Real wide lenses also bend straight lines toward the edges, which these renders don't show. The door and the Trad Rack are hidden, so the dark area on the left is where the door is. The bed is drawn dark with a 50 mm grid, yellow lines through the bed centre, and the orange block is a 50 mm square test part.

- `wall-1-toolhead-parked-back-left.png`: 44 mm into a print, toolhead parked at the back left.
- `wall-2-printing-centre.png`: the same, toolhead printing at the bed centre.
- `wall-3-first-layer.png`: first layer, toolhead toward the back left.
- `wall-4-toolhead-under-camera.png`: toolhead at the far right in front of the camera, the worst case.

Made by exporting the Printer assembly with `export_web`, pointing the page at a local copy of three.js (`npm pack three@0.147.0`), and rendering with `scripts/webcam/camera-view-shot.js` in headless Chromium. `renders/webcam-wall.png` and `webcam-wall-close.png` come from the same page with the camera inside the chamber.
