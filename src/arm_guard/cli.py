from __future__ import annotations

import argparse
import json

from arm_guard.gui import run_dashboard
from arm_guard.live.deps import LiveDependencyError
from arm_guard.live.session import LiveDetectionSession
from arm_guard.live.sources import Esp32HttpCaptureSource, OpenCVCaptureSource
from arm_guard.runtime import ArmGuardApplication


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arm-guard",
        description="Privacy-first scaffold for an ARM edge drowsiness detection system.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="Run a simulated drowsiness detection flow.")
    demo.add_argument("--no-log", action="store_true", help="Do not write anonymized event logs.")
    subparsers.add_parser("inspect-config", help="Print the default runtime configuration.")
    subparsers.add_parser("inspect-device", help="Print the current Arm64 target device spec.")
    subparsers.add_parser("inspect-backends", help="Print available detector backends.")
    subparsers.add_parser("gui", help="Launch the Tkinter dashboard for webcam or video input.")
    calibrate = subparsers.add_parser("calibrate", help="Run simulated driver calibration and persist a local profile.")
    calibrate.add_argument("--driver-id", default="driver-001", help="Local driver identifier used only for anonymized profile derivation.")
    benchmark = subparsers.add_parser("benchmark", help="Run a repeatable simulated benchmark.")
    benchmark.add_argument("--iterations", type=int, default=50, help="Number of simulated frames to process.")
    live = subparsers.add_parser("live", help="Run the baseline detector against a webcam or video file.")
    source_group = live.add_mutually_exclusive_group()
    source_group.add_argument("--camera-index", type=int, default=None, help="Webcam device index.")
    source_group.add_argument("--video", help="Path to a video file.")
    source_group.add_argument(
        "--esp32-url",
        help="Base URL of an ESP32-CAM CameraWebServer, for example http://192.168.4.1",
    )
    live.add_argument(
        "--esp32-timeout",
        type=float,
        default=None,
        help="HTTP timeout in seconds for ESP32-CAM snapshot polling.",
    )
    live.add_argument("--max-frames", type=int, default=120, help="Maximum number of frames to process.")
    live.add_argument(
        "--detector-backend",
        default=None,
        help="Named detector backend from the registry. Defaults to the registry default.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    app = ArmGuardApplication.build_default()

    if args.command == "inspect-config":
        print(app.config)
        return 0

    if args.command == "inspect-device":
        print(json.dumps(app.inspect_device(), indent=2))
        return 0

    if args.command == "inspect-backends":
        print(json.dumps(app.available_detector_backends(), indent=2))
        return 0

    if args.command == "calibrate":
        print(json.dumps(app.run_calibration(driver_id=args.driver_id), indent=2))
        return 0

    if args.command == "benchmark":
        print(json.dumps(app.run_benchmark(iterations=args.iterations), indent=2))
        return 0

    if args.command == "gui":
        return run_dashboard(app)

    if args.command == "live":
        source = build_live_source(app, args)
        try:
            session = LiveDetectionSession(app, source, detector_backend_name=args.detector_backend)
            session.open()
        except LiveDependencyError as exc:
            parser.error(str(exc))
        except KeyError as exc:
            parser.error(str(exc))

        processed = 0
        try:
            while processed < args.max_frames:
                result = session.next_frame()
                processed += 1
                print(
                    f"[frame {processed}] backend={result.detector_backend} "
                    f"score={result.processing.assessment.drowsiness_score:.3f} "
                    f"alert={result.processing.alert.level.value} "
                    f"status={result.processing.health.status.value} "
                    f"fps={result.processing.health.capture_fps:.1f} "
                    f"latency_ms={result.processing.health.latency_ms:.3f}"
                )
                if result.end_of_stream:
                    break
        finally:
            session.close()
        return 0

    if args.command == "demo":
        persist_events = not args.no_log
        print(f"Acceleration profile: {app.acceleration_profile.summary()}")
        print(f"Target device: {app.config.target_device}")
        for index, result in enumerate(app.run_demo(persist_events=persist_events), start=1):
            print(f"[frame {index}] ear={result.assessment.ear:.3f}")
            print(f"  baseline={result.assessment.baseline:.3f}")
            print(f"  threshold={result.assessment.threshold:.3f}")
            print(f"  drowsiness_score={result.assessment.drowsiness_score:.3f}")
            print(f"  alert={result.alert.level}")
            print(f"  status={result.health.status}")
            print(f"  latency_ms={result.health.latency_ms:.3f}")
            print(f"  fps={result.health.capture_fps:.1f}")
            if result.assessment.reasons:
                print(f"  reasons={', '.join(result.assessment.reasons)}")
            if result.health.notes:
                print(f"  health={', '.join(result.health.notes)}")
        if persist_events:
            print(f"events_log={app.config.events_path}")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


def build_live_source(app: ArmGuardApplication, args: argparse.Namespace) -> object:
    if args.esp32_url:
        return Esp32HttpCaptureSource(
            source=args.esp32_url,
            capture_path=app.config.esp32_camera_capture_path,
            timeout_seconds=args.esp32_timeout or app.config.esp32_camera_timeout_seconds,
        )

    if args.video:
        return OpenCVCaptureSource(args.video)

    camera_index = args.camera_index if args.camera_index is not None else app.config.default_camera_index
    return OpenCVCaptureSource(camera_index)
