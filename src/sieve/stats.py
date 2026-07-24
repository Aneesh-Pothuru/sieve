from __future__ import annotations

import math

from .models import Interval


def wilson(failures: int, trials: int, z: float = 1.959963984540054) -> Interval:
    if trials < 0 or failures < 0 or failures > trials:
        raise ValueError("require 0 <= failures <= trials")
    if trials == 0:
        return Interval(0.0, 0.0, 1.0, failures, trials)
    rate = failures / trials
    denominator = 1 + z * z / trials
    center = (rate + z * z / (2 * trials)) / denominator
    margin = (
        z
        * math.sqrt(rate * (1 - rate) / trials + z * z / (4 * trials * trials))
        / denominator
    )
    return Interval(rate, max(0.0, center - margin), min(1.0, center + margin), failures, trials)


def trust_adjusted_band(
    reported_score: float, fp_affected: float, fn_affected: float, invalid: float
) -> tuple[float, float]:
    if not all(0.0 <= value <= 1.0 for value in (reported_score, fp_affected, fn_affected, invalid)):
        raise ValueError("band inputs must be fractions in [0, 1]")
    low = max(0.0, reported_score - fp_affected - invalid / 2)
    high = min(1.0, reported_score + fn_affected + invalid / 2)
    return round(low, 10), round(high, 10)

