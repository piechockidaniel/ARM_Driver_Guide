from __future__ import annotations

import sys


class LiveDependencyError(RuntimeError):
    """Raised when the live CV stack is unavailable."""


def require_live_dependencies() -> tuple[object, object]:
    try:
        import cv2  # type: ignore
        import mediapipe as mp  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on local env
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        raise LiveDependencyError(
            "OpenCV/MediaPipe live mode is unavailable. "
            f"Current interpreter: Python {version}. "
            "Use the project .venv with Python 3.11 and install dependencies from pyproject.toml."
        ) from exc

    return cv2, mp
