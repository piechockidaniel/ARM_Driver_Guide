# Phase 5 — Add adaptive and context-aware features

Status: Not started

## Goal

Make ARM-Guard more realistic and differentiated by adapting to individual drivers and adjusting alerts based on driving context.

## Context from source doc

A fixed drowsiness threshold can fail across different eye shapes, lighting conditions, glasses, camera positions, and driver behavior. This phase adds adaptive calibration and context-aware alerting.

## Subtasks

- [ ]  Implement quick calibration mode for hackathon demo:
    - 10–15 minute calibration target, or
    - shorter simulated calibration for demo mode
- [ ]  Create anonymous local driver profile storage.
- [ ]  Calculate baseline eye-aspect ratio.
- [ ]  Add rolling baseline updates during alert-free driving.
- [ ]  Add detection confidence score.
- [ ]  Implement dynamic threshold adjustment.
- [ ]  Add context inputs:
    - speed
    - time of day
    - road type or simulator mode
- [ ]  Suppress alerts below a configurable speed threshold.
- [ ]  Increase sensitivity during high-risk late-night windows.
- [ ]  Add a simulated vehicle context file for demos.
- [ ]  Implement progressive alert levels:
    - Level 0 — Normal
    - Level 1 — Gentle
    - Level 2 — Moderate
    - Level 3 — Emergency
- [ ]  Add CLI/dashboard display for current context and alert level.

## Suggested scoring formula

```
drowsiness_score =
  weighted_average(
    normalized_EAR_drop,
    blink_duration_score,
    microsleep_duration_score,
    detection_confidence,
    context_risk_multiplier
  )
```

## Acceptance criteria

- Calibration mode creates or updates an anonymous local profile.
- Alert thresholds adapt to the driver baseline.
- Context inputs influence alert behavior.
- Demo can show alert escalation clearly.

## Deliverables

- Calibration command.
- Anonymous local profile logic.
- Context simulator.
- Alert escalation demo.