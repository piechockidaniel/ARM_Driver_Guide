from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from arm_guard.events.models import AnonymizedDetectionEvent


@dataclass(slots=True)
class EventLogger:
    path: Path

    def append(self, event: AnonymizedDetectionEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), ensure_ascii=False))
            handle.write("\n")

    def reset(self) -> None:
        if self.path.exists():
            self.path.unlink()
