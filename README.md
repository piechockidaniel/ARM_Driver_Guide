# ARM-Guard

ARM-Guard is a privacy-first drowsiness-detection prototype targeted at Arm64 edge hardware. The project is aligned with `docs/action plan/` and anchored to the device bundle in `docs/device/`: **Orange Pi 5 Plus / Rockchip RK3588**.

The repository now covers two baseline modes:

- simulated pipeline for repeatable scoring, calibration, benchmarking, and privacy tests
- live baseline detector using `OpenCV + MediaPipe FaceMesh` with a `Tkinter` GUI for webcam, video-file, or `ESP32-CAM` snapshot input

## Python requirement

Use **Python 3.11** for the live CV stack. The project declares `>=3.11,<3.13` because `MediaPipe` is not part of the validated path on the current global Python 3.13 interpreter in this workspace.

On Windows, the expected command path is:

```bash
.venv\Scripts\python.exe main.py gui
```

## Target device

- Board: Orange Pi 5 Plus
- SoC: Rockchip RK3588
- CPU: 4x Cortex-A76 + 4x Cortex-A55
- GPU: Mali-G610
- NPU: up to 6 TOPS
- RAM in provided spec: 16GB LPDDR4/4x
- Notable I/O: MIPI CSI camera, dual 2.5GbE, USB 3.0, M.2 NVMe, Wi-Fi 6 module support

## Run

```bash
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe main.py gui
.venv\Scripts\python.exe main.py live --camera-index 0 --max-frames 120
.venv\Scripts\python.exe main.py live --video path\to\video.mp4 --max-frames 300
.venv\Scripts\python.exe main.py live --esp32-url http://192.168.4.1 --max-frames 120
.venv\Scripts\python.exe main.py demo
.venv\Scripts\python.exe main.py benchmark --iterations 100
```

For `ESP32-CAM`, this build expects the board to expose single JPEG snapshots on `/capture`, which matches the standard `CameraWebServer` firmware flow.
Setup notes for this path are in [docs/esp32-cam-setup.md](/C:/Users/user/source/repos/ARM_Driver_Guide/docs/esp32-cam-setup.md).

## Repository layout

```text
assets/                 Supporting diagrams and future demo assets
benchmarks/             Repeatable benchmark entrypoints
demo/                   Local profiles, logs, and simulator artifacts
docs/                   Source plan, device references, architecture notes
src/arm_guard/
  arm/                  Arm-specific acceleration hooks
  device/               Orange Pi 5 Plus spec and emulator
  domain/               Shared dataclasses and enums
  events/               Anonymized event schema and JSONL logger
  gui.py                Tkinter dashboard
  integrations/         Simulated context and frame providers
  live/                 OpenCV capture and MediaPipe FaceMesh baseline
  pipeline/             EAR, scoring, and orchestration
  privacy/              Consent and privacy controls
  profile/              Adaptive profile calibration and persistence
  safety/               Alerts and reliability monitoring
tests/                  Smoke and behavior tests
```

## What phase 2 now covers

- webcam input
- video-file input
- `ESP32-CAM` HTTP snapshot input
- face and eye landmark detection through MediaPipe FaceMesh
- EAR computation from landmarks
- long-blink and microsleep-like event handling
- live score, alert level, FPS, latency, and status output
- anonymized event logging during live sessions
