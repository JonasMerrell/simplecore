# Webcam

A chamber camera for the simplecore printer: the camera, where it goes, the printed mount and the streaming setup.

## Camera: Logitech C270, bare board

Jonas chose a C270 (2026-11-16) and sent a 3D scan of its board with the case removed ("Logitech C270 Chip v2.0.stl"). The mount holds the bare board.

Measured from the scan:

- Board 58.0 × 21.2 × 1.0 mm, with chamfered ends.
- Lens centre 13.4 mm from one short end and 10.4 mm from one long edge. The lens stands 7.7 mm above the board. Its focus ring is about 11.8 mm across.
- The lens holder base covers the first 19 mm of the board and is 2.7 mm tall. Two posts, 16.4 mm apart, flank the lens.
- Parts on the back are about 1 mm tall. The USB connector on the back, at the far end from the lens, is 3.2 mm tall and about 7 × 8.6 mm.
- The microphone on the front stands 5.8 mm tall, 16 mm along from the lens.

What to expect from this camera:

- **Narrow view.** The lens is 55° diagonal. From the mount it sees roughly the middle 215 × 195 mm of the 313 × 267 mm bed.
- **Heat.** It has no published heat rating. It should be fine with the chamber heater off. At 60 °C and up it may lose focus or fail, and the top of the chamber is the hottest spot.
- **Focus.** The lens is set at the factory for about arm's length and further. The bed centre is about 240 mm away. If the picture is soft, turn the toothed ring (it may have a dot of glue).
- **Pi 3B load.** The C270 sends MJPEG itself at 1280 × 720, so the Pi only forwards frames.

## Where it goes

Under the **front top rail, in the middle**, looking back and 38° down at the bed. The lens axis leaves the mount at x −9, y 226.5, z 548 (front of the printer is −X).

- The nozzle stays at one height (z ≈ 402) and the bed drops, so a camera above the gantry always sees the current layer. The centre of the picture meets the nozzle plane at x ≈ 178, near the bed centre (191). The gantry beam and toolhead cross the view when they are at the front.
- The board's long side runs along the rail, so the whole mount is only 34 mm tall. It spans x −25.5 to −0.1 and its lowest point is z 536.6. The toolhead in that zone tops out at z 521 (Sherpa), and the taller cable chain mount (z 537) never comes closer than x 20.
- Clearances: 3.3 mm to the closed door, about 1 mm under the top insulation (foam).
- **Not checked:** the toolhead's cable chain and the Trad Rack's filament tube are not in the model. If either passes through the front middle above z 537, slide the mount along the rail slot.

## The mount (Part Studio "Webcam", assembly "Webcam", in Printer)

Two printed parts, in ASA or another filament that takes chamber heat:

- **Webcam mount.** A pad under the rail with an M5 hole at each end (M5 × 8 button heads into T-nuts in the rail's bottom slot) and a tray for the board. The board sits on a ledge at each short end, with a 2 mm cavity behind it for the parts on the back and a window in the back wall for the USB connector and cable. A lip holds the cable end of the board.
- **Lens bezel.** A 1.4 mm plate over the lens end, held by four M2 self-tapping screws. It presses on the lens holder base. The lens and its two posts stick through, so the focus ring can still be turned.
- To fit the board: slide the cable end under the lip, lay the board down, screw on the bezel.
- The board and lens in the model are plain reference blocks sized from the scan.
- `step/Webcam mount + bezel.step` has the parts for slicing (it also holds the two reference blocks, so pick the mount and bezel). Print the tray with its back face down.
- The pocket has 0.3 mm clearance all round. The scan is the only size reference, so print the tray first and test the board in it before fitting it to the printer.
- Which way up the picture comes out depends on the sensor's orientation on the board, which the scan doesn't show. If it is upside down, set `rotation: 180` in the Moonraker webcam section.

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
