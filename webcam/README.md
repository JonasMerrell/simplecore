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

Under the **front top rail, in the middle**, looking back and 38° down at the bed. The lens axis crosses the board's front face at x −13, y 226.5, z 550 (front of the printer is −X).

- The nozzle stays at one height (z ≈ 402) and the bed drops, so a camera above the gantry always sees the current layer. The centre of the picture meets the nozzle plane at x ≈ 177, near the bed centre (191). The gantry beam and toolhead cross the view when they are at the front.
- The board's long side runs along the rail. Everything, lens included, stays between x −25.7 and x 9.8, and the lowest point is the lens rim at z 529.5. The toolhead in that zone tops out at z 521 (Sherpa), and the taller cable chain mount (z 537) never comes closer than x 20.
- Clearances: 3.1 mm to the closed door, about 2 mm under the top insulation (foam), 8 mm above the Sherpa when the toolhead is at the very front.
- **Not checked:** the toolhead's cable chain and the Trad Rack's filament tube are not in the model. If either passes through the front middle above z 530, slide the mount along the rail slot.

## The mount (Part Studio "Webcam", assembly "Webcam", in Printer)

Three small printed parts plus the lens holder, in ASA or another filament that takes chamber heat:

- **Webcam mount.** A pad under the rail with an M5 hole at each end (M5 × 8 button heads into T-nuts in the rail's bottom slot) and a shallow tray for the board. The board sits on a 2 mm ledge at each short end, with a 2 mm cavity behind it for the parts on the back and a window right across the back wall for the USB connector and cable.
- **Two clamp bars**, one over each short end of the board, each with two M2 self-tapping screws into the tray walls. They only touch the bare ends of the board, so the lens holder and lens are free.
- **M12 lens holder** (`m12_lens_housing_v2.stl`), printed as it is.
- Assembly: unscrew the stock lens holder from the back of the board, screw the printed holder on in its place, thread the lens in, lay the board in the tray, fit the two bars.
- The board, holder and lens in the model are plain reference blocks.
- `step/Webcam mount + bezel.step` has the parts for slicing (it also holds the reference blocks, so pick the mount and the two bars). Print the tray with its back face down.
- The pocket has 0.3 to 0.5 mm clearance. Print the tray first and test the board in it before fitting it to the printer.
- Which way up the picture comes out depends on the sensor's orientation on the board. If it is upside down, set `rotation: 180` in the Moonraker webcam section.

`scripts/webcam/mkcam.py` builds the studio (tilt, position and board sizes are at the top) and `splice_cam.py` adds it to the documents. Both documents have it. The change only adds a studio, an assembly and one Printer instance.

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

`webcam/predicted-view/` has renders of the model from the lens position at 1280 × 720. The bed is drawn dark with a 50 mm grid, yellow lines through the bed centre, and the orange block is a 50 mm square test part.

- `view-2.1mm-*.png`: with the 2.1 mm M12 lens, taken as 100° diagonal. Real wide lenses also bend straight lines toward the edges, which these renders don't show.
- `view-1..3-*.png`: with the stock 55° lens, for comparison.
- In each set: 1 is 44 mm into a print with the toolhead parked at the back, 2 is the same with the toolhead printing at the bed centre, 3 is the first layer.

Made by exporting the Printer assembly with `export_web`, pointing the page at a local copy of three.js (`npm pack three@0.147.0`), and rendering with `scripts/webcam/camera-view-shot.js` in headless Chromium.
