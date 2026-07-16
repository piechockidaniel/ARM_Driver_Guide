from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


Point = tuple[float, float]


class AlertLevel(StrEnum):
    NONE = "none"
    GENTLE = "gentle"
    MODERATE = "moderate"
    EMERGENCY = "emergency"


class SystemStatus(StrEnum):
    NORMAL = "normal"
    LOW_CONFIDENCE = "low_confidence"
    CAMERA_UNAVAILABLE = "camera_unavailable"
    CONSENT_WITHHELD = "consent_withheld"
    PERFORMANCE_DEGRADED = "performance_degraded"


@dataclass(slots=True, frozen=True)
class DriverContext:
    speed_kph: float
    road_type: str
    hour_24: int
    ambient_light: str = "day"
    consent_granted: bool = True


@dataclass(slots=True, frozen=True)
class RuntimeTelemetry:
    source_device: str
    cpu_temperature_c: float
    memory_pressure_percent: float
    capture_fps: float
    power_draw_watts: float | None = None


@dataclass(slots=True, frozen=True)
class DetectionFrame:
    frame_id: int
    driver_id: str
    left_eye: tuple[Point, Point, Point, Point, Point, Point]
    right_eye: tuple[Point, Point, Point, Point, Point, Point]
    captured_at: datetime
    context: DriverContext
    detection_confidence: float = 0.95
    telemetry: RuntimeTelemetry | None = None


@dataclass(slots=True, frozen=True)
class DrowsinessAssessment:
    ear: float
    baseline: float
    threshold: float
    blink_duration_seconds: float
    microsleep_duration_seconds: float
    drowsiness_score: float
    confidence: float
    reasons: tuple[str, ...] = ()
    should_alert: bool = False


@dataclass(slots=True, frozen=True)
class AlertDecision:
    level: AlertLevel
    actions: tuple[str, ...]
    fleet_notification_required: bool = False
    duration_seconds: float = 0.0


@dataclass(slots=True, frozen=True)
class SystemHealth:
    status: SystemStatus
    camera_online: bool
    fallback_mode: bool
    arm_temperature_c: float
    memory_pressure_percent: float
    acceleration_backend: str
    capture_fps: float
    latency_ms: float
    power_draw_watts: float | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)
