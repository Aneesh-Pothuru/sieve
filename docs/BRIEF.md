# 06 · SIEVE

**The auditor for everything you use to test models and agents —
environments, benchmarks, eval datasets, graders. It measures what your
evals get wrong: tasks that can't be solved, tasks that can't be failed,
graders with measured false-positive and false-negative rates.**

`sieve` · Python · probe agents + grader mutation testing · works on
agentic benchmarks, LLM evals, and sim scenario suites

---

## Objective

Every result you trust flows through an eval: a benchmark task, an
environment, a grader, a labeled dataset. The field now has hard
evidence that this layer is rotten in places — and no tool whose job is
finding the rot. SIEVE audits test infrastructure the way a security
team audits code:

1. **Task validity** — is each task solvable (an oracle can pass it) and
   failable (a null agent scores zero)? Is it solvable *only* by the
   capability it claims to test?
2. **Outcome validity** — does the grader say yes exactly when it should?
   SIEVE measures each grader's **false-positive rate** (wrong/empty/
   cheating trajectories it accepts) and **false-negative rate** (correct
   solutions it rejects) by feeding it deliberately constructed inputs.
3. **Failure partition** — when a policy fails inside an environment,
   was it a policy defect, an environment defect, or a grader defect?
   Three-way, evidenced, at fleet scale — for agentic suites and for
   physical simulation alike.
4. **Dataset quality** — label errors, contamination signals, saturated
   or degenerate items in eval datasets.

One sentence: **SIEVE is the eval for your evals — what it catches is a
bug in the test, and what passes through is a result you can trust.**

---

## Why now

The evidence that this layer fails is recent, quantified, and damning:

