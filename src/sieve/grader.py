from __future__ import annotations

from typing import Any


def grade(configuration: dict[str, Any], answer: Any) -> bool:
    mode = configuration.get("mode", "exact")
    expected = configuration.get("expected")
    if mode == "always_pass":
        return True
    if answer is None:
        return False
    if mode == "exact":
        return answer == expected
    if mode == "normalized":
        return str(answer).strip().casefold() == str(expected).strip().casefold()
    if mode == "accept_empty_diff":
        return answer == expected or answer == ""
    if mode == "weak_allowlist":
        return answer == expected or answer in configuration.get("accepted_wrong", [])
    raise ValueError(f"unknown grader mode: {mode}")

