from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from time import perf_counter

from arm_guard.arm.acceleration import ArmAccelerationProfile
from arm_guard.config import AppConfig
from arm_guard.domain.models import AlertDecision, DetectionFrame, DriverContext, DrowsinessAssessment, RuntimeTelemetry, SystemHealth
from arm_guard.integrations.context import ContextualAlertPolicy
from arm_guard.pipeline.ear import PrivacyPreservingEarEstimator
from arm_guard.pipeline.scoring import DrowsinessScorer
from arm_guard.privacy.consent import ConsentManager
from arm_guard.profile.adaptive import AdaptiveDriverProfiler
from arm_guard.safety.alerts import SafetyAlertSystem
from arm_guard.safety.monitoring import SystemReliabilityMonitor


@dataclass(slots=True, frozen=True)
class ProcessingResult:
    assessment: DrowsinessAssessment
    alert: AlertDecision
    health: SystemHealth


class ArmGuardPipeline:
    def __init__(
        self,
        config: AppConfig,
        ear_estimator: PrivacyPreservingEarEstimator,
        profiler: AdaptiveDriverProfiler,
        alert_policy: ContextualAlertPolicy,
        scorer: DrowsinessScorer,
        alert_system: SafetyAlertSystem,
        monitor: SystemReliabilityMonitor,
        consent_manager: ConsentManager,
        acceleration_profile: ArmAccelerationProfile,
    ) -> None:
        self._config = config
        self._ear_estimator = ear_estimator
        self._profiler = profiler
        self._alert_policy = alert_policy
        self._scorer = scorer
        self._alert_system = alert_system
        self._monitor = monitor
        self._consent_manager = consent_manager
        self._acceleration_profile = acceleration_profile
        self._closed_started_at: dict[str, datetime | None] = {}

    def estimate_average_ear(self, frame: DetectionFrame) -> float:
        return self._ear_estimator.calculate_average(frame.left_eye, frame.right_eye)

    def process(self, frame: DetectionFrame) -> ProcessingResult:
        started_at = perf_counter()
        telemetry = frame.telemetry

        if not self._consent_manager.can_process(frame.context):
            return self._build_no_detection_result(
                started_at=started_at,
                telemetry=telemetry,
                reason="processing blocked by consent policy",
                camera_online=telemetry is not None,
                fallback_mode=False,
                consent_withheld=True,
                confidence=1.0,
            )

        ear = self.estimate_average_ear(frame)
        baseline = self._profiler.update_and_get_baseline(
            driver_id=frame.driver_id,
            ear=ear,
            context=frame.context,
            captured_at=frame.captured_at,
        )
        threshold_multiplier = self._alert_policy.detection_sensitivity_multiplier(frame.context)
        context_risk_multiplier = self._alert_policy.scoring_risk_multiplier(frame.context)
        threshold = baseline * self._config.alert_threshold_ratio * threshold_multiplier
        eyes_closed = ear < threshold
        blink_duration_seconds = self._closed_duration_seconds(frame.driver_id, frame.captured_at, eyes_closed)
        microsleep_duration_seconds = (
            blink_duration_seconds
            if blink_duration_seconds >= self._config.microsleep_duration_seconds
            else 0.0
        )
        confidence = max(0.0, min(1.0, frame.detection_confidence))
        drowsiness_score = self._scorer.score(
            ear=ear,
            baseline=baseline,
            blink_duration_seconds=blink_duration_seconds,
            microsleep_duration_seconds=microsleep_duration_seconds,
            detection_confidence=confidence,
            context_risk_multiplier=context_risk_multiplier,
        )
        should_alert = (
            self._alert_policy.alert_allowed(frame.context)
            and drowsiness_score >= self._config.alert_score_threshold
        )

        reasons: list[str] = []
        if eyes_closed:
            reasons.append("eye aspect ratio below contextual threshold")
        if blink_duration_seconds >= self._config.minimum_blink_duration_seconds:
            reasons.append("prolonged blink detected")
        if microsleep_duration_seconds > 0:
            reasons.append("microsleep-like closure detected")
        if frame.context.road_type.lower() == "highway":
            reasons.append("highway profile active")
        if 2 <= frame.context.hour_24 <= 5:
            reasons.append("peak drowsiness hours")

        assessment = DrowsinessAssessment(
            ear=ear,
            baseline=baseline,
            threshold=threshold,
            blink_duration_seconds=blink_duration_seconds,
            microsleep_duration_seconds=microsleep_duration_seconds,
            drowsiness_score=drowsiness_score,
            confidence=confidence,
            reasons=tuple(reasons),
            should_alert=should_alert,
        )

        duration_seconds = self._profiler.alert_duration_seconds(
            driver_id=frame.driver_id,
            captured_at=frame.captured_at,
            alert_active=should_alert,
        )
        alert = self._alert_system.escalate(assessment, duration_seconds)
        latency_ms = round((perf_counter() - started_at) * 1000, 3)
        health = self._monitor.snapshot(
            acceleration_backend=self._acceleration_profile.summary(),
            camera_online=True,
            fallback_mode=False,
            consent_withheld=False,
            capture_fps=telemetry.capture_fps if telemetry else 0.0,
            latency_ms=latency_ms,
            detection_confidence=confidence,
            arm_temperature_c=telemetry.cpu_temperature_c if telemetry else 0.0,
            memory_pressure_percent=telemetry.memory_pressure_percent if telemetry else 0.0,
            power_draw_watts=telemetry.power_draw_watts if telemetry else None,
        )

        return ProcessingResult(assessment=assessment, alert=alert, health=health)

    def process_missing_detection(
        self,
        *,
        driver_id: str,
        captured_at: datetime,
        context: DriverContext,
        telemetry: RuntimeTelemetry,
        reason: str,
        camera_online: bool = True,
        fallback_mode: bool = False,
        stale_frame_seconds: float | None = None,
    ) -> ProcessingResult:
        started_at = perf_counter()
        self._profiler.alert_duration_seconds(
            driver_id=driver_id,
            captured_at=captured_at,
            alert_active=False,
        )
        return self._build_no_detection_result(
            started_at=started_at,
            telemetry=telemetry,
            reason=reason,
            camera_online=camera_online,
            fallback_mode=fallback_mode,
            consent_withheld=False,
            confidence=0.0,
            stale_frame_seconds=stale_frame_seconds,
        )

    def _closed_duration_seconds(
        self,
        driver_id: str,
        captured_at: datetime,
        eyes_closed: bool,
    ) -> float:
        started_at = self._closed_started_at.get(driver_id)

        if not eyes_closed:
            self._closed_started_at[driver_id] = None
            return 0.0

        if started_at is None:
            self._closed_started_at[driver_id] = captured_at
            return 0.0

        return max(0.0, (captured_at - started_at).total_seconds())

    def _build_no_detection_result(
        self,
        *,
        started_at: float,
        telemetry: RuntimeTelemetry | None,
        reason: str,
        camera_online: bool,
        fallback_mode: bool,
        consent_withheld: bool,
        confidence: float,
        stale_frame_seconds: float | None = None,
    ) -> ProcessingResult:
        assessment = DrowsinessAssessment(
            ear=0.0,
            baseline=self._config.default_baseline_ear,
            threshold=0.0,
            blink_duration_seconds=0.0,
            microsleep_duration_seconds=0.0,
            drowsiness_score=0.0,
            confidence=confidence,
            reasons=(reason,),
            should_alert=False,
        )
        latency_ms = round((perf_counter() - started_at) * 1000, 3)
        health = self._monitor.snapshot(
            acceleration_backend=self._acceleration_profile.summary(),
            camera_online=camera_online,
            fallback_mode=fallback_mode,
            consent_withheld=consent_withheld,
            capture_fps=telemetry.capture_fps if telemetry else 0.0,
            latency_ms=latency_ms,
            detection_confidence=confidence,
            arm_temperature_c=telemetry.cpu_temperature_c if telemetry else 0.0,
            memory_pressure_percent=telemetry.memory_pressure_percent if telemetry else 0.0,
            power_draw_watts=telemetry.power_draw_watts if telemetry else None,
            stale_frame_seconds=stale_frame_seconds,
        )
        return ProcessingResult(
            assessment=assessment,
            alert=self._alert_system.clear(),
            health=health,
        )
