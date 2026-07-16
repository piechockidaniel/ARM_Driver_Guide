from __future__ import annotations

from dataclasses import dataclass, replace
from statistics import fmean
from typing import Any

from arm_guard.arm.acceleration import ArmAccelerationProfile
from arm_guard.config import AppConfig
from arm_guard.device.specs import OrangePi5PlusEmulator, orange_pi_5_plus_spec
from arm_guard.events.logger import EventLogger
from arm_guard.events.models import AnonymizedDetectionEvent
from arm_guard.integrations.context import ContextualAlertPolicy, DemoFrameFactory
from arm_guard.pipeline.ear import PrivacyPreservingEarEstimator
from arm_guard.pipeline.engine import ArmGuardPipeline, ProcessingResult
from arm_guard.pipeline.scoring import DrowsinessScorer
from arm_guard.privacy.consent import ConsentManager
from arm_guard.profile.adaptive import AdaptiveDriverProfiler
from arm_guard.safety.alerts import SafetyAlertSystem
from arm_guard.safety.monitoring import SystemReliabilityMonitor


@dataclass(slots=True)
class ArmGuardApplication:
    config: AppConfig
    pipeline: ArmGuardPipeline
    demo_frames: DemoFrameFactory
    acceleration_profile: ArmAccelerationProfile
    profiler: AdaptiveDriverProfiler
    event_logger: EventLogger
    device_emulator: OrangePi5PlusEmulator

    @classmethod
    def build_default(cls) -> "ArmGuardApplication":
        config = AppConfig()
        acceleration_profile = ArmAccelerationProfile()
        profiler = AdaptiveDriverProfiler(config)
        pipeline = ArmGuardPipeline(
            config=config,
            ear_estimator=PrivacyPreservingEarEstimator(),
            profiler=profiler,
            alert_policy=ContextualAlertPolicy(),
            scorer=DrowsinessScorer(),
            alert_system=SafetyAlertSystem(),
            monitor=SystemReliabilityMonitor(config),
            consent_manager=ConsentManager(),
            acceleration_profile=acceleration_profile,
        )
        return cls(
            config=config,
            pipeline=pipeline,
            demo_frames=DemoFrameFactory(),
            acceleration_profile=acceleration_profile,
            profiler=profiler,
            event_logger=EventLogger(config.events_path),
            device_emulator=OrangePi5PlusEmulator(),
        )

    def run_demo(self, *, persist_events: bool = True) -> list[ProcessingResult]:
        if persist_events:
            self.event_logger.reset()

        results: list[ProcessingResult] = []
        for index, frame in enumerate(self.demo_frames.sample_frames(), start=1):
            result = self.pipeline.process(self._with_emulated_telemetry(frame, index))
            results.append(result)
            if persist_events:
                self.event_logger.append(self._event_for(frame, result))
        return results

    def run_calibration(self, driver_id: str = "driver-001") -> dict[str, Any]:
        for index, frame in enumerate(self.demo_frames.calibration_frames(), start=1):
            frame = self._with_emulated_telemetry(frame, index)
            ear = self.pipeline._ear_estimator.calculate_average(frame.left_eye, frame.right_eye)
            self.profiler.update_and_get_baseline(driver_id=driver_id, ear=ear, context=frame.context)

        output = self.profiler.persist_profile(driver_id, self.config.profiles_dir)
        payload = self.profiler.export_profile(driver_id)
        payload["output_path"] = str(output)
        return payload

    def run_benchmark(self, *, iterations: int = 50) -> dict[str, float]:
        latencies: list[float] = []
        fps_values: list[float] = []
        memory_values: list[float] = []
        power_values: list[float] = []

        frames = self.demo_frames.sample_frames()
        for index in range(iterations):
            frame = self._with_emulated_telemetry(frames[index % len(frames)], index + 1)
            result = self.pipeline.process(frame)
            latencies.append(result.health.latency_ms)
            fps_values.append(result.health.capture_fps)
            memory_values.append(result.health.memory_pressure_percent)
            if result.health.power_draw_watts is not None:
                power_values.append(result.health.power_draw_watts)

        ordered = sorted(latencies)
        p95_index = max(0, min(len(ordered) - 1, round(len(ordered) * 0.95) - 1))
        return {
            "avg_latency_ms": round(fmean(latencies), 3),
            "p95_latency_ms": round(ordered[p95_index], 3),
            "avg_capture_fps": round(fmean(fps_values), 3),
            "avg_memory_pressure_percent": round(fmean(memory_values), 3),
            "avg_power_draw_watts": round(fmean(power_values), 3) if power_values else 0.0,
        }

    def inspect_device(self) -> dict[str, Any]:
        spec = orange_pi_5_plus_spec()
        return {
            "name": spec.name,
            "soc": spec.soc,
            "cpu": spec.cpu,
            "gpu": spec.gpu,
            "npu": spec.npu,
            "ram": spec.ram,
            "storage": spec.storage,
            "connectivity": spec.connectivity,
            "camera_interface": spec.camera_interface,
            "power": spec.power,
            "supported_os": list(spec.supported_os),
            "bundle": [f"{item.name}: {item.note}" for item in spec.bundle],
        }

    def _event_for(self, frame: object, result: ProcessingResult) -> AnonymizedDetectionEvent:
        detection_frame = frame
        return AnonymizedDetectionEvent(
            timestamp=detection_frame.captured_at.isoformat(),
            driver_profile_id=self.profiler.anonymous_profile_id(detection_frame.driver_id),
            drowsiness_score=result.assessment.drowsiness_score,
            alert_level=result.alert.level.value,
            vehicle_speed_kph=detection_frame.context.speed_kph,
            raw_frame_stored=False if self.config.privacy_mode else self.config.store_raw_frames,
            system_status=result.health.status.value,
            latency_ms=result.health.latency_ms,
            detection_confidence=result.assessment.confidence,
        )

    def _with_emulated_telemetry(self, frame: object, frame_index: int) -> object:
        snapshot = self.device_emulator.runtime_snapshot(frame_index)
        telemetry = replace(
            frame.telemetry,
            cpu_temperature_c=snapshot.cpu_temperature_c,
            memory_pressure_percent=snapshot.memory_pressure_percent,
            capture_fps=snapshot.capture_fps,
            power_draw_watts=snapshot.power_draw_watts,
        )
        return replace(frame, telemetry=telemetry)
