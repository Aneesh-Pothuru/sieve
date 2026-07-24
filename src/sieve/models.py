from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuditTask:
    id: str
    prompt: str
    oracle: Any
    grader: dict[str, Any]
    correct_variants: list[Any]
    wrong_mutations: list[Any]
    label_review: bool = False
    evidence_tier: str = "declared-oracle"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Interval:
    rate: float
    low: float
    high: float
    failures: int
    trials: int


@dataclass(frozen=True)
class Finding:
    task_id: str
    verdict: str
    severity: str
    detail: str
    reproducer: str
    evidence_tier: str
    secondary: tuple[str, ...] = ()
    fp_lower_bound: bool = False


@dataclass
class AuditResult:
    suite_name: str
    task_count: int
    findings: list[Finding]
    grader_rates: dict[str, dict[str, Interval]]
    budget: dict[str, Any]
    trust_band: dict[str, float]
    abstention_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["findings"] = [asdict(item) for item in self.findings]
        return payload

