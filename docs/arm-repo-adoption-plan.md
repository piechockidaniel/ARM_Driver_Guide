# ARM Repository Adoption Plan

## Purpose

This document translates the ARM GitHub repository recommendation into a concrete adoption plan for the current ARM-Guard codebase.

The goal is not to import many ARM repositories into the project. The goal is to use only the repositories that improve:

- Arm64 reproducibility
- benchmark credibility
- optimization evidence
- code architecture for future optimized backends

## Current project reality

As of July 16, 2026, ARM-Guard is:

- a Python project
- targeted at `Orange Pi 5 Plus / RK3588`
- running on `Arm64 Linux / Cortex-A class hardware`
- using `OpenCV + MediaPipe` for the current baseline detector
- using local GUI, simulated telemetry, and benchmark hooks

This matters because it excludes several ARM repositories from the first implementation wave:

- no Cortex-M first target
- no Ethos hardware target
- no RTOS-first architecture
- no immediate need for microcontroller-only NN kernels

## Decision summary

### Adopt now

1. `Tool-Solutions`
2. `ComputeLibrary`
3. `CMSIS-DSP`

### Adopt as architecture reference, not runtime dependency

1. `CMSIS-Stream`
2. `AVH`

### Adopt only if the project moves to model inference

1. `Arm NN`

### Defer unless target scope changes

1. `CMSIS-NN`
2. `CMSIS_6`
3. `open-iot-sdk`
4. `Ethos-*`

## Repository-by-repository plan

### 1. Tool-Solutions

Status:
`Adopt now`

Why:
- strongest match for reproducible AArch64 setup
- useful for build notes, packaging, and benchmark reproducibility
- helps Phase 1, Phase 4, and Phase 7 without changing core detector logic

How we should use it:
- as a reference for Arm64 environment setup
- as a pattern for reproducible build and run instructions
- optionally as inspiration for a containerized Arm64 benchmark environment

Do not do:
- do not vendor the repo into ARM-Guard
- do not couple core detector runtime to Tool-Solutions scripts

Code/repo touchpoints:
- [README.md](/C:/Users/user/source/repos/ARM_Driver_Guide/README.md)
- [docs/dependencies.md](/C:/Users/user/source/repos/ARM_Driver_Guide/docs/dependencies.md)
- future `docs/arm64-setup.md`
- future `scripts/` or `tools/` for reproducible benchmark setup

Deliverable:
- dedicated Arm64 setup guide for Orange Pi and AArch64 validation path

### 2. ComputeLibrary

Status:
`Adopt now, but only as an optimization track`

Why:
- best match for the project’s Cortex-A / Arm64 optimization story
- directly supports the claim that ARM-Guard is optimized for Arm, not merely portable
- fits the planned benchmark table and optimized-path comparison

How we should use it:
- as a reference for optimized CPU/GPU implementation patterns
- as a basis for a separate native or accelerated backend experiment
- as evidence for Phase 4 benchmark and optimization notes

Do not do:
- do not replace the Python baseline
- do not hard-wire ComputeLibrary into the main GUI path before benchmark evidence exists
- do not let optimization work destabilize the current baseline detector

Code/repo touchpoints:
- [src/arm_guard/arm](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/arm)
- [benchmarks/run_demo_benchmark.py](/C:/Users/user/source/repos/ARM_Driver_Guide/benchmarks/run_demo_benchmark.py)
- future `benchmarks/compare_backends.py`
- future native extension folder such as `native/` or `src/arm_guard_native/`

Deliverable:
- benchmarkable comparison between:
  - baseline Python path
  - optimized NumPy/OpenCV path
  - Arm-optimized path inspired by ComputeLibrary

### 3. CMSIS-DSP

Status:
`Adopt now`

Why:
- useful for low-level math and feature-processing structure
- relevant even on Cortex-A when the project needs efficient statistics, filtering, or feature transforms
- lower-risk than introducing a whole inference backend

How we should use it:
- as a design reference for optimized feature processing
- as inspiration for extracting math-heavy sections into a backend-friendly layer
- potentially as a comparison point for future native kernels

Do not do:
- do not force embedded-style abstractions into every Python path
- do not treat CMSIS-DSP as a drop-in answer to the whole pipeline

Code/repo touchpoints:
- [src/arm_guard/pipeline/scoring.py](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/pipeline/scoring.py)
- [src/arm_guard/pipeline/ear.py](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/pipeline/ear.py)
- future `src/arm_guard/arm/math_backends.py`

Deliverable:
- clear separation between algorithm definition and math backend implementation

### 4. CMSIS-Stream

Status:
`Reference only for now`

Why:
- current project already has a streaming shape
- useful for formalizing the pipeline
- could improve maintainability before low-level optimization begins

How we should use it:
- as architecture inspiration
- to structure pipeline stages explicitly:
  - capture
  - landmark extraction
  - EAR estimation
  - drowsiness scoring
  - alerting
  - logging

Code/repo touchpoints:
- [src/arm_guard/live](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/live)
- [src/arm_guard/pipeline](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/pipeline)
- [src/arm_guard/runtime.py](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/runtime.py)

Deliverable:
- explicit backend interfaces and stage boundaries

### 5. Arm NN

Status:
`Conditional`

Why:
- only becomes valuable if ARM-Guard gains a true neural inference path
- not needed for the current EAR + landmark baseline

When to adopt:
- if we add a learned drowsiness classifier
- if we introduce TFLite or ONNX inference as a second detector path
- if benchmark goals require comparing rules vs neural inference

Code/repo touchpoints:
- future `src/arm_guard/inference/`
- future model asset folder
- benchmark comparison scripts

