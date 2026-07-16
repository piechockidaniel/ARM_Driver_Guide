from __future__ import annotations

import argparse
import json

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
    calibrate = subparsers.add_parser("calibrate", help="Run simulated driver calibration and persist a local profile.")
    calibrate.add_argument("--driver-id", default="driver-001", help="Local driver identifier used only for anonymized profile derivation.")
    benchmark = subparsers.add_parser("benchmark", help="Run a repeatable simulated benchmark.")
    benchmark.add_argument("--iterations", type=int, default=50, help="Number of simulated frames to process.")

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

    if args.command == "calibrate":
        print(json.dumps(app.run_calibration(driver_id=args.driver_id), indent=2))
        return 0

    if args.command == "benchmark":
        print(json.dumps(app.run_benchmark(iterations=args.iterations), indent=2))
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
