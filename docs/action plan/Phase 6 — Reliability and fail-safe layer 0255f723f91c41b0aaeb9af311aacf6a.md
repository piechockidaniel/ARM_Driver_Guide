# Phase 6 — Reliability and fail-safe layer

Status: Not started

## Goal

Add safety-minded system-health monitoring and graceful degradation so the prototype behaves predictably when inputs or hardware conditions are poor.

## Context from source doc

Drowsiness detection is a safety-related workload. The system should identify camera failures, low confidence, low frame rate, resource pressure, and other conditions that reduce reliability.

## Subtasks

- [ ]  Add camera-health monitor.
- [ ]  Detect missing or stale frames.
- [ ]  Track frame rate and flag low-FPS conditions.
- [ ]  Track landmark detection confidence.
- [ ]  Add low-confidence state instead of returning misleading alerts.
- [ ]  Add CPU temperature check where available on Arm Linux.
- [ ]  Add memory usage check.
- [ ]  Add graceful degradation status:
    - normal
    - low confidence
    - camera unavailable
    - performance degraded
- [ ]  Add logs for system-health events.
- [ ]  Add optional fallback-signal concept or simulator:
    - steering irregularity
    - lane drift
    - acceleration/braking irregularity
- [ ]  Document known limitations and failure cases.
- [ ]  Add a demo scenario showing camera failure or low-confidence mode.

## Acceptance criteria

- System detects and reports common failure modes.
- Low-confidence cases are clearly separated from normal drowsiness alerts.
- Health status is visible in CLI/dashboard and logs.
- Documentation explains limitations and safety boundaries.

## Deliverables

- System-health monitor.
- Low-confidence mode.
- Reliability documentation.
- Failure-mode demo scenario.