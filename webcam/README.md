# Webcam

A chamber camera for the simplecore printer: what to buy, where it goes, and the streaming setup.

## Camera: 3DO Enclosure Camera V2.5

- USB UVC camera made for printer enclosures (Sony IMX258, 120° lens, manual focus by turning the lens). github.com/3DO-EU/Enclosure-Nozzle-Camera-V2
- **Heat:** rated −20 to 65 °C, and 3DO report 48 h in an 80 °C chamber. Ordinary desk webcams are built for room temperature and often fail in heated chambers.
- **Size:** the sensor is 9 × 9 mm and about 7 mm deep. It joins a 30 × 15 mm USB board through a flat cable. Order the **5 cm FPC**, which is what the mount is drawn for. The USB board has a 5-pin 1.0 mm connector for its USB cable.
- **Pi 3B load:** the camera compresses to MJPEG itself, so the Pi only forwards frames. Run it at 1280 × 720, 15 fps.
- Sold by 3do.dk (EU), fabreeko.com and kb-3d.com (US).

## Where it goes

Under the **front top rail, in the middle**, looking back and 38° down at the bed. The lens centre is at x −7, y 226.5, z 546.5 (front of the printer is −X).

- The nozzle stays at one height (z ≈ 402) and the bed drops, so a camera above the gantry always sees the current layer. Its centre line meets the nozzle plane at x ≈ 180, near the bed centre (191). The gantry beam and toolhead cross the view when they are at the front.
- It's the one spot that is clear of everything: the gantry sweeps z 395 to 469 across the whole front, the toolhead reaches z 537 (cable chain mount), and the 9 mm belt conversion puts motors in the front corners. The mount's lowest point is z 538.7, and it sits at x −27 to −0.5, in front of where the cable chain mount can reach (x ≥ 20 at the X minimum).
- **Not checked:** the toolhead's cable chain and the Trad Rack's filament tube are not in the model. If either arcs up through the front middle above z 538, the mount needs to move sideways along the rail (it can slide anywhere along the slot).
- Clearances: 1.7 mm to the closed door, 1.3 mm under the top insulation.

## The mount (Part Studio "Webcam", assembly "Webcam", in Printer)

Two printed parts, in ASA or another filament that takes chamber heat:

- **Webcam mount.** A 4 mm pad under the rail with two M5 holes (M5 × 8 button heads into T-nuts in the rail's bottom slot), a block with a 9.3 mm pocket for the sensor, and a plate with four bosses for the USB board (holes 26 × 11 mm, M2 self-tapping screws). The flat cable runs straight out of the side of the pocket to the board.
- **Lens bezel.** A 1.2 mm plate that holds the sensor in its pocket, with three M2 self-tapping screws. The lens sticks through, so it can still be turned to focus.
- The sensor, lens and USB board in the model are plain reference blocks with 3DO's published sizes.
- `step/Webcam mount + bezel.step` has the parts for slicing (it also holds the three reference blocks, so pick the mount and bezel). Print the mount with the tilted front face down.
- The USB cable leaves the board along the rail toward +Y (the hinge side).

`scripts/webcam/mkcam.py` builds the studio (tilt, position and sizes are at the top) and `splice_cam.py` adds it to the documents. Both documents have it. The change only adds a studio, an assembly and one Printer instance.

## Streaming

- **crowsnest with ustreamer** (`crowsnest.conf`): MJPEG pass-through. On a Pi 3B this costs very little CPU. camera-streamer with WebRTC uses less network but has to decode and re-encode every frame, which is the wrong trade on a Pi 3B that also runs Klipper.
- **Moonraker** (`moonraker-webcam.conf`): one `[webcam chamber]` section. Mainsail, including the fork, reads the camera from Moonraker, so no Mainsail change is needed.
- Timelapse (moonraker-timelapse) renders video on the Pi with ffmpeg. On a 3B that should only run after a print, never during one.
- The Pi 3B has one USB 2.0 bus for everything, including the Ethernet port and the printer's boards. 720p MJPEG is a few Mbit/s, which is fine. Don't run it at 4K.

Install steps (not done yet):

1. Plug the camera in, `ls /dev/v4l/by-id/` and put the path in `crowsnest.conf`.
2. If crowsnest isn't installed: `git clone https://github.com/mainsail-crew/crowsnest.git && cd crowsnest && sudo make install`.
3. Copy `crowsnest.conf` to `~/printer_data/config/`, add the Moonraker section, then restart crowsnest and Moonraker. Restarting Moonraker is safe only when no print is running.
