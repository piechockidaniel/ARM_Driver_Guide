# Phase 4 — Optimize for Arm

Status: Not started

## Goal

Demonstrate measurable Arm-specific performance improvement and produce reusable optimization artifacts for the challenge submission.

## Context from source doc

The project should show that ARM-Guard is built and optimized for Arm64, not merely compatible with Arm. This phase supports the challenge’s Technological Implementation judging category.

## Subtasks

- [ ]  Profile baseline latency on Arm64.
- [ ]  Profile baseline CPU usage and memory usage.
- [ ]  Add benchmark script for repeatable runs.
- [ ]  Measure:
    - average latency
    - P95 latency
    - FPS
    - CPU utilization
    - memory usage
    - estimated power draw or battery impact, if available
- [ ]  Vectorize numeric operations where possible.
- [ ]  Optimize OpenCV / NumPy processing paths.
- [ ]  Add optional C/C++ or Rust extension for EAR computation.
- [ ]  Use NEON intrinsics where practical.
- [ ]  Add build instructions for the optimized extension.
- [ ]  Compare:
    - baseline Python path
    - optimized NumPy/OpenCV path
    - NEON/Arm64 optimized path
    - optional TFLite/ONNX Arm path
- [ ]  Document optimization decisions and tradeoffs.
- [ ]  Capture benchmark results in a table for README/Devpost.

## Benchmark table to complete

| Configuration | Avg latency | P95 latency | FPS | CPU use | Notes |
| --- | --- | --- | --- | --- | --- |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline Python | TBD | TBD | TBD | TBD | Reference implementation |
| Optimized NumPy/OpenCV | TBD | TBD | TBD | TBD | Vectorized processing |
| NEON/Arm64 optimized | TBD | TBD | TBD | TBD | Target submission result |
| TFLite/ONNX Arm path | TBD | TBD | TBD | TBD | Optional model path |

## Acceptance criteria

- Benchmarks run on Arm64.
- Results show baseline vs optimized performance.
- Optimization work is documented.
- Judges can reproduce the benchmark.

## Deliverables

- Benchmark script.
- Benchmark table.
- Optimization notes.
- Reusable Arm64 build instructions.