from __future__ import annotations

from dataclasses import dataclass

from arm_guard.config import AppConfig
from arm_guard.domain.models import SystemHealth, SystemStatus


@dataclass(slots=True)
class SystemReliabilityMonitor:
    config: AppConfig

    def snapshot(
        self,
        *,
        acceleration_backend: str,
        camera_online: bool,
        fallback_mode: bool,
        capture_fps: float,
        latency_ms: float,
        detection_confidence: float,
        arm_temperature_c: float,
        memory_pressure_percent: float,
        power_draw_watts: float | None,
    ) -> SystemHealth:
        notes: list[str] = []
        status = SystemStatus.NORMAL

        if not camera_online:
            status = SystemStatus.CAMERA_UNAVAILABLE
            notes.append("camera input unavailable")
        elif detection_confidence < self.config.low_confidence_threshold:
            status = SystemStatus.LOW_CONFIDENCE
            notes.append("landmark confidence below threshold")

        if arm_temperature_c > self.config.max_arm_temperature_c:
            status = SystemStatus.PERFORMANCE_DEGRADED
            notes.append("thermal throttling recommended")
        if memory_pressure_percent > self.config.max_memory_pressure_percent:
            status = SystemStatus.PERFORMANCE_DEGRADED
            notes.append("memory cleanup recommended")
        if capture_fps < self.config.low_fps_threshold:
            status = SystemStatus.PERFORMANCE_DEGRADED
            notes.append("capture FPS below target threshold")
        if fallback_mode:
            notes.append("backup sensors should be engaged")

        return SystemHealth(
            status=status,
            camera_online=camera_online,
            fallback_mode=fallback_mode,
            arm_temperature_c=arm_temperature_c,
            memory_pressure_percent=memory_pressure_percent,
            acceleration_backend=acceleration_backend,
            capture_fps=capture_fps,
            latency_ms=latency_ms,
            power_draw_watts=power_draw_watts,
            notes=tuple(notes),
        )
