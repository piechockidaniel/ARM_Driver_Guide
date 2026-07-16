from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import numpy as np

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


@dataclass(slots=True)
class Esp32HttpCaptureSource:
    source: str
    capture_path: str = "/capture"
    timeout_seconds: float = 5.0

    def open(self) -> None:
        require_live_dependencies()
        parsed = urlparse(self.source)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise LiveDependencyError(
                "ESP32-CAM source must be a full base URL, for example http://192.168.4.1"
            )

    def read(self) -> tuple[bool, object | None, datetime]:
        cv2, _ = require_live_dependencies()
        request = Request(self._capture_url, headers={"User-Agent": "ARM-Guard/0.1"})
        captured_at = datetime.now(timezone.utc)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read()
        except (HTTPError, URLError, OSError):
            return False, None, captured_at

        frame = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return False, None, captured_at
        return True, frame, captured_at

    def describe(self) -> str:
        parsed = urlparse(self.source)
        host = parsed.netloc or self.source
        return f"esp32-cam:{host}"

    def release(self) -> None:
        return None

    @property
    def _capture_url(self) -> str:
        return f"{self.source.rstrip('/')}/{self.capture_path.lstrip('/')}"
