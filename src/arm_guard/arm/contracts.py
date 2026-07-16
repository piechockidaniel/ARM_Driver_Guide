from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CaptureBackend(Protocol):
    source: int | str

    def open(self) -> None: ...

    def read(self) -> tuple[bool, Any | None, datetime]: ...

    def describe(self) -> str: ...

    def release(self) -> None: ...


@runtime_checkable
class LandmarkDetectorBackend(Protocol):
    @property
    def backend_name(self) -> str: ...

    def detect(self, frame_bgr: Any, *, timestamp_ms: int) -> Any | None: ...

    def draw_overlay(self, frame_bgr: Any, observation: Any | None) -> Any: ...

    def close(self) -> None: ...