Deliverable:
- optional model-based detector backend for later benchmark comparison

### 6. AVH

Status:
`Reference only, optional later`

Why:
- useful for reproducibility and CI storytelling
- less useful for real camera/video performance validation on Orange Pi

When to adopt:
- when we need CI-friendly “Arm route” documentation
- when the submission needs a virtual validation supplement

Do not do:
- do not treat AVH as a substitute for real Orange Pi validation

### 7. CMSIS-NN

Status:
`Deferred`

Why:
- optimized for Cortex-M and quantized microcontroller inference
- current project target is Cortex-A / Linux / Orange Pi

Adopt only if:
- the scope expands to TinyML or a secondary microcontroller build

### 8. CMSIS_6

Status:
`Deferred`

Why:
- useful for embedded conventions and documentation patterns
- not an immediate implementation dependency for the current Linux edge target

### 9. open-iot-sdk

Status:
`Deferred`

Why:
- too broad for the current detector-first objective
- more useful if the project becomes a broader edge/IoT product stack

### 10. Ethos driver stacks

Status:
`Not applicable to current hardware`

Why:
- current target device is `RK3588`, not Arm Ethos hardware

Revisit only if:
- hardware target changes
- a separate Arm NPU path is introduced

## Recommended implementation order

### Wave 1: architecture hardening

Goal:
make the current codebase ready for optimized backends without changing the user-visible baseline

Tasks:
1. Split the live detector into explicit backend interfaces:
   - capture backend
   - landmark backend
   - feature backend
   - alert backend
2. Move Arm-specific hooks out of the generic runtime path.
3. Introduce a backend registry under `src/arm_guard/arm/`.
4. Keep the current OpenCV + MediaPipe path as the default baseline.

Files most likely to change:
- [src/arm_guard/live](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/live)
- [src/arm_guard/pipeline](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/pipeline)
- [src/arm_guard/runtime.py](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/runtime.py)
- [src/arm_guard/arm](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/arm)

Success criteria:
- the code can swap backend implementations without rewriting GUI or logging

### Wave 2: reproducible Arm64 setup

Goal:
improve credibility and reproducibility before deep optimization work

Tasks:
1. Add `docs/arm64-setup.md`.
2. Document Orange Pi runtime dependencies separately from Windows dev dependencies.
3. Add a repeatable install path for AArch64 based on Tool-Solutions ideas.
4. Add benchmark execution instructions targeted at Orange Pi.

Files most likely to change:
- [README.md](/C:/Users/user/source/repos/ARM_Driver_Guide/README.md)
- [docs/dependencies.md](/C:/Users/user/source/repos/ARM_Driver_Guide/docs/dependencies.md)
- new `docs/arm64-setup.md`

Success criteria:
- a third party can reproduce the baseline on Arm64 without guesswork

### Wave 3: benchmark harness

Goal:
prepare the project for meaningful optimization claims

Tasks:
1. Separate benchmark logic from demo logic.
2. Record:
   - average latency
   - P95 latency
   - FPS
   - CPU usage
   - memory usage
3. Add backend labels to results.
4. Reserve comparison rows for future optimized backends.

Files most likely to change:
- [benchmarks/run_demo_benchmark.py](/C:/Users/user/source/repos/ARM_Driver_Guide/benchmarks/run_demo_benchmark.py)
- [src/arm_guard/runtime.py](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/runtime.py)
- future benchmark scripts

Success criteria:
- a baseline benchmark table exists before any Arm optimization branch lands

### Wave 4: first Arm-specific optimization path

Goal:
add one experimental optimized backend without destabilizing the baseline detector

Tasks:
1. Identify the smallest hot path worth accelerating.
   Recommended candidates:
   - EAR computation
   - rolling statistics / score computation
   - frame pre-processing
2. Build an isolated accelerated backend prototype.
3. Compare it against baseline with the benchmark harness.
4. Document gains and tradeoffs.

Repository references:
- `ComputeLibrary`
- `CMSIS-DSP`

Files most likely to change:
- [src/arm_guard/arm](/C:/Users/user/source/repos/ARM_Driver_Guide/src/arm_guard/arm)
- future native extension directory
- benchmark reporting docs

Success criteria:
- one measurable optimization result on Arm64 hardware

### Wave 5: optional model inference path

Goal:
add a second detector path only if it improves the project story

Tasks:
1. Decide whether the project needs a learned drowsiness model.
2. If yes, create a new inference layer instead of mixing it into the EAR baseline.
3. Evaluate `Arm NN` only after the model format is chosen.

Success criteria:
- no model path is added unless it is benchmarkable and justifiable

## Required code changes before optimization work

These are structural prerequisites, not optional cleanup:

1. Introduce backend interfaces in `src/arm_guard/arm/`.
2. Stop treating optimization as a property of the generic runtime.
3. Add backend-aware benchmark output.
4. Keep current baseline detector as the control group.

## What should not happen

1. Do not add five ARM repositories as git submodules.
2. Do not replace the working Python baseline with an unproven native path.
3. Do not introduce Cortex-M-specific code into the main Orange Pi track.
4. Do not claim Arm optimization before benchmark evidence exists.
5. Do not add `Arm NN` before there is a real model inference problem to solve.

## Recommended next concrete task

The next implementation step should be:

`Refactor the current runtime into explicit detector backends and prepare a benchmark comparison harness.`

That gives the project the structure needed for:

- Tool-Solutions-style reproducibility work
- ComputeLibrary-inspired optimization work
- CMSIS-DSP-style math backend work

without destabilizing the current GUI and baseline detector.
