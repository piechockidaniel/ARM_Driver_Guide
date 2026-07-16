from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True, frozen=True)
class AnonymizedDetectionEvent:
    timestamp: str
    driver_profile_id: str
    drowsiness_score: float
    alert_level: str
    vehicle_speed_kph: float
    raw_frame_stored: bool
    system_status: str
    latency_ms: float
    detection_confidence: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