- The **Agentic Benchmark Checklist** (ABC) audited ten popular agent
  benchmarks and found: **τ-bench counted empty responses as
  successes**; an agent can score **100% on SWE-Lancer without solving
  any task**; KernelBench overestimates correct-kernel capability by
  **31 absolute points** from weak fuzzing; SWE-bench Verified uses
  insufficient tests. Net effect: performance mis-estimated **by up to
  100% in relative terms**
  ([ABC](https://arxiv.org/abs/2507.02825),
  [checklist](https://uiuc-kang-lab.github.io/agentic-benchmarks/)).
  ABC is a *checklist for humans*; SIEVE is the machine that runs it.
- **Reward hackability is quantified**: 28.5% of a SWE-bench Verified
  sample passes a verified-incorrect patch; models score +14.14pp on
  hackable tasks ([audit](https://arxiv.org/pdf/2606.16062)).
- **Label errors are pervasive** — the Platinum Benchmarks line showed
  standard benchmarks riddled with wrong ground truth, so models get
  marked wrong for being right (a grader false negative by
  construction); "0% pass across many trials" is now a recognized red
  flag for broken tasks
  ([benchmark auditing](https://arxiv.org/pdf/2605.26079)).
- **Sim testing has the same disease, unmeasured.** Scenario generation
  is mature (Scenic, VerifAI falsification, LLM-driven pipelines
  ([2026](https://arxiv.org/pdf/2602.20644)); coverage tooling
  ([SCOUT](https://arxiv.org/pdf/2510.24949))) and GPU-parallel sim is
  commodity (MJX ~2.7M steps/sec; ManiSkill3
  ([paper](https://arxiv.org/pdf/2410.00425))). But domain randomization
  at scale *will* generate impossible tasks — friction × mass combos
  outside physical coherence, goals inside walls — and every framework
  charges those to the policy. Nobody checks the scenario.

Test infrastructure is the one layer with no tests. That's the product.

**The blog post this proves:** "What a Good Eval Harness Refuses to Do,"
inverted — *here is what your eval harness has been wrongly accepting
and rejecting, measured.*

---

## Non-goals

- Not an eval runner — ASSAY runs evals and gates regressions; SIEVE
  audits whether the evals deserve trust. (Boundary, one line: ASSAY
  scores your model; SIEVE scores your scorer.)
- Not a benchmark or environment author — TERRARIUM authors; SIEVE
  audits (including TERRARIUM's own tasks, v0.3).
- Not a leaderboard police force. Findings ship as coordinated
  disclosures with reproducers and proposed fixes, not gotchas.

---

## Personas

| Persona | Cares about |
|---|---|
| **Eval owner** at a team shipping agents | "Our suite says 84%. How much of that number is real?" |
| **Benchmark/environment author** | "Find my broken tasks and weak graders before a paper does." |
| **Policy/robotics engineer** | "Of last night's 1,086 sim failures, which are actually mine?" |
| **Research lead** | "Before we optimize against this benchmark for a quarter — is it sound?" |

---

## User journeys

### Journey 0 — the demo (no API key, <10 minutes)

```bash
pipx install sieve && sieve demo
```

Bundled: a deliberately imperfect 20-task mini-benchmark ("FlawedBench")
with five seeded defects. The demo audits it keylessly (probe agents are
scripted, graders run locally) and renders the findings report:

```
FLAWEDBENCH AUDIT · 20 tasks · 5 findings

  TASK_UNSOLVABLE   task-07   oracle solution rejected: expected file
                              path referenced in grader does not exist
  TASK_UNFAILABLE   task-12   null agent (does nothing) scores 1.0
  GRADER_FP         task-03   grader accepts empty diff (exit-code-only check)
  GRADER_FN         task-15   correct solution rejected: answer key wrong
                              (label error — 2+2 task keyed to 5)
  WEAK_GRADER       task-19   accepts 4/6 seeded wrong answers

TRUST-ADJUSTED SCORE  a model scoring 80% here could really be 65–90%
```

That last line is the pitch in one number. The hosted version is the
same report as a static page plus a gallery of real public-benchmark
audits as they're published.

### J1 — Audit a benchmark before trusting it

Lena's team is about to spend a quarter optimizing against an agentic
benchmark. First:

```bash
sieve audit ./their-benchmark --graders --tasks --budget 200-runs
```

SIEVE runs the probe battery — oracle solutions (bundled with the
benchmark or synthesized), null/trivial agents (empty response, "I
cannot help", copy-the-prompt), mutation testing of graders (seeded
wrong-but-plausible answers), red-flag scans (0%-pass tasks,
100%-pass tasks, grader accepts-anything checks) — and returns a
per-task findings table plus **measured grader FP/FN rates with CIs**.
Two tasks are unfailable, one grader accepts empty responses (the exact
τ-bench bug). Lena's team excludes them and knows the error bars on the
rest.

### J2 — Partition a night of sim failures three ways

Nina's sweep produced 1,086 failures across 10k scenarios:

```
POLICY DEFECTS       812   (clustered: grasp-slip/specular 447, clutter
                            timeout 219, long tail 146)
ENVIRONMENT DEFECTS  241   goal unreachable 98 · incoherent randomization 71
                           · success predicate unobservable 44 · init
                           interpenetration 28
GRADER DEFECTS        33   success predicate fired on 33 *passes* that
                           oracle review shows are failures (FP) — these
                           runs were counted as wins elsewhere!
UNDETERMINED          33
```

The grader-defect row is what v1 SIEVE adds over every scenario-testing
framework: it audits the *success predicate itself* against oracle and
perturbation evidence, both directions — failures that weren't (FN) and
passes that weren't (FP).

### J3 — Fix the generator, not just the finding

Each environment defect ships with a reproducing seed and a minimal
repro. The 71 incoherent-randomization cases share one cause (friction
and mass sampled independently); the fix is a **generation
precondition**, and SIEVE re-audits to confirm the class is gone.
Findings against TERRARIUM tasks file in TERRARIUM's format; findings
against public benchmarks become disclosure PRs.

### J4 — Continuous audit as the suite evolves

Lena wires `sieve audit --changed` into the benchmark repo's CI: every
new task must pass the probe battery before merge (solvable, failable,
graders survive mutation). The audit becomes a gate — the same shape as
ASSAY's regression gate, one level up the stack.

### End-to-end journey (the product loop)

Point SIEVE at a suite → probe battery runs (oracle / null / mutations /
red flags) → findings with severity + reproducers → fix or exclude →
re-audit confirms → trust-adjusted score contextualizes every number
the suite produces from then on → continuous audit in CI keeps it sound
→ (fleet mode) every sweep's failures partitioned policy / environment /
grader before anyone debugs the wrong thing.

---

## PRD

### P0 — the audit core

| ID | Requirement |
|---|---|
| P0-1 | **Suite adapters** — ingest a benchmark/eval as (tasks, runner, grader): v0.1 supports "local command-line benchmark" (task dirs + grader scripts) and TERRARIUM task format; adapters are ~100-line plugins. |
| P0-2 | **Probe battery: task validity** — oracle-passes (if oracle solutions exist or can be synthesized), null-agent-fails (empty / refuse / echo agents), and duplicate/degenerate-task detection. |
| P0-3 | **Probe battery: grader mutation testing** — a library of wrong-answer generators (empty, truncated, plausible-but-wrong, cheating patterns like hardcoding expected outputs); **measured FP rate per grader**. |
| P0-4 | **Grader FN measurement** — correct-solution variants (formatting changes, alternative valid answers, paraphrases) fed to the grader; **measured FN rate per grader**; label-error candidates flagged when the keyed answer itself fails oracle review. |
| P0-5 | **Red-flag scans** — 0%-pass and 100%-pass items, near-zero-variance graders, accepts-anything graders, statistical outliers. Cheap, run first. |
| P0-6 | **Findings report** — per-task verdicts from the shared vocabulary (`TASK_UNSOLVABLE`, `TASK_UNFAILABLE`, `GRADER_FP`, `GRADER_FN`, `LABEL_ERROR`, `WEAK_GRADER`, `ENV_DEFECT`, …), severity, reproducer command, and the **trust-adjusted score band**. |
| P0-7 | **Budget control** — probe runs cost model calls in some modes; every audit takes a `--budget` and reports what it skipped (no silent truncation). |

### P1 — fleet mode (the sim/environment half)

| ID | Requirement |
|---|---|
| P1-1 | **Scenario fleet runner** — N scenarios across a sim backend (MJX or ManiSkill first), seeded, resumable. |
| P1-2 | **Pre-run validity checks** — goal reachability, physical coherence of randomized parameters, init interpenetration, predicate observability; rejects before compute is spent. |
| P1-3 | **Post-run partitioner** — tiered: oracle probe (privileged policy re-runs the scenario) → perturbation stability → grader audit on both failures *and* passes → three-way verdict. |
| P1-4 | **Failure clustering + coverage** — signatures compress 1,086 failures to ~20 clusters; coverage over the *declared* parameter space with the gaps named. |
| P1-5 | **CI mode** — `sieve audit --changed` gates new tasks/scenarios on the probe battery. |

### P2

- ABC-checklist automation: emit a filled checklist per audited suite.
- Contamination signals (memorization probes against eval items).
- Dual-sim cross-validation as a trust signal.
- LLM-judge auditing in depth (bias probes: length, sycophancy,
  self-preference) — coordinated with ASSAY's judge monitor.

### Success metrics

| Metric | Target |
|---|---|
| Demo: clone → FlawedBench findings report | < 10 min, $0, keyless |
| Seeded-defect recall on FlawedBench-style test suites | ≥ 85% across all defect classes |
| False-finding rate (valid tasks flagged) | ≤ 10% |
| Grader FP/FN measurement reproducibility | CIs reported; repeat audits agree within CI |
| **Launch measurement: audit of ≥ 1 real public agentic benchmark** | findings + measured grader FP/FN published with reproducers, disclosed to maintainers first |
| Fleet mode: policy/env/grader partition precision on seeded sims | ≥ 85% recall of seeded env defects at ≤ 5% policy-misfile rate |
| Triage compression | ≥ 20× (clusters vs raw failures) |

The launch measurement is the whole game: **pick one widely used public
benchmark, measure its grader FP/FN rates, and publish** — the number
that turns "benchmarks are broken" from an anecdote into a dashboard.
If it resembles the 28.5% found in code-RL environments, it's a
significant finding about work the field builds on.

### Launch-day definition

`sieve demo` keyless; `sieve audit` working on local benchmarks +
TERRARIUM tasks; probe battery with measured FP/FN + trust-adjusted
scores; one real public-benchmark audit disclosed and published with
reproducers; CI recipe; LIMITS.md (oracle availability constraints,
which probe classes need model calls and their cost, abstention rates).

### Risks

| Risk | Mitigation |
|---|---|
| Oracle solutions often don't exist | Tiered: bundled oracles > synthesized-and-verified > oracle-free probes only (null agents, mutations, red flags still catch most classes); findings state which tier they rest on |
| Wrong-answer generators miss grader holes (FP underestimated) | Report FP as a *lower bound*, explicitly; grow the mutation library from every published exploit (the flywheel) |
| Auditing the auditor — SIEVE's own probes have bugs | FlawedBench is SIEVE's own regression suite; seeded-defect recall gates every SIEVE release |
| Publishing findings reads as hostile | Coordinated disclosure, reproducer + proposed fix attached, maintainers credited; the ABC paper set the precedent |
| Probe costs explode on big suites | Budgeted audits with explicit skip reporting; red-flag scans (free) always run first |
| Sim fleet scope drags the MVP | Fleet mode is P1; the v0.1 audit core is pure-local and free |

---

## System design

```
 benchmark / eval suite / TERRARIUM tasks / scenario suite
                        │
                        ▼
              ┌───────────────────┐
              │  SUITE ADAPTER    │  tasks · runner · grader, normalized
              └─────────┬─────────┘
                        ▼
              ┌───────────────────┐
              │  RED-FLAG SCAN    │  free: 0%/100% items, degenerate graders
              └─────────┬─────────┘
                        ▼
        ┌────────────────────────────────┐
        │         PROBE BATTERY          │
        │  oracle agents   (solvable?)   │
        │  null agents     (failable?)   │
        │  wrong-answer mutations → FP   │
        │  right-answer variants  → FN   │
        │  label-error review            │
        └───────────────┬────────────────┘
                        ▼
              ┌───────────────────┐     fleet mode (P1):
              │  VERDICT ENGINE   │◀─── pre-run validity · oracle probe ·
              │  (shared vocab,   │     perturbation stability · pass-audit
              │   severity, CIs)  │
              └─────────┬─────────┘
                        ▼
        ┌───────────────────────────────────┐
        │  FINDINGS REPORT                   │
        │  per-task verdicts · grader FP/FN  │
        │  trust-adjusted score band ·       │
        │  reproducers · disclosure bundle   │
        └───────────────────────────────────┘
```

**Grader FP/FN is the signature capability.** Mutation testing for
graders: feed each grader inputs whose correct verdict is *known by
construction* — wrong answers it must reject, correct variants it must
accept — and report acceptance/rejection rates with CIs. It's the same
trick mutation testing plays on unit tests, applied one level up. FP is
reported as a lower bound (you can only seed the exploits you thought
of); FN rests on variant generation plus label review. Both directions,
always — a grader that never false-accepts but rejects every valid
paraphrase is broken in the way that silently punishes good models.

**The trust-adjusted score band** operationalizes the audit: given
measured grader FP/FN and the invalid-task count, a suite's reported
score S becomes a band [S_lo, S_hi]. One number nobody can unsee.

**Fleet mode reuses the same verdict engine.** A sim success predicate
is a grader; an impossible scenario is an unsolvable task. The physical
half of SIEVE is the same audit with more expensive probes (privileged-
oracle re-runs, perturbation stability) — which is why it's one product
and not two.

### Interfaces

- **→ TERRARIUM** — audits its tasks/suites natively; findings file in
  its format (v0.3 integration; adapter is P0).
- **→ ASSAY** — audits ASSAY's datasets and judges; trust-adjusted bands
  annotate ASSAY reports. ASSAY runs the evals; SIEVE decides how much
  they mean.
- **→ CULPRIT** — fleet-mode policy-defect clusters hand representative
  failures to CULPRIT for the deep descent; `ENV_DEFECT`/`GRADER_FP`
  verdicts flow back.
- **← BATON** (v0.3) — long audits and nightly fleet sweeps as durable
  routines.
- **loopkit** — verdict vocabulary lives here; every probe run is a `Run`.

### Milestones

| | Scope |
|---|---|
| **v0.1** | Suite adapter (local + TERRARIUM), red-flag scan, probe battery (oracle/null/mutations/variants), findings report, FlawedBench. **Journey 0 works.** |
| **v0.2** | Grader FP/FN with CIs, trust-adjusted bands, label-error review, budget control, CI mode. |
| **v0.3** | Public-benchmark audit + coordinated disclosure. **Launch.** |
| **v1.0** | Fleet mode (MJX/ManiSkill): pre-run validity, oracle probe, three-way partition, clustering, coverage; publish a sim-suite defect rate. |

### Stack & free tier

Python 3.12 · SQLite findings store · scripted probe agents (keyless) +
LLM probes via Gemini/Groq free tiers where a probe needs generation
(budgeted, counted) · MuJoCo MJX / ManiSkill3 for fleet mode on Kaggle
(30 GPU-h/wk) or CPU for small sweeps · DuckDB for clustering/coverage ·
static reports on GitHub Pages · GitHub Actions CI mode. Total required
spend: **$0**.
