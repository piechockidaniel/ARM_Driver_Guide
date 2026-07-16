from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from arm_guard.live import LiveDependencyError, LiveDetectionSession, OpenCVCaptureSource


class ArmGuardDashboard:
    def __init__(self, app: object) -> None:
        self._app = app
        self._session: LiveDetectionSession | None = None
        self._after_id: str | None = None
        self._photo: ImageTk.PhotoImage | None = None

        self.root = tk.Tk()
        self.root.title("ARM-Guard Baseline Dashboard")
        self.root.geometry("1180x780")
        self.root.configure(bg="#ecf1f7")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_layout()

    def run(self) -> int:
        self.root.mainloop()
        return 0

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x")
        ttk.Label(header, text="ARM-Guard", font=("Segoe UI", 26, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Phase 2 baseline detector with OpenCV + MediaPipe + Tkinter dashboard",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(4, 12))

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(0, 12))
        ttk.Button(controls, text="Start Webcam", command=self._start_webcam).pack(side="left")
        ttk.Button(controls, text="Open Video", command=self._open_video).pack(side="left", padx=8)
        ttk.Button(controls, text="Stop", command=self._stop_session).pack(side="left")

        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)

        self.frame_label = ttk.Label(body)
        self.frame_label.pack(side="left", fill="both", expand=True)

        side = ttk.Frame(body, padding=(16, 0, 0, 0))
        side.pack(side="right", fill="y")

        self.source_var = tk.StringVar(value="source: idle")
        self.score_var = tk.StringVar(value="score: -")
        self.alert_var = tk.StringVar(value="alert: -")
        self.status_var = tk.StringVar(value="status: -")
        self.ear_var = tk.StringVar(value="ear: -")
        self.fps_var = tk.StringVar(value="fps: -")
        self.latency_var = tk.StringVar(value="latency: -")
        self.reason_var = tk.StringVar(value="reason: waiting for input")

        for variable in (
            self.source_var,
            self.score_var,
            self.alert_var,
            self.status_var,
            self.ear_var,
            self.fps_var,
            self.latency_var,
            self.reason_var,
        ):
            ttk.Label(side, textvariable=variable, font=("Segoe UI", 12), wraplength=280, justify="left").pack(
                anchor="w",
                pady=4,
            )

    def _start_webcam(self) -> None:
        self._start_session(OpenCVCaptureSource(self._app.config.default_camera_index))

    def _open_video(self) -> None:
        path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")],
        )
        if path:
            self._start_session(OpenCVCaptureSource(Path(path).as_posix()))

    def _start_session(self, source: OpenCVCaptureSource) -> None:
        self._stop_session()
        self._app.event_logger.reset()
        try:
            self._session = LiveDetectionSession(self._app, source)
            self._session.open()
            self._tick()
        except LiveDependencyError as exc:
            messagebox.showerror("ARM-Guard", str(exc))
            self._session = None

    def _tick(self) -> None:
        if self._session is None:
            return

        result = self._session.next_frame()
        self._update_status(result)
        self._draw_frame(result.frame_rgb)

        if result.end_of_stream:
            self._stop_session()
            return

        self._after_id = self.root.after(self._app.config.gui_refresh_ms, self._tick)

    def _update_status(self, result: object) -> None:
        processing = result.processing
        self.source_var.set(f"source: {result.source_label}")
        self.score_var.set(f"score: {processing.assessment.drowsiness_score:.3f}")
        self.alert_var.set(f"alert: {processing.alert.level.value}")
        self.status_var.set(f"status: {processing.health.status.value}")
        self.ear_var.set(f"ear: {processing.assessment.ear:.3f}")
        self.fps_var.set(f"fps: {processing.health.capture_fps:.1f}")
        self.latency_var.set(f"latency: {processing.health.latency_ms:.3f} ms")
        reasons = ", ".join(processing.assessment.reasons) if processing.assessment.reasons else "no active reasons"
        self.reason_var.set(f"reason: {reasons}")

    def _draw_frame(self, frame_rgb: object | None) -> None:
        if frame_rgb is None:
            self.frame_label.configure(image="", text="No frame available")
            return

        image = Image.fromarray(frame_rgb)
        image.thumbnail((820, 640))
        self._photo = ImageTk.PhotoImage(image)
        self.frame_label.configure(image=self._photo, text="")

    def _stop_session(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        if self._session is not None:
            self._session.close()
            self._session = None

    def _on_close(self) -> None:
        self._stop_session()
        self.root.destroy()


def run_dashboard(app: object) -> int:
    dashboard = ArmGuardDashboard(app)
    return dashboard.run()
