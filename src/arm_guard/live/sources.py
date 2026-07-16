from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from arm_guard.live.deps import LiveDependencyError, require_live_dependencies


@dataclass(slots=True)
class OpenCVCaptureSource:
    source: int | str
    capture: object | None = None

    def open(self) -> None:
        cv2, _ = require_live_dependencies()
        resolved_source: int | str = self.source
        if isinstance(self.source, str) and self.source.isdigit():
            resolved_source = int(self.source)

        self.capture = cv2.VideoCapture(resolved_source)
        if not self.capture or not self.capture.isOpened():
            raise LiveDependencyError(f"Unable to open capture source: {self.source}")

    def read(self) -> tuple[bool, object | None, datetime]:
        if self.capture is None:
            raise RuntimeError("Capture source is not open.")

        ok, frame = self.capture.read()
        return ok, frame if ok else None, datetime.now(timezone.utc)

    def describe(self) -> str:
        if isinstance(self.source, int):
            return f"webcam:{self.source}"
        if Path(self.source).exists():
            return Path(self.source).name
        return str(self.source)

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None
