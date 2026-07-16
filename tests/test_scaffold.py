from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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
