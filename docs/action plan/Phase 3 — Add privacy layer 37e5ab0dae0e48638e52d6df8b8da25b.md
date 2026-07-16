# Phase 3 — Add privacy layer

Status: Not started

## Goal

Make ARM-Guard’s privacy claims concrete, testable, and visible in the demo and documentation.

## Context from source doc

ARM-Guard should process video locally, extract only geometric eye/landmark measurements, discard raw frames, and store only anonymized event metadata.

## Subtasks

- [ ]  Ensure raw frames are not persisted by default.
- [ ]  Add a `privacy_mode` configuration option.
- [ ]  Disable image/frame export when privacy mode is enabled.
- [ ]  Store only anonymized event metadata:
    - timestamp
    - anonymous local driver profile ID
    - drowsiness score
    - alert level
    - vehicle speed or simulated context
    - raw frame stored flag
- [ ]  Implement or document immediate raw-frame disposal after feature extraction.
- [ ]  Add event schema documentation.
- [ ]  Add a data-retention note for local logs.
- [ ]  Add a deletion procedure for stored local profile/event data.
- [ ]  Add a unit test or demo assertion showing `raw_frame_stored = false`.
- [ ]  Avoid overclaiming formal GDPR / CCPA compliance unless formally validated; describe these as privacy-supporting design choices.

## Recommended event schema

```json
{
  "timestamp": "2026-08-20T12:30:00Z",
  "driver_profile_id": "anonymous-local-id",
  "drowsiness_score": 0.82,
  "alert_level": "moderate",
  "vehicle_speed_kph": 74,
  "raw_frame_stored": false
}
```

## Acceptance criteria

- Privacy mode is implemented and documented.
- Raw frames are not saved during normal operation.
- Logs contain only anonymized event metadata.
- A test or demo proves privacy mode behavior.

## Deliverables

- Privacy mode.
- Event schema.
- Privacy documentation.
- Raw-frame discard validation.