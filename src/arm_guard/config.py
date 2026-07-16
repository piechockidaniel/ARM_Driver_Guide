from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AppConfig:
    project_name: str = "ARM-Guard"
    target_device: str = "Orange Pi 5 Plus (RK3588)"
    default_camera_index: int = 0
    gui_refresh_ms: int = 30
    face_landmarker_model_path: Path = Path("assets/models/face_landmarker.task")
    face_landmarker_model_url: str = (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
        "face_landmarker/float16/latest/face_landmarker.task"
    )
    default_baseline_ear: float = 0.27
    alert_threshold_ratio: float = 0.82
    alert_score_threshold: float = 0.55
    baseline_window: int = 120
    minimum_learning_speed_kph: float = 48.0
    learning_target_hours: float = 10.0
    assumed_frame_interval_seconds: float = 1.0
    camera_stale_seconds: int = 10
    speed_alert_floor_kph: float = 5.0
    low_fps_threshold: float = 12.0
    low_confidence_threshold: float = 0.45
    max_arm_temperature_c: float = 85.0
    max_memory_pressure_percent: float = 90.0
    minimum_blink_duration_seconds: float = 0.25
    microsleep_duration_seconds: float = 1.5
    gentle_alert_duration_seconds: float = 3.0
    emergency_alert_duration_seconds: float = 8.0
    blink_reference_seconds: float = 0.4
    microsleep_reference_seconds: float = 2.0
    ear_weight: float = 0.40
    blink_weight: float = 0.20
    microsleep_weight: float = 0.25
    confidence_weight: float = 0.05
    context_risk_weight: float = 0.10
    residential_detection_sensitivity_multiplier: float = 0.95
    highway_detection_sensitivity_multiplier: float = 1.10
    peak_drowsiness_detection_sensitivity_multiplier: float = 1.15
    residential_scoring_risk_multiplier: float = 0.95
    highway_scoring_risk_multiplier: float = 1.10
    peak_drowsiness_scoring_risk_multiplier: float = 1.15
    privacy_mode: bool = True
    store_raw_frames: bool = False
    events_path: Path = Path("demo/output/events.jsonl")
    profiles_dir: Path = Path("demo/profiles")
