from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from arm_guard.domain.models import DetectionFrame
from arm_guard.events.models import AnonymizedDetectionEvent
from arm_guard.live.mediapipe_backend import MediaPipeFaceMeshBackend
from arm_guard.live.sources import OpenCVCaptureSource
from arm_guard.pipeline.engine import ProcessingResult


@dataclass(slots=True, frozen=True)
class LiveFrameResult:
    source_label: str
    frame_rgb: object | None
    processing: ProcessingResult
    end_of_stream: bool = False


class LiveDetectionSession:
    def __init__(self, app: object, source: OpenCVCaptureSource, driver_id: str = "live-driver") -> None:
        self._app = app
        self._source = source
        self._driver_id = driver_id
        self._backend = MediaPipeFaceMeshBackend(
            model_path=app.config.face_landmarker_model_path,
            model_url=app.config.face_landmarker_model_url,
        )
        self._frame_index = 0
        self._opened = False

    def open(self) -> None:
        self._source.open()
        self._opened = True

    def next_frame(self) -> LiveFrameResult:
        if not self._opened:
            self.open()

        ok, frame_bgr, captured_at = self._source.read()
        if not ok or frame_bgr is None:
            return LiveFrameResult(
                source_label=self._source.describe(),
                frame_rgb=None,
                processing=self._app.pipeline.process_missing_detection(
                    driver_id=self._driver_id,
                    captured_at=captured_at,
                    context=self._app.demo_frames.sample_frames()[-1].context,
                    telemetry=self._app.runtime_telemetry(self._frame_index + 1),
                    reason="camera frame unavailable",
                    camera_online=False,
                    fallback_mode=True,
                    stale_frame_seconds=float(self._app.config.camera_stale_seconds + 1),
                ),
                end_of_stream=True,
            )

        self._frame_index += 1
        telemetry = self._app.runtime_telemetry(self._frame_index)
        observation = self._backend.detect(
            frame_bgr,
            timestamp_ms=int(captured_at.timestamp() * 1000),
        )

        if observation is None:
            processing = self._app.pipeline.process_missing_detection(
                driver_id=self._driver_id,
                captured_at=captured_at,
                context=self._app.demo_frames.sample_frames()[-1].context,
                telemetry=telemetry,
                reason="face or eye landmarks not detected",
            )
        else:
            reference = self._app.demo_frames.sample_frames()[-1]
            frame = DetectionFrame(
                frame_id=self._frame_index,
                driver_id=self._driver_id,
                left_eye=observation.left_eye,
                right_eye=observation.right_eye,
                captured_at=captured_at,
                context=reference.context,
                detection_confidence=observation.detection_confidence,
                telemetry=telemetry,
            )
            processing = self._app.pipeline.process(frame)
            self._app.event_logger.append(self._event_for(frame, processing))

        frame_bgr = self._backend.draw_overlay(frame_bgr, observation)
        cv2, _ = self._app.require_live_dependencies()
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return LiveFrameResult(
            source_label=self._source.describe(),
            frame_rgb=frame_rgb,
            processing=processing,
        )

    def close(self) -> None:
        self._backend.close()
        self._source.release()
        self._opened = False

    def _event_for(self, frame: DetectionFrame, result: ProcessingResult) -> AnonymizedDetectionEvent:
        return AnonymizedDetectionEvent(
            timestamp=frame.captured_at.isoformat(),
            driver_profile_id=self._app.profiler.anonymous_profile_id(frame.driver_id),
            drowsiness_score=result.assessment.drowsiness_score,
            alert_level=result.alert.level.value,
            vehicle_speed_kph=frame.context.speed_kph,
            raw_frame_stored=False if self._app.config.privacy_mode else self._app.config.store_raw_frames,
            system_status=result.health.status.value,
            latency_ms=result.health.latency_ms,
            detection_confidence=result.assessment.confidence,
        )
