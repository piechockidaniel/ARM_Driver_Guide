from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from arm_guard.domain.models import Point
from arm_guard.live.deps import require_live_dependencies
from arm_guard.live.model import ensure_face_landmarker_model


LEFT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
RIGHT_EYE_INDICES = (362, 385, 387, 263, 373, 380)


@dataclass(slots=True, frozen=True)
class LandmarkObservation:
    left_eye: tuple[Point, Point, Point, Point, Point, Point]
    right_eye: tuple[Point, Point, Point, Point, Point, Point]
    detection_confidence: float
    overlay_points: tuple[Point, ...]


class MediaPipeFaceMeshBackend:
    def __init__(self, *, model_path: Path, model_url: str) -> None:
        _, mp = require_live_dependencies()
        self._mp = mp
        resolved_model_path = ensure_face_landmarker_model(model_path, model_url)
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(resolved_model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._mesh = mp.tasks.vision.FaceLandmarker.create_from_options(options)

    @property
    def backend_name(self) -> str:
        return "mediapipe-face-landmarker"

    def detect(self, frame_bgr: object, *, timestamp_ms: int) -> LandmarkObservation | None:
        cv2, _ = require_live_dependencies()
        image_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=image_rgb)
        results = self._mesh.detect_for_video(mp_image, timestamp_ms)
        if not results.face_landmarks:
            return None

        face = results.face_landmarks[0]
        height, width = frame_bgr.shape[:2]
        left_eye = self._points(face, LEFT_EYE_INDICES, width, height)
        right_eye = self._points(face, RIGHT_EYE_INDICES, width, height)
        overlay_points = tuple(left_eye + right_eye)

        return LandmarkObservation(
            left_eye=tuple(left_eye),  # type: ignore[arg-type]
            right_eye=tuple(right_eye),  # type: ignore[arg-type]
            detection_confidence=0.92,
            overlay_points=overlay_points,
        )

    def draw_overlay(self, frame_bgr: object, observation: LandmarkObservation | None) -> object:
        cv2, _ = require_live_dependencies()
        if observation is None:
            return frame_bgr

        for x, y in observation.overlay_points:
            cv2.circle(frame_bgr, (int(x), int(y)), 2, (0, 255, 0), -1)

        return frame_bgr

    def close(self) -> None:
        self._mesh.close()

    @staticmethod
    def _points(face: object, indices: tuple[int, ...], width: int, height: int) -> list[Point]:
        points: list[Point] = []
        for index in indices:
            landmark = face.landmark[index]
            points.append((landmark.x * width, landmark.y * height))
        return points
