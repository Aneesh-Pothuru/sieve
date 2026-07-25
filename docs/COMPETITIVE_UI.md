# Competitive UI review

Reviewed 2026-07-24 against AI quality, red-team, and evaluator platforms.

| Product | Relevant surface | What works |
| --- | --- | --- |
| [Giskard](https://www.giskard.ai/products/llm-evaluation) | agent quality and risk testing | Business-readable risks, golden datasets, regression comparison, and exportable evidence support enterprise review. |
| [Patronus](https://docs.patronus.ai/docs) | evaluators and experiments | Evaluator configuration, per-result explanations, benchmarks, traces, and comparisons stay in one quality system. |
| [Galileo](https://galileo.ai/) | evaluation and guardrails | Ground truth, tuned evaluators, failure patterns, and deployment controls form a visible trust lifecycle. |
| [Arize Phoenix](https://arize.com/docs/phoenix/evaluation/llm-evals/evaluator-traces) | evaluator validation | The evaluator itself is traced so a score never appears without inspectable execution evidence. |

## Direction adopted

- Lead with the trust-adjusted interval, explicitly labeled as a sensitivity
  band rather than a confidence interval.
- Separate task validity, grader false positives, grader false negatives, and
  label quality into distinct finding cards.
- Pair every rate with count, Wilson interval, evidence tier, and reproducer.
- Keep budget consumption, skipped probes, abstention, and lower-bound caveats
  in a persistent audit strip.
- Use audit yellow for attention, coral for high-severity defects, and mint for
  verified controls.

The result is an evaluator assurance console rather than a vulnerability list.
