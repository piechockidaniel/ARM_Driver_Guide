from __future__ import annotations

from dataclasses import dataclass

from arm_guard.config import AppConfig
from arm_guard.domain.models import AlertDecision, AlertLevel, DrowsinessAssessment


@dataclass(slots=True, frozen=True)
class SafetyAlertSystem:
    config: AppConfig

    def escalate(self, assessment: DrowsinessAssessment, duration_seconds: float) -> AlertDecision:
        if not assessment.should_alert:
            return self.clear()

        if duration_seconds < self.config.gentle_alert_duration_seconds:
            return AlertDecision(
                level=AlertLevel.GENTLE,
                actions=("seat_vibration_low", "dashboard_nudge"),
                duration_seconds=duration_seconds,
            )

        if duration_seconds < self.config.emergency_alert_duration_seconds:
            return AlertDecision(
                level=AlertLevel.MODERATE,
                actions=("seat_vibration_medium", "audio_tone_soft", "visual_warning"),
                duration_seconds=duration_seconds,
            )

        return AlertDecision(
            level=AlertLevel.EMERGENCY,
            actions=("seat_vibration_high", "audio_tone_urgent", "fleet_notification"),
            fleet_notification_required=True,
            duration_seconds=duration_seconds,
        )

    def clear(self) -> AlertDecision:
        return AlertDecision(level=AlertLevel.NONE, actions=())
