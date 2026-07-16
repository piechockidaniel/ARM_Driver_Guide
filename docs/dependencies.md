# Dependency Notes

Current runtime dependencies:

- Python 3.11
- OpenCV
- MediaPipe
- Pillow

Current constraint:

- The live CV path is validated for the local `.venv` on Python 3.11.
- The current workspace-global interpreter is Python 3.13 and is not the supported path for MediaPipe here.

Reason:

This phase moves the project into a real baseline detector with webcam/video input and landmark detection. ONNX/TFLite and Arm-specific optimization are intentionally deferred to later phases.
