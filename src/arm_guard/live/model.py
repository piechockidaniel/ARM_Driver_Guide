from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

from arm_guard.live.deps import LiveDependencyError


def ensure_face_landmarker_model(model_path: Path, model_url: str) -> Path:
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(model_url, timeout=60) as response:
            model_path.write_bytes(response.read())
    except Exception as exc:  # pragma: no cover - network dependent
        raise LiveDependencyError(
            f"Unable to download MediaPipe Face Landmarker model to {model_path}. "
            f"Source URL: {model_url}"
        ) from exc

    return model_path
