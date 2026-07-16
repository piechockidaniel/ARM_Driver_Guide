from __future__ import annotations

from dataclasses import dataclass

from arm_guard.domain.models import DriverContext


@dataclass(slots=True, frozen=True)
class ConsentManager:
    require_explicit_opt_in: bool = True

    def can_process(self, context: DriverContext) -> bool:
        if not self.require_explicit_opt_in:
            return True
        return context.consent_granted
