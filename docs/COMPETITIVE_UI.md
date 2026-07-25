# Competitive UX and design review

Reviewed 2026-07-24 using official product documentation and public design
system guidance. Sieve is not presented as a substitute for these products:
the review identifies interaction patterns that make evaluator assurance
understandable and inspectable.

## Evaluation and assurance products

| Product | Primary-source evidence | Useful journey pattern | Sieve response |
| --- | --- | --- | --- |
| [Giskard](https://docs.giskard.ai/) | Its Hub supports test datasets, evaluations, team workflows, scans, and continuous red teaming; [scan guidance](https://docs.giskard.ai/hub/sdk/guides/scans) organizes detected vulnerabilities as reviewable risks. | Move from a quality-risk overview into a specific test and then re-run after remediation. | A persistent exception register links every classification to its task, probe evidence, and exact reproducer. |
| [Patronus](https://docs.patronus.ai/docs) | The platform joins experiments, production monitoring, evaluators, comparisons, traces, and human review. Its [experiment model](https://docs.patronus.ai/docs/experiments/concepts) supports task variants, score comparison, output diffs, confidence intervals, and filtering. | Keep dataset, evaluator, run, and explanation connected; let users compare and filter before acting. | The audit desk keeps the suite configuration, live run, rate uncertainty, selected task, and evidence packet in one navigable surface. |
| [Arize Phoenix](https://arize.com/docs/phoenix/evaluation/llm-evals/evaluator-traces) | Evaluator executions retain inputs, judge prompts, reasoning, scores, and timing. Phoenix also recommends a [deterministic dry run](https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments/run-experiments) before a full experiment and lets users filter results then inspect low-scoring examples and traces. | Start small, expose execution details behind each score, and preserve a direct score-to-trace path. | The Sieve demo is explicitly a deterministic fixture replay; selected tasks open a probe trace and evidence-tiered reproducer rather than a score-only card. |
| [Braintrust](https://www.braintrust.dev/docs/evaluate/interpret-results) | Experiment analysis uses filtered trace tables, grouped results, regression ordering, scorer-error views, review assignment, inputs/outputs/expected values, and score explanations. [Comparisons](https://www.braintrust.dev/docs/evaluate/compare-experiments) align cases and show score deltas. | Aggregate first, then filter exceptions and inspect a case with the surrounding evidence. | The task register, severity filters, confusion matrix, Wilson plot, and evidence drawer form the same overview-to-evidence progression, specialized for testing the test. |

## Standards-interface references

| Source | Guidance used |
| --- | --- |
| [USWDS data visualizations](https://designsystem.digital.gov/components/data-visualizations/) | State the chart’s intended message in text, use familiar visual forms, limit each chart to a central idea, use color carefully, and retain an accessible textual equivalent. Sieve pairs every graph with visible values and explanatory copy. |
| [USWDS step indicator](https://designsystem.digital.gov/components/step-indicator/) | Progress needs a distinct current state, short labels, explicit headings, and a textual step/total expression. Sieve’s live status, task count, task states, and separate controls make audit progress legible without color alone. |
| [GOV.UK validation pattern](https://design-system.service.gov.uk/patterns/validation/) | Explain what failed and how to recover; retain submitted values; do not hide errors in vague messages. Sieve retains the selected configuration and makes budget exhaustion, missing oracles, and exact reproducers explicit. |
| [GOV.UK check-answers pattern](https://design-system.service.gov.uk/patterns/check-answers/) | A review surface improves confidence and gives users a chance to catch errors before a consequential action. Sieve exposes the complete evidence packet and exportable audit before a benchmark score is trusted. |

## Product distinction

Most evaluation platforms optimize the model or application by running
datasets through scorers. Sieve challenges the scoring infrastructure itself:

1. Can the declared oracle pass?
2. Can empty, refusing, or echoing behavior fail?
3. Which wrong mutations does the grader accept?
4. Which valid answer variants does it reject?
5. What remains undetermined when budget or trusted evidence is absent?

That distinction drove a **bright assurance atelier** rather than another dark
observability dashboard:

- warm paper layers turn a run into a reviewable assurance dossier;
- calibration rulers and numbered stations communicate measurement;
- high-visibility yellow marks the active method, not generic success;
- blue is reserved for reported/reference signals, coral for exceptions, green
  for evidenced pass states, and gray for undetermined;
- audit stamps name evidence status in text so color is never the only carrier;
- serif editorial headings explain the thesis, while monospace labels identify
  tasks, rates, evidence tiers, and reproducers.

## Interaction decisions

- The public landing page explains problem, method, evidence, architecture,
  boundaries, and current implementation before asking the visitor to run a
  demo.
- The main application starts in a safe idle state and supports start, pause,
  one-task step, reset, scenario presets, oracle policy, mutation coverage, and
  a declared probe budget.
- Canonical defaults replay the actual fixture: 20 tasks, 165/200 probes, five
  findings, reported 80%, and a 65–90% trust-adjusted sensitivity band.
- Budget exhaustion and withheld oracles create visible `UNDETERMINED` states;
  they do not silently become passes.
- Findings can be filtered by severity and opened from either the task register
  or finding register into the same evidence drawer.
- Copy and export controls produce a structured evidence snapshot of the
  current browser replay.
- The static replay is labeled synthetic and deterministic. The Python audit
  core and generated `report.html` are explicitly authoritative.
