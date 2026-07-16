from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arm_guard.domain.models import DetectionFrame, DriverContext
from arm_guard.pipeline.ear import PrivacyPreservingEarEstimator
from arm_guard.runtime import ArmGuardApplication


class ScaffoldTests(unittest.TestCase):
    def test_ear_estimator_returns_expected_ratio(self) -> None:
        estimator = PrivacyPreservingEarEstimator()
        eye = (
            (0.0, 0.0),
            (1.0, 2.0),
            (3.0, 2.0),
            (4.0, 0.0),
            (3.0, -2.0),
            (1.0, -2.0),
        )

        self.assertAlmostEqual(estimator.calculate(eye), 1.0)

    def test_application_demo_alerts_on_later_frames(self) -> None:
        app = ArmGuardApplication.build_default()
        results = app.run_demo()

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].alert.level, "none")
        self.assertNotEqual(results[-1].alert.level, "none")
        self.assertTrue(app.config.events_path.exists())
        self.assertIn("eye aspect ratio below contextual threshold", results[1].assessment.reasons)

    def test_demo_events_do_not_store_raw_frames(self) -> None:
        app = ArmGuardApplication.build_default()
        app.run_demo()

        lines = app.config.events_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreater(len(lines), 0)
        first_event = json.loads(lines[0])
        self.assertFalse(first_event["raw_frame_stored"])

    def test_benchmark_returns_metrics(self) -> None:
        app = ArmGuardApplication.build_default()
        metrics = app.run_benchmark(iterations=10)

        self.assertIn("avg_latency_ms", metrics)
        self.assertIn("p95_latency_ms", metrics)
        self.assertIn("avg_capture_fps", metrics)

    def test_missing_detection_returns_safe_result(self) -> None:
        app = ArmGuardApplication.build_default()
        result = app.pipeline.process_missing_detection(
            driver_id="driver-001",
            captured_at=app.demo_frames.sample_frames()[0].captured_at,
            context=app.live_context(),
            telemetry=app.runtime_telemetry(1),
            reason="face or eye landmarks not detected",
        )

        self.assertEqual(result.assessment.drowsiness_score, 0.0)
        self.assertEqual(result.alert.level, "none")

    def test_consent_blocked_frames_report_consent_withheld(self) -> None:
        app = ArmGuardApplication.build_default()
        frame = app.demo_frames.sample_frames()[0]
        frame = app._with_emulated_telemetry(frame, 1)
        blocked = DetectionFrame(
            frame_id=frame.frame_id,
            driver_id=frame.driver_id,
            left_eye=frame.left_eye,
            right_eye=frame.right_eye,
            captured_at=frame.captured_at,
            context=DriverContext(
                speed_kph=frame.context.speed_kph,
                road_type=frame.context.road_type,
                hour_24=frame.context.hour_24,
                ambient_light=frame.context.ambient_light,
                consent_granted=False,
            ),
            detection_confidence=frame.detection_confidence,
            telemetry=frame.telemetry,
        )

        result = app.pipeline.process(blocked)
        self.assertEqual(result.health.status, "consent_withheld")
        self.assertTrue(result.health.camera_online)

    def test_microsleep_does_not_enable_fallback_mode(self) -> None:
        app = ArmGuardApplication.build_default()
        results = app.run_demo(persist_events=False)

        self.assertGreater(results[-1].assessment.microsleep_duration_seconds, 0.0)
        self.assertFalse(results[-1].health.fallback_mode)

    def test_learning_hours_use_elapsed_timestamps(self) -> None:
        app = ArmGuardApplication.build_default()
        frame = app.demo_frames.sample_frames()[0]
        frame = app._with_emulated_telemetry(frame, 1)
        app.profiler.update_and_get_baseline(
            driver_id=frame.driver_id,
            ear=app.pipeline.estimate_average_ear(frame),
            context=frame.context,
            captured_at=frame.captured_at,
        )
        later = DetectionFrame(
            frame_id=frame.frame_id + 1,
            driver_id=frame.driver_id,
            left_eye=frame.left_eye,
            right_eye=frame.right_eye,
            captured_at=frame.captured_at + timedelta(seconds=10),
            context=frame.context,
            detection_confidence=frame.detection_confidence,
            telemetry=frame.telemetry,
        )
        app.profiler.update_and_get_baseline(
            driver_id=later.driver_id,
            ear=app.pipeline.estimate_average_ear(later),
            context=later.context,
            captured_at=later.captured_at,
        )
        profile = app.profiler.export_profile(frame.driver_id)

        self.assertAlmostEqual(profile["learning_hours"], round(10 / 3600, 4))

    def test_cli_demo_command(self) -> None:
        completed = subprocess.run(
            [sys.executable, "main.py", "demo"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Acceleration profile:", completed.stdout)
        self.assertIn("Target device:", completed.stdout)


if __name__ == "__main__":
    unittest.main()
