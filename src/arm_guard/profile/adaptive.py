from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from arm_guard.config import AppConfig
from arm_guard.domain.models import DriverContext


@dataclass(slots=True)
class DriverLearningState:
    baseline_ear: float
    learning_hours: float = 0.0


class AdaptiveDriverProfiler:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._samples: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=config.baseline_window)
        )
        self._states: dict[str, DriverLearningState] = {}
        self._alert_started_at: dict[str, datetime | None] = {}

    def update_and_get_baseline(self, driver_id: str, ear: float, context: DriverContext) -> float:
        state = self._states.setdefault(
            driver_id,
            DriverLearningState(baseline_ear=self._config.default_baseline_ear),
        )

        if context.speed_kph >= self._config.minimum_learning_speed_kph:
            samples = self._samples[driver_id]
            samples.append(ear)
            state.baseline_ear = sum(samples) / len(samples)
            state.learning_hours = min(
                self._config.learning_target_hours,
                state.learning_hours + (1 / 3600),
            )

        return state.baseline_ear

    def anonymous_profile_id(self, driver_id: str) -> str:
        digest = hashlib.sha256(driver_id.encode("utf-8")).hexdigest()
        return f"anon-{digest[:12]}"

    def alert_duration_seconds(
        self,
        driver_id: str,
        captured_at: datetime,
        *,
        alert_active: bool,
    ) -> float:
        started_at = self._alert_started_at.get(driver_id)

        if not alert_active:
            self._alert_started_at[driver_id] = None
            return 0.0

        if started_at is None:
            self._alert_started_at[driver_id] = captured_at
            return 0.0

        return max(0.0, (captured_at - started_at).total_seconds())

    def export_profile(self, driver_id: str) -> dict[str, object]:
        state = self._states.setdefault(
            driver_id,
            DriverLearningState(baseline_ear=self._config.default_baseline_ear),
        )
        return {
            "driver_profile_id": self.anonymous_profile_id(driver_id),
            "baseline_ear": round(state.baseline_ear, 4),
            "learning_hours": round(state.learning_hours, 4),
            "window_size": len(self._samples[driver_id]),
        }

    def persist_profile(self, driver_id: str, profiles_dir: Path) -> Path:
        profiles_dir.mkdir(parents=True, exist_ok=True)
        payload = self.export_profile(driver_id)
        output = profiles_dir / f"{payload['driver_profile_id']}.json"
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output
