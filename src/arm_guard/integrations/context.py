from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from arm_guard.config import AppConfig
from arm_guard.domain.models import DetectionFrame, DriverContext, Point, RuntimeTelemetry


@dataclass(slots=True, frozen=True)
class ContextualAlertPolicy:
    config: AppConfig

    def alert_allowed(self, context: DriverContext) -> bool:
        return context.speed_kph >= self.config.speed_alert_floor_kph and context.consent_granted

    def detection_sensitivity_multiplier(self, context: DriverContext) -> float:
        multiplier = 1.0
        road = context.road_type.lower()

        if road == "residential":
            multiplier *= self.config.residential_detection_sensitivity_multiplier
        elif road == "highway":
            multiplier *= self.config.highway_detection_sensitivity_multiplier

        if 2 <= context.hour_24 <= 5:
            multiplier *= self.config.peak_drowsiness_detection_sensitivity_multiplier

        return multiplier

    def scoring_risk_multiplier(self, context: DriverContext) -> float:
        multiplier = 1.0
        road = context.road_type.lower()

        if road == "residential":
            multiplier *= self.config.residential_scoring_risk_multiplier
        elif road == "highway":
            multiplier *= self.config.highway_scoring_risk_multiplier

        if 2 <= context.hour_24 <= 5:
            multiplier *= self.config.peak_drowsiness_scoring_risk_multiplier

        return multiplier


@dataclass(slots=True, frozen=True)
class DemoFrameFactory:
    base_time: datetime = datetime(2026, 7, 16, 8, 0, tzinfo=timezone.utc)

    def sample_frames(self) -> list[DetectionFrame]:
        return [
            DetectionFrame(
                frame_id=1,
                driver_id="driver-001",
                left_eye=self._eye(horizontal=4.0, upper=1.8, lower=1.7),
                right_eye=self._eye(horizontal=4.0, upper=1.8, lower=1.7),
                captured_at=self.base_time,
                context=DriverContext(speed_kph=78, road_type="highway", hour_24=8),
                detection_confidence=0.98,
                telemetry=self._telemetry(58.0, 34.0, 28.0, 8.4),
            ),
            DetectionFrame(
                frame_id=2,
                driver_id="driver-001",
                left_eye=self._eye(horizontal=4.0, upper=1.1, lower=1.0),
                right_eye=self._eye(horizontal=4.0, upper=1.0, lower=1.0),
                captured_at=self.base_time + timedelta(seconds=2),
                context=DriverContext(speed_kph=84, road_type="highway", hour_24=3),
                detection_confidence=0.95,
                telemetry=self._telemetry(61.0, 36.0, 27.0, 8.8),
            ),
            DetectionFrame(
                frame_id=3,
                driver_id="driver-001",
                left_eye=self._eye(horizontal=4.0, upper=0.8, lower=0.7),
                right_eye=self._eye(horizontal=4.0, upper=0.8, lower=0.7),
                captured_at=self.base_time + timedelta(seconds=9),
                context=DriverContext(speed_kph=86, road_type="highway", hour_24=3),
                detection_confidence=0.93,
                telemetry=self._telemetry(64.0, 39.0, 26.0, 9.3),
            ),
            DetectionFrame(
                frame_id=4,
                driver_id="driver-001",
                left_eye=self._eye(horizontal=4.0, upper=0.7, lower=0.6),
                right_eye=self._eye(horizontal=4.0, upper=0.7, lower=0.6),
                captured_at=self.base_time + timedelta(seconds=13),
                context=DriverContext(speed_kph=88, road_type="highway", hour_24=3),
                detection_confidence=0.42,
                telemetry=self._telemetry(74.0, 58.0, 10.0, 10.6),
            ),
        ]

    def calibration_frames(self) -> list[DetectionFrame]:
        frames: list[DetectionFrame] = []
        for frame_id in range(100, 112):
            upper = 1.6 + (frame_id % 3) * 0.05
            lower = 1.5 + (frame_id % 2) * 0.05
            frames.append(
                DetectionFrame(
                    frame_id=frame_id,
                    driver_id="driver-001",
                    left_eye=self._eye(horizontal=4.0, upper=upper, lower=lower),
                    right_eye=self._eye(horizontal=4.0, upper=upper, lower=lower),
                    captured_at=self.base_time + timedelta(seconds=frame_id),
                    context=DriverContext(speed_kph=72, road_type="highway", hour_24=14),
                    detection_confidence=0.97,
                    telemetry=self._telemetry(56.0, 32.0, 29.0, 7.9),
                )
            )
        return frames

    def _eye(self, *, horizontal: float, upper: float, lower: float) -> tuple[Point, Point, Point, Point, Point, Point]:
        return (
            (0.0, 0.0),
            (1.0, upper),
            (3.0, lower),
            (horizontal, 0.0),
            (3.0, -lower),
            (1.0, -upper),
        )

    def _telemetry(
        self,
        cpu_temperature_c: float,
        memory_pressure_percent: float,
        capture_fps: float,
        power_draw_watts: float,
    ) -> RuntimeTelemetry:
        return RuntimeTelemetry(
            source_device="Orange Pi 5 Plus",
            cpu_temperature_c=cpu_temperature_c,
            memory_pressure_percent=memory_pressure_percent,
            capture_fps=capture_fps,
            power_draw_watts=power_draw_watts,
        )
