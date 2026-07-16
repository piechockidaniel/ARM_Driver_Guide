from __future__ import annotations

from dataclasses import dataclass

from arm_guard.config import AppConfig


@dataclass(slots=True, frozen=True)
class DrowsinessScorer:
    config: AppConfig

    def score(
        self,
        *,
        ear: float,
        baseline: float,
        blink_duration_seconds: float,
        microsleep_duration_seconds: float,
        detection_confidence: float,
        context_risk_multiplier: float,
    ) -> float:
        normalized_ear_drop = max(0.0, min(1.0, 1.0 - (ear / max(baseline, 0.01))))
        blink_score = min(1.0, blink_duration_seconds / self.config.blink_reference_seconds)
        microsleep_score = min(1.0, microsleep_duration_seconds / self.config.microsleep_reference_seconds)
        confidence_score = max(0.0, min(1.0, detection_confidence))
        min_risk = min(1.0, self.config.residential_scoring_risk_multiplier)
        max_risk = max(
            1.0,
            self.config.highway_scoring_risk_multiplier,
            self.config.peak_drowsiness_scoring_risk_multiplier,
            self.config.highway_scoring_risk_multiplier
            * self.config.peak_drowsiness_scoring_risk_multiplier,
        )
        risk_span = max(0.01, max_risk - min_risk)
        risk_score = max(0.0, min(1.0, (context_risk_multiplier - min_risk) / risk_span))

        weighted = (
            normalized_ear_drop * self.config.ear_weight
            + blink_score * self.config.blink_weight
            + microsleep_score * self.config.microsleep_weight
            + confidence_score * self.config.confidence_weight
            + risk_score * self.config.context_risk_weight
        )
        return round(max(0.0, min(1.0, weighted)), 4)
