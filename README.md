# ARM-Guard

ARM-Guard is a privacy-first drowsiness-detection prototype targeted at Arm64 edge hardware. The current implementation is aligned with the phased action plan in `docs/action plan/` and is now anchored to the device bundle in `docs/device/`: **Orange Pi 5 Plus / Rockchip RK3588**.

This iteration implements a concrete baseline around:

- simulated input frames and vehicle context
- EAR-based drowsiness scoring
- anonymized event logging
- `privacy_mode` behavior
- adaptive baseline calibration
- progressive alert levels
- system-health and degraded-mode reporting
- benchmark and device-emulator commands

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
python main.py demo
python main.py calibrate
python main.py benchmark --iterations 100
python main.py inspect-device
python main.py inspect-config
```

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
  integrations/         Simulated context and frame providers
  pipeline/             EAR, scoring, and orchestration
  privacy/              Consent and privacy controls
  profile/              Adaptive profile calibration and persistence
  safety/               Alerts and reliability monitoring
tests/                  Smoke and behavior tests
```

## Current scope

The project is still using simulated frames instead of a live webcam or video pipeline. That is intentional for this iteration: it lets the repository implement privacy, scoring, benchmarking, calibration, and device-targeting behavior without prematurely hard-coding a computer-vision dependency stack for Orange Pi.

## Next implementation seam

The next risky step is the live landmark backend for webcam/video input on Arm64. That should be chosen explicitly before wiring in heavy dependencies such as OpenCV or MediaPipe.
