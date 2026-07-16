from __future__ import annotations

from math import hypot

from arm_guard.domain.models import Point


class PrivacyPreservingEarEstimator:
    """Calculates ratios only and exposes no raw-image persistence surface."""

    def calculate(self, eye: tuple[Point, Point, Point, Point, Point, Point]) -> float:
        p1, p2, p3, p4, p5, p6 = eye
        vertical_a = self._distance(p2, p6)
        vertical_b = self._distance(p3, p5)
        horizontal = self._distance(p1, p4)

        if horizontal == 0:
            raise ValueError("Eye landmark horizontal distance cannot be zero.")

        return (vertical_a + vertical_b) / (2 * horizontal)

    def calculate_average(
        self,
        left_eye: tuple[Point, Point, Point, Point, Point, Point],
        right_eye: tuple[Point, Point, Point, Point, Point, Point],
    ) -> float:
        return (self.calculate(left_eye) + self.calculate(right_eye)) / 2

    @staticmethod
    def _distance(a: Point, b: Point) -> float:
        return hypot(a[0] - b[0], a[1] - b[1])
