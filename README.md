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

The audit desk has two explicit execution modes:

- **Fixture replay** runs entirely on GitHub Pages and makes no backend claim.
- **Local service** calls an installed `sieve serve`, runs the actual Python
  auditor, and renders the immutable evidence envelope returned after SQLite
  persistence.

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

## Install and run the local service

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .

sieve serve
```

In another terminal:

```bash
curl --fail http://127.0.0.1:8765/readyz
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d '{"suite":"flawedbench","budget":200,"reported_score":0.8}' \
  http://127.0.0.1:8765/v1/audits
```

This is the production path for local integrations: the request executes the
actual adapter and probe engine, persists the complete result plus indexed
findings to SQLite, and returns a retrievable run ID. Audit runs survive
service restarts.

The default bind is loopback-only. Suite paths must stay inside the configured
data root. Request sizes and budgets are capped, unknown fields are rejected,
and non-loopback binds require an explicit `--allow-remote`. Remote operation
still requires an authenticated TLS proxy; SIEVE does not pretend otherwise.

Configuration and endpoint contracts are documented in
[docs/API.md](docs/API.md). Copy `.env.example` to configure the process.

### Container

```bash
docker compose up --build
curl --fail http://127.0.0.1:8765/readyz
```

The Compose profile publishes only on loopback, drops Linux capabilities,
uses a read-only root filesystem, mounts suites read-only, and keeps SQLite in
a named volume.

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
  trust-band math, adapters, report, SQLite persistence, live HTTP journeys,
  restart recovery, request validation, and path confinement.
- `make lint` performs dependency-free AST, whitespace, and JSON checks.

The authoritative build brief is copied to [docs/BRIEF.md](docs/BRIEF.md).
The role-based site flows are documented in
[docs/USER_JOURNEYS.md](docs/USER_JOURNEYS.md), and the primary-source design
review is in [docs/COMPETITIVE_UI.md](docs/COMPETITIVE_UI.md).
See [LIMITS.md](LIMITS.md) before using a result to make a decision.
