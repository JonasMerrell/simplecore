# Webcam

A chamber camera for the simplecore printer: the camera, where it goes, the printed mount and the streaming setup.

## Camera: Logitech C270 bare board with an M12 wide-angle lens

Jonas chose a C270 (2026-11-16). The case comes off, the stock lens holder is swapped for a printed M12 holder, and the mount holds the bare board. Files from Jonas (third-party models, kept in the project files under `x-carriage/webcam/parts/`, not in this repository):

- `C270 board (from Jonas).step`: a model of the board. 58 × 21 × 0.8 mm, lens axis 12.9 mm from one short end, on the centre line. Lens holder screws 16.5 mm apart, either side of the lens. Two 2 mm corner holes. USB connector on the back near the far end, 3 mm tall.
- `m12_lens_housing_v2.stl`: the printed M12 lens holder. Footprint 14.5 mm along the board × 21.2 mm across, 12 mm tall, M12 bore. It replaces the stock holder and uses the stock holder's two screws, from the back of the board.
- His earlier scan of the board ("Logitech C270 Chip v2.0.stl") agrees with the STEP within 1 mm.

**Lens (ordered 2026-11-16):** Richer-R 2.1 mm M12 "150°" lens for 1/3 and 1/4 inch chips.

- On the C270's small sensor I estimate about 95 to 110° diagonal (the stock lens is 55°). The predicted views below use 100°.
- Its length and front flange in the model (17 mm barrel, 18 mm flange, 22 mm overall) are estimates from the listing photo.
- Not confirmed: whether it has an IR-cut filter. If it has none and the C270's filter was in the stock holder, colours will look washed out and pinkish.
- Focus by screwing the lens in or out of the holder, then lock it (a dab of paint or a wrap of PTFE tape on the thread).

Other things to expect:

- **Heat.** The board has no published heat rating. It should be fine with the chamber heater off. At 60 °C and up it may misbehave, and the top of the chamber is the hottest spot.
- **Pi 3B load.** The C270 sends MJPEG itself at 1280 × 720, so the Pi only forwards frames.

## Where it goes

On the **right wall, high up**, taped straight onto the inner face of the aluminium side panel with VHB, looking across the bed and 45° down. Jonas chose the wall on 2026-11-17: at the back the camera was in the way of the toolhead's cable chain, and before that it was drawn under the front rail. The earlier versions are in the history.

- Right is the −Y side, the side the Trad Rack hangs on outside. Jonas's printer has **no upper side insulation boards** (the band above the gantry), so the panel is bare there. The two upper side boards are hidden in the model's "PIR insulation" assembly. The back upper board is left as it was.
- The lens is on the bed's centre line (x 191.2). The lens axis crosses the board at y −9.9, z 548. The board's long side runs front to back.
- The mount covers x 156.2 to 226.2 and z 516.6 to 564.3, and stands 34 mm off the panel. The lens rim reaches 36.4 mm off the panel (y 11.9). The pad's top is 5.9 mm under the top side rail.
- Clearance: with the toolhead as far right as it goes (Y slider 81), everything on it above the gantry stays 80 mm or more off the panel, so 43 mm clear of the lens rim. The gantry end passes 50 mm below the pad.
- **Tilt.** At 45° the whole bed is in the picture at nozzle height with a little room at the far edge (`wall-3`). Jonas asked for a steeper tilt to see more of the bed. At 50° and 55° the far (left) edge of the bed drops out of the top of the picture while empty space opens under the near edge, so the gain came from setting the camera 25 mm further back on the bare panel and centring it on the bed. `TH` at the top of `mkmount.py` changes the tilt.
- **What the view is like.** The door is on the left of the picture and the gantry beam crosses it, so the camera sees the nozzle side of the toolhead when it prints in front of the beam. When the toolhead is right under the camera it fills the picture (`wall-4`).
- Because it is taped, it can go anywhere along the wall.
- **Not checked:** wires or tubes along the right wall are not in the model.

## The mount (Part Studio "Webcam", assembly "Webcam", in Printer)

**One printed part**, in ABS or ASA: the tape pad and Jonas's M12 lens holder in one piece (Jonas asked for this on 2026-11-17). The tray and the two clamp bars of the earlier versions are gone.

- A flat pad, 70 × 48 × 3 mm, takes the VHB tape. A rib below the lens holder and a cheek and strut above it tie the holder to the pad at 45°. The rib and the cheek sit just outside the board's two long edges and locate the board between them.
- The board screws to the back of the lens holder with the stock lens holder's two screws, as in the original camera. Nothing else holds it.
- Two 5 mm screwdriver holes run straight back from the two screws: one through the strut, one through the pad. Fit the board before taping the mount to the wall.
- The space between the board and the pad is open at both ends for the USB cable.
- Assembly: unscrew the stock lens holder from the back of the board, lay the board on the back of the printed holder between the rib and the cheek, drive the two screws through the access holes, thread the lens in and focus it. Clean the panel, then tape the pad on with the lens pointing down and into the chamber.
- VHB: cover most of the pad (about 30 cm²). The whole camera weighs about 30 g, and aluminium is a good surface for the tape.
- **The lens holder in the model is simplified** (flange, tower and a plain bore). The printed part uses the real holder: `scripts/webcam/fuse_holder.py` puts `m12_lens_housing_v2.stl` into the mount body and turns it for printing. The result, `webcam-mount-with-lens-holder.stl`, is in the project files under `x-carriage/webcam/print/` and not in this repository, because it contains the holder's model.
- The holder's STL is not a closed mesh (a few cracks and T-junctions), so the two shells are written into one STL overlapping each other instead of being fused by a mesh boolean. Slicers fuse overlapping shells of one object. Check the sliced preview once: the lens bore, the square sensor pocket and the two screw slots must be open.
- Printing: the holder's front face lies on the bed, so the M12 thread prints upright, as it does when the holder is printed on its own. 70 × 48 × 34 mm, no supports. The pad leans at 45°, nothing overhangs more than that, and the only bridges are four 3 mm corners under the holder's flange.
- The board and lens in the model are plain reference blocks. `step/Webcam mount + bezel.step` has the model's parts.
- Which way up the picture comes out depends on the sensor's orientation on the board. If it is upside down, set `rotation: 180` in the Moonraker webcam section.

`scripts/webcam/mkmount.py` builds the studio (tilt, position and holder sizes are at the top), `splice_cam.py` adds it to the documents and `hide_upper_pir.py` hides the two insulation boards. Both documents have it.

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
- `wall-3-first-layer.png`: first layer, toolhead parked. The whole bed is in the picture.
- `wall-4-toolhead-under-camera.png`: toolhead at the far right in front of the camera, the worst case.

Made by exporting the Printer assembly with `export_web`, pointing the page at a local copy of three.js (`npm pack three@0.147.0`), and rendering with `scripts/webcam/camera-view-shot.js` in headless Chromium. The pictures in `renders/` come from the same page with the camera inside the chamber.
