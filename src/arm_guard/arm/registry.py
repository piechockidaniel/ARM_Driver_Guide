from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from arm_guard.arm.contracts import LandmarkDetectorBackend
from arm_guard.live.mediapipe_backend import MediaPipeFaceMeshBackend


DetectorFactory = Callable[[], LandmarkDetectorBackend]


@dataclass(slots=True, frozen=True)
class DetectorBackendRegistration:
    name: str
    description: str
    factory: DetectorFactory


class DetectorBackendRegistry:
    def __init__(self) -> None:
        self._registrations: dict[str, DetectorBackendRegistration] = {}
        self._default_name: str | None = None

    def register(self, registration: DetectorBackendRegistration, *, default: bool = False) -> None:
        self._registrations[registration.name] = registration
        if default or self._default_name is None:
            self._default_name = registration.name

    def create(self, name: str | None = None) -> LandmarkDetectorBackend:
        backend_name = name or self.default_name
        registration = self._registrations.get(backend_name)
        if registration is None:
            raise KeyError(f"Detector backend '{backend_name}' is not registered.")
        return registration.factory()

    def describe(self) -> list[dict[str, str]]:
        return [
            {
                "name": registration.name,
                "description": registration.description,
                "default": "true" if registration.name == self._default_name else "false",
            }
            for registration in self._registrations.values()
        ]

    @property
    def default_name(self) -> str:
        if self._default_name is None:
            raise RuntimeError("No detector backend is registered.")
        return self._default_name


def build_default_detector_backend_registry(model_path: Path, model_url: str) -> DetectorBackendRegistry:
    registry = DetectorBackendRegistry()
    registry.register(
        DetectorBackendRegistration(
            name="mediapipe-face-landmarker",
            description="MediaPipe Face Landmarker baseline backend with OpenCV frame input.",
            factory=lambda: MediaPipeFaceMeshBackend(model_path=model_path, model_url=model_url),
        ),
        default=True,
    )
    return registry
