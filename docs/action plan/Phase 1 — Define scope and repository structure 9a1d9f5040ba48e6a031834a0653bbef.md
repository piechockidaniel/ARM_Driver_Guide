# Phase 1 — Define scope and repository structure

Status: Not started

## Goal

Create a submission-ready foundation for ARM-Guard so the project is easy to understand, build, validate, and submit for the Arm AI Optimization Challenge.

## Context from source doc

This phase establishes the public repository, license, README, project structure, architecture diagram, dependency notes, and target Arm64 device/environment.

## Subtasks

- [ ]  Choose the final Arm64 target device or environment:
    - Raspberry Pi 5
    - Arm-based laptop
    - Arm cloud instance
    - Jetson Orin Nano or another Arm-powered edge device
    - Orange Pi 5 Plus
- [ ]  Create a public GitHub repository for ARM-Guard.
- [ ]  Add an open-source license:
    - MIT, or
    - Apache 2.0
- [ ]  Add the initial README with:
    - Project pitch
    - Selected challenge track: Track 1 — Optimization output
    - Short problem statement
    - Target Arm64 platform
    - Setup outline
    - Demo expectations
- [ ]  Create the initial repository folders:
    - `src/`
    - `benchmarks/`
    - `docs/`
    - `demo/`
    - `tests/`
    - `assets/`
- [ ]  Add a high-level technical architecture diagram.
- [ ]  Document third-party dependencies and licenses.
- [ ]  Add a “significant updates during submission period” section if any pre-existing work is reused.

## Acceptance criteria

- Public repository exists and is accessible.
- License file is visible at the top level of the repository.
- README explains what ARM-Guard is, why it fits the challenge, and how it will be validated on Arm64.
- Repository structure is ready for implementation.
- Dependencies and license notes are documented.

## Deliverables

- Public repo.
- License file.
- Initial README.
- Architecture diagram.
- Dependency/license notes.