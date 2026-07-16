from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AppConfig:
    project_name: str = "ARM-Guard"
    target_device: str = "Orange Pi 5 Plus (RK3588)"
    default_baseline_ear: float = 0.27
    alert_threshold_ratio: float = 0.82
    baseline_window: int = 120
    minimum_learning_speed_kph: float = 48.0
    learning_target_hours: float = 10.0
    camera_stale_seconds: int = 10
    speed_alert_floor_kph: float = 5.0
    low_fps_threshold: float = 12.0
    low_confidence_threshold: float = 0.45
    max_arm_temperature_c: float = 85.0
    max_memory_pressure_percent: float = 90.0
    privacy_mode: bool = True
    store_raw_frames: bool = False
    events_path: Path = Path("demo/output/events.jsonl")
    profiles_dir: Path = Path("demo/profiles")
