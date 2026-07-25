# SIEVE

SIEVE audits the infrastructure used to test models and agents. It asks
whether tasks are solvable and failable, measures grader false-positive and
false-negative behavior with constructed probes and Wilson intervals, and
turns a reported score into an explicit trust-adjusted sensitivity band.

This v0.1 is deterministic, keyless, and standard-library-only.

## Journey 0

```bash
git clone https://github.com/Aneesh-Pothuru/sieve
cd sieve
make demo
```

The command audits bundled FlawedBench—20 tasks with five seeded defects—and
writes the authoritative generated report to `docs/demo/report.html` plus its
machine-readable evidence to `docs/demo/audit.json`:

```text
TASK_UNSOLVABLE  task-07
TASK_UNFAILABLE  task-12
GRADER_FP        task-03
GRADER_FN        task-15  (secondary: LABEL_ERROR)
WEAK_GRADER      task-19

TRUST-ADJUSTED SCORE  80% -> 65–90%
```

Scripted probes and local graders make the path network-free and keyless.
The root Pages entry is a complete product explanation in `docs/index.html`;
`docs/demo/index.html` is an interactive deterministic replay of the same
fixture. The browser demo makes the workflow inspectable, while the Python
audit and generated report remain authoritative.

## Audit a suite

```bash
# Local manifest format: <suite>/manifest.json
PYTHONPATH=src python -m sieve audit ./flawedbench \
  --budget 200 --output work/report.html --json-output work/audit.json

# A directory of TERRARIUM JSON-subset .yaml task files.
PYTHONPATH=src python -m sieve audit ./terrarium-tasks --format terrarium
```

Every grader call consumes one run from the explicit budget. The output
reports skipped probes; it never silently truncates. The TERRARIUM adapter
validates and audits the vendored declarative format without importing or
calling a deployed TERRARIUM service.

## Adapter contract

The local manifest normalizes each item to:

```text
id, prompt, oracle, grader{mode, expected}, correct_variants,
wrong_mutations, label_review, metadata
```

The auditor runs oracle, null/no-op/refusal/echo, wrong-answer mutations, and
correct-answer variants. A finding records its primary verdict, secondary
tags, evidence tier, severity, reproducer, FP/FN counts, Wilson 95% CI, and
whether an FP estimate is a lower bound.

## Reproducibility

- `make reproduce-flawedbench` regenerates the exact five-finding report.
- `make reproduce-grader-rates` regenerates machine-readable grader rates.
- `make test` verifies the exact seeded findings, Wilson CIs, budget skips,
  trust-band math, adapters, report, and SQLite findings store.
- `make lint` performs dependency-free AST, whitespace, and JSON checks.

The authoritative build brief is copied to [docs/BRIEF.md](docs/BRIEF.md).
The role-based site flows are documented in
[docs/USER_JOURNEYS.md](docs/USER_JOURNEYS.md), and the primary-source design
review is in [docs/COMPETITIVE_UI.md](docs/COMPETITIVE_UI.md).
See [LIMITS.md](LIMITS.md) before using a result to make a decision.
