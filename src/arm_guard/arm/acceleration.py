from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ArmAccelerationProfile:
    target_cpu: str = "Cortex-A76"
    neon_enabled: bool = True
    mali_gpu_enabled: bool = False
    trustzone_enabled: bool = False
    pmu_feedback_enabled: bool = False

    def summary(self) -> str:
        flags = []
        if self.neon_enabled:
            flags.append("NEON")
        if self.mali_gpu_enabled:
            flags.append("Mali GPU")
        if self.trustzone_enabled:
            flags.append("TrustZone")
        if self.pmu_feedback_enabled:
            flags.append("PMU feedback")

        backend = ", ".join(flags) if flags else "portable Python"
        return f"{self.target_cpu} profile using {backend}"
