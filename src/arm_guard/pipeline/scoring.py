from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DrowsinessScorer:
    blink_reference_seconds: float = 0.4
    microsleep_reference_seconds: float = 2.0

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
        blink_score = min(1.0, blink_duration_seconds / self.blink_reference_seconds)
        microsleep_score = min(1.0, microsleep_duration_seconds / self.microsleep_reference_seconds)
        confidence_score = max(0.0, min(1.0, detection_confidence))
        risk_score = min(1.0, 1.25 - min(context_risk_multiplier, 1.25) + 0.2)

        weighted = (
            normalized_ear_drop * 0.40
            + blink_score * 0.20
            + microsleep_score * 0.25
            + confidence_score * 0.05
            + risk_score * 0.10
        )
        return round(max(0.0, min(1.0, weighted)), 4)
