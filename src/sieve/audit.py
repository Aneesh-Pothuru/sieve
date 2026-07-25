from __future__ import annotations

from dataclasses import dataclass
import shlex
from typing import Any

from .grader import grade
from .models import AuditResult, AuditTask, Finding
from .stats import trust_adjusted_band, wilson


@dataclass
class Budget:
    limit: int
    used: int = 0
    skipped: int = 0

    def run(self, grader: dict[str, Any], answer: Any) -> bool | None:
        if self.used >= self.limit:
            self.skipped += 1
            return None
        self.used += 1
        return grade(grader, answer)


def _finding(
    task: AuditTask,
    verdict: str,
    detail: str,
    severity: str = "high",
    secondary: tuple[str, ...] = (),
    fp_lower_bound: bool = False,
    suite_reference: str = ".",
) -> Finding:
    return Finding(
        task_id=task.id,
        verdict=verdict,
        severity=severity,
        detail=detail,
        reproducer=(
            f"sieve audit {shlex.quote(suite_reference)} "
            f"--task {shlex.quote(task.id)}"
        ),
        evidence_tier=task.evidence_tier,
        secondary=secondary,
        fp_lower_bound=fp_lower_bound,
    )


def audit_suite(
    suite_name: str,
    tasks: list[AuditTask],
    budget_limit: int = 200,
    reported_score: float = 0.80,
    suite_reference: str | None = None,
) -> AuditResult:
    budget = Budget(budget_limit)
    reproducer_suite = (
        suite_reference
        if suite_reference is not None
        else "flawedbench" if suite_name == "FlawedBench" else "."
    )
    findings: list[Finding] = []
    rates = {}
    red_flags: list[dict[str, str]] = []
    oracle_undetermined = 0
    prompts: dict[str, list[str]] = {}
    for task in tasks:
        prompts.setdefault(task.prompt.strip().casefold(), []).append(task.id)

    for task in tasks:
        existing: Finding | None = None
        if len(prompts[task.prompt.strip().casefold()]) > 1:
            existing = _finding(
                task,
                "TASK_DEGENERATE",
                "duplicate normalized prompt",
                "medium",
                suite_reference=reproducer_suite,
            )
            red_flags.append({"task_id": task.id, "flag": "duplicate_prompt"})
        if task.grader.get("mode") == "always_pass":
            red_flags.append({"task_id": task.id, "flag": "accepts_anything"})
        history = task.metadata.get("pass_history", [])
        if history and all(bool(value) for value in history):
            red_flags.append({"task_id": task.id, "flag": "100_percent_pass"})
        if history and not any(bool(value) for value in history):
            red_flags.append({"task_id": task.id, "flag": "0_percent_pass"})

        oracle_available = task.metadata.get("oracle_available", task.oracle is not None)
        if oracle_available:
            oracle_result = budget.run(task.grader, task.oracle)
        else:
            oracle_result = None
            oracle_undetermined += 1
        if oracle_result is False:
            if task.label_review:
                existing = _finding(
                    task,
                    "GRADER_FN",
                    "trusted oracle answer rejected; keyed answer is a label-error candidate",
                    secondary=("LABEL_ERROR",),
                    suite_reference=reproducer_suite,
                )
            else:
                existing = _finding(
                    task,
                    "TASK_UNSOLVABLE",
                    "declared oracle solution rejected by the grader",
                    suite_reference=reproducer_suite,
                )

        null_answers = [None, "I cannot help", task.prompt]
        null_results = [budget.run(task.grader, answer) for answer in null_answers]
        accepted_nulls = sum(result is True for result in null_results)
        if accepted_nulls and existing is None:
            existing = _finding(
                task,
                "TASK_UNFAILABLE",
                f"{accepted_nulls}/{len(null_answers)} null/refuse/echo probes accepted",
                "critical",
                suite_reference=reproducer_suite,
            )

        wrong_results = [
            budget.run(task.grader, answer) for answer in task.wrong_mutations
        ]
        wrong_observed = [result for result in wrong_results if result is not None]
        false_accepts = sum(result is True for result in wrong_observed)
        fp_interval = wilson(false_accepts, len(wrong_observed))

        correct_results = [
            budget.run(task.grader, answer) for answer in task.correct_variants
        ]
        correct_observed = [result for result in correct_results if result is not None]
        false_rejects = sum(result is False for result in correct_observed)
        fn_interval = wilson(false_rejects, len(correct_observed))
        rates[task.id] = {"fp": fp_interval, "fn": fn_interval}

        if existing is None and false_accepts:
            if len(wrong_observed) >= 4 and false_accepts / len(wrong_observed) >= 0.5:
                existing = _finding(
                    task,
                    "WEAK_GRADER",
                    f"accepted {false_accepts}/{len(wrong_observed)} constructed wrong answers",
                    "critical",
                    fp_lower_bound=True,
                    suite_reference=reproducer_suite,
                )
            else:
                existing = _finding(
                    task,
                    "GRADER_FP",
                    f"accepted {false_accepts}/{len(wrong_observed)} constructed wrong answers",
                    fp_lower_bound=True,
                    suite_reference=reproducer_suite,
                )
        if existing is None and false_rejects:
            existing = _finding(
                task,
                "GRADER_FN",
                f"rejected {false_rejects}/{len(correct_observed)} correct variants",
                suite_reference=reproducer_suite,
            )
        if existing is not None:
            findings.append(existing)

    fp_tasks = sum(
        finding.verdict in {"GRADER_FP", "WEAK_GRADER"} for finding in findings
    )
    fn_tasks = sum(finding.verdict == "GRADER_FN" for finding in findings)
    invalid_tasks = sum(
        finding.verdict in {"TASK_UNSOLVABLE", "TASK_UNFAILABLE", "TASK_DEGENERATE"}
        for finding in findings
    )
    denominator = len(tasks) or 1
    low, high = trust_adjusted_band(
        reported_score,
        fp_tasks / denominator,
        fn_tasks / denominator,
        invalid_tasks / denominator,
    )
    planned = budget.used + budget.skipped + oracle_undetermined
    abstentions = budget.skipped + oracle_undetermined
    abstention_rate = abstentions / planned if planned else 0.0
    return AuditResult(
        suite_name=suite_name,
        task_count=len(tasks),
        findings=findings,
        grader_rates=rates,
        budget={
            "limit": budget.limit,
            "used": budget.used,
            "skipped": budget.skipped,
            "skipped_reason": "budget exhausted" if budget.skipped else None,
            "oracle_undetermined": oracle_undetermined,
            "model_calls": 0,
            "cost_usd": 0.0,
        },
        trust_band={
            "reported": reported_score,
            "low": low,
            "high": high,
            "fp_affected": fp_tasks / denominator,
            "fn_affected": fn_tasks / denominator,
            "invalid": invalid_tasks / denominator,
        },
        abstention_rate=abstention_rate,
        metadata={
            "ci": "Wilson score interval, 95%",
            "fp_interpretation": "lower bound over constructed mutations",
            "trust_band_interpretation": "sensitivity band, not confidence interval",
            "decision_status": "UNDETERMINED" if abstentions else "DETERMINED",
            "red_flags": red_flags,
        },
    )
