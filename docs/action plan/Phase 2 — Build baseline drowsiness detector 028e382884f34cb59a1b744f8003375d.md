# Phase 2 — Build baseline drowsiness detector

Status: Not started

## Goal

Build a functional end-to-end drowsiness detection prototype that can process webcam or video input and produce a drowsiness score, alert level, and performance logs.

## Context from source doc

This phase creates the baseline detector before Arm-specific optimization. It should provide a clear reference implementation that can later be benchmarked against optimized versions.

## Subtasks

- [ ]  Implement webcam input.
- [ ]  Implement video-file input for repeatable demos and tests.
- [ ]  Add face and eye landmark detection.
- [ ]  Compute eye-aspect ratio from eye landmarks.
- [ ]  Detect long blinks.
- [ ]  Detect microsleep-like events based on sustained eye closure.
- [ ]  Create a drowsiness scoring function using:
    - normalized EAR drop
    - blink duration score
    - microsleep duration score
    - detection confidence
- [ ]  Output current status in CLI or a simple dashboard:
    - drowsiness score
    - alert level
    - FPS
    - latency
- [ ]  Log detection events with:
    - timestamp
    - score
    - alert level
    - latency
    - detection confidence
- [ ]  Add basic validation instructions for running the baseline.

## Acceptance criteria

- The baseline demo runs from webcam or a sample video.
- The system computes EAR and outputs drowsiness status.
- The project logs latency and score data.
- The baseline can be used as a reference for later Arm optimization.

## Deliverables

- Working baseline demo.
- Sample output logs.
- Basic validation instructions.
- Reference implementation for benchmark comparison.