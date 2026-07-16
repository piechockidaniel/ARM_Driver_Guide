# ESP32-CAM Setup

This project can use an `ESP32-CAM` board as a remote image source through HTTP snapshot polling.

The implementation expects the board to expose a JPEG capture endpoint on:

```text
http://<board-ip>/capture
```

That matches the standard `CameraWebServer` firmware pattern commonly used with `ESP32-CAM` boards and the `ESP32-CAM-MB` USB base.

## Hardware fit

Confirmed target class for this repo:

- `ESP32-CAM` style camera board
- `ESP32-CAM-MB` USB programming base
- Wi-Fi image transport only
- image inference still runs on the host machine in Python

## Flash outline

1. Insert the camera board into the `ESP32-CAM-MB` base.
2. Connect the base over USB.
3. In Arduino IDE, install `esp32` board support from Espressif if it is not already present.
4. Open the `CameraWebServer` example.
5. Select an `ESP32 Wrover Module`-compatible board profile if your exact board name is not listed.
6. Set the camera model in the sketch to the profile that matches your module.
7. Enter Wi-Fi SSID and password in the sketch.
8. Flash the firmware.
9. Open the serial monitor and note the assigned IP address.

## Run with ARM-Guard

CLI:

```bash
.venv\Scripts\python.exe main.py live --esp32-url http://<board-ip> --max-frames 120
```

GUI:

1. Start the dashboard.
2. Enter `http://<board-ip>` in the `ESP32 URL` field.
3. Click `Connect ESP32-CAM`.

## Expected behavior

- If the board returns a malformed or unreadable JPEG frame, the pipeline reports `camera_unavailable` for that frame.
- If the board is reachable and the frame is valid but no face is found, the detector stays in the safe no-detection path without storing raw frames.
- If the board is unreachable, the session fails safely and does not store raw frames.
- All face landmarks and scoring remain on the host machine; the ESP32 only supplies images.
